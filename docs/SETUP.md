# Setup

This guide explains how to run FleetTrack locally for development.

## Requirements

- Python 3.11 or newer
- Node.js compatible with the checked-in Next.js version
- `pnpm`
- Microsoft SQL Server with the existing FleetTrack/Balance database
- ODBC Driver 18 for SQL Server

## Backend

```bash
cd "FleetTrack Backend"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

OpenAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend

```bash
cd "FleetTrack Frontend"
pnpm install
pnpm dev
```

The frontend runs at:

```text
http://localhost:3000
```

## Environment Files

Example files are included:

```text
FleetTrack Backend/.env.example
FleetTrack Frontend/.env.example
```

Create local copies named `.env` or `.env.local` as appropriate. Do not commit real credentials.

## Important Configuration Notes

The current backend database session module still contains a local MSSQL connection string. For production or shared development, move database connection details into environment variables before deployment.

Authentication uses an HTTP-only session cookie. For production HTTPS, set:

```env
AUTH_COOKIE_SECURE=true
```

For local development, the frontend proxies API calls through `/api`, so browser requests stay same-origin and include cookies.

## Useful Checks

Backend tests:

```bash
cd "FleetTrack Backend"
venv/bin/python -m unittest discover -s tests -v
```

Frontend build:

```bash
cd "FleetTrack Frontend"
pnpm lint
pnpm build
```

Some historical notes in `docs/CURRENT_STATE.md` mention pre-existing test or typecheck limitations. Check that file when investigating older failures.
