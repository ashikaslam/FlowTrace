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
