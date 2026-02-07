from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, create_db_and_tables
from .api.ai_agents import router as ai_agents_router
from .api.tasks import router as tasks_router
from .api.auth import router as auth_router
import logging

app = FastAPI(
    title="Cloud-Native AI Todo Platform - Main API",
    description="Main API service for the AI-powered todo platform with advanced features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    try:
        create_db_and_tables()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")

# Include the AI agents router with the correct prefix
app.include_router(ai_agents_router)

# Include other necessary routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Cloud-Native AI Todo Platform Main API"}

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
        "service": "main-api",
        "database": db_status,
        "dependencies": {
            "database": db_status
        }
    }