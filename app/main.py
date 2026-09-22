from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.features.auth.routes import router as auth_router
from app.features.users.routes import router as user_router

app = FastAPI(
    title="RBAC Project",
    description="Learning FastAPI with PostgreSQL and RBAC",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health check"},
        {"name": "Authentication", "description": "Register, login, logout"},
        {"name": "Users", "description": "User management"},
    ],
)
# CORS configuration
origins = settings.CORS_ORIGINS.split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Required by Authlib to store OAuth state between redirect and callback
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "message": "Service is healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "fastapi-rbac",
        "version": "1.0.0",
    }
