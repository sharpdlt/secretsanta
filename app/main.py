from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.users import router as users_router
from .routers.admin import router as admin_router
from .routers.auth import router as auth_router

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secret Santa App"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8081"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router, prefix="/api", tags=["Users"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(auth_router, prefix="/api", tags=["Login"])
