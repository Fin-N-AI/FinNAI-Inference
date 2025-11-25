from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base
from web.domain.enums import DisclosureFileType

class DisclosureListEntity(Base):
    """
    https://opendart.fss.or.kr/api/list.json
    """
    __tablename__ = 'disclosure_list'

    id = Column(Integer, primary_key=True, autoincrement=True)

    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)

    # 공시 수신번호 (Unique)
    rcept_no = Column(String(255), nullable=False, unique=True)

    report_nm = Column(String(255))
    rcept_dt = Column(DateTime)  # Date type in Java, mapped to DateTime or Date
    rpt_type = Column(String(255))
    flr_nm = Column(String(255))

    created_at = Column(DateTime, default=func.now())

    company = relationship("CompanyEntity", backref="disclosures")


class DisclosureFileEntity(Base):
    __tablename__ = 'disclosure_file'
    __table_args__ = (
        UniqueConstraint('disclosure_id', 'file_type', 'file_url', name='uq_disclosure_file'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    disclosure_id = Column(Integer, ForeignKey('disclosure_list.id'), nullable=False)

    file_type = Column(SAEnum(DisclosureFileType))
    file_url = Column(String(255))
    raw_content = Column(Text)

    created_at = Column(DateTime, default=func.now())

    disclosure = relationship("DisclosureListEntity", backref="files")