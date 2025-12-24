from telebot import TeleBot
from handlers import PREFIX


def register_fallback(bot: TeleBot):
    @bot.message_handler(
        chat_types=["private"],
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
        ],
    )
    def default_handler(message):
        if not message.text or not message.text.startswith("/"):
            reply = f"Неизвестная команда или некорректный ввод. Используйте /{PREFIX}help для списка команд."
        else:
            reply = f"Неизвестная команда. Используйте /{PREFIX}help для списка команд."
        bot.send_message(message.chat.id, reply)
