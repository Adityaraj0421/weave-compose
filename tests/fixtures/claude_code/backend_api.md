---
name: Backend API Engineer
description: RESTful API design, database schema modeling, and server-side implementation in Python with FastAPI and PostgreSQL. Handles authentication, query optimization, and data validation.
capabilities:
  - api
  - rest
  - database
  - schema
  - authentication
  - python
  - fastapi
  - postgresql
  - endpoints
  - server
version: "1.0"
author: Backend Guild
---

# Backend API Engineer

This skill handles REST API design, data modeling, server-side implementation, and database operations. Use it when building API endpoints, designing database schemas, writing migrations, implementing authentication flows, or optimizing queries.

## When to Use

- Designing or implementing RESTful API endpoints
- Modeling database schemas and writing migrations
- Implementing JWT authentication and authorization
- Writing data validation with Pydantic models
- Optimizing SQL queries and database indexes
- Setting up API versioning, pagination, and error handling
- Integrating third-party services via HTTP clients

## API Design Principles

- **Resource-based URLs.** Use nouns, not verbs: `/users/{id}` not `/getUser`.
- **HTTP verbs correctly.** `GET` reads, `POST` creates, `PUT` replaces, `PATCH` updates, `DELETE` removes.
- **Consistent status codes.** `200` OK, `201` Created, `400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `422` Validation Error, `500` Server Error.
- **Request/response shape.** Always validate input with Pydantic. Always return structured JSON with consistent field names (snake_case).
- **Versioning.** Prefix all routes with `/api/v1/`. Never break existing clients.

## Database Rules

- Normalize schemas to 3NF unless denormalization is justified by query patterns
- Use foreign keys with `ON DELETE CASCADE` or `ON DELETE RESTRICT` as appropriate
- Index every column used in `WHERE`, `JOIN`, or `ORDER BY` clauses
- Never use `SELECT *` in production queries — always name columns explicitly
- Avoid N+1 queries — use `JOIN` or batch loading, not per-row queries in a loop
- All migrations must be reversible (have both `upgrade` and `downgrade` steps)

## Authentication

- Passwords: hash with `bcrypt` (12 rounds minimum). Never store plaintext.
- Sessions: use short-lived JWT access tokens (15 min) + long-lived refresh tokens (7 days)
- Rate limiting: apply to all auth endpoints (`/login`, `/register`, `/refresh`)
- Secrets: load from environment variables via `python-dotenv`. Never hardcode.

## Error Handling

```python
# All endpoint errors use this shape:
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "field": "field_name"  # optional, for validation errors
}
```

## Performance Checklist

- [ ] Query uses indexes — check with `EXPLAIN ANALYZE`
- [ ] Pagination implemented for list endpoints (`limit` + `offset` or cursor)
- [ ] N+1 queries eliminated
- [ ] Sensitive fields excluded from response schemas
- [ ] Rate limiting applied to mutating endpoints
