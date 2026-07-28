from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from .qt import (
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTimer,
    Qt,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

from .database import Database
from .device import running_on_android
from .formatting import (
    display_ymd,
    format_date_medium,
    format_month_year,
    format_week_header,
    format_week_range,
    weekday_name,
)
from .i18n import localize_digits, t, task_count
from .models import Task
from .widgets import (
    AnimatedStack,
    EmptyState,
    GlyphButton,
    Section,
    SegmentedControl,
    TaskCard,
    clear_layout,
    enable_kinetic_scroll,
)


class TaskView(QWidget):
    add_requested = pyqtSignal(object)
    edit_requested = pyqtSignal(int)
    details_requested = pyqtSignal(int)
    complete_requested = pyqtSignal(int, object)
    restore_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int, object)
    star_requested = pyqtSignal(int, bool)
    date_requested = pyqtSignal(int)

    def wire_card(self, card: TaskCard) -> TaskCard:
        card.edit_requested.connect(self.edit_requested)
        card.details_requested.connect(self.details_requested)
        card.completed.connect(lambda task_id, item=card: self.complete_requested.emit(task_id, item))
        card.restored.connect(self.restore_requested)
        card.delete_requested.connect(lambda task_id, item=card: self.delete_requested.emit(task_id, item))
        card.star_requested.connect(self.star_requested)
        card.date_requested.connect(self.date_requested)
        return card


class AllTasksView(TaskView):
    category_changed = pyqtSignal(object, object)
    add_category_requested = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.category_id: int | None = None
        self.compact = False
        self._category_buttons: dict[int | None, QPushButton] = {}
        self._category_signature: tuple = ()
        self._last_refresh_key: tuple[int | None, str] | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.category_scroll = QScrollArea()
        self.category_scroll.setObjectName("categoryChipScroll")
        self.category_scroll.setWidgetResizable(False)
        self.category_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.category_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.category_scroll.setFixedHeight(52)
        self.category_host = QWidget()
        self.category_host.setObjectName("categoryChipHost")
        self.category_layout = QHBoxLayout(self.category_host)
        self.category_layout.setContentsMargins(0, 2, 8, 6)
        self.category_layout.setSpacing(8)
        self.category_scroll.setWidget(self.category_host)
        enable_kinetic_scroll(self.category_scroll)
        root.addWidget(self.category_scroll)

        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText(t("search_tasks"))
        self.search.setClearButtonEnabled(True)
        self.search.setMaximumWidth(420)
        self.search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(170)
        self._search_timer.timeout.connect(self.refresh)
        self.search.textChanged.connect(lambda *_: self._search_timer.start())
        self.toolbar.addWidget(self.search, 1)
        root.addLayout(self.toolbar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(0, 2, 8, 20)
        self.list_layout.setSpacing(22)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)

    def retranslate(self) -> None:
        self.search.setPlaceholderText(t("search_tasks"))
        self.set_categories(self.db.categories())
        self.refresh()

    def set_compact(self, compact: bool) -> None:
        self.compact = compact
        self.search.setMaximumWidth(16_777_215 if compact else 420)
        self.search.setMinimumWidth(0)
        self.list_layout.setContentsMargins(0, 2, 0 if compact else 8, 20)
        self.category_scroll.setVisible(compact)

    def set_categories(self, categories) -> None:
        signature = (t("all"), tuple((item.id, item.name, item.color) for item in categories))
        if signature == self._category_signature and self._category_buttons:
            self._update_chip_selection()
            return
        self._category_signature = signature
        clear_layout(self.category_layout)
        self._category_buttons.clear()
        all_button = self._make_category_chip(t("all"), None)
        self.category_layout.addWidget(all_button)
        for category in categories:
            button = self._make_category_chip(category.name, category.id, category.color)
            self.category_layout.addWidget(button)
        self.category_host.adjustSize()
        self._update_chip_selection()

    def _make_category_chip(self, text: str, category_id: int | None, color: str | None = None) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("categoryChip")
        button.setProperty("active", category_id == self.category_id)
        if color:
            button.setProperty("categoryColor", color)
        button.setMinimumHeight(38)
        button.setMinimumWidth(max(62, button.sizeHint().width() + 12))
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
        button.clicked.connect(lambda checked=False, cid=category_id, label=text: self.category_changed.emit(cid, label))
        self._category_buttons[category_id] = button
        return button

    def _update_chip_selection(self) -> None:
        for category_id, button in self._category_buttons.items():
            button.setProperty("active", category_id == self.category_id)
            button.style().unpolish(button)
            button.style().polish(button)
        active = self._category_buttons.get(self.category_id)
        if active is not None and self.category_scroll.isVisible():
            QTimer.singleShot(0, lambda: self.category_scroll.ensureWidgetVisible(active, 18, 0))

    def set_category(self, category_id: int | None, refresh: bool = True) -> None:
        self.category_id = category_id
        self._update_chip_selection()
        if refresh:
            self.refresh()

    def refresh(self) -> None:
        self._search_timer.stop()
        TaskCard.close_open_card(immediate=True)
        key = (self.category_id, self.search.text().strip())
        preserve_scroll = key == self._last_refresh_key
        previous_scroll = self.scroll.verticalScrollBar().value()
        self._last_refresh_key = key
        clear_layout(self.list_layout)
        tasks = self.db.tasks(
            completed=False,
            category_id=self.category_id,
            search=self.search.text(),
        )
        self._last_rendered_count = len(tasks)
        if not tasks:
            self.list_layout.addWidget(
                EmptyState(
                    t("clear_horizon"),
                    t("no_tasks_match"),
                    "circle",
                ),
                1,
            )
            QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(0))
            return

        today = date.today()
        groups: dict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            if task.is_overdue:
                groups[t("overdue")].append(task)
            elif task.scheduled_date == today:
                groups[t("today")].append(task)
            elif task.scheduled_date and task.scheduled_date > today:
                groups[t("upcoming")].append(task)
            else:
                groups[t("anytime")].append(task)
        for name in (t("overdue"), t("today"), t("upcoming"), t("anytime")):
            items = groups.get(name, [])
            if not items:
                continue
            section = Section(name, len(items))
            for task in items:
                section.add_card(self.wire_card(TaskCard(task, mode="all")))
            self.list_layout.addWidget(section)
        self.list_layout.addStretch()
        target_scroll = previous_scroll if preserve_scroll else 0
        QTimer.singleShot(0, lambda value=target_scroll: self.scroll.verticalScrollBar().setValue(value))


class DayAgenda(TaskView):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.selected_date = date.today()
        self.compact = False
        self._rendered_date: date | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        self.summary_panel = QFrame()
        self.summary_panel.setObjectName("panel")
        self.summary_layout = QHBoxLayout(self.summary_panel)
        self.summary_layout.setContentsMargins(17, 13, 17, 13)
        self.date_title = QLabel()
        self.date_title.setObjectName("sectionTitle")
        self.date_title.setWordWrap(True)
        self.summary = QLabel()
        self.summary.setObjectName("muted")
        self.summary_layout.addWidget(self.date_title, 1)
        self.summary_layout.addWidget(self.summary, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        root.addWidget(self.summary_panel)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        self.container = QWidget()
        self.tasks_layout = QVBoxLayout(self.container)
        self.tasks_layout.setContentsMargins(0, 3, 8, 16)
        self.tasks_layout.setSpacing(9)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)

    def set_compact(self, compact: bool) -> None:
        self.compact = compact
        self.tasks_layout.setContentsMargins(0, 3, 0 if compact else 8, 16)
        self.summary_layout.setContentsMargins(*(13, 11, 13, 11) if compact else (17, 13, 17, 13))

    def set_date(self, value: date) -> None:
        self.selected_date = value
        self.refresh()

    def refresh(self) -> None:
        TaskCard.close_open_card(immediate=True)
        preserve_scroll = self._rendered_date == self.selected_date
        previous_scroll = self.scroll.verticalScrollBar().value()
        self._rendered_date = self.selected_date
        clear_layout(self.tasks_layout)
        tasks = self.db.tasks(scheduled_date=self.selected_date)
        self.date_title.setText(format_date_medium(self.selected_date))
        self.summary.setText(task_count(len(tasks)))
        if not tasks:
            self.tasks_layout.addWidget(
                EmptyState(
                    t("nothing_scheduled"),
                    t("enjoy_space"),
                    "planner",
                ),
                1,
            )
            QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(0))
            return
        all_day = [task for task in tasks if task.all_day]
        timed = [task for task in tasks if not task.all_day]
        if all_day:
            section = Section(t("all_day"), len(all_day))
            for task in all_day:
                section.add_card(self.wire_card(TaskCard(task, mode="day")))
            self.tasks_layout.addWidget(section)
        if timed:
            section = Section(t("timeline"), len(timed))
            for task in timed:
                section.add_card(self.wire_card(TaskCard(task, mode="day")))
            self.tasks_layout.addWidget(section)
        self.tasks_layout.addStretch()
        target_scroll = previous_scroll if preserve_scroll else 0
        QTimer.singleShot(0, lambda value=target_scroll: self.scroll.verticalScrollBar().setValue(value))


class WeekPlanner(TaskView):
    """A single-scroll week layout; avoids nested scrollers and crushed day columns."""

    day_selected = pyqtSignal(object)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.anchor = date.today()
        self.compact = False
        self.vertical_mode: bool | None = None
        self._rendered_week_start: date | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        enable_kinetic_scroll(self.scroll, vertical_only=True)

        self.host = QWidget()
        self.grid = QBoxLayout(QBoxLayout.Direction.LeftToRight, self.host)
        self.grid.setContentsMargins(0, 2, 2, 12)
        self.grid.setSpacing(9)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll)

    @property
    def week_start(self) -> date:
        return self.anchor - timedelta(days=self.anchor.weekday())

    def set_date(self, value: date) -> None:
        self.anchor = value
        self.refresh()

    def set_compact(self, compact: bool) -> None:
        self.compact = compact
        self._sync_direction(force=True)

    def _should_stack_days(self) -> bool:
        return self.compact or self.width() < 980

    def _sync_direction(self, force: bool = False) -> None:
        vertical = self._should_stack_days()
        if not force and vertical == self.vertical_mode:
            return
        self.vertical_mode = vertical
        self.grid.setDirection(
            QBoxLayout.Direction.TopToBottom if vertical else QBoxLayout.Direction.LeftToRight
        )
        self.grid.setSpacing(10 if vertical else 9)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop if vertical else Qt.AlignmentFlag.AlignVCenter)
        self.host.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum if vertical else QSizePolicy.Policy.Expanding,
        )
        self.refresh()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_direction()

    def refresh(self) -> None:
        TaskCard.close_open_card(immediate=True)
        start = self.week_start
        preserve_scroll = self._rendered_week_start == start
        previous_scroll = self.scroll.verticalScrollBar().value()

        if self.vertical_mode is None:
            self.vertical_mode = self._should_stack_days()
            self.grid.setDirection(
                QBoxLayout.Direction.TopToBottom
                if self.vertical_mode
                else QBoxLayout.Direction.LeftToRight
            )
        clear_layout(self.grid)
        tasks = self.db.tasks(date_from=start, date_to=start + timedelta(days=6))
        grouped: dict[date, list[Task]] = defaultdict(list)
        for task in tasks:
            if task.scheduled_date:
                grouped[task.scheduled_date].append(task)

        for offset in range(7):
            current = start + timedelta(days=offset)
            day_panel = QFrame()
            day_panel.setObjectName("weekPanel")
            today_match = current == date.today()
            day_panel.setProperty("today", today_match)
            day_panel.setMinimumWidth(0 if self.vertical_mode else 118)
            day_panel.setMinimumHeight(114 if self.vertical_mode else 0)
            day_panel.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed if self.vertical_mode else QSizePolicy.Policy.Expanding,
            )
            layout = QVBoxLayout(day_panel)
            layout.setContentsMargins(11 if self.vertical_mode else 8, 9, 11 if self.vertical_mode else 8, 10)
            layout.setSpacing(8)

            header_strip = QFrame()
            header_strip.setObjectName("weekHeaderStrip")
            if today_match:
                header_strip.setProperty("today", True)
            header_row = QHBoxLayout(header_strip)
            header_row.setContentsMargins(5, 4, 5, 4)
            header_row.setSpacing(6)
            header = QPushButton(format_week_header(current, self.vertical_mode))
            header.setObjectName("weekDayHeader")
            header.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            header.setStyleSheet("text-align: left;")
            header.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
            header.setCursor(Qt.CursorShape.PointingHandCursor)
            header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            header.clicked.connect(lambda checked=False, d=current: self.day_selected.emit(d))
            header_row.addWidget(header, 1)

            # Use the ASCII plus rather than the full-width symbol; the latter
            # is missing from several Android system fonts.
            add_text = "+  " + t("add")
            add = QPushButton(add_text)
            add.setObjectName("weekAdd")
            add.setProperty("rtl", False)
            add.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
            add.clicked.connect(lambda checked=False, d=current: self.add_requested.emit(d))
            if self.vertical_mode:
                header_row.addWidget(add)
            layout.addWidget(header_strip)

            items = grouped.get(current, [])
            if items:
                if self.vertical_mode:
                    day_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                    day_panel.setMinimumHeight(0)
                for task in items:
                    layout.addWidget(self.wire_card(TaskCard(task, mode="week")))
            else:
                if self.vertical_mode:
                    body = QWidget()
                    body_layout = QVBoxLayout(body)
                    body_layout.setContentsMargins(0, 0, 0, 0)
                    body_layout.setSpacing(0)
                    body_layout.addStretch(1)
                    empty = QLabel(t("no_tasks"))
                    empty.setObjectName("weekEmpty")
                    empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    empty.setMinimumHeight(28)
                    body_layout.addWidget(empty)
                    body_layout.addStretch(1)
                    body.setMinimumHeight(42)
                    layout.addWidget(body)
                else:
                    empty = QLabel(t("no_tasks"))
                    empty.setObjectName("weekEmpty")
                    empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    empty.setMinimumHeight(52)
                    layout.addWidget(empty)

            if not self.vertical_mode:
                layout.addStretch()
                layout.addWidget(add)
            else:
                day_panel.adjustSize()
            self.grid.addWidget(day_panel, 0 if self.vertical_mode else 1)

        if self.vertical_mode:
            self.grid.addStretch(1)
            self.grid.activate()
            self.host.adjustSize()
            self.host.setMinimumHeight(self.host.sizeHint().height())
        else:
            self.host.setMinimumHeight(0)

        self._rendered_week_start = start
        target_scroll = previous_scroll if preserve_scroll else 0
        QTimer.singleShot(0, lambda value=target_scroll: self.scroll.verticalScrollBar().setValue(value))


class CalendarCell(QFrame):
    selected = pyqtSignal(object)

    def __init__(
        self,
        day: date,
        in_month: bool,
        tasks: list[Task],
        compact: bool = False,
        display_day: int | None = None,
        selected: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.day = day
        self.compact = compact
        self.setObjectName("calendarCell")
        self.setProperty("compact", compact)
        self.setProperty("today", day == date.today())
        self.setProperty("muted", not in_month)
        self.setProperty("selected", selected)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.day_bubble: QLabel | None = None

        if compact:
            self.setMinimumSize(38, 44)
            self.setMaximumHeight(48)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(1, 1, 1, 1)
            layout.setSpacing(0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.day_bubble = QLabel(localize_digits(display_day if display_day is not None else day.day))
            self.day_bubble.setObjectName("calendarDayBubble")
            self.day_bubble.setProperty("selected", selected)
            self.day_bubble.setProperty("today", day == date.today())
            self.day_bubble.setProperty("muted", not in_month)
            self.day_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.day_bubble.setFixedSize(34, 34)
            self.day_bubble.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(self.day_bubble, 0, Qt.AlignmentFlag.AlignHCenter)

            dots = QLabel("•" * min(3, len(tasks)))
            dots.setObjectName("calendarTaskDots")
            dots.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dots.setFixedHeight(8)
            dots.setVisible(bool(tasks))
            dots.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(dots, 0, Qt.AlignmentFlag.AlignHCenter)
            return

        self.setMinimumSize(96, 78)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setSpacing(4)
        header = QHBoxLayout()
        day_label = QLabel(localize_digits(display_day if display_day is not None else day.day))
        day_label.setObjectName("calendarDayNumber" if in_month else "calendarDayMuted")
        day_label.setFixedHeight(18)
        day_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header.addWidget(day_label)
        header.addStretch()
        if tasks:
            count = QLabel(localize_digits(len(tasks)))
            count.setObjectName("countPill")
            count.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            header.addWidget(count)
        layout.addLayout(header)
        for task in tasks[:3]:
            line = QLabel(task.title)
            line.setObjectName("calendarTask")
            line.setFixedHeight(19)
            line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            if task.category_color:
                line.setStyleSheet(
                    f"border-left:3px solid {task.category_color}; padding-left:4px;"
                )
            layout.addWidget(line)
        if len(tasks) > 3:
            more = QLabel(t("more", count=localize_digits(len(tasks) - 3)))
            more.setObjectName("muted")
            more.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(more)
        layout.addStretch()

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        targets = [self]
        if self.day_bubble is not None:
            self.day_bubble.setProperty("selected", selected)
            targets.append(self.day_bubble)
        for target in targets:
            target.style().unpolish(target)
            target.style().polish(target)
            target.update()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.day)
        super().mouseReleaseEvent(event)


class MonthPlanner(TaskView):
    """Flat month calendar with an inline agenda for the selected date."""

    day_selected = pyqtSignal(object)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.anchor = date.today().replace(day=1)
        self.selected_date = date.today()
        self.compact = False
        self._cells: dict[date, CalendarCell] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        enable_kinetic_scroll(self.scroll, vertical_only=True)

        self.content = QWidget()
        self.content.setObjectName("monthContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 8, 18)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.calendar_widget = QWidget()
        self.calendar_widget.setObjectName("monthCalendar")
        self.grid = QGridLayout(self.calendar_widget)
        self.grid.setContentsMargins(0, 0, 0, 4)
        self.grid.setHorizontalSpacing(7)
        self.grid.setVerticalSpacing(7)
        self.content_layout.addWidget(self.calendar_widget)

        self.agenda_header = QFrame()
        self.agenda_header.setObjectName("monthAgendaHeader")
        agenda_header_layout = QHBoxLayout(self.agenda_header)
        agenda_header_layout.setContentsMargins(2, 10, 2, 2)
        agenda_header_layout.setSpacing(8)
        self.agenda_date = QLabel()
        self.agenda_date.setObjectName("sectionTitle")
        self.agenda_date.setWordWrap(True)
        self.agenda_count = QLabel()
        self.agenda_count.setObjectName("countPill")
        self.agenda_add = QPushButton("+ " + t("add"))
        self.agenda_add.setObjectName("monthAgendaAdd")
        self.agenda_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.agenda_add.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.agenda_add.clicked.connect(lambda: self.add_requested.emit(self.selected_date))
        agenda_header_layout.addWidget(self.agenda_date, 1)
        agenda_header_layout.addWidget(self.agenda_count)
        agenda_header_layout.addWidget(self.agenda_add)
        self.content_layout.addWidget(self.agenda_header)

        self.agenda_widget = QWidget()
        self.agenda_widget.setObjectName("monthAgenda")
        self.agenda_layout = QVBoxLayout(self.agenda_widget)
        self.agenda_layout.setContentsMargins(0, 0, 0, 0)
        self.agenda_layout.setSpacing(9)
        self.agenda_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(self.agenda_widget)
        self.content_layout.addStretch(1)

        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll)

    def set_date(self, value: date) -> None:
        self.selected_date = value
        self.anchor = value.replace(day=1)
        self.refresh()

    def set_compact(self, compact: bool) -> None:
        if self.compact == compact:
            return
        self.compact = compact
        self.grid.setHorizontalSpacing(1 if compact else 7)
        self.grid.setVerticalSpacing(0 if compact else 7)
        self.grid.setContentsMargins(0, 0, 0, 2 if compact else 4)
        self.content_layout.setContentsMargins(0, 0, 0 if compact else 8, 18)
        self.content_layout.setSpacing(8 if compact else 12)
        self.refresh()

    def _display_month(self) -> tuple[int, int, date]:
        return self.anchor.year, self.anchor.month, self.anchor.replace(day=1)

    def _select_day(self, selected: date) -> None:
        previous = self.selected_date
        display_year, display_month, _ = self._display_month()
        selected_year, selected_month, _ = display_ymd(selected)
        self.selected_date = selected

        if (selected_year, selected_month) != (display_year, display_month):
            self.anchor = selected.replace(day=1)
            self.refresh()
        else:
            old_cell = self._cells.get(previous)
            new_cell = self._cells.get(selected)
            if old_cell is not None and old_cell is not new_cell:
                old_cell.set_selected(False)
            if new_cell is not None:
                new_cell.set_selected(True)
            self._refresh_agenda()

        self.day_selected.emit(selected)
        if self.compact:
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(self.agenda_header, 0, 10))

    def _refresh_agenda(self) -> None:
        TaskCard.close_open_card(immediate=True)
        clear_layout(self.agenda_layout)
        tasks = self.db.tasks(scheduled_date=self.selected_date)
        self.agenda_date.setText(format_date_medium(self.selected_date))
        self.agenda_count.setText(localize_digits(len(tasks)))
        self.agenda_add.setText("+ " + t("add"))

        if not tasks:
            empty = QFrame()
            empty.setObjectName("monthAgendaEmpty")
            empty_layout = QHBoxLayout(empty)
            empty_layout.setContentsMargins(14, 13, 10, 13)
            empty_layout.setSpacing(8)
            message = QLabel(t("nothing_scheduled"))
            message.setObjectName("muted")
            message.setWordWrap(True)
            add = QPushButton("+ " + t("add"))
            add.setObjectName("monthAgendaEmptyAdd")
            add.setCursor(Qt.CursorShape.PointingHandCursor)
            add.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            add.clicked.connect(lambda: self.add_requested.emit(self.selected_date))
            empty_layout.addWidget(message, 1)
            empty_layout.addWidget(add)
            self.agenda_layout.addWidget(empty)
            return

        for task in tasks:
            self.agenda_layout.addWidget(self.wire_card(TaskCard(task, mode="day")))

    def refresh(self) -> None:
        clear_layout(self.grid)
        self._cells.clear()
        for column in range(7):
            probe = date(2026, 7, 19) + timedelta(days=column)
            name = weekday_name(probe, short=True)
            label = QLabel(name if self.compact else name.upper())
            label.setObjectName("monthWeekday" if self.compact else "eyebrow")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedHeight(26 if self.compact else 20)
            self.grid.addWidget(label, 0, column)

        display_year, display_month, month_start = self._display_month()
        first = month_start - timedelta(days=(month_start.weekday() + 1) % 7)
        last = first + timedelta(days=41)
        tasks = self.db.tasks(date_from=first, date_to=last)
        grouped: dict[date, list[Task]] = defaultdict(list)
        for task in tasks:
            if task.scheduled_date:
                grouped[task.scheduled_date].append(task)

        for index in range(42):
            current = first + timedelta(days=index)
            cy, cm, cd = display_ymd(current)
            cell = CalendarCell(
                current,
                cy == display_year and cm == display_month,
                grouped[current],
                compact=self.compact,
                display_day=cd,
                selected=current == self.selected_date,
            )
            cell.selected.connect(self._select_day)
            self._cells[current] = cell
            self.grid.addWidget(cell, index // 7 + 1, index % 7)

        self.calendar_widget.setMinimumHeight(self.grid.sizeHint().height())
        self._refresh_agenda()
        self.content.adjustSize()


class PlannerView(TaskView):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.mode = "day"
        self.selected_date = date.today()
        self.compact = False
        self._pending_mode: str | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        self.toolbar_widget = QWidget()
        self.toolbar_widget.setObjectName("plannerToolbar")
        self.toolbar = QGridLayout(self.toolbar_widget)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.toolbar.setHorizontalSpacing(10)
        self.toolbar.setVerticalSpacing(9)

        self.segments = SegmentedControl([("day", t("day")), ("week", t("week")), ("month", t("month"))])
        self.segments.changed.connect(self._change_mode)

        self.nav_controls = QFrame()
        self.nav_controls.setObjectName("plannerNavBar")
        nav_layout = QHBoxLayout(self.nav_controls)
        nav_layout.setContentsMargins(4, 4, 4, 4)
        nav_layout.setSpacing(4)
        self.previous_button = GlyphButton("left", t("previous"), size=40)
        self.previous_button.clicked.connect(lambda: self._navigate(-1))
        self.today_button = QPushButton(t("today"))
        self.today_button.setObjectName("plannerToday")
        self.today_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.today_button.setMinimumHeight(40)
        self.today_button.setMinimumWidth(72)
        self.today_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.today_button.clicked.connect(self._today_and_release)
        self.following_button = GlyphButton("right", t("next"), size=40)
        self.following_button.clicked.connect(lambda: self._navigate(1))
        for button in (self.previous_button, self.following_button):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nav_layout.addWidget(self.previous_button)
        nav_layout.addWidget(self.today_button, 1)
        nav_layout.addWidget(self.following_button)

        self.toolbar.addWidget(self.segments, 0, 0)
        self.toolbar.addWidget(self.nav_controls, 0, 1, Qt.AlignmentFlag.AlignRight)
        self.toolbar.setColumnStretch(0, 1)
        root.addWidget(self.toolbar_widget)

        self.period_label = QLabel()
        self.period_label.setObjectName("sectionTitle")
        self.period_label.setWordWrap(True)
        root.addWidget(self.period_label)

        self.stack = AnimatedStack(style="slide")
        self.day = DayAgenda(db)
        self.week = WeekPlanner(db)
        self.month = MonthPlanner(db)
        self.stack.addWidget(self.day)
        self.stack.addWidget(self.week)
        self.stack.addWidget(self.month)
        # Keep the segmented control responsive while a short transition is
        # running. Rapid taps are coalesced to the latest requested destination
        # instead of being silently ignored.
        self.stack.transition_finished.connect(self._planner_transition_finished)
        root.addWidget(self.stack, 1)

        for view in (self.day, self.week, self.month):
            view.add_requested.connect(self.add_requested)
            view.edit_requested.connect(self.edit_requested)
            view.details_requested.connect(self.details_requested)
            view.complete_requested.connect(self.complete_requested)
            view.restore_requested.connect(self.restore_requested)
            view.delete_requested.connect(self.delete_requested)
        self.week.day_selected.connect(self._open_day)
        self.month.day_selected.connect(self._select_month_day)
        self.refresh()

    def retranslate(self) -> None:
        self.cancel_animations()
        self.segments.set_labels({"day": t("day"), "week": t("week"), "month": t("month")})
        self.previous_button.glyph = "left"
        self.following_button.glyph = "right"
        self.previous_button.setToolTip(t("previous"))
        self.following_button.setToolTip(t("next"))
        self.previous_button.update()
        self.following_button.update()
        self.today_button.setText(t("today"))
        # Only the visible planner mode is rebuilt now. Hidden modes refresh
        # when selected, avoiding three expensive off-screen widget trees.
        self.refresh()

    def set_compact(self, compact: bool) -> None:
        if self.compact != compact:
            self.compact = compact
            self.toolbar.removeWidget(self.segments)
            self.toolbar.removeWidget(self.nav_controls)
            if compact:
                self.toolbar.addWidget(self.segments, 0, 0, 1, 2)
                self.toolbar.addWidget(self.nav_controls, 1, 0, 1, 2)
                self.toolbar.setColumnStretch(0, 1)
                self.toolbar.setColumnStretch(1, 0)
                self.nav_controls.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                self.today_button.setMinimumWidth(0)
                self.today_button.setMaximumWidth(16_777_215)
                self.today_button.setProperty("touch", True)
            else:
                self.toolbar.addWidget(self.segments, 0, 0)
                self.toolbar.addWidget(self.nav_controls, 0, 1, Qt.AlignmentFlag.AlignRight)
                self.toolbar.setColumnStretch(0, 1)
                self.toolbar.setColumnStretch(1, 0)
                self.nav_controls.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                self.today_button.setMinimumWidth(72)
                self.today_button.setMaximumWidth(96)
                self.today_button.setProperty("touch", False)
            self.today_button.style().unpolish(self.today_button)
            self.today_button.style().polish(self.today_button)
        self.segments.set_compact(compact)
        self.day.set_compact(compact)
        self.week.set_compact(compact)
        self.month.set_compact(compact)

    def _change_mode(self, mode: str) -> None:
        if mode not in {"day", "week", "month"}:
            return
        if self.stack.is_animating:
            # Standard mobile segmented controls accept the tap immediately.
            # The content transition serializes it and keeps only the newest
            # destination, preventing both lost taps and colliding animations.
            self._pending_mode = mode
            return
        self._perform_mode_change(mode)

    def _perform_mode_change(self, mode: str) -> None:
        if mode == self.mode:
            self.segments.select(mode, emit=False, animate=True)
            self.refresh()
            return
        old_index = {"day": 0, "week": 1, "month": 2}[self.mode]
        new_index = {"day": 0, "week": 1, "month": 2}[mode]
        self.mode = mode
        self.refresh()
        if not self.stack.animate_to(new_index, 1 if new_index > old_index else -1):
            self.stack.setCurrentIndex(new_index)

    def _planner_transition_finished(self, _index: int) -> None:
        pending = self._pending_mode
        self._pending_mode = None
        if pending is None:
            self.segments.select(self.mode, emit=False, animate=False)
            return
        # Defer one event-loop turn so the outgoing overlay is fully removed
        # before the next serialized transition begins.
        QTimer.singleShot(0, lambda mode=pending: self._perform_mode_change(mode))

    def _navigate(self, direction: int) -> None:
        self._move(direction)
        self._release_navigation_buttons()

    def _move(self, direction: int) -> None:
        if self.mode == "day":
            self.selected_date += timedelta(days=direction)
        elif self.mode == "week":
            self.selected_date += timedelta(days=7 * direction)
        else:
            month = self.selected_date.month - 1 + direction
            year = self.selected_date.year + month // 12
            month = month % 12 + 1
            self.selected_date = date(year, month, 1)
        self.refresh()

    def _today_and_release(self) -> None:
        self._today()
        self._release_navigation_buttons()

    def _today(self) -> None:
        self.selected_date = date.today()
        self.refresh()

    def _release_navigation_buttons(self) -> None:
        for button in (self.previous_button, self.today_button, self.following_button):
            button.setDown(False)
            button.clearFocus()
            button.update()

    def _open_day(self, selected: date) -> None:
        self.selected_date = selected
        if self.mode == "day" and not self.stack.is_animating:
            self.refresh()
            return
        self.segments.select("day", emit=True, animate=True)

    def _select_month_day(self, selected: date) -> None:
        """Keep Month view open and synchronize the global planner selection."""
        self.selected_date = selected
        self.period_label.setText(format_month_year(selected))

    def cancel_animations(self) -> None:
        self._pending_mode = None
        self.stack.cancel_transition()
        self.segments.set_locked(False)
        self.segments.snap_indicator()

    def refresh(self) -> None:
        if self.mode == "day":
            self.period_label.setVisible(False)
            self.day.set_date(self.selected_date)
        elif self.mode == "week":
            self.period_label.setVisible(True)
            self.week.set_date(self.selected_date)
            start = self.week.week_start
            end = start + timedelta(days=6)
            self.period_label.setText(format_week_range(start, end))
        else:
            self.period_label.setVisible(True)
            self.month.set_date(self.selected_date)
            self.period_label.setText(format_month_year(self.selected_date))


class HistoryView(TaskView):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._last_search = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)
        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText(t("search_completed"))
        self.search.setMaximumWidth(470)
        self.search.setMinimumWidth(0)
        self.search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search.setClearButtonEnabled(True)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(170)
        self._search_timer.timeout.connect(self.refresh)
        self.search.textChanged.connect(lambda *_: self._search_timer.start())
        root.addWidget(self.search)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setContentsMargins(0, 2, 8, 18)
        self.list_layout.setSpacing(9)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(container)
        root.addWidget(self.scroll)

    def retranslate(self) -> None:
        self.search.setPlaceholderText(t("search_completed"))
        self.refresh()

    def set_compact(self, compact: bool) -> None:
        self.search.setMinimumWidth(0)
        self.search.setMaximumWidth(16_777_215 if compact else 470)
        self.list_layout.setContentsMargins(0, 2, 0 if compact else 8, 18)

    def refresh(self) -> None:
        self._search_timer.stop()
        TaskCard.close_open_card(immediate=True)
        search = self.search.text().strip()
        preserve_scroll = search == getattr(self, "_last_search", "")
        previous_scroll = self.scroll.verticalScrollBar().value()
        self._last_search = search
        clear_layout(self.list_layout)
        tasks = self.db.tasks(completed=True, search=self.search.text())
        if not tasks:
            self.list_layout.addWidget(
                EmptyState(
                    t("no_completed"),
                    t("completed_collect"),
                    "return",
                ),
                1,
            )
            QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(0))
            return
        for task in tasks:
            self.list_layout.addWidget(self.wire_card(TaskCard(task, mode="history")))
        self.list_layout.addStretch()
        target_scroll = previous_scroll if preserve_scroll else 0
        QTimer.singleShot(0, lambda value=target_scroll: self.scroll.verticalScrollBar().setValue(value))
