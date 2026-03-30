# app/services/ai_service.py
# Groq (text) + Gemini Vision (image) - BOTH FREE

import requests
import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_model = "llama-3.1-8b-instant"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if self.groq_api_key:
            print("✅ Groq AI (text) - Ready")
        else:
            print("❌ GROQ_API_KEY not found")

        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)
            self._check_gemini_models()
            print("✅ Gemini Vision (image) - Ready")
        else:
            print("❌ GEMINI_API_KEY not found")
            self.gemini_client = None
            self.gemini_model_name = None

    def _check_gemini_models(self):
        try:
            preferred = [
                "gemini-1.5-flash-latest",
                "gemini-1.5-pro-latest",
                "gemini-pro-vision",
            ]
            available = []
            for m in self.gemini_client.models.list():
                available.append(m.name)

            self.gemini_model_name = None
            for pref in preferred:
                for avail in available:
                    if pref in avail:
                        self.gemini_model_name = avail
                        print(f"✅ Gemini model: {avail}")
                        break
                if self.gemini_model_name:
                    break

            if not self.gemini_model_name and available:
                self.gemini_model_name = available[0]
                print(f"✅ Using: {available[0]}")

        except Exception as e:
            print(f"❌ Model check error: {e}")
            self.gemini_model_name = "gemini-1.5-flash-latest"

    # ════════════════════════════════════════════════
    # GROQ - TEXT
    # ════════════════════════════════════════════════

    def _call_groq(self, system_prompt, conversation_history, user_message):
        try:
            if not self.groq_api_key:
                return "AI service not configured."

            messages = [{"role": "system", "content": system_prompt}]
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            messages.append({"role": "user", "content": user_message})

            headers = {
                "Authorization": "Bearer " + self.groq_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.groq_model,
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }

            response = requests.post(
                self.groq_base_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 429:
                return "Thoda busy hoon. 1 minute baad try karo."
            elif response.status_code == 401:
                return "AI configuration error."
            else:
                return "Technical issue. Try again."

        except requests.exceptions.Timeout:
            return "Response slow hai. Try again karo."
        except requests.exceptions.ConnectionError:
            return "Connection error. Try again karo."
        except Exception as e:
            print("❌ Groq error:", e)
            return "Technical issue. Try again."

    # ════════════════════════════════════════════════
    # SINGLE DAY WORKOUT - SHORT AND CLEAN
    # ════════════════════════════════════════════════

    def generate_single_day_workout(
        self, user_data: dict, day_num: int, muscle_group: str
    ) -> str:
        """
        Sirf ek din ka workout generate karo
        Short clean aur readable
        """
        system_prompt = (
            "You are an elite personal trainer. "
            "Create a single day workout plan. "
            "Keep it SHORT and CLEAN. "
            "Maximum 400 words total. "
            "Plain text only. No stars. No hashtags."
        )

        user_message = (
            "Create Day " + str(day_num) + " workout for "
            + str(muscle_group) + ".\n"
            "User goal: " + str(user_data.get("goal", "Fitness")) + "\n\n"

            "EXACT FORMAT - Follow this exactly:\n\n"

            "CARDIO (15 min) - Heart Health\n"
            "Exercise 1: X min | X bpm\n"
            "Exercise 2: X min\n\n"

            "WARM UP (10 min) - Injury Prevention\n"
            "Exercise 1: X reps\n"
            "Exercise 2: X seconds\n\n"

            "MAIN WORKOUT\n"
            "1. Exercise Name\n"
            "   X sets x X reps | X sec rest\n"
            "   Tip: one line tip\n\n"
            "2. Exercise Name\n"
            "   X sets x X reps | X sec rest\n"
            "   Tip: one line tip\n\n"
            "[5 to 6 exercises total]\n\n"

            "CORE (10 min) - Your Foundation\n"
            "1. Exercise: X sets x X reps\n"
            "2. Exercise: X sets x X reps\n"
            "3. Exercise: X sets x X reps\n"
            "4. Exercise: X sets x X reps\n\n"

            "STRETCHING (8 min) - Recovery\n"
            "1. Stretch name: X sec\n"
            "2. Stretch name: X sec\n"
            "3. Stretch name: X sec\n"
            "4. Stretch name: X sec\n\n"

            "RULES:\n"
            "- Maximum 400 words total\n"
            "- 5 to 6 main exercises only\n"
            "- 4 core exercises always\n"
            "- 4 stretches always\n"
            "- Muscle group specific everything\n"
            "- No extra explanation\n"
            "- No markdown\n"
        )

        return self._call_groq(system_prompt, [], user_message)

    # ════════════════════════════════════════════════
    # FULL WORKOUT PLAN - STORED IN DB
    # ════════════════════════════════════════════════

    def generate_workout_plan(self, user_data: dict) -> str:
        """
        Poora plan ek baar generate karo
        DB mein save karo
        User maange tab day by day bhejo
        """
        workout_days = int(user_data.get("workout_days", 4))
        goal = str(user_data.get("goal", "Fitness"))

        # Day schedules based on workout days
        schedules = {
            3: [
                "Chest and Triceps",
                "Back and Biceps",
                "REST",
                "Legs and Shoulders",
                "REST",
                "Full Body",
                "REST"
            ],
            4: [
                "Chest and Triceps",
                "Back and Biceps",
                "REST",
                "Legs",
                "Shoulders and Abs",
                "REST",
                "REST"
            ],
            5: [
                "Chest and Triceps",
                "Back and Biceps",
                "Legs",
                "REST",
                "Shoulders",
                "Full Body",
                "REST"
            ],
            6: [
                "Chest",
                "Back and Biceps",
                "Legs",
                "Shoulders",
                "Arms and Abs",
                "Full Body",
                "REST"
            ]
        }

        schedule = schedules.get(workout_days, schedules[4])

        system_prompt = (
            "You are an elite personal trainer. "
            "Create a structured 7 day workout schedule. "
            "Plain text only. No stars. No hashtags. No markdown."
        )

        user_message = (
            "Create a 7 day workout plan for:\n"
            "Goal: " + goal + "\n"
            "Workout days: " + str(workout_days) + " per week\n"
            "Schedule: " + str(schedule) + "\n\n"

            "FORMAT:\n\n"
            "DAY 1 - CHEST AND TRICEPS\n"
            "Cardio: Treadmill 10 min + Jump rope 3 min\n"
            "Warm up: Arm circles, Shoulder rolls, Light pushups\n"
            "Main: Bench Press 4x10, Incline Press 4x12, "
            "Cable Flyes 3x15, Tricep Pushdown 4x12, "
            "Skull Crushers 3x12, Close Grip Press 3x10\n"
            "Core: Plank 3x60s, Crunches 3x20, "
            "Leg Raises 3x15, Russian Twists 3x20\n"
            "Stretch: Chest stretch, Tricep stretch, Shoulder stretch\n\n"

            "DAY 2 - REST\n"
            "Walk 20 min + Full body stretch 15 min\n\n"

            "[Continue for all 7 days same format]\n\n"

            "RULES:\n"
            "- Very short format like above\n"
            "- All 7 days\n"
            "- REST days include walk and stretch\n"
            "- Goal specific exercises\n"
            "- Maximum 500 words total\n"
        )

        return self._call_groq(system_prompt, [], user_message)

    # ════════════════════════════════════════════════
    # DIET PLAN - SHORT AND PROFESSIONAL
    # ════════════════════════════════════════════════

    def generate_diet_plan(self, user_data: dict) -> str:
        diet_type = str(user_data.get("diet_preference", "Veg"))
        goal = str(user_data.get("goal", "Fitness"))
        weight = str(user_data.get("weight", "70"))

        if diet_type.lower() == "veg":
            protein_sources = "paneer, tofu, dal, curd, milk, soya"
            restriction = "STRICTLY VEG - No meat, chicken, fish, eggs"
        else:
            protein_sources = "chicken breast, eggs, fish, paneer"
            restriction = "Non-veg allowed"

        is_comp = any(w in goal.lower() for w in [
            "compet", "stage", "show", "pro", "contest"
        ])

        plan_type = "Competition Prep" if is_comp else "Fitness"

        system_prompt = (
            "You are an elite Indian sports nutritionist. "
            "Create a professional diet plan. "
            "Short clean format. Maximum 500 words. "
            "Plain text only. No stars. No hashtags."
        )

        user_message = (
            "Create a " + plan_type + " diet plan for:\n"
            "Weight: " + weight + " kg\n"
            "Goal: " + goal + "\n"
            "Diet: " + diet_type + "\n"
            "Rule: " + restriction + "\n"
            "Protein sources: " + protein_sources + "\n\n"

            "EXACT FORMAT:\n\n"

            "DAILY TARGETS\n"
            "Calories: XXXX kcal\n"
            "Protein: XXXg | Carbs: XXXg | Fats: XXg\n"
            "Fiber: XXg | Water: X liters\n\n"

            "MEAL 1 - BREAKFAST (7:00 AM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 2 - MID MORNING (10:00 AM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 3 - PRE WORKOUT (1 hr before gym)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 4 - POST WORKOUT (30 min after)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 5 - LUNCH (2:00 PM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 6 - SNACK (5:00 PM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 7 - DINNER (8:00 PM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "MEAL 8 - BEFORE BED (10:00 PM)\n"
            "Food items with quantity\n"
            "Cal: XXX | P: XXg | C: XXg | F: XXg\n\n"

            "DAILY TOTAL\n"
            "Cal: XXXX | P: XXXg | C: XXXg | F: XXg\n\n"

            "SUPPLEMENTS\n"
            "Morning: supplement + dose\n"
            "Pre workout: supplement + dose\n"
            "Post workout: supplement + dose\n"
            "Night: supplement + dose\n\n"

            "RULES:\n"
            "- Only Indian foods\n"
            "- Follow: " + restriction + "\n"
            "- Protein min 2g per kg (" + weight + "kg)\n"
            "- Short format like above\n"
            "- Maximum 500 words\n"
            "- No extra explanation\n"
        )

        return self._call_groq(system_prompt, [], user_message)

    # ════════════════════════════════════════════════
    # BMI IMAGE ANALYSIS
    # ════════════════════════════════════════════════

    def _download_image(self, image_url: str) -> bytes:
        try:
            twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
            print("⬇️ Downloading image...")
            response = requests.get(
                image_url,
                auth=(twilio_sid, twilio_token),
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ Image downloaded: {len(response.content)} bytes")
                return response.content
            else:
                print(f"❌ Download failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None

    def analyze_bmi_image(self, image_url: str, phone: str = None) -> str:
        try:
            if not self.gemini_client:
                return "Image analysis unavailable. GEMINI_API_KEY check karo."

            if not self.gemini_model_name:
                return "Gemini model load nahi hua. Server restart karo."

            image_bytes = self._download_image(image_url)
            if not image_bytes:
                return "Photo download nahi ho pa rahi. Dobara bhejo."

            print(f"🔍 Sending to: {self.gemini_model_name}")

            prompt_text = """
You are FitBot, an elite AI gym trainer.

FIRST CHECK: Is this a BMI or body composition report?

If NO (selfie, party photo, random image):
Reply: "Bhai yeh normal photo hai! InBody ya BMI report ki photo bhejo."

If YES (BMI/InBody report), use this EXACT format:

━━━━━━━━━━━━━━━━━━━━━━
BMI REPORT ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━

Weight: X kg
Height: X cm
BMI: X (Category)
Body Fat: X%
Muscle Mass: X kg
Visceral Fat: X
BMR: X kcal
Body Water: X liters

━━━━━━━━━━━━━━━━━━━━━━
HEALTH STATUS
━━━━━━━━━━━━━━━━━━━━━━
[2-3 motivating lines about their numbers]

━━━━━━━━━━━━━━━━━━━━━━
DAILY TARGETS
━━━━━━━━━━━━━━━━━━━━━━
Calories: XXXX kcal
Protein: XXXg | Carbs: XXXg | Fats: XXg
Water: X liters/day

━━━━━━━━━━━━━━━━━━━━━━
7 DAY WORKOUT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━
Day 1: Chest + Triceps
Day 2: Back + Biceps
Day 3: REST + Walk
Day 4: Legs
Day 5: Shoulders + Abs
Day 6: Full Body
Day 7: REST + Stretch

Type W1 for Day 1 detail
Type W2 for Day 2 detail
[and so on]

━━━━━━━━━━━━━━━━━━━━━━
DAILY DIET SUMMARY
━━━━━━━━━━━━━━━━━━━━━━
Breakfast 7am: [meal] | XXX cal
Mid Morning 10am: [meal] | XXX cal
Pre Workout: [meal] | XXX cal
Post Workout: [meal] | XXX cal
Lunch 2pm: [meal] | XXX cal
Snack 5pm: [meal] | XXX cal
Dinner 8pm: [meal] | XXX cal
Before Bed: [meal] | XXX cal
Total: XXXX cal

━━━━━━━━━━━━━━━━━━━━━━
TOP 3 TIPS
━━━━━━━━━━━━━━━━━━━━━━
1. [Specific tip from their data]
2. [Specific tip]
3. [Specific tip]

RULES:
- Simple Hinglish
- No stars no hashtags
- Keep it SHORT and clean
- Use the separator lines shown above
- Calculate from actual report data
- Only Indian foods
"""

            response = self.gemini_client.models.generate_content(
                model=self.gemini_model_name,
                contents=[
                    types.Content(
                        parts=[
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type="image/jpeg",
                                    data=base64.b64encode(
                                        image_bytes
                                    ).decode("utf-8")
                                )
                            ),
                            types.Part(text=prompt_text)
                        ]
                    )
                ]
            )

            if response and response.text:
                print("✅ Gemini analysis complete")
                return (
                    "Analysis ready!\n\n"
                    + response.text.strip()
                    + "\n\nKoi doubt ho toh pooch le! 💪"
                )
            else:
                return self._bmi_fallback()

        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return self._bmi_fallback()

    def _bmi_fallback(self) -> str:
        return (
            "Photo analyze nahi ho pa rahi.\n\n"
            "Manually bata do:\n"
            "Weight (kg)?\n"
            "Height (cm)?\n"
            "BMI value?\n"
            "Body fat %?\n"
            "Goal kya hai?\n\n"
            "Main plan bana dunga! 💪"
        )

    # ════════════════════════════════════════════════
    # FITNESS CHAT
    # ════════════════════════════════════════════════

    def get_fitness_response(
        self, user_data, user_message, conversation_history
    ):
        system_prompt = (
            "You are FitBot, elite AI fitness trainer on WhatsApp.\n"
            "User: " + str(user_data.get("name", "Member")) + "\n"
            "Goal: " + str(user_data.get("goal", "Fitness")) + "\n"
            "Weight: " + str(user_data.get("weight", "N/A")) + " kg\n\n"
            "RULES:\n"
            "1. Max 80 words\n"
            "2. Plain text only\n"
            "3. Fitness topics only\n"
            "4. Motivating and friendly\n"
            "5. Science backed advice\n"
        )
        return self._call_groq(system_prompt, conversation_history, user_message)

    def get_ai_response(self, system_prompt, conversation_history, user_message):
        return self._call_groq(system_prompt, conversation_history, user_message)


ai_service = AIService()