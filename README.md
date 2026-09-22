# SubFlow

SubFlow is a portfolio-grade subscription management backend built with Python and FastAPI. It demonstrates API design, async persistence, authentication and authorization, Redis caching, subscription lifecycle rules, payment-provider abstraction, webhook idempotency, migrations, structured logging, Docker and CI.

## Architecture

```text
Client
  |
FastAPI
  |-- JWT / RBAC
  |-- Plans -------- Redis cache
  |-- Subscriptions
  |-- Payments ----- PaymentProvider -> MockPaymentProvider
  |-- Webhooks ----- idempotent event store
  |
PostgreSQL
```

## Features

- Customer registration and JSON login
- JWT Bearer authentication
- Customer/Admin authorization
- Plan administration
- Redis cache-aside for active plans with TTL and invalidation
- Subscription creation, cancellation, plan changes, renewal and expiration
- Calendar-aware monthly/yearly billing periods
- Payment provider abstraction with a deterministic local mock
- Payment webhook processing with duplicate-event protection
- PostgreSQL + SQLAlchemy async
- Alembic migrations
- Structured JSON request logs and `X-Request-ID`
- Ruff, pytest and GitHub Actions
- Docker Compose for API + PostgreSQL + Redis

## Run with Docker

```bash
docker compose up --build
```

The API is available at `http://localhost:8000` and Swagger at `/docs`.

## Migrations

```bash
docker compose exec api alembic upgrade head
```

## Tests

```bash
pytest -v
ruff check .
```

## Important API flows

```text
POST /api/v1/auth/register
POST /api/v1/auth/login

GET  /api/v1/plans

POST /api/v1/subscriptions
GET  /api/v1/subscriptions/me
POST /api/v1/subscriptions/{id}/cancel
POST /api/v1/subscriptions/{id}/change-plan
POST /api/v1/subscriptions/{id}/payments

POST /api/v1/webhooks/payments

POST /api/v1/admin/subscriptions/{id}/renew
POST /api/v1/admin/subscriptions/{id}/expire
```

## Design notes

Redis is an optimization rather than a source of truth. Cache failures fall back to PostgreSQL. Plan mutations invalidate the active-plan cache.

Payment handling is behind a provider protocol so a real provider can be introduced without coupling subscription business logic to one vendor.

Webhook event IDs are persisted before processing. Repeated delivery of the same provider event is therefore treated as a duplicate instead of applying the event twice.

## Portfolio purpose

SubFlow is intentionally vendor-neutral and self-contained. It is designed to demonstrate production backend patterns without depending on proprietary systems or paid third-party services.
