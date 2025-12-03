from telebot import TeleBot


def register_fallback(bot: TeleBot):
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
