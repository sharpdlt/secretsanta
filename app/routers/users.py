from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserCreate, UserOut
from app.repositories.user import UserRepository
from app.core.db import get_async_session

router = APIRouter()


@router.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    user_data = user.model_dump()
    new_user = await user_repo.create_user(user_data)

    return new_user
