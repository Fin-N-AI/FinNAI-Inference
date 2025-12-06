from fastapi import APIRouter

from web.api.request.inference_request import MarketNewsRequest, MarketSectorRequest

router = APIRouter(tags=["Market Intelligence"])


@router.post("/news/analyze", summary="특정 뉴스 심층 분석")
async def analyze_news_deep(req: MarketNewsRequest):
    # URL이 있으면 크롤러 동작, 없으면 content 사용
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
    return {
        "sector": req.sector_name,
        "trend": "상승세 (전주 대비 +5%)",
        "keywords": ["HBM", "DDR5", "AI서버"]
    }
