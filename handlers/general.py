from telebot import TeleBot
from handlers import HELP_TEXT


def register_general_handlers(bot: TeleBot):
    @bot.message_handler(commands=["messbo_start"])
    def start_handler(message):
        bot.send_message(
            message.chat.id,
            "Здравствуйте. Вас приветствует бот MessBo - Доска Объявлений.\n"
            "Для списка команд воспользуйтесь /messbo_help\n",
        )

    @bot.message_handler(commands=["messbo_help"])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT)
