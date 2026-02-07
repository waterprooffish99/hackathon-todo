from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import from the src package
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
from src.api.ai_agents import router as ai_router
from src.db.database import create_db_and_tables

app = FastAPI(title="Hackathon Todo API", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],  # Allow specific local development origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Explicitly allow standard methods including PATCH
    allow_headers=["*"],  # Allow all headers including authorization
)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    import logging

    try:
        create_db_and_tables()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        # Continue anyway since this might be a temporary issue

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(ai_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hackathon Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)