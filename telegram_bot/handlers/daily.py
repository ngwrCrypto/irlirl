from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.states import DailyState
from db.manager import db
from datetime import date

router = Router()

# Note: The entry point for this flow is usually triggered by the scheduler (sending a message with inline keyboard).
# However, we need handlers to process the callback and the subsequent message.

@router.callback_query(F.data.startswith("mood_"))
async def process_mood(callback: CallbackQuery, state: FSMContext):
    mood_value = int(callback.data.split("_")[1])
    today = date.today().isoformat()

    await db.add_mood(today, mood_value)
    await callback.message.answer("Настрій записано! 👌")

    # Prompt for mileage immediately after mood
    await state.set_state(DailyState.mileage)
    await callback.message.answer("Введи пробіг за сьогодні (км). Якщо 0 — пропусти.")
    await callback.answer()

@router.message(DailyState.mileage)
async def process_mileage(message: Message, state: FSMContext):
    text = message.text.strip()

    # Allow skipping if 0 or explicit skip command if we wanted, but prompt says "If 0 - skip" which implies inputting 0.
    # Actually prompt says "Якщо 0 — пропусти", usually implies entering 0 means no change/record, or just don't write anything?
    # Let's assume user types '0' to skip recording, or types a number.

    try:
        value = float(text.replace(',', '.'))
        if value < 0:
            await message.answer("Пробіг не може бути від'ємним. Спробуй ще раз.")
            return

        if value > 0:
            today = date.today().isoformat()
            await db.add_mileage(today, value)
            msg = f"Пробіг {value} км записано."
            if value > 200:
                msg += " ⚠️ Час перевірити масло!"
            await message.answer(msg)
        else:
            await message.answer("Пробіг не змінено.")

        await state.clear()

    except ValueError:
        await message.answer("Будь ласка, введи число.")
