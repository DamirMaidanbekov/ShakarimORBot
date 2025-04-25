import json
import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from states.registration import RegistrationStates
from states.chat import ChatStates
from utils.file_operations import is_user_registered, save_user_data, is_user_banned
from utils.keyboards import get_main_keyboard, get_back_keyboard, get_auth_keyboards
from utils.logger import log_info, log_error, log_callback, log_registration

# Создание роутера
router = Router()


@router.callback_query(F.data == "register")
async def register_command(callback: CallbackQuery, state: FSMContext):
    """Начало процесса регистрации"""
    # Логируем нажатие на кнопку регистрации
    user_id = callback.from_user.id
    log_callback(user_id, "register", username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    print(f"DEBUG: Registration button clicked by user {user_id}")
    
    if is_user_banned(user_id):
        try:
            await callback.answer("Вы заблокированы и не можете использовать бота.", show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return
    
    # Проверка на состояние чата
    current_state = await state.get_state()
    if current_state in [ChatStates.waiting_for_connection.state, ChatStates.connected.state]:
        try:
            await callback.answer("Напишите /stop, чтобы выйти из состояния чата.", show_alert=True)
        except TelegramBadRequest:
            pass
        return
        
    # Проверяем, зарегистрирован ли пользователь
    if is_user_registered(user_id):
        log_info(f"User [ID: {user_id}] tried to register again")
        await callback.message.edit_text(
            "Вы уже зарегистрированы.",
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
        "Пожалуйста, введите Ваше ФИО:"
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
    full_name = message.text
    
    # Проверяем ввод
    if not full_name or full_name.strip() == "":
        log_error(f"User [ID: {user_id}] entered invalid name: '{full_name}'")
        await message.answer("Пожалуйста, введите корректное ФИО.")
        return
    
    log_info(f"User [ID: {user_id}] entered name: {full_name}")
    
    # Сохраняем имя в состоянии
    await state.update_data(full_name=full_name)
    
    # Запрашиваем курс
    await message.answer(
        "Пожалуйста, введите Ваш курс (от 1 до 4):"
    )
    await state.set_state(RegistrationStates.course)


@router.message(RegistrationStates.course)
async def process_course(message: Message, state: FSMContext):
    """Сохранение курса и запрос факультета"""
    user_id = message.from_user.id
    course = message.text
    
    # Проверяем ввод курса
    if not course.isdigit() or int(course) < 1 or int(course) > 4:
        await message.answer("Пожалуйста, введите корректный курс (число от 1 до 4).")
        return
    
    # Сохраняем курс в состоянии
    await state.update_data(course=course)
    log_info(f"User [ID: {user_id}] entered course: {course}")
    
    # Запрашиваем факультет
    await message.answer(
        "Пожалуйста, введите Ваш факультет:"
    )
    await state.set_state(RegistrationStates.faculty)


@router.message(RegistrationStates.faculty)
async def process_faculty(message: Message, state: FSMContext):
    """Сохранение факультета и запрос кафедры"""
    user_id = message.from_user.id
    faculty = message.text
    
    # Проверяем ввод
    if not faculty or faculty.strip() == "":
        await message.answer("Пожалуйста, введите корректный факультет.")
        return
    
    # Сохраняем факультет в состоянии
    await state.update_data(faculty=faculty)
    log_info(f"User [ID: {user_id}] entered faculty: {faculty}")
    
    # Запрашиваем кафедру
    await message.answer(
        "Пожалуйста, введите Вашу кафедру:"
    )
    await state.set_state(RegistrationStates.department)


@router.message(RegistrationStates.department)
async def process_department(message: Message, state: FSMContext):
    """Сохранение кафедры и запрос группы"""
    user_id = message.from_user.id
    department = message.text
    
    # Проверяем ввод
    if not department or department.strip() == "":
        await message.answer("Пожалуйста, введите корректную кафедру.")
        return
    
    # Сохраняем кафедру в состоянии
    await state.update_data(department=department)
    log_info(f"User [ID: {user_id}] entered department: {department}")
    
    # Запрашиваем группу
    await message.answer(
        "Пожалуйста, введите Вашу группу (например, ПИз-200):"
    )
    await state.set_state(RegistrationStates.group)


@router.message(RegistrationStates.group)
async def process_group(message: Message, state: FSMContext):
    """Завершение регистрации"""
    user_id = message.from_user.id
    group = message.text
    
    # Проверяем ввод
    if not group or group.strip() == "":
        log_error(f"User [ID: {user_id}] entered invalid group: '{group}'")
        await message.answer("Пожалуйста, введите корректную группу.")
        return
    
    log_info(f"User [ID: {user_id}] entered group: {group}")
    
    # Получаем все сохраненные данные
    user_data = await state.get_data()
    user_data["group"] = group
    
    # Сохраняем данные пользователя
    user_data["username"] = message.from_user.username
    save_user_data(user_id, user_data)
    
    log_registration(user_id, user_data["full_name"], user_data["course"], 
                     user_data["faculty"], user_data["department"], user_data["group"],
                     username=message.from_user.username)
    log_info(f"User [ID: {user_id}] successfully completed registration")
    
    # Отправляем сообщение об успешной регистрации
    await message.answer(
        "Регистрация успешно завершена! Теперь вы можете задавать вопросы и использовать чат.",
        reply_markup=get_main_keyboard(user_id)
    )
    await state.clear() 