from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

SQLALCHEMY_DATABASE_URL = "sqlite:///./twitterdb.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    with db_session() as db:
        yield db
# class DBSessionManager:
#     def __init__(self):
#         self.db = SessionLocal()

#     def __enter__(self):
#         return self.db

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.db.close()
