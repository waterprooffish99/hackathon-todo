from fastapi import FastAPI
import os

app = FastAPI(
    title="Cloud-Native AI Todo Platform - Notification Service",
    description="Service that consumes reminder events to send user notifications",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Notification Service"}

@app.get("/health")
async def health_check():
    # Check service-specific health indicators
    return {
        "status": "healthy",
        "service": "notification-service",
        "dependencies": {
            "kafka": "connected",  # Placeholder - would check actual Kafka connection
            "dapr": "connected"    # Placeholder - would check actual Dapr connection
        }
    }