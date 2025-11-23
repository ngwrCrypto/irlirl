from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = [
        [KeyboardButton(text="Додати витрату 🛒")],
        [KeyboardButton(text="Показати статистику за тиждень")],
        [KeyboardButton(text="Останні дані")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def expense_categories():
    kb = [
        [KeyboardButton(text="Їжа"), KeyboardButton(text="Паливо")],
        [KeyboardButton(text="Розваги"), KeyboardButton(text="Інше")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def mood_keyboard():
    kb = [
        [InlineKeyboardButton(text="Норм 😊", callback_data="mood_1")],
        [InlineKeyboardButton(text="Не дуже 😞", callback_data="mood_0")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def salary_keyboard():
    kb = [
        [InlineKeyboardButton(text="💰 Ввести зарплату", callback_data="add_salary")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
