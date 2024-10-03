from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    model_used = Column(String, nullable=False)
    response_time = Column(Float, nullable=False)
    clarity = Column(Integer, nullable=True)
    relevance = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    completeness = Column(Integer, nullable=True)
    overall_score = Column(Float, nullable=True)
    explanation = Column(String, nullable=True)
    improvement_suggestions = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    feedback = relationship("Feedback", back_populates="conversation")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    feedback = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    conversation = relationship("Conversation", back_populates="feedback")
