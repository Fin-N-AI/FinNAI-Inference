import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base

# .env 파일 로드
load_dotenv(find_dotenv())

# ----------------------------------------------------------------
# 1. 환경 변수 설정
# ----------------------------------------------------------------
# 예: postgresql+asyncpg://user:password@localhost:5432/finnai_db
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 비동기용 URL (FastAPI 등 웹 서버용) - driver: asyncpg
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 동기용 URL (스크립트/마이그레이션용) - driver: psycopg2
SYNC_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()

# ----------------------------------------------------------------
# 3. Async (비동기) 설정 - 주 사용
# ----------------------------------------------------------------
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 쿼리 로그 출력 (개발 단계에서 True)
    pool_size=10,
    max_overflow=20,
    future=True
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# FastAPI 의존성 주입(Dependency Injection)용 함수
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ----------------------------------------------------------------
# 4. Sync (동기) 설정 - 스크립트 실행용
# ----------------------------------------------------------------
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()