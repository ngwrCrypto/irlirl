from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import TIMEZONE
from jobs.tasks import send_morning_checkin, check_salary_reminder, send_weekly_report

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
    # We can reuse the same time slot or add separate jobs.
    # Prompt says "Wednesday... at 05:30 adds...", "Friday... at 05:30 asks..."
    # So it's part of the morning routine or separate. Let's make it separate for clarity.
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

    scheduler.start()
