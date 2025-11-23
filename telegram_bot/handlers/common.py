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
    # Placeholder for simple last data check, or just a stub
    await message.answer("Функція ще в розробці, але скоро тут будуть твої останні записи!")
