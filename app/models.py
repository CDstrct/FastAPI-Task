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
