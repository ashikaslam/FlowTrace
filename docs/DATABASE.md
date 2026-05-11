# DATABASE.md — FlowTrace Database Design

## Overview

FlowTrace uses a multi-tenant architecture where all data is scoped to a `Workspace`. No cross-workspace data leakage is possible at the query level.

## Entity Relationship Diagram

```
User (global)
  │
  ├──< WorkspaceMembership >──── Workspace (owned by User)
  │         │
  │         ├──< Task (workspace-scoped)
  │         │       ├──< TaskAttachment
  │         │       ├──< TaskComment ──< Mention
  │         │       └──< ActivitySession
  │         │
  │         ├──< ActivitySession
  │         └──── DeveloperStatus (1:1)
  │
  │    Task also has:
  │         ├──< CollaborationRequest (requester → target)
  │         ├──< TaskCollaborator
  │         └──< CollaborationActivityLog
```

## Models

### User
Global account. Email is the unique identifier. One user can belong to multiple workspaces.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| email | EmailField | unique globally |
| full_name | CharField | |
| avatar_url | URLField | public image URL from ImgBB, blank by default |
| is_active | Boolean | |
| created_at | DateTime | |

### Workspace
Isolated tenant container. Slug is auto-generated and globally unique.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| name | CharField | display name |
| slug | SlugField | unique, auto-generated (e.g. `tech-soft-x92k`) |
| owner | FK → User | |
| description | TextField | optional |
| logo | ImageField | optional |
| created_at | DateTime | |

**Slug generation**: `{slugified-name}-{4-char-random}` — retries on collision.

### WorkspaceMembership
Joins a User to a Workspace with a role and workspace-scoped username.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| user | FK → User | |
| workspace | FK → Workspace | |
| role | CharField | `manager` or `developer` |
| username | CharField | unique within workspace only |
| is_active | Boolean | |
| joined_at | DateTime | |

**Unique constraint**: `(workspace, username)` — same username allowed across different workspaces.

**Index**: `(workspace, user)` for fast membership lookups.

### Task
Developer-created work item. Scoped to workspace.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| workspace | FK → Workspace | |
| created_by | FK → WorkspaceMembership | |
| title | CharField | |
| description | TextField | optional |
| status | CharField | `active`, `paused`, `completed` |
| completion_percentage | SmallInt | 0–100 |
| created_at | DateTime | |
| updated_at | DateTime | auto |

**Indexes**: `(workspace, status)`, `(workspace, created_by)`

### ActivitySession
The core tracking model. One row = one continuous work session on a task.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| membership | FK → WorkspaceMembership | who worked |
| task | FK → Task | what they worked on |
| started_at | DateTime | session start |
| ended_at | DateTime | null = currently active |
| completion_at_start | SmallInt | task % when session began |
| completion_at_end | SmallInt | task % when session ended |
| switch_note | TextField | optional note on switch/stop |

**Indexes**: `(membership, started_at)`, `(task, started_at)`

**History preservation**: Sessions are NEVER deleted. They form the immutable audit trail.

**Computed field** (`collaborators`): serializer-level field — returns usernames of other active `TaskCollaborator` records on the same task, excluding the session owner. Used in timeline and live-status responses.

### DeveloperStatus
One row per membership. Tracks the currently active session for fast live-status queries.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| membership | OneToOne → WorkspaceMembership | |
| current_session | FK → ActivitySession | null = idle |
| last_seen | DateTime | auto-updated |

**Computed field** (`current_task.collaborators`): serializer-level field — when a developer is active, the response includes a `collaborators` list of other active `TaskCollaborator` usernames on the same task. Powers the manager overview cards.

### TaskComment + Mention

`TaskComment`: body text with `@mention` support. Mentions are auto-extracted on save.

`Mention`: links a comment to a mentioned WorkspaceMembership. Unique per `(comment, mentioned_user)`.

---

## Collaboration Models

### CollaborationRequest
Records a collaboration invitation from one workspace member to another on a specific task.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| requester | FK → WorkspaceMembership | who sent the request |
| target | FK → WorkspaceMembership | who received it |
| task | FK → Task | task collaboration is requested on |
| workspace | FK → Workspace | denormalized for fast workspace-scoped queries |
| status | CharField | `pending`, `accepted`, `rejected`, `cancelled` |
| message | TextField | optional context message |
| created_at | DateTime | |
| responded_at | DateTime | null until responded or cancelled |

**Unique constraint**: `(requester, target, task)` — one record per pair per task. Re-sending after rejection/cancellation re-opens the same row as `pending`.

**Indexes**: `(target, status)` for fast inbox queries, `(task, status)` for task-level views.

### TaskCollaborator
Tracks who is (or was) actively collaborating on a task. Created when a collaboration request is accepted.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| task | FK → Task | |
| member | FK → WorkspaceMembership | the collaborating developer |
| joined_at | DateTime | when collaboration started |
| left_at | DateTime | null = still active |
| is_active | Boolean | fast filter for current collaborators |

**Unique constraint**: `(task, member)` — one record per developer per task; reactivated on re-join.

**Index**: `(task, is_active)` for live collaborator lookups.

### CollaborationActivityLog
Permanent, append-only audit trail of every collaboration event on a task.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| task | FK → Task | |
| actor | FK → WorkspaceMembership | who performed the action |
| action_type | CharField | see action types below |
| metadata | JSONField | contextual data (target, requester, etc.) |
| timestamp | DateTime | |

**Action types:**

| Value | Meaning |
|-------|---------|
| `request_sent` | Developer sent a collaboration request |
| `request_accepted` | Target accepted the request |
| `request_rejected` | Target rejected the request |
| `request_cancelled` | Requester cancelled before response |
| `collab_started` | Active collaboration session began |
| `collab_ended` | Developer left the collaboration |

**Index**: `(task, timestamp)` for chronological log queries.

**History preservation**: Log rows are NEVER deleted. They form the permanent collaboration audit trail alongside `ActivitySession`.

## Multi-Tenant Isolation Strategy

Every query that touches workspace data filters by `workspace__slug` from the URL. The `IsWorkspaceMember` permission class enforces this at the API layer. No global task/activity queries exist — all are scoped.

## Activity History Preservation

`ActivitySession` rows are append-only. The `close()` method only fills in `ended_at` and `completion_at_end`. No sessions are ever deleted, ensuring complete historical timeline reconstruction.
