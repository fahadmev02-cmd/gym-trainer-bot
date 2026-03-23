# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title="WhatsApp AI Gym Trainer",
    description="AI-powered fitness assistant on WhatsApp",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routes AFTER app is created
from app.routes.webhook import router as webhook_router
app.include_router(
    webhook_router, 
    prefix="/api/v1", 
    tags=["WhatsApp Webhook"]
)


@app.on_event("startup")
async def startup_event():
    print("\n🚀 WhatsApp AI Gym Trainer Starting...")
    print("=" * 50)
    print("✅ FastAPI server is running")
    print("✅ Ready to receive WhatsApp messages!")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    print("\n👋 Server shutting down gracefully...")


@app.get("/")
async def root():
    return {
        "message": "WhatsApp AI Gym Trainer API",
        "status": "running",
        "version": "1.0.0",
        "webhook_url": "/api/v1/webhook"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "gym-trainer-bot"
    }