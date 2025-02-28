import json
import threading
from pathlib import Path
from utils.logs import logger, user_logger, log_message

# Модуль для хранения и записи состояний меню, чтобы при перезагрузке бот "знал" в каком меню находился пользователь

states_file_path = 'resources/.user_states.json'

timer_is_active = False
user_states = {}
lock = threading.Lock()

def load_user_states():
    global user_states
    try:
        file_path = Path(states_file_path)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                user_states = json.load(f)
    except Exception as e:
        log_message(logger, "ERROR", f'Ошибка в load_user_states: {e}')

load_user_states()

def save_states_process():
    global user_states
    global timer_is_active

    with lock:
        try:
            with open(states_file_path, 'w', encoding='utf-8') as f:
                json.dump(user_states, f, ensure_ascii=False, indent=4)
        except Exception as e:
            log_message(logger, "ERROR", f'Ошибка сохранения состояний в save_states_process: {e}')
        timer_is_active = False

def states_set(user_id, state):
    global user_states
    user_id = str(user_id)
    state = str(state)

    with lock:
        if user_id not in user_states:
            user_states[user_id] = []
        
        if state in user_states[user_id]:
            return

        user_states[user_id].append(state)

        save_states()
    return

def states_back(user_id):
    global user_states
    user_id = str(user_id)

    with lock:
        try:
            if user_id not in user_states:
                user_states[user_id] = []
            if user_states[user_id]:
                user_states[user_id].pop()
        except Exception as e:
            print(e)
    
        if not user_states[user_id]:
            del user_states[user_id]

        save_states()

        if user_id not in user_states:
            return 'show_main_menu'
        if not user_states[user_id]:
            return 'show_main_menu'
        return user_states[user_id][-1] if user_states[user_id] else 'show_main_menu'

def clear_states(user_id):
    global user_states
    user_id = str(user_id)

    with lock:
        if user_id in user_states:
            del user_states[user_id]
            save_states()
        return

def save_states():
    def delayed_start():
        save_thread = threading.Thread(
            target=save_states_process
        )
        save_thread.start()

    global timer_is_active
    if timer_is_active:
        return

    timer_is_active = True
    timer = threading.Timer(300, delayed_start)
    timer.start()

def save_states_now():
    global user_states
    try:
        with open(states_file_path, 'w', encoding='utf-8') as f:
            json.dump(user_states, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        log_message(logger, "ERROR", f'Ошибка сохранения состояний в save_states_now: {e}')
        return f'Ошибка сохранения состояний'

def delete_states(user_id):
    user_id = str(user_id)
    global user_states
    with lock:
        if user_id in user_states:  
            del user_states[user_id]
            log_message(user_logger, "INFO", f'Удаление состояния пользователя', user_id)
            result = save_states_now()

            if result == True:
                return f' Состояния {user_id} удалены.'
            else:
                return result
        else:
            return ''