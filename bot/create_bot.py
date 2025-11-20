import telebot
from models import Logger

logger = Logger().get_logger()

def create_bot(token):
    try:
        bot = telebot.TeleBot(token, skip_pending=True)
        return bot
    except Exception as exc:
        logger.error(f"Error creating bot: {exc}")
        return None
