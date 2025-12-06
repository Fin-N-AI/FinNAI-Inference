from pydantic import BaseModel
from typing import Optional


class CompanyRequest(BaseModel):
    company_name: str
    ticker: str


class DataSyncRequest(BaseModel):
    ticker: str


class MarketNewsRequest(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None


class MarketSectorRequest(BaseModel):
    sector_name: str
