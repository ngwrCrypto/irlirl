from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.keyboards import main_menu

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Я твій персональний бот-трекер. 🤖\n"
        "Я допоможу тобі стежити за настроєм, витратами та іншими важливими речами.",
        reply_markup=main_menu()
    )

@router.message(F.text == "Останні дані")
async def show_last_data(message: Message):
    from db.manager import db

    # We need to add a method to DB manager to get last entries, or just query here if we imported aiosqlite.
    # Better to add a method to db/manager.py. Let's assume we will add `get_last_data` there.
    # Wait, I can't modify db/manager.py in this step easily without context.
    # Let's check db/manager.py content first? I have it in previous turns.
    # I will add `get_last_data` to db/manager.py first.

    data = await db.get_last_data()

    msg = "📋 **Останні записи:**\n\n"

    if data['mood']:
        mood = "😊" if data['mood'][1] == 1 else "😞"
        msg += f"Настрій ({data['mood'][0]}): {mood}\n"

    if data['mileage']:
        msg += f"Пробіг ({data['mileage'][0]}): {data['mileage'][1]} км\n"

    if data['expenses']:
        msg += "\n🛒 **Останні витрати:**\n"
        for exp in data['expenses']:
            msg += f"— {exp[0]}: {exp[1]} ({exp[2]}€)\n"

    await message.answer(msg, parse_mode="Markdown")

@router.message(F.text == "Показати статистику за тиждень")
async def show_weekly_stats(message: Message):
    from db.manager import db
    from datetime import date, timedelta

    today = date.today()
    start_of_week = today - timedelta(days=6)

    stats = await db.get_weekly_stats(start_of_week.isoformat(), today.isoformat())

    mood_percent = int(stats['avg_mood'] * 100) if stats['avg_mood'] is not None else 0

    msg = (
        "📊 **Тижневий звіт** (останні 7 днів):\n\n"
        f"💸 Витрачено: {stats['expenses']:.2f} €\n"
        f"💰 Зарплата: {stats['salary']:.2f} €\n"
        f"📉 Залишок: {stats['salary'] - stats['expenses']:.2f} €\n"
        f"😊 Середній настрій: {mood_percent}%\n"
        f"🚗 Пробіг: {stats['mileage']:.1f} км"
    )
    await message.answer(msg, parse_mode="Markdown")
