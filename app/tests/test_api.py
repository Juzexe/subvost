from fastapi import status
from fastapi.testclient import TestClient


def test_payment_html(client: TestClient) -> None:
    res = client.get("/payment")

    assert res.status_code == status.HTTP_200_OK
    assert "<!DOCTYPE html>" in res.text
