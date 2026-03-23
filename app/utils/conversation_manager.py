# app/utils/conversation_manager.py

from app.services.database_service import db_service
from app.services.sheets_service import sheets_service
from app.services.ai_service import ai_service
from app.services.whatsapp_service import whatsapp_service


class ConversationManager:

    def process_message(self, phone: str, message: str) -> str:
        phone = phone.replace("whatsapp:", "").strip()
        user = db_service.get_or_create_user(phone)
        db_service.save_conversation_message(phone, "user", message)
        response = self._handle_message(user, phone, message.strip())
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

    def _handle_start(self, phone: str) -> str:
        db_service.update_onboarding_step(phone, "awaiting_receipt")
        return """Welcome to AI Gym Trainer! 

I am your personal AI fitness trainer. I will help you with:
- Personalized workout plans
- Indian diet plans
- Daily reminders
- Progress tracking
- Fitness guidance

To get started, please enter your gym receipt number."""

    def _handle_receipt_verification(self, phone: str, message: str, user: dict) -> str:
        receipt_number = message.strip()
        result = sheets_service.verify_membership(receipt_number)

        if result["is_valid"]:
            db_service.update_user(phone, {
                "receipt_number": receipt_number,
                "is_verified": True,
                "onboarding_step": "collecting_age"
            })
            member_name = result.get("name", "there")
            return "Membership Verified! Welcome " + member_name + "! Let us set up your fitness profile. Question 1 of 9: What is your age in years? Example: 24"
        else:
            return "Receipt number not found. Please check your receipt number and try again. Contact your gym if you need help."

    def _collect_age(self, phone: str, message: str) -> str:
        try:
            age = int(message.strip())
            if not (10 <= age <= 80):
                return "Please enter a valid age between 10 and 80 years"
            db_service.update_user(phone, {
                "age": age,
                "onboarding_step": "collecting_weight"
            })
            return "Got it! Question 2 of 9: What is your current weight in kg? Example: 75"
        except ValueError:
            return "Please enter your age as a number. Example: 24"

    def _collect_weight(self, phone: str, message: str) -> str:
        try:
            weight = float(message.strip().replace("kg", "").replace("KG", ""))
            if not (30 <= weight <= 250):
                return "Please enter a valid weight between 30 and 250 kg"
            db_service.update_user(phone, {
                "weight": weight,
                "onboarding_step": "collecting_height"
            })
            return "Noted! Question 3 of 9: What is your height in cm? Example: 175"
        except ValueError:
            return "Please enter your weight as a number. Example: 75"

    def _collect_height(self, phone: str, message: str) -> str:
        try:
            height = float(message.strip().replace("cm", "").replace("CM", ""))
            if not (100 <= height <= 250):
                return "Please enter a valid height between 100 and 250 cm"
            db_service.update_user(phone, {
                "height": height,
                "onboarding_step": "collecting_goal"
            })
            return "Perfect! Question 4 of 9: What is your fitness goal? Reply with a number: 1 for Fat Loss, 2 for Muscle Gain, 3 for Maintain Fitness, 4 for Increase Strength, 5 for Improve Endurance"
        except ValueError:
            return "Please enter your height as a number. Example: 175"

    def _collect_goal(self, phone: str, message: str) -> str:
        goals = {
            "1": "Fat Loss",
            "2": "Muscle Gain",
            "3": "Maintain Fitness",
            "4": "Increase Strength",
            "5": "Improve Endurance"
        }
        goal = goals.get(message.strip())

        if not goal:
            message_lower = message.lower()
            if "fat" in message_lower or "loss" in message_lower or "weight" in message_lower:
                goal = "Fat Loss"
            elif "muscle" in message_lower or "bulk" in message_lower or "gain" in message_lower:
                goal = "Muscle Gain"
            elif "maintain" in message_lower or "fit" in message_lower:
                goal = "Maintain Fitness"
            elif "strength" in message_lower or "strong" in message_lower:
                goal = "Increase Strength"
            elif "endurance" in message_lower or "cardio" in message_lower:
                goal = "Improve Endurance"

        if goal:
            db_service.update_user(phone, {
                "goal": goal,
                "onboarding_step": "collecting_diet"
            })
            return "Goal set to " + goal + "! Question 5 of 9: What is your diet preference? Reply 1 for Veg or 2 for Non-Veg"
        else:
            return "Please reply with a number 1 to 5. 1 for Fat Loss, 2 for Muscle Gain, 3 for Maintain Fitness, 4 for Increase Strength, 5 for Improve Endurance"

    def _collect_diet(self, phone: str, message: str) -> str:
        message_lower = message.lower().strip()
        if message_lower in ["1", "veg", "vegetarian", "v"]:
            diet = "Veg"
        elif message_lower in ["2", "non-veg", "nonveg", "non veg", "nv"]:
            diet = "Non-Veg"
        else:
            return "Please reply with 1 for Veg or 2 for Non-Veg"

        db_service.update_user(phone, {
            "diet_preference": diet,
            "onboarding_step": "collecting_workout_days"
        })
        return "Diet set to " + diet + "! Question 6 of 9: How many days per week can you workout? Reply with a number like 3, 4, 5, or 6"

    def _collect_workout_days(self, phone: str, message: str) -> str:
        try:
            days = int(message.strip())
            if not (1 <= days <= 7):
                return "Please enter a number between 1 and 7"
            db_service.update_user(phone, {
                "workout_days": days,
                "onboarding_step": "collecting_meals"
            })
            return "Got it " + str(days) + " days per week! Question 7 of 9: How many meals do you eat per day? Reply with a number like 3, 4, 5, or 6"
        except ValueError:
            return "Please enter a number. Example: 4"

    def _collect_meals(self, phone: str, message: str) -> str:
        try:
            meals = int(message.strip())
            if not (2 <= meals <= 8):
                return "Please enter a valid number between 2 and 8"
            db_service.update_user(phone, {
                "meals_per_day": meals,
                "onboarding_step": "collecting_wake_time"
            })
            return "Got it " + str(meals) + " meals per day! Question 8 of 9: What time do you usually wake up? Example: 6:00 AM"
        except ValueError:
            return "Please enter a number. Example: 4"

    def _collect_wake_time(self, phone: str, message: str) -> str:
        wake_time = message.strip()
        if len(wake_time) < 3:
            return "Please enter a valid time. Example: 6:00 AM"
        db_service.update_user(phone, {
            "wake_up_time": wake_time,
            "onboarding_step": "collecting_gym_time"
        })
        return "Wake up time set to " + wake_time + "! Question 9 of 10: What time do you go to gym? Example: 6:00 PM"

    def _collect_gym_time(self, phone: str, message: str) -> str:
        gym_time = message.strip()
        if len(gym_time) < 3:
            return "Please enter a valid time. Example: 6:00 PM"
        db_service.update_user(phone, {
            "gym_time": gym_time,
            "onboarding_step": "collecting_sleep_time"
        })
        return "Gym time set to " + gym_time + "! Last question 10 of 10: What time do you usually sleep? Example: 11:00 PM"

    def _collect_sleep_time(self, phone: str, user: dict, message: str) -> str:
        sleep_time = message.strip()
        if len(sleep_time) < 3:
            return "Please enter a valid time. Example: 11:00 PM"

        db_service.update_user(phone, {
            "sleep_time": sleep_time,
            "onboarding_step": "generating_plans"
        })

        updated_user = db_service.get_user(phone)

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            "Profile Complete! Thank you " + str(updated_user.get("name", "there")) + "! I am now generating your personalized Workout Plan and Diet Plan. Please wait a moment..."
        )

        workout_plan = ai_service.generate_workout_plan(updated_user)
        diet_plan = ai_service.generate_diet_plan(updated_user)

        db_service.update_user(phone, {
            "workout_plan": workout_plan,
            "diet_plan": diet_plan,
            "onboarding_complete": True,
            "onboarding_step": "complete"
        })

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            "YOUR WORKOUT PLAN\n\n" + workout_plan
        )

        whatsapp_service.send_message(
            "whatsapp:" + phone,
            "YOUR DIET PLAN\n\n" + diet_plan
        )

        return "You are all set " + str(updated_user.get("name", "there")) + "! Your plans have been saved. I will send you gym reminders at " + str(updated_user.get("gym_time")) + " and sleep reminders at " + str(updated_user.get("sleep_time")) + ". Type workout to see your workout plan. Type diet to see your diet plan. Type progress to log your progress. Lets crush your " + str(updated_user.get("goal")) + " goal!"

    def _handle_general_conversation(self, phone: str, user: dict, message: str) -> str:
        message_lower = message.lower().strip()

        if message_lower in ["workout", "workout plan", "my workout", "show workout"]:
            workout_plan = user.get("workout_plan")
            if workout_plan:
                return "YOUR WORKOUT PLAN\n\n" + workout_plan
            else:
                return "Generating your workout plan..."

        elif message_lower in ["diet", "diet plan", "my diet", "show diet", "food"]:
            diet_plan = user.get("diet_plan")
            if diet_plan:
                return "YOUR DIET PLAN\n\n" + diet_plan
            else:
                return "Generating your diet plan..."

        elif "progress" in message_lower:
            return "Weekly Progress Check. Please share: 1. Current weight in kg. 2. How many workouts this week. 3. Any difficulties or questions."

        elif message_lower.startswith("update weight"):
            try:
                new_weight = message_lower.replace("update weight", "").strip()
                db_service.update_user(phone, {"weight": new_weight})
                return "Weight updated to " + new_weight + " kg! Keep tracking your progress."
            except:
                return "Please format as: update weight 80"

        else:
            conversation_history = user.get("conversation_history", [])
            return ai_service.get_fitness_response(user, message, conversation_history)


conversation_manager = ConversationManager()