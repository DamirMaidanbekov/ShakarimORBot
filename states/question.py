from aiogram.fsm.state import State, StatesGroup

# FSM states для задавание вопроса
class QuestionStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_admin_answer = State() 