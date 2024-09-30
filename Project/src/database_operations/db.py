from datetime import datetime
from zoneinfo import ZoneInfo
from judge_llm import LLMJudgementScore
from .table_definitions import Conversation, Feedback
from .base_db_operations import get_db_engine

from sqlalchemy.orm import sessionmaker

tz = ZoneInfo("Europe/Berlin")

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
