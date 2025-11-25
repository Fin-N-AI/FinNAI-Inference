import asyncio
from typing import List, Dict
import FinanceDataReader as fdr

from langchain import hub
# [변경 1] Structured Chat Agent 사용
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import tool

# MCP Client 및 LLM 설정
from agent_test import llm, client

# 기존의 DB 저장 도구들
from web.domain.persistence.dao import (
    save_report_info,
    save_company_info,
    save_financial_info,
    save_disclosure_info
)

def parsing_error_fixer(error: Exception) -> str:
    """
    Structured Agent가 JSON을 문자열로 잘못 보냈을 때,
    에러를 뱉는 대신 에이전트에게 수정 방법을 알려주는 함수.
    """
    error_str = str(error)
    # 문자열 입력 에러가 나면 구체적으로 지시함
    if "String tool inputs are not allowed" in error_str:
        return (
            "SYSTEM ERROR: You passed a STRING value to the tool, but the tool expects a JSON OBJECT.\n"
            "FIX: Do NOT wrap the JSON in quotes.\n"
            "WRONG: \"{\"key\": \"value\"}\"\n"
            "RIGHT: {\"key\": \"value\"}\n"
            "Please try again with the corrected format."
        )
    # 그 외 파싱 에러
    return f"Parsing Error: {error_str}. Check your output format and make sure it's valid JSON."
# --------------------------------------------------------------------------
# 1. 외부(Python)에서 실행할 리스트 확보 함수
# --------------------------------------------------------------------------
def get_top_k_stocks_manual(k: int) -> List[Dict[str, str]]:
    print(f"Running FDR to get top {k} stocks...")
    df = fdr.StockListing('KRX')
    df_filtered = df[df['Market'].isin(['KOSPI', 'KOSDAQ'])]
    df_sorted = df_filtered.dropna(subset=['Marcap']).sort_values(by='Marcap', ascending=False)
    result = df_sorted.head(k)[['Name', 'Code']].to_dict(orient='records')
    return result


async def run_agent_pipeline():
    # --------------------------------------------------------------------------
    # 2. 시스템 초기화
    # --------------------------------------------------------------------------
    print(">>> [System] MCP 도구 로드 중...")
    try:
        mcp_tools = await client.get_tools()

        # update_corplist 선행 실행
        update_tool = next((t for t in mcp_tools if t.name == "update_corplist"), None)
        if update_tool:
            print(">>> [System] DART 기업 코드 파일 갱신 중... (1회)")
            await update_tool.ainvoke({})
            print(">>> [System] 갱신 완료.")
    except Exception as e:
        print(f">>> [Error] 초기화 중 오류 발생: {e}")
        return

    # --------------------------------------------------------------------------
    # 3. Structured Chat Agent 설정 (복잡한 도구 사용에 최적화)
    # --------------------------------------------------------------------------
    tools = [save_report_info, save_company_info, save_financial_info, save_disclosure_info]
    tools.extend(mcp_tools)

    # [핵심] ReAct 구조를 가지면서 JSON 입력을 잘 처리하는 표준 프롬프트 사용
    # Hub에서 검증된 프롬프트를 가져옵니다. (안정성 최고)
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # 에이전트 생성
    agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=parsing_error_fixer,  # 필수
        max_iterations=30
    )

    # --------------------------------------------------------------------------
    # 4. 메인 루프
    # --------------------------------------------------------------------------
    TARGET_COUNT = 3  # 테스트용 3개
    print(f">>> [Controller] 상위 {TARGET_COUNT}개 기업 리스트 확보 중...")

    top_stocks = get_top_k_stocks_manual(TARGET_COUNT)

    print(f">>> [Controller] 총 {len(top_stocks)}개 기업 작업을 시작합니다.")
    print("=" * 60)

    for i, stock in enumerate(top_stocks):
        name = stock['Name']
        code = stock['Code']

        print(f"\n>>> [Task {i + 1}/{len(top_stocks)}] '{name}' ({code}) 처리 시작")

        # Structured Chat Agent에게 보낼 메시지 구성
        # 이 에이전트는 'input' 키 하나만 받습니다.
        user_msg = f"""
        [임무]
        당신은 ETL Worker입니다. '{name}'(종목코드: {code})의 데이터를 찾아 DB에 저장하세요.

        [단계]
        1. 'get_corpcode'로 DART 고유번호 찾기.
        2. **기본 정보 저장 (Base Info)**
           - 'get_corpinfo'를 호출하여 상세 정보를 조회하십시오.
           - **중요: 조회된 결과에 있는 모든 필드(대표자명, 주소, 설립일, 홈페이지 등)를 빠짐없이 'save_company_info'의 인자로 전달하십시오.**
           - 누락된 정보가 없도록 주의하십시오.        
        3. 2023년 사업보고서(11011) 기준 '배당(get_dividend_info)', '임원(get_executives)' 조회.
        4. 조회된 결과가 있다면 'save_financial_info' 등으로 저장.

        저장이 끝나면 "완료"라고 답하고 종료하세요.
        """

        try:
            # invoke 호출 (변수는 input 하나만 있으면 됨)
            await agent_executor.ainvoke({"input": user_msg})
            print(f">>> [Task {i + 1}] 완료.")

        except Exception as e:
            print(f">>> [Task {i + 1}] 에러 발생: {e}")
            continue

    print("=" * 60)
    print(">>> [System] 모든 작업이 종료되었습니다.")


if __name__ == '__main__':
    asyncio.run(run_agent_pipeline())