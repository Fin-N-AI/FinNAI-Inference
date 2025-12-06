from pgvector.sqlalchemy import Vector  # vector 타입 지원
from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base
from web.domain.enums import CompanyFileType



class CompanyEntity(Base):
    """
    https://opendart.fss.or.kr/api/company.json
    """
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # DART 고유 회사코드
    corp_code = Column(String(255))
    # DART 회사명
    name = Column(String(255))
    # DART 종목코드
    stock_code = Column(String(255))

    # 업종 코드
    induty_code = Column(String(255))
    # 시장 구분
    market = Column(String(255))

    # 회사 홈페이지 URL
    homepage_url = Column(String(255))
    # 본사 주소
    headquarters_addr = Column(String(255))
    ceo_name = Column(String(255))
    # 설립일
    founded_date = Column(DateTime)

    # 법인등록번호, 사업자등록번호, 대표전화
    corporate_reg_no = Column(String(255))
    business_reg_no = Column(String(255))
    phone_number = Column(String(255))

    # 회사 개요, 상세 설명
    overview = Column(Text)
    description = Column(Text)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

#
# class CompanyBookmarkEntity(Base):
#     __tablename__ = 'company_bookmark'
#     __table_args__ = (
#         UniqueConstraint('user_account_id', 'company_id', name='uq_company_bookmark_user_company'),
#     )
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     user_account_id = Column(Integer, ForeignKey('user_account.id'))
#     company_id = Column(Integer, ForeignKey('company.id'))
#
#     created_at = Column(DateTime, default=func.now())
#
#     # Relationships
#     user = relationship("UserAccount", backref="bookmarks")
#     company = relationship("Company", backref="bookmarks")
#

class CompanyEmbeddingEntity(Base):
    __tablename__ = 'company_embedding'

    id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey('company.id'))

    # pgvector: vector(1536)
    embedding = Column(Vector(1536))

    created_at = Column(DateTime, default=func.now())

    company = relationship("CompanyEntity", backref="embeddings")
#
#
# class CompanyFileEntity(Base):
#     __tablename__ = 'company_file'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     company_id = Column(Integer, ForeignKey('company.id'))
#     uploaded_by_id = Column(Integer, ForeignKey('user_account.id'), name='uploaded_by')
#
#     file_type = Column(SAEnum(CompanyFileType), nullable=False)
#     file_url = Column(String(255))
#     original_name = Column(String(255))
#     raw_content = Column(Text)
#
#     created_at = Column(DateTime, default=func.now())
#
#     company = relationship("CompanyEntity", backref="files")
#     uploader = relationship("UserAccount")
#
#
# class CompanyFollowing(Base):
#     __tablename__ = 'company_following'
#     __table_args__ = (
#         UniqueConstraint('user_account_id', 'company_id', name='uq_company_following_user_company'),
#     )
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     user_account_id = Column(Integer, ForeignKey('user_account.id'))
#     company_id = Column(Integer, ForeignKey('company.id'))
#
#     created_at = Column(DateTime, default=func.now())
#
#     user = relationship("UserAccount", backref="followings")
#     company = relationship("CompanyEntity", backref="followers")
