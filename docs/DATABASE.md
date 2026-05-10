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
```

## Models

### User
Global account. Email is the unique identifier. One user can belong to multiple workspaces.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| email | EmailField | unique globally |
| full_name | CharField | |
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

### DeveloperStatus
One row per membership. Tracks the currently active session for fast live-status queries.

| Field | Type | Notes |
|-------|------|-------|
| id | BigInt PK | |
| membership | OneToOne → WorkspaceMembership | |
| current_session | FK → ActivitySession | null = idle |
| last_seen | DateTime | auto-updated |

### TaskComment + Mention

`TaskComment`: body text with `@mention` support. Mentions are auto-extracted on save.

`Mention`: links a comment to a mentioned WorkspaceMembership. Unique per `(comment, mentioned_user)`.

## Multi-Tenant Isolation Strategy

Every query that touches workspace data filters by `workspace__slug` from the URL. The `IsWorkspaceMember` permission class enforces this at the API layer. No global task/activity queries exist — all are scoped.

## Activity History Preservation

`ActivitySession` rows are append-only. The `close()` method only fills in `ended_at` and `completion_at_end`. No sessions are ever deleted, ensuring complete historical timeline reconstruction.
