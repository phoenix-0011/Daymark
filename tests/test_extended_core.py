from __future__ import annotations

import sqlite3
from datetime import date, datetime, time, timedelta

import pytest

from daymark.calendar_utils import add_jalali_month, jalali_month_length
from daymark.database import Database
from daymark.formatting import (
    display_ymd,
    format_date_full,
    format_date_medium,
    format_date_short,
    format_datetime_brief,
    format_month_day,
    format_month_year,
    format_time_12,
    format_week_header,
    format_week_range,
    month_name,
    weekday_name,
)
from daymark.i18n import (
    apply_text_input_direction,
    install_text_input_direction_support,
    normalize_digits,
    set_language,
    t,
    task_count,
)
from daymark.models import Subtask, Task, parse_date, parse_datetime, parse_time
from daymark.recurrence import next_date, recurrence_label


def test_task_validation_and_category_lifecycle(tmp_path):
    db = Database(tmp_path / "validation.sqlite3")
    with pytest.raises(ValueError):
        db.save_task(Task(id=None, title="   "))
    with pytest.raises(ValueError):
        db.add_category("   ", "#FFFFFF")

    category_id = db.add_category("  Research  ", "#123456")
    category = next(item for item in db.categories() if item.id == category_id)
    assert category.name == "Research"
    with pytest.raises(sqlite3.IntegrityError):
        db.add_category("research", "#654321")

    task_id = db.save_task(
        Task(id=None, title="Paper", category_id=category_id,
             subtasks=[Subtask(None, "Read abstract")])
    )
    assert db.counts_by_category()[category_id] == 1
    db.delete_category(category_id)
    assert db.task(task_id).category_id is None

    db.delete_task(task_id)
    assert db.task(task_id) is None
    assert db.connection.execute("SELECT COUNT(*) FROM subtasks").fetchone()[0] == 0
    db.close()
    db.close()  # Closing twice must be safe.


def test_task_filters_ordering_and_completed_results(tmp_path):
    db = Database(tmp_path / "filters.sqlite3")
    work = db.categories()[1]
    today = date(2026, 7, 30)

    first = db.save_task(Task(id=None, title="Undated", category_id=work.id))
    second = db.save_task(
        Task(id=None, title="Today timed", category_id=work.id, scheduled_date=today,
             scheduled_time=time(9, 30), all_day=False, starred=True)
    )
    third = db.save_task(
        Task(id=None, title="Tomorrow", notes="special-token", scheduled_date=today + timedelta(days=1))
    )

    assert [task.id for task in db.tasks(category_id=work.id)] == [second, first]
    assert [task.id for task in db.tasks(scheduled_date=today)] == [second]
    assert {task.id for task in db.tasks(date_from=today, date_to=today + timedelta(days=1))} == {second, third}
    assert [task.id for task in db.tasks(search="special-token")] == [third]

    db.complete_task(second)
    completed = db.tasks(completed=True)
    assert [task.id for task in completed] == [second]
    db.close()


def test_pending_reminders_only_returns_due_tasks(tmp_path):
    db = Database(tmp_path / "reminders.sqlite3")
    now = datetime(2026, 7, 30, 10, 0)

    due_id = db.save_task(
        Task(id=None, title="Due", scheduled_date=now.date(), scheduled_time=time(10, 10),
             all_day=False, reminder_minutes=10)
    )
    db.save_task(
        Task(id=None, title="Later", scheduled_date=now.date(), scheduled_time=time(12, 0),
             all_day=False, reminder_minutes=10)
    )
    db.save_task(
        Task(id=None, title="All day", scheduled_date=now.date(), all_day=True, reminder_minutes=10)
    )

    assert [task.id for task in db.pending_reminders(now)] == [due_id]
    db.mark_reminder_sent(due_id)
    assert db.pending_reminders(now) == []
    db.close()


def test_migration_adds_missing_columns_and_preserves_legacy_data(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            color TEXT NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            category_id INTEGER,
            scheduled_date TEXT,
            scheduled_time TEXT,
            all_day INTEGER NOT NULL DEFAULT 1,
            recurrence TEXT NOT NULL DEFAULT 'none',
            reminder_minutes INTEGER,
            reminder_sent INTEGER NOT NULL DEFAULT 0,
            completed_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            position INTEGER NOT NULL DEFAULT 0
        );
        INSERT INTO categories(name, color, position) VALUES ('Legacy', '#123456', 0);
        INSERT INTO tasks(title, created_at, updated_at) VALUES ('Legacy task', '2026-01-01', '2026-01-01');
        """
    )
    connection.commit()
    connection.close()

    db = Database(path)
    columns = {row["name"] for row in db.connection.execute("PRAGMA table_info(tasks)")}
    assert {"starred", "generated_from_id"}.issubset(columns)
    assert db.tasks()[0].title == "Legacy task"
    db.close()


def test_model_helpers_and_schedule_labels():
    assert parse_date(None) is None
    assert parse_date("2026-07-30") == date(2026, 7, 30)
    assert parse_time(None) is None
    assert parse_time("09:15") == time(9, 15)
    assert parse_datetime(None) is None
    assert parse_datetime("2026-07-30T09:15:00") == datetime(2026, 7, 30, 9, 15)

    assert not Task(id=None, title="Anytime").is_overdue
    assert Task(id=None, title="Past", scheduled_date=date(2000, 1, 1)).is_overdue
    assert not Task(id=None, title="Done", scheduled_date=date(2000, 1, 1), completed_at=datetime.now()).is_overdue
    assert Task(id=None, title="Timed past", scheduled_date=date.today(), scheduled_time=time(0, 0), all_day=False).is_overdue

    set_language("en")
    assert Task(id=None, title="Anytime").schedule_label == "Anytime"
    assert Task(id=None, title="Today", scheduled_date=date.today()).schedule_label == "Today"
    tomorrow = date.today() + timedelta(days=1)
    assert Task(id=None, title="Tomorrow", scheduled_date=tomorrow).schedule_label == "Tomorrow"
    assert "9:15 AM" in Task(id=None, title="Timed", scheduled_date=tomorrow,
                              scheduled_time=time(9, 15), all_day=False).schedule_label


def test_recurrence_labels_and_all_branches():
    current = date(2026, 12, 31)
    assert next_date(current, "daily") == date(2027, 1, 1)
    assert next_date(current, "weekly") == date(2027, 1, 7)
    assert next_date(current, "monthly") == date(2027, 1, 31)
    assert next_date(current, "none") is None
    set_language("en")
    assert recurrence_label("daily") == "Every day"
    assert recurrence_label("unknown") == "unknown"


def test_calendar_month_arithmetic_and_invalid_month():
    assert add_jalali_month(date(2024, 3, 20), 1) == date(2024, 4, 20)
    assert add_jalali_month(date(2024, 3, 20), -1) == date(2024, 2, 20)
    with pytest.raises(ValueError):
        jalali_month_length(1403, 0)
    with pytest.raises(ValueError):
        jalali_month_length(1403, 13)


def test_formatting_for_english_and_turkish():
    value = date(2026, 7, 30)
    timestamp = datetime(2026, 7, 30, 9, 5)

    set_language("en")
    assert weekday_name(value) == "Thursday"
    assert weekday_name(value, short=True) == "Thu"
    assert month_name(value) == "July"
    assert month_name(value, short=True) == "Jul"
    assert display_ymd(value) == (2026, 7, 30)
    assert format_time_12(None) == "—"
    assert format_time_12(time(9, 5)) == "9:05 AM"
    assert format_date_short(value) == "Thu, Jul 30"
    assert format_date_medium(value) == "Thursday, July 30"
    assert format_date_full(value) == "Thursday, July 30, 2026"
    assert format_month_day(value) == "July 30"
    assert format_month_day(value, short_month=True) == "Jul 30"
    assert format_month_year(value) == "July 2026"
    assert format_week_header(value, vertical=True) == "Thursday  ·  Jul 30"
    assert format_week_header(value, vertical=False) == "Thu\n30"
    assert format_week_range(value, date(2026, 8, 2)) == "Jul 30 – Aug 2, 2026"
    assert format_datetime_brief(None) == "—"
    assert format_datetime_brief(timestamp) == "Jul 30, 2026 · 9:05 AM"

    set_language("tr")
    assert format_date_short(value) == "Per, 30 Tem"
    assert format_date_medium(value) == "Perşembe, 30 Temmuz"
    assert format_date_full(value) == "Perşembe, 30 Temmuz 2026"
    assert format_month_day(value) == "30 Temmuz"
    assert format_week_range(value, date(2026, 8, 2)) == "30 Tem – 2 Ağu, 2026"
    set_language("en")


def test_i18n_helpers_are_safe_and_predictable():
    set_language("en")
    assert normalize_digits("۱۲٣") == "123"
    assert t("missing_translation_key") == "missing_translation_key"
    assert t("task_count_many", missing="ignored")
    assert task_count(1) == "1 task"
    assert task_count(2, active=True) == "2 active tasks"
    assert apply_text_input_direction() is None
    assert install_text_input_direction_support() is None
