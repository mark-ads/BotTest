import telebot
from modules.config import BOT_TOKEN
from modules.proxy import get_openai_client
from utils.logs import log_message, logger

bot = telebot.TeleBot(BOT_TOKEN)
client = get_openai_client()

def start_bot():
    try:
        log_message(logger, "INFO", "Запуск бота")
        bot.polling(none_stop=True)
    except Exception as e:
        log_message(logger, "CRITICAL", f"Ошибка запуска скрипта, main.py: {e}")
