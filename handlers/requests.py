import re
from telebot import TeleBot, types
from controllers import RequestController, BoardController
from models import Logger
from handlers import DEFAULT_MESSAGE, PREFIX

logger = Logger().get_logger()


def register_request_handlers(
    bot: TeleBot,
    request_controller: RequestController,
    board_controller: BoardController,
):
    def get_token_from_reply(message):
        if not message.reply_to_message:
            return None
        return request_controller.get_token_by_message_id(
            message.chat.id,
            message.reply_to_message.message_id,
        )

    def extract_board_name(text):
        pattern = r'/messbo_\w+(?:@\w+)?\s+(?:([\'"`])(.*?)\1|(\S+))'
        find = re.match(pattern, text)
        return (find.group(2) or find.group(3)).strip() if find else None

    def _process_permission_request(message, request_type):
        try:
            if not message.reply_to_message:
                hint = (
                    "назначить модератора"
                    if request_type == "mod"
                    else "передать права владельца"
                )
                bot.send_message(
                    message.chat.id,
                    f"Ответьте на сообщение пользователя, чтобы {hint}.",
                )
                return

            board_name = extract_board_name(message.text)
            if not board_name:
                bot.send_message(message.chat.id, "Некорректный формат команды.")
                return

            board = board_controller.show_one_board(message.chat.id, board_name)
            if not board or board.owner_id != message.from_user.id:
                bot.send_message(
                    message.chat.id,
                    "Доска не найдена или вы не являетесь её владельцем.",
                )
                return

            target_id = message.reply_to_message.from_user.id

            if request_type == "mod":
                request_token = request_controller.add_mod_request(
                    message.chat.id,
                    board.id,
                    message.from_user.id,
                    target_id,
                    message.id,
                )
                text_add = "прав модерации"
            elif request_type == "own":
                request_token = request_controller.add_own_request(
                    message.chat.id,
                    board.id,
                    message.from_user.id,
                    target_id,
                    message.id,
                )
                text_add = "прав владения (полный контроль)"

            if request_token:
                markup = types.InlineKeyboardMarkup()
                btn_accept = types.InlineKeyboardButton(
                    text="Принять", callback_data=f"req_accept_{request_token}"
                )
                btn_deny = types.InlineKeyboardButton(
                    text="Отклонить", callback_data=f"req_deny_{request_token}"
                )
                markup.add(btn_accept, btn_deny)

                requester = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'
                target = f'<a href="tg://user?id={target_id}">Пользователь</a>'

                reply = (
                    f"{target}, {requester} предлагает Вам получение {text_add} доской '{board_name}'.\n"
                    f"Ответьте на данное сообщение /{PREFIX}accept (для подтверждения) или /{PREFIX}deny (для отклонения)."
                )

                reply_sent = bot.send_message(
                    message.chat.id, reply, parse_mode="HTML", reply_markup=markup
                )
                request_controller.update_request_message_id(
                    request_token, reply_sent.message_id
                )
        except Exception as exc:
            logger.error(f"[{request_type.upper()} REQUEST ERROR]: {exc}")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "add_mod"])
    def add_mod_handler(message):
        _process_permission_request(message, "mod")

    @bot.message_handler(commands=[PREFIX + "owner"])
    def transfer_ownership_handler(message):
        _process_permission_request(message, "own")

    @bot.message_handler(commands=[PREFIX + "rm_mod"])
    def remove_mod_handler(message):
        try:
            if not message.reply_to_message:
                bot.send_message(
                    message.chat.id,
                    "Ответьте на сообщение модератора, которого хотите снять с должности.",
                )
                return

            board_name = extract_board_name(message.text)
            board = board_controller.show_one_board(message.chat.id, board_name)

            if not board or board.owner_id != message.from_user.id:
                bot.send_message(
                    message.chat.id,
                    "Доска не найдена или вы не являетесь её владельцем.",
                )
                return

            target_id = message.reply_to_message.from_user.id
            success = request_controller.remove_mod(board.id, target_id)

            if success:
                reply = (
                    f"Пользователь больше не является модератором доски '{board_name}'."
                )
            else:
                reply = "Не удалось удалить модератора. Возможно, данный пользователь и не является модератором."
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[RM MOD ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "accept"])
    def accept_request_handler(message):
        try:
            token = get_token_from_reply(message)
            if not token:
                bot.send_message(
                    message.chat.id,
                    "Не удалось определить, на какой запрос вы отвечаете.",
                )
                return

            details = request_controller.get_request_details(token)
            if not details or details["target_id"] != message.from_user.id:
                bot.send_message(
                    message.chat.id,
                    "Запрос не найден или вы не являетесь адресатом данного запроса.",
                )
                return

            board_name = board_controller.get_name_by_id(details["board_id"])

            if details["type"] == "mod":
                success = request_controller.accept_mod_request(token)
                reply = (
                    f"Вы стали модератором доски '{board_name}'."
                    if success
                    else "Ошибка получения прав."
                )
            elif details["type"] == "own":
                success = request_controller.accept_own_request(token)
                reply = (
                    f"Права владения доской '{board_name}' переданы Вам."
                    if success
                    else "Ошибка передачи прав."
                )

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[ACCEPT REQUEST ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=[PREFIX + "deny"])
    def deny_request_handler(message):
        try:
            token = get_token_from_reply(message)
            if not token:
                bot.send_message(
                    message.chat.id,
                    "Не удалось определить, на какой запрос вы отвечаете.",
                )
                return

            details = request_controller.get_request_details(token)
            if not details or details["target_id"] != message.from_user.id:
                bot.send_message(
                    message.chat.id,
                    "Запрос не найден или вы не являетесь адресатом данного запроса.",
                )
                return

            request_controller.delete_request(token)
            bot.send_message(message.chat.id, "Запрос отклонён.")
        except Exception as exc:
            logger.error(f"[DENY REQUEST ERROR] Error denying request: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    # buttons
    @bot.callback_query_handler(func=lambda call: call.data.startswith("req_"))
    def handler_request_callback(call):
        try:
            _, action, token = call.data.split("_")

            details = request_controller.get_request_details(token)

            if not details or details["target_id"] != call.from_user.id:
                bot.answer_callback_query(
                    call.id,
                    "Вы не являетесь адресатом данного запроса.",
                    show_alert=True,
                )
                return

            board_name = board_controller.get_name_by_id(details["board_id"])

            if action == "accept":
                if details["type"] == "mod":
                    success = request_controller.accept_mod_request(token)
                    res_text = f"Вы стали модератором доски '{board_name}'."
                elif details["type"] == "own":
                    success = request_controller.accept_own_request(token)
                    res_text = f"Права владения доской '{board_name}' переданы Вам."

                if not success:
                    res_text = "Ошибка при обработке запроса."
            else:
                request_controller.delete_request(token)
                res_text = "Запрос отклонён."

            try:
                bot.delete_message(
                    chat_id=call.message.chat.id, message_id=call.message.message_id
                )
            except Exception:
                pass

            bot.send_message(
                chat_id=call.message.chat.id,
                text=("<b>Запрос обработан</b>\n\n" f"{res_text}"),
                parse_mode="HTML",
            )

            bot.answer_callback_query(call.id, "Запрос обработан.")
        except Exception as exc:
            logger.error(f"[CALLBACK REQUEST ERROR]: {exc}")
            bot.answer_callback_query(call.id, DEFAULT_MESSAGE)
