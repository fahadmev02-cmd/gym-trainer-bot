# app/models/user_model.py

from datetime import datetime


def create_user_document(phone: str) -> dict:
    return {
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