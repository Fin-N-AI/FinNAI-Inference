
from typing import List, Dict, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from fake_useragent import UserAgent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_upstage import ChatUpstage
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool

import OpenDartReader
from web.domain.entity.company import CompanyEntity
from web.domain.entity.disclosure import (DisclosureListEntity, DisclosureFileEntity)
from web.domain.entity.parsed_disclosure_file import ParsedDisclosureFileEntity
from web.domain.entity.finance import FinancialAccountEntity, FinancialIndexEntity
from web.domain.enums import DisclosureFileType

load_dotenv(find_dotenv())


class DataProcessingService:
    def __init__(self):
        self.dart = OpenDartReader(os.getenv("DART_API_KEY"))
        self.ua = UserAgent()
        self.llm = ChatUpstage()
        self.output_parser = StrOutputParser()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=20000,
            chunk_overlap=1000,
            separators=["\n\n", "\n", " ", ""],
        )
        self._setup_prompts()

    def _setup_prompts(self):
        self.map_prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 긴 문서에서 핵심 사실을 빠짐없이 추출하는 데이터 분석가입니다."),
            ("human", """
            다음은 금융 공시 문서의 일부입니다.
            이후 단계에서 초보자를 위한 쉬운 글을 작성할 수 있도록,
            주어진 텍스트 이외의 내용을 요약해서는 안됩니다.
            중요한 사실(숫자, 핵심 기술, 사업 모델, 시장 상황) 위주로 내용을 요약해주세요.

            [문서 일부]
            {text}

            요약:
            """),
        ])
        self.overview_prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 어려운 금융 용어를 주식 초보자도 이해하기 쉽게 풀어주는 '친절한 투자 멘토'입니다."),
            ("human", """
            다음은 회사의 개요에 대한 핵심 내용들입니다.
            이 내용을 바탕으로, 주식을 처음 시작하는 사람도 이 회사가 **'도대체 무엇으로 돈을 버는 회사인지'** 단번에 이해할 수 있도록 1000자 이내의 쉬운 줄글로 설명해주세요.
            주어진 텍스트 이외의 내용을 요약해서는 안됩니다.

            [필수 작성 지침]
            1. **전문 용어 금지**: '영업수익', '당기순이익' 같은 단어 대신 '매출', '순수익' 처럼 쉬운 말로 바꾸거나 풀어서 설명하세요.
            2. **비유와 예시 활용**: 비즈니스 모델이 어렵다면 일상생활의 예시를 들어 설명하세요.
            3. **스토리텔링**: 딱딱한 보고서체가 아니라, 옆에서 말해주는 듯한 부드러운 어조(해요체 또는 부드러운 서술형)를 사용하세요.
            4. **형식**: 절대 번호나 글머리 기호(1., -)를 쓰지 말고, 자연스러운 문단으로 이어지게 작성하세요.

            [내용]
            {text}
            """),
        ])
        self.description_prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 복잡한 기술과 산업 이야기를 대중에게 쉽게 전달하는 'IT/산업 전문 칼럼니스트'입니다."),
            ("human", """
            다음은 회사의 상세 사업 내용들입니다.
            이 내용을 바탕으로 이 회사의 **주요 제품과 서비스가 우리 일상 생활 어디에 쓰이는지**, 그리고 **시장에서 어떤 경쟁력이 있는지** 1000자 이내의 쉬운 줄글로 설명해주세요.
            주어진 텍스트 이외의 내용을 요약해서는 안됩니다.

            [필수 작성 지침]
            1. **쉬운 설명**: 기술적인 스펙 나열보다는, 그 기술이 소비자에게 어떤 가치를 주는지(예: '편리함', '비용 절감')에 집중하세요.
            2. **독자 중심**: "이 회사는 B2B 사업을 영위함" 보다는 "이 회사는 다른 기업들에게 부품을 납품하여 돈을 법니다"와 같이 구체적인 상황을 그려주세요.
            3. **흐름 유지**: 각 사업부가 따로 노는 느낌이 아니라, 회사의 전체적인 사업 방향성이 보이도록 연결하여 작성하세요.
            4. **스토리텔링**: 딱딱한 보고서체가 아니라, 옆에서 말해주는 듯한 부드러운 어조(해요체 또는 부드러운 서술형)를 사용하세요.
            5. **형식**: 번호 매기기를 하지 말고, 한 편의 읽기 쉬운 수필이나 기사처럼 작성하세요.
            
            [내용]
            {text}
            """),
        ])
        self.map_chain = self.map_prompt | self.llm | self.output_parser
        self.overview_chain = self.overview_prompt | self.llm | self.output_parser
        self.description_chain = self.description_prompt | self.llm | self.output_parser

    async def process_company_data(self, corp_code: str, start_date: str, end_date: str, year: int, reprt_code: str = "11011") -> Tuple[
        CompanyEntity,
        List[FinancialAccountEntity],
        List[FinancialIndexEntity],
        List[Tuple[DisclosureListEntity, DisclosureFileEntity, ParsedDisclosureFileEntity]]
    ]:
        # 1. Get Company Info
        company_entity = await run_in_threadpool(self._get_company_info, corp_code)
        print(f"회사 조회 완료 {company_entity.name}")

        # 2. Get Financial Info
        fin_accounts, fin_indices = await run_in_threadpool(self._get_financial_info, corp_code, year, reprt_code)
        print(f"재무 정보 조회 완료 {fin_accounts[0].account_nm}")
        # 3. Get Disclosure Info
        disclosure_data = await run_in_threadpool(self._get_disclosure_info, corp_code, start_date, end_date)
        print(f"공시 정보 조회 완료{disclosure_data}")
        # 4. Summarize (LLM)
        overview_text = ""
        business_text = ""
        
        # Find the longest overview and business content from all disclosures
        longest_overview = ""
        longest_business = ""
        for _, _, parsed_file in disclosure_data:
            if parsed_file.company_overview and len(parsed_file.company_overview) > len(longest_overview):
                longest_overview = parsed_file.company_overview
            if parsed_file.business_contents and len(parsed_file.business_contents) > len(longest_business):
                longest_business = parsed_file.business_contents
        
        if longest_overview:
            overview_text = await run_in_threadpool(self._run_smart_summary, longest_overview, self.overview_chain)
        if longest_business:
            business_text = await run_in_threadpool(self._run_smart_summary, longest_business, self.description_chain)
        company_entity.overview = overview_text
        company_entity.description = business_text
        print("문서 요약 완료")

        return company_entity, fin_accounts, fin_indices, disclosure_data

    def _get_company_info(self, corp_code: str) -> CompanyEntity:
        data = self.dart.company(corp_code)
        if not data:
            raise ValueError(f"Could not find company info for corp_code: {corp_code}")

        return CompanyEntity(
            corp_code=data.get('corp_code'),
            name=data.get('corp_name'),
            stock_code=data.get('stock_code'),
            ceo_name=data.get('ceo_nm'),
            induty_code=data.get('induty_code'),
            market="KOSPI" if "유가" in data.get('corp_cls', '') else "KOSDAQ",
            homepage_url=data.get('hm_url'),
            headquarters_addr=data.get('adres'),
            corporate_reg_no=data.get('jurir_no'),
            business_reg_no=data.get('bizr_no'),
            phone_number=data.get('phn_no'),
            founded_date=pd.to_datetime(data.get('est_dt'), format='%Y%m%d', errors='coerce').to_pydatetime(),
        )

    def _get_financial_info(self, corp_code: str, year: int, reprt_code: str) -> Tuple[List[FinancialAccountEntity], List[FinancialIndexEntity]]:
        df = self.dart.finstate_all(corp_code, year, reprt_code)
        if df is None or df.empty:
            return [], []

        accounts = []
        key_metrics = {}
        for _, row in df.iterrows():
            amount_str = row['thstrm_amount']
            amount = int(amount_str.replace(',', '')) if amount_str and amount_str != '-' else 0
            
            accounts.append(FinancialAccountEntity(
                bsns_year=year,
                reprt_code=reprt_code,
                account_id=row.get('account_id'),
                account_nm=row['account_nm'],
                thstrm_amount=amount
            ))

            clean_nm = row['account_nm'].replace(" ", "").strip()
            if clean_nm in ["자산총계", "자산"]: key_metrics['total_assets'] = amount
            elif clean_nm in ["부채총계", "부채"]: key_metrics['total_liabilities'] = amount
            elif clean_nm in ["자본총계", "자본"]: key_metrics['total_equity'] = amount
            elif clean_nm in ["매출액", "수익(매출액)", "영업수익"]: key_metrics['revenue'] = amount
            elif clean_nm in ["영업이익", "영업이익(손실)"]: key_metrics['operating_income'] = amount
            elif clean_nm in ["당기순이익", "당기순이익(손실)"]: key_metrics['net_income'] = amount
        
        indices = self._calculate_financial_indices(year, reprt_code, key_metrics)
        return accounts, indices

    def _calculate_financial_indices(self, year: int, reprt_code: str, metrics: Dict) -> List[FinancialIndexEntity]:
        indices = []
        assets = metrics.get('total_assets', 0)
        liabilities = metrics.get('total_liabilities', 0)
        equity = metrics.get('total_equity', 0)
        revenue = metrics.get('revenue', 0)
        op_income = metrics.get('operating_income', 0)
        net_income = metrics.get('net_income', 0)

        if equity > 0:
            indices.append(FinancialIndexEntity(bsns_year=year, reprt_code=reprt_code, index_nm="부채비율", index_value=round((liabilities / equity) * 100, 2)))
        if revenue > 0:
            indices.append(FinancialIndexEntity(bsns_year=year, reprt_code=reprt_code, index_nm="영업이익률", index_value=round((op_income / revenue) * 100, 2)))
            indices.append(FinancialIndexEntity(bsns_year=year, reprt_code=reprt_code, index_nm="순이익률", index_value=round((net_income / revenue) * 100, 2)))
        if assets > 0:
            indices.append(FinancialIndexEntity(bsns_year=year, reprt_code=reprt_code, index_nm="ROA", index_value=round((net_income / assets) * 100, 2)))
        if equity > 0:
            indices.append(FinancialIndexEntity(bsns_year=year, reprt_code=reprt_code, index_nm="ROE", index_value=round((net_income / equity) * 100, 2)))
        
        return indices

    async def _get_disclosure_info(self, corp_code: str, start_date: str, end_date: str) -> List[Tuple[DisclosureListEntity, DisclosureFileEntity, ParsedDisclosureFileEntity]]:
        df = await run_in_threadpool(self.dart.list, corp_code, start=start_date, end=end_date, kind='A')
        if df is None or df.empty:
            return []

        disclosure_data = []
        for _, row in df.iterrows():
            rcept_no = row['rcept_no']
            
            # DisclosureList
            disclosure_list = DisclosureListEntity(
                rcept_no=rcept_no,
                report_nm=row['report_nm'],
                rcept_dt=pd.to_datetime(row['rcept_dt'], format='%Y%m%d').to_pydatetime(),
                flr_nm=row['flr_nm']
            )

            # DisclosureFile
            raw_text = await run_in_threadpool(self.dart.document, rcept_no)
            file_type = self._detect_file_type(raw_text)
            disclosure_file = DisclosureFileEntity(
                file_type=file_type,
                file_url=f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                #raw_content=raw_text
            )

            # ParsedDisclosureFile
            parsed_content = await self._parse_disclosure_document(rcept_no)
            parsed_file = ParsedDisclosureFileEntity(**parsed_content)
            
            disclosure_data.append((disclosure_list, disclosure_file, parsed_file))
        return disclosure_data

    def _detect_file_type(self, content: str) -> DisclosureFileType:
        if not content: return DisclosureFileType.ETC
        content_head = content[:500].lower().strip()
        if "<?xml" in content_head or "<dart-xml" in content_head or "<document>" in content_head:
            return DisclosureFileType.XBRL
        if "<html" in content_head or "<!doctype html" in content_head:
            return DisclosureFileType.HTML
        return DisclosureFileType.ETC

    async def _parse_disclosure_document(self, rcept_no: str) -> Dict[str, str]:
        sub_docs = await run_in_threadpool(self.dart.sub_docs, rcept_no)
        parsed_data = {
            "company_overview": None,
            "business_contents": None,
            "shareholder_info": None,
            "investor_protection": None,
            "contingent_liabilities": None
        }

        if sub_docs is None:
            return parsed_data

        target_map = {
            "company_overview": "회사의 개요",
            "business_contents": "사업의 내용",
            "shareholder_info": "주주에 관한 사항",
            "investor_protection": "그 밖에 투자자 보호를 위하여 필요한 사항",
            "contingent_liabilities": "우발부채 등에 관한 사항"
        }

        for key, title in target_map.items():
            target_doc = sub_docs[sub_docs['title'].str.contains(title)]
            if not target_doc.empty:
                try:
                    target_url = target_doc['url'].values[0]
                    headers = {'User-Agent': self.ua.random, 'Referer': 'https://dart.fss.or.kr/'}
                    response = await run_in_threadpool(requests.get, target_url, headers=headers)
                    await run_in_threadpool(time.sleep, random.uniform(0.1, 0.3))
                    soup = await run_in_threadpool(BeautifulSoup, response.content, 'html.parser')
                    raw_text = await run_in_threadpool(lambda s: s.get_text(separator='\n').replace('\xa0', ' '), soup)
                    clean_text = re.sub(r'\n+', '\n', raw_text).strip()
                    parsed_data[key] = clean_text
                except Exception as e:
                    print(f" > Failed to parse {title}: {e}")
                    parsed_data[key] = None
        return parsed_data

    async def _run_smart_summary(self, text_content: str, final_chain) -> str:
        print("문서 요약 시작")
        if not text_content or pd.isna(text_content):
            return ""

        async def invoke_with_retry_async(chain, input_data, max_retries=3):
            for attempt in range(max_retries):
                try:
                    return await chain.ainvoke(input_data)
                except Exception as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        await run_in_threadpool(time.sleep, wait_time)
                        print("요약 중 오류 발생")
                    else:
                        raise e
            raise Exception("API call failed after max retries.")

        if len(text_content) < self.text_splitter._chunk_size:
            return await invoke_with_retry_async(final_chain, {"text": text_content})

        docs = await run_in_threadpool(self.text_splitter.create_documents, [text_content])
        split_texts = [doc.page_content for doc in docs]
        
        chunk_summaries = []
        for text_piece in split_texts:
            res = await invoke_with_retry_async(self.map_chain, {"text": text_piece})
            chunk_summaries.append(res)
            await run_in_threadpool(time.sleep, 1) # Throttling

        combined_summary = "\n\n".join(chunk_summaries)
        return await invoke_with_retry_async(final_chain, {"text": combined_summary})
