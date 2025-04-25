from aiogram.fsm.state import State, StatesGroup

# FSM states для FAQ
class FAQStates(StatesGroup):
    waiting_for_number = State() 