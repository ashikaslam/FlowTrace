# API.md — FlowTrace REST API

## Authentication

All endpoints (except register and login) require a JWT Bearer token.

```
Authorization: Bearer <access_token>
```

Tokens are workspace-scoped — the JWT payload includes `workspace_id`, `workspace_slug`, and `role`.

---

## Auth Endpoints

### POST /api/auth/register/
Create a new user account.

**Request:**
```json
{ "email": "jane@company.com", "full_name": "Jane Smith", "password": "securepass" }
```

**Response:** `201`
```json
{ "id": 1, "email": "jane@company.com", "full_name": "Jane Smith", "created_at": "..." }
```

---

### POST /api/auth/login/
Login with workspace credentials.

**Request:**
```json
{ "workspace_slug": "tech-soft-x92k", "username": "jane", "password": "securepass" }
```

**Response:** `200`
```json
{
  "access": "<jwt>",
  "refresh": "<jwt>",
  "user": { "id": 1, "email": "...", "full_name": "..." },
  "workspace": "tech-soft-x92k",
  "role": "manager"
}
```

---

### POST /api/auth/token/refresh/
Refresh access token.

**Request:** `{ "refresh": "<refresh_token>" }`

---

### GET /api/auth/me/
Get current user profile.

---

### GET /api/auth/{workspace_slug}/members/
List all workspace members. Requires membership.

---

### POST /api/auth/{workspace_slug}/developers/create/
Create a developer account. Requires manager role.

**Request:**
```json
{ "full_name": "Dev Name", "email": "dev@co.com", "username": "devname" }
```

**Response:** `201`
```json
{
  "membership": { "id": 2, "username": "devname", "role": "developer", ... },
  "generated_password": "aB3xK9mP",
  "login_url": "/workspace/tech-soft-x92k/login/"
}
```

---

## Workspace Endpoints

### GET/POST /api/workspaces/
List user's workspaces or create a new one.

**Create request:**
```json
{ "name": "My Company", "description": "Optional" }
```

**Create response:** `201` — workspace object with auto-generated slug.

---

### GET/PATCH /api/workspaces/{workspace_slug}/
Get or update workspace details.

---

### GET /api/workspaces/{workspace_slug}/stats/
Live workspace statistics.

**Response:**
```json
{
  "total_members": 5,
  "active_now": 3,
  "total_tasks": 42,
  "active_sessions": [
    { "username": "john", "task": "Fix login bug", "started_at": "..." }
  ]
}
```

---

## Task Endpoints

### GET /api/tasks/{workspace_slug}/
List tasks. Managers see all; developers see their own.

**Query params:** `?status=active|paused|completed`

---

### POST /api/tasks/{workspace_slug}/
Create a task.

**Request:** `{ "title": "Fix login bug", "description": "Optional" }`

---

### GET/PATCH/DELETE /api/tasks/{workspace_slug}/{task_id}/
Get, update, or delete a task.

---

### POST /api/tasks/{workspace_slug}/{task_id}/attachments/
Upload a file attachment. `multipart/form-data` with `file` field.

---

## Activity Endpoints

### POST /api/activity/{workspace_slug}/start/
Start a work session on a task. Closes any open session first.

**Request:** `{ "task_id": 5 }`

**Response:** `201` — ActivitySession object.

---

### POST /api/activity/{workspace_slug}/switch/
Switch from current task to another. Logs completion % and note.

**Request:**
```json
{ "next_task_id": 7, "completion_percentage": 35, "note": "Urgent request from manager" }
```

**Response:** `201` — new ActivitySession object.

---

### POST /api/activity/{workspace_slug}/stop/
Stop current session without starting a new one.

**Request:** `{ "completion_percentage": 60, "note": "End of day" }`

---

### GET /api/activity/{workspace_slug}/timeline/
My activity timeline.

**Query params:** `?date=2025-01-15`

---

### GET /api/activity/{workspace_slug}/timeline/{username}/
Any developer's timeline (manager access).

**Query params:** `?date=2025-01-15`

---

### GET /api/activity/{workspace_slug}/live/
Live status of all developers in workspace.

**Response:**
```json
[
  {
    "username": "john",
    "current_task": { "id": 5, "title": "Fix login bug", "started_at": "...", "completion": 35 },
    "last_seen": "..."
  },
  { "username": "jane", "current_task": null, "last_seen": "..." }
]
```

---

### GET /api/activity/{workspace_slug}/status/
My current status.

---

## Comment Endpoints

### GET/POST /api/comments/{workspace_slug}/tasks/{task_id}/
List or create comments on a task.

**Create request:** `{ "body": "Looks good @john, please review" }`

Mentions are auto-extracted and stored.

---

### GET /api/comments/{workspace_slug}/mentions/
My unread mentions.

---

### POST /api/comments/{workspace_slug}/mentions/{mention_id}/read/
Mark a mention as read.

---

### GET /api/comments/{workspace_slug}/suggest/?q=jo
Autocomplete @mention suggestions. Returns list of matching usernames.

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Validation error — check `detail` or field errors |
| 401 | Missing or invalid token |
| 403 | Not a workspace member or insufficient role |
| 404 | Resource not found |

## Pagination

List endpoints return paginated responses:
```json
{ "count": 42, "next": "...", "previous": null, "results": [...] }
```

Default page size: 20. Use `?page=2` to paginate.
