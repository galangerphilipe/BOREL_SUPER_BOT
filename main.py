import logging
from core.bot import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from keep_alive import keep_alive
keep_alive()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.application.run_polling()