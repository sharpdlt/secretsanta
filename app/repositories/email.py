from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.email import EmailError


class EmailErrorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_errors(self):
        result = await self.db.execute(select(EmailError))
        return result.scalars().all()

    async def get_error(self, error_id: int):
        return await self.db.get(EmailError, error_id)

    async def delete_error(self, error: EmailError):
        await self.db.delete(error)
        await self.db.commit()

    async def save_error(self, giver_email: str, receiver_email: str, error_message: str):
        email_error = EmailError(
            giver_email=giver_email,
            receiver_email=receiver_email,
            error_message=error_message
        )
        self.db.add(email_error)
        await self.db.commit()
