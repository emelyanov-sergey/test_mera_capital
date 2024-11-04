import aiohttp
import ssl
import certifi
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from core.db_model import DeribitIndex
from core.logger import logger


async def get_index_price(async_session: AsyncSession):
    index_names = [
        "btc_usd",
        "eth_usd",
    ]
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    get_index_price_url = "https://test.deribit.com/api/v2/public/" \
                          "get_index_price?index_name="
    async with aiohttp.ClientSession(connector=conn) as session:
        for i in index_names:
            try:
                async with session.get(
                    get_index_price_url + str(i)
                ) as response:

                    r = await response.json()
                    price = str(r['result']['index_price'])
                    ticker = 'BTC' if i == "btc_usd" else 'ETH'

                    object = DeribitIndex(
                        price=price,
                        ticker=ticker,
                        created_at=int(datetime.utcnow().timestamp())
                    )

                    async with async_session() as db_session:
                        async with db_session.begin():
                            db_session.add(object)
                            await db_session.commit()
                            await db_session.flush()
                            logger.info(
                                f"Successfully saved {ticker} price: {price}"
                            )
            except Exception as e:
                logger.error(f"Error fetching {i}: {str(e)}")
