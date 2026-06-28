# Local Setup Guide

This guide explains how to run the Website Trust Advisor on your local machine for development and testing.

> **Security note:** Never commit real secrets, API keys, or passwords to Git. The `.env` file is listed in `.gitignore` and must stay there.

---

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Git | Any recent | Clone the repository |
| Docker | 24+ | Run PostgreSQL, Redis, and services via Compose |
| Docker Compose | v2 (built into Docker Desktop) | Orchestrate containers |
| Node.js | 20 LTS | Run the Next.js frontend locally |
| npm | 10+ | Install frontend dependencies |
| Python | 3.11+ | Run the FastAPI backend locally (optional — Docker handles this too) |

> **Easiest path:** Docker Compose handles PostgreSQL, Redis, backend, and frontend in one command. You only need Node locally if you want to run the frontend outside Docker (e.g. for hot reload during UI work).

---

## 1. Clone the Repository

```bash
git clone https://github.com/M2elsharawy/website-trust-scanner.git
cd website-trust-scanner
```

---

## 2. Configure Environment Variables

The project uses a single `.env` file at the project root. A template is provided:

```bash
cp .env.example .env
```

Open `.env` and fill in the required values. The table below describes each variable:

### Required — must be changed from defaults

| Variable | Description | How to generate |
|---|---|---|
| `POSTGRES_PASSWORD` | PostgreSQL password | `openssl rand -base64 32` |
| `SECRET_KEY` | JWT signing key — must be ≥ 32 random bytes | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_API_KEY` | Admin API key | `python -c "import secrets; print(secrets.token_hex(32))"` |

### Connection strings (use defaults for local Docker setup)

| Variable | Default for local Docker | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://trustscanner:<password>@db:5432/trustscanner` | Replace `<password>` with your `POSTGRES_PASSWORD` |
| `REDIS_URL` | `redis://redis:6379/0` | Matches the Redis container in docker-compose.yml |
| `POSTGRES_DB` | `trustscanner` | |
| `POSTGRES_USER` | `trustscanner` | |

### Frontend URLs

| Variable | Local value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |
| `NEXT_PUBLIC_BACKEND_URL` | `http://localhost:8000` |

### Optional for local development

| Variable | Default | Notes |
|---|---|---|
| `APP_ENV` | `development` | Set to `production` to enable `secure` cookies and host validation |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed frontend origins |
| `REPUTATION_PROVIDER` | `mock` | Use `mock` locally — do not set real API keys unless testing provider integration |
| `GOOGLE_SAFE_BROWSING_API_KEY` | _(empty)_ | Only needed if `REPUTATION_PROVIDER=google_safe_browsing` |
| `VIRUSTOTAL_API_KEY` | _(empty)_ | Only needed if `REPUTATION_PROVIDER=virustotal` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | |
| `SCAN_TIMEOUT_SECONDS` | `8` | |

---

## 3. Start All Services with Docker Compose

This single command starts PostgreSQL, Redis, backend, Celery worker, Celery beat, and frontend:

```bash
docker compose up --build
```

First run takes a few minutes while Docker builds the images. Subsequent starts are faster.

To run in the background:

```bash
docker compose up --build -d
```

### Individual service ports

| Service | URL |
|---|---|
| Frontend (Next.js) | http://localhost:3000 |
| Backend (FastAPI) | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## 4. Run Database Migrations

After the backend container is healthy, run Alembic migrations:

```bash
docker compose exec backend alembic upgrade head
```

This creates all tables in the PostgreSQL database. You must run this on every fresh database or after pulling new migration files.

---

## 5. Run the Backend Locally (Without Docker)

If you prefer to run the backend outside Docker (with a local Python environment):

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.dev.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

You still need PostgreSQL and Redis running. The easiest way is to start only the infra containers:

```bash
# From project root:
docker compose up db redis -d
```

Then update your local `.env` to point to localhost instead of the Docker service names:

```
DATABASE_URL=postgresql+asyncpg://trustscanner:<password>@localhost:5432/trustscanner
REDIS_URL=redis://localhost:6379/0
```

---

## 6. Run the Frontend Locally (Without Docker)

```bash
cd frontend

# Install dependencies
npm install

# Start development server with hot reload
npm run dev
```

Frontend runs at http://localhost:3000. Make sure `NEXT_PUBLIC_API_URL=http://localhost:8000` is set (either in `.env` or `frontend/.env.local`).

To run a production build locally:

```bash
npm run build
npm start
```

---

## 7. Run Backend Tests

```bash
cd backend

# With virtual environment activated:
pytest

# With coverage:
pytest --cov=app --cov-report=term-missing

# Or via Docker:
docker compose exec backend pytest
```

---

## 8. Run Frontend Type Check and Build

```bash
cd frontend

# TypeScript check (no output = no errors):
npx tsc --noEmit

# Production build:
npm run build
```

Both of these run automatically in CI on every PR.

---

## 9. Stop and Clean Up

Stop all running containers:

```bash
docker compose down
```

Stop and remove all data volumes (full reset — database will be empty):

```bash
docker compose down -v
```

---

## 10. Local Setup Checklist

Run through these checks after first setup to confirm everything is working:

### Infrastructure
- [ ] `docker compose up --build` completes without errors
- [ ] `docker compose ps` shows all services as `healthy` or `running`
- [ ] http://localhost:8000/api/v1/health returns `{"status": "ok"}`
- [ ] http://localhost:3000 loads the homepage

### Database
- [ ] `docker compose exec backend alembic upgrade head` completes without errors
- [ ] No `ERROR` lines in backend container logs (`docker compose logs backend`)

### Auth
- [ ] Can register a new account at http://localhost:3000/en/register
- [ ] Can log in at http://localhost:3000/en/login
- [ ] Logged-in user is redirected to `/en/sites`
- [ ] Unauthenticated access to `/en/sites` redirects to `/en/login`

### Visitor Flow
- [ ] Enter `https://example.com` in the home page scan form → returns a Trust Score
- [ ] Enter `http://localhost` → blocked with SSRF error
- [ ] Enter `http://169.254.169.254` → blocked with SSRF error

### Frontend Build
- [ ] `cd frontend && npx tsc --noEmit` exits with no errors
- [ ] `cd frontend && npm run build` completes successfully

### Tests
- [ ] `cd backend && pytest` exits with all tests passing

---

## 11. Common Issues

| Problem | Likely cause | Fix |
|---|---|---|
| `POSTGRES_PASSWORD is required` on `docker compose up` | `.env` file missing or password not set | Copy `.env.example` → `.env` and set `POSTGRES_PASSWORD` |
| `alembic upgrade head` fails with `connection refused` | Database container not yet healthy | Wait for `db` to show `healthy` in `docker compose ps`, then retry |
| Frontend shows `Network Error` when scanning | `NEXT_PUBLIC_API_URL` not set or backend not running | Confirm backend is up and the env var points to `http://localhost:8000` |
| Backend shows `passlib: error reading bcrypt version` | Known `passlib` + `bcrypt 4.x` mismatch | Non-breaking warning — authentication still works. Will be resolved in Release 1.0.1. |
| `middleware` deprecation warning in Next.js build | Next.js 16 convention change | Non-breaking — will be addressed in Release 1.0.1. |
| `pytest-asyncio` deprecation warnings | Pending test suite update | Non-breaking — tests pass. Will be resolved in Release 1.0.1. |
