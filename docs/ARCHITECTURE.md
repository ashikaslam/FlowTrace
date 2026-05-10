# ARCHITECTURE.md — FlowTrace System Architecture

## Core Philosophy

FlowTrace uses an **API-first, template-rendered** architecture. Django renders HTML shells; all data flows through REST APIs consumed by vanilla JavaScript.

```
Browser
  │
  ├── GET /dashboard/{slug}/     → Django renders HTML template (no data)
  │
  └── JS fetch /api/activity/... → DRF returns JSON → JS updates DOM
```

This means the backend is already a proper API server. Migrating to React requires only replacing the template layer — zero backend changes.

## Layer Separation

```
┌─────────────────────────────────────┐
│           Browser / Client          │
│  HTML Templates + Vanilla JS        │
│  All data via fetch() → REST API    │
└──────────────┬──────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────┐
│         Django REST Framework       │
│  Serializers → Views → URL routing  │
│  JWT Authentication                 │
│  Workspace-scoped permissions       │
└──────────────┬──────────────────────┘
               │ ORM
┌──────────────▼──────────────────────┐
│         SQLite / PostgreSQL         │
│  Multi-tenant isolated data         │
└─────────────────────────────────────┘
```

## App Structure

Each Django app owns a single domain:

| App | Responsibility |
|-----|---------------|
| `accounts` | User model, JWT auth, workspace membership |
| `workspaces` | Workspace CRUD, permissions, stats |
| `tasks` | Task lifecycle, attachments |
| `activity` | Session tracking, switching, timeline — **core** |
| `comments` | Comments, @mention parsing, notifications |

## URL Routing Pattern

```
/                          → accounts.urls (landing, register, login)
/dashboard/{slug}/         → workspaces.urls (page rendering only)
/tasks/{slug}/             → tasks.urls (page rendering only)
/activity/{slug}/          → activity.urls (page rendering only)

/api/auth/                 → accounts.api_urls
/api/workspaces/           → workspaces.api_urls
/api/tasks/                → tasks.api_urls
/api/activity/             → activity.api_urls
/api/comments/             → comments.api_urls
```

## Permission Model

```
IsAuthenticated
  └── IsWorkspaceMember (user has active membership in workspace)
        └── IsWorkspaceManager (membership.role == 'manager')
```

Workspace slug always comes from the URL — never from the request body or JWT claims alone. This prevents privilege escalation.

## Settings Architecture

```
config/settings/
  ├── base.py         # Shared: apps, middleware, DRF, JWT
  ├── development.py  # SQLite, DEBUG=True, CORS allow all
  └── production.py   # PostgreSQL, DEBUG=False, strict CORS
```

`DJANGO_ENV` environment variable controls which settings load.

## Scalability Path

| Current | Future |
|---------|--------|
| Django Templates | React SPA (zero backend changes) |
| Polling (10s) | Django Channels WebSockets |
| SQLite | PostgreSQL (settings swap) |
| Single server | Celery + Redis for async tasks |
| Monolith | Microservices (API contracts already defined) |
