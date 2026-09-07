import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.auth.dependencies import get_current_user
from app.auth.router import router as auth_router
from app.vehicles.router import router as vehicles_router
from app.tariffs.router import router as tariffs_router
from app.contracts.router import router as contracts_router
from app.customers.router import router as customers_router
from app.suppliers.router import router as suppliers_router
from app.lookups.router import router as lookups_router
app = FastAPI( title = "FleetTrack Backend API", description = "API for FleetTrack Backend", version = "1.0.0" )


# Explicit development origins; configure a comma-separated list for other frontends.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",") if origin.strip()],
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
)


@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

app.include_router(auth_router)

authenticated = [Depends(get_current_user)]
app.include_router(customers_router, dependencies=authenticated)
app.include_router(suppliers_router, dependencies=authenticated)
app.include_router(lookups_router, dependencies=authenticated)

app.include_router(vehicles_router, dependencies=authenticated)
app.include_router(tariffs_router, dependencies=authenticated)
app.include_router(contracts_router, dependencies=authenticated)
