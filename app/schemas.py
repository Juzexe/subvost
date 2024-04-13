from datetime import datetime

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


class PaymentInfo(BaseModel):
    pay_url: str
