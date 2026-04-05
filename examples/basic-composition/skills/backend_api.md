---
name: Backend API Engineer
description: Designing and implementing RESTful APIs, database schemas, and server-side business logic using FastAPI and PostgreSQL with a focus on correctness, validation, and testability.
capabilities: [api, rest, fastapi, postgresql, database, validation, testing, python]
version: "1.0"
author: Weave Example
---

# Backend API Engineer

This skill governs how API endpoints, data models, and server-side logic are designed and implemented. Every endpoint must be validated, documented, and covered by tests.

## Endpoint Design

- Follow REST conventions strictly: GET for reads, POST for creates, PATCH for partial updates, DELETE for removes.
- Return consistent JSON envelopes: `{"data": ..., "error": null}` on success, `{"data": null, "error": "..."}` on failure.
- Use plural resource names in paths: `/users`, `/orders/{order_id}`, not `/user` or `/getOrder`.
- Never expose internal IDs or database primary keys in URLs. Use UUIDs.

## Request Validation

- Use Pydantic models for all request bodies and query parameters. No raw `dict` inputs.
- Validate at the boundary — never trust incoming data inside business logic layers.
- Return HTTP 422 with field-level error details for validation failures. Never 500.
- Strip and normalize strings on input: trim whitespace, lowercase emails.

## Database

- Use SQLAlchemy ORM with Alembic for migrations. Never write raw DDL by hand.
- Every table must have: `id` (UUID), `created_at`, `updated_at` columns.
- Index foreign keys and any column used in a WHERE clause.
- Never run N+1 queries. Use `joinedload` or `selectinload` for relationships.

## Testing

- Every endpoint must have at least one happy-path test and one error-path test.
- Use `pytest` with `httpx.AsyncClient` against a test database, not mocks.
- Seed test data in fixtures, not inside test functions.
- Tests must be independent and order-agnostic — never share state between tests.
