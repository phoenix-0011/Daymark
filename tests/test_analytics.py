from datetime import date, datetime, timedelta

from daymark.analytics import calculate_insights, completion_streak
from daymark.models import Task


def completed_on(day: date, category: str = "Work") -> Task:
    return Task(
        id=None,
        title="Done",
        category_name=category,
        completed_at=datetime.combine(day, datetime.min.time()),
    )


def pending_on(day: date | None) -> Task:
    return Task(id=None, title="Pending", scheduled_date=day)


def test_completion_streak_accepts_yesterday_as_open_streak():
    today = date(2026, 7, 27)
    completed = [completed_on(today - timedelta(days=i)) for i in (1, 2, 3)]
    assert completion_streak(completed, today) == 3


def test_insight_snapshot_counts_week_and_upcoming():
    today = date(2026, 7, 27)
    completed = [completed_on(today), completed_on(today - timedelta(days=1))]
    pending = [pending_on(today), pending_on(today + timedelta(days=2))]
    snapshot = calculate_insights(pending, completed, today)
    assert snapshot.completed_total == 2
    assert snapshot.pending_total == 2
    assert snapshot.today_completed == 1
    assert snapshot.week_completed == 2
    assert snapshot.upcoming_counts[0] == 1
    assert snapshot.upcoming_counts[2] == 1
