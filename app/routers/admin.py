from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository, UserPairRepository
from app.repositories.city import CityRepository
from app.repositories.email import EmailErrorRepository
from app.models.user import UserOut
from app.models.city import CityOut, CityCreate
from app.core.db import get_async_session
from .auth import get_current_user
from app.utils.mailer import send_pair_email
from app.utils.pairing import generate_pairs_for_all_cities
from typing import List, Tuple

router = APIRouter()


@router.get("/admin/dashboard")
def admin_dashboard(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user}! This is the admin dashboard."}


@router.get("/admin/users/", response_model=List[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_async_session), current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    user_repo = UserRepository(db)
    users = await user_repo.get_all_users()
    return users


@router.post("/admin/generate_pairs/", response_model=List[Tuple[UserOut, UserOut]])
async def generate_user_pairs(db: AsyncSession = Depends(get_async_session),
                              current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    user_repo = UserRepository(db)
    user_pair_repo = UserPairRepository(db)
    city_repo = CityRepository(db)

    cities = await city_repo.get_all_cities()
    if not cities:
        raise HTTPException(status_code=400, detail="No cities available")

    city_users = {}
    for city in cities:
        users = await user_repo.get_users_by_city(city.id)
        city_users[city.name] = users

    city_pairs = generate_pairs_for_all_cities(city_users)

    for city_name, pairs_info in city_pairs.items():
        for pair in pairs_info["pairs"]:
            giver = pair[0]
            receiver = pair[1]

            try:
                await user_pair_repo.create_pair(giver.email, receiver.email)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

    return city_pairs


@router.get("/admin/unpaired_users/", response_model=List[UserOut])
async def get_unpaired_users(db: AsyncSession = Depends(get_async_session),
                             current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    pair_repo = UserPairRepository(db)
    unpaired_users = await pair_repo.get_users_without_gift()
    return unpaired_users


@router.post("/admin/send_emails/")
async def send_emails(db: AsyncSession = Depends(get_async_session), current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    pair_repo = UserPairRepository(db)
    pairs = await pair_repo.get_all_pairs()
    email_error_repo = EmailErrorRepository(db)

    for pair in pairs:
        try:
            await send_pair_email(pair.giver_email, pair.receiver_email)
        except Exception as e:
            await email_error_repo.save_error(pair.giver_email, pair.receiver_email, str(e))

    return {"status": "Emails sent to all pairings"}


@router.get("/admin/email_errors/")
async def get_email_errors(db: AsyncSession = Depends(get_async_session),
                           current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    email_error_repo = EmailErrorRepository(db)
    errors = await email_error_repo.get_all_errors()
    return {"errors": errors}


@router.post("/admin/retry_send_email/{error_id}")
async def retry_send_email(error_id: int, db: AsyncSession = Depends(get_async_session),
                           current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

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


@router.get("/admin/cities/{city_id}", response_model=CityOut)
async def get_city_by_id(city_id: int, db: AsyncSession = Depends(get_async_session),
                         current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    city_repo = CityRepository(db)
    city = await city_repo.get_city_by_id(city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.post("/admin/cities/", response_model=CityOut)
async def create_city(city: CityCreate, db: AsyncSession = Depends(get_async_session),
                      current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    city_repo = CityRepository(db)
    city_data = city.model_dump()
    city = await city_repo.create_city(city_data)
    return city


@router.put("/admin/cities/{city_id}", response_model=CityOut)
async def update_city(city_id: int, city_data: dict, db: AsyncSession = Depends(get_async_session),
                      current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    city_repo = CityRepository(db)
    city = await city_repo.update_city(city_id, city_data)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city
