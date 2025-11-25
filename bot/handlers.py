import time
from telebot import TeleBot
from controllers import BoardController
from models import Logger
import re

logger = Logger().get_logger()

HELP_TEXT = (
    "/messbo_start = Приветствие бота\n"
    "/messbo_help = Показать список команд\n"
    "/messbo_new_board <название> = Создать новую доску (название указывать необязательно)\n"
    "/messbo_show_boards = Показать все Ваши доски\n"
    "/messbo_show_board <название> = Показать Вашу доску с данным названием\n"
    "/messbo_rename '<название доски>' '<новое название доски>' = Переименовать Вашу доску с первого указанного названия на новое. Оба названия необходимо заключить в любые кавычки\n"
    "/messbo_remove_board <название доски> = Удалить Вашу доску\n"
)


def register_handlers(bot: TeleBot, controller: BoardController):
    @bot.message_handler(commands=["messbo_start"])
    def start_handler(message):
        reply = (
            "Здравствуйте. Вас приветствует бот MessBo - Доска Объявлений.\n"
            "Для списка команд воспользуйтесь /messbo_help\n"
        )
        bot.send_message(message.chat.id, reply)

    @bot.message_handler(commands=["messbo_help"])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT)

    @bot.message_handler(commands=["messbo_new_board"])
    def new_board_handler(message):
        try:
            logger.info(
                f"[NEW BOARD REQUEST] User '{message.from_user.username}' ({message.from_user.id}) sent {message.text}."
            )
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            board = controller.create_board(message.from_user.id, argument)
            reply = (
                f"Доска {board.name} создана."
                if board
                else f"Не удалось создать доску '{argument}'."
            )

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[NEW BOARD ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")

    @bot.message_handler(commands=["messbo_show_boards"])
    def show_boards_handler(message):
        try:
            boards = controller.show_all_boards(message.from_user.id)
            if boards:
                lines = (f"{i + 1}. {item}" for i, item in enumerate(boards))
                reply = "\n".join(lines)
            else:
                reply = "У вас нет досок."

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARDS ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка, попробуйте позже.")

    @bot.message_handler(commands=["messbo_show_board"])
    def show_board_handler(message):
        try:
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски.")
                return

            board = controller.show_one_board(message.from_user.id, argument)
            reply = (
                board.name if board else f"Вашей доски с названием '{argument}' нет."
            )

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARD ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")

    @bot.message_handler(commands=["messbo_rename"])
    def rename_board_handler(message):
        try:
            pattern = r'/messbo_rename\s+([\'"`])(.*?)\1\s+([\'"`])(.*?)\3'
            find = re.match(pattern, message.text)
            if not find:
                bot.send_message(
                    message.chat.id,
                    "Неверный формат команды. Используйте кавычки для названий доски.",
                )
                return

            argument_old = find.group(2).strip()
            argument_new = find.group(4).strip()

            if not argument_old:
                bot.send_message(message.chat.id, "Укажите нынешнее название доски.")
                return
            if not argument_new:
                bot.send_message(
                    message.chat.id, f"Укажите новое название доски для {argument_old}."
                )
                return

            rename_ok = controller.rename_board(
                message.from_user.id, argument_old, argument_new
            )

            reply = (
                f"Доска {argument_old} переименована в {argument_new}."
                if rename_ok
                else "Не удалось переименовать доску."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"Error renaming board: {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")

    @bot.message_handler(commands=["messbo_remove_board"])
    def remove_board_handler(message):
        try:
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски на удаление.")
                return

            remove_ok = controller.remove_board(message.from_user.id, argument)

            reply = (
                f"Доска {argument} успешно удалена."
                if remove_ok
                else f"Не удалось удалить доску {argument}."
            )
            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"Error removing board: {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")

    @bot.message_handler(
        content_types=[
            "photo",
            "video",
            "audio",
            "document",
            "voice",
            "voice_note",
            "sticker",
            "text",
            "location",
            "contact",
            "web_app_data",
        ]
    )
    def default_handler(message):
        if not message.text or not message.text.startswith("/"):
            reply = "Неизвестная команда или некорректный ввод. Используйте /messbo_help для списка команд."
        else:
            reply = "Неизвестная команда. Используйте /messbo_help для списка команд."
        bot.send_message(message.chat.id, reply)
