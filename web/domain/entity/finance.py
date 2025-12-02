from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Float, BigInteger
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base


class FinancialAccountEntity(Base):
    __tablename__ = 'financial_account'

    id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey('company.id'))

    bsns_year = Column(Integer)
    reprt_code = Column(String(255))

    account_id = Column(String(255))
    account_nm = Column(String(255))

    thstrm_amount = Column(BigInteger)  # Java Long -> Python Integer/BigInteger (SQLAlchemy handles automatically)

    created_at = Column(DateTime, default=func.now())

    company = relationship("CompanyEntity", backref="financial_accounts")


class FinancialIndexEntity(Base):
    __tablename__ = 'financial_index'

    id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey('company.id'))

    bsns_year = Column(Integer)
    reprt_code = Column(String(255))

    index_nm = Column(String(255))
    index_value = Column(Float)  # Java Double -> Python Float

    created_at = Column(DateTime, default=func.now())

    company = relationship("CompanyEntity", backref="financial_indices")
