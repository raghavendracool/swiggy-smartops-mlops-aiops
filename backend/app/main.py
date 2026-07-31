from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import BACKEND_TITLE, BACKEND_VERSION
from backend.app.database import Base, SessionLocal, engine

from backend.app import models

from backend.app.routes import (
    address_routes,
    admin_routes,
    auth_routes,
    mlops_routes,
    order_routes,
    restaurant_routes,
)
from backend.app.seed_data import seed_master_data

app = FastAPI(
    title=BACKEND_TITLE,
    description="Swiggy SmartOps backend with model v2, MLOps dashboard, location, weather, distance, customer retention, and coupon intelligence",
    version=BACKEND_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_master_data(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Swiggy SmartOps backend is running",
        "version": BACKEND_VERSION,
        "features": [
            "model v2 location weather prediction",
            "restaurant location master",
            "menu master",
            "address book",
            "order for someone else",
            "weather API",
            "distance calculation",
            "business scenario engine",
            "customer retention dashboard",
            "coupon recommendation dashboard",
            "restaurant operations risk",
            "area operations risk",
            "MLOps business dashboard",
        ],
    }


app.include_router(auth_routes.router)
app.include_router(address_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(order_routes.router)
app.include_router(admin_routes.router)
app.include_router(mlops_routes.router)