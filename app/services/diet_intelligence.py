# app/services/diet_intelligence.py
# Indian food database, calorie estimation, budget-friendly alternatives

import re


# ── Calorie database (per standard serving) ─────────────────────────────────
INDIAN_FOOD_DB = {
    # ── Grains & breads ──────────────────────────────────────────────────
    "roti":          {"cal": 70,  "protein": 3,  "carbs": 15, "fat": 1,  "serving": "1 roti"},
    "chapati":       {"cal": 70,  "protein": 3,  "carbs": 15, "fat": 1,  "serving": "1 chapati"},
    "paratha":       {"cal": 140, "protein": 4,  "carbs": 20, "fat": 5,  "serving": "1 paratha"},
    "rice":          {"cal": 150, "protein": 3,  "carbs": 33, "fat": 0,  "serving": "1 cup cooked"},
    "brown rice":    {"cal": 130, "protein": 3,  "carbs": 28, "fat": 1,  "serving": "1 cup cooked"},
    "poha":          {"cal": 180, "protein": 4,  "carbs": 35, "fat": 3,  "serving": "1 bowl"},
    "upma":          {"cal": 200, "protein": 5,  "carbs": 36, "fat": 4,  "serving": "1 bowl"},
    "idli":          {"cal": 40,  "protein": 2,  "carbs": 8,  "fat": 0,  "serving": "1 piece"},
    "dosa":          {"cal": 120, "protein": 3,  "carbs": 20, "fat": 3,  "serving": "1 dosa"},
    "uttapam":       {"cal": 150, "protein": 4,  "carbs": 25, "fat": 3,  "serving": "1 piece"},
    "puri":          {"cal": 110, "protein": 2,  "carbs": 14, "fat": 5,  "serving": "1 puri"},
    "bread":         {"cal": 80,  "protein": 3,  "carbs": 15, "fat": 1,  "serving": "2 slices"},
    "oats":          {"cal": 150, "protein": 5,  "carbs": 27, "fat": 3,  "serving": "1 bowl"},
    "cornflakes":    {"cal": 130, "protein": 3,  "carbs": 28, "fat": 1,  "serving": "1 bowl"},
    # ── Pulses & legumes ─────────────────────────────────────────────────
    "dal":           {"cal": 130, "protein": 9,  "carbs": 20, "fat": 1,  "serving": "1 bowl"},
    "rajma":         {"cal": 160, "protein": 10, "carbs": 25, "fat": 1,  "serving": "1 bowl"},
    "chhole":        {"cal": 160, "protein": 9,  "carbs": 27, "fat": 2,  "serving": "1 bowl"},
    "moong dal":     {"cal": 120, "protein": 8,  "carbs": 18, "fat": 1,  "serving": "1 bowl"},
    "sprouts":       {"cal": 100, "protein": 8,  "carbs": 14, "fat": 1,  "serving": "1 cup"},
    "soya chunks":   {"cal": 100, "protein": 18, "carbs": 6,  "fat": 1,  "serving": "50g dry"},
    # ── Dairy ────────────────────────────────────────────────────────────
    "paneer":        {"cal": 165, "protein": 11, "carbs": 3,  "fat": 13, "serving": "100g"},
    "milk":          {"cal": 90,  "protein": 5,  "carbs": 8,  "fat": 4,  "serving": "200ml"},
    "curd":          {"cal": 60,  "protein": 4,  "carbs": 6,  "fat": 2,  "serving": "100g"},
    "lassi":         {"cal": 120, "protein": 5,  "carbs": 15, "fat": 4,  "serving": "1 glass"},
    "chaas":         {"cal": 40,  "protein": 2,  "carbs": 4,  "fat": 1,  "serving": "1 glass"},
    "whey protein":  {"cal": 120, "protein": 25, "carbs": 3,  "fat": 1,  "serving": "1 scoop"},
    "egg":           {"cal": 70,  "protein": 6,  "carbs": 0,  "fat": 5,  "serving": "1 whole"},
    "egg white":     {"cal": 17,  "protein": 4,  "carbs": 0,  "fat": 0,  "serving": "1 white"},
    # ── Non-veg proteins ─────────────────────────────────────────────────
    "chicken breast":{"cal": 165, "protein": 31, "carbs": 0,  "fat": 4,  "serving": "100g"},
    "chicken":       {"cal": 180, "protein": 28, "carbs": 0,  "fat": 7,  "serving": "100g"},
    "fish":          {"cal": 140, "protein": 26, "carbs": 0,  "fat": 4,  "serving": "100g"},
    "tuna":          {"cal": 110, "protein": 25, "carbs": 0,  "fat": 1,  "serving": "100g"},
    "mutton":        {"cal": 220, "protein": 25, "carbs": 0,  "fat": 13, "serving": "100g"},
    # ── Vegetables ───────────────────────────────────────────────────────
    "sabzi":         {"cal": 80,  "protein": 2,  "carbs": 10, "fat": 4,  "serving": "1 bowl"},
    "saag":          {"cal": 80,  "protein": 4,  "carbs": 8,  "fat": 4,  "serving": "1 bowl"},
    "palak":         {"cal": 30,  "protein": 3,  "carbs": 4,  "fat": 0,  "serving": "1 cup"},
    "broccoli":      {"cal": 35,  "protein": 3,  "carbs": 7,  "fat": 0,  "serving": "1 cup"},
    "salad":         {"cal": 40,  "protein": 1,  "carbs": 7,  "fat": 1,  "serving": "1 bowl"},
    # ── Snacks & others ──────────────────────────────────────────────────
    "banana":        {"cal": 90,  "protein": 1,  "carbs": 23, "fat": 0,  "serving": "1 medium"},
    "apple":         {"cal": 70,  "protein": 0,  "carbs": 18, "fat": 0,  "serving": "1 medium"},
    "peanuts":       {"cal": 160, "protein": 7,  "carbs": 6,  "fat": 14, "serving": "30g"},
    "almonds":       {"cal": 160, "protein": 6,  "carbs": 6,  "fat": 14, "serving": "30g"},
    "peanut butter": {"cal": 190, "protein": 8,  "carbs": 7,  "fat": 16, "serving": "2 tbsp"},
    "samosa":        {"cal": 250, "protein": 4,  "carbs": 28, "fat": 13, "serving": "1 piece"},
    "chai":          {"cal": 60,  "protein": 2,  "carbs": 8,  "fat": 2,  "serving": "1 cup"},
    "coffee":        {"cal": 10,  "protein": 0,  "carbs": 2,  "fat": 0,  "serving": "1 cup black"},
}

# ── Budget-friendly alternatives ────────────────────────────────────────────
BUDGET_ALTERNATIVES = {
    "low": {
        "protein": ["dal", "soya chunks", "egg", "egg white", "moong dal", "sprouts"],
        "meal_base": ["roti", "rice", "poha", "upma", "oats"],
        "fat_source": ["peanuts", "peanut butter"],
        "avoid": ["whey protein", "chicken breast", "fish", "paneer (large)"]
    },
    "medium": {
        "protein": ["paneer", "egg", "chicken", "dal", "soya chunks"],
        "meal_base": ["roti", "brown rice", "oats", "poha", "dosa"],
        "fat_source": ["almonds", "curd", "peanut butter"],
        "avoid": []
    },
    "high": {
        "protein": ["chicken breast", "fish", "whey protein", "paneer", "tuna"],
        "meal_base": ["brown rice", "oats", "roti", "sweet potato"],
        "fat_source": ["almonds", "avocado", "olive oil"],
        "avoid": []
    }
}

# ── Region-based meal preferences ───────────────────────────────────────────
REGIONAL_FOODS = {
    "North Indian": {
        "breakfast": ["poha", "paratha", "upma", "roti + curd"],
        "lunch":     ["dal + roti", "rajma chawal", "paneer sabzi + roti"],
        "dinner":    ["dal + roti", "sabzi + roti", "khichdi"],
        "snacks":    ["lassi", "peanuts", "fruit"],
    },
    "South Indian": {
        "breakfast": ["idli + sambar", "dosa", "upma", "uttapam"],
        "lunch":     ["rice + sambar + sabzi", "curd rice", "rasam rice"],
        "dinner":    ["dosa", "idli", "rice + dal"],
        "snacks":    ["chaas", "coconut chutney + idli", "fruit"],
    },
    "East Indian": {
        "breakfast": ["roti + egg", "poha", "rice + dal"],
        "lunch":     ["fish curry + rice", "dal + rice", "rajma rice"],
        "dinner":    ["roti + sabzi", "khichdi", "dal + rice"],
        "snacks":    ["muri (puffed rice)", "banana", "curd"],
    },
    "West Indian": {
        "breakfast": ["thepla", "poha", "upma", "dhokla"],
        "lunch":     ["dal + rice", "roti + sabzi", "khichdi"],
        "dinner":    ["roti + dal", "rice + kadhi", "bajra roti + sabzi"],
        "snacks":    ["chaas", "dhokla", "fruit"],
    },
    "Other": {
        "breakfast": ["oats", "poha", "upma", "roti + egg"],
        "lunch":     ["dal + roti", "rice + sabzi", "salad + protein"],
        "dinner":    ["roti + sabzi", "dal + rice", "soup + bread"],
        "snacks":    ["banana", "peanuts", "curd"],
    }
}


class DietIntelligence:

    def estimate_calories_from_text(self, text: str) -> dict:
        """
        Parse a text description and estimate total calories.
        Returns dict with total_calories, items found, and breakdown.
        """
        text_lower = text.lower()
        total_cal = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        found_items = []

        for food_name, info in INDIAN_FOOD_DB.items():
            # Check number prefix (e.g. "2 roti", "3 eggs")
            pattern = r"(\d+)\s*" + re.escape(food_name)
            match = re.search(pattern, text_lower)
            if match:
                qty = int(match.group(1))
            elif food_name in text_lower:
                qty = 1
            else:
                continue

            cal = info["cal"] * qty
            protein = info["protein"] * qty
            carbs = info["carbs"] * qty
            fat = info["fat"] * qty
            total_cal += cal
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
            found_items.append(
                f"{qty}x {food_name} = {cal} kcal"
            )

        return {
            "total_calories": total_cal,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat,
            "items": found_items
        }

    def format_calorie_estimate(self, text: str) -> str:
        result = self.estimate_calories_from_text(text)
        if not result["items"]:
            return (
                "Food items nahi pehchane. Try karo:\n"
                "\"2 roti, 1 bowl dal, 1 banana\""
            )
        lines = "\n".join(result["items"])
        return (
            "CALORIE ESTIMATE\n\n"
            + lines + "\n\n"
            "Total: " + str(result["total_calories"]) + " kcal\n"
            "Protein: " + str(result["protein"]) + "g | "
            "Carbs: " + str(result["carbs"]) + "g | "
            "Fat: " + str(result["fat"]) + "g"
        )

    def get_meal_suggestion(
        self, goal: str, budget: str, region: str, meal_type: str = "lunch"
    ) -> str:
        """
        Return a simple meal suggestion based on goal, budget, region.
        meal_type: breakfast / lunch / dinner / snacks
        """
        region_key = region if region in REGIONAL_FOODS else "Other"
        budget_key = budget if budget in BUDGET_ALTERNATIVES else "medium"
        region_foods = REGIONAL_FOODS[region_key]

        base_options = region_foods.get(meal_type, region_foods["lunch"])
        protein_options = BUDGET_ALTERNATIVES[budget_key]["protein"]

        suggestions = []
        for item in base_options[:2]:
            suggestions.append(item)

        # Add protein source
        if protein_options:
            suggestions.append(protein_options[0])

        goal_note = ""
        if "fat loss" in goal.lower():
            goal_note = "Portion chhota rakhna. Protein high, carbs low."
        elif "muscle" in goal.lower():
            goal_note = "Protein high rakhna. Post workout zaroor khana."
        elif "maintain" in goal.lower():
            goal_note = "Balanced meal. Calories aur macros track karo."

        result = (
            meal_type.upper() + " SUGGESTION\n\n"
            + "\n".join("• " + s for s in suggestions)
        )
        if goal_note:
            result += "\n\nTip: " + goal_note
        return result

    def get_budget_tip(self, budget: str) -> str:
        tips = {
            "low": (
                "Budget-Friendly Protein Sources:\n"
                "• Dal (cheapest, 9g protein/bowl)\n"
                "• Soya chunks (18g protein/50g — best value!)\n"
                "• Egg whites (4g protein, very cheap)\n"
                "• Sprouts (make at home, free!)\n\n"
                "Save karo supplement pe — pehle food fix karo!"
            ),
            "medium": (
                "Mid Budget Proteins:\n"
                "• Paneer (11g/100g)\n"
                "• Egg (6g each)\n"
                "• Chicken (28g/100g)\n"
                "• Dal + Rice combo (complete amino acids)\n\n"
                "1 whey supplement lena — baaki food se cover karo!"
            ),
            "high": (
                "Premium Protein Sources:\n"
                "• Chicken breast (31g/100g)\n"
                "• Fish / Tuna (25g/100g)\n"
                "• Whey protein (25g/scoop)\n"
                "• Paneer (premium quality)\n\n"
                "High budget = no excuses on nutrition!"
            )
        }
        return tips.get(budget, tips["medium"])


diet_intelligence = DietIntelligence()
