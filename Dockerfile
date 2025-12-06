# Python 기본 이미지 사용
FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY requirements.in .

RUN uv pip install --system -r requirements.in

COPY . .

EXPOSE 8000

CMD ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]