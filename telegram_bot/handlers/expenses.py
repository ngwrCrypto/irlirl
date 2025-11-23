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

# Salary Handlers
from aiogram.types import CallbackQuery
from utils.states import SalaryState

@router.callback_query(F.data == "add_salary")
async def start_salary(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SalaryState.amount)
    await callback.message.answer("Введи суму зарплати в €:")
    await callback.answer()

@router.message(SalaryState.amount)
async def process_salary(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount < 0:
            raise ValueError("Negative amount")

        today = date.today().isoformat()
        await db.add_salary(today, amount)

        await message.answer(f"🤑 Зарплата {amount}€ записана! Гуляємо! 🎉", reply_markup=main_menu())
        await state.clear()

    except ValueError:
        await message.answer("Будь ласка, введи коректне число.")
