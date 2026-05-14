# API.md — FlowTrace REST API

## Authentication

All endpoints (except login and register-workspace) require an active Django session. The session cookie is set automatically on login and sent by the browser on every request — no manual token handling needed.

All mutating requests (`POST`, `PATCH`, `PUT`, `DELETE`) must include the CSRF token:

```
X-CSRFToken: <value of csrftoken cookie>
```

---

## Auth Endpoints

### POST /api/auth/register-workspace/
Create a new user account + workspace in one step. Sets session cookie on success.

**Request:**
```json
{ "email": "jane@company.com", "full_name": "Jane Smith", "password": "securepass", "workspace_name": "My Company" }
```

**Response:** `201`
```json
{
  "workspace_slug": "tech-soft-x92k",
  "workspace_name": "My Company",
  "username": "jane",
  "role": "manager",
  "login_url": "/workspace/tech-soft-x92k/login/"
}
```

---

### POST /api/auth/login/
Login with workspace credentials. Sets session cookie on success.

**Request:**
```json
{ "workspace_slug": "tech-soft-x92k", "username": "jane", "password": "securepass" }
```

**Response:** `200`
```json
{
  "user": { "id": 1, "email": "...", "full_name": "..." },
  "workspace": "tech-soft-x92k",
  "role": "manager"
}
```

---

### POST /api/auth/logout/
Destroy the current session.

**Response:** `200` `{ "detail": "Logged out." }`

---

### GET /api/auth/me/
Get current user profile. Returns `id`, `email`, `full_name`, `avatar_url`, `created_at`.

---

### PATCH /api/auth/{workspace_slug}/profile/update/
Update the current user's profile. All fields optional.

**Request:**
```json
{ "full_name": "Jane Smith", "email": "jane@new.com", "username": "jane_new" }
```

**Response:** `200`
```json
{ "full_name": "Jane Smith", "email": "jane@new.com" }
```

**Errors:**
- `400` — Email already in use, or username already taken in this workspace

---

### POST /api/auth/avatar/upload/
Upload a profile picture. Image is stored on ImgBB and the public URL is saved to the user.

**Request:** `multipart/form-data` with `avatar` field (image file, max 5 MB).

**Response:** `200`
```json
{ "avatar_url": "https://i.ibb.co/..." }
```

**Errors:**
- `400` — No file, file exceeds 5 MB, or non-image MIME type
- `502` — ImgBB upload failed

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
My activity timeline. Each session includes a `collaborators` field listing other active collaborators on that task.

**Query params:** `?date=2025-01-15`

**Response (session object):**
```json
{
  "id": 12,
  "task_id": 5,
  "task_title": "Fix payment API",
  "username": "alex",
  "started_at": "...",
  "ended_at": "...",
  "duration_seconds": 3600,
  "completion_at_start": 20,
  "completion_at_end": 65,
  "switch_note": "",
  "collaborators": ["john"]
}
```

---

### GET /api/activity/{workspace_slug}/timeline/{username}/
Any developer's timeline (manager access). Also includes `collaborators` per session.

**Query params:** `?date=2025-01-15`

---

### GET /api/activity/{workspace_slug}/live/
Live status of all developers in workspace.

**Response:**
```json
[
  {
    "username": "john",
    "current_task": {
      "id": 5,
      "title": "Fix login bug",
      "started_at": "...",
      "completion": 35,
      "collaborators": ["mike", "sarah"]
    },
    "last_seen": "..."
  },
  { "username": "jane", "current_task": null, "last_seen": "..." }
]
```

`collaborators` lists the usernames of other active collaborators on the same task. Empty array when working solo.

---

### GET /api/activity/{workspace_slug}/status/
My current status.

---

## Collaboration Endpoints

All collaboration endpoints are workspace-scoped. Cross-workspace collaboration is structurally impossible — member lookups always filter by `workspace__slug`.

### GET /api/activity/{workspace_slug}/collab/members/?q=
List all workspace members available for collaboration. Returns all members when `q` is empty, or filters by username/full name when provided. Now includes `avatar_url`.

**Query params:** `?q=john` (optional)

**Response:**
```json
[
  { "username": "john", "full_name": "John Smith", "avatar_url": "https://i.ibb.co/..." },
  { "username": "mike", "full_name": "Mike Lee", "avatar_url": "" }
]
```

Returns up to 50 results. Never includes the requesting developer themselves.

---

### GET /api/activity/{workspace_slug}/collab/tasks/{task_id}/member-status/
Returns the current collaboration status of every workspace member for a specific task, from the perspective of the requesting developer.

**Response:**
```json
{
  "john": "collaborating",
  "mike": "pending",
  "sarah": "rejected",
  "alex": "none"
}
```

**Status values:**

| Value | Meaning |
|-------|---------|
| `collaborating` | Member is an active `TaskCollaborator` on this task |
| `pending` | Requester has a pending outgoing request to this member |
| `rejected` | Member previously rejected the requester's request |
| `none` | No active relationship — request can be sent freely |

Used by the collaboration modal to show status badges and block/warn before sending duplicate requests.

---

### POST /api/activity/{workspace_slug}/collab/request/
Send a collaboration request to a workspace developer on a specific task.

**Request:**
```json
{ "target_username": "john", "task_id": 5, "message": "Need help with the payment logic" }
```

**Response:** `201` — CollaborationRequest object.
```json
{
  "id": 1,
  "requester_username": "alex",
  "target_username": "john",
  "task_id": 5,
  "task_title": "Fix payment API issue",
  "status": "pending",
  "message": "Need help with the payment logic",
  "created_at": "...",
  "responded_at": null
}
```

If a previous request to the same developer on the same task was rejected/cancelled, it is re-opened as `pending`.

**Errors:**
- `400` — Request already pending, or self-request
- `404` — Developer or task not found in workspace

---

### GET /api/activity/{workspace_slug}/collab/incoming/
List all pending collaboration requests received by the current developer.

**Response:** Paginated list of CollaborationRequest objects with `status=pending`.

---

### GET /api/activity/{workspace_slug}/collab/history/
All collaboration requests involving the current developer (both sent and received, **all statuses including pending**), sorted newest first.

**Response:**
```json
[
  {
    "id": 1,
    "direction": "sent",
    "other_username": "john",
    "task_id": 5,
    "task_title": "Fix payment API",
    "status": "pending",
    "message": "Need help with the payment logic",
    "created_at": "...",
    "responded_at": null
  },
  {
    "id": 2,
    "direction": "received",
    "other_username": "alex",
    "task_id": 8,
    "task_title": "Auth bug",
    "status": "rejected",
    "message": "",
    "created_at": "...",
    "responded_at": "..."
  }
]
```

`direction`: `sent` = current developer sent the request, `received` = they received it.

Note: received requests with `pending` status are excluded here since they appear in the `incoming/` endpoint instead.

---

### POST /api/activity/{workspace_slug}/collab/{request_id}/respond/
Accept or reject an incoming collaboration request.

**Request:** `{ "action": "accept" }` or `{ "action": "reject" }`

**On accept:**
- Request status → `accepted`
- `TaskCollaborator` record created (or reactivated)
- Two `CollaborationActivityLog` entries written: `request_accepted` + `collab_started`

**On reject:**
- Request status → `rejected`
- One log entry written: `request_rejected`

**Response:** Updated CollaborationRequest object.

**Errors:** `404` if request not found or not pending.

---

### POST /api/activity/{workspace_slug}/collab/{request_id}/cancel/
Cancel a pending outgoing request (requester only).

**Response:** `{ "status": "cancelled" }`

---

### GET /api/activity/{workspace_slug}/collab/tasks/{task_id}/collaborators/
List all collaborators on a task (active and past).

**Response:**
```json
[
  { "id": 1, "username": "john", "full_name": "John Smith", "joined_at": "...", "left_at": null, "is_active": true },
  { "id": 2, "username": "mike", "full_name": "Mike Lee", "joined_at": "...", "left_at": "...", "is_active": false }
]
```

---

### GET /api/activity/{workspace_slug}/collab/tasks/{task_id}/logs/
Full collaboration history log for a task. Permanent and append-only.

**Response:**
```json
[
  { "id": 1, "actor_username": "alex", "action_type": "request_sent", "metadata": { "target": "john" }, "timestamp": "..." },
  { "id": 2, "actor_username": "john", "action_type": "request_accepted", "metadata": { "requester": "alex" }, "timestamp": "..." },
  { "id": 3, "actor_username": "john", "action_type": "collab_started", "metadata": { "with": "alex" }, "timestamp": "..." }
]
```

**Action types:** `request_sent`, `request_accepted`, `request_rejected`, `request_cancelled`, `collab_started`, `collab_ended`

---

### GET /api/activity/{workspace_slug}/collab/my-timeline/
Sessions on tasks where the current developer is a collaborator (tasks they didn't create but accepted collaboration on).

**Query params:** `?date=2025-01-15`

**Response:** Same session object format as the main timeline, including `collaborators` field.

---

### GET /api/activity/{workspace_slug}/collab/workspace/
Manager endpoint. Returns all tasks in the workspace that currently have active collaborators, grouped by task.

**Response:**
```json
[
  {
    "task_id": 5,
    "task_title": "Fix payment API",
    "since": "...",
    "collaborators": [
      { "username": "john", "full_name": "John Smith", "joined_at": "..." },
      { "username": "mike", "full_name": "Mike Lee", "joined_at": "..." }
    ]
  }
]
```

---

### POST /api/activity/{workspace_slug}/collab/tasks/{task_id}/leave/
Leave an active collaboration on a task.

**Response:** `{ "status": "left" }`

Writes a `collab_ended` log entry and sets `TaskCollaborator.is_active = false` with `left_at` timestamp.

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

### GET /api/comments/{workspace_slug}/suggest/?q=jo
Autocomplete @mention suggestions. Returns list of matching usernames.

---

## Quick Notes Endpoints

### GET /api/notes/{workspace_slug}/
List notes visible to the current user.
- Developers see their own personal notes + all team notes
- Managers see all notes (personal and team)

Response is ordered by pinned first, then most recently updated.

---

### POST /api/notes/{workspace_slug}/
Create a note.

**Request:**
```json
{ "title": "Remember to update staging", "content": "Deploy by Friday", "color": "yellow", "note_type": "personal" }
```

- Developers can only create `personal` notes (the `note_type` field is ignored and forced to `personal`)
- Managers can create `personal` or `team` notes

**Response:** `201` — QuickNote object

---

### PATCH /api/notes/{workspace_slug}/{note_id}/
Update a note. Owner only (managers can also edit team notes).

**Request:** Any subset of `title`, `content`, `color`, `note_type`, `is_pinned`

---

### DELETE /api/notes/{workspace_slug}/{note_id}/
Delete a note. Owner only (managers can also delete team notes).

**Response:** `204 No Content`

---

### POST /api/notes/{workspace_slug}/{note_id}/pin/
Toggle pin status of a note. Owner or manager only.

**Response:**
```json
{ "is_pinned": true }
```

---

## Request Size Limits

All requests pass through `RequestSizeLimitMiddleware`:

| Content type | Max size | Error |
|---|---|---|
| `multipart/form-data` (file uploads) | 7 MB | `413` |
| JSON / everything else | 512 KB | `413` |

The largest realistic JSON payload in FlowTrace is a task with a long description (~5 KB). 512 KB is intentionally generous.

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Validation error — check `detail` or field errors |
| 401 | Not authenticated (no active session) |
| 403 | Not a workspace member or insufficient role |
| 404 | Resource not found |

## Pagination

List endpoints return paginated responses:
```json
{ "count": 42, "next": "...", "previous": null, "results": [...] }
```

Default page size: 20. Use `?page=2` to paginate.
