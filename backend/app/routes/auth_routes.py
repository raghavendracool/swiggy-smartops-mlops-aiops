from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import LoginRequest

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/login")
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