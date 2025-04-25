import json
import os
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

from config import ADMIN_GROUP_ID, ADMIN_IDS, QUESTION_NOTIFICATION_TOPIC_ID, QUESTION_ANSWER_TOPIC_ID, ADMIN_TOPICS
from states.question import QuestionStates
from states.chat import ChatStates
from utils.file_operations import is_user_registered, load_user_data, is_user_banned, get_user_language
from utils.keyboards import get_main_keyboard
from utils.media import save_media_file
from utils.logger import log_info, log_error, log_question, log_callback, log_message
from utils.messages import get_message

# Создание роутера
router = Router()

# Хранение активных вопросов в памяти: {question_id: {data}}
active_questions = {}
# Счетчик для генерации ID вопросов
question_counter = 1


@router.callback_query(F.data == "ask")
async def ask_question(callback: CallbackQuery, state: FSMContext):
    """Начало процесса ask"""
    user_id = callback.from_user.id
    language = get_user_language(user_id)
    
    # Логируем нажатие на кнопку
    log_callback(user_id, "ask", username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    if is_user_banned(user_id):
        log_info(f"Banned user [ID: {user_id}] tried to ask a question")
        try:
            await callback.answer(get_message("banned_user", language), show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return
    
    # Проверка на состояние чата
    current_state = await state.get_state()
    if current_state in [ChatStates.waiting_for_connection.state, ChatStates.connected.state]:
        log_info(f"User [ID: {user_id}] tried to ask a question while in chat")
        try:
            await callback.answer(get_message("exit_chat_first", language), show_alert=True)
        except TelegramBadRequest:
            pass
        return
    
    # Проверка на Регистрацию
    if not is_user_registered(user_id):
        log_info(f"Unregistered user [ID: {user_id}] tried to ask a question")
        await callback.message.edit_text(
            "Для того чтобы задать вопрос, необходимо зарегистрироваться.",
            reply_markup=get_main_keyboard()
        )
        try:
            await callback.answer()
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    log_info(f"User [ID: {user_id}] started asking a question")
    await callback.message.edit_text(get_message("ask_question", language))
    await state.set_state(QuestionStates.waiting_for_question)
    try:
        await callback.answer()
    except TelegramBadRequest:
        # Игнорируем ошибку, если callback query устарел
        pass


@router.message(QuestionStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext, bot: Bot):
    """Обработка отправленный вопрос."""
    global question_counter
    
    user_id = message.from_user.id
    language = get_user_language(user_id)
    user_data = load_user_data(user_id)
    
    # Логируем сообщение с вопросом
    log_message("Question", user_id, message.content_type, username=message.from_user.username, full_name=message.from_user.full_name)

    # Создание ID вопроса
    question_id = str(question_counter)
    question_counter += 1

    # Сохранение медиафайла, если есть
    media_info = await save_media_file(message, question_id)

    # Сохранение вопроса в памяти
    question_data = {
        "question_id": question_id,
        "user_id": user_id,
        "full_name": user_data.get("full_name", ""),
        "course": user_data.get("course", ""),
        "faculty": user_data.get("faculty", ""),
        "department": user_data.get("department", ""),
        "group": user_data.get("group", ""),
        "content_type": message.content_type,
        "text": message.text if message.content_type == "text" else None,
        "media": media_info,
        "status": "pending",
        "answer": None,
        "admin_id": None
    }

    # Сохраняем вопрос в памяти
    active_questions[question_id] = question_data
    
    # Логируем создание вопроса
    log_question("asked", question_id, user_id=user_id)

    # Отправляем подтверждение пользователю
    await message.answer(get_message("question_accepted", language).format(question_id))
    await state.clear()
    
    # Отправляем главное меню
    await message.answer(get_message("select_option", language), reply_markup=get_main_keyboard(user_id))

    # Создание клавиатуры с кнопкой ответа
    builder = InlineKeyboardBuilder()
    builder.button(text="Ответить", callback_data=f"answer_question_{question_id}")

    # Базовое сообщение с информацией о вопросе
    admin_message = (
        f"<b>Новый вопрос #{question_id}</b>\n"
        f"От: {user_data.get('full_name', '')}\n"
        f"Курс: {user_data.get('course', '')}\n"
        f"Факультет: {user_data.get('faculty', '')}\n"
        f"Группа: {user_data.get('group', '')}\n\n"
    )

    # Отправка уведомления в топик для уведомлений
    if message.content_type == "text":
        await bot.send_message(
            ADMIN_GROUP_ID,
            admin_message + f"<b>Вопрос:</b>\n{message.text}",
            message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
        )
    else:
        # Отправляем медиафайл с описанием в топик уведомлений
        if message.content_type == "photo":
            await bot.send_photo(
                ADMIN_GROUP_ID,
                message.photo[-1].file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )
        elif message.content_type == "video":
            await bot.send_video(
                ADMIN_GROUP_ID,
                message.video.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )
        elif message.content_type == "audio":
            await bot.send_audio(
                ADMIN_GROUP_ID,
                message.audio.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )
        elif message.content_type == "voice":
            await bot.send_voice(
                ADMIN_GROUP_ID,
                message.voice.file_id,
                caption=admin_message,
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )
        elif message.content_type == "video_note":
            await bot.send_video_note(
                ADMIN_GROUP_ID,
                message.video_note.file_id,
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )
        elif message.content_type == "document":
            await bot.send_document(
                ADMIN_GROUP_ID,
                message.document.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                message_thread_id=QUESTION_NOTIFICATION_TOPIC_ID
            )

    # Отправка вопроса с кнопкой ответа в топик для ответов
    if message.content_type == "text":
        await bot.send_message(
            ADMIN_GROUP_ID,
            admin_message + f"<b>Вопрос:</b>\n{message.text}",
            reply_markup=builder.as_markup(),
            message_thread_id=QUESTION_ANSWER_TOPIC_ID
        )
    else:
        # Отправляем медиафайл с описанием и кнопкой в топик ответов
        if message.content_type == "photo":
            await bot.send_photo(
                ADMIN_GROUP_ID,
                message.photo[-1].file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )
        elif message.content_type == "video":
            await bot.send_video(
                ADMIN_GROUP_ID,
                message.video.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )
        elif message.content_type == "audio":
            await bot.send_audio(
                ADMIN_GROUP_ID,
                message.audio.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )
        elif message.content_type == "voice":
            await bot.send_voice(
                ADMIN_GROUP_ID,
                message.voice.file_id,
                caption=admin_message,
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )
        elif message.content_type == "video_note":
            await bot.send_video_note(
                ADMIN_GROUP_ID,
                message.video_note.file_id,
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )
        elif message.content_type == "document":
            await bot.send_document(
                ADMIN_GROUP_ID,
                message.document.file_id,
                caption=admin_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else ""),
                reply_markup=builder.as_markup(),
                message_thread_id=QUESTION_ANSWER_TOPIC_ID
            )

    log_info(f"Question #{question_id} from user [ID: {user_id}] accepted")
    await state.clear()


@router.callback_query(F.data.startswith("answer_question_"))
async def handle_answer_button(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия кнопки ответа на вопрос."""
    admin_id = callback.from_user.id
    
    # Логируем нажатие на кнопку ответа
    callback_data = callback.data
    log_callback(admin_id, callback_data, username=callback.from_user.username, full_name=callback.from_user.full_name)
    
    if admin_id not in ADMIN_IDS:
        log_info(f"Non-admin user [ID: {admin_id}] tried to answer a question")
        try:
            await callback.answer("У вас нет прав для ответа на вопросы.", show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    question_id = callback.data.split("_")[2]

    # Проверяем существует ли вопрос
    if question_id not in active_questions:
        log_error(f"Admin [ID: {admin_id}] tried to answer non-existent question #{question_id}")
        try:
            await callback.answer("Вопрос не найден.", show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    question_data = active_questions[question_id]
    user_language = get_user_language(question_data["user_id"])

    if question_data["status"] == "answered":
        log_info(f"Admin [ID: {admin_id}] tried to answer already answered question #{question_id}")
        try:
            await callback.answer("На этот вопрос уже дан ответ.", show_alert=True)
        except TelegramBadRequest:
            # Игнорируем ошибку, если callback query устарел
            pass
        return

    # Сохранение ID админа, который будет отвечать
    question_data["admin_id"] = admin_id
    active_questions[question_id] = question_data
    
    # Получаем имя админа из ADMIN_TOPICS
    admin_name = callback.from_user.full_name
    for name, topic_info in ADMIN_TOPICS.items():
        if topic_info["user_id"] == admin_id:
            admin_name = name
            break
    
    # Логируем начало ответа на вопрос
    log_question("answer_start", question_id, admin_id=admin_id, admin_name=admin_name)

    # Установка состояния ожидания ответа
    await state.set_state(QuestionStates.waiting_for_admin_answer)
    await state.update_data(question_id=question_id)
    
    # Формируем текст вопроса
    question_text = ""
    if question_data["content_type"] == "text":
        question_text = question_data["text"]
    else:
        question_text = f"[{question_data['content_type']}]"
        if question_data["media"] and question_data["media"]["caption"]:
            question_text += f"\n<b>Подпись:</b>\n{question_data['media']['caption']}"
    
    # Переведенные сообщения для админа
    write_answer_text = {
        "ru": f"Напиши ответ {admin_name}:",
        "kz": f"{admin_name} жауап жазыңыз:",
        "en": f"Write answer {admin_name}:"
    }
    question_text_label = {
        "ru": f"<b>Вопрос #{question_id}:</b>",
        "kz": f"<b>Сұрақ #{question_id}:</b>", 
        "en": f"<b>Question #{question_id}:</b>"
    }
    
    await callback.message.edit_text(
        f"{write_answer_text.get(user_language, write_answer_text['ru'])}\n\n"
        f"{question_text_label.get(user_language, question_text_label['ru'])}\n{question_text}"
    )
    try:
        await callback.answer()
    except TelegramBadRequest:
        # Игнорируем ошибку, если callback query устарел
        pass


@router.message(QuestionStates.waiting_for_admin_answer)
async def process_admin_answer(message: Message, state: FSMContext, bot: Bot):
    """Обработка ответа администратора."""
    admin_id = message.from_user.id
    admin_name = message.from_user.full_name
    
    # Логируем ответное сообщение от админа
    log_message("Answer", admin_id, message.content_type, username=message.from_user.username, full_name=admin_name)
    
    state_data = await state.get_data()
    question_id = state_data["question_id"]

    # Проверяем существует ли вопрос
    if question_id not in active_questions:
        log_error(f"Admin [ID: {admin_id}] tried to answer non-existent question #{question_id}")
        await message.answer("Вопрос не найден.")
        await state.clear()
        return

    question_data = active_questions[question_id]
    user_id = question_data["user_id"]
    user_language = get_user_language(user_id)

    # Проверка, что отвечает тот же админ, который начал отвечать
    if question_data["admin_id"] != admin_id:
        log_error(f"Admin [ID: {admin_id}] tried to answer question #{question_id} started by another admin")
        await message.answer("Вы не можете ответить на этот вопрос.")
        await state.clear()
        return

    # Получаем имя админа из ADMIN_TOPICS
    admin_display_name = admin_name
    for name, topic_info in ADMIN_TOPICS.items():
        if topic_info["user_id"] == admin_id:
            admin_display_name = name
            break

    # Сохранение медиафайла, если есть
    media_info = await save_media_file(message, question_id)

    # Обновление данных вопроса
    question_data["status"] = "answered"
    question_data["answer"] = {
        "content_type": message.content_type,
        "text": message.text if message.content_type == "text" else None,
        "media": media_info
    }
    
    # Обновляем вопрос в памяти
    active_questions[question_id] = question_data

    # Получаем переведенные сообщения для пользователя
    answer_title = get_message("question_answer_received", user_language).split("\n")[0].format(question_id)
    question_label = {
        "ru": "<b>Вопрос:</b>",
        "kz": "<b>Сұрақ:</b>",
        "en": "<b>Question:</b>"
    }
    answer_label = {
        "ru": f"<b>Ответ от {admin_display_name}:</b>",
        "kz": f"<b>{admin_display_name} жауабы:</b>",
        "en": f"<b>Answer from {admin_display_name}:</b>"
    }
    menu_hint = {
        "ru": "\n\nЧтобы открыть меню напишите /start",
        "kz": "\n\nМәзірді ашу үшін /start жазыңыз",
        "en": "\n\nTo open the menu, type /start"
    }

    # Формируем сообщение с ответом
    answer_message = (
        f"{answer_title}\n\n"
        f"{question_label.get(user_language, question_label['ru'])}\n"
    )

    # Добавляем вопрос
    if question_data["content_type"] == "text":
        answer_message += question_data["text"]
    else:
        answer_message += f"[{question_data['content_type']}]"
        if question_data["media"]["caption"]:
            answer_message += f"\n<b>Подпись:</b>\n{question_data['media']['caption']}"

    answer_message += f"\n\n{answer_label.get(user_language, answer_label['ru'])}\n"

    # Добавляем подсказку про /start в конце сообщения
    footer_message = menu_hint.get(user_language, menu_hint["ru"])

    # Отправляем ответ без клавиатуры
    if message.content_type == "text":
        await bot.send_message(
            question_data["user_id"],
            answer_message + message.text + footer_message
        )
    else:
        # Отправляем медиафайл с описанием
        if message.content_type == "photo":
            await bot.send_photo(
                question_data["user_id"],
                message.photo[-1].file_id,
                caption=answer_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else "") + footer_message
            )
        elif message.content_type == "video":
            await bot.send_video(
                question_data["user_id"],
                message.video.file_id,
                caption=answer_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else "") + footer_message
            )
        elif message.content_type == "audio":
            await bot.send_audio(
                question_data["user_id"],
                message.audio.file_id,
                caption=answer_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else "") + footer_message
            )
        elif message.content_type == "voice":
            await bot.send_voice(
                question_data["user_id"],
                message.voice.file_id,
                caption=answer_message + footer_message
            )
        elif message.content_type == "video_note":
            # Для видеозаметок нельзя добавить подпись, поэтому отправляем дополнительное сообщение
            await bot.send_video_note(
                question_data["user_id"],
                message.video_note.file_id
            )
            await bot.send_message(
                question_data["user_id"],
                footer_message
            )
        elif message.content_type == "document":
            await bot.send_document(
                question_data["user_id"],
                message.document.file_id,
                caption=answer_message + (f"\n<b>Подпись:</b>\n{message.caption}" if message.caption else "") + footer_message
            )

    await message.answer(f"Ответ на вопрос #{question_id} успешно отправлен.")
    # Логируем завершение ответа на вопрос
    log_question("answered", question_id, admin_id=admin_id, admin_name=admin_display_name)
    log_info(f"Answer to question #{question_id} from admin [ID: {admin_id}] has been sent to user [ID: {question_data['user_id']}]")
    await state.clear() 