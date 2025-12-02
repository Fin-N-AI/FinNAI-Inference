from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, LargeBinary
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base

#
# class UserProfile(Base):
#     __tablename__ = 'user_profile'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     # OneToOne 관계: unique=True 설정
#     user_account_id = Column(Integer, ForeignKey('user_account.id'), unique=True)
#
#     username = Column(String(255))
#
#     # @Lob byte[] -> LargeBinary
#     profile_image = Column(LargeBinary)
#
#     bio = Column(String(255))
#
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, onupdate=func.now())
#
#     user = relationship("UserAccount", backref=relationship("UserProfile", uselist=False))
