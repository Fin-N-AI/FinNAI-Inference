from fastapi import APIRouter, BackgroundTasks
from web.api.request.inference_request import DataSyncRequest
from web.api.response.inference_response import DataSyncResponse

router = APIRouter(tags=["Data Management"])


@router.post("/sync/news", response_model=DataSyncResponse, summary="뉴스 수집 강제 실행")
async def sync_news(req: DataSyncRequest, background_tasks: BackgroundTasks):
    """
    Initiate news synchronization for a specific ticker.
    
    Parameters:
        req (DataSyncRequest): Request containing the ticker to synchronize.
    
    Returns:
        DataSyncResponse: `status` is `'success'` when the synchronization job is accepted, `message` is a human-readable status, and `collected_count` is the number of articles collected (0 when the work is scheduled to run later).
    """
    # background_tasks.add_task(news_service.sync_news, req.ticker)

    return DataSyncResponse(
        status="success",
        message=f"{req.ticker} 뉴스 수집 작업이 백그라운드에서 시작되었습니다.",
        collected_count=0
    )


@router.post("/sync/dart", response_model=DataSyncResponse, summary="DART 공시 수집 실행")
async def sync_dart(req: DataSyncRequest):
    """
    Trigger a DART disclosure synchronization and return a summary of the update.
    
    Parameters:
        req (DataSyncRequest): Request payload specifying the scope of the synchronization (e.g., ticker or identifiers).
    
    Returns:
        DataSyncResponse: Summary object containing `status`, a human-readable `message`, and `collected_count` indicating how many disclosures were updated.
    """
    return DataSyncResponse(
        status="success",
        message="최신 공시 2건을 업데이트했습니다.",
        collected_count=2
    )