from aiogram.fsm.state import StatesGroup, State


class LanguageStates(StatesGroup):
    """States for language selection."""
    selecting_language = State() 