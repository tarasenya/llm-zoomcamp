import os
from datetime import datetime
from zoneinfo import ZoneInfo
from judge_llm import LLMJudgementScore
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
tz = ZoneInfo("Europe/Berlin")


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
    #TODO: delete this column
    relevance_explanation = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    feedback = relationship("Feedback", back_populates="conversation")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    feedback = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    conversation = relationship("Conversation", back_populates="feedback")

#TODO: delete it, use from base db operations
def create_user_and_db():
    if os.path.exists("../.env"):
        POSTGRES_HOST = os.getenv("POSTGRES_HOST_LOCAL")
    else:
        POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    # Connect to PostgreSQL server
    print(os.getenv("POSTGRES_USER"))
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create user if not exists
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{username}'")
    if cur.fetchone() is None:
        cur.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
        print(f"User {username} created.")
    else:
        print(f"User {username} already exists.")

    # Create database if not exists
    dbname = os.getenv("POSTGRES_DB")
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
    if cur.fetchone() is None:
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"Database {dbname} created.")
    else:
        print(f"Database {dbname} already exists.")

    # Grant privileges to user
    cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username}")
    print(f"Granted all privileges on {dbname} to {username}")

    cur.close()
    conn.close()

# TODO: delete it
def get_db_engine():
    if os.path.exists("../.env"):
        POSTGRES_HOST = os.getenv("POSTGRES_HOST_LOCAL")
    else:
        POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    return create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER', 'your_username')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'your_password')}@"
        f"{POSTGRES_HOST}/"
        f"{os.getenv('POSTGRES_DB', 'vague_translator')}"
    )


def init_db():
    engine = get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def save_conversation(
    conversation_id: int,
    question: str,
    answer: str,
    model_used: str,
    llm_judgement_score: LLMJudgementScore,
    response_time: float,
    timestamp=None,
):
    if timestamp is None:
        timestamp = datetime.now(tz)

    session = get_db_session()
    try:
        conversation = Conversation(
            id=conversation_id,
            question=question,
            answer=answer,
            model_used=model_used,
            response_time=response_time,
            clarity=llm_judgement_score.clarity,
            #TODO: Delete it
            relevance_explanation = 'Hello',
            relevance=llm_judgement_score.relevance,
            accuracy=llm_judgement_score.accuracy,
            completeness=llm_judgement_score.completeness,
            overall_score=llm_judgement_score.overall_score,
            explanation=llm_judgement_score.explanation,
            improvement_suggestions=llm_judgement_score.improvement_suggestions,
            timestamp=timestamp,
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
            timestamp=timestamp,
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
