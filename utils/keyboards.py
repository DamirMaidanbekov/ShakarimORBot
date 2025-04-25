from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from utils.file_operations import is_user_registered, get_user_language


# Словарь с текстами кнопок на разных языках
BUTTON_TEXTS = {
    "ru": {
        "register": "Зарегистрироваться",
        "faq": "Популярные вопросы",
        "ask_question": "Задать вопрос в Офис Регистратуры",
        "chat": "Связаться с Офис Регистраторы(Чат)",
        "menu": "Меню",
        "back_to_list": "Назад к списку",
        "back": "Назад",
        "confirm": "Подтвердить",
        "cancel": "Отмена"
    },
    "kz": {
        "register": "Тіркелу",
        "faq": "Жиі қойылатын сұрақтар",
        "ask_question": "Тіркеу кеңсесіне сұрақ қою",
        "chat": "Тіркеу кеңсесімен байланысу (Чат)",
        "menu": "Мәзір",
        "back_to_list": "Тізімге оралу",
        "back": "Артқа",
        "confirm": "Растау",
        "cancel": "Болдырмау"
    },
    "en": {
        "register": "Register",
        "faq": "Frequently Asked Questions",
        "ask_question": "Ask a question to the Registration Office",
        "chat": "Contact the Registration Office (Chat)",
        "menu": "Menu",
        "back_to_list": "Back to list",
        "back": "Back",
        "confirm": "Confirm",
        "cancel": "Cancel"
    }
}


def get_button_text(key: str, language: str) -> str:
    """Получение текста кнопки на нужном языке."""
    if language not in BUTTON_TEXTS or key not in BUTTON_TEXTS[language]:
        return BUTTON_TEXTS["ru"].get(key, key)
    return BUTTON_TEXTS[language][key]


def get_main_keyboard(user_id: int = None):
    """Создайте клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()
    
    # Получаем язык пользователя
    language = "ru"
    if user_id is not None:
        language = get_user_language(user_id)
    
    # Only show registration button if user is not registered
    if user_id is not None and not is_user_registered(user_id):
        builder.button(
            text=get_button_text("register", language),
            callback_data="register"
        )
    
    builder.button(
        text=get_button_text("faq", language),
        callback_data="faq"
    )
    
    builder.button(
        text=get_button_text("ask_question", language),
        callback_data="ask"
    )
    
    # Add chat button if user is registered
    if user_id is not None and is_user_registered(user_id):
        builder.button(
            text=get_button_text("chat", language),
            callback_data="chat"
        )
    
    builder.adjust(1)  # Place buttons vertically
    return builder.as_markup()


def get_faq_list_keyboard(language: str = "ru"):
    """Создание клавиатуры со списком вопросов FAQ."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button_text("menu", language),
        callback_data="main_menu"
    )
    builder.adjust(1)  # Place button vertically
    return builder.as_markup()


def get_faq_back_keyboard(language: str = "ru"):
    """Создание клавиатуры для возврата к списку FAQ."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button_text("back_to_list", language),
        callback_data="faq_list"
    )
    builder.adjust(1)  # Place button vertically
    return builder.as_markup()


def get_back_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой 'Назад'."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=get_button_text("back", language),
        callback_data="back"
    )
    return builder.as_markup()


def get_auth_keyboards(language: str = "ru") -> tuple[InlineKeyboardMarkup, InlineKeyboardMarkup]:
    """Создает клавиатуры для авторизации."""
    # Клавиатура для подтверждения
    confirm_builder = InlineKeyboardBuilder()
    confirm_builder.button(
        text=get_button_text("confirm", language),
        callback_data="auth_confirm"
    )
    confirm_builder.button(
        text=get_button_text("cancel", language),
        callback_data="auth_cancel"
    )
    confirm_builder.adjust(2)  # Размещаем кнопки в 2 колонки
    
    # Клавиатура для отмены
    cancel_builder = InlineKeyboardBuilder()
    cancel_builder.button(
        text=get_button_text("cancel", language),
        callback_data="auth_cancel"
    )
    
    return confirm_builder.as_markup(), cancel_builder.as_markup()


def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора языка."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Русский 🇷🇺", callback_data="lang_ru")
    builder.button(text="Қазақша 🇰🇿", callback_data="lang_kz")
    builder.button(text="English 🇬🇧", callback_data="lang_en")
    builder.adjust(1)  # Размещаем кнопки вертикально
    return builder.as_markup() 