# MCCTV LFR Vans — FastAPI Backend

FastAPI replacement for the Django backend (`MCCTV-LFR-Vans-backend`).
Both backends share the same Postgres database during the migration period.

## Database layout

| Prefix | Owner | Tables |
|--------|-------|--------|
| *(none)* | Django | `van_requests`, `participants`, `users`, `stops`, `van_request_participants`, `auth_*`, `django_*` |
| `api_` | FastAPI | `api_users`, `api_van_requests`, `api_participants`, `api_stops`, `api_van_request_participants`, `api_van_request_participants`, `api_mission_admin_panels`, `api_token_store` |

FastAPI tables are prefixed with `api_` to avoid collisions with Django's
existing tables. Both sets of tables coexist in the same schema without
conflicts.

## Setup

```bash
cd mcctv-lfr-vans-api
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env                              # fill in DATABASE_URL etc.
```

## Running migrations

```bash
# Apply all migrations to the database
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Preview SQL without applying
alembic upgrade head --sql
```

## Starting the server

```bash
uvicorn app.main:app --reload --port 8001
```

The Django backend runs on port 8000; FastAPI runs on port 8001 during
parallel operation.

## Frontend switchover

The frontend (`MCCTV-LFR-Vans-frontend`) is currently configured to talk
to the Django base URL. Switch it to the FastAPI base URL (`/api/v1/…`)
one feature at a time as routes are verified.

## Django shutdown note

Once the frontend is fully switched to the FastAPI base URL and all
features are verified in production:

1. Stop the Django server (`gunicorn`/`uwsgi` process).
2. Remove the Django app from the server.
3. **Data migration:** copy any live data from the unprefixed Django tables
   into the `api_*` FastAPI tables, then verify row counts.
4. Drop the Django tables after data migration is confirmed:

```sql
-- Run only after data migration is complete and verified
DROP TABLE IF EXISTS
    van_request_participants, stops, van_requests,
    participants, authtoken_token,
    auth_user, auth_group, auth_permission,
    auth_user_groups, auth_user_user_permissions,
    auth_group_permissions,
    django_admin_log, django_content_type,
    django_migrations, django_session
CASCADE;
```

> **Do not drop Django tables** until data has been migrated and the
> frontend cutover is complete and stable in production.
