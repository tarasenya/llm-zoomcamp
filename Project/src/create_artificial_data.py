import datetime
import random

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy.orm import sessionmaker

from database_operations.base_db_operations import get_db_engine
from database_operations.table_definitions import Base
from database_operations.table_definitions import Conversation
from database_operations.table_definitions import Feedback


load_dotenv('../.env')

def generate_data(n_minutes):
    # Create a SQLite database in memory
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    fake = Faker()

    # Generate data for n minutes from now
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=n_minutes)
    current_time = datetime.datetime.now()

    while current_time < end_time:
        # Create a conversation
        conv = Conversation(
            id=fake.uuid4(),
            question=fake.sentence(),
            answer=fake.paragraph(),
            model_used=random.choice(["GPT-3", "GPT-4", "BERT", "T5"]),
            response_time=round(random.uniform(0, 5), 2),
            clarity=random.randint(0, 5),
            relevance=random.randint(0, 5),
            accuracy=random.randint(0, 5),
            completeness=random.randint(0, 5),
            overall_score=round(random.uniform(0, 5), 2),
            explanation=fake.paragraph(),
            improvement_suggestions=fake.paragraph(),
            timestamp=current_time,
        )
        session.add(conv)

        # Create feedback for this conversation
        feedback = Feedback(
            conversation_id=conv.id,
            feedback=random.randint(0, 5),
            timestamp=current_time + datetime.timedelta(minutes=random.randint(1, 10)),
        )
        session.add(feedback)

        # Move time forward
        current_time += datetime.timedelta(seconds=random.randint(1, 5))

    # Commit the session to save the data
    session.commit()

    # Query and print some data to verify
    conversations = session.query(Conversation).all()
    feedbacks = session.query(Feedback).all()

    print(
        f"Generated {len(conversations)} conversations and {len(feedbacks)}\
          feedback entries.")

    session.close()


if __name__ == "__main__":
    n_minutes = 2  # Generate data for the next 60 minutes
    generate_data(n_minutes)
