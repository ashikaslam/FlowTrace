# Deploying FlowTrace on Render

## Overview

You will create two Render services:
1. **PostgreSQL** database (free tier)
2. **Web Service** (Django app)

---

## Step 1 — Push to GitHub

Make sure your code is on GitHub. Render deploys directly from a repo.

```bash
git add .
git commit -m "ready for render"
git push
```

---

## Step 2 — Add required files

### `build.sh` (in project root)

Render runs this script on every deploy.

```bash
#!/usr/bin/env bash
set -o errexit

pip install uv
uv sync
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate
```

Make it executable:

```bash
chmod +x build.sh
```

### `gunicorn` dependency

Add gunicorn to your project:

```bash
uv add gunicorn
```

Commit both changes:

```bash
git add .
git commit -m "add build.sh and gunicorn"
git push
```

---

## Step 3 — Create PostgreSQL database on Render

1. Go to [render.com](https://render.com) → **New** → **PostgreSQL**
2. Name it `flowtrace-db`
3. Choose the **Free** plan
4. Click **Create Database**
5. Once created, copy the **Internal Database URL** — you'll need it in Step 5

---

## Step 4 — Create the Web Service

1. Go to **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:

| Field | Value |
|-------|-------|
| **Name** | `flowtrace` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

---

## Step 5 — Set Environment Variables

In your Web Service → **Environment** tab, add these:

| Key | Value |
|-----|-------|
| `DJANGO_ENV` | `production` |
| `SECRET_KEY` | a long random string (generate below) |
| `DATABASE_URL` | the Internal Database URL from Step 3 |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://your-app-name.onrender.com` |
| `PYTHON_VERSION` | `3.13.0` |

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Step 6 — Update production settings to use DATABASE_URL

Render provides a single `DATABASE_URL` env var. Update `config/settings/production.py`:

```python
from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
    )
}

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

Add `dj-database-url`:
```bash
uv add dj-database-url
git add .
git commit -m "use dj-database-url for render"
git push
```

---

## Step 7 — Make sure DJANGO_SETTINGS_MODULE is set

In `config/wsgi.py`, confirm this line exists (it should already):

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
```

Render will override it via the `DJANGO_SETTINGS_MODULE` env var. Add this to your environment variables:

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |

---

## Step 8 — Deploy

Click **Deploy** (or push a new commit). Render will:
1. Run `build.sh` — installs deps, collects static, runs migrations
2. Start gunicorn

Your app will be live at `https://your-app-name.onrender.com`

---

## Notes

- **Static files** — `collectstatic` copies files to `staticfiles/`. Django serves them in dev; on Render add `whitenoise` for production static serving (optional but recommended).
- **Media files** — Render's free tier has no persistent disk. Uploaded files (attachments) will be lost on redeploy. For production use an S3 bucket.
- **Free tier spins down** after 15 minutes of inactivity and takes ~30s to wake up on the next request. Upgrade to a paid plan to avoid this.

### Optional: Add WhiteNoise for static files

```bash
uv add whitenoise
```

In `config/settings/production.py`, add to `MIDDLEWARE` right after `SecurityMiddleware`:

```python
"whitenoise.middleware.WhiteNoiseMiddleware",
```

And add:
```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```
