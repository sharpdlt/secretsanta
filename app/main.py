from fastapi import FastAPI
from .routers.users import router as users_router
from .routers.admin import router as admin_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secret Santa App"
)

app.include_router(users_router, prefix="/api", tags=["Users"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])