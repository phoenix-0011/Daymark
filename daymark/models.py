from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Optional

from .formatting import format_date_short, format_time_12
from .i18n import t


@dataclass(slots=True)
class Category:
    id: int
    name: str
    color: str
    position: int = 0


@dataclass(slots=True)
class Subtask:
    id: int | None
    title: str
    completed: bool = False
    position: int = 0


@dataclass(slots=True)
class Task:
    id: int | None
    title: str
    notes: str = ""
    category_id: int | None = None
    category_name: str | None = None
    category_color: str | None = None
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    all_day: bool = True
    recurrence: str = "none"
    reminder_minutes: int | None = None
    reminder_sent: bool = False
    starred: bool = False
    generated_from_id: int | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    subtasks: list[Subtask] = field(default_factory=list)

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def is_overdue(self) -> bool:
        if self.is_completed or self.scheduled_date is None:
            return False
        now = datetime.now()
        if self.scheduled_time and not self.all_day:
            return datetime.combine(self.scheduled_date, self.scheduled_time) < now
        return self.scheduled_date < now.date()

    @property
    def schedule_label(self) -> str:
        if not self.scheduled_date:
            return t("anytime")
        today = date.today()
        if self.scheduled_date == today:
            day = t("today")
        elif self.scheduled_date == today.fromordinal(today.toordinal() + 1):
            day = t("tomorrow")
        else:
            day = format_date_short(self.scheduled_date)
        if self.scheduled_time and not self.all_day:
            return f"{day} · {format_time_12(self.scheduled_time)}"
        return day


def parse_date(value: Optional[str]) -> date | None:
    return date.fromisoformat(value) if value else None


def parse_time(value: Optional[str]) -> time | None:
    return time.fromisoformat(value) if value else None


def parse_datetime(value: Optional[str]) -> datetime | None:
    return datetime.fromisoformat(value) if value else None

