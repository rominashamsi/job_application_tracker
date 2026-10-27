import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase





load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None :
    raise ValueError("DATABASE_URL is missing from .env")


engine = create_engine(DATABASE_URL)

Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base (DeclarativeBase):
    pass


def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()


        
if __name__ == "__main__":
    with engine.connect() as connection:
        print("Database connection successful!")