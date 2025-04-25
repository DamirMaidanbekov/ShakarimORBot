import json
import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from states.registration import RegistrationStates
from states.chat import ChatStates
from utils.file_operations import is_user_registered, save_user_data, is_user_banned, get_user_language
from utils.keyboards import get_main_keyboard, get_back_keyboard, get_auth_keyboards
from utils.logger import log_info, log_error, log_callback, log_registration
from utils.messages import get_message

# Создание роутера
router = Router()


@router.callback_query(F.data == "register")
async def register_command(callback: CallbackQuery, state: FSMContext):
    """Начало процесса регистрации"""
    # Логируем нажатие на кнопку регистрации
    user_id = callback.from_user.id
    language = get_user_language(user_id)
    log_callback(user_id, "register", username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    print(f"DEBUG: Registration button clicked by user {user_id}")
    
    if is_user_banned(user_id):
        try:
            await callback.answer(get_message("banned_user", language), show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return
    
    # Проверка на состояние чата
    current_state = await state.get_state()
    if current_state in [ChatStates.waiting_for_connection.state, ChatStates.connected.state]:
        try:
            await callback.answer(get_message("exit_chat_first", language), show_alert=True)
        except TelegramBadRequest:
            pass
        return
        
    # Проверяем, зарегистрирован ли пользователь
    if is_user_registered(user_id):
        log_info(f"User [ID: {user_id}] tried to register again")
        await callback.message.edit_text(
            get_message("already_registered", language),
            reply_markup=get_main_keyboard(user_id)
        )
        try:
            await callback.answer()
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    log_info(f"User [ID: {user_id}] started registration process")
    # Начало процесса регистрации
    await callback.message.edit_text(
        get_message("enter_name", language)
    )
    await state.set_state(RegistrationStates.full_name)
    try:
        await callback.answer()
    except TelegramBadRequest:
        # Игнорируем ошибку, если callback query устарел
        pass


@router.message(RegistrationStates.full_name)
async def process_name(message: Message, state: FSMContext):
    """Сохранение имени и запрос курса"""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    full_name = message.text
    
    # Проверяем ввод
    if not full_name or full_name.strip() == "":
        log_error(f"User [ID: {user_id}] entered invalid name: '{full_name}'")
        await message.answer(get_message("enter_name", language))
        return
    
    log_info(f"User [ID: {user_id}] entered name: {full_name}")
    
    # Сохраняем имя в состоянии
    await state.update_data(full_name=full_name)
    
    # Запрашиваем курс
    await message.answer(
        get_message("enter_course", language)
    )
    await state.set_state(RegistrationStates.course)


@router.message(RegistrationStates.course)
async def process_course(message: Message, state: FSMContext):
    """Сохранение курса и запрос факультета"""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    course = message.text
    
    # Проверяем ввод курса
    if not course.isdigit() or int(course) < 1 or int(course) > 4:
        await message.answer(get_message("invalid_course", language))
        return
    
    # Сохраняем курс в состоянии
    await state.update_data(course=course)
    log_info(f"User [ID: {user_id}] entered course: {course}")
    
    # Запрашиваем факультет
    await message.answer(
        get_message("enter_faculty", language)
    )
    await state.set_state(RegistrationStates.faculty)


@router.message(RegistrationStates.faculty)
async def process_faculty(message: Message, state: FSMContext):
    """Сохранение факультета и запрос кафедры"""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    faculty = message.text
    
    # Проверяем ввод
    if not faculty or faculty.strip() == "":
        await message.answer(get_message("invalid_faculty", language))
        return
    
    # Сохраняем факультет в состоянии
    await state.update_data(faculty=faculty)
    log_info(f"User [ID: {user_id}] entered faculty: {faculty}")
    
    # Запрашиваем кафедру
    await message.answer(
        get_message("enter_department", language)
    )
    await state.set_state(RegistrationStates.department)


@router.message(RegistrationStates.department)
async def process_department(message: Message, state: FSMContext):
    """Сохранение кафедры и запрос группы"""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    department = message.text
    
    # Проверяем ввод
    if not department or department.strip() == "":
        await message.answer(get_message("invalid_department", language))
        return
    
    # Сохраняем кафедру в состоянии
    await state.update_data(department=department)
    log_info(f"User [ID: {user_id}] entered department: {department}")
    
    # Запрашиваем группу
    await message.answer(
        get_message("enter_group", language)
    )
    await state.set_state(RegistrationStates.group)


@router.message(RegistrationStates.group)
async def process_group(message: Message, state: FSMContext):
    """Завершение регистрации"""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    group = message.text
    
    # Проверяем ввод
    if not group or group.strip() == "":
        log_error(f"User [ID: {user_id}] entered invalid group: '{group}'")
        await message.answer(get_message("invalid_group", language))
        return
    
    log_info(f"User [ID: {user_id}] entered group: {group}")
    
    # Получаем все сохраненные данные
    user_data = await state.get_data()
    user_data["group"] = group
    
    # Сохраняем данные пользователя
    user_data["username"] = message.from_user.username
    user_data["telegram_id"] = user_id  # Сохраняем telegram ID пользователя
    save_user_data(user_id, user_data)
    
    # Логируем завершение регистрации
    log_registration("complete", user_id, message.from_user.username, user_data["full_name"])
    
    log_info(f"User [ID: {user_id}] successfully completed registration")
    
    # Сначала отправляем сообщение об успешной регистрации
    await message.answer(get_message("registration_successful", language))
    
    # Затем отправляем приветственное сообщение с главным меню, как после выбора языка
    await message.answer(
        f"{get_message('welcome', language)}",
        reply_markup=get_main_keyboard(user_id)
    )
    
    # Очищаем состояние
    await state.clear() 