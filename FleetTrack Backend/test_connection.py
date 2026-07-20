from sqlalchemy import create_engine, text

DATABASE_URL = (
    "mssql+pyodbc://sa:FleetTrack%402026@localhost:1433/Balance"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&TrustServerCertificate=yes"
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT DB_NAME()"))
    print(result.fetchone())