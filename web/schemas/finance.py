from datetime import datetime
from typing import Optional
from pydantic import Field

from web.domain.models.models import BaseSchema


class FinancialAccount(BaseSchema):
    """
    DART 단일회사 전체 재무제표 (OpenDART API: /api/fnlttSinglAcntAll.json)
    재무제표의 원본 계정 데이터(Raw Data)를 저장합니다. (예: 자산총계, 매출액 등)
    """
    id: int = Field(
        description="재무제표 계정 레코드 ID (PK)"
    )
    company_id: Optional[int] = Field(
        default=None,
        description="해당 재무제표의 기업 ID (Company 테이블의 id 참조, FK)"
    )

    bsns_year: Optional[int] = Field(
        description="사업연도 (Fiscal Year). 예: 2023, 2024 (시계열 데이터의 기준 연도)"
    )
    reprt_code: Optional[str] = Field(
        description="보고서 코드 (데이터의 시점 구분). "
                    "11011: 사업보고서(연간), 11012: 반기보고서, 11013/11014: 분기보고서"
    )
    account_id: Optional[str] = Field(
        description="계정 ID (DART/IFRS 표준 ID). 예: 'ifrs-full_Revenue', 'ifrs-full_Assets'. "
                    "정확한 계정 매핑 및 비교 분석 시 사용되는 식별자"
    )
    account_nm: Optional[str] = Field(
        description="계정명 (한글). 예: '매출액', '자산총계'. "
                    "사용자 질의(자연어)와 매칭되는 필드"
    )
    thstrm_amount: Optional[int] = Field(
        description="당기 금액 (Current Period Amount). "
                    "해당 계정의 실제 수치 데이터 (단위: 원)"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="데이터 수집 및 생성 일시"
    )


class FinancialIndex(BaseSchema):
    """
    재무제표 보조 지표 (Calculated/Derived Metrics)
    FinancialAccount의 원본 데이터를 기반으로 2차 가공/계산된 투자 지표입니다.
    """
    id: int = Field(
        description="재무 지표 레코드 ID (PK)"
    )
    company_id: Optional[int] = Field(
        default=None,
        description="해당 지표의 기업 ID (Company 테이블의 id 참조, FK)"
    )

    bsns_year: Optional[int] = Field(
        description="사업연도 (Fiscal Year). 지표 계산의 기준이 되는 연도"
    )
    reprt_code: Optional[str] = Field(
        description="보고서 코드. 해당 지표가 산출된 시점 (11011: 연말 기준 등)"
    )
    index_nm: Optional[str] = Field(
        description="지표명 (Metric Name). 예: 'ROE', 'PER', '부채비율', '영업이익률'. "
                    "LLM이 특정 투자 지표를 검색할 때 사용하는 키워드"
    )
    index_value: Optional[float] = Field(
        description="계산된 지표 값 (Calculated Value). "
                    "비율(%) 또는 배수(x) 등의 수치 데이터"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="지표 계산 및 생성 일시"
    )