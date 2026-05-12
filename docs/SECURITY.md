# SECURITY.md — FlowTrace Security

## Workspace Isolation

Every API endpoint that accesses workspace data requires the `workspace_slug` in the URL. The `IsWorkspaceMember` permission class verifies the requesting user has an active membership in that specific workspace before any data is returned.

```python
# Every workspace-scoped query looks like this:
Task.objects.filter(workspace__slug=workspace_slug)
# Never:
Task.objects.all()  # ← this never appears in workspace-scoped views
```

Cross-workspace data access is structurally impossible — there are no global list endpoints for tasks, sessions, or comments.

## Authentication

- Django session authentication via `django.contrib.sessions`
- Session cookie (`sessionid`) is `HttpOnly`, `SameSite=Lax`, and `Secure` in production
- Sessions last 30 days (`SESSION_COOKIE_AGE`), renewed on every request (`SESSION_SAVE_EVERY_REQUEST`)
- `SESSION_EXPIRE_AT_BROWSER_CLOSE = False` — sessions survive browser restarts
- CSRF protection enforced on all mutating requests via `X-CSRFToken` header
- No tokens stored in `localStorage` — eliminates XSS token theft risk

## Authorization Levels

| Permission Class | Requirement |
|-----------------|-------------|
| `IsAuthenticated` | Active Django session |
| `IsWorkspaceMember` | Active membership in URL workspace |
| `IsWorkspaceManager` | Membership with `role=manager` |

Manager-only operations: creating developers, viewing all developer timelines, workspace settings.

## File Upload Security

- Files stored under `media/attachments/YYYY/MM/` — organized, not guessable
- Workspace membership required to upload
- Task must belong to the same workspace as the uploader
- `Pillow` installed for image validation (can be extended to validate MIME types)

## API Protection

- CSRF protection enabled for session-based requests
- CORS configured — development allows all origins; production uses explicit allowlist
- `XFrameOptionsMiddleware` prevents clickjacking
- `SecurityMiddleware` handles HTTPS redirects and HSTS in production

## Sensitive Data

- Passwords are hashed via Django's `AbstractBaseUser` (PBKDF2 by default)
- Generated developer passwords are returned once at creation time and never stored in plaintext
- `SECRET_KEY` loaded from environment variable — never hardcoded
- No JWTs or bearer tokens — session IDs are opaque and server-side only

## Production Checklist

- [ ] Set `SECRET_KEY` to a strong random value in `.env`
- [ ] Set `DJANGO_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Configure `CORS_ALLOWED_ORIGINS`
- [ ] Use PostgreSQL
- [ ] Serve media files via nginx (not Django)
- [ ] Enable HTTPS / configure `SECURE_SSL_REDIRECT`
- [ ] Confirm `SESSION_COOKIE_SECURE=True` and `CSRF_COOKIE_SECURE=True` (set automatically in production.py)
