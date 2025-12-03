import re
from telebot import TeleBot
from controllers import RequestController, BoardController
from models import Logger
from handlers import DEFAULT_MESSAGE

logger = Logger().get_logger()


def register_request_handlers(
    bot: TeleBot,
    request_controller: RequestController,
    board_controller: BoardController,
):

    @bot.message_handler(commands=["messbo_add_mod"])
    def add_mod_handler(message):
        try:
            logger.info(
                f"[ADD MOD REQUEST] '{message.from_user.id}': '{message.text}'."
            )

            if not message.reply_to_message:
                bot.send_message(
                    message.chat.id,
                    "Для назначения модератора доски используйте /messbo_add_mod '<название доски>' в ответ на любое сообщение пользователя, которого хотите назначить.",
                )
                return
            target_id = message.reply_to_message.from_user.id

            pattern = r'/messbo_add_mod\s+([\'"`])(.*?)\1'
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(message.chat.id, "Некорректный формат команды.")
                return

            argument_board = find.group(2).strip()

            board = board_controller.show_one_board(message.chat.id, argument_board)
            if not board:
                bot.send_message(
                    message.chat.id, f"Доска '{argument_board}' не найдена."
                )
                return

            if board.owner_id != message.from_user.id:
                bot.send_message(
                    message.chat.id, "Вы не являетесь владельцем этой доски."
                )
                return

            request_token = request_controller.add_mod_request(
                message.chat.id, board.id, message.from_user.id, target_id
            )

            if request_token:
                requester = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.username}</a>'
                target = f'<a href="tg://user?id={target_id}">Пользователь</a>'

                reply = (
                    f"{target}, {requester} послал Вам запрос на получение прав модерации доски '{argument_board}'.\n"
                    f"Для подтверждения ответьте на данное сообщение командой /messbo_accept, для отклонения - /messbo_deny.",
                )

                reply_sent = bot.send_message(
                    message.chat.id,
                    reply,
                    parse_mode="HTML",
                )

                request_controller.update_request_message_id(
                    request_token, reply_sent.message_id
                )
            else:
                bot.send_message(
                    message.chat.id, "Не удалось создать запрос на доступ."
                )
        except Exception as exc:
            logger.error(f"[ADD ACCESS ERROR]: '{exc}'.")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    def get_token_from_reply(message):
        if not message.reply_to_message:
            return None
        return request_controller.get_token_by_message_id(
            message.chat.id,
            message.reply_to_message.message_id,
        )

    @bot.message_handler(commands=["messbo_accept"])
    def accept_request_handler(message):
        try:
            token = get_token_from_reply(message)
            if not token:
                bot.send_message(
                    message.chat.id,
                    "Не удалось определить, на какой запрос вы отвечаете.",
                )
                return

            details = request_controller.get_mod_request(token)
            if not details:
                bot.send_message(message.chat.id, "Запрос не найден или уже обработан.")
                return
            if details["target_id"] != message.from_user.id:
                bot.send_message(
                    message.chat.id, "Вы не являетесь адресатом этот запроса."
                )
                return

            success = requests_controller.accept_mod_request(token)
            board_name = board_controller.get_board_name(details["board_id"])

            if success:
                reply = f"Запрос принят. Доступ модератора к доске '{board_name}' предоставлен."
            else:
                reply = "Доступ модератора к доске '{board_name}' уже предоставлен или произошлоа ошибка при обработке запроса."
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[ACCEPT REQUEST ERROR] Error accepting request: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=["messbo_deny"])
    def deny_request_handler(message):
        try:
            token = get_token_from_reply(message)
            if not token:
                bot.send_message(
                    message.chat.id,
                    "Не удалось определить, на какой запрос вы отвечаете.",
                )
                return

            details = request_controller.get_mod_request(token)
            if not details:
                bot.send_message(message.chat.id, "Запрос не найден или уже обработан.")
                return

            if details["target_id"] != message.from_user.id:
                bot.send_message(
                    message.chat.id, "Вы не являетесь адресатом этого запроса."
                )
                return

            deleted = request_controller.delete_request(token)
            board_name = board_controller.get_board_name(details["board_id"])

            if deleted:
                reply = f"Запрос модерации доски '{board_name}' отклонён."
            else:
                reply = f"Запрос не найден для отклонения. Возможно, он уже был удалён."

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[DENY REQUEST ERROR] Error denying request: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)
