from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Order, OrderPrediction
from backend.app.services.business_insights_service import (
    get_area_risk_records,
    get_coupon_recommendation_records,
    get_customer_retention_records,
    get_mlops_business_summary,
    get_restaurant_risk_records,
)

router = APIRouter(prefix="", tags=["MLOps Business Dashboard"])


@router.get("/admin/mlops/summary")
def get_admin_mlops_summary(db: Session = Depends(get_db)):
    offline_summary = get_mlops_business_summary()

    orders = db.query(Order).all()
    predictions = db.query(OrderPrediction).all()

    prediction_map = {
        prediction.order_id: prediction
        for prediction in predictions
    }

    total_live_orders = len(orders)

    high_risk_orders = 0
    critical_orders = 0
    revenue_at_risk = 0
    delay_probability_sum = 0
    probability_count = 0
    rain_orders = 0
    long_distance_orders = 0
    someone_else_orders = 0

    for order in orders:
        prediction = prediction_map.get(order.order_id)

        if order.raining_num == 1:
            rain_orders += 1

        if order.distance_km and order.distance_km > 8:
            long_distance_orders += 1

        if order.receiver_type and order.receiver_type != "Self":
            someone_else_orders += 1

        if prediction:
            delay_probability_sum += prediction.delay_probability or 0
            probability_count += 1

            if prediction.delay_risk == "High Delay Risk":
                high_risk_orders += 1
                revenue_at_risk += order.net_amount or 0

            if prediction.delay_probability and prediction.delay_probability >= 0.80:
                critical_orders += 1

    avg_delay_probability = (
        delay_probability_sum / probability_count
        if probability_count > 0
        else 0
    )

    return {
        "live_orders": {
            "total_live_orders": total_live_orders,
            "high_risk_orders": high_risk_orders,
            "critical_orders": critical_orders,
            "rain_orders": rain_orders,
            "long_distance_orders": long_distance_orders,
            "someone_else_orders": someone_else_orders,
            "avg_delay_probability": round(avg_delay_probability, 4),
            "revenue_at_risk": round(revenue_at_risk, 2),
        },
        "offline_business_summary": offline_summary,
    }


@router.get("/admin/mlops/customer-retention")
def get_customer_retention(
    limit: int = Query(100),
    risk: str = Query("All")
):
    return get_customer_retention_records(limit=limit, risk=risk)


@router.get("/admin/mlops/coupon-recommendations")
def get_coupon_recommendations(limit: int = Query(100)):
    return get_coupon_recommendation_records(limit=limit)


@router.get("/admin/mlops/restaurant-risk")
def get_restaurant_risk(limit: int = Query(100)):
    return get_restaurant_risk_records(limit=limit)


@router.get("/admin/mlops/area-risk")
def get_area_risk(limit: int = Query(100)):
    return get_area_risk_records(limit=limit)