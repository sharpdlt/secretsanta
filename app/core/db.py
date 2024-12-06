import pika
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings

async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True, future=True)


async def get_async_session() -> AsyncSession:
    async_session_maker = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session


def connect_to_rabbitmq():
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URI))
    channel = connection.channel()
    return connection, channel


