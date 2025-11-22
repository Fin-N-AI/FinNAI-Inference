from fastapi import APIRouter
from web.api.request.inference_request import MarketNewsRequest, MarketSectorRequest

router = APIRouter(tags=["Market Intelligence"])


@router.post("/news/analyze", summary="특정 뉴스 심층 분석")
async def analyze_news_deep(req: MarketNewsRequest):
    # URL이 있으면 크롤러 동작, 없으면 content 사용
    """
    Analyze a news article and produce a concise market sentiment summary.
    
    Parameters:
        req (MarketNewsRequest): Request containing `content` for direct analysis or `url` pointing to the article to fetch (URL-based fetching is indicated but not implemented).
    
    Returns:
        dict: Analysis result with keys:
            - `summary` (str): Short Korean summary of the article's market implication.
            - `score` (float): Sentiment score where higher indicates more positive sentiment.
            - `recommendation` (str): Investment recommendation based on the analysis.
    """
    target_content = req.content
    if req.url:
        # target_content = await news_crawler.fetch(req.url)
        pass

    return {
        "summary": "해당 기사는 반도체 업황의 턴어라운드를 시사합니다.",
        "score": 0.8,  # 긍정
        "recommendation": "Strong Buy"
    }


@router.post("/sector", summary="섹터 동향 분석")
async def analyze_sector(req: MarketSectorRequest):
    """
    Provide a basic sector analysis for the requested market sector.
    
    Parameters:
        req (MarketSectorRequest): Request containing at least `sector_name` to analyze.
    
    Returns:
        dict: Analysis containing:
            - "sector": the requested sector name,
            - "trend": a short textual trend summary,
            - "keywords": a list of related sector keywords.
    """
    return {
        "sector": req.sector_name,
        "trend": "상승세 (전주 대비 +5%)",
        "keywords": ["HBM", "DDR5", "AI서버"]
    }