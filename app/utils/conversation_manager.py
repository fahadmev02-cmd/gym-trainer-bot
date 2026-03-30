# app/utils/conversation_manager.py

from app.services.database_service import db_service
from app.services.sheets_service import sheets_service
from app.services.ai_service import ai_service
from app.services.whatsapp_service import whatsapp_service
import time


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
        elif step == "collecting_workout_days":
            return self._collect_workout_days(phone, message)
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
            "WELCOME TO AI GYM TRAINER\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Main hoon tera personal AI Fitness Trainer!\n\n"
            "Main dunga:\n"
            "Personalized Workout Plan\n"
            "Indian Diet Plan + Macros\n"
            "Daily Reminders\n"
            "Progress Tracking\n"
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
                "is_verified": True,
                "onboarding_step": "collecting_age"
            })
            return (
                "MEMBERSHIP VERIFIED!\n\n"
                "Welcome " + name + "!\n\n"
                "Chalo tera Fitness Profile banate hain.\n"
                "Sirf 9 questions - 2 minute ka kaam!\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "QUESTION 1 OF 9\n"
                "Teri age kya hai?\n"
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
                "QUESTION 2 OF 9\n"
                "Tera current weight? (kg)\n\n"
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
                "QUESTION 3 OF 9\n"
                "Teri height? (cm mein)\n\n"
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
                "QUESTION 4 OF 9\n"
                "Tera fitness goal?\n\n"
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
                "QUESTION 5 OF 9\n"
                "Diet preference?\n\n"
                "1 - Veg\n"
                "2 - Non-Veg\n\n"
                "1 ya 2 type karo"
            )
        else:
            return "1 se 6 number type karo."

    def _collect_diet(self, phone: str, message: str) -> str:
        msg = message.lower().strip()
        if msg in ["1", "veg", "vegetarian", "v"]:
            diet = "Veg"
        elif msg in ["2", "non-veg", "nonveg", "non veg", "nv"]:
            diet = "Non-Veg"
        else:
            return "1 (Veg) ya 2 (Non-Veg) type karo."

        db_service.update_user(phone, {
            "diet_preference": diet,
            "onboarding_step": "collecting_workout_days"
        })
        return (
            "Diet: " + diet + "\n\n"
            "QUESTION 6 OF 9\n"
            "Hafte mein kitne din gym?\n\n"
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
                "onboarding_step": "collecting_meals"
            })
            return (
                str(days) + " days per week!\n\n"
                "QUESTION 7 OF 9\n"
                "Din mein kitni baar khana?\n\n"
                "3 - Basic\n"
                "4 - Good\n"
                "5 - Best for fitness\n"
                "6 - Advanced\n\n"
                "Number type karo"
            )
        except ValueError:
            return "Sirf number type karo. Example: 4"

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
                "QUESTION 8 OF 9\n"
                "Subah kitne baje uthta hai?\n\n"
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
            "QUESTION 9 OF 10\n"
            "Gym kitne baje jaata hai?\n\n"
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
            "LAST QUESTION! 10 OF 10\n"
            "Raat ko kitne baje sota hai?\n\n"
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

        # ── Profile confirm karo ──────────────────────────────
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
                "Gym Days: " + str(workout_days) + " per week\n"
                "Gym Time: " + str(updated_user.get("gym_time")) + "\n\n"
                "Plan generate ho raha hai...\n"
                "30 seconds wait karo!"
            )
        )

        # ── Plans generate karo ───────────────────────────────
        print("Generating plans for:", phone)
        workout_plan = ai_service.generate_workout_plan(updated_user)
        diet_plan = ai_service.generate_diet_plan(updated_user)

        # ── Save karo ─────────────────────────────────────────
        db_service.update_user(phone, {
            "workout_plan": workout_plan,
            "diet_plan": diet_plan,
            "onboarding_complete": True,
            "onboarding_step": "complete"
        })

        # ── Schedule bhejo ────────────────────────────────────
        schedule = self.DAY_SCHEDULE.get(workout_days, self.DAY_SCHEDULE[4])
        schedule_text = ""
        for day_num, muscle in schedule.items():
            schedule_text += "Day " + str(day_num) + ": " + muscle + "\n"

        time.sleep(1)

        # ── Main menu bhejo ───────────────────────────────────
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
                "W1 - Day 1 workout detail\n"
                "W2 - Day 2 workout detail\n"
                "W3 - Day 3 workout detail\n"
                "W4 - Day 4 workout detail\n"
                "W5 - Day 5 workout detail\n"
                "W6 - Day 6 workout detail\n\n"
                "D  - Diet plan dekhna\n"
                "S  - Supplements guide\n"
                "T  - Today ka workout\n"
                "P  - Progress update\n"
                "M  - Main menu\n"
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
            "W1 type karo - Day 1 start karte hain!"
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

        # ── Workout Day Commands W1-W7 ────────────────────────
        for day_num in range(1, 8):
            if msg in ["w" + str(day_num), "day " + str(day_num),
                       "workout " + str(day_num)]:
                return self._send_day_workout(
                    phone, user, day_num, schedule
                )

        # ── Diet Command ──────────────────────────────────────
        if msg in ["d", "diet", "khana", "food", "diet plan"]:
            return self._send_diet(phone, user)

        # ── Supplements ───────────────────────────────────────
        elif msg in ["s", "supp", "supplements", "supplement"]:
            return (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "SUPPLEMENT GUIDE\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "MUST HAVE:\n"
                "Whey Protein\n"
                "Post workout: 25-30g\n"
                "Muscle repair ke liye\n\n"
                "Creatine Monohydrate\n"
                "Daily: 5g\n"
                "Strength 10-15% badhata hai\n\n"
                "Multivitamin\n"
                "Morning: 1 tablet\n"
                "Nutrient gaps fill karta hai\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "GOOD TO HAVE:\n"
                "Omega 3: 1-2g daily\n"
                "Vitamin D3: 2000 IU morning\n"
                "Magnesium: 400mg night\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "ADVANCED:\n"
                "Pre Workout: Before gym\n"
                "BCAA: During workout\n"
                "ZMA: Before bed\n\n"
                "Budget kam hai?\n"
                "Whey + Creatine se shuru karo!\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )

        # ── Today's Workout ───────────────────────────────────
        elif msg in ["t", "today", "aaj", "aaj ka"]:
            return ai_service.get_fitness_response(
                user,
                "Give today's workout in 60 words max. "
                "Just exercise names with sets and reps. "
                "Motivating tone. Plain text.",
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
                "\nD  - Diet plan\n"
                "S  - Supplements\n"
                "T  - Today workout\n"
                "P  - Progress\n\n"
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
                    str(abs(round(diff, 1))) + " kg loss! Amazing!"
                    if diff < 0
                    else str(round(diff, 1)) + " kg gain! Muscles!"
                )
                return (
                    "Weight Updated!\n\n"
                    "Old: " + str(old_w) + " kg\n"
                    "New: " + str(new_w) + " kg\n"
                    "Change: " + change + "\n\n"
                    "Keep going!"
                )
            except Exception:
                return "Format: update weight 80"

        # ── AI Chat ───────────────────────────────────────────
        else:
            history = user.get("conversation_history", [])
            return ai_service.get_fitness_response(user, message, history)

    # ================================================================
    # SEND SINGLE DAY WORKOUT - CLEAN SHORT
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

        # Workout day - generate fresh
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

        # Generate single day workout
        day_workout = ai_service.generate_single_day_workout(
            user, day_num, muscle_group
        )

        # Send the workout
        whatsapp_service.send_message(
            "whatsapp:" + phone,
            day_workout
        )

        # Next day hint
        next_day = day_num + 1 if day_num < 7 else 1
        next_muscle = schedule.get(next_day, "Rest")

        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Crush it today bhai!\n\n"
            "Next: Day " + str(next_day) +
            " - " + next_muscle + "\n"
            "W" + str(next_day) + " type karo next day!\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ================================================================
    # SEND DIET - CLEAN FORMAT
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

        # Send diet plan
        parts = self._split_text(diet_plan, 1000)
        for part in parts:
            whatsapp_service.send_message("whatsapp:" + phone, part)
            time.sleep(1)

        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Diet plan complete!\n\n"
            "Golden Rules:\n"
            "Har 3 ghante mein kuch khao\n"
            "Post workout skip mat karo\n"
            "3-4 liter paani daily\n"
            "Raat ko heavy carbs avoid karo\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "S type karo supplements ke liye!"
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