import logging
import os
from datetime import datetime

# Создаем папку для логов, если она не существует
os.makedirs('logs', exist_ok=True)

# Настраиваем логгер
logger = logging.getLogger('semgu_support')
logger.setLevel(logging.DEBUG)

# Создаем обработчик для вывода в консоль с более высоким уровнем логирования
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Создаем обработчик для записи в файл, который логирует даже отладочные сообщения
log_filename = f"logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Создаем форматтеры и добавляем их к обработчикам
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                  datefmt='%H:%M:%S')
file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Добавляем обработчики к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def setup_logging():
    """Инициализация системы логирования"""
    logger.info("Система логирования инициализирована")
    return logger

# Утилитарные функции логирования
def log_info(message):
    """Логирование информационного сообщения"""
    logger.info(message)

def log_warning(message):
    """Логирование предупреждения"""
    logger.warning(message)
    
def log_error(message):
    """Логирование ошибки"""
    logger.error(message)
    
def log_debug(message):
    """Логирование отладочного сообщения"""
    logger.debug(message)

def log_command(user_id, username=None, command=None, full_name=None):
    """Логирование команды пользователя"""
    user_info = f"[ID: {user_id}]"
    if username:
        user_info += f" @{username}"
    if full_name:
        user_info += f" ({full_name})"
    
    logger.info(f"Command: {command} | User: {user_info}")
    
def log_callback(user_id, callback_data, username=None, full_name=None):
    """Логирование обратного вызова"""
    user_info = f"[ID: {user_id}]"
    if username:
        user_info += f" @{username}"
    if full_name:
        user_info += f" ({full_name})"
    
    logger.info(f"Callback: {callback_data} | User: {user_info}")
    
def log_chat_message(user_id, username=None, message_text=None, full_name=None):
    """Логирование сообщения чата"""
    user_info = f"[ID: {user_id}]"
    if username:
        user_info += f" @{username}"
    if full_name:
        user_info += f" ({full_name})"
    
    if message_text:
        message_preview = f" | Message: {message_text[:50]}{'...' if len(message_text) > 50 else ''}"
    else:
        message_preview = ""
        
    logger.info(f"Chat Message | User: {user_info}{message_preview}")
    
def log_admin_action(admin_id, admin_username=None, action=None, target_id=None, admin_name=None):
    """Логирование действия администратора"""
    admin_info = f"[ID: {admin_id}]"
    if admin_username:
        admin_info += f" @{admin_username}"
    if admin_name:
        admin_info += f" ({admin_name})"
        
    target_info = f" | Target: {target_id}" if target_id else ""
    logger.info(f"Admin Action: {action} | Admin: {admin_info}{target_info}")
    
def log_exception(e, context=""):
    """Логирование исключения с контекстом"""
    logger.error(f"Exception{' in ' + context if context else ''}: {str(e)}")

def log_message(source, user_id, message_type=None, username=None, full_name=None):
    """Логирование сообщения от пользователя или админа"""
    user_info = f"[ID: {user_id}]"
    if username:
        user_info += f" @{username}"
    if full_name:
        user_info += f" ({full_name})"
    
    msg_type = f" ({message_type})" if message_type else ""
    
    logger.info(f"{source} message{msg_type} received from {user_info}")

def log_chat_connection(action, user_id, admin_id=None, admin_name=None):
    """Логирование соединения чата"""
    if action == "start":
        logger.info(f"User [ID: {user_id}] started waiting for chat connection")
    elif action == "connect":
        logger.info(f"Admin [ID: {admin_id}] ({admin_name}) connected to user [ID: {user_id}]")
    elif action == "disconnect_user":
        logger.info(f"User [ID: {user_id}] disconnected from chat with admin [ID: {admin_id}] ({admin_name})")
    elif action == "disconnect_admin":
        logger.info(f"Admin [ID: {admin_id}] ({admin_name}) disconnected from chat with user [ID: {user_id}]")
    elif action == "timeout":
        logger.info(f"Chat connection for user [ID: {user_id}] timed out")

def log_question(action, question_id, user_id=None, admin_id=None, admin_name=None):
    """Логирование вопросов"""
    if action == "asked":
        logger.info(f"User [ID: {user_id}] asked question #{question_id}")
    elif action == "answer_start":
        logger.info(f"Admin [ID: {admin_id}] ({admin_name}) started answering question #{question_id}")
    elif action == "answered":
        logger.info(f"Admin [ID: {admin_id}] ({admin_name}) answered question #{question_id}")

def log_registration(action, user_id, username=None, full_name=None):
    """Логирование регистрации"""
    user_info = f"[ID: {user_id}]"
    if username:
        user_info += f" @{username}"
    if full_name:
        user_info += f" ({full_name})"
    
    if action == "start":
        logger.info(f"User {user_info} started registration")
    elif action == "complete":
        logger.info(f"User {user_info} completed registration")
    elif action == "already":
        logger.info(f"User {user_info} tried to register but already registered") 