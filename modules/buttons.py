from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from modules.telegram_bot import bot
from modules.users import is_user, is_admin, is_request, process_add_request_last_name, set_command_menu, show_requests, show_users, process_remove_user, process_add_admin, remove_admin, show_user_info
from modules.users import check_subscription
from modules.states import states_set, states_back, save_states_now, clear_states
from gpt.dialogs import choose_gpt, disconnect_gpt, gpt_text_handler, waiting_for_gpt, stop_waiting
from utils.logs import gpt_logger, user_logger, logger, log_message
from modules.notify import show_notification_menu
from gpt.update_promt import show_prompt_menu_call, show_prompt_menu_message
import threading
import time

# Модуль со всеми основными кнопками меню (в полной версии тут располагаются почти все Reply кнопки)

#--------------------------- ГЛАВНОЕ ---------------------------
#---------------------------- МЕНЮ -----------------------------
@bot.message_handler(func=lambda message: message.text == "В главное меню")
def show_main_menu(message):
    if is_user(message.from_user.id):
        clear_states(message.from_user.id)
        markup = create_main_menu()
        bot.send_message(message.chat.id, "Переходим в главное меню.", reply_markup=markup)
    else:
        markup = check_status()
        bot.send_message(message.chat.id, "У Вас нет доступа к этому боту.", reply_markup=markup)
@bot.message_handler(func=lambda message: message.text == "Главное меню")
def show_main_menu2(message):
    if is_user(message.from_user.id):
        clear_states(message.from_user.id)
        markup = create_main_menu()
        bot.send_message(message.chat.id, "Переходим в главное меню.", reply_markup=markup)
    else:
        markup = check_status()
        bot.send_message(message.chat.id, "У Вас нет доступа к этому боту.", reply_markup=markup)


    
#-------------------------- ФУНКЦИОНАЛЬНЫЕ --------------------------
#----------------------------- КНОПКИ ------------------------------

# кнопка /start
def start_chat_logic():
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        try:
            if is_user(message.from_user.id):
                markup = create_main_menu()
                bot.send_message(message.chat.id, '''👋 Добро пожаловать! Вы в главном меню.''', reply_markup=markup)
                clear_states(message.from_user.id)
            else:
                markup = access_request()
                bot.send_message(message.chat.id, 'У Вас нет доступа к этому боту. \n\nНажмите на кнопку "Запросить доступ", чтобы отправить запрос на добавление.', reply_markup=markup)
                log_message(user_logger, "INFO", 'Неизвестный пользователь нажал "/start"', message.from_user.id)
        except telebot.apihelper.ApiTelegramException as e:
            if "bot was blocked by the user" in str(e):
                log_message(user_logger, "INFO", 'Пользователь заблокировал бота', message.from_user.id)
                print(f"Пользователь заблокировал бота: {message.chat.id}")

# проверка статуса пользователя
def check_status():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton('Проверить статус'))
    return markup

@bot.message_handler(func=lambda message: message.text == "Проверить статус")
def check_status_menu(message):
    if is_admin(message.from_user.id):
        markup = create_main_menu()
        bot.send_message(message.chat.id, "Вы являетесь администратором", reply_markup=markup)
        clear_states(message.from_user.id)
    elif is_user(message.from_user.id):
        markup = create_main_menu()
        bot.send_message(message.chat.id, '''👋 Добро пожаловать! Мы подготовили всё, чтобы Вы стали успешнее в недвижимости! Ваши помощники:

📌 Тренировки диалогов — отработка общения с покупателями и собственниками.
📌 Создание объявлений — помощник по написанию продающих текстов для объектов недвижимости.
📌 Контент для соцсетей — генерация постов, сторис и рилсов для SMM.
📌 Обучение и развитие — ввод в профессию и повышение квалификации.
📌 Личный психолог — помощь в преодолении стресса и поддержка в сложных ситуациях.
📌 Ипотека — консультации и помощь в подборе ипотечных программ.
📌 Анализ звонков — оценка разговоров с клиентами и рекомендации по улучшению.
📌 Поздравления на заказ — создание уникальных и запоминающихся текстов для поздравлений.
📌 И многое другое — инструменты для эффективной работы и развития в сфере недвижимости.

📖 Хотите узнать больше? Нажмите «О программе» в меню, а затем «Инструкция», чтобы познакомиться с функциями сервиса подробнее.

Просто выберите нужную кнопочку и начните работать с ботом — вводите текст с клавиатуры или общайтесь голосом через микрофон. 
Экономьте время, улучшайте навыки и достигайте новых высот! 🚀''', reply_markup=markup)
        clear_states(message.from_user.id)
    elif is_request(message.from_user.id):
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Вы уже отправили запрос на добавление.\nЗапрос на рассмотрении, ожидайте.", reply_markup=markup)
        threading.Thread(target=delay_response, args=(message,)).start()
    else:
        markup = access_request()
        bot.send_message(message.chat.id, "Вы не являетесь пользователем. \n\nВы можете запросить доступ.", reply_markup=markup)

# запросить доступ
def access_request():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton('Запросить доступ')
        )
    return markup

@bot.message_handler(func=lambda message: message.text == "Запросить доступ")
def request_menu(message):
    if is_user(message.from_user.id):
        markup = create_main_menu()
        clear_states(message.from_user.id)
        bot.send_message(message.chat.id, "Вы авторизованный пользователь", reply_markup=markup)
    elif is_admin(message.from_user.id):
        markup = create_main_menu()
        clear_states(message.from_user.id)
        bot.send_message(message.chat.id, "Вы являетесь администратором", reply_markup=markup)
    elif is_request(message.from_user.id):
        markup = check_status()
        bot.send_message(message.chat.id, "Ожидайте принятия запроса", reply_markup=markup)
    else:
        log_message(user_logger, "INFO", 'Новый пользователь начал регистрацию запроса', message.from_user.id)
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Напишите Вашу фамилию:", reply_markup = markup)
        bot.register_next_step_handler_by_chat_id(message.chat.id, process_add_request_last_name)

# задержка ответа бота
def delay_response(message):
    markup = check_status()
    bot.send_message(message.chat.id, "Бот спит 3 секунды.")
    time.sleep(3)
    bot.send_message(message.chat.id, "Бот проснулся.", reply_markup=markup)

# отключение текущей GPT
@bot.message_handler(func=lambda message: message.text == "Оставить бота")
def handle_disconnect_button(message):
    user_id = message.from_user.id
    # Отключение от текущего бота
    response = disconnect_gpt(user_id)
    log_message(gpt_logger, "INFO", f'Пользователь "{user_id}": Оставить бота')
    bot.reply_to(message, response)
    stop_waiting(user_id)
    functions_map[states_back(message.from_user.id)](message)


# кнопка Назад
@bot.message_handler(func=lambda message: message.text == "Назад")
def back_button(message):
    if not is_user(message.from_user.id):
        markup = check_status()
        bot.send_message(message.chat.id, "У Вас нет доступа к этому боту.", reply_markup=markup)
        return
    user_id = message.from_user.id
    functions_map[states_back(user_id)](message)

@bot.message_handler(commands=['update_menu'])
def handle_update_command_menu(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message.id, "У вас нет администраторских прав на выполнение этого действия.")
        return
    set_command_menu(message)

@bot.message_handler(commands=['save_states'])
def handle_update_command_menu(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message.id, "У вас нет администраторских прав на выполнение этого действия.")
        return
    result = save_states_now()
    if result == True:
        bot.send_message(user_id, 'Состояния сохранены')
    else:
        bot.send_message(user_id, result)

# управление через callback data
@bot.callback_query_handler(func=lambda call: is_user(call.from_user.id))
def handle_admin_callback(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data

    if data.startswith("user_management"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "У вас нет администраторских прав на выполнение этого действия.")
            return

        action = data.split(":")[1]

        if action == "show_users":
            show_users(user_id)

        elif action == "remove_user":
            bot.send_message(user_id, "Отправьте ID пользователя, которого нужно удалить:")
            bot.register_next_step_handler_by_chat_id(user_id, process_remove_user)

        elif action == "add_admin":
            bot.send_message(user_id, "Отправьте ID пользователя, которого нужно повысить до администратора:")
            bot.register_next_step_handler_by_chat_id(user_id, process_add_admin)

        elif action == "remove_admin":
            remove_admin(user_id)
        
        elif action == "requests":
            show_requests(call.message)

        elif action == 'save_states':
            result = save_states_now()
            if result == True:
                bot.send_message(user_id, 'Состояния сохранены')
            else:
                bot.send_message(user_id, result)

        elif action == 'set_command_menu':
            set_command_menu(call)
            
        elif action == 'info':
            first_message = bot.send_message(user_id, 'Введите ID пользователя')
            bot.register_next_step_handler(call.message, show_user_info, first_message)

        elif action == "back_to_main":
            main_menu = create_main_menu()
            bot.send_message(call.message.chat.id, "Вы вернулись в главное меню.", reply_markup=main_menu)

    elif data.startswith("clear_history"):
        bot.answer_callback_query(call.id)
        if not is_user(call.from_user.id):
            bot.answer_callback_query(call.id, "У вас нет прав на выполнение этого действия.")
            return
        assistant_name = data.split(":")[1]
        # Определяем и удаляем историю
        result = detect_delete_method(user_id, assistant_name)
    
        # Проверяем оставшихся ассистентов после удаления
        remaining_assistants = check_dialogs_and_threads(user_id)
    
        if remaining_assistants:
            # Если остались ассистенты, обновляем сообщение с кнопками
            markup = InlineKeyboardMarkup()
            for assistant in remaining_assistants:
                markup.add(InlineKeyboardButton(assistant, callback_data=f'clear_history:{assistant}'))
        
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Выберите ассистента, чтобы удалить его историю:",
                reply_markup=markup
            )
        else:
            # Если ассистентов не осталось, заменяем сообщение на уведомление
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="История всех ассистентов удалена."
            )

        bot.send_message(call.message.chat.id, result)



# карта состояний

functions_map = {
    'show_main_menu' : show_main_menu,
    'show_work_menu' : show_work_menu,
    'show_assistants_menu' : show_assistants_menu
    }