import telebot
from config import BOT_TOKEN
from database import initialize_db
from bot import create_bot, BoardManager, register_handlers, run_bot
from models import Logger

logger = Logger().get_logger()

def main(token):
    try:
        initialize_db()
        bot = create_bot(token)
        manager = BoardManager()
        register_handlers(bot, manager)
        
        run_bot(bot)
    except Exception as exc:
        logger.error(f"Error in main execution: {exc}.")

if (__name__ == "__main__"):
    main(BOT_TOKEN)
