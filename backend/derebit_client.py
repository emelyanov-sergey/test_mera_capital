import aiohttp
import asyncio
import ssl
import certifi
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Dict

from db.db_model import DeribitIndex
from core.logger import logger


async def fetch_single_index(
        session: aiohttp.ClientSession, index_name: str
) -> Dict:
    """Получение данных для одного индекса"""
    get_index_price_url = (
        "https://test.deribit.com/api/v2/public/get_index_price"
    )
    try:
        async with session.get(
            f"{get_index_price_url}?index_name={index_name}"
        ) as response:
            r = await response.json()
            price = str(r['result']['index_price'])
            ticker = 'BTC' if index_name == "btc_usd" else 'ETH'
            return {
                'price': price,
                'ticker': ticker,
                'success': True
            }
    except Exception as e:
        logger.error(f"Error fetching {index_name}: {str(e)}")
        return {
            'ticker': 'BTC' if index_name == "btc_usd" else 'ETH',
            'success': False,
            'error': str(e)
        }


async def save_all_to_db(async_session: AsyncSession, data_list: List[Dict]):
    """Сохранение всех данных за одну транзакцию"""
    current_timestamp = int(datetime.utcnow().timestamp())
    objects_to_save = []

    for data in data_list:
        if data['success']:
            index_object = DeribitIndex(
                price=data['price'],
                ticker=data['ticker'],
                created_at=current_timestamp
            )
            objects_to_save.append(index_object)

    if not objects_to_save:
        logger.warning("No valid data to save")
        return

    try:
        async with async_session() as session:
            async with session.begin():
                session.add_all(objects_to_save)
                await session.commit()

                for obj in objects_to_save:
                    logger.info(
                        f"Successfully saved {obj.ticker} price: {obj.price}"
                    )

    except Exception as e:
        logger.error(f"Error saving batch to database: {str(e)}")
        raise


async def get_index_price(async_session: AsyncSession):
    """Основная функция получения и сохранения данных"""
    index_names = ["btc_usd", "eth_usd"]

    # Настройка SSL
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        fetch_tasks = [
            fetch_single_index(session, index_name)
            for index_name in index_names
        ]
        results = await asyncio.gather(*fetch_tasks)

        await save_all_to_db(async_session, results)
