from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

db_pwd = os.getenv("DB_PWD")
db_server = os.getenv("DB_SERVER")
database_url = os.getenv("DATABASE_URL", f"mssql+pyodbc://sa:{db_pwd}@{db_server},1433/MultiAgents?driver=ODBC+Driver+17+for+SQL+Server")

engine = create_engine(database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
