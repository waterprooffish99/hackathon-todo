from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly allow standard methods
    allow_headers=["*"],  # Allow all headers including authorization
)

# Create database tables on startup
@app.on_event("startup")
async def on_startup():
    import asyncio
    import logging

    max_retries = 15
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            create_db_and_tables()
            logging.info("Database tables created successfully")
            break
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed to connect to database: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logging.warning("Max retries reached. Database may not be ready yet, but continuing startup...")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hackathon Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)