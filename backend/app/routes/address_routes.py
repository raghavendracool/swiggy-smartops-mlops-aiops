from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import CustomerAddress, User
from backend.app.schemas import AddressRequest
from backend.app.services.location_service import reverse_geocode_location

router = APIRouter(prefix="", tags=["Addresses"])


@router.get("/location/reverse")
def reverse_location(latitude: float = Query(...), longitude: float = Query(...)):
    return reverse_geocode_location(latitude, longitude)


@router.post("/addresses")
def create_address(request: AddressRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == request.user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if request.is_default == 1:
        db.query(CustomerAddress).filter(
            CustomerAddress.user_id == request.user_id
        ).update({"is_default": 0})

    address = CustomerAddress(
        user_id=request.user_id,
        receiver_name=request.receiver_name,
        receiver_phone=request.receiver_phone,
        address_label=request.address_label,
        address_line=request.address_line,
        area=request.area,
        city=request.city,
        state=request.state,
        pincode=request.pincode,
        latitude=request.latitude,
        longitude=request.longitude,
        is_default=request.is_default,
        order_for_someone_else_flag=request.order_for_someone_else_flag,
        receiver_type=request.receiver_type,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address_to_dict(address)


@router.get("/addresses/user/{user_id}")
def get_user_addresses(user_id: int, db: Session = Depends(get_db)):
    addresses = db.query(CustomerAddress).filter(
        CustomerAddress.user_id == user_id
    ).order_by(
        CustomerAddress.is_default.desc(),
        CustomerAddress.address_id.desc()
    ).all()

    return [address_to_dict(address) for address in addresses]


def address_to_dict(address: CustomerAddress):
    return {
        "address_id": address.address_id,
        "user_id": address.user_id,
        "receiver_name": address.receiver_name,
        "receiver_phone": address.receiver_phone,
        "address_label": address.address_label,
        "address_line": address.address_line,
        "area": address.area,
        "city": address.city,
        "state": address.state,
        "pincode": address.pincode,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "is_default": address.is_default,
        "order_for_someone_else_flag": address.order_for_someone_else_flag,
        "receiver_type": address.receiver_type,
    }