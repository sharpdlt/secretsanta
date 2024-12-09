from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
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

    async def get_users_by_city(self, city_id: int) -> List[User]:
        result = await self.db.execute(select(User).where(User.city_id == city_id))
        return result.scalars().all()

    async def create_email_context(self, giver_email: str, receiver_email: str) -> dict:
        giver = await self.get_user_by_email(giver_email)
        receiver = await self.get_user_by_email(receiver_email)

        context = {
            "giver_name": giver.full_name,
            "receiver_name": receiver.full_name,
            "receiver_wishlist": receiver.wishlist or [],
            "receiver_no_wishlist": receiver.no_wishlist or [],
            "personal_message": "Не забудь добавить индивидуальности в свой подарок!",
        }

        return context


class UserPairRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pair(self, giver_email: str, receiver_email: str) -> UserPair:
        giver = await self.db.execute(select(User).where(User.email == giver_email))
        receiver = await self.db.execute(select(User).where(User.email == receiver_email))

        giver = giver.scalars().first()
        receiver = receiver.scalars().first()

        if giver.city_id != receiver.city_id:
            raise ValueError("Users must be from the same city to exchange gifts.")

        pair = UserPair(giver_id=giver.id, receiver_id=receiver.id)
        self.db.add(pair)
        await self.db.commit()
        await self.db.refresh(pair)
        return pair

    async def get_all_pairs(self) -> List[UserPair]:
        result = await self.db.execute(select(UserPair))
        return result.scalars().all()

    async def get_users_without_gift(self) -> List[User]:
        pair_alias = aliased(UserPair)

        result = await self.db.execute(
            select(User)
            .outerjoin(pair_alias, (User.id == pair_alias.giver_id) | (User.id == pair_alias.receiver_id))
            .filter(pair_alias.id == None)
        )
        return result.scalars().all()

    async def get_pair_by_user_ids(self, giver_id: int, receiver_id: int) -> Optional[UserPair]:
        result = await self.db.execute(
            select(UserPair)
            .where((UserPair.giver_id == giver_id) & (UserPair.receiver_id == receiver_id))
        )
        return result.scalars().first()

    async def get_users_in_pair(self, pair_id: int) -> Optional[List[User]]:
        result = await self.db.execute(
            select(User)
            .join(UserPair, (User.id == UserPair.giver_id) | (User.id == UserPair.receiver_id))
            .where(UserPair.id == pair_id)
        )
        return result.scalars().all()
