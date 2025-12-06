from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base


class DartReportEntity(Base):
    __tablename__ = 'dart_report'

    id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey('company.id'))

    rcept_no = Column(String(255), unique=True)

    report_type = Column(String(255))
    title = Column(String(255))
    content = Column(Text)

    published_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    company = relationship("CompanyEntity", backref="reports")
