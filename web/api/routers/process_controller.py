from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from web.config.database import get_db
from web.domain.dao.data_processing_dao import DataProcessingDAO
from web.services.data_processing_service import DataProcessingService

router = APIRouter(prefix="/api/v1/process")


@router.post("/{corp_code}", status_code=201)
async def process_company_data(
        corp_code: str,
        start_date: str = None,
        end_date: str = None,
        year: int = None,
        db: AsyncSession = Depends(get_db)
):
    """
    지정된 기업 코드에 대한 전체 데이터 처리 파이프라인을 실행합니다.
    (기업 정보, 재무 정보, 공시 정보 수집, 파싱, 요약 및 저장)
    """
    if year is None:
        year = datetime.now().year
    if end_date is None:
        end_date = f"{year}1231"
    if start_date is None:
        start_date = f"{year}0101"

    service = DataProcessingService()
    dao = DataProcessingDAO()
    #ToDo: 여기 stockcode로 조회해서 중복되면 바로 응답
    try:
        # 서비스 호출하여 모든 데이터 객체 생성
        company, fin_accounts, fin_indices, disclosure_data = service.process_company_data(
            corp_code=corp_code,
            start_date=start_date,
            end_date=end_date,
            year=year
        )

        # DAO를 통해 트랜잭션 내에서 모든 데이터 저장
        await dao.save_all_in_transaction(
            db=db,
            company=company,
            fin_accounts=fin_accounts,
            fin_indices=fin_indices,
            disclosure_data=disclosure_data
        )

        return {"message": f"Successfully processed and saved all data for corp_code: {corp_code}"}

    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        # TODO: 로깅 추가
        print(f"Error processing {corp_code}: {e}")

        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
