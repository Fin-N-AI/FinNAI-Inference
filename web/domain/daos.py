from datetime import datetime
from typing import Optional

from langchain.tools import tool
from sqlalchemy import select
from sqlalchemy.orm import Session

# 1. 설정 및 Entity 임포트 (경로는 프로젝트에 맞게 수정)
from web.config.database import SessionLocal
from web.domain.entity.company import CompanyEntity
from web.domain.entity.disclosure import DisclosureListEntity
from web.domain.entity.finance import FinancialAccountEntity
from web.domain.entity.report import DartReportEntity
from web.schemas.company import Company
from web.schemas.disclosure import DisclosureList
from web.schemas.finance import FinancialAccount
from web.schemas.report import DartReport


# (User가 제공한 Entity 클래스 이름에 맞춤)


def get_db():
    """DB 세션을 생성하고 에러 발생 시 닫아주는 헬퍼 함수"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


@tool("save_company_info", args_schema=Company)
def save_company_info(
        corp_code: str,
        name: str,
        stock_code: str,
        ceo_name:Optional[str] = None,
        induty_code: Optional[str] = None,
        market: Optional[str] = None,
        homepage_url: Optional[str] = None,
        headquarters_addr: Optional[str] = None,
        founded_date: Optional[datetime] = None,
        corporate_reg_no: Optional[str] = None,
        business_reg_no: Optional[str] = None,
        phone_number: Optional[str] = None,
        overview: Optional[str] = None,
        description: Optional[str] = None,
        id: Optional[int] = None
):
    """
    회사의 기본 정보를 DB 'company' 테이블에 저장하거나 업데이트합니다.
    (종목코드 stock_code를 기준으로 중복을 확인합니다.)
    """
    db = get_db()
    try:
        # 1. 조회: 이미 존재하는 회사인가? (stock_code 기준)
        stmt = select(CompanyEntity).where(CompanyEntity.stock_code == stock_code)
        existing_company = db.execute(stmt).scalars().first()

        if existing_company:
            # 2-1. 존재하면 업데이트 (Update)
            existing_company.corp_code = corp_code
            existing_company.name = name
            existing_company.ceo_name = ceo_name
            existing_company.induty_code = induty_code
            existing_company.market = market
            existing_company.homepage_url = homepage_url
            existing_company.headquarters_addr = headquarters_addr
            existing_company.founded_date = founded_date
            existing_company.corporate_reg_no = corporate_reg_no
            existing_company.business_reg_no = business_reg_no
            existing_company.phone_number = phone_number
            existing_company.overview = overview
            existing_company.description = description

            action = "Updated"
            target_id = existing_company.id
        else:
            # 2-2. 없으면 신규 생성 (Insert)
            new_company = CompanyEntity(
                corp_code=corp_code,
                name=name,
                ceo_name=ceo_name,
                stock_code=stock_code,
                induty_code=induty_code,
                market=market,
                homepage_url=homepage_url,
                headquarters_addr=headquarters_addr,
                founded_date=founded_date,
                corporate_reg_no=corporate_reg_no,
                business_reg_no=business_reg_no,
                phone_number=phone_number,
                overview=overview,
                description=description
            )
            db.add(new_company)
            db.commit()  # ID 생성을 위해 커밋
            db.refresh(new_company)

            action = "Created"
            target_id = new_company.id

        db.commit()
        return f"Company info {action} successfully. ID: {target_id}, Name: {name}"

    except Exception as e:
        db.rollback()
        return f"Error saving company info: {str(e)}"
    finally:
        db.close()


@tool("save_financial_info", args_schema=FinancialAccount)
def save_financial_info(
        company_id: int,
        bsns_year: int,
        reprt_code: str,
        account_nm: str,
        thstrm_amount: int,
        account_id: Optional[str] = None,  # Optional 처리
        id: Optional[int] = None
):
    """
    회사의 재무 정보를 DB 'financial_account' 테이블에 저장합니다.
    중복 체크 기준: [회사ID + 사업연도 + 보고서코드 + 계정명]
    """
    db = get_db()
    try:
        # 1. 중복 조회 (복합 키 조건)
        stmt = select(FinancialAccountEntity).where(
            FinancialAccountEntity.company_id == company_id,
            FinancialAccountEntity.bsns_year == bsns_year,
            FinancialAccountEntity.reprt_code == reprt_code,
            FinancialAccountEntity.account_nm == account_nm
        )
        existing_account = db.execute(stmt).scalars().first()

        if existing_account:
            # 2-1. 업데이트 (금액이나 계정코드가 바뀌었을 수 있음)
            existing_account.thstrm_amount = thstrm_amount
            existing_account.account_id = account_id
            action = "Updated"
        else:
            # 2-2. 신규 생성
            new_account = FinancialAccountEntity(
                company_id=company_id,
                bsns_year=bsns_year,
                reprt_code=reprt_code,
                account_id=account_id,
                account_nm=account_nm,
                thstrm_amount=thstrm_amount
            )
            db.add(new_account)
            action = "Created"

        db.commit()
        return f"Financial info {action} successfully. Year: {bsns_year}, Account: {account_nm}"

    except Exception as e:
        db.rollback()
        return f"Error saving financial info: {str(e)}"
    finally:
        db.close()


@tool("save_disclosure_info", args_schema=DisclosureList)
def save_disclosure_info(
        company_id: int,
        rcept_no: str,
        report_nm: str,
        rcept_dt: datetime,
        rpt_type: Optional[str] = None,
        flr_nm: Optional[str] = None,
        id: Optional[int] = None
):
    """
    회사의 공시 정보를 저장합니다.
    중복 체크 기준: [rcept_no (접수번호)] - DART에서 유일한 키입니다.
    """
    db = get_db()
    try:
        # 1. 중복 조회 (접수번호 기준)
        stmt = select(DisclosureListEntity).where(DisclosureListEntity.rcept_no == rcept_no)
        existing_disclosure = db.execute(stmt).scalars().first()

        if existing_disclosure:
            # 2-1. 업데이트 (보통 공시 내용은 잘 안 바뀌지만, 정정 공시 등의 경우 대비)
            existing_disclosure.report_nm = report_nm
            existing_disclosure.rpt_type = rpt_type
            existing_disclosure.company_id = company_id  # 혹시 연결이 잘못되었을 경우 수정
            action = "Updated"
        else:
            # 2-2. 신규 생성
            new_disclosure = DisclosureListEntity(
                company_id=company_id,
                rcept_no=rcept_no,
                report_nm=report_nm,
                rcept_dt=rcept_dt,
                rpt_type=rpt_type,
                flr_nm=flr_nm
            )
            db.add(new_disclosure)
            action = "Created"

        db.commit()
        return f"Disclosure info {action} successfully. Report: {report_nm}"

    except Exception as e:
        db.rollback()
        return f"Error saving disclosure info: {str(e)}"
    finally:
        db.close()


@tool("save_report_info", args_schema=DartReport)
def save_report_info(
        company_id: int,
        rcept_no: str,
        title: str,
        report_type: str,
        content: str,
        published_at: datetime,
        id: Optional[int] = None
):
    """
    상세 리포트(본문 포함)를 저장합니다.
    중복 체크 기준: [rcept_no (접수번호)]
    """
    db = get_db()
    try:
        # 1. 중복 조회 (접수번호 기준)
        stmt = select(DartReportEntity).where(DartReportEntity.rcept_no == rcept_no)
        existing_report = db.execute(stmt).scalars().first()

        if existing_report:
            # 2-1. 업데이트 (내용 수정 등)
            existing_report.title = title
            existing_report.content = content
            existing_report.published_at = published_at
            action = "Updated"
        else:
            # 2-2. 신규 생성
            new_report = DartReportEntity(
                company_id=company_id,
                rcept_no=rcept_no,
                title=title,
                report_type=report_type,
                content=content,
                published_at=published_at
            )
            db.add(new_report)
            action = "Created"

        db.commit()
        return f"Report info {action} successfully. Title: {title}"

    except Exception as e:
        db.rollback()
        return f"Error saving report info: {str(e)}"
    finally:
        db.close()