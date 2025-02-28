from modules.telegram_bot import client
from modules.telegram_bot import bot
from gpt.dialogs import send_long_message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from utils.logs import log_message, logger
from modules.states import clear_states
from modules import buttons

# модуль для просмотра и изменения промпта ассистента (OpenAI Assistant API)

bot_map = {
# тут были все используемые ассистенты
    }

def show_prompt_menu_message(message):
    try:
        markup = InlineKeyboardMarkup(row_width=1)
        for bot_name, bot_id in bot_map.items():
            button = InlineKeyboardButton(
                text=f'{bot_name}',
                callback_data=f'editBot:{bot_id}'
            )
            markup.add(button)
        close_button = InlineKeyboardButton(
            text=f'Закрыть меню',
            callback_data=f'closePromptMenu'
        )
        markup.add(close_button)
        bot.send_message(message.chat.id, "Выберите бота", reply_markup=markup)
    except Exception as e:
        log_message(logger, "ERROR", f"Ошибка в show_promt_menu: {e}")
        bot.send_message(message.chat.id, f"Ошибка при загрузке списка ботов: {e}")

def get_bot_name_by_id(bot_id):
    for name, id in bot_map.items():
        if id == bot_id:
            return name

def show_prompt_menu_call(call):
    try:
        markup = InlineKeyboardMarkup(row_width=1)
        for bot_name, bot_id in bot_map.items():
            button = InlineKeyboardButton(
                text=f'{bot_name}',
                callback_data=f'editBot:{bot_id}'
            )
            markup.add(button)
        close_button = InlineKeyboardButton(
                text=f'Закрыть меню',
                callback_data=f'closePromptMenu'
            )
        markup.add(close_button)
        bot.edit_message_text(
            f"Список ботов:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        log_message(logger, "ERROR", f"Ошибка в show_promt_menu: {e}")
        bot.send_message(call.message.chat.id, f"Ошибка при загрузке списка ботов: {e}")

def get_bot_name_by_id(bot_id):
    for name, id in bot_map.items():
        if id == bot_id:
            return name

# Обработка Закрыть меню
@bot.callback_query_handler(func=lambda call: call.data == "closePromptMenu")
def handle_request_selection(call):

    bot.delete_message(call.message.chat.id, call.message.message_id)

# Обработка выбора бота
@bot.callback_query_handler(func=lambda call: call.data.startswith("editBot:"))
def handle_request_selection(call):
    
    bot_id = call.data.split(":")[1]

    markup = InlineKeyboardMarkup(row_width=1)
    retrieve_button = InlineKeyboardButton(
        text="Запросить данные", callback_data=f"retrieveBot:{bot_id}"
    )
    change_button = InlineKeyboardButton(
        text="Изменить промпт", callback_data=f"changePrompt:{bot_id}"
    )
    back_button = InlineKeyboardButton(
        text="Другие промпты", callback_data=f"menuPrompt"
    )
    markup.add(retrieve_button, change_button, back_button)


    bot.edit_message_text(
        f"Выбран бот:\n{get_bot_name_by_id(bot_id)}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

# Обработка retrieve (получения данных бота)
@bot.callback_query_handler(func=lambda call: call.data.startswith("retrieveBot:"))
def handle_request_selection(call):
    bot_id = call.data.split(":")[1]

    retrieve_assistant(call, bot_id)

    bot.delete_message(call.message.chat.id, call.message.message_id)

# Обработка change (обновление промпта)
@bot.callback_query_handler(func=lambda call: call.data.startswith("changePrompt:"))
def handle_request_selection(call):
    bot_id = call.data.split(":")[1]
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Передумал отправлять"))
    message_to_user = bot.send_message(call.message.chat.id, "Пожалуйста, отправьте текстовый файл (.txt)", reply_markup=markup)
    bot.register_next_step_handler(message_to_user, update_prompt_with_txt, bot_id)

    bot.delete_message(call.message.chat.id, call.message.message_id)

def update_prompt_with_txt(message, assistant_id):
    try:

        if message.text == 'Передумал отправлять':
            markup = buttons.create_main_menu()
            bot.send_message(message.from_user.id, "Отменяем отправку", reply_markup=markup)
            clear_states(message.from_user.id)
            return

        elif message.document.mime_type == 'text/plain':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
        
            # Декодируем содержимое файла
            text_content = downloaded_file.decode('utf-8')

            try:
                markup = buttons.create_update_menu()
                temp_message = bot.reply_to(message, f'Меняем промпт "{get_bot_name_by_id(assistant_id)}".', reply_markup=markup)
                assistant = client.beta.assistants.update(
                    assistant_id,  # Заменить на настоящий ID ассистента
                    instructions=text_content,  # Инструкции ассистента
                )

                markup = InlineKeyboardMarkup(row_width=1)
                back_button = InlineKeyboardButton(
                    text="Другие промпты", callback_data=f"menuPrompt"
                )
                markup.add(back_button)
                bot.reply_to(message, f'Промпт "{get_bot_name_by_id(assistant_id)}" изменен.', reply_markup=markup)
            except Exception as e:
                print(e)
                log_message(logger, "ERROR", f'Ошибка в update_prompt_with_txt: {e}')
                bot.reply_to(message, f'Ошибка в update_prompt_with_txt: {e}')
    except Exception as e:

        log_message(logger, "ERROR", f'Ошибка в update_promt_with_txt: {e}')
        bot.send_message(message.from_user.id, f'Ошибка в update_promt_with_txt: {e}')

def retrieve_assistant(call, assistant_id):
    user_id = call.from_user.id
    try:
        my_assistant = client.beta.assistants.retrieve(assistant_id)
    except Exception as e:
        log_message(logger, 'ERROR', f'Ошибка в retrieve_assistant: {e}')
        return f'Ошибка в retrieve_assistant: {e}'

    try:
       response = (f"Имя: {getattr(my_assistant, 'name', 'Имя не найдено')}\nМодель: {getattr(my_assistant, 'model', 'Модель не найдена')}\nТемп: {getattr(my_assistant,'temperature', 'Температура не найдена')}\n\nПромпт:\n{getattr(my_assistant,'instructions', 'Промпт не найден')}")
       log_message(logger, 'INFO', f'Админ запросил данные "{get_bot_name_by_id(assistant_id)}"', user_id)
       send_long_message(response, user_id)
    except Exception as e:
       log_message(logger, 'ERROR', f'Ошибка в retreive_assistant: {e}')