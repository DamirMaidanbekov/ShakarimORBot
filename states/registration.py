from aiogram.fsm.state import State, StatesGroup

# FSM states для регистрации
class RegistrationStates(StatesGroup):
    full_name = State()
    course = State()
    faculty = State()
    department = State()
    group = State() 