import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.smtp import process_email_queue
from app.routers.users import router as users_router
from app.routers.admin import router as admin_router
from app.core.config import settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    email_task = asyncio.create_task(start_email_queue())

    try:
        yield
    finally:
        email_task.cancel()
        try:
            await email_task
        except asyncio.CancelledError:
            print("Фоновая задача корректно завершена.")


async def start_email_queue():
    print("Запуск фоновой обработки email-очереди.")
    while True:
        try:
            await process_email_queue()
        except Exception as e:
            print(f"Ошибка в email-очереди: {e}")
            await asyncio.sleep(5)


print("Инициализация FastAPI...")
app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/api", tags=["Users"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
