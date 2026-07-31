from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.config import MODEL_VERSION
from backend.app.database import get_db
from backend.app.models import (
    CustomerAddress,
    Order,
    OrderPrediction,
    Product,
    Restaurant,
)
from backend.app.schemas import OrderRequest
from backend.app.services.distance_service import (
    estimate_travel_minutes,
    get_distance_bucket,
    haversine_distance_km,
)
from backend.app.services.location_service import reverse_geocode_location
from backend.app.services.ml_service import predict_delay
from backend.app.services.weather_service import fetch_weather

router = APIRouter(prefix="", tags=["Orders"])


@router.post("/orders")
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

    selected_address = None

    if request.address_id is not None:
        selected_address = db.query(CustomerAddress).filter(
            CustomerAddress.address_id == request.address_id,
            CustomerAddress.user_id == request.user_id
        ).first()

        if selected_address is None:
            raise HTTPException(status_code=404, detail="Selected address not found")

        customer_latitude = selected_address.latitude
        customer_longitude = selected_address.longitude
        customer_area = selected_address.area
        customer_city = selected_address.city
        customer_state = selected_address.state
        customer_zone = selected_address.area
        customer_location_name = selected_address.address_line
        receiver_name = selected_address.receiver_name
        receiver_type = selected_address.receiver_type
        delivery_address = selected_address.address_line
        order_for_someone_else_flag = selected_address.order_for_someone_else_flag

    else:
        customer_latitude = request.customer_latitude or restaurant.restaurant_latitude
        customer_longitude = request.customer_longitude or restaurant.restaurant_longitude

        customer_location = reverse_geocode_location(
            customer_latitude,
            customer_longitude
        )

        customer_area = customer_location["area"]
        customer_city = customer_location["city"]
        customer_state = customer_location["state"]
        customer_zone = customer_location["area"]
        customer_location_name = customer_location["display_name"]
        receiver_name = "Self"
        receiver_type = "Self"
        delivery_address = customer_location_name
        order_for_someone_else_flag = 0

    distance_km = haversine_distance_km(
        customer_latitude,
        customer_longitude,
        restaurant.restaurant_latitude,
        restaurant.restaurant_longitude
    )

    distance_bucket = get_distance_bucket(distance_km)

    weather = fetch_weather(
        customer_latitude,
        customer_longitude,
        fallback_raining_num=request.raining_num
    )

    automatic_raining_num = weather["raining_num"]

    estimated_travel_minutes = estimate_travel_minutes(
        distance_km=distance_km,
        raining_num=automatic_raining_num,
        surge_num=request.surge_num
    )

    gross_amount = product.price * request.quantity

    total_discount_amount = (
        request.coupon_discount_amount +
        request.membership_benefit_amount
    )

    net_amount = gross_amount - total_discount_amount

    operational_scenario = get_operational_scenario(
        automatic_raining_num=automatic_raining_num,
        distance_km=distance_km,
        surge_num=request.surge_num,
        order_for_someone_else_flag=order_for_someone_else_flag
    )

    ml_input = {
        "city_clean": restaurant.city,
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
        "raining_num": automatic_raining_num,
        "auto_raining_flag": automatic_raining_num,
        "campaign_exposed_num": request.campaign_exposed_num,
        "delivery_success_num": request.delivery_success_num,
        "order_for_someone_else_flag": order_for_someone_else_flag,

        "customer_area": customer_area,
        "customer_zone": customer_zone,
        "customer_latitude": customer_latitude,
        "customer_longitude": customer_longitude,

        "restaurant_area": restaurant.area,
        "restaurant_latitude": restaurant.restaurant_latitude,
        "restaurant_longitude": restaurant.restaurant_longitude,

        "distance_km": distance_km,
        "distance_bucket": distance_bucket,
        "estimated_travel_minutes": estimated_travel_minutes,

        "weather_condition": weather["weather_condition"],
        "weather_severity": weather["weather_severity"],
        "temperature": weather["temperature"],
        "precipitation_mm": weather["precipitation_mm"],
        "wind_speed": weather["wind_speed"],

        "receiver_type": receiver_type,
        "operational_scenario": operational_scenario,

        "membership_tier": request.membership_tier,
        "assigned_nearby_restaurant_name": restaurant.restaurant_name,
        "assigned_restaurant_cuisine": product.cuisine_tag,
        "restaurant_location_name": restaurant.location_name,

        "coupon_name": request.coupon_name,
        "campaign_name": request.campaign_name,
        "channel": request.channel,
        "objective": request.objective,
    }

    prediction_result = predict_delay(ml_input)

    recommendation = prediction_result["recommendation"]

    if automatic_raining_num == 1:
        recommendation += " | Weather impact detected."

    if distance_km > 8:
        recommendation += " | Long-distance delivery route."

    if order_for_someone_else_flag == 1:
        recommendation += " | Delivery address is not customer's default/current address."

    order = Order(
        user_id=request.user_id,
        address_id=request.address_id,
        restaurant_id=request.restaurant_id,
        product_id=request.product_id,

        receiver_name=receiver_name,
        receiver_type=receiver_type,
        delivery_address=delivery_address,

        city=restaurant.city,
        device_type=request.device_type,
        quantity=request.quantity,

        gross_amount=gross_amount,
        coupon_discount_amount=request.coupon_discount_amount,
        membership_benefit_amount=request.membership_benefit_amount,
        total_discount_amount=total_discount_amount,
        net_amount=net_amount,

        coupon_used_num=request.coupon_used_num,
        surge_num=request.surge_num,
        raining_num=automatic_raining_num,
        auto_raining_flag=automatic_raining_num,
        campaign_exposed_num=request.campaign_exposed_num,
        delivery_success_num=request.delivery_success_num,
        rating=request.rating,

        customer_latitude=customer_latitude,
        customer_longitude=customer_longitude,
        customer_location_name=customer_location_name,
        customer_area=customer_area,
        customer_city_name=customer_city,
        customer_state_name=customer_state,
        customer_zone=customer_zone,

        restaurant_latitude=restaurant.restaurant_latitude,
        restaurant_longitude=restaurant.restaurant_longitude,
        restaurant_location_name=restaurant.location_name,
        restaurant_area=restaurant.area,
        restaurant_city_name=restaurant.city,

        distance_km=distance_km,
        distance_bucket=distance_bucket,
        estimated_travel_minutes=estimated_travel_minutes,

        temperature=weather["temperature"],
        precipitation_mm=weather["precipitation_mm"],
        weather_code=weather["weather_code"],
        weather_condition=weather["weather_text"],
        weather_severity=weather["weather_severity"],
        wind_speed=weather["wind_speed"],

        operational_scenario=operational_scenario,
        order_status="PLACED",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    order_prediction = OrderPrediction(
        order_id=order.order_id,
        model_version=MODEL_VERSION,
        delay_prediction=prediction_result["delay_prediction"],
        delay_probability=prediction_result["delay_probability"],
        delay_risk=prediction_result["delay_risk"],
        recommendation=recommendation,
    )

    db.add(order_prediction)
    db.commit()

    return {
        "order_id": order.order_id,
        "order_status": order.order_status,
        "restaurant_name": restaurant.restaurant_name,
        "product_name": product.product_name,
        "receiver_name": receiver_name,
        "receiver_type": receiver_type,
        "delivery_address": delivery_address,

        "gross_amount": gross_amount,
        "net_amount": net_amount,

        "customer_area": customer_area,
        "customer_city_name": customer_city,
        "restaurant_location_name": restaurant.location_name,
        "restaurant_area": restaurant.area,

        "distance_km": distance_km,
        "distance_bucket": distance_bucket,
        "estimated_travel_minutes": estimated_travel_minutes,

        "weather": weather["weather_text"],
        "weather_condition": weather["weather_condition"],
        "weather_severity": weather["weather_severity"],
        "temperature": weather["temperature"],
        "precipitation_mm": weather["precipitation_mm"],
        "wind_speed": weather["wind_speed"],
        "raining_num": automatic_raining_num,
        "weather_api_status": weather["weather_api_status"],

        "operational_scenario": operational_scenario,

        "model_version": MODEL_VERSION,
        "delay_prediction": prediction_result["delay_prediction"],
        "delay_risk": prediction_result["delay_risk"],
        "delay_probability": prediction_result["delay_probability"],
        "recommendation": recommendation,
    }


@router.get("/orders/user/{user_id}")
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.order_id.desc()).all()

    result = []

    for order in orders:
        prediction = db.query(OrderPrediction).filter(
            OrderPrediction.order_id == order.order_id
        ).first()

        result.append(order_to_dict(order, prediction))

    return result


def get_operational_scenario(
    automatic_raining_num,
    distance_km,
    surge_num,
    order_for_someone_else_flag
):
    if automatic_raining_num == 1 and distance_km > 8 and surge_num == 1:
        return "Rain + Long Distance + Surge"

    if automatic_raining_num == 1 and distance_km <= 3:
        return "Rain + Nearby"

    if automatic_raining_num == 0 and distance_km > 8:
        return "Non-rain + Long Distance"

    if order_for_someone_else_flag == 1:
        return "Order For Someone Else"

    if surge_num == 1 and distance_km > 7:
        return "Surge + Medium/Far Distance"

    return "Normal Order"


def order_to_dict(order: Order, prediction: OrderPrediction | None):
    return {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "city": order.city,
        "receiver_name": order.receiver_name,
        "receiver_type": order.receiver_type,
        "delivery_address": order.delivery_address,
        "gross_amount": order.gross_amount,
        "net_amount": order.net_amount,
        "order_status": order.order_status,
        "customer_area": order.customer_area,
        "customer_city_name": order.customer_city_name,
        "restaurant_location_name": order.restaurant_location_name,
        "restaurant_area": order.restaurant_area,
        "distance_km": order.distance_km,
        "distance_bucket": order.distance_bucket,
        "estimated_travel_minutes": order.estimated_travel_minutes,
        "weather_condition": order.weather_condition,
        "weather_severity": order.weather_severity,
        "temperature": order.temperature,
        "precipitation_mm": order.precipitation_mm,
        "raining_num": order.raining_num,
        "surge_num": order.surge_num,
        "operational_scenario": order.operational_scenario,
        "model_version": prediction.model_version if prediction else None,
        "delay_risk": prediction.delay_risk if prediction else None,
        "delay_probability": prediction.delay_probability if prediction else None,
        "recommendation": prediction.recommendation if prediction else None,
        "created_at": order.created_at,
    }