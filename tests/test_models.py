from sqlalchemy import inspect

from app.models.customer import Customer
from app.models.plan import Plan
from app.models.subscription import Subscription


def test_customer_table_name() -> None:
    assert Customer.__tablename__ == "customers"


def test_plan_table_name() -> None:
    assert Plan.__tablename__ == "plans"


def test_subscription_table_name() -> None:
    assert Subscription.__tablename__ == "subscriptions"


def test_subscription_foreign_keys() -> None:
    mapper = inspect(Subscription)

    customer_id = mapper.columns.customer_id
    plan_id = mapper.columns.plan_id

    customer_fk = next(iter(customer_id.foreign_keys))
    plan_fk = next(iter(plan_id.foreign_keys))

    assert customer_fk.target_fullname == "customers.id"
    assert plan_fk.target_fullname == "plans.id"
