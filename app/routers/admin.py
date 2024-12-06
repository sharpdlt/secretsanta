from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository, UserPairRepository
from app.repositories.email import EmailErrorRepository
from app.models.user import UserOut
from app.core.db import get_async_session
from app.core.auth import get_admin_user
from app.utils.mailer import send_pair_email, log_email_error
from app.utils.pairing import generate_pairs
from typing import List, Tuple

router = APIRouter()


@router.get("/admin/dashboard")
def admin_dashboard(current_user: str = Depends(get_admin_user)):
    return {"message": f"Welcome, {current_user}! This is the admin dashboard."}


@router.get("/admin/users/", response_model=List[UserOut])
async def get_all_users(
        db: AsyncSession = Depends(get_async_session),
        admin: bool = Depends(get_admin_user),
):
    if not admin:
        raise HTTPException(status_code=403, detail="Access forbidden")

    user_repo = UserRepository(db)
    users = await user_repo.get_all_users()
    return users


@router.post("/generate_pairs/", response_model=List[Tuple[UserOut, UserOut]])
async def generate_user_pairs(
        db: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(db)
    pair_repo = UserPairRepository(db)

    users = await user_repo.get_all_users()
    if not users:
        raise HTTPException(status_code=400, detail="No users available for pairing")

    pairs, remaining = generate_pairs(users)

    for giver, receiver in pairs:
        await pair_repo.create_pair(giver_email=giver.email, receiver_email=receiver.email)

    return [{"giver": giver, "receiver": receiver} for giver, receiver in pairs]


@router.get("/unpaired_users/", response_model=List[UserOut])
async def get_unpaired_users(
        db: AsyncSession = Depends(get_async_session),
):
    pair_repo = UserPairRepository(db)
    unpaired_users = await pair_repo.get_users_without_gift()
    return unpaired_users


@router.post("/send_emails/")
async def send_emails(
        db: AsyncSession = Depends(get_async_session),
):
    pair_repo = UserPairRepository(db)
    pairs = await pair_repo.get_all_pairs()

    for pair in pairs:
        try:
            await send_pair_email(pair.giver_email, pair.receiver_email)
        except Exception as e:
            await log_email_error(db, pair.giver_email, pair.receiver_email, str(e))

    return {"status": "Emails sent to all pairings"}


@router.get("/email_errors/")
async def get_email_errors(db: AsyncSession = Depends(get_async_session)):
    email_error_repo = EmailErrorRepository(db)
    errors = await email_error_repo.get_all_errors()
    return {"errors": errors}


@router.post("/retry_send_email/{error_id}")
async def retry_send_email(error_id: int, db: AsyncSession = Depends(get_async_session)):
    email_error_repo = EmailErrorRepository(db)
    error = await email_error_repo.get_error(error_id)

    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    try:
        await send_pair_email(error.giver_id, error.receiver_id)
        await email_error_repo.delete_error(error)
        return {"status": "Email resent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resend email: {str(e)}")
