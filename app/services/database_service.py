# app/services/database_service.py

from pymongo import MongoClient
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def _today() -> str:
    return date.today().isoformat()


class DatabaseService:
    def __init__(self):
        try:
            self.client = MongoClient(os.getenv("MONGODB_URI"))
            self.db = self.client[os.getenv("MONGODB_DATABASE", "gym_trainer")]
            self.users_collection = self.db["users"]
            self.users_collection.create_index("phone", unique=True)
            print("✅ MongoDB connected successfully")
        except Exception as e:
            print("❌ MongoDB connection failed:", e)

    def get_user(self, phone: str):
        try:
            return self.users_collection.find_one({"phone": phone})
        except Exception as e:
            print("❌ get_user error:", e)
            return None

    def create_user(self, phone: str):
        from app.models.user_model import create_user_document
        try:
            user_doc = create_user_document(phone)
            self.users_collection.insert_one(user_doc)
            print("✅ New user created:", phone)
            return user_doc
        except Exception as e:
            print("❌ create_user error:", e)
            return None

    def get_or_create_user(self, phone: str):
        user = self.get_user(phone)
        if not user:
            user = self.create_user(phone)
        return user

    def update_user(self, phone: str, updates: dict):
        try:
            updates["updated_at"] = datetime.utcnow()
            updates["last_interaction"] = datetime.utcnow()
            self.users_collection.update_one(
                {"phone": phone},
                {"$set": updates}
            )
        except Exception as e:
            print("❌ update_user error:", e)

    def update_onboarding_step(self, phone: str, step: str):
        self.update_user(phone, {"onboarding_step": step})

    def save_conversation_message(self, phone: str, role: str, content: str):
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow()
            }
            self.users_collection.update_one(
                {"phone": phone},
                {
                    "$push": {
                        "conversation_history": {
                            "$each": [message],
                            "$slice": -10
                        }
                    },
                    "$set": {"last_interaction": datetime.utcnow()}
                }
            )
        except Exception as e:
            print("❌ save_conversation_message error:", e)

    def add_progress_entry(self, phone: str, progress: dict):
        try:
            self.users_collection.update_one(
                {"phone": phone},
                {"$push": {"weekly_progress": progress}}
            )
        except Exception as e:
            print("❌ add_progress_entry error:", e)

    # ── Streak & engagement ──────────────────────────────────

    def log_workout_done(self, phone: str) -> dict:
        """
        Mark today's workout as done.
        Updates streak, weekly count, consistency score.
        Returns updated engagement info.
        """
        try:
            user = self.get_user(phone)
            if not user:
                return {}

            today = _today()
            last_checkin = user.get("last_checkin_date")
            streak = int(user.get("streak_count", 0))
            longest = int(user.get("longest_streak", 0))
            weekly = int(user.get("weekly_workouts_done", 0))
            total = int(user.get("total_workouts_done", 0))

            # Avoid double-counting same day
            if last_checkin == today:
                return {
                    "streak": streak,
                    "weekly": weekly,
                    "total": total,
                    "already_done": True
                }

            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if last_checkin == yesterday:
                streak += 1
            else:
                streak = 1  # reset streak

            longest = max(longest, streak)
            weekly += 1
            total += 1

            # Consistency score = (workouts done this week / target days) * 100
            workout_days = max(int(user.get("workout_days", 4)), 1)
            consistency = min(int((weekly / workout_days) * 100), 100)

            self.update_user(phone, {
                "streak_count": streak,
                "longest_streak": longest,
                "last_checkin_date": today,
                "last_workout_date": today,
                "weekly_workouts_done": weekly,
                "total_workouts_done": total,
                "consistency_score": consistency
            })
            return {
                "streak": streak,
                "weekly": weekly,
                "total": total,
                "consistency": consistency,
                "already_done": False
            }
        except Exception as e:
            print("❌ log_workout_done error:", e)
            return {}

    def reset_weekly_workouts(self):
        """Called every Monday to reset weekly counter."""
        try:
            self.users_collection.update_many(
                {"onboarding_complete": True},
                {"$set": {"weekly_workouts_done": 0}}
            )
        except Exception as e:
            print("❌ reset_weekly_workouts error:", e)

    def add_calorie_log(self, phone: str, calories: int, notes: str = ""):
        try:
            entry = {
                "date": _today(),
                "calories": calories,
                "notes": notes
            }
            self.users_collection.update_one(
                {"phone": phone},
                {
                    "$push": {
                        "calorie_logs": {
                            "$each": [entry],
                            "$slice": -30
                        }
                    }
                }
            )
        except Exception as e:
            print("❌ add_calorie_log error:", e)

    def get_all_users_with_reminders(self):
        try:
            return list(self.users_collection.find({
                "is_verified": True,
                "onboarding_complete": True
            }))
        except Exception as e:
            print("❌ get_all_users_with_reminders error:", e)
            return []

    def get_inactive_users(self, hours: int = 24):
        """Return users who haven't interacted in the last `hours` hours."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return list(self.users_collection.find({
                "is_verified": True,
                "onboarding_complete": True,
                "last_interaction": {"$lt": cutoff}
            }))
        except Exception as e:
            print("❌ get_inactive_users error:", e)
            return []


db_service = DatabaseService()