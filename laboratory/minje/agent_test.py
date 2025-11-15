import asyncio
from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage
from langchain.agents import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv, find_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain import hub
load_dotenv(find_dotenv())

#MCP 클라이언트 설정
client = MultiServerMCPClient({
    "DART": {
        "transport": "stdio",  # 필수
        "command": "docker",
        "args": [
            "run",
            "--rm",
            "-i",
            "-v", ".:/app/data/mcp/DART",
            "-e", "DART_API_KEY=" + os.getenv("DART_API_KEY"),
            "-e", "USECASE=light",
            "snaiws/dart:latest"
        ]
    }
})

#LLM 및 에이전트 준비
llm = ChatUpstage()

#에이전트용 프롬프트 준비
system_message = """
당신은 대한민국 최고의 기업 신용 분석가입니다. DART MCP 도구를 이용하여 사용자의 질문에 대답해주세요.

당신은 다음 도구들을 사용할 수 있습니다:
{tools}

반드시 다음 형식을 사용해서 답변해야 합니다:

Thought: 다음에 무엇을 할지 생각합니다
Action: 수행할 행동. [{tool_names}] 중에서 하나를 선택해야 합니다.
Action Input: 행동에 대한 입력값
Observation: 행동의 결과
... (이 Thought/Action/Action Input/Observation 패턴은 여러 번 반복될 수 있습니다)
Thought: 이제 최종 답변을 알았습니다
Final Answer: (당신은 대한민국 최고의 기업 신용 분석가입니다. 분석된 결과를 바탕으로, 유쾌하고 명료하며 전문가적인 톤으로 최종 답변을 작성해주세요.) 원본 질문에 대한 최종 답변
"""

# 2. 수정된 ChatPromptTemplate 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", "{input}"),  # <-- {question}을 {input}으로 변경
    ("ai", "{agent_scratchpad}")# intermediate_steps 리스트를 LLM이 다음 행동을 추론할 수 있도록 **특정 형식(ReAct)로 변환한 문자열
])

async def run_dart_agent():
    print("DART MCP 서버(Docker)에 연결을 시도합니다...")

    # [수정 1] await 추가, get_tools() -> load_tools()로 변경
    tools = await client.get_tools()

    print("--- 로드된 도구 (DART) ---")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    print("-------------------------")

    agent_executor = create_react_agent(llm, tools, prompt=prompt)

    question = "삼성전자의 2024년 3분기 보고서에서 현금흐름표를 요약해줘."

    print(f"\n[질문]: {question}\n")

    try:
        #intermediate_steps : (중간 단계) 에이전트가 지금 까지 수행한 (액션, 관찰) 쌍의 실제 기록
        result = await agent_executor.ainvoke({"input": question, "intermediate_steps":[]})

        # 최종 답변만 출력
        print(f"\n[최종 답변]:\n{result['messages'][-1].content}")

    except Exception as e:
        print(f"에이전트 실행 중 오류 발생: {e}")

if __name__ == '__main__':
    asyncio.run(run_dart_agent())