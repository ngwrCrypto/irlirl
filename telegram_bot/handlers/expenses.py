from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils.states import ExpenseState
from utils.keyboards import expense_categories, main_menu
from db.manager import db
from datetime import date

router = Router()

@router.message(F.text == "Додати витрату 🛒")
async def start_expense(message: Message, state: FSMContext):
    await state.set_state(ExpenseState.category)
    await message.answer("Оберіть категорію витрати:", reply_markup=expense_categories())

@router.message(ExpenseState.category)
async def process_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(ExpenseState.amount)
    await message.answer("Введи суму в €.", reply_markup=None)

@router.message(ExpenseState.amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount < 0:
            raise ValueError("Negative amount")

        data = await state.get_data()
        category = data['category']
        today = date.today().isoformat()

        await db.add_expense(today, category, amount)
        await message.answer(f"✅ Записано: {category} - {amount}€", reply_markup=main_menu())
        await state.clear()

    except ValueError:
        await message.answer("Будь ласка, введи коректне число (більше 0).")
