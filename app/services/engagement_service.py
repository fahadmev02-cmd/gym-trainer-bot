# app/services/engagement_service.py
# Streak tracking, consistency scores, gamification rewards & nudges

import random


class EngagementService:

    # ── Reward messages based on streak ─────────────────────────────────

    _STREAK_REWARDS = {
        1:  "Wah bhai! Pehla step uthaya! Kal bhi aana! 💪",
        3:  "3 din streak! Tu serious ho raha hai. Teri mehnat rang layegi! 🔥",
        5:  "5 din streak! Bhai tu BEAST ban raha hai! 🦁",
        7:  "EK HAFTE POORA! Tu toh legend hai yaar! 🏆",
        10: "10 din! Double digits! Teri consistency dekh ke dil khush hua! 🌟",
        14: "2 HAFTE! Tu professional jogger ban gaya! Coach proud hai! 💎",
        21: "21 din! Ek nayi aadat ban gayi! Habit loop lock ho gaya! 🔐",
        30: "30 DIN STREAK! TU GOD-LEVEL HAI BHAI! Khud ko ek gift de! 🎁",
    }

    _MILESTONE_WORKOUTS = {
        10:  "10 workouts done! Tu serious player hai! 💪",
        25:  "25 workouts! Quarter century! Ekdum top performer! 🥇",
        50:  "50 WORKOUTS! Yaar tu dedicated hai 100%! 🔥🔥",
        100: "100 WORKOUTS! Bhai legend ban gaya tu! Hall of Fame! 🏆🏆",
    }

    # ── Nudge messages for inactivity ────────────────────────────────────

    _NUDGE_MESSAGES = [
        "Aye bhai, kal miss ho gayi gym? Koi nahi — aaj double dose lagao! 💪",
        "Teri muscles teri raah dekh rahi hain yaar... gym yaad aaya? 😅",
        "Bhai sona achi baat hai but gym toh karna padega! Chalo uth! 🚀",
        "Ek din miss karo toh okay, do din nahi! Aaj pakka jayenge gym! 💯",
        "Remember karo kyun shuru kiya tha... goal abhi bhi wohi hai! 🎯",
        "Success wahi paate hain jo roz dikhte hain. TU dikhe aaj! 🦁",
        "Aaj ka workout kal ka confidence hai. Chalo bhai, let's go! ⚡",
    ]

    _SKIP_COACHING = [
        (
            "Bhai ruk! Ek second soch.\n\n"
            "Skip karna easy hai — kal bhi itna hi easy lagega.\n"
            "Aur phir ek hafte baad tujhe guilt aayega.\n\n"
            "Sirf 30 min. Bas. Kar le aaj! 💪\n"
            "Bol de — main aa raha hoon gym! 🔥"
        ),
        (
            "Skip? Seriously bhai? 😅\n\n"
            "Teri body ne teri baat maani thi jab tune shuru kiya tha.\n"
            "Ab teri body teri baat sune — uth aur chal gym!\n\n"
            "Ek baar shuru kar — baad mein thanks dega apne aap ko! 💯"
        ),
        (
            "Aaj thaka hua hai? Sab hote hain bhai.\n\n"
            "Lekin champions wahi hain jo thake hue bhi jaate hain!\n"
            "Aaj light workout kar — 20 minute bhi kaafi hai.\n\n"
            "T type karo — aaj ka quick workout bhejta hoon! ⚡"
        ),
    ]

    # ── Tone detection keywords ──────────────────────────────────────────

    _LAZY_KEYWORDS = [
        "nahi jaaunga", "nahi jaunga", "skip", "kal jaaunga", "kal jaunga",
        "tired", "thaka", "thaki", "bored", "man nahi", "nahi karna",
        "chhod do", "leave it", "rest day", "neend aa rahi", "bahut thaka"
    ]

    _MOTIVATED_KEYWORDS = [
        "aa gaya", "aa gaya gym", "done", "complete", "kar liya",
        "workout kiya", "gym gaya", "gym gayi", "finished", "strong",
        "mazaa aaya", "feel good", "great", "awesome", "beast", "fire"
    ]

    _CONFUSED_KEYWORDS = [
        "kya karna chahiye", "kaise", "samajh nahi", "guide karo",
        "help", "suggest", "bata", "explain", "what should", "which",
        "confused", "doubt", "puchna tha", "poochna tha"
    ]

    def detect_tone(self, message: str) -> str:
        """Returns 'lazy', 'motivated', 'confused', or 'neutral'."""
        msg = message.lower()
        for kw in self._LAZY_KEYWORDS:
            if kw in msg:
                return "lazy"
        for kw in self._MOTIVATED_KEYWORDS:
            if kw in msg:
                return "motivated"
        for kw in self._CONFUSED_KEYWORDS:
            if kw in msg:
                return "confused"
        return "neutral"

    def is_skip_intent(self, message: str) -> bool:
        msg = message.lower()
        skip_phrases = [
            "skip", "nahi jaaunga", "nahi jaunga", "nahi karna aaj",
            "aaj nahi", "miss kar raha", "miss karunga", "rest le raha",
            "aaj rest", "skip today", "skip kar raha"
        ]
        return any(p in msg for p in skip_phrases)

    def is_workout_done(self, message: str) -> bool:
        msg = message.lower()
        done_phrases = [
            "done", "kar liya", "workout kiya", "gym gaya", "gym gayi",
            "completed", "finish", "ho gaya", "kiya aaj", "aaj kiya",
            "workout done", "gym done", "complete", "workout complete"
        ]
        return any(p in msg for p in done_phrases)

    def get_skip_coaching(self) -> str:
        return random.choice(self._SKIP_COACHING)

    def get_streak_reward(
        self, streak: int, total_workouts: int,
        rewarded_milestones: list = None
    ) -> str:
        """
        Return a reward message for streak or workout-count milestones.

        rewarded_milestones: list of already-awarded milestone keys (strings)
        to avoid showing the same reward twice.  Pass user's
        ``rewarded_milestones`` field from MongoDB if available.
        """
        if rewarded_milestones is None:
            rewarded_milestones = []

        reward = None
        reward_key = None

        # Check total workout milestones first (rarer, higher priority)
        for milestone in sorted(self._MILESTONE_WORKOUTS.keys(), reverse=True):
            key = "workout_" + str(milestone)
            if total_workouts >= milestone and key not in rewarded_milestones:
                reward = self._MILESTONE_WORKOUTS[milestone]
                reward_key = key
                break

        # If no workout milestone, check streak milestones
        if reward is None:
            for milestone in sorted(self._STREAK_REWARDS.keys(), reverse=True):
                key = "streak_" + str(milestone)
                if streak >= milestone and key not in rewarded_milestones:
                    reward = self._STREAK_REWARDS[milestone]
                    reward_key = key
                    break

        return reward or "", reward_key

    def get_nudge_message(self, days_inactive: int) -> str:
        return random.choice(self._NUDGE_MESSAGES)

    def get_consistency_label(self, score: int) -> str:
        if score >= 90:
            return "LEGEND 🏆"
        elif score >= 75:
            return "CONSISTENT 🔥"
        elif score >= 50:
            return "DECENT 💪"
        elif score >= 25:
            return "NEEDS WORK ⚠️"
        else:
            return "JUST STARTING 🌱"

    def get_tone_system_hint(self, tone: str) -> str:
        """Extra system hint to inject based on detected tone."""
        if tone == "lazy":
            return (
                "User seems lazy/unmotivated. "
                "Be energetic, persuasive, short. Push them gently. "
                "Use Hinglish. Max 3 sentences."
            )
        elif tone == "motivated":
            return (
                "User is pumped up! Match their energy. "
                "Celebrate with them. Give next action step. "
                "Max 3 sentences. Hinglish."
            )
        elif tone == "confused":
            return (
                "User is confused. Be super clear and simple. "
                "Give ONE clear answer. Numbered steps if needed. "
                "Max 4 sentences."
            )
        return ""


engagement_service = EngagementService()
