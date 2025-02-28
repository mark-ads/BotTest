import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YANDEX_TOKEN = os.getenv("YANDEX_KEY")
CHANNEL = int(os.getenv("CHANNEL_ID"))
KAFKA_YSK_TEXT = os.getenv("KAFKA_YSK_TEXT")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_LOGS_TOPIC = os.getenv("KAFKA_LOGS_TOPIC")
BOT_NAME = os.getenv("BOT_NAME")

from utils import logs
if not BOT_TOKEN or not OPENAI_API_KEY:
    logs.log_message(logs.logger, "CRITICAL", "Токены TELEGRAM_BOT_TOKEN и OPENAI_API_KEY не заданы")
    raise ValueError("Токены TELEGRAM_BOT_TOKEN и OPENAI_API_KEY должны быть заданы в переменных среды.")