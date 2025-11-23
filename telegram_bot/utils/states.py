from aiogram.fsm.state import State, StatesGroup

class ExpenseState(StatesGroup):
    category = State()
    amount = State()

class SalaryState(StatesGroup):
    amount = State()

class DailyState(StatesGroup):
    mood = State()
    mileage = State()
