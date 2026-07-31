from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    name: str
    email: str
    membership_tier: str = "NONE"


class AddressRequest(BaseModel):
    user_id: int
    receiver_name: str
    receiver_phone: str = ""
    address_label: str = "Home"

    address_line: str
    area: str
    city: str
    state: str = "Telangana"
    pincode: str = ""

    latitude: float
    longitude: float

    is_default: int = 0
    order_for_someone_else_flag: int = 0
    receiver_type: str = "Self"


class OrderRequest(BaseModel):
    user_id: int
    restaurant_id: int
    product_id: int

    address_id: Optional[int] = None

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

    customer_latitude: Optional[float] = None
    customer_longitude: Optional[float] = None