import uuid
from typing import TYPE_CHECKING

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select

from app import models, schemas
from app.core.config import settings
from app.core.security import verify_password

if TYPE_CHECKING:
    from app.core.dependecies import AsyncSession


async def get_user_by_email(session: "AsyncSession", email: str) -> models.User | None:
    query = select(models.User).where(models.User.email == email)
    return (await session.execute(query)).scalar_one_or_none()


async def authenticate_user(session: "AsyncSession", email: str, password: str) -> schemas.User | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return schemas.User(**user.__dict__)


async def create_payment(
    session: "AsyncSession", user: models.User | None, amount: float, description: str
) -> models.Payment:
    payment = models.Payment(id=uuid.uuid4(), amount=amount, user_id=user.id if user else None, description=description)
    session.add(payment)
    await session.commit()
    return payment


# TODO: add proper logging when erros happens
async def get_payment_url(session: "AsyncSession", email: str, username: str, amount: float, description: str) -> str:
    user = await get_user_by_email(session, email)
    payment = await create_payment(session, user, amount, description)
    body = {
        "project_id": settings.project_id,
        "payment_id": str(payment.id),
        "name": "Оплата заказа",
        "description": f"{username} - {payment.description}",
        "mode": settings.payment_mode,
        "sum": payment.amount,
        "currency": "RUB",
        "customer": {
            "phone": user.phone if user else "",
            "email": user.email if user else "",
        },
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://pay.superhub.host/api/v1/payments", json=body)
        if not res.is_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Can't make payment request",
            )
        url = res.json().get("response", {}).get("pay_url")
        if not url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment doesn't return url",
            )
        return url
