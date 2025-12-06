from pydantic import BaseModel
from typing import List, Dict


class CompanyBriefingResponse(BaseModel):
    introduction: str
    bull_points: List[str]
    bear_points: List[str]


class CompanyHighlightResponse(BaseModel):
    highlight_text: str
    sentiment: str


class DataSyncResponse(BaseModel):
    status: str
    message: str
    collected_count: int


class ReportResponse(BaseModel):
    summary: str
    insights: List[str]
    key_metrics: Dict[str, str]
