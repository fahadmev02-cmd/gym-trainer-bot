# app/services/ai_service.py
# Using Groq API - 100% FREE

import requests
import os
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"

        if self.api_key:
            print("✅ AI service initialized - Groq API Ready")
        else:
            print("❌ AI service - GROQ_API_KEY not found in .env file")

    def _call_groq(self, system_prompt, conversation_history, user_message):
        try:
            if not self.api_key:
                return "AI service not configured."

            messages = [{"role": "system", "content": system_prompt}]

            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            messages.append({"role": "user", "content": user_message})

            headers = {
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                print("✅ Groq response received")
                return ai_response

            elif response.status_code == 429:
                print("⚠️ Groq rate limit hit")
                return "I am a bit busy right now. Please try again in a moment."

            elif response.status_code == 401:
                print("❌ Groq API key is invalid")
                return "AI service configuration error."

            else:
                print("❌ Groq error status:", response.status_code)
                return "I am having a technical issue. Please try again."

        except requests.exceptions.Timeout:
            print("❌ Groq request timed out")
            return "Response took too long. Please try again."

        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Groq API")
            return "Cannot connect to AI service. Please try again."

        except Exception as e:
            print("❌ Groq unexpected error:", e)
            return "I am having a technical issue. Please try again."

    def generate_workout_plan(self, user_data):
        system_prompt = (
            "You are an expert certified personal trainer. "
            "Create clear and practical workout plans. "
            "Plain text only, no markdown symbols."
        )

        user_message = (
            "Create a weekly workout plan for:\n"
            "Name: " + str(user_data.get("name", "User")) + "\n"
            "Age: " + str(user_data.get("age", "25")) + " years\n"
            "Weight: " + str(user_data.get("weight", "70")) + " kg\n"
            "Height: " + str(user_data.get("height", "170")) + " cm\n"
            "Goal: " + str(user_data.get("goal", "Fitness")) + "\n"
            "Workout Days: " + str(user_data.get("workout_days", "4")) + " per week\n\n"
            "Format like this:\n"
            "DAY 1 - CHEST\n"
            "Bench Press: 4 sets x 10 reps\n"
            "Incline Press: 3 sets x 12 reps\n\n"
            "DAY 2 - REST\n\n"
            "Rules:\n"
            "- Exactly " + str(user_data.get("workout_days", "4")) + " workout days\n"
            "- Match to goal: " + str(user_data.get("goal", "Fitness")) + "\n"
            "- Include rest days\n"
            "- No extra explanation\n"
        )

        print("Generating workout plan...")
        result = self._call_groq(system_prompt, [], user_message)
        print("Workout plan generated")
        return result

    def generate_diet_plan(self, user_data):
        diet_type = str(user_data.get("diet_preference", "Veg"))
        meals = str(user_data.get("meals_per_day", "4"))

        if diet_type.lower() == "veg":
            diet_restriction = "STRICTLY VEGETARIAN - no meat, chicken, fish, or eggs"
        else:
            diet_restriction = "Non-vegetarian - can include chicken, eggs, fish"

        system_prompt = (
            "You are an expert Indian nutritionist. "
            "Create practical Indian meal plans. "
            "Plain text only, no markdown symbols."
        )

        user_message = (
            "Create a daily Indian diet plan for:\n"
            "Name: " + str(user_data.get("name", "User")) + "\n"
            "Weight: " + str(user_data.get("weight", "70")) + " kg\n"
            "Height: " + str(user_data.get("height", "170")) + " cm\n"
            "Goal: " + str(user_data.get("goal", "Fitness")) + "\n"
            "Diet: " + diet_type + "\n"
            "Rule: " + diet_restriction + "\n"
            "Meals per day: " + meals + "\n\n"
            "Format like this:\n"
            "BREAKFAST - 400 cal\n"
            "Oats with milk: 1 bowl\n"
            "Banana: 1\n\n"
            "LUNCH - 600 cal\n"
            "Dal: 1 bowl\n"
            "Roti: 2\n"
            "Sabzi: 1 bowl\n\n"
            "TOTAL: 2000 cal\n\n"
            "Rules:\n"
            "- Only Indian foods\n"
            "- Follow strictly: " + diet_restriction + "\n"
            "- Exactly " + meals + " meals\n"
            "- Include calories\n"
            "- No extra explanation\n"
        )

        print("Generating diet plan...")
        result = self._call_groq(system_prompt, [], user_message)
        print("Diet plan generated")
        return result

    def get_fitness_response(self, user_data, user_message, conversation_history):
        system_prompt = (
            "You are FitBot, an AI fitness trainer on WhatsApp.\n"
            "Chatting with " + str(user_data.get("name", "a gym member")) + ".\n\n"
            "Their Profile:\n"
            "Age: " + str(user_data.get("age", "N/A")) + "\n"
            "Weight: " + str(user_data.get("weight", "N/A")) + " kg\n"
            "Goal: " + str(user_data.get("goal", "N/A")) + "\n"
            "Diet: " + str(user_data.get("diet_preference", "N/A")) + "\n"
            "Gym Time: " + str(user_data.get("gym_time", "N/A")) + "\n\n"
            "STRICT RULES:\n"
            "1. Maximum 100 words per response - very important\n"
            "2. Plain text only - no stars, no dashes, no hashtags\n"
            "3. For fitness questions give helpful answers\n"
            "4. For non fitness topics redirect politely\n"
            "5. Be motivating and friendly\n"
            "6. Their goal is " + str(user_data.get("goal", "fitness")) + "\n"
        )

        return self._call_groq(system_prompt, conversation_history, user_message)

    def get_ai_response(self, system_prompt, conversation_history, user_message):
        return self._call_groq(system_prompt, conversation_history, user_message)


ai_service = AIService()