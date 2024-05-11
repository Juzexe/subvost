from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.schemas import PaymentNotificationRequest


@pytest.fixture()
def client() -> TestClient:
    from app.main import create_app

    return TestClient(create_app())


@pytest.fixture()
def payment() -> PaymentNotificationRequest:
    return PaymentNotificationRequest(
        name="Test payment",
        description="Haha",
        mode=0,
        sum=69.0,
        currency="RUB",
        uuid=uuid4(),
        external_id=uuid4(),
        provider_name="sber",
        method_name="card",
        status=2,
        created_at=datetime.now(),
    )
