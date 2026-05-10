from django.db import transaction
from django.utils import timezone
from .models import ActivitySession, DeveloperStatus
from apps.tasks.models import Task


@transaction.atomic
def start_session(membership, task_id):
    """Start working on a task. Closes any open session first."""
    task = Task.objects.get(id=task_id, workspace=membership.workspace)

    # Close existing open session if any
    status, _ = DeveloperStatus.objects.get_or_create(membership=membership)
    if status.current_session and not status.current_session.ended_at:
        status.current_session.close(
            completion_percentage=status.current_session.task.completion_percentage
        )

    session = ActivitySession.objects.create(
        membership=membership,
        task=task,
        completion_at_start=task.completion_percentage,
    )

    # Mark task as active
    Task.objects.filter(id=task_id).update(status=Task.STATUS_ACTIVE)

    status.current_session = session
    status.save(update_fields=["current_session", "last_seen"])
    return session


@transaction.atomic
def switch_task(membership, next_task_id, completion_percentage, note=""):
    """Close current session and open a new one on a different task."""
    status, _ = DeveloperStatus.objects.get_or_create(membership=membership)

    if status.current_session and not status.current_session.ended_at:
        current_task = status.current_session.task
        status.current_session.close(completion_percentage=completion_percentage, note=note)
        # Update task completion and pause it
        Task.objects.filter(id=current_task.id).update(
            completion_percentage=completion_percentage,
            status=Task.STATUS_PAUSED,
        )

    return start_session(membership, next_task_id)


@transaction.atomic
def stop_session(membership, completion_percentage, note=""):
    """Stop current session without starting a new one."""
    status, _ = DeveloperStatus.objects.get_or_create(membership=membership)
    if status.current_session and not status.current_session.ended_at:
        task = status.current_session.task
        status.current_session.close(completion_percentage=completion_percentage, note=note)
        Task.objects.filter(id=task.id).update(
            completion_percentage=completion_percentage,
            status=Task.STATUS_PAUSED,
        )
        status.current_session = None
        status.save(update_fields=["current_session", "last_seen"])
