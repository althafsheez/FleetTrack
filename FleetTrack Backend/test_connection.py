from sqlalchemy import create_engine 

DATABASE_URL = ("mssql+pyodbc://@Sheez_Laptop/FleetTrack_DB_Dev"
                "?driver=ODBC+Driver+18+for+SQL+Server"
                "&trusted_connection=yes"
                "&TrustServerCertificate=yes")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"timeout": 30})

with engine.connect() as connection:
    print("Connection to the database was successful!")