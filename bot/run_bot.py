from models import Logger

logger = Logger().get_logger()

def run_bot(bot):
    try:
        logger.info("Bot is running...")
        print("Bot is running...")
        bot.polling(none_stop=True, interval=0)
    except Exception as exc:
        logger.error(f"Error running bot: {exc}")
