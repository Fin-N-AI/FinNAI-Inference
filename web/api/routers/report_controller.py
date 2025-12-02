import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from web.api.request.inference_request import CompanyRequest
from web.api.response.inference_response import ReportResponse, CompanyBriefingResponse, CompanyHighlightResponse
# from web.api.request.report_request import ReportMetadata (필요 시 사용)

# LangChain 관련 임포트
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI

router = APIRouter(tags=["Report Analysis"])

# 임시 파일 저장 경로
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/analyze", response_model=ReportResponse, summary="PDF 보고서 분석")
async def analyze_report(
        file: UploadFile = File(...),
        report_type: str = Form("annual", description="보고서 유형 (annual/quarterly)")
):
    """
        Analyze an uploaded PDF report and produce a structured summary, insights, and key metrics.
        
        Validates and processes the provided PDF file, performs report-level analysis, and returns a structured ReportResponse containing a human-readable summary, extracted insights, and key financial/operational metrics.
        
        Parameters:
            report_type (str): Report type indicator; expected values are "annual" or "quarterly" and affect analysis context.
        
        Returns:
            ReportResponse: An object with:
                - summary (str): A concise summary of the report.
                - insights (list[str]): Key observations and actionable points extracted from the report.
                - key_metrics (dict[str, str]): Named metrics (e.g., "매출액", "영업이익") mapped to their extracted or inferred values.
        """
    pass
    # 1. 파일 검증
    # if file.content_type != "application/pdf":
    #     raise HTTPException(status_code=400, detail="PDF 파일만 지원합니다.")
    #
    # # 2. 임시 파일 저장
    # file_id = str(uuid.uuid4())
    # file_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")
    #
    # try:
    #     with open(file_path, "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
    #
    #     # -------------------------------------------------------
    #     # 3. AI 분석 로직 (LangChain)
    #     # -------------------------------------------------------
    #
    #     # (1) PDF 로드
    #     loader = PyPDFLoader(file_path)
    #     pages = loader.load_and_split()
    #
    #     # (2) 요약 수행 (실제 구현 시엔 토큰 수에 맞춰 Map-Reduce 사용 권장)
    #     llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    #     chain = load_summarize_chain(llm, chain_type="map_reduce")
    #
    #     # 비용 절약을 위해 앞부분 3페이지만 테스트
    #     summary_result = chain.run(pages[:3])
    #
    #     # (3) 더미 데이터 (실제로는 LLM 프롬프트로 추출해야 함)
    #     insights = [
    #         f"{report_type} 보고서 기준, 주요 사업 부문 성장세 지속",
    #         "원자재 가격 상승에 따른 리스크 관리 필요"
    #     ]
    #     key_metrics = {
    #         "매출액": "분석 중...",
    #         "영업이익": "분석 중..."
    #     }
    #
    #     return ReportResponse(
    #         summary=summary_result,
    #         insights=insights,
    #         key_metrics=key_metrics
    #     )
    #
    # except Exception as e:
    #     print(f"Error processing file: {e}")
    #     raise HTTPException(status_code=500, detail="보고서 분석 중 오류가 발생했습니다.")
    #
    # finally:
    #     # 4. 임시 파일 삭제
    #     if os.path.exists(file_path):
    #         os.remove(file_path)