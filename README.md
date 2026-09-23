# SubFlow
[![Tests](https://github.com/jecas/subflow/actions/workflows/tests.yml/badge.svg)](https://github.com/jecas/subflow/actions/workflows/tests.yml)

SubFlow is a production-style asynchronous subscription management backend built with Python and FastAPI.

The project demonstrates how I design and structure backend services with clear separation between API, business logic, persistence, caching, external providers, and infrastructure concerns.

It includes authentication, role-based authorization, subscription lifecycle management, Redis caching, idempotent payment processing, protected webhooks, database migrations, structured logging, automated testing, Docker, and CI.

## Architecture

```text
                         ┌──────────────┐
                         │    Client    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   FastAPI    │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
         JWT / RBAC        Business Logic     Request Logging
                              Services
              │                 │
              │        ┌────────┼────────┐
              │        │        │        │
              │        ▼        ▼        ▼
              │      Plans   Subscriptions Payments
              │        │                 │
              │        ▼                 ▼
              │      Redis       PaymentProvider
              │                      │
              │                      ▼
              │              MockPaymentProvider
              │
              └─────────────────┬─────────────────
                                │
                                ▼
                          PostgreSQL
                                ▲
                                │
                         Webhook Events
```

## Features

### Authentication & Authorization

- Customer registration
- JSON-based login
- JWT Bearer authentication
- Customer and administrator roles
- Protected customer and admin endpoints

### Subscription Management

- Create subscriptions
- Cancel at the end of the billing period
- Change subscription plans
- Renew subscriptions
- Expire subscriptions
- Calendar-aware monthly and yearly billing periods
- Ownership and subscription-state validation

### Payments

- Payment provider abstraction
- Mock payment provider for local development and testing
- Payment persistence
- `Idempotency-Key` support
- Duplicate payment prevention
- Database-level idempotency protection

### Webhooks

- Payment webhook processing
- Shared-secret authentication
- Duplicate-event detection
- Persistent webhook event store
- Database-level duplicate protection

### Caching

Active plans use a Redis cache-aside strategy.

PostgreSQL remains the source of truth. If Redis is unavailable, requests fall back to PostgreSQL instead of failing.

Plan mutations invalidate the active-plan cache.

### Observability

- Structured JSON request logs
- `X-Request-ID` propagation
- Request duration
- HTTP method, path, and status logging

## Tech Stack

**Backend**

Python 3.12 · FastAPI · Pydantic

**Database**

PostgreSQL · SQLAlchemy Async · Alembic

**Caching**

Redis

**Testing & Quality**

Pytest · Ruff · Unit Tests · Integration Tests

**Infrastructure**

Docker · Docker Compose · GitHub Actions

## Project Structure

```text
app/
├── api/
│   ├── dependencies.py
│   └── routes/
├── cache/
├── core/
├── db/
├── models/
├── providers/
├── repositories/
├── schemas/
└── services/

alembic/
tests/
├── integration/
└── ...
```

The application follows a layered structure:

```text
API Routes
    ↓
Services
    ↓
Repositories
    ↓
SQLAlchemy
    ↓
PostgreSQL
```

External payment behavior is isolated behind a provider abstraction.

## Run with Docker

### Requirements

- Docker
- Docker Compose

Start the complete environment:

```bash
docker compose up --build
```

This starts:

- SubFlow API
- PostgreSQL
- Redis

The API is available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Database Migrations

Migrations are managed with Alembic.

Apply all migrations:

```bash
docker compose exec api alembic upgrade head
```

Migration history currently covers the initial application schema, payment and webhook persistence, and payment idempotency.

## Tests

Run the complete test suite:

```bash
pytest -v
```

Run integration tests:

```bash
pytest -v tests/integration
```

Run linting:

```bash
ruff check .
```

## CI Pipeline

GitHub Actions validates every change by running:

```text
Ruff
  ↓
Alembic upgrade
  ↓
Alembic downgrade
  ↓
Alembic upgrade
  ↓
Unit tests
  ↓
Integration tests
  ↓
Docker image build
```

This verifies both application behavior and database migration reversibility.

## API Overview

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Plans

```text
GET /api/v1/plans
```

### Subscriptions

```text
POST /api/v1/subscriptions
GET  /api/v1/subscriptions/me

POST /api/v1/subscriptions/{id}/cancel
POST /api/v1/subscriptions/{id}/change-plan
POST /api/v1/subscriptions/{id}/payments
```

Payment requests require:

```text
Idempotency-Key: <unique-key>
```

Repeating the same payment request with the same key returns the existing payment instead of creating another charge.

### Webhooks

```text
POST /api/v1/webhooks/payments
```

Webhook requests require:

```text
X-Webhook-Secret: <configured-secret>
```

Webhook event IDs are persisted and duplicate deliveries are not processed twice.

### Administration

```text
POST /api/v1/admin/plans
PATCH /api/v1/admin/plans/{id}

GET  /api/v1/admin/customers
GET  /api/v1/admin/subscriptions

POST /api/v1/admin/subscriptions/{id}/renew
POST /api/v1/admin/subscriptions/{id}/expire
```

## Design Decisions

### PostgreSQL is the source of truth

Redis is used only as an optimization. Cache failures do not make the plans API unavailable.

### Payment providers are isolated

Payment processing is defined behind a provider protocol.

```text
PaymentService
      │
      ▼
PaymentProvider
      │
      ├── MockPaymentProvider
      │
      └── Future external provider
```

This keeps provider-specific behavior outside the core subscription logic.

### Payments are idempotent

Clients provide an `Idempotency-Key`.

The key is persisted with a unique database constraint, preventing duplicate payment records for repeated requests.

### Webhooks are idempotent

Provider event IDs are stored in PostgreSQL.

Repeated delivery of an already processed event is detected and does not apply the event twice.

### Database migrations are tested in both directions

CI performs:

```text
upgrade → downgrade → upgrade
```

before running the test suite.

This helps detect migration problems before changes are merged.

## Portfolio Purpose

SubFlow is vendor-neutral and self-contained.

It was built to demonstrate production backend engineering patterns without relying on proprietary code, internal systems, or paid third-party services.

The project focuses on the kinds of concerns that appear in real backend systems:

- API design
- asynchronous I/O
- persistence
- authentication and authorization
- business-state transitions
- caching
- external-provider abstraction
- idempotency
- webhook processing
- observability
- database migrations
- automated testing
- containerization
- CI
