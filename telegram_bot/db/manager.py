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

    async def get_last_data(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Last Mood
            async with db.execute("SELECT date, value FROM mood ORDER BY date DESC LIMIT 1") as cursor:
                mood = await cursor.fetchone()

            # Last Mileage
            async with db.execute("SELECT date, value FROM mileage ORDER BY date DESC LIMIT 1") as cursor:
                mileage = await cursor.fetchone()

            # Last 3 Expenses
            async with db.execute("SELECT date, category, amount FROM expenses ORDER BY date DESC LIMIT 3") as cursor:
                expenses = await cursor.fetchall()

        return {
            "mood": mood,
            "mileage": mileage,
            "expenses": expenses
        }

db = DatabaseManager(DB_PATH)
