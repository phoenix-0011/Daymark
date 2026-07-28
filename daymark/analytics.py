from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta

from .models import Task


@dataclass(frozen=True, slots=True)
class InsightSnapshot:
    completed_total: int
    pending_total: int
    overdue_total: int
    completion_rate: int
    streak_days: int
    today_completed: int
    week_completed: int
    daily_completed: tuple[int, ...]
    daily_labels: tuple[date, ...]
    heatmap_counts: dict[date, int]
    category_counts: tuple[tuple[str, int], ...]
    upcoming_counts: tuple[int, ...]
    upcoming_labels: tuple[date, ...]


def _completed_dates(tasks: list[Task]) -> list[date]:
    return [task.completed_at.date() for task in tasks if task.completed_at is not None]


def completion_streak(tasks: list[Task], today: date | None = None) -> int:
    """Return the current completion streak.

    A streak can end today or yesterday, matching the convention used by habit
    and productivity apps: users do not lose yesterday's streak at midnight
    before they have had a chance to complete today's work.
    """
    today = today or date.today()
    completed_days = set(_completed_dates(tasks))
    if not completed_days:
        return 0
    cursor = today if today in completed_days else today - timedelta(days=1)
    if cursor not in completed_days:
        return 0
    streak = 0
    while cursor in completed_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def calculate_insights(
    pending: list[Task],
    completed: list[Task],
    today: date | None = None,
) -> InsightSnapshot:
    today = today or date.today()
    completed_dates = _completed_dates(completed)
    heatmap = Counter(completed_dates)

    completed_total = len(completed)
    pending_total = len(pending)
    overdue_total = sum(1 for task in pending if task.is_overdue)
    denominator = completed_total + pending_total
    completion_rate = round(completed_total * 100 / denominator) if denominator else 0

    last_seven = tuple(today - timedelta(days=offset) for offset in range(6, -1, -1))
    daily_completed = tuple(heatmap.get(day, 0) for day in last_seven)

    upcoming_days = tuple(today + timedelta(days=offset) for offset in range(7))
    upcoming_counts = tuple(
        sum(1 for task in pending if task.scheduled_date == day)
        for day in upcoming_days
    )

    categories = Counter(
        task.category_name or ""
        for task in completed
    )
    category_counts = tuple(categories.most_common(5))

    return InsightSnapshot(
        completed_total=completed_total,
        pending_total=pending_total,
        overdue_total=overdue_total,
        completion_rate=completion_rate,
        streak_days=completion_streak(completed, today),
        today_completed=heatmap.get(today, 0),
        week_completed=sum(daily_completed),
        daily_completed=daily_completed,
        daily_labels=last_seven,
        heatmap_counts=dict(heatmap),
        category_counts=category_counts,
        upcoming_counts=upcoming_counts,
        upcoming_labels=upcoming_days,
    )
