# ENVIRONMENT.md — Setup & Development Guide

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Initial Setup

```bash
# 1. Create virtual environment
uv venv

# 2. Install all dependencies
uv sync

# 3. Activate environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 4. Configure environment
cp .env .env.local
# Edit .env with your settings

# 5. Run migrations
python manage.py migrate

# 6. Create admin user (optional)
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_ENV` | `development` | `development` or `production` |
| `SECRET_KEY` | dev key | Django secret key — change in production |
| `DB_NAME` | — | PostgreSQL database name (production) |
| `DB_USER` | — | PostgreSQL user (production) |
| `DB_PASSWORD` | — | PostgreSQL password (production) |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `ALLOWED_HOSTS` | — | Comma-separated allowed hosts (production) |
| `CORS_ALLOWED_ORIGINS` | — | Comma-separated CORS origins (production) |

## Adding Dependencies

```bash
# Add a package
uv add package-name

# Add a dev-only package
uv add --dev package-name

# Remove a package
uv remove package-name

# Sync after pulling changes
uv sync
```

Never use `pip install` — always use `uv add`.

## Running Tests

```bash
python manage.py test
```

## Database Operations

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
rm db.sqlite3 && python manage.py migrate
```

## Switching to PostgreSQL

1. Set `DJANGO_ENV=production` in `.env`
2. Fill in `DB_*` variables
3. Run `python manage.py migrate`

## Production Deployment

```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
uv add gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Serve static/media files via nginx. Never use Django's dev server in production.
