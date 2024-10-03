import os

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine

from .table_definitions import Base


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
