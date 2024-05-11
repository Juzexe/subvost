from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    email: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    expire: datetime
    token_type: str = "bearer"


class PaymentResponse(BaseModel):
    pay_url: str


class Customer(BaseModel):
    email: str
    phone: str


class PaymentInfoBase(BaseModel):
    name: str
    description: str
    mode: int
    sum: float
    currency: str


class PaymentRequest(PaymentInfoBase):
    project_id: str
    payment_id: UUID
    customer: Customer


class PaymentNotificationRequest(PaymentInfoBase):
    uuid: UUID
    external_id: UUID
    provider_name: str
    method_name: str
    created_at: datetime
    status: int
