# Citizen Complaint Tracker API

A REST API for filing and tracking public-service complaints. Citizens report problems such as a broken street light or a water leak, and officers move each complaint through a defined lifecycle until it is resolved or rejected.

I built this project to practise the day-to-day work of a junior backend developer: designing a small API, validating input, separating responsibilities across modules, writing automated tests, and documenting the result so that another developer can run and extend it without asking me questions.

**Stack:** Python 3.10+, FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2, pytest.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [Project Structure and Architecture](#3-project-structure-and-architecture)
4. [Data Model](#4-data-model)
5. [API Reference](#5-api-reference)
6. [Validation and Error Handling](#6-validation-and-error-handling)
7. [Testing](#7-testing)
8. [Design Decisions](#8-design-decisions)
9. [Security and Data Handling](#9-security-and-data-handling)
10. [Troubleshooting](#10-troubleshooting)
11. [Known Limitations and Future Work](#11-known-limitations-and-future-work)

---

## 1. Overview

The system models one workflow: a citizen files a complaint, and an officer works it to a conclusion.

```
pending --> in_progress --> resolved
   |             |
   +-------------+--------> rejected
```

A new complaint always starts as `pending`. An officer can move it to `in_progress`, `resolved` or `rejected` and attach remarks explaining the decision. Once a complaint is `resolved` or `rejected` it is closed, and the API refuses further status changes. I added this rule deliberately, because a record that can be silently reopened would make any report built on top of it unreliable.

The API supports creating, reading, listing, updating the status of, and deleting complaints. Listing supports filtering by status and category, and pagination. A reporting endpoint returns a count of complaints per status.

---

## 2. Quick Start

### Prerequisites

- Python 3.10 or newer (the code uses the `str | None` type syntax)
- `pip`
- Git

### Installation

```bash
git clone <your-repository-url>
cd complaint-tracker

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

I use a virtual environment so that the project's dependencies stay separate from the rest of the system.

### Run the server

```bash
uvicorn app.main:app --reload
```

The `--reload` flag restarts the server when a file changes, which is convenient during development but should not be used in production.

The API is now available at `http://127.0.0.1:8000`. FastAPI generates interactive documentation automatically:

- Complaint dashboard: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs` (lets you send requests from the browser)
- ReDoc: `http://127.0.0.1:8000/redoc`

The SQLite database file `complaints.db` and its tables are created automatically on first start. No manual database setup is required.

### Try it

```bash
curl -X POST http://127.0.0.1:8000/complaints \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Broken street light",
        "description": "The light near the ward office has been off for a week.",
        "category": "electricity",
        "citizen_name": "Ram Shrestha",
        "phone": "9800000000"
      }'
```

---

## 3. Project Structure and Architecture

```
complaint-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py        # Routes: receives requests, returns responses
│   ├── crud.py        # Database operations and business rules
│   ├── models.py      # SQLAlchemy table definitions and enums
│   ├── schemas.py     # Pydantic models: request and response validation
│   └── database.py    # Engine, session factory and get_db dependency
├── tests/
│   └── test_api.py    # Automated tests
├── requirements.txt
├── .gitignore
└── README.md
```

I separated the code into layers so that each file has one reason to change.

| Layer | File | Responsibility |
|-------|------|----------------|
| HTTP | `main.py` | Define URLs, read requests, choose status codes, translate errors into HTTP responses. It contains no SQL. |
| Business logic and data access | `crud.py` | Query and modify the database, and enforce rules such as "closed complaints cannot be changed". It knows nothing about HTTP. |
| Validation | `schemas.py` | Describe what valid input and output look like. |
| Persistence | `models.py`, `database.py` | Describe the tables and manage the database connection. |

A request flows through these layers in order:

```
Client -> main.py (route) -> schemas.py (validate input) -> crud.py (logic + database) -> main.py -> Client
```

Keeping the business rule in `crud.py` rather than in the route means it can be reused and tested without going through HTTP. When the rule is broken, `crud.py` raises a `ClosedComplaintError`, and `main.py` converts that into a `400` response. This keeps the data layer independent of the web framework.

### Dependency injection for the database session

Each route receives its database session through FastAPI's `Depends(get_db)`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Every request gets its own session, and the `finally` block guarantees the session is closed even when an error occurs. This also lets the tests replace the real database with a temporary one without changing any application code.

---

## 4. Data Model

### Complaint

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | integer | generated | Primary key |
| `title` | string | yes | 5 to 100 characters |
| `description` | string | yes | At least 10 characters |
| `category` | enum | yes | `road`, `water`, `electricity`, `waste`, `other` |
| `citizen_name` | string | yes | 2 to 80 characters |
| `phone` | string | no | 7 to 15 digits, digits only |
| `status` | enum | generated | `pending` (default), `in_progress`, `resolved`, `rejected` |
| `remarks` | string | no | Officer's note, set when the status is updated |
| `created_at` | datetime | generated | Set on creation |
| `updated_at` | datetime | generated | Refreshed on every update |

I used enums for `status` and `category` instead of free text. A typo such as `"resolvd"` is rejected at the boundary, so the database can only ever contain values the rest of the code understands.

---

## 5. API Reference

All request and response bodies are JSON. Interactive documentation for every endpoint is available at `/docs`.

| Method | Endpoint | Purpose | Success | Errors |
|--------|----------|---------|---------|--------|
| GET | `/` | Complaint dashboard | 200 | none |
| GET | `/api/health` | Health check | 200 | none |
| POST | `/complaints` | File a new complaint | 201 | 422 |
| POST | `/auth/register` | Create a citizen account | 201 | 409, 422 |
| POST | `/auth/login` | Log in, get a bearer token | 200 | 401 |
| GET | `/auth/me` | Current user | 200 | 401 |
| POST | `/auth/logout` | Invalidate the token | 204 | 401 |
| GET | `/complaints` | List complaints (admin: all, citizen: own) | 200 | 401, 422 |
| GET | `/complaints/stats` | Count by status | 200 | none |
| GET | `/complaints/{id}` | Get one complaint | 200 | 404 |
| PATCH | `/complaints/{id}/status` | **Admin only.** Update status and remarks | 200 | 400, 401, 403, 404, 422 |
| DELETE | `/complaints/{id}` | **Admin only.** Delete a complaint | 204 | 401, 403, 404 |

### Create a complaint

`POST /complaints`

Request:

```json
{
  "title": "Broken street light",
  "description": "Light near ward office is off for a week.",
  "category": "electricity",
  "citizen_name": "Ram Shrestha",
  "phone": "9800000000"
}
```

Response `201 Created`:

```json
{
  "id": 1,
  "title": "Broken street light",
  "description": "Light near ward office is off for a week.",
  "category": "electricity",
  "citizen_name": "Ram Shrestha",
  "phone": "9800000000",
  "status": "pending",
  "remarks": null,
  "created_at": "2026-11-03T13:15:59.044252",
  "updated_at": "2026-11-03T13:15:59.044261"
}
```

### List complaints

`GET /complaints`

| Query parameter | Type | Default | Description |
|-----------------|------|---------|-------------|
| `status` | enum | none | Return only complaints with this status |
| `category` | enum | none | Return only complaints in this category |
| `skip` | integer, 0 or more | 0 | Number of records to skip |
| `limit` | integer, 1 to 100 | 20 | Maximum records to return |

Results are ordered newest first. Example, the second page of ten pending road complaints:

```bash
curl "http://127.0.0.1:8000/complaints?status=pending&category=road&skip=10&limit=10"
```

I capped `limit` at 100 so that a single request cannot ask the server to return an unbounded amount of data.

### Update the status

`PATCH /complaints/{id}/status`

```json
{
  "status": "resolved",
  "remarks": "Light replaced on 3 November."
}
```

I used `PATCH` rather than `PUT` because the request changes part of the resource instead of replacing all of it.

If the complaint is already `resolved` or `rejected`, the API responds with `400`:

```json
{ "detail": "Complaint is already resolved" }
```

### Statistics

`GET /complaints/stats`

```json
{
  "pending": 0,
  "in_progress": 0,
  "resolved": 1,
  "rejected": 0,
  "total": 1
}
```

The counts are computed in the database with a `GROUP BY` query rather than by loading every row into Python, so the cost does not grow with the amount of data returned.

### HTTP status codes used

| Code | Meaning | Where it is used |
|------|---------|------------------|
| 200 | OK | Successful reads and updates |
| 201 | Created | A complaint was created |
| 204 | No Content | A complaint was deleted |
| 400 | Bad Request | Business rule violated (closed complaint) |
| 404 | Not Found | No complaint with that id |
| 422 | Unprocessable Entity | Input failed validation |

### Roles and authentication

- **Citizen** (self-registered): files complaints and sees only their own, including the admin's status and remarks. Cannot change status or delete.
- **Admin**: sees every complaint, and is the only role that can change a status or delete. Admins cannot be created through the API.

Send the token from `/auth/login` as `Authorization: Bearer <token>` (Swagger UI: the Authorize button is not wired; use curl or the dashboard). Tokens last 12 hours and only their hash is stored.

The first admin is created on startup from the `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables. If unset, it defaults to `admin` / `admin123` and prints a warning. **Change this before deploying.**

```bash
ADMIN_USERNAME=officer ADMIN_PASSWORD='a-strong-password' uvicorn app.main:app --reload
```

Existing `complaints.db` files: `create_all` adds the new `users` and `auth_tokens` tables but not the new `complaints.owner_id` column. Delete `complaints.db` to recreate it (old complaints without an owner would only be visible to admins anyway).

---

## 6. Validation and Error Handling

Validation is declared once, in `schemas.py`, and FastAPI applies it automatically before any route code runs.

```python
class ComplaintCreate(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    category: Category
    citizen_name: str = Field(min_length=2, max_length=80)
    phone: str | None = Field(default=None, pattern=r"^\d{7,15}$")
```

When validation fails, the API returns `422` with a list that identifies each bad field and explains the problem:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 5 characters"
    },
    {
      "type": "enum",
      "loc": ["body", "category"],
      "msg": "Input should be 'road', 'water', 'electricity', 'waste' or 'other'"
    }
  ]
}
```

The `loc` field tells the caller exactly where the problem is, which makes the error usable by a front-end developer without reading my source code.

I distinguish two kinds of failure on purpose. A `422` means the request was malformed (wrong shape or values). A `400` means the request was well-formed but not allowed in the current state of the data. Using different codes lets a client react differently to each.

---

## 7. Testing

The suite contains 23 tests covering the main success paths, validation failures, missing records, filtering, pagination, the closed-complaint rule and the statistics endpoint.

```bash
pytest -v
```

### How the tests are isolated

The tests never touch the real `complaints.db` file. A fixture builds a fresh in-memory SQLite database for each test and swaps it in using FastAPI's `dependency_overrides`:

```python
app.dependency_overrides[get_db] = override_get_db
```

Each test starts with empty tables and the tables are dropped afterwards, so tests cannot depend on one another or on the order they run in. In-memory SQLite is also fast, so the whole suite finishes in about a second.

### What is covered

| Area | Tests |
|------|-------|
| Health check | Service responds with 200 |
| Create | Valid input returns 201 with status `pending`; short title, invalid category and bad phone each return 422 |
| Read | Existing id returns 200; unknown id returns 404 |
| List | Category filter; pagination with `limit` and `skip` |
| Update | Status changes and remarks are saved; a closed complaint returns 400 |
| Delete | Returns 204; a later read returns 404 |
| Report | Counts per status and total are correct |

### Adding a new test

Follow the same pattern: create the data you need through the API, perform one action, and assert on the status code and the body.

```python
def test_filter_by_status(client):
    create(client)
    create(client)
    client.patch("/complaints/1/status", json={"status": "resolved"})
    pending = client.get("/complaints", params={"status": "pending"}).json()
    assert len(pending) == 1
```

---

## 8. Design Decisions

| Decision | Reason |
|----------|--------|
| FastAPI | Automatic request validation and interactive documentation from the type hints, with little boilerplate. |
| SQLite | Requires no installation, so anyone can run the project in a minute. The SQLAlchemy layer means moving to PostgreSQL later needs a connection-string change and little else. |
| Synchronous SQLAlchemy | The workload is small and the synchronous style is easier to read and debug. Async would add complexity without a measurable benefit here. |
| Separate `crud.py` | Keeps business rules testable and independent of HTTP. |
| Enums for status and category | Prevents invalid values from ever reaching the database. |
| Closed complaints are immutable | Protects the integrity of the record and of any statistics derived from it. |
| Pagination with a maximum limit | Protects the server from very large responses. |
| Tests use an in-memory database | Fast, isolated and repeatable, and never risks real data. |

---

## 9. Security and Data Handling

Complaints contain personal data: a citizen's name and phone number. I treat that as the main risk in the system and document what the code does and does not protect against.

**What is in place**

- All input is validated by Pydantic before it reaches the database, including length limits and a digits-only pattern for the phone number.
- Database access goes through SQLAlchemy with bound parameters, so user input is never concatenated into SQL strings. This prevents SQL injection.
- Enum validation rejects unexpected values for `status` and `category`.
- Error responses do not expose stack traces or internal details.
- The `complaints.db` file is listed in `.gitignore` so that real data is never committed to the repository.

**What is not in place yet**

- Authentication is basic (username and password, bearer tokens, no password reset, no login rate limiting). Role checks are in place: only admins can change status or delete.
- Phone numbers are stored in plain text and returned in full by every read endpoint. A production system should limit who can see them, and consider masking them in list responses.
- There is no rate limiting and no HTTPS configuration. These would normally be handled by a reverse proxy in front of the application.

I list these gaps openly because documenting a limitation is part of handling data responsibly: a reader should never assume a protection exists when it does not.

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'app'` when running `pytest` | Tests were started from the wrong folder | Run `pytest` from the project root, the folder that contains `app/` |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed, or the virtual environment is not active | Activate `.venv`, then run `pip install -r requirements.txt` |
| `Address already in use` | Another process is using port 8000 | Stop that process, or run `uvicorn app.main:app --port 8001` |
| `422 Unprocessable Entity` on a request that looks correct | A field breaks a validation rule | Read the `loc` and `msg` fields in the response body |
| `TypeError` on `str \| None` | Python older than 3.10 | Upgrade Python |
| Data from an earlier run is still present | `complaints.db` persists between runs | Stop the server and delete `complaints.db`; it will be recreated |

---

## 11. Known Limitations and Future Work

**Limitations**

- No authentication or role separation (see section 9).
- Deletion is permanent. A real system would normally mark records as deleted so that an audit trail remains.
- Timestamps are stored by SQLite without timezone information, so they are returned without a timezone suffix. They are generated in UTC, but a production database such as PostgreSQL would store and return the timezone explicitly.
- There is no history of status changes; only the latest status and remarks are kept.
- The schema is created automatically with `create_all`, which does not handle later changes to the tables.

**Planned improvements, in priority order**

1. Password reset and login rate limiting.
2. A status-history table to record who changed a complaint, when, and why.
3. Database migrations with Alembic.
4. Soft delete instead of permanent deletion.
5. PostgreSQL support and a Dockerfile.
6. Continuous integration that runs the tests on every push.
