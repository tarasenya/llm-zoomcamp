import os
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
tz = ZoneInfo("Europe/Berlin")

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(String, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    course = Column(String, nullable=False)
    model_used = Column(String, nullable=False)
    response_time = Column(Float, nullable=False)
    relevance = Column(String, nullable=False)
    relevance_explanation = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    feedback = relationship("Feedback", back_populates="conversation")

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, ForeignKey('conversations.id'))
    feedback = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    conversation = relationship("Conversation", back_populates="feedback")

def get_db_engine():
    return create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER', 'your_username')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'your_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'postgres')}/"
        f"{os.getenv('POSTGRES_DB', 'course_assistant')}"
    )

def init_db():
    engine = get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def save_conversation(conversation_id, question, answer_data, course, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    session = get_db_session()
    try:
        conversation = Conversation(
            id=conversation_id,
            question=question,
            answer=answer_data["answer"],
            course=course,
            model_used=answer_data["model_used"],
            response_time=answer_data["response_time"],
            relevance=answer_data["relevance"],
            relevance_explanation=answer_data["relevance_explanation"],
            timestamp=timestamp
        )
        session.add(conversation)
        session.commit()
    finally:
        session.close()

def save_feedback(conversation_id, feedback_value, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    session = get_db_session()
    try:
        feedback = Feedback(
            conversation_id=conversation_id,
            feedback=feedback_value,
            timestamp=timestamp
        )
        session.add(feedback)
        session.commit()
    finally:
        session.close()

def get_feedback_stats():
    session = get_db_session()
    try:
        thumbs_up = session.query(Feedback).filter(Feedback.feedback > 0).count()
        thumbs_down = session.query(Feedback).filter(Feedback.feedback < 0).count()
        return {"thumbs_up": thumbs_up, "thumbs_down": thumbs_down}
    finally:
        session.close()