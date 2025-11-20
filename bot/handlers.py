import time
from telebot import TeleBot
from bot import BoardManager
from models import Logger

logger = Logger().get_logger()

HELP_TEXT = (
    "/messbo_start = Приветствие бота\n"
    "/messbo_help = Показать список команд\n"
    "/messbo_new_board <название> = Создать новую доску (название указывать необязательно)\n"
    "/messbo_show_boards = Показать все Ваши доски\n"
    "/messbo_show_board <название> = Показать Вашу доску с данным названием\n"
)

def register_handlers(bot: TeleBot, manager: BoardManager):
    @bot.message_handler(commands=['messbo_start'])
    def start_handler(message):
        reply = (
            "Добро пожаловать в бота MessBo - Доска Объявлений.\n"
            "Для списка команд напишите /messbo_help\n"
        )
        bot.send_message(message.chat.id, reply)
        # time.sleep(0.05)
    
    @bot.message_handler(commands=['messbo_help'])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT)
        # time.sleep(0.05)

    @bot.message_handler(commands=['messbo_new_board'])
    def new_board_handler(message):
        try:
            logger.info(f"[NEW BOARD] User '{message.from_user.username}' ({message.from_user.id}) sent {message.text}.")
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            board = manager.create_board(message.from_user.id, argument)
            reply = f"Доска {board.name} создана." if board else f"Не удалось создать доску '{argument}'."

            logger.info(
                f"[NEW BOARD RESULT] User '{message.from_user.username}' ({message.from_user.id}), "
                f"argument='{argument}', result='{reply}'"
            )

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[NEW BOARD ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")
        # time.sleep(0.05)

    @bot.message_handler(commands=['messbo_show_boards'])
    def show_boards_handler(message):
        try:
            boards = manager.show_all_boards(message.from_user.id)
            reply = "\n".join(f"{i + 1}. {boards[i]}" for i in range(len(boards))) if boards else "У вас нет досок."

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARDS ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка, попробуйте позже.")
        # time.sleep(0.05)

    @bot.message_handler(commands=['messbo_show_board'])
    def show_board_handler(message):
        try:
            parts = message.text.split(maxsplit=1)
            argument = parts[1] if len(parts) > 1 else None

            if not argument:
                bot.send_message(message.chat.id, "Укажите название доски.")
                return

            board_name = manager.show_one_board(message.from_user.id, argument)
            reply = board_name if board_name else f"Вашей доски с названием '{argument}' нет."

            bot.send_message(message.chat.id, reply)
        except Exception as exc:
            logger.error(f"[SHOW BOARD ERROR] {exc}")
            bot.send_message(message.chat.id, "Ошибка. Попробуйте позже.")
        # time.sleep(0.05)

    @bot.message_handler(content_types=['text', 'sticker', 'photo', 'video', 'audio', 'document', 'location', 'contact', 'voice', 'voice_note', 'new_chat_members', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message', 'web_app_data'])
    def default_handler(message):
        if not message.text.startswith("/"):
            reply = "Неизвестная команда или некорректный ввод. Используйте /messbo_help для списка команд."
        else:
            reply = "Неизвестная команда. Используйте /messbo_help для списка команд."
        bot.send_message(message.chat.id, reply)
