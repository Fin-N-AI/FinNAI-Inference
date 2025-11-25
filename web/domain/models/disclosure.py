from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import Field
from web.domain.enums import DisclosureFileType
from web.domain.models.models import BaseSchema


class DisclosureList(BaseSchema):
    """
    DART 공시 목록 정보 (OpenDART API: /api/list.json 결과)
    특정 기업의 개별 공시 건에 대한 메타데이터를 저장합니다.
    """
    id: int = Field(
        description="공시 목록 레코드의 내부 고유 ID (PK)"
    )
    company_id: int = Field(
        description="해당 공시를 제출한 기업의 ID (Company 테이블의 id 참조, FK)"
    )
    rcept_no: str = Field(
        description="DART 접수번호 (14자리). DART 시스템 내에서 공시를 식별하는 고유 키 (Unique Key)"
    )
    report_nm: Optional[str] = Field(
        default=None,
        description="공시 보고서 제목 (예: '분기보고서 (2024.03)', '주요사항보고서(유상증자결정)')"
    )
    rcept_dt: Optional[date] = Field(
        default=None,
        description="공시 접수 일자 (YYYY-MM-DD). 시계열 분석 시 기준 날짜로 사용"
    )
    rpt_type: Optional[str] = Field(
        default=None,
        description="공시 유형 코드 (A: 정기공시, B: 주요사항보고, I: 거래소공시 등). 필터링 용도"
    )
    flr_nm: Optional[str] = Field(
        default=None,
        description="공시 제출인명 (법인명 또는 대표자명). 데이터 출처 확인용"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="공시 데이터 수집 및 레코드 생성 일시"
    )


class DisclosureFile(BaseSchema):
    """
    공시 상세 내용 및 첨부파일 데이터
    DisclosureList의 rcept_no를 통해 다운로드(/api/document.xml 등)받은 구체적인 문서 내용입니다.
    LLM이 실제로 분석(Reading/Summary)하게 될 텍스트 데이터를 담습니다.
    """
    id: int = Field(
        description="공시 파일 레코드의 내부 고유 ID (PK)"
    )
    disclosure_id: int = Field(
        description="연관된 공시 목록 ID (DisclosureList 테이블의 id 참조, FK). 1:N 관계 가능성 고려"
    )
    file_type: Optional[DisclosureFileType] = Field(
        default=None,
        description="파일 포맷 유형 (HTML, XML, PDF 등). 파싱 전략 결정을 위한 메타데이터"
    )
    file_url: Optional[str] = Field(
        default=None,
        description="파일 저장 경로 URL (S3 버킷 주소 등). 원본 파일 접근용"
    )
    raw_content: Optional[str] = Field(
        default=None,
        description="파일에서 추출한 텍스트 원문(Full Text). LLM 임베딩 및 요약의 직접적인 대상이 되는 핵심 데이터"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="파일 다운로드 및 파싱 완료 일시"
    )