from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}" \
               f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
