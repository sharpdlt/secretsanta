from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.city import City
from typing import List, Optional

class CityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_city(self, city_data: dict) -> City:
        city = City(**city_data)
        self.db.add(city)
        await self.db.commit()
        await self.db.refresh(city)
        return city

    async def get_city_by_id(self, city_id: int) -> Optional[City]:
        result = await self.db.execute(select(City).where(City.id == city_id))
        return result.scalars().first()

    async def get_all_cities(self) -> List[City]:
        result = await self.db.execute(select(City))
        return result.scalars().all()

    async def update_city(self, city_id: int, city_data: dict) -> Optional[City]:
        city = await self.get_city_by_id(city_id)
        if city:
            for key, value in city_data.items():
                setattr(city, key, value)
            await self.db.commit()
            await self.db.refresh(city)
            return city
        return None

    async def delete_city(self, city_id: int) -> bool:
        city = await self.get_city_by_id(city_id)
        if city:
            await self.db.delete(city)
            await self.db.commit()
            return True
        return False
