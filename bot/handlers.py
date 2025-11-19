from telebot import TeleBot
from bot import BoardManager
from models import Logger

logger = Logger().get_logger()

def register_handlers(bot: TeleBot, manager: BoardManager):
    @bot.message_handler(content_types=['text'])
    def text_handler(message):
        try:
            logger.info(f"Message received from '{message.from_user.username}': '{message.text}';")
            text = message.text.strip().lower()
            match (text):
                case "/help":
                    bot.send_message(message.from_user.id, """
/new_board = Создать новую доску
""")
                case "/new_board":
                    manager.create_board(message.from_user.id)
                    bot.send_message(message.from_user.id, "Новая доска создана.")
                case _:
                    bot.send_message(message.from_user.id, "Напишите '/help' для списка команд.")
        except Exception as exc:
            logger.error(f"Error in handler: '{exc}';")
            bot.send_message(message.from_user.id, "Произошла ошибка. Попробуйте позже.")
