from fastapi import FastAPI
import os

app = FastAPI(
    title="Cloud-Native AI Todo Platform - Recurring Task Service",
    description="Service that consumes task completion events to create next occurrences for recurring tasks",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Recurring Task Service"}

@app.get("/health")
async def health_check():
    # Check service-specific health indicators
    return {
        "status": "healthy",
        "service": "recurring-task-service",
        "dependencies": {
            "kafka": "connected",  # Placeholder - would check actual Kafka connection
            "dapr": "connected"    # Placeholder - would check actual Dapr connection
        }
    }