# FlowTrace

**Developer Workflow Intelligence Platform**

FlowTrace tracks how developers actually work — task switching, context changes, workflow timelines, and productivity flow. It is NOT a project management tool. It's a real-time activity intelligence platform.

## What It Does

- Tracks every task a developer works on with precise start/end times
- Logs every context switch with completion percentage and optional notes
- Visualizes developer workflow as a timeline (like a Git history graph)
- Gives managers a live view of what every developer is doing right now
- Preserves complete historical activity — nothing is ever deleted

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django 5.2, Django REST Framework |
| Auth | JWT via djangorestframework-simplejwt |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Django Templates, TailwindCSS CDN, Vanilla JS |
| Package Manager | uv |

## Quick Start

```bash
# Clone and enter project
cd FlowTrace

# Install dependencies
uv sync

# Configure environment
cp .env .env.local  # edit as needed

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Visit `http://localhost:8000`

## Project Structure

```
flowtrace/
├── apps/
│   ├── accounts/       # User auth, workspace membership
│   ├── workspaces/     # Workspace management, permissions
│   ├── tasks/          # Task CRUD, attachments
│   ├── activity/       # Core: session tracking, switching, timeline
│   └── comments/       # Comments, @mentions
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── templates/
│   ├── base/
│   ├── accounts/
│   ├── dashboard/
│   ├── tasks/
│   └── activity/
├── static/
├── media/
├── docs/
├── manage.py
├── pyproject.toml
└── .env
```

## Documentation

| File | Contents |
|------|----------|
| [DATABASE.md](docs/DATABASE.md) | Schema, relationships, indexing |
| [API.md](docs/API.md) | All endpoints with examples |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design decisions |
| [WORKFLOW.md](docs/WORKFLOW.md) | Task switching lifecycle |
| [SECURITY.md](docs/SECURITY.md) | Auth, isolation, upload security |
| [ENVIRONMENT.md](docs/ENVIRONMENT.md) | Setup and deployment guide |
| [FUTURE_PLANS.md](docs/FUTURE_PLANS.md) | Roadmap and upgrade paths |

## Core Concept

```
Developer starts Task A
  → Authority requests Task D (urgent)
    → Developer switches: logs 30% completion on A, note: "interrupted"
    → Task D session starts
      → Emergency Task E
        → Switch again: logs 10% on D
        → Task E session starts
        → Task E done: 100%
      → Resume Task D
    → Task D done: 100%
  → Resume Task A
→ Task A continues from 30%
```

FlowTrace captures every step of this with timestamps, durations, and notes.
