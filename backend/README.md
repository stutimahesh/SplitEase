# SplitEase backend

A Flask REST API for the SplitEase expense splitter.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## Run

```bash
python run.py
```

The API runs at `http://localhost:5000`. It uses SQLite by default (`splitease.db`,
created automatically on first run) — no separate database server needed. Set the
`DATABASE_URL` environment variable to point at Postgres/MySQL instead if you want.

## Load sample data (optional)

```bash
python seed.py
```

Creates a sample group ("Goa Trip") with 3 users and 2 expenses so the frontend
isn't empty on first load. Login with `alice@example.com` / `password123`
(or `bob@example.com` / `carol@example.com`, same password).

## Run tests

```bash
python -m pytest tests/ -v
```

## API overview

| Method | Route | Description |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Log in, get a JWT |
| GET | `/api/auth/me` | Current user (auth required) |
| POST | `/api/groups` | Create a group |
| GET | `/api/groups` | List groups you belong to |
| GET | `/api/groups/<id>` | Group detail + members |
| POST | `/api/groups/<id>/members` | Add a member by email |
| POST | `/api/groups/<id>/expenses` | Add an expense (equal or custom split) |
| GET | `/api/groups/<id>/expenses` | List a group's expenses |
| GET | `/api/groups/<id>/balances` | Net balance per member |
| GET | `/api/groups/<id>/settle-up` | Minimum set of payments to settle the group |

All routes except register/login require an `Authorization: Bearer <token>` header.
