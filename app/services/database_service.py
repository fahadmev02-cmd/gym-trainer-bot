# app/services/database_service.py

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


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
        try:
            user_doc = {
                "phone": phone,
                "receipt_number": None,
                "name": None,
                "age": None,
                "weight": None,
                "height": None,
                "goal": None,
                "diet_preference": None,
                "workout_days": None,
                "meals_per_day": None,
                "wake_up_time": None,
                "gym_time": None,
                "sleep_time": None,
                "workout_plan": None,
                "diet_plan": None,
                "is_verified": False,
                "onboarding_complete": False,
                "onboarding_step": "start",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_interaction": datetime.utcnow(),
                "weekly_progress": [],
                "conversation_history": []
            }
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

    def get_all_users_with_reminders(self):
        try:
            return list(self.users_collection.find({
                "is_verified": True,
                "onboarding_complete": True
            }))
        except Exception as e:
            print("❌ get_all_users_with_reminders error:", e)
            return []


db_service = DatabaseService()