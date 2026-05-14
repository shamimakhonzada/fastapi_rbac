# FastAPI RBAC — Role-Based Access Control API

A production-ready REST API built with FastAPI, PostgreSQL, and SQLAlchemy. It covers user authentication (email/password and Google OAuth), role-based access control, and a clean feature-based project structure.

---

## Features

- **JWT Authentication** — cookie-based access tokens with configurable expiry
- **Google OAuth 2.0** — sign in with Google, auto-links existing accounts
- **Role-Based Access Control** — `admin` and `user` roles with route-level enforcement
- **User Management** — CRUD operations, profile endpoint, password change
- **Standardised Responses** — every endpoint returns a consistent `{ success, message, data }` envelope
- **Database Migrations** — managed with Alembic
- **CORS** — pre-configured for local frontend development

---

## Tech Stack

| Layer | Library |
|---|---|
| Framework | FastAPI 0.136 |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth / JWT | python-jose, bcrypt |
| OAuth | Authlib |
| Validation | Pydantic v2 |
| Server | Uvicorn |

---

## Project Structure

```
app/
├── main.py                  # App entry point, middleware, routers
├── core/
│   ├── config.py            # Settings loaded from .env
│   ├── database.py          # SQLAlchemy engine and session
│   ├── dependencies.py      # get_db, get_current_user
│   ├── exceptions.py        # Global exception handlers
│   ├── oauth.py             # Authlib Google OAuth client
│   ├── security.py          # Password hashing, JWT creation
│   └── seeds/
│       └── admin_seed.py    # Initial admin user seeder
├── features/
│   ├── auth/
│   │   ├── routes.py        # /api/v1/auth/*
│   │   ├── service.py       # Registration, login, token logic
│   │   ├── repository.py    # DB queries for auth
│   │   ├── schema.py        # RegisterSchema, LoginSchema
│   │   └── utils.py         # Re-exports from core/security
│   └── users/
│       ├── routes.py        # /api/v1/users/*
│       ├── service.py       # User business logic
│       ├── repository.py    # DB queries for users
│       ├── model.py         # User SQLAlchemy model
│       └── schema.py        # UserResponse, UpdateUser, etc.
└── common/
    ├── enums/
    │   └── user_role.py     # UserRole enum (admin, user)
    ├── responses/
    │   ├── response_builder.py   # success_response() helper
    │   └── standard_response.py  # StandardResponse Pydantic model
    └── utils/
        └── permissions.py   # require_roles() dependency
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd fastApi

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy the example below into a `.env` file at the project root and fill in your values.

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rbac_db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Frontend redirect after OAuth
FRONTEND_URL=http://localhost:3000
```

### Database Setup

```bash
# Run all migrations
alembic upgrade head
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are at `/docs`.

---

## API Reference

### Authentication — `/api/v1/auth`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/register` | Register with email and password | Public |
| `POST` | `/login` | Login, sets `access_token` cookie | Public |
| `POST` | `/logout` | Clears the auth cookie | Public |
| `GET` | `/google/login` | Redirect to Google consent screen | Public |
| `GET` | `/google/callback` | OAuth callback, redirects to frontend | Public |

### Users — `/api/v1/users`

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/` | List all users | Admin |
| `GET` | `/{user_id}` | Get a user by ID | Admin |
| `PUT` | `/{user_id}` | Update a user | Owner or Admin |
| `DELETE` | `/{user_id}` | Delete a user | Admin |
| `PATCH` | `/{user_id}` | Change a user's password | Authenticated |
| `GET` | `/me/profile` | Get the current user's profile | Authenticated |

---

## Authentication Flow

### Email / Password

1. `POST /api/v1/auth/register` with `username`, `email`, `full_name`, `password`
2. `POST /api/v1/auth/login` with `email`, `password` — sets an `httpOnly` cookie
3. All subsequent requests carry the cookie automatically

### Google OAuth

1. Redirect the user to `GET /api/v1/auth/google/login`
2. Google authenticates and redirects back to the callback
3. The callback issues a JWT cookie and redirects to `FRONTEND_URL`
4. If the email already exists in the database, the Google account is linked automatically

---

## Response Format

Every endpoint returns the same envelope:

```json
{
  "success": true,
  "message": "Human-readable message",
  "data": { }
}
```

Errors follow the same shape with `"success": false`.

---

## User Model

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Primary key |
| `username` | string | Unique |
| `email` | string | Unique |
| `full_name` | string | |
| `hashed_password` | string | `null` for OAuth-only accounts |
| `role` | string | `user` or `admin` |
| `provider` | string | e.g. `google`, `null` for email accounts |
| `provider_id` | string | Provider's user ID (`sub` claim) |
| `is_verified` | boolean | `true` automatically for OAuth users |
| `created_at` | timestamp | |
| `updated_at` | timestamp | |
