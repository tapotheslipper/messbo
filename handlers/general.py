from telebot import TeleBot
from handlers import HELP_TEXT


def register_general_handlers(bot: TeleBot):
    @bot.message_handler(commands=["messbo_start"])
    def start_handler(message):
        bot.send_message(
            message.chat.id,
            "Здравствуйте. Вас приветствует бот <b>MessBo - Доска Объявлений</b>.\n"
            "Для списка команд воспользуйтесь /messbo_help\n",
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["messbo_help"])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT, parse_mode="HTML")
