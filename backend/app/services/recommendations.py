from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.task import Task
from app.models.user import User
from app.schemas.recommendation import (
    Recommendation,
    RecommendationResponse,
)
from app.services.context_intelligence import (
    get_event_context,
    get_task_context,
)


def _as_utc(value: datetime) -> datetime:
    """Normalize datetimes before comparing them."""
    if value.tzinfo is None or value.utcoffset() is None:
        # Defensive fallback for legacy naive database values.
        value = value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def generate_recommendations(
    db: Session,
    user_id: int,
) -> RecommendationResponse:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise LookupError("Recommendation user not found")

    try:
        ZoneInfo(user.timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(
            "The user's configured timezone is invalid"
        ) from exc

    now = datetime.now(timezone.utc)
    due_soon_cutoff = now + timedelta(hours=24)
    upcoming_event_cutoff = now + timedelta(hours=2)

    recommendations: list[Recommendation] = []

    # Rule 1: Unfinished tasks with deadlines in the past.
    # Rule 2: Unfinished tasks due within the next 24 hours.
    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == user_id,
            Task.status.notin_(["completed", "cancelled"]),
        )
        .all()
    )

    for task in tasks:
        task_context = get_task_context(db, task)
        context_ids = [item.id for item in task_context]

        if task.due_at is not None:
            due_at_utc = _as_utc(task.due_at)

            if due_at_utc < now:
                recommendations.append(
                    Recommendation(
                        code="overdue_task",
                        title="Review an overdue task",
                        message=(
                            f'"{task.title}" is past its deadline. '
                            "Review its status and decide whether to "
                            "complete it or reschedule it."
                        ),
                        priority="high",
                        entity_type="task",
                        entity_id=task.id,
                        context_ids=context_ids,
                    )
                )
            elif due_at_utc <= due_soon_cutoff:
                task_priority = (
                    task.priority
                    if task.priority in {"high", "normal", "low"}
                    else "normal"
                )

                recommendations.append(
                    Recommendation(
                        code="task_due_soon",
                        title="Plan a task due soon",
                        message=(
                            f'"{task.title}" is due within the next '
                            "24 hours. Review your available time and "
                            "plan when to work on it."
                        ),
                        priority=task_priority,
                        entity_type="task",
                        entity_id=task.id,
                        context_ids=context_ids,
                    )
                )

        # Rule 3: Surface constraints explicitly linked to unfinished tasks.
        for item in task_context:
            if item.context_type != "constraint":
                continue

            importance = (
                item.extra_data.get("importance")
                if isinstance(item.extra_data, dict)
                else None
            )
            recommendation_priority = (
                "high" if importance == "high" else "normal"
            )

            recommendations.append(
                Recommendation(
                    code="task_constraint",
                    title="Account for a task constraint",
                    message=(
                        f'Before planning "{task.title}", account for '
                        f'the constraint "{item.title}": {item.value}'
                    ),
                    priority=recommendation_priority,
                    entity_type="task",
                    entity_id=task.id,
                    context_ids=[item.id],
                )
            )

    # Rule 4: Suggest preparation for events starting within two hours.
    events = (
        db.query(Event)
        .filter(Event.user_id == user_id)
        .all()
    )

    for event in events:
        starts_at_utc = _as_utc(event.starts_at)

        if now <= starts_at_utc <= upcoming_event_cutoff:
            event_context = get_event_context(db, event)
            event_constraints = [
                item
                for item in event_context
                if item.context_type == "constraint"
            ]

            if event_constraints:
                constraint_text = "; ".join(
                    f"{item.title}: {item.value}"
                    for item in event_constraints
                )
                message = (
                    f'"{event.title}" starts within two hours. '
                    f"Prepare for it and account for these constraints: "
                    f"{constraint_text}"
                )
            else:
                message = (
                    f'"{event.title}" starts within two hours. '
                    "Review its details and prepare before it begins."
                )

            recommendations.append(
                Recommendation(
                    code="upcoming_event",
                    title="Prepare for an upcoming event",
                    message=message,
                    priority="normal",
                    entity_type="event",
                    entity_id=event.id,
                    context_ids=[item.id for item in event_context],
                )
            )

    # Stable ordering: priority first, then rule code and entity ID.
    priority_order = {"high": 0, "normal": 1, "low": 2}

    recommendations.sort(
        key=lambda recommendation: (
            priority_order[recommendation.priority],
            recommendation.code,
            recommendation.entity_id,
            tuple(recommendation.context_ids),
        )
    )

    return RecommendationResponse(
        generated_at=now,
        timezone=user.timezone,
        recommendations=recommendations,
    )