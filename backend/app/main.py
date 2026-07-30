from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# ==================================================
# 1. Paths
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT_DIR / "models" / "swiggy_delay_model_small.pkl"
FEATURES_PATH = ROOT_DIR / "models" / "model_features.pkl"


# ==================================================
# 2. Database - local SQLite now
# Later we will replace this with AWS RDS PostgreSQL
# ==================================================

DATABASE_URL = "sqlite:///./swiggy_orders.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ==================================================
# 3. Load ML model
# ==================================================

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


# ==================================================
# 4. Database Tables
# ==================================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    membership_tier = Column(String, default="NONE")


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    cuisine_tag = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cuisine_tag = Column(String, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    city = Column(String)
    device_type = Column(String)
    quantity = Column(Integer)

    gross_amount = Column(Float)
    coupon_discount_amount = Column(Float)
    membership_benefit_amount = Column(Float)
    total_discount_amount = Column(Float)
    net_amount = Column(Float)

    coupon_used_num = Column(Integer)
    surge_num = Column(Integer)
    raining_num = Column(Integer)
    campaign_exposed_num = Column(Integer)
    delivery_success_num = Column(Integer)

    rating = Column(Float)
    order_status = Column(String, default="PLACED")
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderPrediction(Base):
    __tablename__ = "order_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))

    delay_prediction = Column(Integer)
    delay_risk = Column(String)
    delay_probability = Column(Float)
    recommendation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================================================
# 5. Request Models
# ==================================================

class LoginRequest(BaseModel):
    name: str
    email: str
    membership_tier: str = "NONE"


class OrderRequest(BaseModel):
    user_id: int
    restaurant_id: int
    product_id: int

    city: str
    device_type: str = "Android"
    quantity: int = 1

    coupon_used_num: int = 0
    coupon_discount_amount: float = 0
    membership_benefit_amount: float = 0

    surge_num: int = 0
    raining_num: int = 0
    campaign_exposed_num: int = 0
    delivery_success_num: int = 1

    rating: float = 4.0
    membership_tier: str = "NONE"

    coupon_name: str = "NONE"
    campaign_name: str = "NONE"
    channel: str = "NONE"
    objective: str = "NONE"


# ==================================================
# 6. FastAPI App
# ==================================================

app = FastAPI(
    title="Swiggy SmartOps Fullstack API",
    description="Mini Swiggy app backend with ML delay prediction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# 7. DB Session
# ==================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================================================
# 8. ML Prediction Function
# ==================================================

def predict_delay(ml_input: dict):
    input_df = pd.DataFrame([ml_input])

    input_encoded = pd.get_dummies(input_df)

    input_encoded = input_encoded.reindex(
        columns=model_features,
        fill_value=0
    )

    prediction = int(model.predict(input_encoded)[0])

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(input_encoded)[0][1])
    else:
        probability = 0.0

    delay_risk = "High Delay Risk" if prediction == 1 else "Low Delay Risk"

    recommendation = (
        "Increase delivery partner availability / monitor zone"
        if prediction == 1
        else "Normal monitoring"
    )

    return prediction, probability, delay_risk, recommendation


# ==================================================
# 9. Startup - create tables and seed data
# ==================================================

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    if db.query(Restaurant).count() == 0:
        restaurants = [
            Restaurant(
                restaurant_name="Hyderabad Biryani House",
                city="Hyderabad",
                cuisine_tag="Biryani"
            ),
            Restaurant(
                restaurant_name="Bangalore Burger Point",
                city="Bangalore",
                cuisine_tag="Burger"
            ),
            Restaurant(
                restaurant_name="Chinese Bowl",
                city="Hyderabad",
                cuisine_tag="Chinese"
            ),
        ]

        db.add_all(restaurants)
        db.commit()

        products = [
            Product(
                restaurant_id=1,
                product_name="Paneer Biryani",
                price=320,
                cuisine_tag="Biryani"
            ),
            Product(
                restaurant_id=1,
                product_name="Chicken Biryani",
                price=380,
                cuisine_tag="Biryani"
            ),
            Product(
                restaurant_id=2,
                product_name="Veg Burger",
                price=180,
                cuisine_tag="Burger"
            ),
            Product(
                restaurant_id=2,
                product_name="Cheese Burger",
                price=220,
                cuisine_tag="Burger"
            ),
            Product(
                restaurant_id=3,
                product_name="Veg Noodles",
                price=250,
                cuisine_tag="Chinese"
            ),
        ]

        db.add_all(products)
        db.commit()

    db.close()


# ==================================================
# 10. API Routes
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Swiggy SmartOps backend is running"
    }


@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if user is None:
        user = User(
            name=request.name,
            email=request.email,
            membership_tier=request.membership_tier
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "membership_tier": user.membership_tier
    }


@app.get("/restaurants")
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()

    return [
        {
            "restaurant_id": r.restaurant_id,
            "restaurant_name": r.restaurant_name,
            "city": r.city,
            "cuisine_tag": r.cuisine_tag
        }
        for r in restaurants
    ]


@app.get("/restaurants/{restaurant_id}/products")
def get_products(restaurant_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(
        Product.restaurant_id == restaurant_id
    ).all()

    return [
        {
            "product_id": p.product_id,
            "restaurant_id": p.restaurant_id,
            "product_name": p.product_name,
            "price": p.price,
            "cuisine_tag": p.cuisine_tag
        }
        for p in products
    ]


@app.post("/orders")
def create_order(request: OrderRequest, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(
        Restaurant.restaurant_id == request.restaurant_id
    ).first()

    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    product = db.query(Product).filter(
        Product.product_id == request.product_id
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    gross_amount = product.price * request.quantity

    total_discount_amount = (
        request.coupon_discount_amount +
        request.membership_benefit_amount
    )

    net_amount = gross_amount - total_discount_amount

    order = Order(
        user_id=request.user_id,
        restaurant_id=request.restaurant_id,
        product_id=request.product_id,
        city=request.city,
        device_type=request.device_type,
        quantity=request.quantity,
        gross_amount=gross_amount,
        coupon_discount_amount=request.coupon_discount_amount,
        membership_benefit_amount=request.membership_benefit_amount,
        total_discount_amount=total_discount_amount,
        net_amount=net_amount,
        coupon_used_num=request.coupon_used_num,
        surge_num=request.surge_num,
        raining_num=request.raining_num,
        campaign_exposed_num=request.campaign_exposed_num,
        delivery_success_num=request.delivery_success_num,
        rating=request.rating,
        order_status="PLACED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    ml_input = {
        "city": request.city,
        "device_type": request.device_type,
        "gross_amount": gross_amount,
        "coupon_discount_amount": request.coupon_discount_amount,
        "membership_benefit_amount": request.membership_benefit_amount,
        "total_discount_amount": total_discount_amount,
        "net_amount": net_amount,
        "quantity": request.quantity,
        "rating": request.rating,
        "order_month": datetime.utcnow().month,
        "order_dayofweek": datetime.utcnow().weekday(),
        "coupon_used_num": request.coupon_used_num,
        "surge_num": request.surge_num,
        "raining_num": request.raining_num,
        "campaign_exposed_num": request.campaign_exposed_num,
        "delivery_success_num": request.delivery_success_num,
        "membership_tier": request.membership_tier,
        "restaurant_name": restaurant.restaurant_name,
        "product_name": product.product_name,
        "cuisine_tag": product.cuisine_tag,
        "coupon_name": request.coupon_name,
        "campaign_name": request.campaign_name,
        "channel": request.channel,
        "objective": request.objective,
    }

    prediction, probability, delay_risk, recommendation = predict_delay(ml_input)

    order_prediction = OrderPrediction(
        order_id=order.order_id,
        delay_prediction=prediction,
        delay_probability=probability,
        delay_risk=delay_risk,
        recommendation=recommendation
    )

    db.add(order_prediction)
    db.commit()

    return {
        "order_id": order.order_id,
        "order_status": order.order_status,
        "gross_amount": gross_amount,
        "net_amount": net_amount,
        "delay_prediction": prediction,
        "delay_risk": delay_risk,
        "delay_probability": probability,
        "recommendation": recommendation
    }


@app.get("/orders/user/{user_id}")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.order_id.desc()).all()

    result = []

    for order in orders:
        prediction = db.query(OrderPrediction).filter(
            OrderPrediction.order_id == order.order_id
        ).first()

        result.append({
            "order_id": order.order_id,
            "city": order.city,
            "gross_amount": order.gross_amount,
            "net_amount": order.net_amount,
            "order_status": order.order_status,
            "delay_risk": prediction.delay_risk if prediction else None,
            "delay_probability": prediction.delay_probability if prediction else None,
            "created_at": order.created_at
        })

    return result


@app.get("/admin/orders")
def get_admin_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.order_id.desc()).all()

    result = []

    for order in orders:
        prediction = db.query(OrderPrediction).filter(
            OrderPrediction.order_id == order.order_id
        ).first()

        result.append({
            "order_id": order.order_id,
            "user_id": order.user_id,
            "city": order.city,
            "gross_amount": order.gross_amount,
            "net_amount": order.net_amount,
            "raining_num": order.raining_num,
            "surge_num": order.surge_num,
            "delay_risk": prediction.delay_risk if prediction else None,
            "delay_probability": prediction.delay_probability if prediction else None,
            "recommendation": prediction.recommendation if prediction else None,
            "created_at": order.created_at
        })

    return result