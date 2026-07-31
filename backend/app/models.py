from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    membership_tier = Column(String, default="NONE")
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    address_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    receiver_name = Column(String, nullable=False)
    receiver_phone = Column(String, default="")
    address_label = Column(String, default="Home")

    address_line = Column(String, nullable=False)
    area = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    is_default = Column(Integer, default=0)
    order_for_someone_else_flag = Column(Integer, default=0)
    receiver_type = Column(String, default="Self")

    created_at = Column(DateTime, default=datetime.utcnow)


class Restaurant(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, index=True)

    restaurant_name = Column(String, nullable=False)
    cuisine_tag = Column(String, nullable=False)
    city = Column(String, nullable=False)

    location_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    area = Column(String)
    pincode = Column(String)

    restaurant_latitude = Column(Float, nullable=False)
    restaurant_longitude = Column(Float, nullable=False)

    rating = Column(Float, default=4.2)
    cost_for_two = Column(Float, default=400)
    default_prep_minutes = Column(Integer, default=25)
    is_active = Column(Integer, default=1)
    location_source = Column(String, default="seed")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))

    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cuisine_tag = Column(String, nullable=False)
    food_type = Column(String, default="Veg")
    description = Column(String, default="")
    is_available = Column(Integer, default=1)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"))
    address_id = Column(Integer, ForeignKey("customer_addresses.address_id"), nullable=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))

    receiver_name = Column(String)
    receiver_type = Column(String)
    delivery_address = Column(String)

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
    auto_raining_flag = Column(Integer)
    campaign_exposed_num = Column(Integer)
    delivery_success_num = Column(Integer)

    rating = Column(Float)

    customer_latitude = Column(Float)
    customer_longitude = Column(Float)
    customer_location_name = Column(String)
    customer_area = Column(String)
    customer_city_name = Column(String)
    customer_state_name = Column(String)
    customer_zone = Column(String)

    restaurant_latitude = Column(Float)
    restaurant_longitude = Column(Float)
    restaurant_location_name = Column(String)
    restaurant_area = Column(String)
    restaurant_city_name = Column(String)

    distance_km = Column(Float)
    distance_bucket = Column(String)
    estimated_travel_minutes = Column(Float)

    temperature = Column(Float)
    precipitation_mm = Column(Float)
    weather_code = Column(Integer)
    weather_condition = Column(String)
    weather_severity = Column(String)
    wind_speed = Column(Float)

    operational_scenario = Column(String)

    order_status = Column(String, default="PLACED")
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderPrediction(Base):
    __tablename__ = "order_predictions"

    prediction_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))

    model_version = Column(String)
    delay_prediction = Column(Integer)
    delay_risk = Column(String)
    delay_probability = Column(Float)
    recommendation = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)