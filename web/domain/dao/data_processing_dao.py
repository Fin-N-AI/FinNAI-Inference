from typing import List, Tuple

# [변경] AsyncSession과 select 임포트
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from web.domain.entity.company import CompanyEntity
from web.domain.entity.disclosure import DisclosureListEntity, DisclosureFileEntity
from web.domain.entity.finance import FinancialAccountEntity, FinancialIndexEntity
from web.domain.entity.parsed_disclosure_file import ParsedDisclosureFileEntity


class DataProcessingDAO:
    async def get_company_by_corp_code(self, db: AsyncSession, corp_code: str) -> CompanyEntity | None:
        """
        주어진 corp_code로 회사 엔티티를 조회합니다.
        """
        result = await db.execute(select(CompanyEntity).filter(CompanyEntity.corp_code == corp_code))
        return result.scalars().first()

    # [변경] async def로 선언, db 타입 힌트 변경
    async def save_all_in_transaction(
            self,
            db: AsyncSession,
            company: CompanyEntity,
            fin_accounts: List[FinancialAccountEntity],
            fin_indices: List[FinancialIndexEntity],
            disclosure_data: List[Tuple[DisclosureListEntity, DisclosureFileEntity, ParsedDisclosureFileEntity]]
    ):
        try:
            # 1. Upsert Company
            # [변경] await 추가
            # merge는 비동기 함수이므로 await를 해야 실제 객체가 반환됩니다.
            company = await db.merge(company)
            await db.flush()  # [변경] await 추가

            # Assign company_id to related entities
            company_id = company.id

            # (참고) company가 merge되면서 attached 상태가 되었으므로
            # relationship 설정이 잘 되어 있다면 객체 할당만으로도 FK가 잡히지만,
            # 명시적으로 ID를 넣는 현재 로직도 안전합니다.
            for account in fin_accounts:
                account.company_id = company_id
            for index in fin_indices:
                index.company_id = company_id
            for disc_list, _, _ in disclosure_data:
                disc_list.company_id = company_id

            # 2. Bulk insert financial accounts and indices
            # [변경] AsyncSession에서는 bulk_save_objects 대신 add_all 사용 권장
            if fin_accounts:
                db.add_all(fin_accounts)
            if fin_indices:
                db.add_all(fin_indices)

            # add_all은 동기함수지만, DB 반영은 나중 flush/commit 때 일어납니다.

            # 3. Insert disclosure data
            for disc_list, disc_file, parsed_file in disclosure_data:
                # Upsert DisclosureList
                # [변경] db.query -> await db.execute(select(...))
                query = select(DisclosureListEntity).filter_by(rcept_no=disc_list.rcept_no)
                result = await db.execute(query)
                existing_disclosure = result.scalars().first()

                if existing_disclosure:
                    # Update existing
                    existing_disclosure.report_nm = disc_list.report_nm
                    disclosure_list_orm = existing_disclosure
                else:
                    db.add(disc_list)
                    await db.flush()  # [변경] await 추가 (ID 생성을 위해 필수)
                    disclosure_list_orm = disc_list

                disclosure_id = disclosure_list_orm.id

                # Upsert DisclosureFile
                # [변경] select 구문으로 변경
                query_file = select(DisclosureFileEntity).filter_by(disclosure_id=disclosure_id)
                result_file = await db.execute(query_file)
                existing_file = result_file.scalars().first()

                if not existing_file:
                    disc_file.disclosure_id = disclosure_id
                    db.add(disc_file)
                    await db.flush()  # [변경] await 추가
                    disclosure_file_id = disc_file.id
                else:
                    disclosure_file_id = existing_file.id

                # Upsert ParsedDisclosureFile
                # [변경] select 구문으로 변경
                query_parsed = select(ParsedDisclosureFileEntity).filter_by(disclosure_file_id=disclosure_file_id)
                result_parsed = await db.execute(query_parsed)
                existing_parsed = result_parsed.scalars().first()

                if not existing_parsed:
                    parsed_file.disclosure_file_id = disclosure_file_id
                    parsed_file.company_id = company_id
                    db.add(parsed_file)

            await db.commit()  # [변경] await 추가
        except Exception as e:
            print("db 저장 중 오류 발생")
            await db.rollback()  # [변경] await 추가
            raise e