from app.schemas.webhook import PaymentWebhook


def test_payment_webhook_defaults_data_to_empty_dict() -> None:
    event = PaymentWebhook(
        event_id="evt_1",
        event_type="payment.succeeded",
        payment_id="pay_1",
    )

    assert event.data == {}
