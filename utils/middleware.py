from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils.file_operations import get_user_language


class LanguageTrackingMiddleware(BaseMiddleware):
    """
    Middleware для отслеживания языка пользователя.
    
    Этот middleware сохраняет информацию о языке пользователя в данных обработчика,
    чтобы ее можно было использовать во всех обработчиках без повторного получения.
    """
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id из сообщения или колбэка
        user = event.from_user
        if user:
            # Получаем язык пользователя и добавляем его в data
            language = get_user_language(user.id)
            data["user_language"] = language
        
        # Передаем управление дальше
        return await handler(event, data) 