from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from modules.telegram_bot import bot
from modules.users import users
from modules import buttons
from utils.logs import log_message, logger

admin_notifications = {}

def show_notification_menu(message):
    admin_id = message.from_user.id
    global admin_notifications
    markup = create_notification_menu()
    if admin_id not in admin_notifications or not admin_notifications[admin_id]:
        bot.send_message(admin_id, '''Вы перешли в меню отправки уведомлений для всех пользователей.

Инструкция:
1) Нажмите на <b>Редактировать сообщение</b>
2) Напишите и отправьте сообщение. Бот запомнит его, но не отправит пользователям
    (бот запоминает уведомление до перезагрузки бота. Вы можете продолжить редактирование даже после выхода из меню)
3) Бот отправит уведомление ВАМ в ответ, проверьте его, если нужно - еще раз отредактируйте
    (можно вручную нажать "Показать сообщение")
4) Когда уведомление готово - нажмите <b>Отправить уведомление</b>. Его получат все пользователи''', parse_mode='HTML', reply_markup=markup)
        admin_notifications[admin_id] = 'Уведомление отсутствует'
    else:
        bot.send_message(admin_id, 'Ваше текущее уведомление:', parse_mode='HTML')
        bot.send_message(admin_id, admin_notifications[admin_id], parse_mode='HTML')
        bot.send_message(admin_id, 'Выберите действие:', parse_mode='HTML', reply_markup=markup)

    bot.register_next_step_handler(message, process_notification)


def create_notification_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton('Редактировать сообщение'),
        KeyboardButton('Показать текущее сообщение'),
        KeyboardButton('Отправить уведомление'),
        KeyboardButton('Назад')
    )
    return markup

def process_notification(message):
    print('запускаем process_notification')
    admin_id = message.from_user.id
    if message.text == 'Редактировать сообщение':
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(KeyboardButton('Отменить редактирование'))
        bot.send_message(admin_id, '<b>Напишите уведомление для пользователей:</b>', parse_mode='HTML', reply_markup=markup)
        bot.register_next_step_handler(message, edit_notification)
    elif message.text == 'Показать текущее сообщение':
        global admin_notifications
        if admin_notifications[admin_id]:
            show_notification_menu(message)
        else: 
            bot.send_message(admin_id, '<b>Вы ещё не составляли уведомление</b>', parse_mode='HTML')
            show_notification_menu(message)
    elif message.text == 'Отправить уведомление':
        bot.send_message(admin_id, '<b>Ваше текущее уведомление:</b>', parse_mode='HTML')
        bot.send_message(admin_id, admin_notifications[admin_id], parse_mode='HTML')
        bot.send_message(admin_id, '<b>Уверены, что хотите отправить?</b>\n\nНапишите в чат "Отправить" без ковычек.\nИли другой текст, для отмены.', parse_mode='HTML')
        bot.register_next_step_handler(message, send_notification)
    elif message.text == 'Назад':
        buttons.back_button(message)


def edit_notification(message):
    print('запускаем edit')
    admin_id = message.from_user.id
    if message.text == 'Отменить редактирование':
        show_notification_menu(message)
    else:
        global admin_notifications
        notification = message.html_text  # Получаем текст с форматированием HTML
        admin_notifications[admin_id] = notification
        show_notification_menu(message)

def send_notification(message):
    print('запускаем send')
    admin_id = message.from_user.id
    if message.text == 'Отправить':
        log_message(logger, 'INFO', 'Админ отправил уведомления пользователям', admin_id)
        global admin_notifications
        text = admin_notifications[admin_id]
        for user in users:
            try:
                bot.send_message(user, text, parse_mode='HTML')
            except Exception as e:
                bot.send_message(admin_id, f'Ошибка отправки уведомления для {str(user)}: {e}')
                log_message(logger, 'ERROR', f'Ошибка отправки уведомления для {str(user)}: {e}')
        admin_notifications[admin_id] = None
        buttons.show_main_menu(message)
    else: 
        show_notification_menu(message)