from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker  

DATABASE_URL = (
    "mssql+pyodbc://sa:FleetTrack%402026@localhost:1433/Balance"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)
engine = create_engine(DATABASE_URL,pool_pre_ping=True,connect_args={"timeout": 30})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

