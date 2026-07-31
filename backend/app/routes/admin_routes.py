from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Order, OrderPrediction
from backend.app.routes.order_routes import order_to_dict

router = APIRouter(prefix="", tags=["Admin"])


@router.get("/admin/orders")
def get_admin_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.order_id.desc()).all()

    result = []

    for order in orders:
        prediction = db.query(OrderPrediction).filter(
            OrderPrediction.order_id == order.order_id
        ).first()

        result.append(order_to_dict(order, prediction))

    return result