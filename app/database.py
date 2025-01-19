from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:200123@localhost/fastapi' 

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionalLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():#SQLALCHEMY
    db = SessionalLocal()
    try:
        yield db
    finally:
        db.close()

# using SQLALCHEMY