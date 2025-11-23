# File structure

```
telegram_bot/
├── .env
├── .gitignore
├── Dockerfile
├── bot.py
├── config.py
├── docker-compose.yml
├── requirements.txt
├── db/
│   ├── manager.py
│   └── schema.sql
├── handlers/
│   ├── common.py
│   ├── daily.py
│   └── expenses.py
├── jobs/
│   ├── scheduler.py
│   └── tasks.py
└── utils/
    ├── finance.py
    ├── keyboards.py
    ├── states.py
    └── weather.py
```

# .env

```
BOT_TOKEN=your_token_here
ADMIN_ID=your_admin_id
```

# .gitignore

```
.env
__pycache__/
*.py[cod]
*$py.class
.DS_Store
bot.db
data/
```

# Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set timezone to Europe/Dublin
RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Europe/Dublin /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a volume for the database persistence
VOLUME /app/data

# Environment variable for DB path to use the volume
ENV DB_PATH=/app/data/bot.db

CMD ["python", "bot.py"]
```

# docker-compose.yml

```yaml
version: "3.8"

services:
  bot:
    build: .
    container_name: telegram_tracker_bot
    restart: unless-stopped
    volumes:
      - bot_data:/app/data
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - DB_PATH=/app/data/bot.db
      - TZ=Europe/Dublin

volumes:
  bot_data:
```

# requirements.txt

```text
aiogram>=3.0.0
apscheduler
aiosqlite
httpx
python-dotenv
pytz
```

# SQL Schema

```sql
CREATE TABLE IF NOT EXISTS mood (
    date TEXT PRIMARY KEY,
    value INTEGER CHECK(value IN (0, 1))
);

CREATE TABLE IF NOT EXISTS mileage (
    date TEXT PRIMARY KEY,
    value REAL CHECK(value >= 0)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL CHECK(amount >= 0)
);

CREATE TABLE IF NOT EXISTS salary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL CHECK(amount >= 0)
);
```

# bot.py

```python
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_ID
from db.manager import db
from handlers import common, expenses, daily
from jobs.scheduler import setup_scheduler

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Initialize DB
    await db.create_tables()

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Send Startup Message
    await bot.send_message(ADMIN_ID, "Бот запущено дороу! 🚀")

    # Register Routers
    dp.include_router(common.router)
    dp.include_router(expenses.router)
    dp.include_router(daily.router)

    # Setup Scheduler
    setup_scheduler(bot)

    # Start Polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

# config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")  # Optional: for admin-specific notifications if needed
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Weather Configuration (Longford, Ireland)
LATITUDE = 53.727
LONGITUDE = -7.798
TIMEZONE = "Europe/Dublin"
```

# db/manager.py

```python
import aiosqlite
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_tables(self):
        with open("db/schema.sql", "r") as f:
            schema = f.read()

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(schema)
            await db.commit()
            logger.info("Database tables created/verified.")

    async def add_mood(self, date: str, value: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO mood (date, value) VALUES (?, ?)",
                (date, value)
            )
            await db.commit()

    async def add_mileage(self, date: str, value: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO mileage (date, value) VALUES (?, ?)",
                (date, value)
            )
            await db.commit()

    async def add_expense(self, date: str, category: str, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                (date, category, amount)
            )
            await db.commit()

    async def add_salary(self, date: str, amount: float):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO salary (date, amount) VALUES (?, ?)",
                (date, amount)
            )
            await db.commit()

    async def get_weekly_stats(self, start_date: str, end_date: str):
        async with aiosqlite.connect(self.db_path) as db:
            # Expenses
            async with db.execute(
                "SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            ) as cursor:
                expenses = (await cursor.fetchone())[0] or 0.0

            # Salary
            async with db.execute(
                "SELECT SUM(amount) FROM salary WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            ) as cursor:
                salary = (await cursor.fetchone())[0] or 0.0

            # Mood
            async with db.execute(
                "SELECT AVG(value) FROM mood WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            ) as cursor:
                avg_mood = (await cursor.fetchone())[0]

            # Mileage
            async with db.execute(
                "SELECT SUM(value) FROM mileage WHERE date BETWEEN ? AND ?",
                (start_date, end_date)
            ) as cursor:
                mileage = (await cursor.fetchone())[0] or 0.0

        return {
            "expenses": expenses,
            "salary": salary,
            "avg_mood": avg_mood,
            "mileage": mileage
        }

db = DatabaseManager(DB_PATH)
```

# handlers/common.py

```python
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
```

# handlers/daily.py

```python
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
```

# handlers/expenses.py

```python
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
```

# jobs/scheduler.py

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import TIMEZONE
from jobs.tasks import send_morning_checkin, check_salary_reminder, send_weekly_report, send_evening_forecast, send_hourly_rates

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # Daily Morning Routine (05:30)
    scheduler.add_job(
        send_morning_checkin,
        'cron',
        hour=5,
        minute=30,
        kwargs={'bot': bot}
    )

    # Salary Reminders (Wed, Fri at 05:30)
    scheduler.add_job(
        check_salary_reminder,
        'cron',
        day_of_week='wed,fri',
        hour=5,
        minute=30,
        kwargs={'bot': bot}
    )

    # Weekly Report (Sunday 20:00)
    scheduler.add_job(
        send_weekly_report,
        'cron',
        day_of_week='sun',
        hour=20,
        minute=0,
        kwargs={'bot': bot}
    )

    # Evening Forecast (Daily 20:00)
    scheduler.add_job(
        send_evening_forecast,
        'cron',
        hour=20,
        minute=0,
        kwargs={'bot': bot}
    )

    # Hourly Rates
    scheduler.add_job(
        send_hourly_rates,
        'cron',
        minute=0, # Every hour at minute 0
        kwargs={'bot': bot}
    )

    scheduler.start()
```

# jobs/tasks.py

```python
from aiogram import Bot
from config import ADMIN_ID
from utils.weather import get_weather
from utils.keyboards import mood_keyboard
from db.manager import db
from datetime import date, timedelta
from utils.finance import get_exchange_rates

async def send_morning_checkin(bot: Bot):
    # 1. Mood
    await bot.send_message(
        ADMIN_ID,
        "Як твій настрій сьогодні? 😊 / 😞",
        reply_markup=mood_keyboard()
    )

    # 2. Weather
    weather_info = await get_weather()
    await bot.send_message(ADMIN_ID, weather_info)

async def check_salary_reminder(bot: Bot):
    today = date.today().weekday() # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6

    if today == 2: # Wednesday
        await bot.send_message(ADMIN_ID, "Завтра зарплата! Плани на фінанси? 💸")
    elif today == 4: # Friday
        await bot.send_message(ADMIN_ID, "Скільки прийшло на карту? Введи суму в €.")
        # Note: Logic to capture the answer would typically involve FSM or a specific handler.

async def send_weekly_report(bot: Bot):
    today = date.today()
    start_of_week = today - timedelta(days=6) # Last 7 days including today

    stats = await db.get_weekly_stats(start_of_week.isoformat(), today.isoformat())

    mood_percent = int(stats['avg_mood'] * 100) if stats['avg_mood'] is not None else 0

    msg = (
        "Тижневий звіт:\n"
        f"— Витрачено: {stats['expenses']} €\n"
        f"— Зарплата: {stats['salary']} €\n"
        f"— Залишок: {stats['salary'] - stats['expenses']} €\n"
        f"— Середній настрій: {mood_percent}%\n"
        f"— Пробіг за тиждень: {stats['mileage']} км"
    )

    await bot.send_message(ADMIN_ID, msg)

async def send_evening_forecast(bot: Bot):
    from utils.weather import get_weather_forecast
    forecast_info = await get_weather_forecast()
    await bot.send_message(ADMIN_ID, forecast_info)

async def send_hourly_rates(bot: Bot):
    rates_info = await get_exchange_rates()
    await bot.send_message(ADMIN_ID, rates_info)
```

# utils/keyboards.py

```python
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
```

# utils/states.py

```python
from aiogram.fsm.state import State, StatesGroup

class ExpenseState(StatesGroup):
    category = State()
    amount = State()

class SalaryState(StatesGroup):
    amount = State()

class DailyState(StatesGroup):
    mood = State()
    mileage = State()
```

# utils/weather.py

```python
import httpx
from config import LATITUDE, LONGITUDE

async def get_weather() -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            wind = current.get("wind_speed_10m", "N/A")
            code = current.get("weather_code", 0)

            # WMO Weather interpretation codes (simplified)
            if code == 0:
                emoji = "☀️" # Clear sky
                desc = "Sunny"
            elif code in [1, 2, 3]:
                emoji = "☁️" # Cloudy
                desc = "Cloudy"
            elif code in [45, 48]:
                emoji = "🌫️" # Fog
                desc = "Foggy"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                emoji = "🌧️" # Rain
                desc = "Rain"
            elif code in [71, 73, 75, 77, 85, 86]:
                emoji = "❄️" # Snow
                desc = "Snow"
            elif code in [95, 96, 99]:
                emoji = "⛈️" # Thunderstorm
                desc = "Storm"
            else:
                emoji = "🌡"
                desc = "Normal"

            return f"Погода сьогодні: {desc} {emoji}, 🌡 {temp}°C, 💨 {wind} км/год"

    except Exception as e:
        return f"Не вдалося отримати погоду: {e}"

async def get_weather_forecast() -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 2
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            # Index 1 is tomorrow (0 is today)
            code = daily.get("weather_code", [0, 0])[1]
            temp_max = daily.get("temperature_2m_max", [0, 0])[1]
            temp_min = daily.get("temperature_2m_min", [0, 0])[1]

            # WMO Weather interpretation codes (simplified)
            if code == 0:
                emoji = "☀️"
                desc = "Sunny"
            elif code in [1, 2, 3]:
                emoji = "☁️"
                desc = "Cloudy"
            elif code in [45, 48]:
                emoji = "🌫️"
                desc = "Foggy"
            elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                emoji = "🌧️"
                desc = "Rain"
            elif code in [71, 73, 75, 77, 85, 86]:
                emoji = "❄️"
                desc = "Snow"
            elif code in [95, 96, 99]:
                emoji = "⛈️"
                desc = "Storm"
            else:
                emoji = "🌡"
                desc = "Normal"

            return f"Прогноз на завтра: {desc} {emoji}, 🌡 {temp_min}°C ... {temp_max}°C"

    except Exception as e:
        return f"Не вдалося отримати прогноз: {e}"

```

# utils/finance.py

```python
import httpx

async def get_exchange_rates() -> str:
    try:
        async with httpx.AsyncClient() as client:
            # 1. Fiat (NBU API for UAH)
            # https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json
            fiat_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
            fiat_resp = await client.get(fiat_url)
            fiat_data = fiat_resp.json()

            usd_uah = next((item['rate'] for item in fiat_data if item['cc'] == 'USD'), 0.0)
            eur_uah = next((item['rate'] for item in fiat_data if item['cc'] == 'EUR'), 0.0)

            # 2. Crypto (CoinGecko API)
            # https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd
            crypto_url = "https://api.coingecko.com/api/v3/simple/price"
            crypto_params = {
                "ids": "bitcoin,ethereum",
                "vs_currencies": "usd"
            }
            crypto_resp = await client.get(crypto_url, params=crypto_params)
            crypto_data = crypto_resp.json()

            btc_usd = crypto_data.get('bitcoin', {}).get('usd', 0.0)
            eth_usd = crypto_data.get('ethereum', {}).get('usd', 0.0)

            return (
                f"💰 Курс валют:\n"
                f"🇺🇸 USD: {usd_uah:.2f} ₴\n"
                f"🇪🇺 EUR: {eur_uah:.2f} ₴\n\n"
                f"💎 Крипта:\n"
                f"₿ BTC: {btc_usd:,.2f} $\n"
                f"Ξ ETH: {eth_usd:,.2f} $"
            )

    except Exception as e:
        return f"Помилка отримання курсів: {e}"
```
