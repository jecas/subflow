from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing() -> None:
    password = "very-secret-password"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_access_token_round_trip() -> None:
    customer_id = uuid4()

    token = create_access_token(customer_id)

    assert decode_access_token(token) == customer_id
