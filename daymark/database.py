from __future__ import annotations

import sqlite3
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path

from .models import Category, Subtask, Task, parse_date, parse_datetime, parse_time
from .recurrence import next_date


class Database:
    """Single-connection SQLite store used by the UI thread.

    All multi-step writes are wrapped in transactions. WAL plus a short busy
    timeout makes app restarts and Android lifecycle interruptions less likely
    to leave a half-written task or a transient "database is locked" error.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._closed = False
        self.connection = sqlite3.connect(str(path), timeout=4.0)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 4000")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")
        self.connection.execute("PRAGMA temp_store = MEMORY")
        self.connection.execute("PRAGMA cache_size = -4096")
        self.connection.execute("PRAGMA journal_size_limit = 4194304")
        self._migrate()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                color TEXT NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                scheduled_date TEXT,
                scheduled_time TEXT,
                all_day INTEGER NOT NULL DEFAULT 1,
                recurrence TEXT NOT NULL DEFAULT 'none',
                reminder_minutes INTEGER,
                reminder_sent INTEGER NOT NULL DEFAULT 0,
                starred INTEGER NOT NULL DEFAULT 0,
                generated_from_id INTEGER,
                completed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                position INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_subtasks_task_position
            ON subtasks(task_id, position, id);

            CREATE INDEX IF NOT EXISTS idx_tasks_status_date
            ON tasks(completed_at, scheduled_date);

            CREATE INDEX IF NOT EXISTS idx_tasks_category_status
            ON tasks(category_id, completed_at);
            """
        )
        task_columns = {row["name"] for row in self.connection.execute("PRAGMA table_info(tasks)")}
        if "starred" not in task_columns:
            self.connection.execute("ALTER TABLE tasks ADD COLUMN starred INTEGER NOT NULL DEFAULT 0")
        if "generated_from_id" not in task_columns:
            self.connection.execute("ALTER TABLE tasks ADD COLUMN generated_from_id INTEGER")
        self.connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_generated_from ON tasks(generated_from_id)"
        )

        count = self.connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if count == 0:
            defaults = [
                ("Personal", "#D88C6A", 0),
                ("Work", "#7B9E87", 1),
                ("Study", "#8C86B8", 2),
                ("Wellbeing", "#D0A75E", 3),
            ]
            self.connection.executemany(
                "INSERT INTO categories(name, color, position) VALUES (?, ?, ?)", defaults
            )
        self.connection.commit()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.connection.execute("PRAGMA optimize")
            self.connection.execute("PRAGMA wal_checkpoint(PASSIVE)")
        except sqlite3.Error:
            pass
        self.connection.close()

    def categories(self) -> list[Category]:
        rows = self.connection.execute(
            "SELECT id, name, color, position FROM categories ORDER BY position, name"
        ).fetchall()
        return [Category(**dict(row)) for row in rows]

    def add_category(self, name: str, color: str) -> int:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Category name cannot be empty")
        with self.connection:
            position = self.connection.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM categories"
            ).fetchone()[0]
            cursor = self.connection.execute(
                "INSERT INTO categories(name, color, position) VALUES (?, ?, ?)",
                (clean_name, color, position),
            )
            return int(cursor.lastrowid)

    def delete_category(self, category_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    def save_task(self, task: Task) -> int:
        with self.connection:
            return self._write_task(task)

    def _write_task(self, task: Task) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        reminder_sent = 0
        if task.id is not None:
            existing = self.task(task.id)
            if existing:
                reminder_changed = (
                    existing.scheduled_date != task.scheduled_date
                    or existing.scheduled_time != task.scheduled_time
                    or existing.all_day != task.all_day
                    or existing.reminder_minutes != task.reminder_minutes
                )
                reminder_sent = 0 if reminder_changed else int(existing.reminder_sent)

        title = task.title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")

        values = (
            title,
            task.notes.strip(),
            task.category_id,
            task.scheduled_date.isoformat() if task.scheduled_date else None,
            task.scheduled_time.isoformat(timespec="minutes") if task.scheduled_time else None,
            int(task.all_day),
            task.recurrence,
            task.reminder_minutes,
            reminder_sent,
            int(task.starred),
            task.generated_from_id,
        )
        if task.id is None:
            cursor = self.connection.execute(
                """
                INSERT INTO tasks(
                    title, notes, category_id, scheduled_date, scheduled_time,
                    all_day, recurrence, reminder_minutes, reminder_sent, starred,
                    generated_from_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (*values, now, now),
            )
            task_id = int(cursor.lastrowid)
            task.id = task_id
        else:
            cursor = self.connection.execute(
                """
                UPDATE tasks SET title=?, notes=?, category_id=?, scheduled_date=?,
                    scheduled_time=?, all_day=?, recurrence=?, reminder_minutes=?,
                    reminder_sent=?, starred=?, generated_from_id=?, updated_at=? WHERE id=?
                """,
                (*values, now, task.id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Task {task.id} does not exist")
            task_id = task.id

        self.connection.execute("DELETE FROM subtasks WHERE task_id = ?", (task_id,))
        subtask_rows = [
            (task_id, item.title.strip(), int(item.completed), position)
            for position, item in enumerate(task.subtasks)
            if item.title.strip()
        ]
        if subtask_rows:
            self.connection.executemany(
                "INSERT INTO subtasks(task_id, title, completed, position) VALUES (?, ?, ?, ?)",
                subtask_rows,
            )
        return task_id

    def task(self, task_id: int) -> Task | None:
        row = self.connection.execute(self._task_select() + " WHERE t.id = ?", (task_id,)).fetchone()
        if not row:
            return None
        task = self._row_to_task(row)
        task.subtasks = self._subtasks_for(task_id)
        return task

    def tasks(
        self,
        *,
        completed: bool = False,
        category_id: int | None = None,
        scheduled_date: date | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str = "",
    ) -> list[Task]:
        clauses = ["t.completed_at IS NOT NULL" if completed else "t.completed_at IS NULL"]
        params: list[object] = []
        if category_id is not None:
            clauses.append("t.category_id = ?")
            params.append(category_id)
        if scheduled_date is not None:
            clauses.append("t.scheduled_date = ?")
            params.append(scheduled_date.isoformat())
        if date_from is not None:
            clauses.append("t.scheduled_date >= ?")
            params.append(date_from.isoformat())
        if date_to is not None:
            clauses.append("t.scheduled_date <= ?")
            params.append(date_to.isoformat())
        if search.strip():
            clauses.append(
                "(t.title LIKE ? OR t.notes LIKE ? OR EXISTS ("
                "SELECT 1 FROM subtasks s WHERE s.task_id=t.id AND s.title LIKE ?))"
            )
            token = f"%{search.strip()}%"
            params.extend([token, token, token])
        order = (
            "t.completed_at DESC, t.id DESC"
            if completed
            else "t.starred DESC, CASE WHEN t.scheduled_date IS NULL THEN 1 ELSE 0 END, "
            "t.scheduled_date, CASE WHEN t.all_day = 1 THEN 0 ELSE 1 END, "
            "t.scheduled_time, t.created_at, t.id"
        )
        sql = self._task_select() + " WHERE " + " AND ".join(clauses) + " ORDER BY " + order
        tasks = [self._row_to_task(row) for row in self.connection.execute(sql, params)]
        self._attach_subtasks(tasks)
        return tasks

    def counts_by_category(self) -> dict[int, int]:
        rows = self.connection.execute(
            """
            SELECT category_id, COUNT(*) AS total FROM tasks
            WHERE completed_at IS NULL AND category_id IS NOT NULL GROUP BY category_id
            """
        ).fetchall()
        return {int(row["category_id"]): int(row["total"]) for row in rows}

    def complete_task(self, task_id: int) -> int | None:
        with self.connection:
            task = self.task(task_id)
            if not task or task.is_completed:
                return None
            now = datetime.now().isoformat(timespec="seconds")
            self.connection.execute(
                "UPDATE tasks SET completed_at=?, updated_at=? WHERE id=?", (now, now, task_id)
            )
            if not task.scheduled_date or task.recurrence == "none":
                return None

            following = next_date(task.scheduled_date, task.recurrence)
            if following is None:
                return None

            next_subtasks = [
                Subtask(None, item.title, False, position)
                for position, item in enumerate(task.subtasks)
            ]
            generated = replace(
                task,
                id=None,
                scheduled_date=following,
                completed_at=None,
                reminder_sent=False,
                generated_from_id=task_id,
                created_at=None,
                updated_at=None,
                subtasks=next_subtasks,
            )
            return self._write_task(generated)

    def restore_task(self, task_id: int) -> None:
        with self.connection:
            task = self.task(task_id)
            if not task or not task.is_completed:
                return

            # New builds mark the automatically generated next occurrence.
            deleted = self.connection.execute(
                "DELETE FROM tasks WHERE generated_from_id=? AND completed_at IS NULL",
                (task_id,),
            ).rowcount

            # Compatibility fallback for occurrences created before the marker
            # column existed. Keep the narrow timestamp/data match to avoid
            # deleting a separately-created duplicate task.
            if not deleted and task.scheduled_date and task.recurrence != "none" and task.completed_at:
                following = next_date(task.scheduled_date, task.recurrence)
                if following:
                    for candidate in self.tasks(scheduled_date=following):
                        generated_at_completion = (
                            candidate.created_at is not None
                            and abs((candidate.created_at - task.completed_at).total_seconds()) <= 5
                        )
                        same_occurrence = (
                            candidate.title == task.title
                            and candidate.notes == task.notes
                            and candidate.category_id == task.category_id
                            and candidate.scheduled_time == task.scheduled_time
                            and candidate.all_day == task.all_day
                            and candidate.recurrence == task.recurrence
                            and candidate.reminder_minutes == task.reminder_minutes
                        )
                        if generated_at_completion and same_occurrence:
                            self.connection.execute("DELETE FROM tasks WHERE id = ?", (candidate.id,))
                            break

            now = datetime.now().isoformat(timespec="seconds")
            self.connection.execute(
                "UPDATE tasks SET completed_at=NULL, reminder_sent=0, updated_at=? WHERE id=?",
                (now, task_id),
            )

    def set_task_starred(self, task_id: int, starred: bool) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connection:
            self.connection.execute(
                "UPDATE tasks SET starred=?, updated_at=? WHERE id=?",
                (int(starred), now, task_id),
            )

    def set_task_date(self, task_id: int, value: date | None) -> None:
        """Move a task without loading and rewriting all of its subtasks."""
        now = datetime.now().isoformat(timespec="seconds")
        with self.connection:
            if value is None:
                self.connection.execute(
                    """
                    UPDATE tasks SET scheduled_date=NULL, scheduled_time=NULL,
                        all_day=1, reminder_minutes=NULL, recurrence='none',
                        reminder_sent=0, updated_at=? WHERE id=?
                    """,
                    (now, task_id),
                )
            else:
                self.connection.execute(
                    "UPDATE tasks SET scheduled_date=?, reminder_sent=0, updated_at=? WHERE id=?",
                    (value.isoformat(), now, task_id),
                )

    def delete_task(self, task_id: int) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def pending_reminders(self, now: datetime) -> list[Task]:
        horizon = now + timedelta(minutes=1)
        rows = self.connection.execute(
            self._task_select()
            + """
            WHERE t.completed_at IS NULL
              AND t.reminder_sent = 0
              AND t.reminder_minutes IS NOT NULL
              AND t.scheduled_date IS NOT NULL
              AND t.scheduled_time IS NOT NULL
              AND t.all_day = 0
            """
        ).fetchall()
        due: list[Task] = []
        for row in rows:
            task = self._row_to_task(row)
            scheduled = datetime.combine(task.scheduled_date, task.scheduled_time)
            reminder_at = scheduled - timedelta(minutes=task.reminder_minutes or 0)
            if reminder_at <= horizon and scheduled >= now - timedelta(hours=12):
                due.append(task)
        return due

    def mark_reminder_sent(self, task_id: int) -> None:
        with self.connection:
            self.connection.execute("UPDATE tasks SET reminder_sent = 1 WHERE id = ?", (task_id,))

    def _subtasks_for(self, task_id: int) -> list[Subtask]:
        rows = self.connection.execute(
            "SELECT id, title, completed, position FROM subtasks "
            "WHERE task_id=? ORDER BY position, id",
            (task_id,),
        ).fetchall()
        return [
            Subtask(
                id=int(row["id"]),
                title=row["title"],
                completed=bool(row["completed"]),
                position=int(row["position"]),
            )
            for row in rows
        ]

    def _attach_subtasks(self, tasks: list[Task]) -> None:
        task_ids = [task.id for task in tasks if task.id is not None]
        if not task_ids:
            return
        placeholders = ",".join("?" for _ in task_ids)
        rows = self.connection.execute(
            f"SELECT id, task_id, title, completed, position FROM subtasks "
            f"WHERE task_id IN ({placeholders}) ORDER BY task_id, position, id",
            task_ids,
        ).fetchall()
        by_task: dict[int, list[Subtask]] = {}
        for row in rows:
            by_task.setdefault(int(row["task_id"]), []).append(
                Subtask(
                    id=int(row["id"]),
                    title=row["title"],
                    completed=bool(row["completed"]),
                    position=int(row["position"]),
                )
            )
        for task in tasks:
            if task.id is not None:
                task.subtasks = by_task.get(task.id, [])

    @staticmethod
    def _task_select() -> str:
        return """
            SELECT t.*, c.name AS category_name, c.color AS category_color
            FROM tasks t LEFT JOIN categories c ON c.id = t.category_id
        """

    @staticmethod
    def _row_to_task(row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            notes=row["notes"],
            category_id=row["category_id"],
            category_name=row["category_name"],
            category_color=row["category_color"],
            scheduled_date=parse_date(row["scheduled_date"]),
            scheduled_time=parse_time(row["scheduled_time"]),
            all_day=bool(row["all_day"]),
            recurrence=row["recurrence"],
            reminder_minutes=row["reminder_minutes"],
            reminder_sent=bool(row["reminder_sent"]),
            starred=bool(row["starred"]) if "starred" in row.keys() else False,
            generated_from_id=(
                row["generated_from_id"] if "generated_from_id" in row.keys() else None
            ),
            completed_at=parse_datetime(row["completed_at"]),
            created_at=parse_datetime(row["created_at"]),
            updated_at=parse_datetime(row["updated_at"]),
        )
