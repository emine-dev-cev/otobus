import uuid
import random
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
from jose import JWTError, jwt
import httpx

from database import Base, engine, get_db
from models import Payment, PaymentStatus
from schemas import PaymentCreate, PaymentResponse
from kafka_producer import publish, stop_producer
from config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Bus Ticket App — Mock Payment Processing",
    version="1.0.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


@app.on_event("shutdown")
async def shutdown():
    await stop_producer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as e:
        print(f"[Payment] JWT Validation Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")
    except Exception as e:
        print(f"[Payment] Unexpected Auth Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token.")


@app.post("/payments", response_model=PaymentResponse, status_code=201, tags=["Payments"])
async def process_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    user_id = token_data["sub"]

    # Prevent duplicate payment
    existing = db.query(Payment).filter(
        Payment.booking_id == payload.booking_id,
        Payment.status == PaymentStatus.success,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu rezervasyon için ödeme zaten yapılmış.")

    # Payment processing — always successful as requested
    is_success = True
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    payment = Payment(
        booking_id=payload.booking_id,
        user_id=user_id,
        amount=payload.amount,
        method=payload.method,
        status=PaymentStatus.success if is_success else PaymentStatus.failed,
        transaction_id=transaction_id if is_success else None,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    if is_success:
        # Confirm booking status in booking service
        async with httpx.AsyncClient() as client:
            try:
                await client.patch(
                    f"{settings.booking_service_url}/bookings/{payload.booking_id}/status",
                    json={"status": "confirmed"},
                    headers={"Authorization": f"Bearer {_get_service_token()}"},
                    timeout=5.0,
                )
            except Exception:
                pass  # Non-blocking

        await publish("payment.success", {
            "payment_id": str(payment.id),
            "booking_id": str(payload.booking_id),
            "user_id": user_id,
            "amount": payment.amount,
            "transaction_id": transaction_id,
        })
    else:
        await publish("payment.failed", {
            "payment_id": str(payment.id),
            "booking_id": str(payload.booking_id),
            "user_id": user_id,
            "amount": payment.amount,
        })

    return payment


def _get_service_token() -> str:
    """Generate an internal service-to-service admin token."""
    from jose import jwt as jose_jwt
    from datetime import datetime, timedelta, timezone
    payload = {
        "sub": "service-account",
        "role": "admin",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    return jose_jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


@app.get("/payments/{booking_id}", response_model=PaymentResponse, tags=["Payments"])
def get_payment(
    booking_id: UUID,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user),
):
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).order_by(
        Payment.created_at.desc()
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Ödeme kaydı bulunamadı.")
    if str(payment.user_id) != token_data["sub"] and token_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Erişim yetkisi yok.")
    return payment


@app.get("/payments/health", tags=["Health"])
@app.get("/payments/health/", tags=["Health"], include_in_schema=False)
def health():
    return {"status": "ok", "service": "payment-service"}
