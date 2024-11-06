from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, time

from db.db_model import DeribitIndex
from db.db_connetcion import get_async_session
from .schema import IndexSchema


router = APIRouter()


async def get_ticker_data(db: AsyncSession, query):
    """Общая функция для выполнения запросов к БД"""
    result = await db.execute(query)
    return result.scalars()


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
    query = select(DeribitIndex).filter_by(ticker=ticker.upper())
    result = await get_ticker_data(db, query)
    all_results = result.all()

    if not all_results:
        raise HTTPException(
            status_code=404,
            detail="Prices not found for the specified ticker"
        )

    return all_results


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
    query = (
        select(DeribitIndex)
        .filter_by(ticker=ticker.upper())
        .order_by(DeribitIndex.created_at.desc())
    )
    results = await get_ticker_data(db, query)
    last_price = results.first()

    if not last_price:
        raise HTTPException(
            status_code=404,
            detail="Latest price not found for the specified ticker"
        )

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

            query = (
                select(DeribitIndex)
                .filter(
                    DeribitIndex.ticker == ticker.upper(),
                    DeribitIndex.created_at >= start_timestamp,
                    DeribitIndex.created_at <= end_timestamp,
                )
                .order_by(DeribitIndex.created_at)
            )
            results = await get_ticker_data(db, query)
            result = results.first()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start date format. Use YYYY-MM-DD."
            )

    else:
        query = (
            select(DeribitIndex)
            .filter_by(ticker=ticker.upper())
            .order_by(DeribitIndex.created_at.desc())
        )
        results = await get_ticker_data(db, query)
        result = results.first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Prices not found for the specified ticker and date range"
        )

    return result
