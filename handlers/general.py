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

    @bot.message_handler(commands=["messbp_help"])
    def help_handler(message):
        bot.send_message(message.chat.id, HELP_TEXT)

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
