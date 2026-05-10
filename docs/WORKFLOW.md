# WORKFLOW.md — Task Switching Lifecycle

## The Core Problem

```
09:00  Developer starts Task A
10:30  Manager: "Drop everything, do Task D"
10:30  Developer switches → Task A paused at 40%
12:00  Emergency: Task E must be done NOW
12:00  Developer switches → Task D paused at 20%
13:30  Task E completed → 100%
13:30  Developer resumes Task D
15:00  Task D completed → 100%
15:00  Developer resumes Task A
17:00  End of day → Task A at 65%
```

Without FlowTrace: manager sees Task A "in progress" all day with no visibility.
With FlowTrace: complete timeline with every switch, duration, and completion state.

## Session Lifecycle

```
start_session(task_id)
  │
  ├── Close any open session (completion_at_end = current task %)
  ├── Update previous task status → "paused"
  ├── Create new ActivitySession (started_at = now)
  ├── Update task status → "active"
  └── Update DeveloperStatus.current_session

switch_task(next_task_id, completion_percentage, note)
  │
  ├── Close current session with provided completion % and note
  ├── Update current task: completion_percentage, status → "paused"
  └── Call start_session(next_task_id)

stop_session(completion_percentage, note)
  │
  ├── Close current session
  ├── Update task: completion_percentage, status → "paused"
  └── Set DeveloperStatus.current_session = null
```

## ActivitySession States

```
[created] → started_at set, ended_at = null  → "ACTIVE"
[closed]  → ended_at set, completion_at_end set → "HISTORICAL"
```

Sessions are never deleted. The full chain of sessions for a task forms its complete history.

## Timeline Reconstruction

To reconstruct a developer's day:

```sql
SELECT * FROM activity_activitysession
WHERE membership_id = X
  AND started_at::date = '2025-01-15'
ORDER BY started_at ASC;
```

Each row is one work block. Gaps between `ended_at` and next `started_at` = time not tracked (breaks, meetings, etc.).

## Completion Percentage Flow

- `completion_at_start`: snapshot of task % when session began (for historical accuracy)
- `completion_at_end`: what developer reported when switching/stopping
- `Task.completion_percentage`: always reflects the latest reported value

This means you can see: "Task went from 0% → 30% → 30% → 65% → 100%" across multiple sessions.

## DeveloperStatus — Live Tracking

`DeveloperStatus` is a single-row-per-developer table that always points to the current open session. This enables O(1) "what is everyone doing right now" queries without scanning all sessions.

```python
# Live dashboard query
DeveloperStatus.objects.filter(
    membership__workspace__slug=slug
).select_related('current_session__task')
```

---

## Collaboration Lifecycle

### The Problem It Solves

```
14:00  Alex is stuck on Task X (payment bug)
14:05  Alex requests collaboration from John
14:06  John receives notification on dashboard
14:07  John accepts
         → TaskCollaborator created for John on Task X
         → CollaborationActivityLog: request_sent, request_accepted, collab_started
14:07  Both Alex and John work on Task X
         → Task X appears in both developers' activity context
16:00  Bug fixed. John leaves collaboration.
         → TaskCollaborator.is_active = False, left_at = 16:00
         → CollaborationActivityLog: collab_ended
```

Without FlowTrace: John's 2 hours on Task X are invisible. Alex gets all the credit.
With FlowTrace: complete collaboration trail with timestamps, participants, and history.

### Collaboration Request Flow

```
send_collaboration_request(target_username, task_id, message)
  │
  ├── Validate target is in same workspace
  ├── Validate task belongs to workspace
  ├── Create or re-open CollaborationRequest (status=pending)
  └── Write CollaborationActivityLog: request_sent

respond_to_request(request_id, action='accept'|'reject')
  │
  ├── Update CollaborationRequest.status
  ├── Set responded_at = now
  ├── Write log: request_accepted or request_rejected
  └── [if accept]
        ├── Create/reactivate TaskCollaborator
        └── Write log: collab_started

leave_collaboration(task_id)
  │
  ├── Set TaskCollaborator.is_active = False, left_at = now
  └── Write log: collab_ended
```

### Collaboration Status Transitions

```
[pending] ──accept──► [accepted]
[pending] ──reject──► [rejected]
[pending] ──cancel──► [cancelled]
[rejected|cancelled] ──re-request──► [pending]  (same row re-opened)
```

### Shared Activity Visibility

When a developer accepts a collaboration request, they appear in:

- `TaskCollaborator` list on the task detail page (active/inactive status + join/leave timestamps)
- `CollaborationActivityLog` for the task (full permanent history)
- **Developer timeline** — `ActivitySession` objects include a `collaborators` field listing co-workers on the same task. The timeline has two tabs: "My Sessions" (own sessions with collab badges) and "Collaborated Tasks" (sessions on tasks the developer joined as a collaborator)
- **Developer Collaboration section** — two tabs: "Pending Requests" (incoming with Accept/Reject) and "History" (all past sent/received requests with status)
- **Manager overview cards** — each live developer card shows active collaborators as pills when the current task has co-workers
- **Manager Collaborations section** — dedicated view listing all tasks in the workspace with active collaborators, showing all participant usernames and join times
- **Manager timeline** — sessions with collaborators show a collab badge and accent-colored card border

### Workspace Isolation Guarantee

Every collaboration lookup filters by `workspace__slug`:

```python
# Member search — only same-workspace members returned
WorkspaceMembership.objects.filter(workspace__slug=workspace_slug, is_active=True)

# Request creation — target must exist in same workspace
WorkspaceMembership.objects.get(workspace__slug=workspace_slug, username=target_username)
```

Cross-workspace collaboration is structurally impossible, not just policy-enforced.
