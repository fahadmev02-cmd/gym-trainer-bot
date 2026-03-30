# app/routes/webhook.py
from fastapi import APIRouter, Request, Form, Response
from typing import Optional
from app.utils.conversation_manager import conversation_manager
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(default=""),
    MessageSid: str = Form(None),
    NumMedia: str = Form(default="0"),        # ✅ How many photos sent
    MediaUrl0: Optional[str] = Form(None),    # ✅ Photo URL if sent
    MediaContentType0: Optional[str] = Form(None)  # ✅ image/jpeg etc
):
    """
    Main webhook endpoint.
    Now handles both text messages AND photos.
    """
    try:
        print(f"\n📨 Message from {From}")
        print(f"📝 Text: {Body}")
        print(f"📸 Media count: {NumMedia}")

        # Clean phone number
        sender_phone = From.replace("whatsapp:", "").strip()

        # ✅ Check if user sent a photo
        num_media = int(NumMedia) if NumMedia else 0

        if num_media > 0 and MediaUrl0:
            # ─────────────────────────────────────
            # USER SENT A PHOTO
            # ─────────────────────────────────────
            print(f"📸 Photo received: {MediaUrl0}")
            print(f"📸 Type: {MediaContentType0}")

            # Check if it's actually an image
            if MediaContentType0 and "image" in MediaContentType0:
                print("✅ Valid image received - sending for analysis")

                # Send "analyzing" message to user first
                whatsapp_service.send_message(
                    From,
                    "📸 Photo mil gaya! Analyze kar raha hoon... thoda wait karo 🔍"
                )

                # Analyze the BMI report image
                response_text = ai_service.analyze_bmi_image(
                    image_url=MediaUrl0,
                    phone=sender_phone
                )

            else:
                response_text = (
                    "Yeh file support nahi hai. "
                    "Please apni BMI report ki clear photo bhejo 📸"
                )

        else:
            # ─────────────────────────────────────
            # USER SENT TEXT MESSAGE (Normal flow)
            # ─────────────────────────────────────
            if not Body or not Body.strip():
                response_text = "Kuch message bhi bhejo bhai 😄"
            else:
                response_text = conversation_manager.process_message(
                    phone=sender_phone,
                    message=Body
                )

        # Send response
        if response_text:
            whatsapp_service.send_message(From, response_text)

        # Twilio expects empty 200 response
        return Response(content="", status_code=200)

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return Response(content="", status_code=200)


@router.get("/webhook")
async def webhook_health_check():
    return {
        "status": "running",
        "message": "WhatsApp AI Gym Trainer is active! 💪"
    }