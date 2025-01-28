import os
from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://deez_nuts_user:3ggO96X7fqJVLnrV6INOt3VsKwm4bReF@dpg-cuci0256l47c7392393g-a:5432/deez_nuts")

database = Database(DATABASE_URL)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def connect():
    await database.connect()

async def disconnect():
    await database.disconnect()
