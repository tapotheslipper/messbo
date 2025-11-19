import signal
import sys
from models import Logger

logger = Logger().get_logger()

def signal_handler(sig, frame):
    logger.info("Keyboard Interrupt received. Stopping bot...")
    print("Bot stopped")
    sys.exit(0)

def run_bot(bot):
    logger.info("Bot is starting...")
    print("Bot is starting...")

    signal.signal(signal.SIGINT, signal_handler)
    
    try:        
        bot.polling(
            interval=0,
            timeout=20
        )
    except Exception as exc:
        logger.error(f"Error running bot: {exc}", exc_info=True)
        print("Bot crashed unexpectedly")
        sys.exit(1)
