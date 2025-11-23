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
