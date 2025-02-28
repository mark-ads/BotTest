from modules.telegram_bot import start_bot
from modules.buttons import start_chat_logic
from modules.speechkit import start_consumer_poll
#from gpt import create_assistant
#from gpt import update_assistant

if __name__ == "__main__":
    try:
        start_consumer_poll()
        start_chat_logic()  # Инициализируем логику чат-бота
        start_bot()  # Запускаем бота
    except Exception as e:
        print(e)