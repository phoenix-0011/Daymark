from __future__ import annotations

import tempfile
import unittest
from datetime import date, time
from pathlib import Path

from daymark.database import Database
from daymark.device import use_compact_layout
from daymark.models import Subtask, Task
from daymark.recurrence import next_date


class RecurrenceTests(unittest.TestCase):
    def test_weekday_skips_weekend(self):
        self.assertEqual(next_date(date(2026, 7, 24), "weekdays"), date(2026, 7, 27))

    def test_month_end_is_safe(self):
        self.assertEqual(next_date(date(2026, 1, 31), "monthly"), date(2026, 2, 28))


class ResponsiveLayoutTests(unittest.TestCase):
    def test_phone_width_uses_compact_layout(self):
        self.assertTrue(use_compact_layout(412, force_android=False))

    def test_android_forces_compact_layout(self):
        self.assertTrue(use_compact_layout(1400, force_android=True))

    def test_desktop_width_keeps_desktop_layout(self):
        self.assertFalse(use_compact_layout(1280, force_android=False))


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_save_complete_restore_and_search(self):
        category = self.db.categories()[0]
        task_id = self.db.save_task(
            Task(
                id=None,
                title="Prepare study notes",
                notes="Chapter five",
                category_id=category.id,
                scheduled_date=date(2026, 7, 22),
                scheduled_time=time(10, 30),
                all_day=False,
                reminder_minutes=10,
            )
        )
        self.assertEqual(len(self.db.tasks(search="study")), 1)
        task = self.db.task(task_id)
        task.title = "Prepare final study notes"
        self.db.save_task(task)
        self.assertEqual(self.db.task(task_id).title, "Prepare final study notes")
        self.db.complete_task(task_id)
        self.assertEqual(len(self.db.tasks()), 0)
        self.assertEqual(len(self.db.tasks(completed=True)), 1)
        self.db.restore_task(task_id)
        self.assertEqual(len(self.db.tasks()), 1)


    def test_edit_preserves_sent_reminder_until_schedule_changes(self):
        task_id = self.db.save_task(
            Task(
                id=None,
                title="Call Alex",
                scheduled_date=date(2026, 7, 24),
                scheduled_time=time(9, 0),
                all_day=False,
                reminder_minutes=10,
            )
        )
        self.db.mark_reminder_sent(task_id)
        task = self.db.task(task_id)
        task.notes = "Bring the report"
        self.db.save_task(task)
        self.assertTrue(self.db.task(task_id).reminder_sent)

        task = self.db.task(task_id)
        task.scheduled_time = time(10, 0)
        self.db.save_task(task)
        self.assertFalse(self.db.task(task_id).reminder_sent)

    def test_restoring_recurring_task_removes_generated_duplicate(self):
        task_id = self.db.save_task(
            Task(
                id=None,
                title="Daily planning",
                scheduled_date=date(2026, 7, 22),
                recurrence="daily",
            )
        )
        self.db.complete_task(task_id)
        self.assertEqual(len(self.db.tasks()), 1)
        self.db.restore_task(task_id)
        active = self.db.tasks()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].id, task_id)
        self.assertEqual(active[0].scheduled_date, date(2026, 7, 22))

    def test_subtasks_persist_search_and_copy_to_recurring_task(self):
        task_id = self.db.save_task(
            Task(
                id=None,
                title="Morning routine",
                scheduled_date=date(2026, 7, 22),
                recurrence="daily",
                subtasks=[
                    Subtask(None, "Drink water", False, 0),
                    Subtask(None, "Review priorities", True, 1),
                ],
            )
        )
        loaded = self.db.task(task_id)
        self.assertEqual([item.title for item in loaded.subtasks], ["Drink water", "Review priorities"])
        self.assertEqual(len(self.db.tasks(search="priorities")), 1)
        next_id = self.db.complete_task(task_id)
        generated = self.db.task(next_id)
        self.assertEqual([item.title for item in generated.subtasks], ["Drink water", "Review priorities"])
        self.assertEqual([item.completed for item in generated.subtasks], [False, False])
        self.assertEqual(generated.generated_from_id, task_id)


    def test_restore_recurring_task_does_not_delete_manual_duplicate(self):
        original_id = self.db.save_task(
            Task(
                id=None,
                title="Daily planning",
                notes="Same content",
                scheduled_date=date(2026, 7, 22),
                recurrence="daily",
            )
        )
        manual_id = self.db.save_task(
            Task(
                id=None,
                title="Daily planning",
                notes="Same content",
                scheduled_date=date(2026, 7, 23),
                recurrence="daily",
            )
        )
        generated_id = self.db.complete_task(original_id)
        self.assertIsNotNone(generated_id)

        self.db.restore_task(original_id)
        active_ids = {task.id for task in self.db.tasks()}
        self.assertIn(original_id, active_ids)
        self.assertIn(manual_id, active_ids)
        self.assertNotIn(generated_id, active_ids)

    def test_updating_missing_task_rolls_back_cleanly(self):
        ghost = Task(id=999_999, title="Ghost task", subtasks=[Subtask(None, "No orphan", False, 0)])
        with self.assertRaises(KeyError):
            self.db.save_task(ghost)
        count = self.db.connection.execute("SELECT COUNT(*) FROM subtasks").fetchone()[0]
        self.assertEqual(count, 0)

    def test_completing_task_twice_is_idempotent(self):
        task_id = self.db.save_task(
            Task(id=None, title="One completion", scheduled_date=date(2026, 7, 22), recurrence="daily")
        )
        first_generated = self.db.complete_task(task_id)
        second_generated = self.db.complete_task(task_id)
        self.assertIsNotNone(first_generated)
        self.assertIsNone(second_generated)
        self.assertEqual(len(self.db.tasks()), 1)

    def test_completion_creates_next_recurring_instance(self):
        task_id = self.db.save_task(
            Task(
                id=None,
                title="Weekly review",
                scheduled_date=date(2026, 7, 22),
                recurrence="weekly",
            )
        )
        next_id = self.db.complete_task(task_id)
        self.assertIsNotNone(next_id)
        active = self.db.tasks()
        self.assertEqual(active[0].scheduled_date, date(2026, 7, 29))
        self.assertEqual(len(self.db.tasks(completed=True)), 1)


if __name__ == "__main__":
    unittest.main()


def test_star_and_date_quick_actions(tmp_path):
    db = Database(tmp_path / "quick-actions.sqlite3")
    task_id = db.save_task(
        Task(
            id=None,
            title="Quick action",
            scheduled_date=date(2026, 7, 27),
            scheduled_time=time(8, 30),
            all_day=False,
            reminder_minutes=10,
        )
    )

    db.set_task_starred(task_id, True)
    starred = db.task(task_id)
    assert starred is not None and starred.starred is True

    db.set_task_date(task_id, date(2026, 8, 2))
    moved = db.task(task_id)
    assert moved is not None
    assert moved.scheduled_date == date(2026, 8, 2)
    assert moved.scheduled_time == time(8, 30)
    assert moved.reminder_minutes == 10

    db.set_task_date(task_id, None)
    cleared = db.task(task_id)
    assert cleared is not None
    assert cleared.scheduled_date is None
    assert cleared.scheduled_time is None
    assert cleared.reminder_minutes is None
    assert cleared.recurrence == "none"
    db.close()
