"""
Security headers and CORS configuration for the API.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.security import SecurityMiddleware
from starlette.types import ASGIApp
from typing import List


def add_security_headers(app: FastAPI):
    """
    Add security headers to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add Security Middleware
    app.add_middleware(
        SecurityMiddleware,
        content_security_policy="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;",
        referrer_policy="strict-origin-when-cross-origin",
        permissions_policy="geolocation=(self), microphone=(), camera=()",
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,
        strict_transport_security_preload=True,
    )


def configure_cors(
    app: FastAPI,
    allowed_origins: List[str] = None,
    allowed_methods: List[str] = None,
    allowed_headers: List[str] = None,
    allow_credentials: bool = True
):
    """
    Configure CORS middleware for the application.

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins
        allowed_methods: List of allowed methods
        allowed_headers: List of allowed headers
        allow_credentials: Whether to allow credentials
    """
    if allowed_origins is None:
        # In production, you should specify exact origins
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8080",
            "https://todo-platform.example.com",
            "https://*.todo-platform.example.com"
        ]

    if allowed_methods is None:
        allowed_methods = ["*"]

    if allowed_headers is None:
        allowed_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Methods",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        # Expose headers that clients can read
        expose_headers=[
            "Access-Control-Allow-Origin",
            "Access-Control-Expose-Headers",
            "Content-Disposition"  # For file downloads
        ]
    )


def add_custom_security_headers():
    """
    Factory function to create a middleware that adds custom security headers.
    """
    def security_headers_middleware(app: ASGIApp):
        async def middleware(scope, receive, send):
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    # Add security headers to the response
                    headers = message.get("headers", [])

                    # Add security headers
                    security_headers = [
                        (b"X-Content-Type-Options", b"nosniff"),
                        (b"X-Frame-Options", b"SAMEORIGIN"),
                        (b"X-XSS-Protection", b"1; mode=block"),
                        (b"Strict-Transport-Security", b"max-age=31536000; includeSubDomains; preload"),
                        (b"Referrer-Policy", b"strict-origin-when-cross-origin"),
                        (b"Permissions-Policy", b"geolocation=(), microphone=(), camera=()"),
                    ]

                    # Add headers that don't already exist
                    for header_name, header_value in security_headers:
                        if not any(h[0] == header_name for h in headers):
                            headers.append((header_name, header_value))

                    message["headers"] = headers

                await send(message)

            await app(scope, receive, send_wrapper)

        return middleware

    return add_custom_security_headers