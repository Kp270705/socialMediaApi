
from sqlmodel import SQLModel, Field, create_engine

sqlite_filename=f"database.db"
sqlite_url=f"sqlite:///{sqlite_filename}"

engine=create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)