# app/utils/conversation_manager.py

from app.services.database_service import db_service
from app.services.sheets_service import sheets_service
from app.services.ai_service import ai_service
from app.services.whatsapp_service import whatsapp_service
from app.services.engagement_service import engagement_service
from app.services.diet_intelligence import diet_intelligence
import time
from datetime import datetime


class ConversationManager:

    # ── Workout day schedule ──────────────────────────
    DAY_SCHEDULE = {
        3: {
            1: "Chest and Triceps",
            2: "Back and Biceps",
            3: "REST",
            4: "Legs and Shoulders",
            5: "REST",
            6: "Full Body",
            7: "REST"
        },
        4: {
            1: "Chest and Triceps",
            2: "Back and Biceps",
            3: "REST",
            4: "Legs",
            5: "Shoulders and Abs",
            6: "REST",
            7: "REST"
        },
        5: {
            1: "Chest and Triceps",
            2: "Back and Biceps",
            3: "Legs",
            4: "REST",
            5: "Shoulders",
            6: "Full Body",
            7: "REST"
        },
        6: {
            1: "Chest",
            2: "Back and Biceps",
            3: "Legs",
            4: "Shoulders",
            5: "Arms and Abs",
            6: "Full Body",
            7: "REST"
        }
    }

    def process_message(self, phone: str, message: str) -> str:
        phone = phone.replace("whatsapp:", "").strip()
        user = db_service.get_or_create_user(phone)
        db_service.save_conversation_message(phone, "user", message)
        response = self._handle_message(user, phone, message.strip())
        if response:
            db_service.save_conversation_message(phone, "assistant", response)
        return response

    def _handle_message(self, user: dict, phone: str, message: str) -> str:
        step = user.get("onboarding_step", "start")

        if step == "start":
            return self._handle_start(phone)
        elif step == "awaiting_receipt":
            return self._handle_receipt_verification(phone, message, user)
        elif step == "collecting_age":
            return self._collect_age(phone, message)
        elif step == "collecting_weight":
            return self._collect_weight(phone, message)
        elif step == "collecting_height":
            return self._collect_height(phone, message)
        elif step == "collecting_goal":
            return self._collect_goal(phone, message)
        elif step == "collecting_diet":
            return self._collect_diet(phone, message)
        elif step == "collecting_budget":
            return self._collect_budget(phone, message)
        elif step == "collecting_region":
            return self._collect_region(phone, message)
        elif step == "collecting_workout_days":
            return self._collect_workout_days(phone, message)
        elif step == "collecting_workout_time":
            return self._collect_workout_time(phone, message)
        elif step == "collecting_meals":
            return self._collect_meals(phone, message)
        elif step == "collecting_wake_time":
            return self._collect_wake_time(phone, message)
        elif step == "collecting_gym_time":
            return self._collect_gym_time(phone, message)
        elif step == "collecting_sleep_time":
            return self._collect_sleep_time(phone, user, message)
        elif step == "complete":
            return self._handle_general_conversation(phone, user, message)
        else:
            db_service.update_onboarding_step(phone, "start")
            return self._handle_start(phone)

    # ================================================================
    # ONBOARDING
    # ================================================================

    def _handle_start(self, phone: str) -> str:
        db_service.update_onboarding_step(phone, "awaiting_receipt")
        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "WELCOME TO FITBOT AI\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Main hoon tera personal AI Fitness Coach!\n\n"
            "Main dunga:\n"
            "Personalized Workout Plan\n"
            "Indian Diet Plan (budget + region wise)\n"
            "Daily Streaks + Gamification\n"
            "Smart Reminders\n"
            "Progress Dashboard\n"
            "24/7 Fitness Guidance\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Pehle tera Gym Receipt Number enter karo\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    def _handle_receipt_verification(
        self, phone: str, message: str, user: dict
    ) -> str:
        receipt_number = message.strip()
        result = sheets_service.verify_membership(receipt_number)

        if result["is_valid"]:
            name = result.get("name", "there")
            db_service.update_user(phone, {
                "receipt_number": receipt_number,
                "name": name,
                "is_verified": True,
                "onboarding_step": "collecting_age"
            })
            return (
                "MEMBERSHIP VERIFIED!\n\n"
                "Welcome " + name + "!\n\n"
                "Chalo tera Fitness Profile banate hain.\n"
                "Sirf 13 quick questions — 3 minute ka kaam!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Q1/13 — Teri age kya hai?\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Example: 24"
            )
        else:
            return (
                "Receipt Number Nahi Mila\n\n"
                "Gym counter pe jaao\n"
                "Ya call karo: [Gym Number]\n\n"
                "Dobara try karo:"
            )

    def _collect_age(self, phone: str, message: str) -> str:
        try:
            age = int(message.strip())
            if not (10 <= age <= 80):
                return "10 se 80 ke beech age likho."
            db_service.update_user(phone, {
                "age": age,
                "onboarding_step": "collecting_weight"
            })
            return (
                "Q2/13 — Tera current weight? (kg)\n\n"
                "Example: 75"
            )
        except ValueError:
            return "Sirf number type karo. Example: 24"

    def _collect_weight(self, phone: str, message: str) -> str:
        try:
            weight = float(
                message.strip().replace("kg", "").replace("KG", "")
            )
            if not (30 <= weight <= 250):
                return "30 se 250 kg ke beech weight likho."
            db_service.update_user(phone, {
                "weight": weight,
                "onboarding_step": "collecting_height"
            })
            return (
                "Q3/13 — Teri height? (cm mein)\n\n"
                "Example: 175\n"
                "5ft 9in = 175 cm"
            )
        except ValueError:
            return "Sirf number type karo. Example: 75"

    def _collect_height(self, phone: str, message: str) -> str:
        try:
            height = float(
                message.strip().replace("cm", "").replace("CM", "")
            )
            if not (100 <= height <= 250):
                return "100 se 250 cm ke beech height likho."
            db_service.update_user(phone, {
                "height": height,
                "onboarding_step": "collecting_goal"
            })
            return (
                "Q4/13 — Tera fitness goal?\n\n"
                "1 - Fat Loss\n"
                "2 - Muscle Gain\n"
                "3 - Maintain Fitness\n"
                "4 - Strength Badhana\n"
                "5 - Endurance\n"
                "6 - Competition Prep\n\n"
                "Number type karo: 1 se 6"
            )
        except ValueError:
            return "Sirf number type karo. Example: 175"

    def _collect_goal(self, phone: str, message: str) -> str:
        goals = {
            "1": "Fat Loss",
            "2": "Muscle Gain",
            "3": "Maintain Fitness",
            "4": "Increase Strength",
            "5": "Improve Endurance",
            "6": "Competition Prep"
        }
        goal = goals.get(message.strip())

        if not goal:
            msg = message.lower()
            if "fat" in msg or "loss" in msg:
                goal = "Fat Loss"
            elif "muscle" in msg or "bulk" in msg or "gain" in msg:
                goal = "Muscle Gain"
            elif "maintain" in msg:
                goal = "Maintain Fitness"
            elif "strength" in msg:
                goal = "Increase Strength"
            elif "endurance" in msg:
                goal = "Improve Endurance"
            elif "compet" in msg or "stage" in msg:
                goal = "Competition Prep"

        if goal:
            db_service.update_user(phone, {
                "goal": goal,
                "onboarding_step": "collecting_diet"
            })
            return (
                "Goal: " + goal + "\n\n"
                "Q5/13 — Diet preference?\n\n"
                "1 - Veg\n"
                "2 - Non-Veg\n"
                "3 - Vegan\n"
                "4 - Jain\n\n"
                "1 / 2 / 3 / 4 type karo"
            )
        else:
            return "1 se 6 number type karo."

    def _collect_diet(self, phone: str, message: str) -> str:
        msg = message.lower().strip()
        if msg in ["1", "veg", "vegetarian", "v"]:
            diet = "Veg"
        elif msg in ["2", "non-veg", "nonveg", "non veg", "nv"]:
            diet = "Non-Veg"
        elif msg in ["3", "vegan"]:
            diet = "Vegan"
        elif msg in ["4", "jain"]:
            diet = "Jain"
        else:
            return "1 (Veg), 2 (Non-Veg), 3 (Vegan) ya 4 (Jain) type karo."

        db_service.update_user(phone, {
            "diet_preference": diet,
            "onboarding_step": "collecting_budget"
        })
        return (
            "Diet: " + diet + "\n\n"
            "Q6/13 — Tera monthly food budget?\n\n"
            "1 - Low (tight budget, basic foods)\n"
            "2 - Medium (paneer, eggs, chicken)\n"
            "3 - High (whey, fish, premium foods)\n\n"
            "1 / 2 / 3 type karo"
        )

    def _collect_budget(self, phone: str, message: str) -> str:
        msg = message.lower().strip()
        budget_map = {
            "1": "low", "low": "low",
            "2": "medium", "medium": "medium",
            "3": "high", "high": "high"
        }
        budget = budget_map.get(msg)
        if not budget:
            return "1 (Low), 2 (Medium) ya 3 (High) type karo."

        db_service.update_user(phone, {
            "budget": budget,
            "onboarding_step": "collecting_region"
        })
        return (
            "Budget: " + budget.title() + "\n\n"
            "Q7/13 — Tera region / state?\n\n"
            "1 - North Indian (UP, Delhi, Punjab, Haryana)\n"
            "2 - South Indian (TN, Karnataka, Kerala, AP)\n"
            "3 - East Indian (Bengal, Odisha, Bihar)\n"
            "4 - West Indian (Gujarat, Maharashtra, Rajasthan)\n"
            "5 - Other\n\n"
            "1 / 2 / 3 / 4 / 5 type karo"
        )

    def _collect_region(self, phone: str, message: str) -> str:
        region_map = {
            "1": "North Indian",
            "2": "South Indian",
            "3": "East Indian",
            "4": "West Indian",
            "5": "Other",
            "north": "North Indian",
            "south": "South Indian",
            "east": "East Indian",
            "west": "West Indian",
        }
        msg = message.lower().strip()
        region = region_map.get(msg) or region_map.get(msg.split()[0] if msg else "")

        if not region:
            return "1 se 5 number type karo."

        db_service.update_user(phone, {
            "region": region,
            "onboarding_step": "collecting_workout_days"
        })
        return (
            "Region: " + region + "\n\n"
            "Q8/13 — Hafte mein kitne din gym?\n\n"
            "3 - Beginner\n"
            "4 - Recommended\n"
            "5 - Intermediate\n"
            "6 - Advanced\n\n"
            "Number type karo"
        )

    def _collect_workout_days(self, phone: str, message: str) -> str:
        try:
            days = int(message.strip())
            if not (1 <= days <= 7):
                return "1 se 7 ke beech number type karo."
            db_service.update_user(phone, {
                "workout_days": days,
                "onboarding_step": "collecting_workout_time"
            })
            return (
                str(days) + " days per week!\n\n"
                "Q9/13 — Har session mein kitna time available hai? (minutes)\n\n"
                "Example: 45 ya 60 ya 90"
            )
        except ValueError:
            return "Sirf number type karo. Example: 4"

    def _collect_workout_time(self, phone: str, message: str) -> str:
        try:
            minutes = int(
                message.strip().replace("min", "").replace("mins", "").strip()
            )
            if not (20 <= minutes <= 180):
                return "20 se 180 minutes ke beech likhna."
            db_service.update_user(phone, {
                "available_workout_time": minutes,
                "onboarding_step": "collecting_meals"
            })
            return (
                str(minutes) + " min per session!\n\n"
                "Q10/13 — Din mein kitni baar khana?\n\n"
                "3 - Basic\n"
                "4 - Good\n"
                "5 - Best for fitness\n"
                "6 - Advanced\n\n"
                "Number type karo"
            )
        except ValueError:
            return "Sirf minutes mein number likhna. Example: 60"

    def _collect_meals(self, phone: str, message: str) -> str:
        try:
            meals = int(message.strip())
            if not (2 <= meals <= 8):
                return "2 se 8 ke beech number type karo."
            db_service.update_user(phone, {
                "meals_per_day": meals,
                "onboarding_step": "collecting_wake_time"
            })
            return (
                str(meals) + " meals per day!\n\n"
                "Q11/13 — Subah kitne baje uthta hai?\n\n"
                "Example: 6:00 AM"
            )
        except ValueError:
            return "Sirf number type karo. Example: 5"

    def _collect_wake_time(self, phone: str, message: str) -> str:
        wake_time = message.strip()
        if len(wake_time) < 3:
            return "Sahi format: 6:00 AM"
        db_service.update_user(phone, {
            "wake_up_time": wake_time,
            "onboarding_step": "collecting_gym_time"
        })
        return (
            "Wake up: " + wake_time + "\n\n"
            "Q12/13 — Gym kitne baje jaata hai?\n\n"
            "Example: 6:00 PM"
        )

    def _collect_gym_time(self, phone: str, message: str) -> str:
        gym_time = message.strip()
        if len(gym_time) < 3:
            return "Sahi format: 6:00 PM"
        db_service.update_user(phone, {
            "gym_time": gym_time,
            "onboarding_step": "collecting_sleep_time"
        })
        return (
            "Gym time: " + gym_time + "\n\n"
            "Q13/13 (LAST!) — Raat ko kitne baje sota hai?\n\n"
            "Example: 11:00 PM"
        )

    def _collect_sleep_time(
        self, phone: str, user: dict, message: str
    ) -> str:
        sleep_time = message.strip()
        if len(sleep_time) < 3:
            return "Sahi format: 11:00 PM"

        db_service.update_user(phone, {
            "sleep_time": sleep_time,
            "onboarding_step": "generating_plans"
        })

        updated_user = db_service.get_user(phone)
        name = updated_user.get("name", "Bhai")
        goal = updated_user.get("goal", "Fitness")
        workout_days = int(updated_user.get("workout_days", 4))
        budget = updated_user.get("budget", "medium")
        region = updated_user.get("region", "North Indian")

        # ── Profile confirm ──────────────────────────────────
        whatsapp_service.send_message(
            "whatsapp:" + phone,
            (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "PROFILE COMPLETE!\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Name: " + str(name) + "\n"
                "Age: " + str(updated_user.get("age")) + " yrs\n"
                "Weight: " + str(updated_user.get("weight")) + " kg\n"
                "Height: " + str(updated_user.get("height")) + " cm\n"
                "Goal: " + str(goal) + "\n"
                "Diet: " + str(updated_user.get("diet_preference")) + "\n"
                "Budget: " + str(budget).title() + "\n"
                "Region: " + str(region) + "\n"
                "Gym Days: " + str(workout_days) + " per week\n"
                "Session: " + str(updated_user.get("available_workout_time", 60)) + " min\n"
                "Gym Time: " + str(updated_user.get("gym_time")) + "\n\n"
                "Plan generate ho raha hai...\n"
                "30 seconds wait karo!"
            )
        )

        # ── Generate plans ───────────────────────────────────
        print("Generating plans for:", phone)
        workout_plan = ai_service.generate_workout_plan(updated_user)
        diet_plan = ai_service.generate_diet_plan(updated_user)

        # ── Save ─────────────────────────────────────────────
        db_service.update_user(phone, {
            "workout_plan": workout_plan,
            "diet_plan": diet_plan,
            "plan_intensity": "moderate",
            "plan_generated_at": datetime.utcnow(),
            "onboarding_complete": True,
            "onboarding_step": "complete"
        })

        # ── Send schedule + menu ─────────────────────────────
        schedule = self.DAY_SCHEDULE.get(workout_days, self.DAY_SCHEDULE[4])
        schedule_text = ""
        for day_num, muscle in schedule.items():
            schedule_text += "Day " + str(day_num) + ": " + muscle + "\n"

        time.sleep(1)

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "PLAN READY HAI " + str(name).upper() + "!\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "TERA WEEKLY SCHEDULE:\n\n"
                + schedule_text +
                "\n━━━━━━━━━━━━━━━━━━━━━━\n"
                "COMMANDS:\n\n"
                "W1-W6  - Day wise workout\n"
                "D      - Diet plan\n"
                "S      - Supplements guide\n"
                "T      - Today ka workout\n"
                "P      - Progress update\n"
                "M      - Main menu\n"
                "/dashboard - Mera progress\n"
                "DONE   - Workout done mark karo\n"
                "SKIP   - (Coach will motivate!)\n"
                "CAL [food] - Calorie check\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Koi bhi command type karo!\n"
                "Ya fitness question pooch lo!"
            )
        )

        return self._get_final_message(updated_user)

    def _get_final_message(self, user: dict) -> str:
        name = user.get("name", "Bhai")
        goal = user.get("goal", "Fitness")
        gym_time = user.get("gym_time", "N/A")
        sleep_time = user.get("sleep_time", "N/A")
        return (
            "REMINDERS SET!\n\n"
            "Gym reminder: " + str(gym_time) + "\n"
            "Sleep reminder: " + str(sleep_time) + "\n"
            "Meal reminders: Din bhar\n\n"
            "Goal: " + str(goal) + "\n"
            "90 din consistent reh!\n\n"
            "W1 type karo - Day 1 start karte hain! 💪"
        )

    # ================================================================
    # GENERAL CONVERSATION
    # ================================================================

    def _handle_general_conversation(
        self, phone: str, user: dict, message: str
    ) -> str:
        msg = message.lower().strip()
        workout_days = int(user.get("workout_days", 4))
        schedule = self.DAY_SCHEDULE.get(workout_days, self.DAY_SCHEDULE[4])

        # ── /dashboard ────────────────────────────────────────
        if msg in ["/dashboard", "dashboard", "mera progress", "my progress"]:
            return self._send_dashboard(phone, user)

        # ── Workout Day Commands W1-W7 ────────────────────────
        for day_num in range(1, 8):
            if msg in ["w" + str(day_num), "day " + str(day_num),
                       "workout " + str(day_num)]:
                return self._send_day_workout(
                    phone, user, day_num, schedule
                )

        # ── Workout DONE ──────────────────────────────────────
        if engagement_service.is_workout_done(message):
            return self._handle_workout_done(phone, user)

        # ── SKIP intent ───────────────────────────────────────
        if engagement_service.is_skip_intent(message):
            return engagement_service.get_skip_coaching()

        # ── Calorie check ─────────────────────────────────────
        if msg.startswith("cal ") or msg.startswith("calories "):
            food_text = (
                message[4:].strip()
                if msg.startswith("cal ")
                else message[9:].strip()
            )
            result = diet_intelligence.format_calorie_estimate(food_text)
            cal_data = diet_intelligence.estimate_calories_from_text(food_text)
            if cal_data["total_calories"] > 0:
                db_service.add_calorie_log(
                    phone, cal_data["total_calories"], food_text
                )
            return result

        # ── Diet Command ──────────────────────────────────────
        if msg in ["d", "diet", "khana", "food", "diet plan"]:
            return self._send_diet(phone, user)

        # ── Budget tip ────────────────────────────────────────
        elif msg in ["budget", "budget tip", "cheap food", "sasta"]:
            budget = user.get("budget", "medium")
            return diet_intelligence.get_budget_tip(budget)

        # ── Supplements ───────────────────────────────────────
        elif msg in ["s", "supp", "supplements", "supplement"]:
            return self._get_supplements_guide(user)

        # ── Today's Workout ───────────────────────────────────
        elif msg in ["t", "today", "aaj", "aaj ka"]:
            return ai_service.get_fitness_response(
                user,
                "Give today's workout in 60 words max. "
                "Just exercise names with sets and reps. "
                "Motivating Hinglish tone. Plain text.",
                []
            )

        # ── Progress ──────────────────────────────────────────
        elif msg in ["p", "progress", "update"]:
            return (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "PROGRESS UPDATE\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Yeh 4 cheezein batao:\n\n"
                "1. Current weight (kg)?\n"
                "2. Is hafte kitne workouts?\n"
                "3. Diet follow ki?\n"
                "4. Koi problem hai?\n\n"
                "Sab ek saath bhejo!"
            )

        # ── Menu ─────────────────────────────────────────────
        elif msg in ["m", "menu", "help", "options"]:
            schedule_text = ""
            for d, muscle in schedule.items():
                schedule_text += "W" + str(d) + " - " + muscle + "\n"
            return (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "MAIN MENU\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "WORKOUT:\n"
                + schedule_text +
                "\nD        - Diet plan\n"
                "S        - Supplements\n"
                "T        - Today workout\n"
                "P        - Progress\n"
                "/dashboard - Full progress\n"
                "DONE     - Mark workout done\n"
                "CAL [food] - Calorie check\n\n"
                "Ya seedha question pooch!"
            )

        # ── Weight Update ─────────────────────────────────────
        elif "update weight" in msg:
            try:
                new_w = msg.replace("update weight", "").strip()
                old_w = float(user.get("weight", 0))
                db_service.update_user(phone, {"weight": float(new_w)})
                diff = float(new_w) - old_w
                change = (
                    str(abs(round(diff, 1))) + " kg loss! Amazing! 🔥"
                    if diff < 0
                    else str(round(diff, 1)) + " kg gain! Muscles ban rahe hain! 💪"
                )
                return (
                    "Weight Updated!\n\n"
                    "Old: " + str(old_w) + " kg\n"
                    "New: " + str(new_w) + " kg\n"
                    "Change: " + change + "\n\n"
                    "Keep going! 💯"
                )
            except Exception:
                return "Format: update weight 80"

        # ── AI Chat with tone detection ───────────────────────
        else:
            tone = engagement_service.detect_tone(message)
            tone_hint = engagement_service.get_tone_system_hint(tone)
            history = user.get("conversation_history", [])
            return ai_service.get_fitness_response(
                user, message, history, tone_hint=tone_hint
            )

    # ================================================================
    # WORKOUT DONE — STREAK UPDATE
    # ================================================================

    def _handle_workout_done(self, phone: str, user: dict) -> str:
        result = db_service.log_workout_done(phone)

        if result.get("already_done"):
            return (
                "Arre bhai, aaj ka already count ho gaya! 😄\n"
                "Double credit nahi milta. Kal bhi aana! 💪"
            )

        streak = result.get("streak", 0)
        weekly = result.get("weekly", 0)
        total = result.get("total", 0)

        reward = engagement_service.get_streak_reward(streak, total)

        base_msg = (
            "WORKOUT DONE! 💪\n\n"
            "Streak: " + str(streak) + " din 🔥\n"
            "Is hafte: " + str(weekly) + " workouts\n"
            "Total: " + str(total) + " workouts"
        )

        if reward:
            base_msg += "\n\n" + reward
        else:
            base_msg += "\n\nAal izz well! Kal bhi aana! 🔥"

        return base_msg

    # ================================================================
    # DASHBOARD
    # ================================================================

    def _send_dashboard(self, phone: str, user: dict) -> str:
        name = user.get("name", "Bhai")
        goal = user.get("goal", "N/A")
        weight = user.get("weight", "N/A")
        streak = int(user.get("streak_count", 0))
        longest = int(user.get("longest_streak", 0))
        weekly = int(user.get("weekly_workouts_done", 0))
        workout_days = int(user.get("workout_days", 4))
        total = int(user.get("total_workouts_done", 0))
        score = int(user.get("consistency_score", 0))
        intensity = user.get("plan_intensity", "moderate")
        budget = user.get("budget", "N/A")
        region = user.get("region", "N/A")
        diet = user.get("diet_preference", "N/A")

        label = engagement_service.get_consistency_label(score)

        # Weekly progress bar
        done_bars = min(weekly, workout_days)
        bar = "[" + "#" * done_bars + "-" * (workout_days - done_bars) + "]"

        # Calorie logs (last 3 days)
        cal_logs = user.get("calorie_logs", [])
        cal_section = ""
        if cal_logs:
            last = cal_logs[-3:] if len(cal_logs) >= 3 else cal_logs
            cal_lines = ""
            for entry in last:
                cal_lines += (
                    entry.get("date", "") + ": "
                    + str(entry.get("calories", 0)) + " kcal\n"
                )
            cal_section = (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "RECENT CALORIE LOGS\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                + cal_lines + "\n"
            )

        # Motivational note
        if score >= 80:
            note = "Tu toh BEAST hai! Plan upgrade ho raha hai! 🦁"
        elif score >= 50:
            note = "Acha chal raha hai! Thoda aur push kar! 💪"
        elif streak > 0:
            note = "Streak " + str(streak) + " chal rahi hai — mat todna! 🔥"
        else:
            note = "Aaj se shuru karo — DONE type karo workout ke baad! 🎯"

        dashboard = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "TERA DASHBOARD — " + str(name).upper() + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "GOAL: " + str(goal) + "\n"
            "WEIGHT: " + str(weight) + " kg\n"
            "DIET: " + str(diet) + " | REGION: " + str(region) + "\n"
            "BUDGET: " + str(budget).title() + "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "STREAK & CONSISTENCY\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Current Streak: " + str(streak) + " din 🔥\n"
            "Best Streak: " + str(longest) + " din 🏆\n"
            "Total Workouts: " + str(total) + "\n\n"
            "Is hafte: " + bar + " " + str(weekly) + "/" + str(workout_days) + "\n"
            "Consistency: " + str(score) + "% — " + label + "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "PLAN STATUS\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Current Intensity: " + str(intensity).upper() + "\n"
            "(Plan har Sunday auto-update hota hai)\n\n"
            + cal_section +
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "COACH MESSAGE\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + note
        )

        return dashboard

    # ================================================================
    # SEND SINGLE DAY WORKOUT
    # ================================================================

    def _send_day_workout(
        self,
        phone: str,
        user: dict,
        day_num: int,
        schedule: dict
    ) -> str:
        muscle_group = schedule.get(day_num, "Full Body")

        # REST day
        if "REST" in muscle_group.upper():
            return (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "DAY " + str(day_num) + " - ACTIVE RECOVERY\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Aaj REST day hai!\n\n"
                "ACTIVE RECOVERY:\n"
                "Morning walk: 20-30 min\n"
                "Target: 100-110 bpm only\n\n"
                "STRETCHING (15 min):\n"
                "Cat cow: 10 reps\n"
                "Hip flexor: 45 sec each\n"
                "Hamstring: 45 sec each\n"
                "Spinal twist: 30 sec each\n"
                "Child pose: 2 min\n\n"
                "Yaad rakh:\n"
                "Muscles rest mein grow karti hain!\n"
                "Kal ke workout ke liye recharge karo.\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "W" + str(day_num + 1 if day_num < 7 else 1) +
                " type karo next day ke liye!"
            )

        # Workout day — generate fresh
        whatsapp_service.send_message(
            "whatsapp:" + phone,
            (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "DAY " + str(day_num) + " - " +
                muscle_group.upper() + "\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Generating tera workout...\n"
                "10 seconds wait karo!"
            )
        )

        day_workout = ai_service.generate_single_day_workout(
            user, day_num, muscle_group
        )

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            day_workout
        )

        next_day = day_num + 1 if day_num < 7 else 1
        next_muscle = schedule.get(next_day, "Rest")

        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Crush it today bhai!\n\n"
            "Workout ho jaye toh DONE type karo! 💪\n"
            "Next: Day " + str(next_day) +
            " - " + next_muscle + "\n"
            "W" + str(next_day) + " type karo next day!\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ================================================================
    # SEND DIET
    # ================================================================

    def _send_diet(self, phone: str, user: dict) -> str:
        diet_plan = user.get("diet_plan")

        if not diet_plan:
            return "Diet plan nahi mila. 'start' type karo."

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "TERA DIET PLAN\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "WHY NUTRITION MATTERS:\n\n"
                "70% results kitchen se aate hain.\n"
                "Gym sirf 30% hai.\n\n"
                "Protein = Muscle building block\n"
                "Carbs = Energy fuel\n"
                "Fats = Hormone production\n\n"
                "Post workout meal = Most important\n"
                "Skip mat karna kabhi!\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
        )

        time.sleep(0.5)

        parts = self._split_text(diet_plan, 1000)
        for part in parts:
            whatsapp_service.send_message("whatsapp:" + phone, part)
            time.sleep(1)

        budget = user.get("budget", "medium")
        budget_tip = diet_intelligence.get_budget_tip(budget)

        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Diet plan complete!\n\n"
            "Golden Rules:\n"
            "Har 3 ghante mein kuch khao\n"
            "Post workout skip mat karo\n"
            "3-4 liter paani daily\n"
            "Raat ko heavy carbs avoid karo\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + budget_tip + "\n\n"
            "S type karo supplements ke liye!"
        )

    # ================================================================
    # SUPPLEMENTS GUIDE (budget-aware)
    # ================================================================

    def _get_supplements_guide(self, user: dict) -> str:
        budget = user.get("budget", "medium")

        if budget == "low":
            core = (
                "BUDGET FRIENDLY SUPPLEMENTS:\n"
                "Creatine Monohydrate\n"
                "Daily: 5g | Cheapest, most effective\n\n"
                "Multivitamin\n"
                "Morning: 1 tablet | Nutrient gaps fill\n\n"
                "Protein via food: Dal + Soya chunks\n"
                "Whey skip karo — pehle diet fix karo!"
            )
        elif budget == "high":
            core = (
                "PREMIUM SUPPLEMENTS:\n"
                "Whey Isolate: 25-30g post workout\n"
                "Creatine: 5g daily\n"
                "Multivitamin: Morning\n"
                "Omega 3 Fish Oil: 1-2g daily\n"
                "Vitamin D3: 2000 IU\n"
                "Magnesium: 400mg night\n"
                "Pre Workout: Before gym\n"
                "BCAA: During workout\n"
                "ZMA: Before bed"
            )
        else:
            core = (
                "MUST HAVE:\n"
                "Whey Protein\n"
                "Post workout: 25-30g\n\n"
                "Creatine Monohydrate\n"
                "Daily: 5g\n\n"
                "Multivitamin\n"
                "Morning: 1 tablet\n\n"
                "GOOD TO HAVE:\n"
                "Omega 3: 1-2g daily\n"
                "Vitamin D3: 2000 IU\n"
                "Magnesium: 400mg night"
            )

        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "SUPPLEMENT GUIDE\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            + core + "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Budget: " + str(budget).title() + " plan ke hisaab se!"
        )

    # ================================================================
    # TEXT SPLITTER
    # ================================================================

    def _split_text(self, text: str, max_length: int) -> list:
        if len(text) <= max_length:
            return [text]

        parts = []
        lines = text.split("\n")
        current = ""

        for line in lines:
            test = current + line + "\n"
            if len(test) > max_length:
                if current.strip():
                    parts.append(current.strip())
                current = line + "\n"
            else:
                current = test

        if current.strip():
            parts.append(current.strip())

        return parts


# ================================================================
# CRITICAL - DO NOT REMOVE
# ================================================================
conversation_manager = ConversationManager()
