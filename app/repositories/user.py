from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserPair
from typing import Optional, List


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def create_email_context(self, giver_email: str, receiver_email: str) -> dict:
        giver = await self.get_user_by_email(giver_email)
        receiver = await self.get_user_by_email(receiver_email)

        context = {
            "giver_name": giver.name,
            "receiver_name": receiver.name,
            "receiver_wishlist": receiver.wishlist or [],
            "receiver_no_wishlist": receiver.no_wishlist or [],
            "personal_message": "Не забудь добавить индивидуальности в свой подарок!",
        }

        return context


class UserPairRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pair(self, giver_email: str, receiver_email: str) -> UserPair:
        pair = UserPair(giver_id=giver_email, receiver_id=receiver_email)
        self.db.add(pair)
        await self.db.commit()
        await self.db.refresh(pair)
        return pair

    async def get_all_pairs(self) -> List[UserPair]:
        result = await self.db.execute(select(UserPair))
        return result.scalars().all()

    async def get_users_without_gift(self) -> List[User]:
        query = select(User).where(
            ~User.id.in_(select(UserPair.receiver_id)),
        )
        result = await self.db.execute(query)
        return result.scalars().all()
