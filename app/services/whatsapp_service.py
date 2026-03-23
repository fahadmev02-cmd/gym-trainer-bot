# app/services/whatsapp_service.py

from twilio.rest import Client
import os
import time
from dotenv import load_dotenv

load_dotenv()


class WhatsAppService:
    def __init__(self):
        try:
            self.client = Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.from_number = os.getenv(
                "TWILIO_WHATSAPP_NUMBER",
                "whatsapp:+14155238886"
            )
            self.max_length = 1400
            print("✅ WhatsApp service initialized")
        except Exception as e:
            print("❌ WhatsApp service failed:", e)
            self.client = None
            self.from_number = None

    def split_message(self, message: str) -> list:
        """
        Split long messages into chunks under 1400 characters.
        """
        # If short enough return as is
        if len(message) <= self.max_length:
            return [message]

        parts = []
        lines = message.split("\n")
        current_part = ""

        for line in lines:
            # Check if adding this line would exceed limit
            test = current_part + line + "\n"

            if len(test) > self.max_length:
                # Save current part if not empty
                if current_part.strip():
                    parts.append(current_part.strip())
                # Start fresh with current line
                current_part = line + "\n"
            else:
                current_part = test

        # Add remaining content
        if current_part.strip():
            parts.append(current_part.strip())

        return parts

    def send_message(self, to_phone: str, message: str) -> bool:
        """
        Send WhatsApp message.
        Automatically splits long messages.
        """
        try:
            if not self.client:
                print("❌ Twilio client not initialized")
                return False

            # Add whatsapp: prefix if missing
            if not to_phone.startswith("whatsapp:"):
                to_phone = "whatsapp:" + to_phone

            # Split into parts
            parts = self.split_message(message)
            total = len(parts)

            print("📤 Sending", total, "part(s) to", to_phone)

            for i, part in enumerate(parts):
                # Double check each part length
                if len(part) > 1400:
                    # Force split at 1400 chars
                    part = part[:1400]

                try:
                    msg = self.client.messages.create(
                        from_=self.from_number,
                        body=part,
                        to=to_phone
                    )
                    print("✅ Part", i + 1, "of", total, "sent - SID:", msg.sid)

                    # Small delay between parts
                    if i < total - 1:
                        time.sleep(1.5)

                except Exception as e:
                    print("❌ Failed to send part", i + 1, ":", e)
                    return False

            return True

        except Exception as e:
            print("❌ send_message error:", e)
            return False

    def send_reminder(self, phone: str, reminder_text: str) -> bool:
        """
        Send reminder message.
        """
        return self.send_message("whatsapp:" + phone, reminder_text)


whatsapp_service = WhatsAppService()