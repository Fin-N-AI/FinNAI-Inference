import datetime

from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from web.config.database import Base


class ParsedDisclosureFileEntity(Base):
    __tablename__ = 'parsed_disclosure_file'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    disclosure_file_id = Column(BigInteger, ForeignKey('disclosure_file.id'), nullable=False, unique=True)
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)

    company_overview = Column(Text, nullable=True)
    business_contents = Column(Text, nullable=True)
    shareholder_info = Column(Text, nullable=True)
    investor_protection = Column(Text, nullable=True)
    contingent_liabilities = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.datetime.now())

    disclosure_file = relationship("DisclosureFileEntity", back_populates="parsed_file")
    company = relationship("CompanyEntity")
