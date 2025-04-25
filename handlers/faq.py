from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from states.faq import FAQStates
from states.chat import ChatStates
from utils.file_operations import load_faq, is_user_banned, get_user_language
from utils.keyboards import get_main_keyboard, get_faq_list_keyboard, get_faq_back_keyboard
from utils.messages import get_message

# Создание роутера
router = Router()


@router.callback_query(F.data == "faq")
async def show_faq(callback: CallbackQuery, state: FSMContext):
    """Отображение списка часто задаваемых вопросов."""
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
    
    await state.set_state(FAQStates.waiting_for_number)
    # Загружаем FAQ для выбранного языка пользователя
    faq_data = load_faq(language)

    if not faq_data:
        # FAQ данные пусты, показываем сообщение об отсутствии FAQ
        await callback.message.edit_text(
            "В данный момент нет популярных вопросов.",
            reply_markup=get_main_keyboard(user_id)
        )
        try:
            await callback.answer()
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    # Формируем список вопросов
    faq_list = f"<b>{get_message('faq_title', language)}</b>\n\n"
    for q_id, q_data in faq_data.items():
        faq_list += f"{q_id}. {q_data['question']}\n\n"

    faq_list += f"\n{get_message('faq_question_prompt', language)}"

    await callback.message.edit_text(
        faq_list,
        reply_markup=get_faq_list_keyboard(language)
    )
    try:
        await callback.answer()
    except TelegramBadRequest:
        # Игнорируем ошибку, если callback query устарел
        pass


@router.message(F.text.regexp(r'^\d+$'), FAQStates.waiting_for_number)
async def show_selected_faq(message: Message):
    """Показ выбранного вопроса FAQ."""
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    # Загружаем FAQ для выбранного языка пользователя
    faq_data = load_faq(language)
    question_id = message.text

    if question_id not in faq_data:
        # Если вопрос не найден, уведомляем пользователя
        await message.answer(
            get_message("question_not_found", language),
            reply_markup=get_faq_list_keyboard(language)
        )
        return

    question = faq_data[question_id]["question"]
    answer = faq_data[question_id]["answer"]
    
    # Тексты на разных языках
    question_text = {
        "ru": "Вопрос",
        "kz": "Сұрақ",
        "en": "Question"
    }
    
    answer_text = {
        "ru": "Ответ",
        "kz": "Жауап",
        "en": "Answer"
    }
    
    # Выбираем правильный текст в зависимости от языка
    q_text = question_text.get(language, question_text["ru"])
    a_text = answer_text.get(language, answer_text["ru"])

    await message.answer(
        f"<b>{q_text} {question_id}:</b>\n{question}\n\n<b>{a_text}:</b>\n{answer}",
        reply_markup=get_faq_back_keyboard(language)
    )


@router.callback_query(F.data == "faq_list")
async def back_to_faq_list(callback: CallbackQuery, state: FSMContext):
    """Возврат к списку вопросов FAQ."""
    await show_faq(callback, state) 