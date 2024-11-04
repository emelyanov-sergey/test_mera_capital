from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DeribitIndex(Base):
    __tablename__ = 'deribit_index'

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    created_at = Column(Integer, nullable=False)


async def insert_object(async_session, object):
    async with async_session() as session:
        async with session.begin():
            session.add(object)
