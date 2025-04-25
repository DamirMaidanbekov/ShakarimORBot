from aiogram.fsm.state import State, StatesGroup

# FSM states для чата
class ChatStates(StatesGroup):
    """Состояния для чата"""
    waiting_for_connection = State()  # Ожидание подключения
    connected = State()  # Чат активен
    disconnected_by_admin = State()  # Отключен администратором 