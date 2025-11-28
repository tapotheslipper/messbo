import re
from telebot import TeleBot
from controllers import BoardController
from models import Logger
from handlers import DEFAULT_MESSAGE

logger = Logger().get_logger()


def register_board_handlers(bot: TeleBot, controller: BoardController):

    @bot.message_handler(commands=["messbo_new_board"])
    def new_board_handler(message):
        try:
            logger.info(
                f"[NEW BOARD REQUEST] '{message.from_user.id}': '{message.text}'."
            )

            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            board, name = controller.create_board(
                message.chat.id, message.from_user.id, argument
            )
            reply = (
                f"Доска {board.name} создана."
                if board
                else f"Не удалось создать доску '{name}'."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[NEW BOARD ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=["messbo_show_boards"])
    def show_boards_handler(message):
        try:
            boards = controller.show_all_boards(message.chat.id)
            reply = (
                "\n".join(f"{i + 1}. {board}" for i, board in enumerate(boards))
                if boards
                else "В этом чате нет досок."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARDS ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=["messbo_show_board"])
    def show_board_handler(message):
        try:
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски.")
                return

            board = controller.show_one_board(message.chat.id, argument)
            reply = board.name if board else f"Доски '{argument}' нет."
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARD ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=["messbo_rename"])
    def rename_board_handler(message):
        try:
            pattern = r'/messbo_rename\s+([\'"`])(.*?)\1\s+([\'"`])(.*?)\3'
            find = re.match(pattern, message.text)

            if not find:
                bot.send_message(message.chat.id, "Некорректный формат команды.")
                return

            old = find.group(2).strip()
            new = find.group(4).strip()

            res = controller.rename_board(
                message.chat.id, message.from_user.id, old, new
            )
            responses = {
                "renamed": f"Доска '{old}' переименована в '{new}'.",
                "duplicate": f"Доска с названием '{new}' уже существует.",
                "no_access": "У Вас нет прав на редактирование.",
                "not_found": f"Доска '{old}' не найдена.",
            }
            bot.send_message(message.chat.id, responses.get(res, DEFAULT_MESSAGE))
        except Exception as exc:
            logger.error(f"[RENAME ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)

    @bot.message_handler(commands=["messbo_remove_board"])
    def remove_board_handler(message):
        try:
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски.")
                return

            ok = controller.remove_board(
                message.chat.id, message.from_user.id, argument
            )
            reply = f"Доска '{argument}' удалена." if ok else DEFAULT_MESSAGE
        except Exception as exc:
            logger.error(f"[REMOVE ERROR]: '{exc}'")
            bot.send_message(message.chat.id, DEFAULT_MESSAGE)
