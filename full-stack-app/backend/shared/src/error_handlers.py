from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

# Set up logger
logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions globally."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation exceptions."""
    logger.error(f"Validation Exception: {str(exc)}")

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "ValidationError",
                "message": str(exc),
                "status_code": 422
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"General Exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "status_code": 500
            }
        }
    )

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    # Add other exception handlers as needed