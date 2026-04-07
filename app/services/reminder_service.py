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

        # Check for users inactive > 24 hours — run every hour
        self.scheduler.add_job(
            self._send_inactivity_nudges,
            trigger=CronTrigger(hour="*", minute=0),
            id="inactivity_nudge",
            replace_existing=True
        )

        # Reset weekly workout counter every Monday 00:01
        self.scheduler.add_job(
            self._reset_weekly_counters,
            trigger=CronTrigger(day_of_week="mon", hour=0, minute=1),
            id="weekly_reset",
            replace_existing=True
        )

        # Auto-regenerate plans every Sunday at 9 AM
        self.scheduler.add_job(
            self._regenerate_adaptive_plans,
            trigger=CronTrigger(day_of_week="sun", hour=9, minute=0),
            id="plan_regen",
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
                        "Hey " + name + "! Gym time aa raha hai. "
                        "Aaj ka workout ready? T type karo! 💪"
                    )

                if self._is_time_match(
                    user.get("sleep_time"), current_hour, current_minute
                ):
                    whatsapp_service.send_reminder(
                        phone,
                        "Sleep time " + name + "! Recovery equally important hai. "
                        "Rest le — kal ke liye recharge ho! 😴"
                    )

                if self._is_time_match(
                    user.get("wake_up_time"), current_hour, current_minute
                ):
                    streak = int(user.get("streak_count", 0))
                    streak_txt = (
                        " Teri " + str(streak) + " din ki streak chal rahi hai!"
                        if streak > 1 else ""
                    )
                    whatsapp_service.send_reminder(
                        phone,
                        "Good morning " + name + "!" + streak_txt
                        + " Paani pi, breakfast kar, goal yaad rakh! 🌅"
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
                    "Paani pi bhai! 3-4 liters daily. Muscles ko hydration chahiye! 💧"
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
                weekly = int(user.get("weekly_workouts_done", 0))
                target = int(user.get("workout_days", 4))
                score = int(user.get("consistency_score", 0))

                msg = (
                    "Weekly Check-in " + name + "!\n\n"
                    "Is hafte: " + str(weekly) + "/" + str(target) +
                    " workouts done\n"
                    "Consistency: " + str(score) + "%\n\n"
                    "Update bhejo:\n"
                    "1. Current weight (kg)?\n"
                    "2. Koi issue?\n\n"
                    "Type P to log progress!"
                )
                whatsapp_service.send_reminder(user.get("phone"), msg)
        except Exception as e:
            print("❌ Weekly progress check error:", e)

    def _send_inactivity_nudges(self):
        """Send nudge to users who haven't messaged in >24 hours."""
        from app.services.database_service import db_service
        from app.services.whatsapp_service import whatsapp_service
        from app.services.engagement_service import engagement_service

        try:
            inactive_users = db_service.get_inactive_users(hours=24)
            for user in inactive_users:
                phone = user.get("phone")
                name = user.get("name", "bhai")
                last = user.get("last_interaction")
                if last is None:
                    days_since = 1
                else:
                    days_since = max(
                        1,
                        int((datetime.utcnow() - last).total_seconds() // 86400)
                    )
                nudge = engagement_service.get_nudge_message(days_since)
                whatsapp_service.send_reminder(
                    phone,
                    name + ", " + nudge
                )
        except Exception as e:
            print("❌ Inactivity nudge error:", e)

    def _reset_weekly_counters(self):
        """Reset weekly workout counts every Monday."""
        from app.services.database_service import db_service
        try:
            db_service.reset_weekly_workouts()
            print("✅ Weekly workout counters reset")
        except Exception as e:
            print("❌ Weekly reset error:", e)

    def _regenerate_adaptive_plans(self):
        """
        Every Sunday regenerate workout + diet plans with adaptive intensity.
        - consistency >= 80% → increase intensity
        - consistency < 40% → decrease intensity
        - else → keep moderate
        """
        from app.services.database_service import db_service
        from app.services.ai_service import ai_service
        from app.services.whatsapp_service import whatsapp_service
        from datetime import datetime

        try:
            users = db_service.get_all_users_with_reminders()
            for user in users:
                phone = user.get("phone")
                name = user.get("name", "bhai")
                score = int(user.get("consistency_score", 0))

                if score >= 80:
                    new_intensity = "intense"
                elif score < 40:
                    new_intensity = "light"
                else:
                    new_intensity = "moderate"

                user["plan_intensity"] = new_intensity
                workout_plan = ai_service.generate_workout_plan(user)
                diet_plan = ai_service.generate_diet_plan(user)

                db_service.update_user(phone, {
                    "workout_plan": workout_plan,
                    "diet_plan": diet_plan,
                    "plan_intensity": new_intensity,
                    "plan_generated_at": datetime.utcnow()
                })

                intensity_msg = {
                    "intense": "Tu consistent hai! Plan upgrade ho gaya! 🔥",
                    "light":   "Koi nahi, plan thoda easy kiya. Wapas aao! 💪",
                    "moderate": "Balanced plan ready hai! 👍"
                }.get(new_intensity, "")

                whatsapp_service.send_reminder(
                    phone,
                    name + "! Naya weekly plan ready hai!\n\n"
                    + intensity_msg + "\n\n"
                    "W1 type karo new plan dekhne ke liye!"
                )
        except Exception as e:
            print("❌ Plan regeneration error:", e)

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("Reminder service stopped")


reminder_service = ReminderService()