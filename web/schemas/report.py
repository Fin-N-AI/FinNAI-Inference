from datetime import datetime
from typing import Optional

from pydantic import Field

from web.domain.models.models import BaseSchema


class DartReport(BaseSchema):
    """
    DART 공시 보고서 통합 데이터
    공시 목록 메타데이터와 본문 내용(Content)을 함께 포함하는 스키마입니다.
    """
    id: int = Field(
        description="리포트 고유 ID (PK)"
    )
    company_id: Optional[int] = Field(
        default=None,
        description="연관된 회사의 내부 DB ID (Company 테이블의 id 참조, FK). "
                    "주의: DART의 '고유번호(corp_code)'가 아님."
    )
    rcept_no: Optional[str] = Field(
        default=None,
        description="DART 접수번호 (Unique Key). "
                    "해당 보고서를 식별하는 14자리 고유 번호"
    )
    title: Optional[str] = Field(
        default=None,
        description="보고서 제목 (예: '분기보고서(2024.09)', '주식매수선택권행사'). "
                    "사용자가 보고서를 검색하거나 식별할 때 사용하는 이름"
    )
    report_type: Optional[str] = Field(
        default=None,
        description="보고서 유형 분류 (예: '정기공시', '주요사항보고'). "
                    "공시의 성격을 파악하는 필터링 키워드"
    )
    content: Optional[str] = Field(
        default=None,
        description="보고서 본문 내용 (Text Content). "
                    "LLM이 읽고 요약하거나 질문에 답변할 때 사용하는 핵심 텍스트 데이터"
    )
    published_at: Optional[datetime] = Field(
        default=None,
        description="공시 제출/게시 일시 (DART 접수일자). "
                    "정보의 최신성을 판단하는 기준 시간"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="데이터 생성 및 저장 일시"
    )