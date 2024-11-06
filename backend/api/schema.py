from pydantic import BaseModel


class IndexSchema(BaseModel):
    ticker: str
    price: float
    created_at: int
