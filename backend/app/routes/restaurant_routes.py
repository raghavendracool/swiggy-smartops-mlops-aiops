from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Product, Restaurant

router = APIRouter(prefix="", tags=["Restaurants"])


@router.get("/restaurants")
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).filter(Restaurant.is_active == 1).all()

    return [
        {
            "restaurant_id": r.restaurant_id,
            "restaurant_name": r.restaurant_name,
            "cuisine_tag": r.cuisine_tag,
            "city": r.city,
            "location_name": r.location_name,
            "address": r.address,
            "area": r.area,
            "pincode": r.pincode,
            "restaurant_latitude": r.restaurant_latitude,
            "restaurant_longitude": r.restaurant_longitude,
            "rating": r.rating,
            "cost_for_two": r.cost_for_two,
            "default_prep_minutes": r.default_prep_minutes,
        }
        for r in restaurants
    ]


@router.get("/restaurants/{restaurant_id}/products")
def get_products(restaurant_id: int, db: Session = Depends(get_db)):
    products = db.query(Product).filter(
        Product.restaurant_id == restaurant_id,
        Product.is_available == 1
    ).all()

    return [
        {
            "product_id": p.product_id,
            "restaurant_id": p.restaurant_id,
            "product_name": p.product_name,
            "price": p.price,
            "cuisine_tag": p.cuisine_tag,
            "food_type": p.food_type,
            "description": p.description,
        }
        for p in products
    ]