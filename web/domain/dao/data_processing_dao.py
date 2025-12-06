from typing import List, Tuple

from sqlalchemy import select
# [변경] AsyncSession과 select 임포트
from sqlalchemy.ext.asyncio import AsyncSession

from web.domain.entity.company import CompanyEntity
from web.domain.entity.disclosure import DisclosureListEntity, DisclosureFileEntity
from web.domain.entity.finance import FinancialAccountEntity, FinancialIndexEntity
from web.domain.entity.parsed_disclosure_file import ParsedDisclosureFileEntity


class DataProcessingDAO:


    async def save_all_in_transaction(


            self,


            db: AsyncSession,


            company: CompanyEntity,


            fin_accounts: List[FinancialAccountEntity],


            fin_indices: List[FinancialIndexEntity],


            disclosure_data: List[Tuple[DisclosureListEntity, DisclosureFileEntity, ParsedDisclosureFileEntity]]


    ):


        print("[DAO] Transaction started.")


        print(f"[DAO] Upserting company with corp_code: {company.corp_code}")
        query = select(CompanyEntity).filter_by(corp_code=company.corp_code)
        result = await db.execute(query)
        existing_company = result.scalars().first()

        if existing_company:
            print(f"[DAO]   -> Found existing company. Updating fields.")
            # Update existing company if necessary
            existing_company.name = company.name
            existing_company.stock_code = company.stock_code
            existing_company.induty_code = company.induty_code
            existing_company.market = company.market
            existing_company.homepage_url = company.homepage_url
            existing_company.headquarters_addr = company.headquarters_addr
            existing_company.ceo_name = company.ceo_name
            existing_company.founded_date = company.founded_date
            existing_company.corporate_reg_no = company.corporate_reg_no
            existing_company.business_reg_no = company.business_reg_no
            existing_company.phone_number = company.phone_number
            existing_company.overview = company.overview
            existing_company.description = company.description
            company_orm = existing_company
        else:
            print(f"[DAO]   -> No existing company. Creating new one.")
            db.add(company)
            await db.flush()
            company_orm = company

        company_id = company_orm.id
        print(f"[DAO] Company upserted. ID: {company_id}")
        for account in fin_accounts:
            account.company_id = company_id
        for index in fin_indices:


            index.company_id = company_id


        for disc_list, _, _ in disclosure_data:


            disc_list.company_id = company_id





        # 2. Bulk insert financial accounts and indices


        print("[DAO] Adding financial accounts and indices.")


        if fin_accounts:


            db.add_all(fin_accounts)


        if fin_indices:


            db.add_all(fin_indices)


        print("[DAO] Financial data added to session.")





        # 3. Insert disclosure data


        print(f"[DAO] Processing {len(disclosure_data)} disclosure items.")


        for i, (disc_list, disc_file, parsed_file) in enumerate(disclosure_data):


            print(f"[DAO] Item {i + 1}/{len(disclosure_data)}: Upserting DisclosureList for rcept_no={disc_list.rcept_no}")


            # Upsert DisclosureList


            query = select(DisclosureListEntity).filter_by(rcept_no=disc_list.rcept_no)


            result = await db.execute(query)


            existing_disclosure = result.scalars().first()





            if existing_disclosure:


                print(f"[DAO]   -> Found existing DisclosureList. Updating.")


                existing_disclosure.report_nm = disc_list.report_nm


                disclosure_list_orm = existing_disclosure


            else:


                print(f"[DAO]   -> No existing DisclosureList. Creating new one.")


                db.add(disc_list)


                await db.flush()


                disclosure_list_orm = disc_list





            disclosure_id = disclosure_list_orm.id


            print(f"[DAO]   -> DisclosureList ready. ID: {disclosure_id}")




            # Upsert DisclosureFile


            print(f"[DAO] Item {i + 1}/{len(disclosure_data)}: Upserting DisclosureFile for disclosure_id={disclosure_id}")


            query_file = select(DisclosureFileEntity).filter_by(disclosure_id=disclosure_id)


            result_file = await db.execute(query_file)


            existing_file = result_file.scalars().first()





            if not existing_file:


                print(f"[DAO]   -> No existing DisclosureFile. Creating new one.")


                disc_file.disclosure_id = disclosure_id


                db.add(disc_file)


                await db.flush()


                disclosure_file_id = disc_file.id


            else:


                print(f"[DAO]   -> Found existing DisclosureFile.")


                disclosure_file_id = existing_file.id


            print(f"[DAO]   -> DisclosureFile ready. ID: {disclosure_file_id}")





            # Upsert ParsedDisclosureFile


            print(


                f"[DAO] Item {i + 1}/{len(disclosure_data)}: Upserting ParsedDisclosureFile for disclosure_file_id={disclosure_file_id}")


            query_parsed = select(ParsedDisclosureFileEntity).filter_by(disclosure_file_id=disclosure_file_id)


            result_parsed = await db.execute(query_parsed)


            existing_parsed = result_parsed.scalars().first()





            if not existing_parsed:


                print(f"[DAO]   -> No existing ParsedDisclosureFile. Creating new one.")


                parsed_file.disclosure_file_id = disclosure_file_id


                parsed_file.company_id = company_id


                db.add(parsed_file)


            else:


                print(f"[DAO]   -> Found existing ParsedDisclosureFile. Skipping.")





        print("[DAO] All items processed. Awaiting commit from controller.")




