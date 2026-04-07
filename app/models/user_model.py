# app/models/user_model.py

from datetime import datetime


def create_user_document(phone: str) -> dict:
    return {
        # ── Identity ────────────────────────────────────────
        "phone": phone,
        "receipt_number": None,
        "name": None,
        # ── Body stats ──────────────────────────────────────
        "age": None,
        "weight": None,
        "height": None,
        # ── Fitness profile ─────────────────────────────────
        "goal": None,              # Fat Loss / Muscle Gain / etc.
        "diet_preference": None,   # Veg / Non-Veg / Vegan / Jain
        "budget": None,            # low / medium / high
        "region": None,            # North Indian / South Indian / etc.
        "workout_days": None,
        "available_workout_time": None,  # minutes per session
        "meals_per_day": None,
        "experience_level": None,   # just_starting / less_1_month / 1_2_months / 2_plus_months
        "injuries": None,           # None or description of injuries/conditions
        "cardio_preference": None,  # dedicated / mix
        # ── Schedule ────────────────────────────────────────
        "wake_up_time": None,
        "gym_time": None,
        "sleep_time": None,
        # ── Plans ───────────────────────────────────────────
        "workout_plan": None,
        "diet_plan": None,
        "plan_intensity": "moderate",  # light / moderate / intense
        "plan_generated_at": None,
        # ── Onboarding ──────────────────────────────────────
        "is_verified": False,
        "onboarding_complete": False,
        "onboarding_step": "start",
        # ── Engagement & streaks ────────────────────────────
        "streak_count": 0,
        "longest_streak": 0,
        "last_checkin_date": None,   # date string YYYY-MM-DD
        "last_workout_date": None,   # date string YYYY-MM-DD
        "weekly_workouts_done": 0,
        "consistency_score": 0,      # 0-100
        "total_workouts_done": 0,
        # ── Calorie tracking ────────────────────────────────
        "calorie_logs": [],          # [{date, calories, notes}]
        # ── Progress ────────────────────────────────────────
        "weekly_progress": [],
        # ── Timestamps ──────────────────────────────────────
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_interaction": datetime.utcnow(),
        # ── Conversation ────────────────────────────────────
        "conversation_history": []
    }