import hashlib
import uuid
from hmac import HMAC
from typing import Any

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select

from app import models, schemas
from app.core.config import settings
from app.core.dependecies import AsyncSession
from app.core.security import get_password_hash, verify_password


async def get_user_by_email(session: AsyncSession, email: str) -> models.User | None:
    query = select(models.User).where(models.User.email == email)
    return (await session.execute(query)).scalar_one_or_none()


async def create_user(session: AsyncSession, email: str, password: str) -> models.User:
    new_user = models.User(email=email, hashed_password=get_password_hash(password))
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> schemas.User | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return schemas.User(**user.__dict__)


async def create_new_user(session: AsyncSession, email: str, password: str) -> schemas.User | None:
    user = await get_user_by_email(session, email)
    if user:
        return None
    user = await create_user(session, email, password)
    if not user:
        return None
    return schemas.User(**user.__dict__)


async def create_payment(
    session: AsyncSession, user: models.User | None, amount: float, description: str
) -> models.Payment:
    payment = models.Payment(id=uuid.uuid4(), amount=amount, user_id=user.id if user else None, description=description)
    session.add(payment)
    await session.commit()
    return payment


def create_payment_body(email: str, username: str, payment: models.Payment, user: models.User | None) -> dict[str, Any]:
    body = {
        "project_id": settings.payment_project_id,
        "payment_id": str(payment.id),
        "name": "Оплата заказа",
        "description": f"{username} - {payment.description}",
        "mode": settings.payment_mode,
        "sum": payment.amount,
        "currency": "RUB",
        "customer": {
            "phone": user.phone if user else "",
            "email": user.email if user else email,
        },
    }
    try:
        schemas.PaymentRequest.model_validate(body)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't create valid payment request body: {e}",
        )
    return body


# TODO: add proper logging when erros happens
async def get_payment_url(session: AsyncSession, email: str, username: str, amount: float, description: str) -> str:
    user = await get_user_by_email(session, email)
    payment = await create_payment(session, user, amount, description)
    body = create_payment_body(email, username, payment, user)
    async with httpx.AsyncClient() as client:
        res = await client.post("https://pay.superhub.host/api/v1/payments", json=body)
        if res.is_error:
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


def create_hmac_message(payment: schemas.PaymentNotificationRequest) -> str:
    parts = [
        f"{payment.uuid}",
        f"{payment.external_id}",
        f"{payment.sum:.2f}",
        f"{payment.currency}",
        f"{payment.provider_name}",
        f"{payment.method_name}",
        f"{payment.status}",
        f"{payment.mode}",
    ]
    return ":".join(parts)


async def validate_signature(
    session: AsyncSession, payment: schemas.PaymentNotificationRequest, signature: str
) -> bool:
    if payment.mode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment with test mode not valid",
        )
    if payment.status != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment status not valid",
        )
    db_payment = await session.get(models.Payment, payment.external_id)
    if not db_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment with this id didn't exist",
        )
    if db_payment.status == 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already paid",
        )
    message = create_hmac_message(payment)
    hmac = HMAC(settings.payment_secret_key.encode(), message.encode(), hashlib.sha256)
    return hmac.hexdigest() == signature


async def update_payment(session: AsyncSession, payment: schemas.PaymentNotificationRequest) -> None:
    db_payment = await session.get(models.Payment, payment.external_id)
    if not db_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment with this id didn't exist",
        )
    db_payment.status = payment.status
    await session.commit()
