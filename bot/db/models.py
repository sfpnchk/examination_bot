from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from .base import Base, CreatedMixin, UpdatedMixin


class User(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "user"

    name = Column(String(100), nullable=True)
    user_name = Column(String(100), nullable=True)


class Discipline(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "discipline"

    name = Column(String(100), nullable=False)
    short_description = Column(String(4096))


class Question(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "question"

    discipline_id = Column(
        Integer, ForeignKey("discipline.id", ondelete="CASCADE"), nullable=False
    )
    photo = Column(ARRAY(String), nullable=True)
    text = Column(String(100), nullable=False)
    material = Column(String(800), nullable=False)


class Answer(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "answer"

    question_id = Column(Integer, ForeignKey("question.id"), nullable=False)
    text = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)


class UserAnswer(Base, CreatedMixin, UpdatedMixin):
    __tablename__ = "user_answer"

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("answer.id"), nullable=False)
