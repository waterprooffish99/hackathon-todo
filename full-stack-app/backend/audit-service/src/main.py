from fastapi import FastAPI
import os
from ..shared.src.database import engine

app = FastAPI(
    title="Cloud-Native AI Todo Platform - Audit Service",
    description="Service that consumes all task events for immutable logging and compliance",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Audit Service"}

@app.get("/health")
async def health_check():
    # Check database connectivity
    try:
        with engine.connect() as conn:
            pass
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "service": "audit-service",
        "database": db_status,
        "dependencies": {
            "database": db_status,
            "kafka": "connected",  # Placeholder - would check actual Kafka connection
            "dapr": "connected"    # Placeholder - would check actual Dapr connection
        }
    }