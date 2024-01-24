import os
from typing import Dict, Type, Union
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from sqlmodel import Session, SQLModel, create_engine


def create_db_schemas(session:Session):
    
    session.exec(text("CREATE SCHEMA IF NOT EXISTS application"))
    session.commit()

def create_tables(engine: Engine):
    
    SQLModel.metadata.create_all(engine)


def get_session():
    engine = get_sqlmodel_engine()
    with Session(engine) as session:
        yield session
        
        
def get_sqlmodel_engine() -> Engine:
     return create_engine(get_pg_con_string())
     
     
def get_pg_con_string():
    """
    Get postgresql connection string.
    :return:
    """
    pg_user = os.getenv("pg_user")
    pg_dbname = os.getenv("pg_dbname")
    pg_password = os.getenv("pg_password")
    pg_host = os.getenv("pg_host")
    pg_port = os.getenv("pg_port")

    return f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_dbname}"