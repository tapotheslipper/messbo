import time
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
    
    while True:
        try:        
            bot.polling(
                interval=1,
                timeout=20,
                non_stop=True
            )
        except KeyboardInterrupt:
            signal_handler(None, None)
        except Exception as exc:
            logger.error(f"Polling crashed: {exc}", exc_info=True)
            print("Polling crashed, restarting in 5 seconds...")
            time.sleep(5)

