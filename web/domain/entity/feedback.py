from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text,
    ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

from web.config.database import Base
#
#
# class FeedbackBoard(Base):
#     __tablename__ = 'feedback_board'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     user_account_id = Column(Integer, ForeignKey('user_account.id'))
#
#     title = Column(String(255), nullable=False)
#     content = Column(Text, nullable=False)
#     is_public = Column(Boolean, default=True)
#
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, onupdate=func.now())
#     deleted_at = Column(DateTime)
#
#     user = relationship("UserAccount", backref="feedbacks")
#     # OneToMany relationship defined via backref in FeedbackComment or explicitly here
#     comments = relationship("FeedbackComment", back_populates="board", cascade="all, delete-orphan")
#
#
# class FeedbackComment(Base):
#     __tablename__ = 'feedback_comment'
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#
#     feedback_board_id = Column(Integer, ForeignKey('feedback_board.id'))
#     user_account_id = Column(Integer, ForeignKey('user_account.id'))
#
#     content = Column(Text, nullable=False)
#
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, onupdate=func.now())
#     deleted_at = Column(DateTime)
#
#     board = relationship("FeedbackBoard", back_populates="comments")
#     user = relationship("UserAccount", backref="comments")
