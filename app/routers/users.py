from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserCreate, UserOut
from app.models.city import CityOut
from app.repositories.user import UserRepository
from app.repositories.city import CityRepository
from app.repositories.email import EmailErrorRepository
from app.core.db import get_async_session
from app.core.config import settings
from app.utils.render_email_template import render_email_template
from app.utils.mailer import send_email
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    user_repo = UserRepository(db)
    email_error_repo = EmailErrorRepository(db)

    existing_user = await user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    user_data = user.model_dump()
    new_user = await user_repo.create_user(user_data)

    context = {
        "name": new_user.full_name,
    }
    try:
        body_html = render_email_template("welcome_email.html", context)
    except Exception as e:
        logging.error(f"Template rendering failed: {str(e)}")
        async with get_async_session() as db:
            await email_error_repo.save_error(
                giver_email=settings.SMTP_USER,
                receiver_email=new_user.email,
                error_message=f"Template rendering failed: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to render email template.",
        )

    try:
        await send_email(
            giver_email=settings.SMTP_USER,
            receiver_email=new_user.email,
            subject="Welcome to Secret Santa",
            body_html=body_html,
        )
    except HTTPException as e:
        await email_error_repo.save_error(
            giver_email=settings.SMTP_USER,
            receiver_email=new_user.email,
            error_message=f"Failed to send email: {str(e.detail)}"
        )
        raise e

    return new_user


@router.get("/cities/", response_model=List[CityOut])
async def get_all_cities(db: AsyncSession = Depends(get_async_session)):
    city_repo = CityRepository(db)
    cities = await city_repo.get_all_cities()
    return cities
