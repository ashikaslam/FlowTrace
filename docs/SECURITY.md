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

- JWT tokens via `djangorestframework-simplejwt`
- Access tokens expire in 8 hours
- Refresh tokens expire in 7 days
- Token payload includes `workspace_id`, `workspace_slug`, `role` for client-side routing
- Token claims are NOT used for server-side authorization — workspace slug from URL is always re-verified

## Authorization Levels

| Permission Class | Requirement |
|-----------------|-------------|
| `IsAuthenticated` | Valid JWT token |
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
- JWT secret key loaded from environment variable — never hardcoded

## Production Checklist

- [ ] Set `SECRET_KEY` to a strong random value in `.env`
- [ ] Set `DJANGO_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Configure `CORS_ALLOWED_ORIGINS`
- [ ] Use PostgreSQL
- [ ] Serve media files via nginx (not Django)
- [ ] Enable HTTPS / configure `SECURE_SSL_REDIRECT`
