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

    @bot.message_handler(commands=["messbo_add_access"])
    def add_access_handler(message):
        try:
            logger.info(
                f"[ADD ACCESS REQUEST] '{message.from_user.id}': '{message.text}'."
            )

            pattern = r'/messbo_add_access\s+([\'"`])(.*?)\1\s+([^\s]+)'
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(message.chat.id, "Некорректный формат команды.")
                return

            argument_board = find.group(2).strip()
            argument_user = find.group(3).strip()

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

            try:
                chat_member = bot.get_chat_member(message.chat.id, argument_user)
                mentioned_user_id = chat_member.user.id if chat_member else None
            except Exception as exc:
                bot.send_message(
                    message.chat.id,
                    f"Пользователь '{argument_user}' не найден в этом чате.",
                )
                return

            request_id = make_access_request(
                message.chat.id, argument_board, mentioned_user_id
            )
            if request_id:
                bot.send_message(
                    mentioned_user_id,
                    f"Пользователь '' послал вам запрос на получение прав модерации доски '{argument_board}' в чате '{message.chat.title}'.\n"
                    "Для подтверждения используйте команду /accept_request, для отклонения - /deny_request.",
                )
                bot.send_message(
                    message.chat.id,
                    f"Запрос на доступ к доске '{argument_board}' отправлен пользователю '{argument_user}'.",
                )
            else:
                bot.send_message(
                    message.chat.id, "Не удалось создать запрос на доступ."
                )
        except Exception as exc:
            logger.error(f"[ADD ACCESS ERROR]: '{exc}'.")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)
