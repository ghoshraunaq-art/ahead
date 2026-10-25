
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.context import ContextItem
from app.models.context_links import TaskContext
from app.models.event import Event
from app.models.task import Task
from app.models.user import User
from app.services.recommendations import generate_recommendations


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    session = TestingSession()

    session.add(
        User(
            id=1,
            name="Test User",
            email="test@ahead.local",
            timezone="UTC",
        )
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def add_task(
    db,
    *,
    title="Test task",
    user_id=1,
    status="pending",
    priority="normal",
    due_at=None,
):
    task = Task(
        user_id=user_id,
        title=title,
        description=None,
        status=status,
        priority=priority,
        due_at=due_at,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def add_context(db, *, user_id=1, importance="high"):
    item = ContextItem(
        user_id=user_id,
        context_type="constraint",
        title="Study location",
        value="I need a quiet environment",
        source="manual",
        extra_data={"importance": importance},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def test_overdue_and_due_soon_tasks_are_recommended(db):
    now = datetime.now(timezone.utc)

    overdue = add_task(
        db,
        title="Overdue task",
        due_at=now - timedelta(hours=1),
    )
    due_soon = add_task(
        db,
        title="Upcoming deadline",
        due_at=now + timedelta(hours=12),
    )
    completed = add_task(
        db,
        title="Completed task",
        status="completed",
        due_at=now - timedelta(hours=1),
    )
    cancelled = add_task(
        db,
        title="Cancelled task",
        status="cancelled",
        due_at=now + timedelta(hours=12),
    )

    result = generate_recommendations(db, user_id=1)

    matching = {
        (item.code, item.entity_id)
        for item in result.recommendations
    }

    assert ("overdue_task", overdue.id) in matching
    assert ("task_due_soon", due_soon.id) in matching

    excluded_ids = {completed.id, cancelled.id}
    assert not any(
        item.entity_type == "task" and item.entity_id in excluded_ids
        for item in result.recommendations
    )


def test_high_importance_constraint_is_included(db):
    task = add_task(db, title="Study DBMS")
    context = add_context(db, importance="high")

    db.add(TaskContext(task_id=task.id, context_id=context.id))
    db.commit()

    result = generate_recommendations(db, user_id=1)

    recommendation = next(
        item
        for item in result.recommendations
        if item.code == "task_constraint"
        and item.entity_id == task.id
    )

    assert recommendation.priority == "high"
    assert recommendation.context_ids == [context.id]
    assert "quiet environment" in recommendation.message


def test_low_importance_constraint_gets_normal_priority(db):
    task = add_task(db, title="Read notes")
    context = add_context(db, importance="low")

    db.add(TaskContext(task_id=task.id, context_id=context.id))
    db.commit()

    result = generate_recommendations(db, user_id=1)

    recommendation = next(
        item
        for item in result.recommendations
        if item.code == "task_constraint"
        and item.entity_id == task.id
    )

    assert recommendation.priority == "normal"


def test_only_upcoming_events_are_recommended(db):
    now = datetime.now(timezone.utc)

    upcoming = Event(
        user_id=1,
        title="Upcoming class",
        description=None,
        starts_at=now + timedelta(hours=1),
        ends_at=now + timedelta(hours=2),
    )
    past = Event(
        user_id=1,
        title="Past class",
        description=None,
        starts_at=now - timedelta(hours=2),
        ends_at=now - timedelta(hours=1),
    )
    db.add_all([upcoming, past])
    db.commit()
    db.refresh(upcoming)
    db.refresh(past)

    result = generate_recommendations(db, user_id=1)

    upcoming_ids = {
        item.entity_id
        for item in result.recommendations
        if item.code == "upcoming_event"
    }

    assert upcoming.id in upcoming_ids
    assert past.id not in upcoming_ids


def test_recommendations_do_not_include_another_users_tasks(db):
    own_task = add_task(
        db,
        title="My overdue task",
        user_id=1,
        due_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    other_user = User(
        id=2,
        name="Another User",
        email="another@ahead.local",
        timezone="UTC",
    )
    db.add(other_user)
    db.commit()

    other_task = add_task(
        db,
        title="Private task",
        user_id=2,
        due_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    result = generate_recommendations(db, user_id=1)

    overdue_ids = {
        item.entity_id
        for item in result.recommendations
        if item.code == "overdue_task"
    }

    assert own_task.id in overdue_ids
    assert other_task.id not in overdue_ids


def test_invalid_user_timezone_is_rejected(db):
    user = db.query(User).filter(User.id == 1).one()
    user.timezone = "Invalid/Timezone"
    db.commit()

    with pytest.raises(ValueError, match="timezone is invalid"):
        generate_recommendations(db, user_id=1)


def test_missing_user_is_rejected(db):
    with pytest.raises(LookupError, match="user not found"):
        generate_recommendations(db, user_id=999)


def test_empty_database_data_returns_no_recommendations(db):
    result = generate_recommendations(db, user_id=1)

    assert result.recommendations == []
    assert result.timezone == "UTC"


def test_recommendations_are_sorted_by_priority(db):
    now = datetime.now(timezone.utc)

    low = add_task(
        db,
        title="Low priority task",
        priority="low",
        due_at=now + timedelta(hours=5),
    )
    high = add_task(
        db,
        title="High priority task",
        priority="high",
        due_at=now + timedelta(hours=5),
    )
    normal = add_task(
        db,
        title="Normal priority task",
        priority="normal",
        due_at=now + timedelta(hours=5),
    )

    result = generate_recommendations(db, user_id=1)

    due_soon = [
        item
        for item in result.recommendations
        if item.code == "task_due_soon"
    ]

    assert [item.entity_id for item in due_soon] == [
        high.id,
        normal.id,
        low.id,
    ]
