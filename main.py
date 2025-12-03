import telebot
from config import BOT_TOKEN
from database import initialize_db
from bot import create_bot, run_bot_polling
from controllers import BoardController, RequestController
from handlers import register_handlers
from models import Logger

logger = Logger().get_logger()


def main(token):
    try:
        initialize_db()
        the_bot = create_bot(token)
        ctrls = {"board": BoardController(), "request": RequestController()}
        register_handlers(the_bot, ctrls)

        run_bot_polling(the_bot)
    except Exception as exc:
        logger.error(f"Error in main.py execution: {exc}.", exc_info=True)


if __name__ == "__main__":
    main(BOT_TOKEN)
