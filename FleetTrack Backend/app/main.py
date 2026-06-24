from fastapi import FastAPI
from app.customers.router import router as customers_router
app = FastAPI( title = "FleetTrack Backend API", description = "API for FleetTrack Backend", version = "1.0.0" )


@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

app.include_router(customers_router)
