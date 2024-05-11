import pytest
from pytest_mock import MockerFixture

from app.core.config import settings
from app.core.dependecies import AsyncSession
from app.models import Payment
from app.schemas import PaymentNotificationRequest
from app.services import create_hmac_message, validate_signature


def test_create_hmac_message(payment: PaymentNotificationRequest) -> None:
    message = create_hmac_message(payment)

    assert message == f"{payment.uuid}:{payment.external_id}:{payment.sum:.2f}:{payment.currency}:{payment.provider_name}:{payment.method_name}:{payment.status}:{payment.mode}"  # fmt: skip # noqa: E501


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("signature", "valid"),
    [
        ("123456789abcdef", False),
    ],
)
async def test_validate_signature(
    mocker: MockerFixture, payment: PaymentNotificationRequest, signature: str, valid: bool
) -> None:
    mocker.patch.object(AsyncSession, "get", return_value=Payment(status=0))
    mocker.patch.object(settings, "payment_secret_key", "abc")

    is_valid = await validate_signature(AsyncSession(), payment, signature)

    assert is_valid == valid
