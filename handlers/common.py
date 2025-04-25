from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from utils.file_operations import is_user_banned, get_user_language, set_user_language
from utils.keyboards import get_main_keyboard, get_language_selection_keyboard
from utils.messages import get_message
from states.chat import ChatStates
from states.language import LanguageStates

# Создание роутера
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start."""
    user_id = message.from_user.id
    
    if is_user_banned(user_id):
        await message.answer(get_message("banned_user", get_user_language(user_id)))
        return
    
    # Проверка на состояние чата
    current_state = await state.get_state()
    if current_state in [ChatStates.waiting_for_connection.state, ChatStates.connected.state]:
        await message.answer(get_message("exit_chat_first", get_user_language(user_id)))
        return
    
    # Устанавливаем состояние выбора языка
    await state.set_state(LanguageStates.selecting_language)
    
    await message.answer(
        get_message("select_language", "ru"),  # Используем триязычное сообщение
        reply_markup=get_language_selection_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора языка."""
    user_id = callback.from_user.id
    language = callback.data.split("_")[1]  # Извлекаем код языка из callback_data
    
    # Сохраняем выбранный язык
    set_user_language(user_id, language)
    
    # Получаем сообщение о выборе языка
    language_message = get_message("language_selected", language)
    welcome_message = get_message("welcome", language)
    
    # Очищаем состояние
    await state.clear()
    
    # Отправляем сообщение о выборе языка
    await callback.message.edit_text(
        f"{language_message}\n\n{welcome_message}",
        reply_markup=get_main_keyboard(user_id)
    )
    
    try:
        await callback.answer()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Отображение главного меню."""
    user_id = callback.from_user.id
    language = get_user_language(user_id)
    
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
    
    # Очищаем состояние
    await state.clear()
        
    await callback.message.edit_text(
        get_message("select_option", language),
        reply_markup=get_main_keyboard(user_id)
    )
    try:
        await callback.answer()
    except TelegramBadRequest:
        # Игнорируем ошибку, если callback query устарел
        pass


@router.message(Command("language"))
async def cmd_language(message: Message, state: FSMContext):
    """Обработка команды /language для смены языка."""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    if is_user_banned(user_id):
        await message.answer(get_message("banned_user", language))
        return
    
    # Проверка на состояние чата
    current_state = await state.get_state()
    if current_state in [ChatStates.waiting_for_connection.state, ChatStates.connected.state]:
        await message.answer(get_message("exit_chat_first", language))
        return
    
    # Устанавливаем состояние выбора языка
    await state.set_state(LanguageStates.selecting_language)
    
    await message.answer(
        get_message("select_language", "ru"),  # Используем триязычное сообщение
        reply_markup=get_language_selection_keyboard()
    ) 