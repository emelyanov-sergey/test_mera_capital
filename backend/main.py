from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from db.db_connetcion import engine, async_session
from derebit_client import get_index_price
from db.db_model import Base
from api.routers import router


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler.add_job(
        get_index_price,
        'interval',
        args=[async_session],
        minutes=1
    )
    scheduler.start()

    yield

    scheduler.shutdown()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(router)
