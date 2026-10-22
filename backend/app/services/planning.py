from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.context import ContextItem
from app.models.event import Event
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User
from app.schemas.planning import (
    DailyPlanningResponse,
    PlannedEvent,
    PlannedReminder,
    PlannedTask,
    PlanningContextItem,
    PlanningObservation,
)
from app.services.context_intelligence import (
    get_event_context,
    get_reminder_context,
    get_task_context,
)


def _utc_datetime(value: datetime) -> datetime:
    """Normalize a datetime for comparisons and sorting."""
    if value.tzinfo is None or value.utcoffset() is None:
        # Compatibility fallback for any existing naive database values.
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _serialize_context(
    items: list[ContextItem],
) -> list[PlanningContextItem]:
    return [
        PlanningContextItem(
            id=item.id,
            context_type=item.context_type,
            title=item.title,
            value=item.value,
            source=item.source,
            extra_data=item.extra_data,
        )
        for item in items
    ]


def build_daily_plan(
    db: Session,
    user_id: int,
    plan_date: date | None = None,
) -> DailyPlanningResponse:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise LookupError("Planning user not found")

    try:
        user_timezone = ZoneInfo(user.timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("The user's configured timezone is invalid") from exc

    if plan_date is None:
        plan_date = datetime.now(user_timezone).date()

    local_start = datetime.combine(
        plan_date,
        time.min,
        tzinfo=user_timezone,
    )
    local_end = datetime.combine(
        date.fromordinal(plan_date.toordinal() + 1),
        time.min,
        tzinfo=user_timezone,
    )

    day_start_utc = local_start.astimezone(timezone.utc)
    day_end_utc = local_end.astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)

    # Keep unfinished tasks, including tasks without a deadline.
    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.status.notin_(["completed", "cancelled"]),
        )
        .all()
    )

    priority_order = {"high": 0, "normal": 1, "low": 2}

    tasks.sort(
        key=lambda task: (
            priority_order.get(task.priority, 3),
            task.due_at is None,
            (
                _utc_datetime(task.due_at)
                if task.due_at is not None
                else datetime.max.replace(tzinfo=timezone.utc)
            ),
            task.id,
        )
    )

    planned_tasks = [
        PlannedTask(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            context=_serialize_context(get_task_context(db, task)),
        )
        for task in tasks
    ]

    observations: list[PlanningObservation] = []

    for task in tasks:
        if (
            task.due_at is not None
            and task.status != "completed"
            and _utc_datetime(task.due_at) < now_utc
        ):
            observations.append(
                PlanningObservation(
                    code="overdue_task",
                    message=f'Task "{task.title}" is past its deadline.',
                    entity_type="task",
                    entity_id=task.id,
                )
            )

    # Include events that overlap the local day. An event without an end
    # time is treated as a point event at its start time.
    events = (
        db.query(Event)
        .filter(
            Event.user_id == user_id,
            Event.starts_at < day_end_utc,
            or_(
                Event.ends_at > day_start_utc,
                and_(
                    Event.ends_at.is_(None),
                    Event.starts_at >= day_start_utc,
                ),
            ),
        )
        .order_by(Event.starts_at.asc(), Event.id.asc())
        .all()
    )

    planned_events = [
        PlannedEvent(
            id=event.id,
            title=event.title,
            description=event.description,
            starts_at=event.starts_at,
            ends_at=event.ends_at,
            context=_serialize_context(get_event_context(db, event)),
        )
        for event in events
    ]

    # Only pending reminders are presented as upcoming actions.
    reminders = (
        db.query(Reminder)
        .filter(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.remind_at >= day_start_utc,
            Reminder.remind_at < day_end_utc,
        )
        .order_by(Reminder.remind_at.asc(), Reminder.id.asc())
        .all()
    )

    planned_reminders = [
        PlannedReminder(
            id=reminder.id,
            title=reminder.title,
            message=reminder.message,
            remind_at=reminder.remind_at,
            status=reminder.status,
            context=_serialize_context(
                get_reminder_context(db, reminder)
            ),
        )
        for reminder in reminders
    ]

    return DailyPlanningResponse(
        plan_date=plan_date,
        timezone=user.timezone,
        tasks=planned_tasks,
        events=planned_events,
        reminders=planned_reminders,
        observations=observations,
    )