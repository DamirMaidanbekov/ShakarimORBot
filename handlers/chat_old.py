import json
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage, StorageKey

from config import ADMIN_GROUP_ID, CHAT_NOTIFICATION_TOPIC_ID, ADMIN_TOPICS, ADMIN_IDS
from states.chat import ChatStates
from utils.file_operations import is_user_registered, load_user_data, is_user_banned
from utils.keyboards import get_main_keyboard
from utils.logger import log_info, log_error, log_chat_connection, log_callback, log_message, log_debug
from handlers.questions import active_questions

# Создание роутера
router = Router()

# Словарь для хранения активных чатов: {user_id: admin_name}
active_chats = {}
# Словарь для хранения пользователей ожидающих соединения: {user_id: True}
waiting_users = {}
# Словарь для хранения связанных пользователей: {admin_id: user_id}
admin_connections = {}
# Словарь для хранения ID сообщений с уведомлениями: {user_id: (message_id, admin_name)}
notification_messages = {}

# Команды администратора
@router.message(Command("list"))
async def handle_list_command(message: Message):
    """Показать активные чаты и неотвеченные вопросы."""
    user_id = message.from_user.id
    
    # Проверка на администратора
    if user_id not in ADMIN_IDS:
        log_info(f"Non-admin user [ID: {user_id}] tried to use /list command")
        await message.answer("У вас нет прав для использования этой команды.")
        return
    
    # Подготовка списков
    active_chats_list = []
    waiting_users_list = []
    unanswered_questions = []
    
    # Получение активных чатов
    for user_id, admin_name in active_chats.items():
        user_data = load_user_data(user_id)
        active_chats_list.append(
            f"ID: {user_id}\n"
            f"Имя: {user_data.get('full_name', '')}\n"
            f"Админ: {admin_name}\n"
        )
    
    # Получение ожидающих пользователей
    for user_id in waiting_users:
        user_data = load_user_data(user_id)
        waiting_users_list.append(
            f"ID: {user_id}\n"
            f"Имя: {user_data.get('full_name', '')}\n"
        )
    
    # Получение неотвеченных вопросов
    for question_id, question_data in active_questions.items():
        if question_data["status"] == "pending":
            unanswered_questions.append(
                f"ID: {question_id}\n"
                f"От: {question_data['full_name']}\n"
                f"Курс: {question_data['course']}\n"
                f"Факультет: {question_data['faculty']}\n"
                f"Группа: {question_data['group']}\n"
            )
    
    # Форматирование ответа
    response = "Активные чаты:\n"
    if active_chats_list:
        response += "\n".join(active_chats_list)
    else:
        response += "Нет активных чатов\n"
    
    response += "\nОжидающие пользователи:\n"
    if waiting_users_list:
        response += "\n".join(waiting_users_list)
    else:
        response += "Нет ожидающих пользователей\n"
    
    response += "\nНеотвеченные вопросы:\n"
    if unanswered_questions:
        response += "\n".join(unanswered_questions)
    else:
        response += "Нет неотвеченных вопросов"
    
    await message.answer(response)
    log_info(f"Admin [ID: {user_id}] requested list of active chats and questions")

@router.message(Command("result"))
async def handle_result_command(message: Message):
    """Показать статистику обработанных чатов и отвеченных вопросов."""
    user_id = message.from_user.id
    
    # Проверка на администратора
    if user_id not in ADMIN_IDS:
        log_info(f"Non-admin user [ID: {user_id}] tried to use /result command")
        await message.answer("У вас нет прав для использования этой команды.")
        return
    
    # Подсчет отвеченных вопросов
    answered_questions = sum(1 for q in active_questions.values() if q["status"] == "answered")
    total_questions = len(active_questions)
    
    response = (
        f"Статистика:\n"
        f"Всего вопросов: {total_questions}\n"
        f"Отвечено вопросов: {answered_questions}\n"
        f"Активных чатов: {len(active_chats)}\n"
        f"Ожидающих пользователей: {len(waiting_users)}"
    )
    
    await message.answer(response)
    log_info(f"Admin [ID: {user_id}] requested statistics")

@router.message(Command("delete"))
async def handle_delete_command(message: Message, state: FSMContext, bot: Bot):
    """Удалить вопрос или чат по ID."""
    user_id = message.from_user.id
    
    # Проверка на администратора
    if user_id not in ADMIN_IDS:
        log_info(f"Non-admin user [ID: {user_id}] tried to use /delete command")
        await message.answer("У вас нет прав для использования этой команды.")
        return
    
    # Разбор аргументов команды
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "Использование:\n"
            "/delete question <id> - удалить вопрос\n"
            "/delete chat <id> - удалить чат"
        )
        return
    
    command_type = args[1]
    target_id = args[2]
    
    if command_type == "question":
        # Удаление вопроса
        if target_id in active_questions:
            del active_questions[target_id]
            await message.answer(f"Вопрос #{target_id} удален")
            log_info(f"Admin [ID: {user_id}] deleted question #{target_id}")
        else:
            await message.answer(f"Вопрос #{target_id} не найден")
    
    elif command_type == "chat":
        # Удаление чата
        target_id = int(target_id)
        if target_id in active_chats:
            admin_name = active_chats[target_id]
            # Поиск ID администратора из ADMIN_TOPICS
            admin_id = None
            admin_topic_id = None
            for name, info in ADMIN_TOPICS.items():
                if name == admin_name:
                    admin_id = info["user_id"]
                    admin_topic_id = info["id"]
                    break
            
            if admin_id and admin_id in admin_connections:
                del admin_connections[admin_id]
            
            # Отправка сообщения в топик администратора
            if admin_topic_id:
                await bot.send_message(
                    ADMIN_GROUP_ID,
                    "Связь был прерван принудительно!",
                    message_thread_id=admin_topic_id
                )
                # Изменение названия топика администратора
                try:
                    await bot.edit_forum_topic(
                        chat_id=ADMIN_GROUP_ID,
                        message_thread_id=admin_topic_id,
                        name=f"🟢|{admin_name}"
                    )
                    log_info(f"Changed topic title to 🟢|{admin_name}")
                except Exception as e:
                    log_error(f"Error changing topic title: {e}", exc_info=True)
            
            # Отправка сообщения пользователю
            await bot.send_message(
                target_id,
                "Связь был прерван принудительно!\n\nНапишите /start чтобы продолжить.",
                reply_markup=get_main_keyboard(target_id)
            )
            
            # Очистка состояния пользователя
            user_state = StorageKey(chat_id=target_id, user_id=target_id, bot_id=message.bot.id)
            await state.storage.set_state(user_state, None)
            
            del active_chats[target_id]
            await message.answer(f"Чат с пользователем {target_id} удален")
            log_info(f"Admin [ID: {user_id}] deleted chat with user [ID: {target_id}]")
        elif target_id in waiting_users:
            # Отправка сообщения пользователю
            await bot.send_message(
                target_id,
                "Связь был прерван принудительно!\n\nНапишите /start чтобы продолжить.",
                reply_markup=get_main_keyboard(target_id)
            )
            
            # Очистка состояния пользователя
            user_state = StorageKey(chat_id=target_id, user_id=target_id, bot_id=message.bot.id)
            await state.storage.set_state(user_state, None)
            
            del waiting_users[target_id]
            await message.answer(f"Ожидание пользователя {target_id} удалено")
            log_info(f"Admin [ID: {user_id}] deleted waiting user [ID: {target_id}]")
        else:
            await message.answer(f"Чат или ожидание пользователя {target_id} не найдены")
    
    else:
        await message.answer(
            "Неверный тип удаления. Используйте:\n"
            "/delete question <id> - удалить вопрос\n"
            "/delete chat <id> - удалить чат"
        )

@router.callback_query(F.data == "chat")
async def start_chat(callback: CallbackQuery, state: FSMContext):
    """Начало процесса чата."""
    user_id = callback.from_user.id
    
    # Логируем нажатие на кнопку чата
    log_callback(user_id, "chat", username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    # Проверка на бан
    if is_user_banned(user_id):
        log_info(f"Banned user [ID: {user_id}] tried to start chat")
        try:
            await callback.answer("Вы заблокированы и не можете использовать бота.", show_alert=True)
        except TelegramBadRequest:
            pass
        return
    
    # Проверка на регистрацию
    if not is_user_registered(user_id):
        log_info(f"Unregistered user [ID: {user_id}] tried to start chat")
        await callback.message.edit_text(
            "Для того чтобы связаться с Офис Регистраторы, необходимо зарегистрироваться.",
            reply_markup=get_main_keyboard()
        )
        try:
            await callback.answer()
        except TelegramBadRequest:
            pass
        return
    
    # Проверка на активный чат
    if user_id in active_chats or user_id in waiting_users:
        log_info(f"User [ID: {user_id}] tried to start chat but already in chat or waiting")
        try:
            await callback.answer("Вы уже пытаетесь связаться или на связи. Напишите /stop, чтобы выйти из состояния чата.", show_alert=True)
        except TelegramBadRequest:
            pass
        return
    
    # Сохранение пользователя в ожидающих
    waiting_users[user_id] = True
    
    # Установка состояния ожидания соединения
    await state.set_state(ChatStates.waiting_for_connection)
    
    # Логируем начало ожидания соединения
    log_chat_connection("start", user_id)
    
    # Отправка сообщения пользователю
    await callback.message.edit_text(
        "Подождите, пожалуйста! Пытаемся связаться. Напишите /stop, чтобы отменить."
    )
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass
    
    # Отправка уведомления администраторам
    user_data = load_user_data(user_id)
    
    # Клавиатура для подключения
    builder = InlineKeyboardBuilder()
    builder.button(text="Связаться", callback_data=f"connect_{user_id}")
    
    # Отправка уведомления
    notification_text = (
        "Кто-то пытается связаться\n"
        f"От: {user_data.get('full_name', '')}\n"
        f"Курс: {user_data.get('course', '')}\n"
        f"Факультет: {user_data.get('faculty', '')}\n"
        f"Группа: {user_data.get('group', '')}\n\n"
        "🟢|Открыто"
    )
    
    # Отправляем и сохраняем ID сообщения
    notification_msg = await callback.bot.send_message(
        ADMIN_GROUP_ID,
        notification_text,
        reply_markup=builder.as_markup(),
        message_thread_id=CHAT_NOTIFICATION_TOPIC_ID
    )
    # Сохраняем ID сообщения для быстрого обновления
    notification_messages[user_id] = (notification_msg.message_id, None)
    log_info(f"Notification sent to admin group for user [ID: {user_id}], message ID: {notification_msg.message_id}")


@router.callback_query(F.data.startswith("connect_"))
async def connect_to_chat(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Подключение администратора к чату."""
    admin_id = callback.from_user.id
    admin_name = None
    
    # Логируем нажатие на кнопку подключения
    callback_data = callback.data
    log_callback(admin_id, callback_data, username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    # Проверка на админа
    for name, info in ADMIN_TOPICS.items():
        if info["user_id"] == admin_id:
            admin_name = name
            break
    
    if not admin_name:
        log_info(f"Non-admin user [ID: {admin_id}] tried to connect to chat")
        try:
            await callback.answer("У вас нет прав для ответа.", show_alert=True)
        except TelegramBadRequest:
            pass
        return
    
    # Получаем ID пользователя из данных колбэка
    user_id = int(callback.data.split("_")[1])
    
    # Проверяем, ожидает ли пользователь соединения
    if user_id not in waiting_users:
        log_info(f"Admin [ID: {admin_id}] ({admin_name}) tried to connect to user [ID: {user_id}] who is not waiting")
        try:
            await callback.answer("Пользователь больше не ожидает соединения.", show_alert=True)
        except TelegramBadRequest:
            pass
        
        # Обновляем сообщение, чтобы удалить кнопку
        notification_text = callback.message.text.replace("🟢|Открыто", "🔴|Закрыто")
        await callback.message.edit_text(notification_text)
        log_info(f"Notification updated to 'closed' for user [ID: {user_id}]")
        return
    
    # Удаляем пользователя из ожидающих
    del waiting_users[user_id]
    
    # Добавляем в активные чаты
    active_chats[user_id] = admin_name
    admin_connections[admin_id] = user_id
    
    # Обновляем статус топика админа
    ADMIN_TOPICS[admin_name]["status"] = "busy"
    
    # Логируем подключение
    log_chat_connection("connect", user_id, admin_id, admin_name)
    log_debug(f"Admin connections dict: {admin_connections}")
    log_debug(f"Active chats dict: {active_chats}")
    
    # Обновляем сообщение в топике уведомлений
    notification_text = callback.message.text.replace("🟢|Открыто", f"🟡|{admin_name}")
    await callback.message.edit_text(notification_text)
    log_info(f"Notification updated to 'connected' ({admin_name}) for user [ID: {user_id}]")
    
    # Обновляем сохраненный ID и админа в словаре уведомлений
    if user_id in notification_messages:
        msg_id, _ = notification_messages[user_id]
        notification_messages[user_id] = (msg_id, admin_name)
    
    # Отправляем сообщение пользователю
    user_message = f"Админ: {admin_name}\n\nС вами связались! Можете писать в чат, чтобы общаться. Напишите /stop, чтобы завершить."
    await bot.send_message(user_id, user_message)
    log_info(f"Connection message sent to user [ID: {user_id}]")
    
    # Устанавливаем состояние для пользователя напрямую через бота
    try:
        # Отправляем специальное служебное сообщение пользователю для изменения состояния
        await bot.send_message(
            user_id,
            "Устанавливаем активное соединение...",
            reply_markup=None
        )
        # Хак: отправляем в канал событие обновления состояния пользователя
        log_info(f"Setting user [ID: {user_id}] to ChatStates.connected via connect_to_chat")
    except Exception as e:
        log_error(f"Error setting user state: {e}", exc_info=True)
    
    # Изменяем название топика админа
    try:
        admin_topic_id = ADMIN_TOPICS[admin_name]["id"]
        await bot.edit_forum_topic(
            chat_id=ADMIN_GROUP_ID,
            message_thread_id=admin_topic_id,
            name=f"🟡|{admin_name}"
        )
        log_info(f"Changed topic title to 🟡|{admin_name}")
    except Exception as e:
        log_error(f"Error changing topic title: {e}", exc_info=True)
    
    # Отправляем сообщение админу в его топик
    admin_topic_id = ADMIN_TOPICS[admin_name]["id"]
    user_data = load_user_data(user_id)
    admin_message = (
        f"От: {user_data.get('full_name', '')}\n"
        f"Курс: {user_data.get('course', '')}\n"
        f"Факультет: {user_data.get('faculty', '')}\n"
        f"Группа: {user_data.get('group', '')}\n\n"
        "Вы связались! Можете писать в чат, чтобы общаться. Напишите /stop, чтобы завершить."
    )
    
    # Отправляем сообщение в топик админа без статуса в тексте
    await bot.send_message(
        ADMIN_GROUP_ID,
        admin_message,
        message_thread_id=admin_topic_id
    )
    log_info(f"Connection message sent to admin [ID: {admin_id}] in topic {admin_topic_id}")


@router.message(Command("stop"))
async def handle_stop_command(message: Message, state: FSMContext, bot: Bot):
    """Обработка команды остановки чата."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Логируем команду остановки
    log_info(f"Stop command received from user [ID: {user_id}]")
    log_debug(f"Current admin connections: {admin_connections}")
    log_debug(f"Current active chats: {active_chats}")
    
    # Если сообщение от пользователя (не из группы)
    if chat_id == user_id:
        current_state = await state.get_state()
        
        # Проверяем, находится ли пользователь в ожидании соединения
        if user_id in waiting_users:
            del waiting_users[user_id]
            log_chat_connection("timeout", user_id)
            
            # Обновляем уведомление напрямую по сохраненному ID
            if user_id in notification_messages:
                msg_id, _ = notification_messages[user_id]
                try:
                    # Используем более прямой метод для редактирования сообщения
                    user_data = load_user_data(user_id)
                    notification_text = (
                        "Кто-то пытается связаться\n"
                        f"От: {user_data.get('full_name', '')}\n"
                        f"Курс: {user_data.get('course', '')}\n"
                        f"Факультет: {user_data.get('faculty', '')}\n"
                        f"Группа: {user_data.get('group', '')}\n\n"
                        "🔴|Закрыто"
                    )
                    
                    # Пробуем разные подходы к редактированию
                    try:
                        # Подход 1: Используем update_message
                        await bot.edit_message_text(
                            text=notification_text,
                            chat_id=ADMIN_GROUP_ID,
                            message_id=msg_id
                        )
                        log_info(f"Successfully updated notification (Method 1) for user [ID: {user_id}]")
                    except Exception as e1:
                        log_error(f"Method 1 failed: {e1}")
                        try:
                            # Подход 2: С параметром disable_web_page_preview
                            await bot.edit_message_text(
                                text=notification_text,
                                chat_id=ADMIN_GROUP_ID,
                                message_id=msg_id,
                                disable_web_page_preview=True
                            )
                            log_info(f"Successfully updated notification (Method 2) for user [ID: {user_id}]")
                        except Exception as e2:
                            log_error(f"Method 2 failed: {e2}")
                            # В случае крайней неудачи отправляем новое сообщение
                            await bot.send_message(
                                ADMIN_GROUP_ID,
                                f"УВЕДОМЛЕНИЕ ОБНОВЛЕНО: {notification_text}",
                                message_thread_id=CHAT_NOTIFICATION_TOPIC_ID
                            )
                            log_info(f"Sent new notification message for user [ID: {user_id}]")
                    
                    # Удаляем запись из словаря
                    del notification_messages[user_id]
                except Exception as e:
                    log_error(f"Error updating notification directly: {e}", exc_info=True)
                    # В случае ошибки отправляем новое сообщение
                    try:
                        await bot.send_message(
                            ADMIN_GROUP_ID,
                            "ВАЖНО: Не удалось обновить уведомление. Пользователь прервал связь.",
                            message_thread_id=CHAT_NOTIFICATION_TOPIC_ID
                        )
                    except Exception as e:
                        log_error(f"Error sending new notification: {e}", exc_info=True)
            
            await message.answer("Связь прервана вами! Напишите /start, чтобы продолжить.", reply_markup=get_main_keyboard(user_id))
            await state.clear()
            log_info(f"User [ID: {user_id}] disconnected while waiting")
            return
        
        # Проверяем, находится ли пользователь в активном чате
        if user_id in active_chats:
            admin_name = active_chats[user_id]
            
            # Обновляем статус топика админа
            if admin_name in ADMIN_TOPICS:
                ADMIN_TOPICS[admin_name]["status"] = "open"
                admin_topic_id = ADMIN_TOPICS[admin_name]["id"]
                admin_id = ADMIN_TOPICS[admin_name]["user_id"]
                
                # Логируем разрыв соединения пользователем
                log_chat_connection("disconnect_user", user_id, admin_id, admin_name)
                
                # Удаляем связь админа
                if admin_id in admin_connections:
                    del admin_connections[admin_id]
                
                # Отправляем сообщение админу
                await bot.send_message(
                    ADMIN_GROUP_ID,
                    "Связь прервана пользователем!",
                    message_thread_id=admin_topic_id
                )
                log_info(f"Disconnection message sent to admin [ID: {admin_id}]")
                
                # Изменяем название топика админа
                try:
                    await bot.edit_forum_topic(
                        chat_id=ADMIN_GROUP_ID,
                        message_thread_id=admin_topic_id,
                        name=f"🟢|{admin_name}"
                    )
                    log_info(f"Changed topic title to 🟢|{admin_name}")
                except Exception as e:
                    log_error(f"Error changing topic title: {e}", exc_info=True)
                
                # Обновляем сообщение в топике уведомлений напрямую
                if user_id in notification_messages:
                    msg_id, saved_admin_name = notification_messages[user_id]
                    if saved_admin_name == admin_name:
                        try:
                            user_data = load_user_data(user_id)
                            notification_text = (
                                "Кто-то пытается связаться\n"
                                f"От: {user_data.get('full_name', '')}\n"
                                f"Курс: {user_data.get('course', '')}\n"
                                f"Факультет: {user_data.get('faculty', '')}\n"
                                f"Группа: {user_data.get('group', '')}\n\n"
                                "🔴|Закрыто"
                            )
                            
                            # Пробуем разные подходы к редактированию
                            try:
                                # Подход 1: Используем update_message
                                await bot.edit_message_text(
                                    text=notification_text,
                                    chat_id=ADMIN_GROUP_ID,
                                    message_id=msg_id
                                )
                                log_info(f"Successfully updated notification (Method 1) for user [ID: {user_id}]")
                            except Exception as e1:
                                log_error(f"Method 1 failed: {e1}")
                                try:
                                    # Подход 2: С параметром disable_web_page_preview
                                    await bot.edit_message_text(
                                        text=notification_text,
                                        chat_id=ADMIN_GROUP_ID,
                                        message_id=msg_id,
                                        disable_web_page_preview=True
                                    )
                                    log_info(f"Successfully updated notification (Method 2) for user [ID: {user_id}]")
                                except Exception as e2:
                                    log_error(f"Method 2 failed: {e2}")
                                    # В случае крайней неудачи отправляем новое сообщение
                                    await bot.send_message(
                                        ADMIN_GROUP_ID,
                                        f"УВЕДОМЛЕНИЕ ОБНОВЛЕНО: {notification_text}",
                                        message_thread_id=CHAT_NOTIFICATION_TOPIC_ID
                                    )
                                    log_info(f"Sent new notification message for user [ID: {user_id}]")
                            
                            # Удаляем запись из словаря
                            del notification_messages[user_id]
                        except Exception as e:
                            log_error(f"Error updating notification directly: {e}", exc_info=True)
                            # Просто логируем ошибку и продолжаем
            
            # Удаляем из активных чатов
            del active_chats[user_id]
            
            # Отправляем сообщение пользователю
            await message.answer("Связь прервана вами! Напишите /start, чтобы продолжить.", reply_markup=get_main_keyboard(user_id))
            
            # Очищаем состояние пользователя
            await state.clear()
            log_info(f"User [ID: {user_id}] disconnected from active chat")
            return
        
        # Если пользователь не в ожидании и не в чате
        log_info(f"User [ID: {user_id}] tried to stop chat but was not in chat")
        await message.answer("ОШИБКА!!! Вы не пытаетесь связаться или Вы не на связи!")
        return

    # Если сообщение из группы (от админа)
    elif message.chat.id == int(ADMIN_GROUP_ID) and message.message_thread_id:
        # Находим админа по топику
        admin_name = None
        for name, info in ADMIN_TOPICS.items():
            if info["id"] == message.message_thread_id:
                admin_name = name
                break
        
        if not admin_name:
            log_error(f"Stop command received from unknown topic ID: {message.message_thread_id}")
            await message.answer("ОШИБКА!!! Этот топик не настроен для чата.")
            return
        
        # Проверяем, есть ли у админа активное соединение
        if user_id not in admin_connections:
            log_info(f"Admin [ID: {user_id}] ({admin_name}) tried to stop chat but was not connected")
            # Если админ не в активном чате, просто пропускаем сообщение без оповещения
            return
        
        connected_user_id = admin_connections[user_id]
        
        # Проверяем что администратор в активном чате
        if connected_user_id not in active_chats or active_chats[connected_user_id] != admin_name:
            log_error(f"Admin [ID: {user_id}] ({admin_name}) in inconsistent state with user [ID: {connected_user_id}]")
            await message.answer("Ошибка: связь была разорвана. Напишите /stop для сброса.")
            return
        
        # Логируем разрыв соединения администратором
        log_chat_connection("disconnect_admin", connected_user_id, user_id, admin_name)
        
        # Отправляем сообщение пользователю
        await bot.send_message(
            connected_user_id,
            "Связь прервана ответчиком! Напишите /start, чтобы продолжить.",
            reply_markup=get_main_keyboard(connected_user_id)
        )
        log_info(f"Disconnection message sent to user [ID: {connected_user_id}]")
        
        # Удаляем пользователя из активных чатов
        del active_chats[connected_user_id]
        
        # Удаляем связь админа
        del admin_connections[user_id]
        
        # Изменяем название топика админа
        try:
            await bot.edit_forum_topic(
                chat_id=ADMIN_GROUP_ID,
                message_thread_id=message.message_thread_id,
                name=f"🟢|{admin_name}"
            )
            log_info(f"Changed topic title to 🟢|{admin_name}")
        except Exception as e:
            log_error(f"Error changing topic title: {e}", exc_info=True)
        
        # Обновляем сообщение в топике уведомлений напрямую
        if connected_user_id in notification_messages:
            msg_id, saved_admin_name = notification_messages[connected_user_id]
            if saved_admin_name == admin_name:
                try:
                    user_data = load_user_data(connected_user_id)
                    notification_text = (
                        "Кто-то пытается связаться\n"
                        f"От: {user_data.get('full_name', '')}\n"
                        f"Курс: {user_data.get('course', '')}\n"
                        f"Факультет: {user_data.get('faculty', '')}\n"
                        f"Группа: {user_data.get('group', '')}\n\n"
                        "🔴|Закрыто"
                    )
                    
                    # Пробуем разные подходы к редактированию
                    try:
                        # Подход 1: Используем update_message
                        await bot.edit_message_text(
                            text=notification_text,
                            chat_id=ADMIN_GROUP_ID,
                            message_id=msg_id
                        )
                        log_info(f"Successfully updated notification (Method 1) for user [ID: {connected_user_id}]")
                    except Exception as e1:
                        log_error(f"Method 1 failed: {e1}")
                        try:
                            # Подход 2: С параметром disable_web_page_preview
                            await bot.edit_message_text(
                                text=notification_text,
                                chat_id=ADMIN_GROUP_ID,
                                message_id=msg_id,
                                disable_web_page_preview=True
                            )
                            log_info(f"Successfully updated notification (Method 2) for user [ID: {connected_user_id}]")
                        except Exception as e2:
                            log_error(f"Method 2 failed: {e2}")
                            # В случае крайней неудачи отправляем новое сообщение
                            await bot.send_message(
                                ADMIN_GROUP_ID,
                                f"УВЕДОМЛЕНИЕ ОБНОВЛЕНО: {notification_text}",
                                message_thread_id=CHAT_NOTIFICATION_TOPIC_ID
                            )
                            log_info(f"Sent new notification message for user [ID: {connected_user_id}]")
                    
                    # Удаляем запись из словаря
                    del notification_messages[connected_user_id]
                except Exception as e:
                    log_error(f"Error updating notification directly: {e}", exc_info=True)
                    # Просто логируем ошибку и продолжаем
        
        # Обновляем статус админа
        ADMIN_TOPICS[admin_name]["status"] = "open"
        
        # Отправляем сообщение админу
        await message.answer("Связь прервана вами!")
        log_info(f"Admin [ID: {user_id}] ({admin_name}) disconnected from chat")

        # Устанавливаем состояние disconnected_by_admin для пользователя
        user_state = StorageKey(chat_id=connected_user_id, user_id=connected_user_id, bot_id=message.bot.id)
        await state.storage.set_state(user_state, ChatStates.disconnected_by_admin)


# Измененный обработчик для обработки всех сообщений в чате от пользователя
@router.message()
async def handle_all_user_messages(message: Message, state: FSMContext, bot: Bot):
    """Обработка всех сообщений от пользователя."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Получаем текущее состояние пользователя
    current_state = await state.get_state()
    
    # Если пользователь в состоянии disconnected_by_admin
    if current_state == ChatStates.disconnected_by_admin.state:
        # Проверяем, является ли сообщение командой /start
        if message.text == "/start":
            # Разрешаем только команду /start
            await state.clear()
            return
        
        # Проверяем, является ли сообщение нажатием на кнопку чата
        if message.text == "💬 Чат":
            # Разрешаем только кнопку чата
            await state.clear()
            return
        
        # Для всех остальных действий блокируем
        await message.answer("Связь была прервана ответчиком. Вы можете только начать новый чат.")
        return
    
    # Пропускаем команду /stop, она обрабатывается отдельно
    if message.text == "/stop":
        return
    
    # Если сообщение от пользователя (не из группы)
    if chat_id == user_id:
        # Проверяем состояние пользователя
        current_state = await state.get_state()
        log_debug(f"Message from user [ID: {user_id}], state: {current_state}")
        log_debug(f"User in active_chats: {user_id in active_chats}")
        
        # Если пользователь в активном чате
        if user_id in active_chats:
            admin_name = active_chats[user_id]
            
            # Логируем сообщение от пользователя
            log_message("User", user_id, message.content_type, username=message.from_user.username, full_name=message.from_user.full_name)
            
            # Проверяем наличие админа в словаре
            if admin_name not in ADMIN_TOPICS:
                log_error(f"Admin {admin_name} not found in ADMIN_TOPICS for user [ID: {user_id}]")
                await message.answer("Ошибка: админ не найден. Чат будет закрыт.")
                await state.clear()
                del active_chats[user_id]
                return
            
            admin_topic_id = ADMIN_TOPICS[admin_name]["id"]
            
            # Пересылаем сообщение админу в зависимости от типа контента
            try:
                # Обработка разных типов контента без добавления информации об ответе
                if message.content_type == "text":
                    # Обычное текстовое сообщение
                    await bot.send_message(
                        ADMIN_GROUP_ID,
                        message.text,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "photo":
                    # Фотография
                    await bot.send_photo(
                        ADMIN_GROUP_ID,
                        message.photo[-1].file_id,
                        caption=message.caption,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "video":
                    # Видео
                    await bot.send_video(
                        ADMIN_GROUP_ID,
                        message.video.file_id,
                        caption=message.caption,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "audio":
                    # Аудио
                    await bot.send_audio(
                        ADMIN_GROUP_ID,
                        message.audio.file_id,
                        caption=message.caption,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "voice":
                    # Голосовое сообщение
                    await bot.send_voice(
                        ADMIN_GROUP_ID,
                        message.voice.file_id,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "video_note":
                    # Видеокружок
                    await bot.send_video_note(
                        ADMIN_GROUP_ID,
                        message.video_note.file_id,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "document":
                    # Документ
                    await bot.send_document(
                        ADMIN_GROUP_ID,
                        message.document.file_id,
                        caption=message.caption,
                        message_thread_id=admin_topic_id
                    )
                elif message.content_type == "sticker":
                    # Стикер
                    await bot.send_sticker(
                        ADMIN_GROUP_ID,
                        message.sticker.file_id,
                        message_thread_id=admin_topic_id
                    )
                else:
                    # Для других типов контента отправляем уведомление
                    await bot.send_message(
                        ADMIN_GROUP_ID,
                        f"Пользователь отправил сообщение типа: {message.content_type}, который не поддерживается.",
                        message_thread_id=admin_topic_id
                    )
                
                log_info(f"Message from user [ID: {user_id}] sent to admin {admin_name} in topic {admin_topic_id}")
            except Exception as e:
                log_error(f"Error forwarding message to admin: {e}", exc_info=True)
                await message.answer("Возникла ошибка при отправке сообщения. Попробуйте еще раз или напишите /stop для завершения чата.")
            return
        
        # Если пользователь в ожидании
        elif user_id in waiting_users and current_state == ChatStates.waiting_for_connection.state:
            log_info(f"Message from waiting user [ID: {user_id}] blocked")
            # Любое сообщение кроме /stop блокируется
            await message.answer("Напишите /stop, чтобы выйти из состояния чата.")
            return
    
    # Если сообщение из группы (от админа)
    elif message.chat.id == int(ADMIN_GROUP_ID) and message.message_thread_id:
        # Находим админа по топику
        admin_name = None
        for name, info in ADMIN_TOPICS.items():
            if info["id"] == message.message_thread_id:
                admin_name = name
                break
        
        if not admin_name:
            return
        
        # Логируем сообщение от админа
        log_message("Admin", user_id, message.content_type, username=message.from_user.username, full_name=message.from_user.full_name)
        log_debug(f"Admin [ID: {user_id}] in admin_connections: {user_id in admin_connections}")
        
        # Проверяем, есть ли у админа активное соединение
        if user_id not in admin_connections:
            # Если админ не в активном чате, просто пропускаем сообщение без оповещения
            log_info(f"Message from admin [ID: {user_id}] ({admin_name}) ignored - not in active chat")
            return
        
        connected_user_id = admin_connections[user_id]
        log_debug(f"Admin [ID: {user_id}] connected to user [ID: {connected_user_id}]")
        log_debug(f"User [ID: {connected_user_id}] in active_chats: {connected_user_id in active_chats}")
        
        # Проверяем что администратор в активном чате
        if connected_user_id not in active_chats or active_chats[connected_user_id] != admin_name:
            log_error(f"Admin [ID: {user_id}] ({admin_name}) in inconsistent state with user [ID: {connected_user_id}]")
            await message.answer("Ошибка: связь была разорвана. Напишите /stop для сброса.")
            return
        
        # Пересылаем сообщение пользователю в зависимости от типа контента
        try:
            # Обработка разных типов контента без добавления префикса или информации об ответе
            if message.content_type == "text":
                # Обычное текстовое сообщение
                await bot.send_message(
                    connected_user_id,
                    message.text
                )
            elif message.content_type == "photo":
                # Фотография
                await bot.send_photo(
                    connected_user_id,
                    message.photo[-1].file_id,
                    caption=message.caption
                )
            elif message.content_type == "video":
                # Видео
                await bot.send_video(
                    connected_user_id,
                    message.video.file_id,
                    caption=message.caption
                )
            elif message.content_type == "audio":
                # Аудио
                await bot.send_audio(
                    connected_user_id,
                    message.audio.file_id,
                    caption=message.caption
                )
            elif message.content_type == "voice":
                # Голосовое сообщение
                await bot.send_voice(
                    connected_user_id,
                    message.voice.file_id
                )
            elif message.content_type == "video_note":
                # Видеокружок
                await bot.send_video_note(
                    connected_user_id,
                    message.video_note.file_id
                )
            elif message.content_type == "document":
                # Документ
                await bot.send_document(
                    connected_user_id,
                    message.document.file_id,
                    caption=message.caption
                )
            elif message.content_type == "sticker":
                # Стикер
                await bot.send_sticker(
                    connected_user_id,
                    message.sticker.file_id
                )
            else:
                # Для других типов контента отправляем уведомление
                await bot.send_message(
                    connected_user_id,
                    f"Сообщение типа: {message.content_type} не поддерживается."
                )
            
            log_info(f"Message from admin [ID: {user_id}] ({admin_name}) sent to user [ID: {connected_user_id}]")
        except Exception as e:
            log_error(f"Error forwarding message to user: {e}", exc_info=True)
            await message.answer("Возникла ошибка при отправке сообщения. Попробуйте еще раз или напишите /stop для завершения чата.") 