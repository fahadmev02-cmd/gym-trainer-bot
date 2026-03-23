# app/services/reminder_service.py

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import re


class ReminderService:
    def __init__(self):
        try:
            self.scheduler = BackgroundScheduler()
            self._setup_jobs()
            self.scheduler.start()
            print("✅ Reminder service started")
        except Exception as e:
            print("❌ Reminder service failed:", e)

    def _setup_jobs(self):
        self.scheduler.add_job(
            self._check_and_send_reminders,
            trigger=CronTrigger(minute="*"),
            id="reminder_check",
            replace_existing=True
        )

        self.scheduler.add_job(
            self._send_weekly_progress_check,
            trigger=CronTrigger(day_of_week="sun", hour=8, minute=0),
            id="weekly_progress",
            replace_existing=True
        )

        self.scheduler.add_job(
            self._send_hydration_reminders,
            trigger=CronTrigger(hour="8,10,12,14,16,18,20", minute=0),
            id="hydration_reminder",
            replace_existing=True
        )

    def _parse_time(self, time_str: str):
        if not time_str:
            return None, None
        try:
            time_str = str(time_str).strip().upper()
            if "AM" in time_str or "PM" in time_str:
                numbers = re.findall(r"\d+", time_str)
                if not numbers:
                    return None, None
                hour = int(numbers[0])
                minute = int(numbers[1]) if len(numbers) > 1 else 0
                if "PM" in time_str and hour != 12:
                    hour += 12
                elif "AM" in time_str and hour == 12:
                    hour = 0
                return hour, minute
            elif ":" in time_str:
                parts = time_str.split(":")
                return int(parts[0]), int(parts[1])
        except Exception as e:
            print("⚠️ Time parsing error for", time_str, ":", e)
        return None, None

    def _is_time_match(self, time_str: str, target_hour: int, target_minute: int) -> bool:
        hour, minute = self._parse_time(time_str)
        if hour is None:
            return False
        try:
            scheduled_time = datetime.now().replace(
                hour=hour, minute=minute, second=0
            )
            reminder_time = scheduled_time - timedelta(minutes=15)
            current_time = datetime.now()
            return (
                current_time.hour == reminder_time.hour and
                current_time.minute == reminder_time.minute
            )
        except Exception:
            return False

    def _check_and_send_reminders(self):
        from app.services.database_service import db_service
        from app.services.whatsapp_service import whatsapp_service

        current_hour = datetime.now().hour
        current_minute = datetime.now().minute

        try:
            users = db_service.get_all_users_with_reminders()
            for user in users:
                phone = user.get("phone")
                name = user.get("name", "there")

                if self._is_time_match(
                    user.get("gym_time"), current_hour, current_minute
                ):
                    whatsapp_service.send_reminder(
                        phone,
                        "Hey " + name + "! Gym time is coming up soon. Are you ready for today's workout? Type workout to see your plan!"
                    )

                if self._is_time_match(
                    user.get("sleep_time"), current_hour, current_minute
                ):
                    whatsapp_service.send_reminder(
                        phone,
                        "Sleep time " + name + "! Recovery is just as important as training. Rest well and come back stronger tomorrow!"
                    )

                if self._is_time_match(
                    user.get("wake_up_time"), current_hour, current_minute
                ):
                    whatsapp_service.send_reminder(
                        phone,
                        "Good morning " + name + "! A new day to get closer to your goals. Drink water, have breakfast and stay active!"
                    )

        except Exception as e:
            print("❌ Reminder check error:", e)

    def _send_hydration_reminders(self):
        from app.services.database_service import db_service
        from app.services.whatsapp_service import whatsapp_service

        try:
            users = db_service.get_all_users_with_reminders()
            for user in users:
                whatsapp_service.send_reminder(
                    user.get("phone"),
                    "Drink water! Stay hydrated. Aim for 3 to 4 liters today."
                )
        except Exception as e:
            print("❌ Hydration reminder error:", e)

    def _send_weekly_progress_check(self):
        from app.services.database_service import db_service
        from app.services.whatsapp_service import whatsapp_service

        try:
            users = db_service.get_all_users_with_reminders()
            for user in users:
                name = user.get("name", "there")
                whatsapp_service.send_reminder(
                    user.get("phone"),
                    "Weekly Progress Check " + name + "! Please share: 1. Current weight in kg. 2. Workouts completed this week. 3. Any difficulties. Type progress to log your update!"
                )
        except Exception as e:
            print("❌ Weekly progress check error:", e)

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Reminder service stopped")


reminder_service = ReminderService()