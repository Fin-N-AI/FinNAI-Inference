import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_upstage import ChatUpstage

load_dotenv(find_dotenv())

# MCP 클라이언트 설정
client = MultiServerMCPClient({
    "DART-Main": {
        "transport": "stdio",  # 필수
        "command": "docker",
        "args": [
            "run",
            "--rm",
            "-i",
            "--init",
            "-v", ".:/app/data/mcp/DART",
            "-e", "DART_API_KEY=" + os.getenv("DART_API_KEY"),
            "-e", "USECASE=main",
            "snaiws/dart:latest"
        ]
    }
})
#
# client = MultiServerMCPClient({
#         "DART-Main": {
#             "transport": "stdio",
#             "command": "docker",
#             "args": [
#                 "exec",            # [변경] run -> exec
#                 "-i",              # [필수] interactive
#                 "dart-mcp",        # [변경] 접속할 컨테이너 이름
#                 "python", "/app/mcp_server/run_server.py" # 실행 명령
#             ]
#         }
#     })

# LLM 및 에이전트 준비
llm = ChatUpstage()

# 에이전트용 프롬프트 준비
system_message = """
당신은 대한민국 최고의 기업 신용 분석가입니다. DART MCP 도구를 이용하여 아래의 작업을 수행하세요.

당신은 다음 도구들을 사용할 수 있습니다:
{tools}

반드시 다음 형식을 사용해서 답변해야 합니다:

Thought: 다음에 무엇을 할지 생각합니다
Action: 수행할 행동. [{tool_names}] 중에서 하나를 선택해야 합니다.
Action Input: 행동에 대한 입력값
Observation: 행동의 결과
... (이 Thought/Action/Action Input/Observation 패턴은 여러 번 반복될 수 있습니다)
Thought: 이제 최종 답변을 알았습니다
Final Answer: 원본 질문에 대한 최종 답변
"""

# 2. 수정된 ChatPromptTemplate 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("user", "{input}"),
    ("ai", "{agent_scratchpad}")
])


async def run_dart_agent(query: str):
    print("DART MCP 서버(Docker)에 연결을 시도합니다...")
    tools = await client.get_tools()
    for tool in tools:
        print(tool)


if __name__ == '__main__':
    asyncio.run(run_dart_agent("test"))
