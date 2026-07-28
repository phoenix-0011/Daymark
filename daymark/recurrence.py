from __future__ import annotations

import calendar
from datetime import date, timedelta

from .i18n import t

RECURRENCE_LABELS = {
    "none": "Does not repeat",
    "daily": "Every day",
    "weekdays": "Every weekday",
    "weekly": "Every week",
    "monthly": "Every month",
}
RECURRENCE_KEYS = {
    "none": "does_not_repeat",
    "daily": "every_day",
    "weekdays": "every_weekday",
    "weekly": "every_week",
    "monthly": "every_month",
}


def recurrence_label(value: str) -> str:
    return t(RECURRENCE_KEYS.get(value, value))


def next_date(current: date, recurrence: str) -> date | None:
    if recurrence == "daily":
        return current + timedelta(days=1)
    if recurrence == "weekdays":
        candidate = current + timedelta(days=1)
        while candidate.weekday() >= 5:
            candidate += timedelta(days=1)
        return candidate
    if recurrence == "weekly":
        return current + timedelta(days=7)
    if recurrence == "monthly":
        year = current.year + (1 if current.month == 12 else 0)
        month = 1 if current.month == 12 else current.month + 1
        day = min(current.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)
    return None
