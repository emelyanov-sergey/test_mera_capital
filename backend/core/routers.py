from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, time

from .db_model import DeribitIndex
from .db_connetcion import get_async_session
from .schema import IndexSchema


router = APIRouter()


@router.get("/all_prices/{ticker}", response_model=List[IndexSchema])
async def get_all_prices_by_ticker(
    ticker: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получение всех сохраненных данных по указанной валюте

    Этот эндпоинт возвращает все записанные цены для заданного тикера:
    BTC или ETH.
    """
    query = await db.execute(
        select(DeribitIndex).filter_by(ticker=ticker.upper())
    )
    results = query.scalars().all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Prices not found for the specified ticker"
        )

    return results


@router.get("/latest-price/{tiker}", response_model=IndexSchema)
async def get_latest_prices(
    ticker: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получение последней цены валюты

    Этот эндпоинт возвращает самую последнюю запись цены для заданного тикера:
    BTC или ETH.
    """
    query = await db.execute(
        select(DeribitIndex)
        .filter_by(ticker=ticker.upper())
        .order_by(DeribitIndex.created_at.desc())
    )
    last_price = query.scalars().first()
    return last_price


@router.get("/prices/{ticker}", response_model=IndexSchema)
async def get_prices_by_ticker(
    ticker: str,
    date: Optional[str] = Query(
        None,
        description="Date in YYYY-MM-DD format"
    ),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Получение цены валюты с фильтром по дате

    Этот эндпоинт возвращает  первую запись цены для заданного тикера:
    BTC или ETH, на указанную дату.
    """
    if date:
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            start_of_day = datetime.combine(date_obj, time(0, 0, 0))
            end_of_day = datetime.combine(date_obj, time(23, 59, 59))
            start_timestamp = int(start_of_day.timestamp())
            end_timestamp = int(end_of_day.timestamp())
            query = await db.execute(
                select(DeribitIndex)
                .filter(
                    DeribitIndex.ticker == ticker.upper(),
                    DeribitIndex.created_at >= start_timestamp,
                    DeribitIndex.created_at <= end_timestamp,
                )
                .order_by(DeribitIndex.created_at)
            )
            result = query.scalars().first()

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start date format. Use YYYY-MM-DD."
            )
    else:
        query = await db.execute(
            select(DeribitIndex)
            .filter_by(ticker=ticker.upper())
            .order_by(DeribitIndex.created_at.desc())
        )
        result = query.scalars().first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Prices not found for the specified ticker and date range"
        )

    return result
