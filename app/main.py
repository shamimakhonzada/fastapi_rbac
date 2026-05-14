from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.features.auth.routes import router as auth_router
from app.features.users.routes import router as user_router

app = FastAPI(
    title="RBAC Project",
    description="Learning FastAPI with PostgreSQL and RBAC",
    version="1.0.0",
)
# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
]

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


@app.get("/")
async def root():
    return {"message": "Hello Shamim!"}
