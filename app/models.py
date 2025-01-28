import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

database = Database(DATABASE_URL)

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"} if "render.com" in DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import Column, Integer, String, Enum
from .database import Base
from enum import Enum as PyEnum

class Status(PyEnum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    status = Column(Enum(Status), default=Status.TODO)
