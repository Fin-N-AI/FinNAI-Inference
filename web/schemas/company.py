from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import Field
from web.domain.enums import CompanyFileType
from web.domain.models.models import BaseSchema


class Company(BaseSchema):  # 혹은 사용하시던 BaseSchema
    """
    https://opendart.fss.or.kr/api/company.json
    기업 기본 정보 스키마
    """

    id: Optional[int] = Field(
        default=None,  # <--- 이게 있어야 진짜 Optional이 됩니다.
        description="회사 고유 ID (PK)"
    )
    corp_code: Optional[str] = Field(
        default=None,
        description="고유 회사코드 (DART 고유번호)"
    )
    name: Optional[str] = Field(
        default=None,
        description="회사명 (법인명)"
    )
    ceo_name: Optional[str] = Field(
        default=None,
        description="대표이사(CEO) 이름"
    )
    stock_code: Optional[str] = Field(
        default=None,
        description="DART 종목코드 (상장사 코드)"
    )
    induty_code: Optional[str] = Field(
        default=None,
        description="업종 코드 (DART 표준산업분류코드)"
    )
    market: Optional[str] = Field(
        default=None,
        description="소속 시장 구분 (예: KOSPI, KOSDAQ, KONEX 등)"
    )
    homepage_url: Optional[str] = Field(
        default=None,
        description="회사 대표 홈페이지 URL"
    )
    headquarters_addr: Optional[str] = Field(
        default=None,
        description="본사 소재지 주소"
    )
    founded_date: Optional[datetime] = Field(
        default=None,
        description="설립일 (YYYY-MM-DD)"
    )
    corporate_reg_no: Optional[str] = Field(
        default=None,
        description="법인등록번호"
    )
    business_reg_no: Optional[str] = Field(
        default=None,
        description="사업자등록번호"
    )
    phone_number: Optional[str] = Field(
        default=None,
        description="대표 전화번호"
    )
    overview: Optional[str] = Field(
        default=None,
        description="회사에 대한 간단한 요약. (주소, 대표자명 등 다른 필드에 있는 정보는 제외하고 순수 개요만 넣을 것)"
    )
    description: Optional[str] = Field(
        default=None,
        description="상세 설명. (주의: 전화번호, 홈페이지, 사업자번호 등은 해당되는 별도 필드에 넣고 여기에 텍스트로 뭉쳐 넣지 마십시오.)"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="데이터 생성 일시"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="데이터 최종 수정 일시"
    )
class CompanyEmbedding(BaseSchema):
    """
    기업 정보 벡터 임베딩 스키마 (검색/RAG용)
    """
    id: int = Field(
        description="임베딩 ID (PK)"
    )
    company_id: Optional[int] = Field(
        default=None,
        description="연관 회사 ID (FK)"
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="텍스트 임베딩 벡터 (차원: 1536 - OpenAI Ada-002 등)"
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="임베딩 생성 일시"
    )

