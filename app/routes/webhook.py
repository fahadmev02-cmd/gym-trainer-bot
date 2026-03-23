# app/routes/webhook.py
from fastapi import APIRouter
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import Response
from app.utils.conversation_manager import conversation_manager
from app.services.whatsapp_service import whatsapp_service
from app.config import config
import hmac
import hashlib

router = APIRouter()


def verify_twilio_signature(request: Request):
    """
    Security: Verify that the request actually came from Twilio.
    This prevents fake requests to your webhook.
    """
    # For development, you can skip this check
    # For production, implement proper Twilio signature verification
    pass


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),        # Sender's WhatsApp number
    Body: str = Form(...),        # Message text
    MessageSid: str = Form(None)  # Message ID from Twilio
):
    """
    This is the main webhook endpoint.
    Twilio calls this URL every time someone sends a message to your WhatsApp number.
    
    FastAPI automatically parses the form data that Twilio sends.
    """
    try:
        print(f"\n📨 Incoming message from {From}: {Body}")
        
        # Clean up the sender's phone number
        # Twilio sends it as "whatsapp:+919876543210"
        # We extract just "+919876543210"
        sender_phone = From.replace("whatsapp:", "").strip()
        
        # Process the message and get response
        response_text = conversation_manager.process_message(
            phone=sender_phone,
            message=Body
        )
        
        # Send the response via WhatsApp
        if response_text:
            whatsapp_service.send_message(From, response_text)
        
        # Twilio expects an empty 200 response
        return Response(content="", status_code=200)
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        # Still return 200 to prevent Twilio from retrying
        return Response(content="", status_code=200)


@router.get("/webhook")
async def webhook_health_check():
    """
    Health check endpoint - useful to verify the server is running.
    """
    return {
        "status": "running",
        "message": "WhatsApp AI Gym Trainer is active! 💪"
    }