from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mssql+pyodbc://sa:1234@localhost/ThoughtNest?driver=ODBC+Driver+18+for+SQL+Server"

engine = create_engine(DATABASE_URL, connect_args={"driver": "ODBC Driver 17 for SQL Server"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  

def db_dependency():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()