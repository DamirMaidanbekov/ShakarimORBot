from handlers.common import router as common_router
from handlers.registration import router as registration_router
from handlers.faq import router as faq_router
from handlers.questions import router as questions_router
from handlers.chat import router as chat_router

__all__ = [
    'common_router',
    'registration_router',
    'faq_router',
    'questions_router',
    'chat_router'
] 