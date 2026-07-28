from __future__ import annotations

import calendar
from collections.abc import Callable

from datetime import date, time, timedelta

from .qt import (
    QAbstractScrollArea,
    QAbstractSpinBox,
    QApplication,
    QColorDialog,
    QColor,
    QDate,
    QDialog,
    QEasingCurve,
    QEvent,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QIntValidator,
    QTimer,
    QLabel,
    QLineEdit,
    QMainWindow,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QPushButton,
    QRect,
    QScrollArea,
    QSizePolicy,
    QPoint,
    QTextEdit,
    QTime,
    QTimeEdit,
    Qt,
    QVBoxLayout,
    QWidget,
)

from .device import running_on_android, use_compact_layout
from .formatting import format_date_full, format_date_medium, format_datetime_brief, format_month_year, format_time_12, month_names, weekday_name
from .i18n import apply_text_input_direction, language, language_items, localize_digits, normalize_digits, t
from .models import Category, Subtask, Task
from .recurrence import RECURRENCE_KEYS, recurrence_label
from .templates import TaskTemplate, grouped_templates
from .theme import PALETTE_KEYS, category_swatches, normalize_palette_name
from .widgets import CheckOption, GlyphButton, GlyphIcon, HoverCheck, SoftSelect, clear_layout, enable_kinetic_scroll, theme_colors


REMINDERS = [
    ("no_reminder", None),
    ("at_scheduled_time", 0),
    ("minutes_before_10", 10),
    ("minutes_before_30", 30),
    ("hour_before", 60),
    ("day_before", 1440),
]


def reminder_label(minutes: int | None) -> str:
    key = next((key for key, value in REMINDERS if value == minutes), "no_reminder")
    return t(key)


def compact_dialog(parent=None) -> bool:
    width = parent.width() if parent and parent.width() > 0 else 1_000
    return running_on_android() or use_compact_layout(width)


def _main_window(parent=None) -> QMainWindow | None:
    widget = parent
    while widget is not None:
        if isinstance(widget, QMainWindow):
            return widget
        widget = widget.parentWidget() if hasattr(widget, "parentWidget") else None
    active = QApplication.activeWindow()
    return active if isinstance(active, QMainWindow) else None


def managed_overlay_geometry(parent=None) -> QRect:
    main = _main_window(parent)
    if main is not None and hasattr(main, "overlay_geometry"):
        geometry = main.overlay_geometry()
        if isinstance(geometry, QRect) and geometry.isValid():
            return geometry
    screen = (main.windowHandle().screen() if main and main.windowHandle() else None) or QApplication.primaryScreen()
    return screen.availableGeometry() if screen else QRect(0, 0, 360, 720)


def configure_mobile_text_input(widget) -> None:
    """Keep Android's native selection handles from becoming detached overlays.

    Qt exposes ImhNoTextHandles specifically for this purpose. Daymark still
    renders its own caret, while the floating Android tear-drop handles are
    suppressed for compact composer fields.
    """
    if not running_on_android():
        return
    widget.setInputMethodHints(
        widget.inputMethodHints() | Qt.InputMethodHint.ImhNoTextHandles
    )


class VerticalOnlyScrollArea(QScrollArea):
    """A scroll area that is physically incapable of horizontal panning.

    Hiding a horizontal scrollbar is not sufficient with QScroller: Android
    touch overshoot can still translate the complete child widget sideways.
    This class clamps the horizontal range and value after every layout/scroll
    update and ignores horizontal deltas at the content-scrolling boundary.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.setMinimumWidth(0)
        self.viewport().setMinimumWidth(0)
        bar = self.horizontalScrollBar()
        bar.valueChanged.connect(self._lock_horizontal_position)
        bar.rangeChanged.connect(self._lock_horizontal_range)

    def _lock_horizontal_position(self, *args) -> None:
        bar = self.horizontalScrollBar()
        if bar.value() != 0:
            blocked = bar.blockSignals(True)
            bar.setValue(0)
            bar.blockSignals(blocked)

    def _lock_horizontal_range(self, minimum=0, maximum=0) -> None:
        bar = self.horizontalScrollBar()
        if bar.minimum() != 0 or bar.maximum() != 0:
            blocked = bar.blockSignals(True)
            bar.setRange(0, 0)
            bar.setValue(0)
            bar.blockSignals(blocked)

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        # QScroller may send a horizontal delta even when the bar is hidden.
        # Discard it and allow only vertical content movement.
        super().scrollContentsBy(0, dy)
        self._lock_horizontal_position()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._lock_horizontal_range()


class ManagedDialog(QDialog):
    """Consistent Android overlay shown below Daymark's persistent top bar."""

    def __init__(self, parent=None, *, page: bool = True):
        super().__init__(parent)
        self._managed_compact = compact_dialog(parent)
        self._managed_page = page
        self._entrance_animation = None
        self._managed_animating = False
        self._geometry_sync_timer = QTimer(self)
        self._geometry_sync_timer.setSingleShot(True)
        self._geometry_sync_timer.setInterval(36)
        self._geometry_sync_timer.timeout.connect(self._sync_managed_geometry)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        if self._managed_compact:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
            input_method = QApplication.inputMethod()
            input_method.visibleChanged.connect(self._queue_managed_geometry_sync)
            if hasattr(input_method, "keyboardRectangleChanged"):
                input_method.keyboardRectangleChanged.connect(self._queue_managed_geometry_sync)

    def _queue_managed_geometry_sync(self, *args) -> None:
        if self._managed_compact and self.isVisible():
            # Keyboard visibility and keyboard-rectangle signals commonly arrive
            # in bursts. One restartable timer prevents several competing window
            # resizes and the visible up/down hop they caused.
            self._geometry_sync_timer.setInterval(170 if self._managed_animating else 36)
            self._geometry_sync_timer.start()

    def _managed_available_bounds(self) -> QRect:
        bounds = managed_overlay_geometry(self.parentWidget()).adjusted(4, 0, -4, -5)
        input_method = QApplication.inputMethod()
        keyboard = input_method.keyboardRectangle()
        if input_method.isVisible() and keyboard.isValid() and keyboard.height() > 40:
            keyboard_top = int(keyboard.top())
            if not bounds.top() < keyboard_top <= bounds.bottom() + 1:
                screen = QApplication.primaryScreen()
                screen_bottom = screen.availableGeometry().bottom() + 1 if screen else bounds.bottom() + 1
                keyboard_top = screen_bottom - int(keyboard.height())
            if bounds.top() < keyboard_top < bounds.bottom() + 1:
                bounds.setHeight(max(220, keyboard_top - bounds.top()))
        return bounds

    def _sync_managed_geometry(self) -> None:
        if not self._managed_compact:
            return
        bounds = self._managed_available_bounds()
        if self._managed_page:
            self.setGeometry(bounds)
        else:
            preferred_width = int(getattr(self, "_managed_preferred_width", 520))
            minimum_width = int(getattr(self, "_managed_minimum_width", 300))
            minimum_height = int(getattr(self, "_managed_minimum_height", 220))
            preferred_width = max(minimum_width, preferred_width)
            width = max(minimum_width, min(preferred_width, bounds.width() - 24))
            height = max(minimum_height, min(self.sizeHint().height(), bounds.height() - 32))
            self.setGeometry(
                bounds.left() + (bounds.width() - width) // 2,
                bounds.top() + (bounds.height() - height) // 2,
                width,
                height,
            )

    def showEvent(self, event) -> None:
        self._sync_managed_geometry()
        super().showEvent(event)
        if running_on_android():
            for editor in self.findChildren(QLineEdit):
                configure_mobile_text_input(editor)
            for editor in self.findChildren(QTextEdit):
                configure_mobile_text_input(editor)
        if not self._managed_compact:
            return
        target_geometry = self.geometry()
        if running_on_android() and self._managed_page:
            # Animating a top-level Android dialog geometry forces the platform
            # window and every nested scroll area to relayout on each frame.
            # Page dialogs therefore open in-place; their internal controls and
            # navigation retain motion without producing frame drops.
            self._managed_animating = False
            self.setGraphicsEffect(None)
            return
        effect = QGraphicsOpacityEffect(self)
        effect.setOpacity(0.88)
        self.setGraphicsEffect(effect)
        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(115 if running_on_android() else 170)
        fade.setStartValue(0.88)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade)
        self._managed_animating = True
        # Template/schedule/editor pages use a restrained push transition. The
        # keyboard-managed composer stays still so IME geometry never competes
        # with an entrance animation.
        if not running_on_android() and not getattr(self, "_keyboard_managed", False):
            start_geometry = target_geometry.translated(10 if self._managed_page else 0, 7 if not self._managed_page else 0)
            self.setGeometry(start_geometry)
            slide = QPropertyAnimation(self, b"geometry", self)
            slide.setDuration(180)
            slide.setStartValue(start_geometry)
            slide.setEndValue(target_geometry)
            slide.setEasingCurve(QEasingCurve.Type.OutCubic)
            group.addAnimation(slide)

        def finish() -> None:
            if self._entrance_animation is group:
                self._entrance_animation = None
            self._managed_animating = False
            self.setGeometry(target_geometry)
            self.setGraphicsEffect(None)
            group.deleteLater()

        group.finished.connect(finish)
        self._entrance_animation = group
        group.start()
        QTimer.singleShot(0, lambda: None)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Back, Qt.Key.Key_Escape):
            event.accept()
            self.reject()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if (
            self._managed_compact
            and not getattr(self, "_keyboard_managed", False)
            and not self._managed_animating
        ):
            self._geometry_sync_timer.setInterval(0)
            self._geometry_sync_timer.start()

    def _stop_managed_activity(self) -> None:
        self._geometry_sync_timer.stop()
        animation = self._entrance_animation
        self._entrance_animation = None
        if animation is not None:
            animation.stop()
            animation.deleteLater()
        self._managed_animating = False
        self.setGraphicsEffect(None)

    def _release_text_input(self) -> None:
        # Clear focus and selections before the Android window disappears.
        # Without this, Samsung/Qt can leave the native blue cursor handle
        # floating over the next screen.
        for line_edit in self.findChildren(QLineEdit):
            line_edit.deselect()
            line_edit.clearFocus()
        for text_edit in self.findChildren(QTextEdit):
            cursor = text_edit.textCursor()
            cursor.clearSelection()
            text_edit.setTextCursor(cursor)
            text_edit.clearFocus()
        input_method = QApplication.inputMethod()
        input_method.reset()
        input_method.hide()

    def accept(self) -> None:
        self._stop_managed_activity()
        self._release_text_input()
        super().accept()

    def reject(self) -> None:
        self._stop_managed_activity()
        self._release_text_input()
        super().reject()


def fit_phone_width(dialog: QDialog, parent=None) -> None:
    dialog.adjustSize()
    screen = None
    if parent and parent.windowHandle() and parent.windowHandle().screen():
        screen = parent.windowHandle().screen()
    if screen is None:
        screen = QApplication.primaryScreen()
    if screen:
        bounds = screen.availableGeometry()
        available = bounds.width()
        available_height = bounds.height()
        left, top = bounds.x(), bounds.y()
    else:
        available = parent.width() if parent and parent.width() > 0 else 360
        available_height = parent.height() if parent and parent.height() > 0 else 720
        left = top = 0
    width = max(304, min(640, available - 10))
    target_height = min(dialog.sizeHint().height(), available_height - 14)
    dialog.setMinimumWidth(width)
    dialog.setMaximumWidth(width)
    dialog.setMaximumHeight(available_height - 14)
    dialog.resize(width, max(320, target_height))
    x = left + max(5, (available - width) // 2)
    y = top + max(7, (available_height - dialog.height()) // 2)
    dialog.move(x, y)


class TimeField(QWidget):
    def __init__(self, value: time, parent=None):
        super().__init__(parent)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("h:mm AP")
        self.time_edit.setTime(QTime(value.hour, value.minute))
        self.time_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.time_edit.setMinimumHeight(42)
        self.time_edit.setMinimumWidth(116 if running_on_android() else 142)
        arrows = QFrame()
        arrows.setObjectName("stepper")
        arrow_layout = QVBoxLayout(arrows)
        arrow_layout.setContentsMargins(0, 1, 0, 1)
        arrow_layout.setSpacing(0)
        up = GlyphButton("up", t("minutes_later_15"), size=20)
        down = GlyphButton("down", t("minutes_earlier_15"), size=20)
        up.clicked.connect(lambda: self.time_edit.setTime(self.time_edit.time().addSecs(15 * 60)))
        down.clicked.connect(lambda: self.time_edit.setTime(self.time_edit.time().addSecs(-15 * 60)))
        arrow_layout.addWidget(up)
        arrow_layout.addWidget(down)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.addWidget(self.time_edit, 1)
        layout.addWidget(arrows)

    def time(self) -> QTime:
        return self.time_edit.time()

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.time_edit.setEnabled(enabled)
        for button in self.findChildren(GlyphButton):
            button.setEnabled(enabled)


class DateField(QWidget):
    """Compact Gregorian date editor for the supported LTR languages."""

    def __init__(self, value: date, compact: bool = False, parent=None):
        super().__init__(parent)
        self.day = SoftSelect()
        self.day.setFixedWidth(68 if compact else 84)
        self.day.setPopupMaxVisibleItems(10)
        self.month = SoftSelect()
        self.month.setMinimumWidth(104 if compact else 138)
        self.month.setPopupMaxVisibleItems(10)
        for month_number, month_name in enumerate(month_names(), start=1):
            self.month.addItem(month_name, month_number)
        self.month.setCurrentIndex(value.month - 1)
        self.year = QLineEdit(str(value.year))
        self.year.setObjectName("yearField")
        self.year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year.setMaxLength(4)
        self.year.setValidator(QIntValidator(1900, 2100, self.year))
        self.year.setFixedWidth(68 if compact else 86)
        self.year.setMinimumHeight(42)
        self.month.currentIndexChanged.connect(self._refresh_days)
        self.year.textChanged.connect(self._refresh_days)
        self._refresh_days()
        self.day.setCurrentIndex(max(0, self.day.findData(value.day)))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4 if compact else 8)
        layout.addWidget(self.day)
        layout.addWidget(self.month, 1)
        layout.addWidget(self.year)

    def _numeric_year(self) -> int:
        value = normalize_digits(self.year.text())
        return int(value) if value.isdigit() and len(value) == 4 else 0

    def _refresh_days(self, *args) -> None:
        selected_day = self.day.currentData() or 1
        year = self._numeric_year() or 2000
        month = self.month.currentData() or 1
        total = QDate(year, month, 1).daysInMonth()
        self.day.clear()
        for day_number in range(1, total + 1):
            self.day.addItem(str(day_number), day_number)
        self.day.setCurrentIndex(max(0, self.day.findData(min(selected_day, total))))

    def python_date(self) -> date | None:
        year = self._numeric_year()
        month = self.month.currentData() or 1
        day = self.day.currentData() or 1
        if not 1900 <= year <= 2100:
            return None
        try:
            return date(year, month, day)
        except ValueError:
            return None

    def date(self) -> QDate:
        value = self.python_date()
        return QDate(value.year, value.month, value.day) if value else QDate()

    def isValid(self) -> bool:
        return self.python_date() is not None

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.day.setEnabled(enabled)
        self.month.setEnabled(enabled)
        self.year.setEnabled(enabled)


def field_label(text: str, compact: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    if not compact:
        label.setFixedWidth(105)
    return label


class MessageDialog(ManagedDialog):
    def __init__(
        self,
        title: str,
        message: str,
        *,
        confirm_text: str = "OK",
        destructive: bool = False,
        cancellable: bool = False,
        parent=None,
    ):
        super().__init__(parent, page=False)
        compact = compact_dialog(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(0 if compact else 430)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        root_widget = QWidget()
        root_widget.setObjectName("dialogRoot")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(root_widget)
        layout = QVBoxLayout(root_widget)
        layout.setContentsMargins(*(16, 18, 16, 16) if compact else (26, 23, 26, 22))
        layout.setSpacing(11)

        heading = QLabel(title)
        heading.setObjectName("messageTitle")
        layout.addWidget(heading)
        copy = QLabel(message)
        copy.setObjectName("messageText")
        copy.setWordWrap(True)
        copy.setMinimumWidth(0 if compact else 360)
        layout.addWidget(copy)
        layout.addSpacing(7)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        if not compact:
            actions.addStretch()
        if cancellable:
            cancel = QPushButton(t("cancel"))
            cancel.setObjectName("secondary")
            if compact:
                cancel.setMinimumHeight(46)
                cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            else:
                cancel.setFixedSize(108, 40)
            cancel.clicked.connect(self.reject)
            actions.addWidget(cancel, 1 if compact else 0)
        confirm = QPushButton(t("ok") if confirm_text == "OK" else (t("delete") if confirm_text == "Delete" else confirm_text))
        confirm.setObjectName("dangerPrimary" if destructive else "primary")
        if compact:
            confirm.setMinimumHeight(46)
            confirm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            confirm.setFixedSize(108, 40)
        confirm.clicked.connect(self.accept)
        actions.addWidget(confirm, 1 if compact else 0)
        layout.addLayout(actions)


def show_warning(parent, title: str, message: str) -> None:
    MessageDialog(title, message, parent=parent).exec()


def confirm_action(parent, title: str, message: str, confirm_text: str = "Delete") -> bool:
    dialog = MessageDialog(
        title,
        message,
        confirm_text=confirm_text,
        destructive=True,
        cancellable=True,
        parent=parent,
    )
    return dialog.exec() == QDialog.DialogCode.Accepted


class TaskDetailsDialog(ManagedDialog):
    def __init__(self, task: Task, parent=None):
        super().__init__(parent, page=True)
        compact = compact_dialog(parent)
        self.setWindowTitle(t("task_details"))
        self.setMinimumWidth(0 if compact else 540)

        page = QFrame()
        page.setObjectName("managedDialogPage")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(*(14, 10, 14, 12) if compact else (24, 20, 24, 20))
        root.setSpacing(9)

        header = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=42)
        back.clicked.connect(self.accept)
        heading = QLabel(t("task_details"))
        heading.setObjectName("dialogTitleCompact")
        header.addWidget(back)
        header.addWidget(heading)
        header.addStretch()
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(scroll, vertical_only=True)
        content_widget = QWidget()
        content = QVBoxLayout(content_widget)
        content.setContentsMargins(0, 3, 0, 14)
        content.setSpacing(10 if compact else 16)
        content.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(content_widget)
        root.addWidget(scroll, 1)

        chips = QHBoxLayout()
        chips.setSpacing(8)
        if task.category_name:
            category_chip = QFrame()
            category_chip.setObjectName("detailChip")
            chip_layout = QHBoxLayout(category_chip)
            chip_layout.setContentsMargins(9, 4, 10, 4)
            chip_layout.setSpacing(6)
            dot = QLabel()
            dot.setFixedSize(7, 7)
            fallback_dot = theme_colors()["muted"]
            dot.setStyleSheet(f"background:{task.category_color or fallback_dot}; border-radius:3px;")
            chip_layout.addWidget(dot)
            chip_layout.addWidget(QLabel(task.category_name))
            chips.addWidget(category_chip)
        status = QLabel(t("overdue") if task.is_overdue else t("active"))
        status.setObjectName("detailOverdue" if task.is_overdue else "detailStatus")
        chips.addWidget(status)
        chips.addStretch()
        content.addLayout(chips)

        title = QLabel(task.title)
        title.setObjectName("detailTitle")
        title.setWordWrap(True)
        content.addWidget(title)

        notes_panel = QFrame()
        notes_panel.setObjectName("detailPanel")
        notes_layout = QVBoxLayout(notes_panel)
        notes_layout.setContentsMargins(13 if compact else 16, 11 if compact else 14, 13 if compact else 16, 12 if compact else 15)
        notes_layout.setSpacing(6)
        notes_heading = QLabel(t("notes"))
        notes_heading.setObjectName("detailSection")
        notes_layout.addWidget(notes_heading)
        notes = QLabel(task.notes or t("no_notes"))
        notes.setObjectName("detailBody" if task.notes else "detailPlaceholder")
        notes.setWordWrap(True)
        notes.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        notes_layout.addWidget(notes)
        content.addWidget(notes_panel)

        if task.subtasks:
            subtasks_panel = QFrame()
            subtasks_panel.setObjectName("detailPanel")
            subtasks_layout = QVBoxLayout(subtasks_panel)
            subtasks_layout.setContentsMargins(13 if compact else 16, 11 if compact else 14, 13 if compact else 16, 12 if compact else 15)
            subtasks_layout.setSpacing(7)
            subtasks_heading = QLabel(t("subtasks"))
            subtasks_heading.setObjectName("detailSection")
            subtasks_layout.addWidget(subtasks_heading)
            for item in task.subtasks:
                row = QLabel(("✓  " if item.completed else "○  ") + item.title)
                row.setObjectName("detailBody")
                row.setWordWrap(True)
                subtasks_layout.addWidget(row)
            content.addWidget(subtasks_panel)

        info_panel = QFrame()
        info_panel.setObjectName("detailPanel")
        info = QGridLayout(info_panel)
        info.setContentsMargins(13 if compact else 16, 11 if compact else 14, 13 if compact else 16, 12 if compact else 15)
        info.setHorizontalSpacing(13 if compact else 22)
        info.setVerticalSpacing(8 if compact else 12)
        info.setColumnStretch(1, 1)
        info_heading = QLabel(t("details"))
        info_heading.setObjectName("detailSection")
        info.addWidget(info_heading, 0, 0, 1, 2)

        if task.scheduled_date:
            date_value = format_date_full(task.scheduled_date)
            if task.all_day:
                time_value = t("all_day")
            elif task.scheduled_time:
                time_value = format_time_12(task.scheduled_time)
            else:
                time_value = "—"
        else:
            date_value, time_value = t("anytime"), "—"
        reminder_lookup = {minutes: t(key) for key, minutes in REMINDERS}
        rows = [
            (t("date"), date_value),
            (t("time"), time_value),
            (t("category"), task.category_name or t("uncategorized")),
            (t("repeats"), recurrence_label(task.recurrence)),
            (t("reminder"), reminder_lookup.get(task.reminder_minutes, t("no_reminder"))),
            (t("created"), format_datetime_brief(task.created_at)),
            (t("updated"), format_datetime_brief(task.updated_at)),
        ]
        for row_index, (label_text, value_text) in enumerate(rows, start=1):
            label = QLabel(label_text)
            label.setObjectName("detailKey")
            value = QLabel(value_text)
            value.setObjectName("detailValue")
            value.setWordWrap(True)
            info.addWidget(label, row_index, 0, Qt.AlignmentFlag.AlignTop)
            info.addWidget(value, row_index, 1, Qt.AlignmentFlag.AlignTop)
        content.addWidget(info_panel)
        content.addStretch()

        if not compact:
            self.resize(600, 720)


class SubtaskEditorRow(QFrame):
    def __init__(self, text: str = "", completed: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("subtaskEditorRow")
        self.completed = completed
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 4, 3)
        layout.setSpacing(8)
        self.check = HoverCheck(completed, 24)
        self.check.setToolTip(t("done"))
        self.edit = QLineEdit(text)
        self.edit.setObjectName("subtaskInput")
        self.edit.setPlaceholderText(t("subtask_placeholder"))
        self.edit.setMinimumHeight(42)
        configure_mobile_text_input(self.edit)
        self.remove = QPushButton("×")
        self.remove.setObjectName("subtaskRemove")
        self.remove.setToolTip(t("remove_subtask"))
        self.remove.setFixedSize(38, 38)
        self.remove.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.check)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.remove)

    def value(self, position: int) -> Subtask | None:
        title = self.edit.text().strip()
        if not title:
            return None
        return Subtask(None, title, self.check.isChecked(), position)


class SchedulePickerDialog(ManagedDialog):
    """Stable, strictly vertical task-scheduling surface.

    The calendar always reserves six week rows and date selection updates the
    existing buttons in place. This prevents the complete dialog from changing
    height when a date is selected. The scroll position is also restored around
    month changes so Android cannot visibly bounce the page.
    """

    def __init__(
        self,
        scheduled_date: date | None,
        scheduled_time: time | None,
        all_day: bool,
        recurrence: str,
        reminder_minutes: int | None,
        parent=None,
    ):
        super().__init__(parent, page=True)
        self.setWindowTitle(t("schedule_task"))
        self.selected_date = scheduled_date
        anchor = scheduled_date or date.today()
        self.visible_month = date(anchor.year, anchor.month, 1)
        self._day_buttons: list[QPushButton] = []
        self._day_button_values: list[tuple[QPushButton, date]] = []
        self._weekday_labels: list[QLabel] = []
        self._schedule_quick_columns: int | None = None
        self._schedule_fit_pending = False
        self._schedule_fit_running = False
        self._last_schedule_fit_width: int | None = None
        self._calendar_day_size = 36

        page = QFrame()
        page.setObjectName("managedDialogPage")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(14, 10, 14, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=42)
        back.clicked.connect(self.reject)
        title = QLabel(t("schedule_task"))
        title.setObjectName("dialogTitleCompact")
        header.addWidget(back)
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        self.scroll = VerticalOnlyScrollArea()
        # The body width is managed explicitly so no child sizeHint can create
        # a horizontal scroll range on Android.
        self.scroll.setWidgetResizable(False)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        enable_kinetic_scroll(self.scroll, vertical_only=True)

        body = QWidget()
        self._schedule_body = body
        body.setMinimumWidth(0)
        body.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        body_layout = QVBoxLayout(body)
        self._schedule_body_layout = body_layout
        body_layout.setContentsMargins(2, 4, 2, 22)
        body_layout.setSpacing(13)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(body)
        self.scroll.viewport().installEventFilter(self)
        root.addWidget(self.scroll, 1)

        month_row = QHBoxLayout()
        previous = GlyphButton("left", t("previous_month"), size=38)
        previous.clicked.connect(lambda: self._move_month(-1))
        self.month_title = QLabel()
        self.month_title.setObjectName("scheduleMonthTitle")
        self.month_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        following = GlyphButton("right", t("next_month"), size=38)
        following.clicked.connect(lambda: self._move_month(1))
        month_row.addWidget(previous)
        month_row.addWidget(self.month_title, 1)
        month_row.addWidget(following)
        body_layout.addLayout(month_row)

        self.calendar_host = QWidget()
        self.calendar_host.setMinimumWidth(0)
        self.calendar_grid = QGridLayout(self.calendar_host)
        self.calendar_grid.setContentsMargins(0, 0, 0, 0)
        self.calendar_grid.setHorizontalSpacing(3 if compact_dialog(parent) else 4)
        self.calendar_grid.setVerticalSpacing(4)
        for column in range(7):
            self.calendar_grid.setColumnStretch(column, 1)
        body_layout.addWidget(self.calendar_host)

        quick = QGridLayout()
        self._schedule_quick_layout = quick
        self._schedule_quick_buttons: list[QPushButton] = []
        # A real top margin keeps the first quick action clear of the calendar;
        # layout spacing alone was not enough while the calendar was relaid out.
        quick.setContentsMargins(0, 8, 0, 0)
        quick.setHorizontalSpacing(7)
        quick.setVerticalSpacing(8)
        quick.setColumnStretch(0, 1)
        quick.setColumnStretch(1, 1)
        self._schedule_quick_values = [
            (t("today"), date.today()),
            (t("tomorrow"), date.today() + timedelta(days=1)),
            (t("three_days_later"), date.today() + timedelta(days=3)),
            (t("this_sunday"), date.today() + timedelta(days=(6 - date.today().weekday()) % 7)),
            (t("no_date"), None),
        ]
        quick_height = 42 if compact_dialog(parent) else 40
        for index, (label, value) in enumerate(self._schedule_quick_values):
            button = QPushButton(label)
            button.setObjectName("scheduleQuick")
            button.setMinimumWidth(0)
            button.setFixedHeight(quick_height)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda checked=False, v=value: self._select_date(v))
            self._schedule_quick_buttons.append(button)
            quick.addWidget(button, index, 0)
        body_layout.addLayout(quick)

        separator = QFrame()
        separator.setObjectName("scheduleSeparator")
        separator.setFixedHeight(1)
        body_layout.addWidget(separator)

        self.time_toggle = CheckOption(t("time"), bool(scheduled_date and scheduled_time and not all_day))
        self.time_toggle.setMinimumHeight(26)
        self.time_field = TimeField(scheduled_time or time(9, 0))
        self.reminder = SoftSelect()
        for key, minutes in REMINDERS:
            self.reminder.addItem(t(key), minutes)
        self.reminder.setPopupFitToContents(True)
        self.reminder.setCurrentIndex(max(0, self.reminder.findData(reminder_minutes)))
        self.recurrence = SoftSelect()
        for value in RECURRENCE_KEYS:
            self.recurrence.addItem(recurrence_label(value), value)
        self.recurrence.setPopupFitToContents(True)
        self.recurrence.setCurrentIndex(max(0, self.recurrence.findData(recurrence)))

        responsive = QFrame()
        self._schedule_responsive = responsive
        responsive.setObjectName("scheduleResponsivePanel")
        responsive.setMinimumWidth(0)
        responsive.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        compact_schedule = compact_dialog(parent)

        reminder_label_widget = QLabel(t("reminder"))
        reminder_label_widget.setObjectName("scheduleRowLabel")
        reminder_label_widget.setMinimumHeight(22)
        repeat_label_widget = QLabel(t("repeat"))
        repeat_label_widget.setObjectName("scheduleRowLabel")
        repeat_label_widget.setMinimumHeight(22)

        if compact_schedule:
            # Each control gets its own vertical group. Explicit group spacing
            # prevents labels from painting over the field above them and keeps
            # the full bottom edge of the Repeat selector visible.
            responsive_layout = QVBoxLayout(responsive)
            responsive_layout.setContentsMargins(0, 2, 0, 10)
            responsive_layout.setSpacing(12)

            self.time_field.setMinimumWidth(0)
            self.time_field.time_edit.setMinimumWidth(0)
            self.time_field.setFixedHeight(46)
            self.time_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.reminder.setMinimumWidth(0)
            self.reminder.setFixedHeight(46)
            self.reminder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.recurrence.setMinimumWidth(0)
            self.recurrence.setFixedHeight(46)
            self.recurrence.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            time_group = QWidget()
            time_layout = QVBoxLayout(time_group)
            time_layout.setContentsMargins(0, 0, 0, 0)
            time_layout.setSpacing(6)
            time_layout.addWidget(self.time_toggle)
            time_layout.addWidget(self.time_field)

            reminder_group = QWidget()
            reminder_layout = QVBoxLayout(reminder_group)
            reminder_layout.setContentsMargins(0, 0, 0, 0)
            reminder_layout.setSpacing(6)
            reminder_layout.addWidget(reminder_label_widget)
            reminder_layout.addWidget(self.reminder)

            repeat_group = QWidget()
            repeat_layout = QVBoxLayout(repeat_group)
            repeat_layout.setContentsMargins(0, 0, 0, 0)
            repeat_layout.setSpacing(6)
            repeat_layout.addWidget(repeat_label_widget)
            repeat_layout.addWidget(self.recurrence)

            responsive_layout.addWidget(time_group)
            responsive_layout.addWidget(reminder_group)
            responsive_layout.addWidget(repeat_group)
        else:
            responsive_layout = QGridLayout(responsive)
            responsive_layout.setContentsMargins(0, 2, 0, 8)
            responsive_layout.setHorizontalSpacing(10)
            responsive_layout.setVerticalSpacing(10)
            responsive_layout.addWidget(self.time_toggle, 0, 0)
            responsive_layout.addWidget(self.time_field, 0, 1)
            responsive_layout.addWidget(reminder_label_widget, 1, 0)
            responsive_layout.addWidget(self.reminder, 1, 1)
            responsive_layout.addWidget(repeat_label_widget, 2, 0)
            responsive_layout.addWidget(self.recurrence, 2, 1)
            responsive_layout.setColumnStretch(1, 1)
        body_layout.addWidget(responsive)

        footer = QHBoxLayout()
        footer.addStretch()
        cancel = QPushButton(t("cancel"))
        cancel.setObjectName("secondary")
        cancel.setMinimumHeight(46)
        cancel.clicked.connect(self.reject)
        done = QPushButton(t("done"))
        done.setObjectName("primary")
        done.setMinimumHeight(46)
        done.clicked.connect(self.accept)
        footer.addWidget(cancel, 1 if compact_dialog(parent) else 0)
        footer.addWidget(done, 1 if compact_dialog(parent) else 0)
        root.addLayout(footer)

        self.time_toggle.toggled.connect(self._sync_controls)
        self._render_calendar(preserve_scroll=False)
        self._sync_controls()
        self._queue_schedule_fit(0)

    def eventFilter(self, watched, event) -> bool:
        scroll = getattr(self, "scroll", None)
        if (
            scroll is not None
            and watched is scroll.viewport()
            and event.type() in (QEvent.Type.Resize, QEvent.Type.Show)
        ):
            self._queue_schedule_fit(0)
        return super().eventFilter(watched, event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._queue_schedule_fit(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._queue_schedule_fit(0)

    def _queue_schedule_fit(self, delay: int = 0) -> None:
        if self._schedule_fit_pending:
            return
        self._schedule_fit_pending = True
        QTimer.singleShot(delay, self._fit_schedule_to_viewport)

    def _restore_schedule_scroll(self, value: int) -> None:
        if not hasattr(self, "scroll"):
            return
        bar = self.scroll.verticalScrollBar()
        bar.setValue(max(bar.minimum(), min(value, bar.maximum())))

    def _fit_schedule_to_viewport(self) -> None:
        """Size the schedule body without changing the visible scroll position."""
        self._schedule_fit_pending = False
        if self._schedule_fit_running:
            return
        if not hasattr(self, "scroll") or not hasattr(self, "_schedule_body"):
            return
        viewport = self.scroll.viewport()
        viewport_width = viewport.width()
        if viewport_width <= 0:
            return
        if (
            self._last_schedule_fit_width == viewport_width
            and self._schedule_body.width() == viewport_width
        ):
            return

        self._schedule_fit_running = True
        self._last_schedule_fit_width = viewport_width
        vertical = self.scroll.verticalScrollBar()
        previous_scroll = vertical.value()
        try:
            content_width = max(1, viewport_width)

            # Reflow quick actions only when the actual column count changes.
            # Rebuilding this grid on every date selection caused a visible hop.
            quick_columns = 1 if content_width < 430 else 2
            if quick_columns != self._schedule_quick_columns:
                while self._schedule_quick_layout.count():
                    item = self._schedule_quick_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(self._schedule_body)
                for index, button in enumerate(self._schedule_quick_buttons):
                    button.setMinimumWidth(0)
                    button.setMaximumWidth(content_width)
                    button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    row = index // quick_columns
                    column = index % quick_columns
                    is_no_date = self._schedule_quick_values[index][1] is None
                    if is_no_date and quick_columns > 1:
                        self._schedule_quick_layout.addWidget(button, row, 0, 1, quick_columns)
                    else:
                        self._schedule_quick_layout.addWidget(button, row, column)
                self._schedule_quick_layout.setColumnStretch(0, 1)
                self._schedule_quick_layout.setColumnStretch(1, 1 if quick_columns > 1 else 0)
                self._schedule_quick_columns = quick_columns

            self.calendar_host.setMinimumWidth(0)
            self.calendar_host.setMaximumWidth(content_width)
            self._schedule_responsive.setMinimumWidth(0)
            self._schedule_responsive.setMaximumWidth(content_width)

            # The calendar always has one weekday row plus six week rows.
            body_margins = 4
            inner_width = max(1, content_width - body_margins)
            horizontal_spacing = max(0, self.calendar_grid.horizontalSpacing()) * 6
            day_size = max(28, min(40, (inner_width - horizontal_spacing) // 7))
            self._calendar_day_size = day_size
            for label in self._weekday_labels:
                label.setFixedHeight(20)
            for button in self._day_buttons:
                button.setFixedSize(day_size, day_size)

            vertical_spacing = max(0, self.calendar_grid.verticalSpacing())
            calendar_height = 20 + (6 * day_size) + (6 * vertical_spacing) + 2
            self.calendar_host.setFixedHeight(calendar_height)

            self._schedule_body.setMinimumWidth(0)
            self._schedule_body.setMaximumWidth(content_width)
            self._schedule_body.setFixedWidth(content_width)
            self._schedule_body_layout.activate()
            natural_height = max(
                viewport.height(),
                self._schedule_body_layout.sizeHint().height(),
                self._schedule_body_layout.minimumSize().height(),
            ) + 4
            self._schedule_body.setFixedHeight(natural_height)
            self._schedule_body.resize(content_width, natural_height)

            horizontal = self.scroll.horizontalScrollBar()
            blocked = horizontal.blockSignals(True)
            horizontal.setRange(0, 0)
            horizontal.setValue(0)
            horizontal.blockSignals(blocked)
            self.calendar_grid.invalidate()
            self._schedule_body.updateGeometry()
            self._restore_schedule_scroll(previous_scroll)
        finally:
            self._schedule_fit_running = False

    def _move_month(self, delta: int) -> None:
        year = self.visible_month.year + (self.visible_month.month - 1 + delta) // 12
        month = (self.visible_month.month - 1 + delta) % 12 + 1
        self.visible_month = date(year, month, 1)
        self._render_calendar()

    def _select_date(self, value: date | None) -> None:
        previous_scroll = self.scroll.verticalScrollBar().value()
        previous_month = self.visible_month
        self.selected_date = value
        if value is not None:
            self.visible_month = date(value.year, value.month, 1)

        if self.visible_month != previous_month:
            self._render_calendar()
        else:
            self._refresh_calendar_selection()
        self._sync_controls()
        self._restore_schedule_scroll(previous_scroll)

    def _six_week_calendar(self) -> list[list[date]]:
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(
            self.visible_month.year, self.visible_month.month
        )
        while len(weeks) < 6:
            start = weeks[-1][-1] + timedelta(days=1)
            weeks.append([start + timedelta(days=offset) for offset in range(7)])
        return weeks[:6]

    @staticmethod
    def _refresh_dynamic_style(widget: QWidget) -> None:
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()

    def _refresh_calendar_selection(self) -> None:
        for button, value in self._day_button_values:
            selected = value == self.selected_date
            if button.property("selected") != selected:
                button.setProperty("selected", selected)
                self._refresh_dynamic_style(button)

    def _render_calendar(self, *, preserve_scroll: bool = True) -> None:
        previous_scroll = self.scroll.verticalScrollBar().value() if preserve_scroll else 0
        self.calendar_host.setUpdatesEnabled(False)
        try:
            clear_layout(self.calendar_grid)
            self._day_buttons.clear()
            self._day_button_values.clear()
            self._weekday_labels.clear()

            sunday = date(2024, 1, 7)
            for column in range(7):
                label = QLabel(weekday_name(sunday + timedelta(days=column), short=True))
                label.setObjectName("calendarWeekday")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFixedHeight(20)
                self.calendar_grid.addWidget(label, 0, column)
                self._weekday_labels.append(label)

            for row, week in enumerate(self._six_week_calendar(), start=1):
                for column, value in enumerate(week):
                    button = QPushButton(localize_digits(value.day))
                    button.setObjectName("scheduleDay")
                    button.setProperty("outsideMonth", value.month != self.visible_month.month)
                    button.setProperty("selected", value == self.selected_date)
                    button.setProperty("today", value == date.today())
                    button.setMinimumWidth(0)
                    button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    button.setFixedSize(self._calendar_day_size, self._calendar_day_size)
                    button.clicked.connect(lambda checked=False, v=value: self._select_date(v))
                    self.calendar_grid.addWidget(
                        button,
                        row,
                        column,
                        alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    )
                    self._day_buttons.append(button)
                    self._day_button_values.append((button, value))
            self.month_title.setText(format_month_year(self.visible_month))
            self.calendar_grid.activate()
        finally:
            self.calendar_host.setUpdatesEnabled(True)
            self.calendar_host.update()

        self._restore_schedule_scroll(previous_scroll)

    def _sync_controls(self) -> None:
        has_date = self.selected_date is not None
        self.time_toggle.setEnabled(has_date)
        timed = has_date and self.time_toggle.isChecked()
        self.time_field.setEnabled(timed)
        self.reminder.setEnabled(timed)
        self.recurrence.setEnabled(has_date)
        if not timed:
            self.reminder.setCurrentIndex(0)

    def value(self) -> tuple[date | None, time | None, bool, str, int | None]:
        if self.selected_date is None:
            return None, None, True, "none", None
        timed = self.time_toggle.isChecked()
        qtime = self.time_field.time()
        return (
            self.selected_date,
            time(qtime.hour(), qtime.minute()) if timed else None,
            not timed,
            self.recurrence.currentData() or "none",
            self.reminder.currentData() if timed else None,
        )


class TemplatePreviewDialog(ManagedDialog):
    def __init__(self, template: TaskTemplate, categories: list[Category], parent=None):
        super().__init__(parent, page=True)
        self.template = template
        self.setWindowTitle(template.title)

        page = QFrame()
        page.setObjectName("templatePreview")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(14, 10, 14, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=42)
        back.clicked.connect(self.reject)
        heading = QLabel(t("customize_template"))
        heading.setObjectName("dialogTitleCompact")
        header.addWidget(back)
        header.addWidget(heading)
        header.addStretch()
        root.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(2, 2, 2, 16)
        body_layout.setSpacing(12)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(body)
        root.addWidget(self.scroll, 1)

        self.category = SoftSelect()
        self.category.addItem(t("no_category"), None)
        for category in categories:
            self.category.addItem(category.name, category.id)
        if template.category_hint:
            match = next(
                (item.id for item in categories if item.name.casefold() == template.category_hint.casefold()),
                None,
            )
            if match is not None:
                self.category.setCurrentIndex(max(0, self.category.findData(match)))
        body_layout.addWidget(self.category)

        emoji = QLabel(template.emoji)
        emoji.setObjectName("templateHeroEmoji")
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addWidget(emoji)

        self.title = QLineEdit(template.title)
        self.title.setObjectName("templateTitleInput")
        self.title.setMinimumHeight(48)
        body_layout.addWidget(self.title)

        description = QLabel(template.description)
        description.setObjectName("templateDescription")
        description.setWordWrap(True)
        body_layout.addWidget(description)

        template_settings = QFrame()
        template_settings.setObjectName("detailPanel")
        settings_layout = QGridLayout(template_settings)
        settings_layout.setContentsMargins(12, 10, 12, 10)
        settings_layout.setHorizontalSpacing(10)
        settings_layout.setVerticalSpacing(8)
        repeat_label_widget = QLabel(t("repeat"))
        repeat_label_widget.setObjectName("scheduleRowLabel")
        self.recurrence = SoftSelect()
        for value in RECURRENCE_KEYS:
            self.recurrence.addItem(recurrence_label(value), value)
        self.recurrence.setPopupFitToContents(True)
        self.recurrence.setCurrentIndex(max(0, self.recurrence.findData(template.recurrence)))
        settings_layout.addWidget(repeat_label_widget, 0, 0)
        settings_layout.addWidget(self.recurrence, 0, 1)
        self.template_time_toggle = CheckOption(t("time"), False)
        self.template_time = TimeField(time(8, 0))
        self.template_time.setEnabled(False)
        self.template_time_toggle.toggled.connect(self.template_time.setEnabled)
        settings_layout.addWidget(self.template_time_toggle, 1, 0)
        settings_layout.addWidget(self.template_time, 1, 1)
        body_layout.addWidget(template_settings)

        heading = QLabel(t("subtasks"))
        heading.setObjectName("detailSection")
        body_layout.addWidget(heading)
        self.subtasks_host = QWidget()
        self.subtasks_layout = QVBoxLayout(self.subtasks_host)
        self.subtasks_layout.setContentsMargins(0, 0, 0, 0)
        self.subtasks_layout.setSpacing(6)
        self.subtask_rows: list[SubtaskEditorRow] = []
        for subtask in template.subtasks:
            self._add_subtask(subtask)
        body_layout.addWidget(self.subtasks_host)

        add_subtask = QPushButton("+  " + t("add_subtask"))
        add_subtask.setObjectName("templateAddSubtask")
        add_subtask.clicked.connect(lambda: self._add_subtask("", focus=True))
        body_layout.addWidget(add_subtask)

        use = QPushButton(t("use_template"))
        use.setObjectName("primary")
        use.setMinimumHeight(50)
        use.clicked.connect(self._accept_if_valid)
        root.addWidget(use)
        apply_text_input_direction(self)

    def _add_subtask(self, text: str, focus: bool = False) -> None:
        row = SubtaskEditorRow(text)
        row.remove.clicked.connect(lambda: self._remove_subtask(row))
        self.subtasks_layout.addWidget(row)
        self.subtask_rows.append(row)
        if focus:
            row.edit.setFocus()
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(row, 8, 8))

    def _remove_subtask(self, row: SubtaskEditorRow) -> None:
        if row in self.subtask_rows:
            self.subtask_rows.remove(row)
            row.setParent(None)
            row.deleteLater()

    def _accept_if_valid(self) -> None:
        if not self.title.text().strip():
            show_warning(self, t("title_needed"), t("title_needed_message"))
            return
        self.accept()

    def value(self) -> dict[str, object]:
        subtasks = [
            value.title
            for position, row in enumerate(self.subtask_rows)
            if (value := row.value(position)) is not None
        ]
        return {
            "title": self.title.text().strip(),
            "notes": self.template.description,
            "subtasks": subtasks,
            "category_id": self.category.currentData(),
            "recurrence": self.recurrence.currentData() or "none",
            "scheduled_time": (
                time(self.template_time.time().hour(), self.template_time.time().minute())
                if self.template_time_toggle.isChecked()
                else None
            ),
        }


class TaskTemplateDialog(ManagedDialog):
    def __init__(self, categories: list[Category], parent=None):
        super().__init__(parent, page=True)
        self.categories = categories
        self.selected_value: dict[str, object] | None = None
        self.setWindowTitle(t("task_templates"))

        page = QWidget()
        page.setObjectName("templateLibrary")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(14, 10, 14, 12)
        root.setSpacing(9)

        header = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=42)
        back.clicked.connect(self.reject)
        title = QLabel(t("task_templates"))
        title.setObjectName("dialogTitleCompact")
        header.addWidget(back)
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        subtitle = QLabel(t("template_hint"))
        subtitle.setObjectName("dialogSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText(t("template_search"))
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(150)
        self._search_timer.timeout.connect(self._rebuild)
        self.search.textChanged.connect(lambda *_: self._search_timer.start())
        root.addWidget(self.search)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        self.host = QWidget()
        self.list_layout = QVBoxLayout(self.host)
        self.list_layout.setContentsMargins(0, 4, 0, 12)
        self.list_layout.setSpacing(7)
        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll, 1)
        self._rebuild()
        apply_text_input_direction(self)

    def _rebuild(self) -> None:
        self._search_timer.stop()
        self.host.setUpdatesEnabled(False)
        try:
            clear_layout(self.list_layout)
            token = self.search.text().strip().casefold()
            for group, templates in grouped_templates():
                visible = [
                    item for item in templates
                    if not token or token in item.title.casefold() or token in item.description.casefold()
                ]
                if not visible:
                    continue
                heading = QLabel(group)
                heading.setObjectName("templateGroup")
                self.list_layout.addWidget(heading)
                for template in visible:
                    button = QPushButton(f"{template.emoji}    {template.title}")
                    button.setObjectName("templateCard")
                    button.setMinimumHeight(56)
                    button.setCursor(Qt.CursorShape.PointingHandCursor)
                    button.clicked.connect(lambda checked=False, item=template: self._open_template(item))
                    self.list_layout.addWidget(button)
            self.list_layout.addStretch()
        finally:
            self.host.setUpdatesEnabled(True)
            self.host.update()

    def _open_template(self, template: TaskTemplate) -> None:
        dialog = TemplatePreviewDialog(template, self.categories, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_value = dialog.value()
            self.accept()


class TaskDialog(ManagedDialog):
    CREATE_CATEGORY = "__create_category__"

    def __init__(
        self,
        categories: list[Category],
        task: Task | None = None,
        initial_date: date | None = None,
        category_creator: Callable[[str, str], Category | None] | None = None,
        parent=None,
    ):
        super().__init__(parent, page=True)
        self.compact = compact_dialog(parent)
        self._keyboard_managed = self.compact
        self.original = task
        self.categories = list(categories)
        self.category_creator = category_creator
        self._previous_category_id = task.category_id if task else None
        self.scheduled_date = task.scheduled_date if task else initial_date
        self.scheduled_time = task.scheduled_time if task else None
        self.all_day = task.all_day if task else True
        self.recurrence_value = task.recurrence if task else "none"
        self.reminder_minutes = task.reminder_minutes if task else None
        self.subtask_rows: list[SubtaskEditorRow] = []
        self._subtask_animations: list[object] = []
        self._initial_focus_done = False
        self._composer_height = 0
        self._child_dialog_opening = False

        self.setWindowTitle(t("edit_task") if task else t("new_task_title"))
        self.setObjectName("taskComposerDialog")

        sheet = QFrame()
        self.sheet = sheet
        sheet.setObjectName("taskComposerSheet")
        shell = QVBoxLayout(self)
        # Android may present QDialog as a full overlay regardless of its window
        # geometry. Keep the actual composer sheet top-anchored with explicit,
        # symmetrical margins so its width is correct from the very first frame.
        shell.setContentsMargins(7 if self.compact else 4, 0 if self.compact else 4, 7 if self.compact else 4, 6 if self.compact else 4)
        shell.setAlignment(Qt.AlignmentFlag.AlignTop)
        sheet.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed if self.compact else QSizePolicy.Policy.Expanding)
        shell.addWidget(sheet, 0, Qt.AlignmentFlag.AlignTop)
        root = QVBoxLayout(sheet)
        self.composer_layout = root
        root.setContentsMargins(16 if self.compact else 24, 10 if self.compact else 18, 16 if self.compact else 24, 10)
        root.setSpacing(7)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 2)
        header.setSpacing(8)
        close = GlyphButton("left", t("close"), size=42)
        close.clicked.connect(self.reject)
        heading = QLabel(t("edit_task") if task else t("new_task_title"))
        heading.setObjectName("composerHeaderTitle")
        header.addWidget(close)
        header.addWidget(heading)
        header.addStretch()
        root.addLayout(header)

        self.title = QLineEdit(task.title if task else "")
        self.title.setObjectName("composerTitle")
        self.title.setPlaceholderText(t("task_title"))
        self.title.setClearButtonEnabled(True)
        self.title.setMinimumHeight(54)
        configure_mobile_text_input(self.title)
        root.addWidget(self.title)

        # Subtasks expand naturally for the first few rows and then become the
        # only scrolling region in the composer. This keeps notes and actions
        # directly below the rows instead of distributing them across the page.
        self.subtasks_scroll = QScrollArea()
        self.subtasks_scroll.setObjectName("composerSubtasks")
        self.subtasks_scroll.setWidgetResizable(True)
        self.subtasks_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.subtasks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.subtasks_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        enable_kinetic_scroll(self.subtasks_scroll, vertical_only=True)
        self.subtasks_host = QWidget()
        self.subtasks_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.subtasks_layout = QVBoxLayout(self.subtasks_host)
        self.subtasks_layout.setContentsMargins(0, 0, 0, 0)
        self.subtasks_layout.setSpacing(5)
        self.subtasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.subtasks_scroll.setWidget(self.subtasks_host)
        self.subtasks_scroll.setFixedHeight(52)
        root.addWidget(self.subtasks_scroll)

        existing_subtasks = task.subtasks if task and task.subtasks else []
        if existing_subtasks:
            for subtask in existing_subtasks:
                self._add_subtask(subtask.title, subtask.completed)
        else:
            self._add_subtask("")

        self.notes_toggle = QPushButton(t("hide_notes") if task and task.notes else t("add_notes"))
        self.notes_toggle.setObjectName("composerNotesToggle")
        self.notes_toggle.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.notes_toggle.clicked.connect(self._toggle_notes)
        root.addWidget(self.notes_toggle, 0, Qt.AlignmentFlag.AlignLeft)
        self.notes = QTextEdit(task.notes if task else "")
        self.notes.setObjectName("composerNotes")
        self.notes.setPlaceholderText(t("notes_optional"))
        self.notes.setFixedHeight(82)
        self.notes.setVisible(bool(task and task.notes))
        configure_mobile_text_input(self.notes)
        enable_kinetic_scroll(self.notes, vertical_only=True)
        root.addWidget(self.notes)

        self.schedule_summary = QLabel()
        self.schedule_summary.setObjectName("composerScheduleSummary")
        root.addWidget(self.schedule_summary)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self.category = SoftSelect()
        self.category.setObjectName("composerCategory")
        self.category.setMinimumWidth(118)
        self.category.setMaximumWidth(170)
        self.category.setPopupMaxVisibleItems(7)
        self._populate_categories(self._previous_category_id)
        self.category.currentIndexChanged.connect(self._category_changed)
        toolbar.addWidget(self.category, 1)

        self.schedule_button = GlyphButton("calendar", t("schedule_task"), size=46)
        self.schedule_button.clicked.connect(self._open_schedule)
        toolbar.addWidget(self.schedule_button)
        self.add_subtask_button = GlyphButton("subtask", t("add_subtask"), size=46)
        self.add_subtask_button.clicked.connect(lambda: self._add_subtask("", focus=True))
        toolbar.addWidget(self.add_subtask_button)
        self.templates_button = GlyphButton("template", t("task_templates"), size=46)
        self.templates_button.clicked.connect(self._open_templates)
        toolbar.addWidget(self.templates_button)
        self.save_button = GlyphButton("send", t("send_task"), size=52, accent=True)
        self.save_button.clicked.connect(self._validate)
        toolbar.addWidget(self.save_button)
        root.addLayout(toolbar)

        self._update_schedule_summary()
        apply_text_input_direction(self)
        QTimer.singleShot(0, self._update_composer_layout)
        if self.compact:
            self._keyboard_sync_timer = QTimer(self)
            self._keyboard_sync_timer.setSingleShot(True)
            self._keyboard_sync_timer.setInterval(24)
            self._keyboard_sync_timer.timeout.connect(self._sync_keyboard_geometry)
            input_method = QApplication.inputMethod()
            input_method.visibleChanged.connect(self._schedule_keyboard_geometry_sync)
            if hasattr(input_method, "keyboardRectangleChanged"):
                input_method.keyboardRectangleChanged.connect(self._schedule_keyboard_geometry_sync)
        else:
            self.resize(650, 620)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self.compact:
            self.title.setFocus(Qt.FocusReason.OtherFocusReason)
            return
        # One primary request plus a guarded fallback is enough. Repeated focus
        # stealing made Samsung keyboards briefly close/reopen when the user
        # tapped a subtask before the delayed title timers had finished.
        QTimer.singleShot(70, self._activate_title_input)
        QTimer.singleShot(260, self._activate_title_input)
        QTimer.singleShot(0, self._schedule_keyboard_geometry_sync)

    def _activate_title_input(self) -> None:
        if not self.isVisible():
            return
        focused = self.focusWidget()
        # Never steal focus from another editor the user has already tapped.
        if self._initial_focus_done:
            return
        if isinstance(focused, (QLineEdit, QTextEdit)) and focused is not self.title:
            self._initial_focus_done = True
            return
        self._initial_focus_done = True
        self.raise_()
        self.activateWindow()
        self.title.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.title.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self.title.setCursorPosition(len(self.title.text()))
        self.title.ensurePolished()
        input_method = QApplication.inputMethod()
        input_method.update(Qt.InputMethodQuery.ImEnabled | Qt.InputMethodQuery.ImCursorRectangle)
        if not input_method.isVisible():
            input_method.show()
        self._schedule_keyboard_geometry_sync()

    def _populate_categories(self, selected_id=None) -> None:
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItem(t("no_category"), None)
        for item in self.categories:
            self.category.addItem(item.name, item.id)
        if self.category_creator is not None:
            self.category.addItem("+  " + t("create_new"), self.CREATE_CATEGORY)
        index = self.category.findData(selected_id)
        self.category.setCurrentIndex(max(0, index))
        self.category.blockSignals(False)

    def _category_changed(self, index: int) -> None:
        value = self.category.currentData()
        if value == self.CREATE_CATEGORY:
            QTimer.singleShot(0, self._create_category)
        else:
            self._previous_category_id = value

    def _create_category(self) -> None:
        self.category.setCurrentIndex(max(0, self.category.findData(self._previous_category_id)))
        dialog = CategoryDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted or self.category_creator is None:
            return
        category = self.category_creator(dialog.name.text().strip(), dialog.color)
        if category is None:
            return
        self.categories.append(category)
        self._previous_category_id = category.id
        self._populate_categories(category.id)

    def _subtask_natural_height(self) -> int:
        count = max(1, len(self.subtask_rows))
        row_height = max(46, max((row.sizeHint().height() for row in self.subtask_rows), default=46))
        return count * row_height + max(0, count - 1) * self.subtasks_layout.spacing() + 2

    def _update_subtask_viewport(self, maximum: int = 168) -> None:
        natural = self._subtask_natural_height()
        self.subtasks_scroll.setFixedHeight(max(50, min(maximum, natural)))
        self.subtasks_host.adjustSize()

    def _update_composer_layout(self) -> None:
        if not hasattr(self, "subtasks_scroll"):
            return
        self._update_subtask_viewport()
        self.composer_layout.activate()
        # The sheet height is intentionally stable. Content changes only alter
        # the internal subtask viewport, avoiding the visible shrink/grow bounce.
        self._schedule_keyboard_geometry_sync()

    def _focus_subtask(self, row: SubtaskEditorRow) -> None:
        if not self.isVisible() or row not in self.subtask_rows:
            return
        row.edit.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        row.edit.setCursorPosition(len(row.edit.text()))
        self.subtasks_scroll.ensureWidgetVisible(row, 8, 8)
        input_method = QApplication.inputMethod()
        if not input_method.isVisible():
            input_method.show()

    def _add_subtask(self, text: str, completed: bool = False, focus: bool = False) -> None:
        row = SubtaskEditorRow(text, completed)
        row.remove.clicked.connect(lambda: self._remove_subtask(row))
        self.subtasks_layout.addWidget(row)
        self.subtask_rows.append(row)

        if not focus or not self.isVisible():
            self._update_composer_layout()
            return

        # Insert new rows with a short height/fade animation. The outer sheet
        # remains fixed, so only the local subtask region moves.
        target_height = max(48, row.sizeHint().height())
        row.setMinimumHeight(0)
        row.setMaximumHeight(0)
        opacity = None
        if not running_on_android():
            opacity = QGraphicsOpacityEffect(row)
            opacity.setOpacity(0.0)
            row.setGraphicsEffect(opacity)

        height_animation = QPropertyAnimation(row, b"maximumHeight", row)
        height_animation.setDuration(190)
        height_animation.setStartValue(0)
        height_animation.setEndValue(target_height)
        height_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        group = QParallelAnimationGroup(row)
        group.addAnimation(height_animation)
        if not running_on_android():
            fade_animation = QPropertyAnimation(opacity, b"opacity", row)
            fade_animation.setDuration(150)
            fade_animation.setStartValue(0.0)
            fade_animation.setEndValue(1.0)
            fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            group.addAnimation(fade_animation)
        self._subtask_animations.append(group)

        def finish() -> None:
            row.setMaximumHeight(16_777_215)
            if opacity is not None:
                row.setGraphicsEffect(None)
            if group in self._subtask_animations:
                self._subtask_animations.remove(group)
            self._update_composer_layout()
            self._focus_subtask(row)
            group.deleteLater()

        group.finished.connect(finish)
        # Reserve the target viewport once. The row itself expands smoothly,
        # but the whole composer is not forced through a layout pass every frame.
        self._update_subtask_viewport()
        group.start()

    def _remove_subtask(self, row: SubtaskEditorRow) -> None:
        if row not in self.subtask_rows:
            return
        if len(self.subtask_rows) == 1:
            row.edit.clear()
            row.edit.setFocus()
            return
        self.subtask_rows.remove(row)
        start_height = max(1, row.height(), row.sizeHint().height())
        row.setMinimumHeight(0)
        row.setMaximumHeight(start_height)
        animation = QPropertyAnimation(row, b"maximumHeight", self)
        animation.setDuration(125 if running_on_android() else 155)
        animation.setStartValue(start_height)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finish_removal() -> None:
            if animation in self._subtask_animations:
                self._subtask_animations.remove(animation)
            row.hide()
            row.setParent(None)
            row.deleteLater()
            self._update_composer_layout()
            animation.deleteLater()

        animation.finished.connect(finish_removal)
        self._subtask_animations.append(animation)
        animation.start()

    def _toggle_notes(self) -> None:
        visible = not self.notes.isVisible()
        if not visible and self.notes.hasFocus():
            self.notes.clearFocus()
            QApplication.inputMethod().reset()
        self.notes.setVisible(visible)
        self.notes_toggle.setText(t("hide_notes") if visible else t("add_notes"))
        # The composer sheet has a stable height, so showing notes simply
        # reflows content once without resizing the window or restarting the IME.
        self._update_composer_layout()

    def _hide_keyboard(self) -> None:
        focus = self.focusWidget()
        if focus is not None:
            focus.clearFocus()
        self._initial_focus_done = True
        input_method = QApplication.inputMethod()
        input_method.reset()
        input_method.hide()
        self._schedule_keyboard_geometry_sync()

    def _open_schedule(self) -> None:
        if self._child_dialog_opening:
            return
        self._child_dialog_opening = True
        self._hide_keyboard()
        QTimer.singleShot(0, self._exec_schedule_dialog)

    def _exec_schedule_dialog(self) -> None:
        if not self.isVisible():
            self._child_dialog_opening = False
            return
        try:
            dialog = SchedulePickerDialog(
                self.scheduled_date,
                self.scheduled_time,
                self.all_day,
                self.recurrence_value,
                self.reminder_minutes,
                self,
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                (
                    self.scheduled_date,
                    self.scheduled_time,
                    self.all_day,
                    self.recurrence_value,
                    self.reminder_minutes,
                ) = dialog.value()
                self._update_schedule_summary()
        finally:
            self._child_dialog_opening = False
            self._schedule_keyboard_geometry_sync()

    def _open_templates(self) -> None:
        if self._child_dialog_opening:
            return
        self._child_dialog_opening = True
        self._hide_keyboard()
        QTimer.singleShot(0, self._exec_templates_dialog)

    def _exec_templates_dialog(self) -> None:
        if not self.isVisible():
            self._child_dialog_opening = False
            return
        try:
            dialog = TaskTemplateDialog(self.categories, self)
            if dialog.exec() != QDialog.DialogCode.Accepted or not dialog.selected_value:
                return
            value = dialog.selected_value
            self.title.setText(str(value.get("title", "")))
            self.notes.setPlainText(str(value.get("notes", "")))
            self.notes.setVisible(bool(self.notes.toPlainText()))
            self.notes_toggle.setText(t("hide_notes") if self.notes.isVisible() else t("add_notes"))
            for row in list(self.subtask_rows):
                row.setParent(None)
                row.deleteLater()
            self.subtask_rows.clear()
            subtasks = [str(item) for item in value.get("subtasks", [])]
            for item in subtasks or [""]:
                self._add_subtask(item)
            self._update_composer_layout()
            category_id = value.get("category_id")
            self._previous_category_id = category_id
            self.category.setCurrentIndex(max(0, self.category.findData(category_id)))
            recurrence = str(value.get("recurrence", "none"))
            template_time = value.get("scheduled_time")
            if recurrence != "none" or isinstance(template_time, time):
                self.scheduled_date = self.scheduled_date or date.today()
                self.recurrence_value = recurrence
                if isinstance(template_time, time):
                    self.scheduled_time = template_time
                    self.all_day = False
                else:
                    self.all_day = True
            self._update_schedule_summary()
        finally:
            self._child_dialog_opening = False
            self._schedule_keyboard_geometry_sync()

    def _update_schedule_summary(self) -> None:
        if self.scheduled_date is None:
            text = t("schedule_summary_anytime")
        elif self.all_day or self.scheduled_time is None:
            text = t("schedule_summary_all_day", date=format_date_medium(self.scheduled_date))
        else:
            text = t(
                "schedule_summary_timed",
                date=format_date_medium(self.scheduled_date),
                time=format_time_12(self.scheduled_time),
            )
        self.schedule_summary.setText(text)

    def _schedule_keyboard_geometry_sync(self, *args) -> None:
        if self.compact and hasattr(self, "_keyboard_sync_timer"):
            self._keyboard_sync_timer.start()

    def _sync_managed_geometry(self) -> None:
        # ManagedDialog calls this before TaskDialog.showEvent; overriding it
        # prevents the composer from flashing at full-screen height first.
        self._sync_keyboard_geometry()

    def _sync_keyboard_geometry(self, *args) -> None:
        if not self.compact or not hasattr(self, "sheet"):
            return

        # Keep the transparent dialog overlay fixed. Android can restart the IME
        # when a dialog window itself is repeatedly resized during focus changes.
        # Only the top-anchored inner sheet changes height.
        overlay = managed_overlay_geometry(self.parentWidget())
        if self.geometry() != overlay:
            self.setGeometry(overlay)

        input_method = QApplication.inputMethod()
        keyboard = input_method.keyboardRectangle()
        keyboard_visible = input_method.isVisible() and keyboard.isValid() and keyboard.height() > 40
        available_bottom = overlay.bottom() + 1
        if keyboard_visible:
            keyboard_top = int(keyboard.top())
            if not overlay.top() < keyboard_top <= overlay.bottom() + 1:
                screen = QApplication.primaryScreen()
                screen_bottom = screen.availableGeometry().bottom() + 1 if screen else overlay.bottom() + 1
                keyboard_top = screen_bottom - int(keyboard.height())
            if overlay.top() < keyboard_top < available_bottom:
                available_bottom = keyboard_top

        available_height = max(300, available_bottom - overlay.top() - 6)
        closed_height = max(390, min(540, int(overlay.height() * 0.50)))
        target_height = min(closed_height, available_height)

        # Width is controlled exclusively by the symmetric shell margins. The
        # fixed sheet height prevents add/hide notes from causing a half-second
        # resize bounce.
        if self.sheet.height() != target_height:
            self.sheet.setFixedHeight(target_height)
            self._composer_height = target_height

        # Allocate the remaining vertical budget to subtasks. Notes and toolbar
        # keep their normal positions directly underneath the subtask viewport.
        base_without_subtasks = 272 + (82 if self.notes.isVisible() else 0)
        allowed_subtasks = max(50, min(170, target_height - base_without_subtasks))
        self._update_subtask_viewport(allowed_subtasks)
        self.composer_layout.activate()

        focus = self.focusWidget()
        if isinstance(focus, QLineEdit) and focus is not self.title:
            QTimer.singleShot(0, lambda widget=focus: self.subtasks_scroll.ensureWidgetVisible(widget, 8, 8))

    def _validate(self) -> None:
        if not self.title.text().strip():
            show_warning(self, t("title_needed"), t("title_needed_message"))
            self.title.setFocus()
            return
        self.accept()

    def task_value(self) -> Task:
        subtasks = [
            value
            for position, row in enumerate(self.subtask_rows)
            if (value := row.value(position)) is not None
        ]
        return Task(
            id=self.original.id if self.original else None,
            title=self.title.text().strip(),
            notes=self.notes.toPlainText().strip(),
            category_id=self.category.currentData() if self.category.currentData() != self.CREATE_CATEGORY else None,
            scheduled_date=self.scheduled_date,
            scheduled_time=self.scheduled_time if self.scheduled_date and not self.all_day else None,
            all_day=self.all_day if self.scheduled_date else True,
            recurrence=self.recurrence_value if self.scheduled_date else "none",
            reminder_minutes=self.reminder_minutes if self.scheduled_date and not self.all_day else None,
            reminder_sent=self.original.reminder_sent if self.original else False,
            starred=self.original.starred if self.original else False,
            generated_from_id=self.original.generated_from_id if self.original else None,
            completed_at=self.original.completed_at if self.original else None,
            created_at=self.original.created_at if self.original else None,
            updated_at=self.original.updated_at if self.original else None,
            subtasks=subtasks,
        )


class DateOnlyPickerDialog(ManagedDialog):
    def __init__(self, selected_date: date | None, parent=None):
        super().__init__(parent, page=True)
        self.setWindowTitle(t("change_date"))
        self.selected_date = selected_date
        anchor = selected_date or date.today()
        self.visible_month = date(anchor.year, anchor.month, 1)

        page = QFrame()
        page.setObjectName("managedDialogPage")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(page)
        root = QVBoxLayout(page)
        root.setContentsMargins(14, 10, 14, 12)
        root.setSpacing(10)

        top = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=42)
        back.clicked.connect(self.reject)
        title = QLabel(t("change_date"))
        title.setObjectName("dialogTitleCompact")
        top.addWidget(back)
        top.addWidget(title)
        top.addStretch()
        root.addLayout(top)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(2, 8, 2, 12)
        body_layout.setSpacing(12)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(body)
        root.addWidget(self.scroll, 1)

        header = QHBoxLayout()
        previous = GlyphButton("left", t("previous_month"), size=38)
        previous.clicked.connect(lambda: self._move_month(-1))
        self.month_title = QLabel()
        self.month_title.setObjectName("scheduleMonthTitle")
        self.month_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        following = GlyphButton("right", t("next_month"), size=38)
        following.clicked.connect(lambda: self._move_month(1))
        header.addWidget(previous)
        header.addWidget(self.month_title, 1)
        header.addWidget(following)
        body_layout.addLayout(header)

        self.calendar_host = QWidget()
        self.calendar_grid = QGridLayout(self.calendar_host)
        self.calendar_grid.setContentsMargins(0, 0, 0, 0)
        self.calendar_grid.setHorizontalSpacing(4)
        self.calendar_grid.setVerticalSpacing(4)
        body_layout.addWidget(self.calendar_host)

        quick = QHBoxLayout()
        quick.setSpacing(7)
        for label, value in (
            (t("today"), date.today()),
            (t("tomorrow"), date.today() + timedelta(days=1)),
            (t("no_date"), None),
        ):
            button = QPushButton(label)
            button.setObjectName("scheduleQuick")
            button.clicked.connect(lambda checked=False, v=value: self._select(v))
            quick.addWidget(button, 1)
        body_layout.addLayout(quick)

        footer = QHBoxLayout()
        footer.addStretch()
        cancel = QPushButton(t("cancel"))
        cancel.setObjectName("secondary")
        cancel.setMinimumHeight(46)
        cancel.clicked.connect(self.reject)
        done = QPushButton(t("done"))
        done.setObjectName("primary")
        done.setMinimumHeight(46)
        done.clicked.connect(self.accept)
        footer.addWidget(cancel)
        footer.addWidget(done)
        root.addLayout(footer)

        self._render()

    def _move_month(self, delta: int) -> None:
        year = self.visible_month.year + (self.visible_month.month - 1 + delta) // 12
        month = (self.visible_month.month - 1 + delta) % 12 + 1
        self.visible_month = date(year, month, 1)
        self._render()

    def _select(self, value: date | None) -> None:
        self.selected_date = value
        if value is not None:
            self.visible_month = date(value.year, value.month, 1)
        self._render()

    def _render(self) -> None:
        clear_layout(self.calendar_grid)
        self.month_title.setText(format_month_year(self.visible_month))
        sunday = date(2024, 1, 7)
        for column in range(7):
            label = QLabel(weekday_name(sunday + timedelta(days=column), short=True))
            label.setObjectName("calendarWeekday")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_grid.addWidget(label, 0, column)
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(
            self.visible_month.year, self.visible_month.month
        )
        for row, week in enumerate(weeks, start=1):
            for column, value in enumerate(week):
                button = QPushButton(localize_digits(value.day))
                button.setObjectName("scheduleDay")
                button.setProperty("outsideMonth", value.month != self.visible_month.month)
                button.setProperty("selected", value == self.selected_date)
                button.setProperty("today", value == date.today())
                button.setFixedHeight(38)
                button.clicked.connect(lambda checked=False, d=value: self._select(d))
                self.calendar_grid.addWidget(button, row, column)

    def value(self) -> date | None:
        return self.selected_date


class TaskEditDialog(ManagedDialog):
    def __init__(
        self,
        categories: list[Category],
        task: Task,
        category_creator: Callable[[str, str], Category | None] | None = None,
        parent=None,
    ):
        super().__init__(parent, page=True)
        self.original = task
        self.categories = list(categories)
        self.category_creator = category_creator
        self.scheduled_date = task.scheduled_date
        self.scheduled_time = task.scheduled_time
        self.all_day = task.all_day
        self.recurrence_value = task.recurrence
        self.reminder_minutes = task.reminder_minutes
        self.subtask_rows: list[SubtaskEditorRow] = []
        self.setModal(True)
        self.setWindowTitle(t("edit_task_details"))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        if compact_dialog(parent):
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        root_widget = QWidget()
        root_widget.setObjectName("taskEditPage")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(root_widget)
        root = QVBoxLayout(root_widget)
        root.setContentsMargins(18, 14, 18, 16)
        root.setSpacing(10)

        header = QHBoxLayout()
        back = GlyphButton("left", t("close"), size=44)
        back.clicked.connect(self.reject)
        heading = QLabel(t("edit_task_details"))
        heading.setObjectName("dialogTitle")
        done = QPushButton(t("save_changes"))
        done.setObjectName("editTaskDone")
        done.clicked.connect(self._save)
        header.addWidget(back)
        header.addWidget(heading)
        header.addStretch()
        header.addWidget(done)
        root.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        content = QWidget()
        content.setObjectName("taskEditContent")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 4, 0, 24)
        self.content_layout.setSpacing(8)
        self.scroll.setWidget(content)
        root.addWidget(self.scroll, 1)

        self.category = SoftSelect()
        self.category.setObjectName("taskEditCategory")
        self.category.addItem(t("no_category"), None)
        for category in self.categories:
            self.category.addItem(category.name, category.id)
        self.category.setPopupMaxVisibleItems(8)
        self.category.setCurrentIndex(max(0, self.category.findData(task.category_id)))
        self.content_layout.addWidget(self.category, 0, Qt.AlignmentFlag.AlignLeft)

        self.title = QLineEdit(task.title)
        self.title.setObjectName("taskEditTitle")
        self.title.setPlaceholderText(t("task_title"))
        self.title.setMinimumHeight(62)
        self.content_layout.addWidget(self.title)

        self.subtasks_host = QWidget()
        self.subtasks_layout = QVBoxLayout(self.subtasks_host)
        self.subtasks_layout.setContentsMargins(0, 0, 0, 0)
        self.subtasks_layout.setSpacing(5)
        for item in task.subtasks:
            self._add_subtask(item.title, item.completed)
        self.content_layout.addWidget(self.subtasks_host)
        add_subtask = QPushButton("+  " + t("add_subtask"))
        add_subtask.setObjectName("taskEditAddSubtask")
        add_subtask.clicked.connect(lambda: self._add_subtask("", False, True))
        self.content_layout.addWidget(add_subtask, 0, Qt.AlignmentFlag.AlignLeft)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        self.content_layout.addWidget(divider)

        self.date_value = QLabel()
        self.date_row = self._make_action_row("calendar", t("due_date"), self.date_value, self._edit_date)
        self.content_layout.addWidget(self.date_row)
        self.time_value = QLabel()
        self.time_row = self._make_action_row("clock", t("time_reminder"), self.time_value, self._edit_time)
        self.content_layout.addWidget(self.time_row)

        repeat_row = QFrame()
        repeat_row.setObjectName("taskEditRow")
        repeat_layout = QHBoxLayout(repeat_row)
        repeat_layout.setContentsMargins(8, 8, 8, 8)
        repeat_layout.setSpacing(12)
        repeat_layout.addWidget(GlyphIcon("repeat", 34))
        repeat_label = QLabel(t("repeat_task"))
        repeat_label.setObjectName("taskEditRowLabel")
        repeat_layout.addWidget(repeat_label, 1)
        self.repeat = SoftSelect()
        self.repeat.setMaximumWidth(180)
        for value in RECURRENCE_KEYS:
            self.repeat.addItem(recurrence_label(value), value)
        self.repeat.setPopupFitToContents(True)
        self.repeat.setCurrentIndex(max(0, self.repeat.findData(task.recurrence)))
        repeat_layout.addWidget(self.repeat)
        self.content_layout.addWidget(repeat_row)

        self.notes_value = QLabel(t("add") if not task.notes else task.notes[:28])
        self.notes_row = self._make_action_row("tasks", t("notes_label"), self.notes_value, self._toggle_notes)
        self.content_layout.addWidget(self.notes_row)
        self.notes = QTextEdit(task.notes)
        self.notes.setObjectName("taskEditNotes")
        self.notes.setPlaceholderText(t("notes_optional"))
        self.notes.setFixedHeight(112)
        self.notes.setVisible(bool(task.notes))
        enable_kinetic_scroll(self.notes, vertical_only=True)
        self.content_layout.addWidget(self.notes)

        attachment_value = QLabel(t("coming_soon"))
        attachment = self._make_action_row("template", t("attachment"), attachment_value, None)
        attachment.setEnabled(False)
        self.content_layout.addWidget(attachment)
        self.content_layout.addStretch()

        self._update_summaries()
        apply_text_input_direction(self)
        if not compact_dialog(parent):
            self.resize(620, 760)

    def _make_action_row(self, glyph: str, label_text: str, value_label: QLabel, callback) -> QPushButton:
        button = QPushButton()
        button.setObjectName("taskEditRow")
        button.setMinimumHeight(68)
        layout = QHBoxLayout(button)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        layout.addWidget(GlyphIcon(glyph, 34))
        label = QLabel(label_text)
        label.setObjectName("taskEditRowLabel")
        layout.addWidget(label, 1)
        value_label.setObjectName("taskEditRowValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(value_label)
        chevron = QLabel("›")
        chevron.setObjectName("taskEditChevron")
        layout.addWidget(chevron)
        for child in button.findChildren(QWidget):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if callback is not None:
            button.clicked.connect(callback)
        return button

    def _add_subtask(self, text: str, completed: bool = False, focus: bool = False) -> None:
        row = SubtaskEditorRow(text, completed)
        row.remove.clicked.connect(lambda: self._remove_subtask(row))
        self.subtasks_layout.addWidget(row)
        self.subtask_rows.append(row)
        if focus:
            row.edit.setFocus()
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(row, 12, 12))

    def _remove_subtask(self, row: SubtaskEditorRow) -> None:
        if row in self.subtask_rows:
            self.subtask_rows.remove(row)
            row.setParent(None)
            row.deleteLater()

    def _edit_date(self) -> None:
        QApplication.inputMethod().hide()
        dialog = DateOnlyPickerDialog(self.scheduled_date, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.scheduled_date = dialog.value()
            if self.scheduled_date is None:
                self.scheduled_time = None
                self.all_day = True
                self.reminder_minutes = None
                self.recurrence_value = "none"
                self.repeat.setCurrentIndex(max(0, self.repeat.findData("none")))
            self._update_summaries()

    def _edit_time(self) -> None:
        QApplication.inputMethod().hide()
        dialog = SchedulePickerDialog(
            self.scheduled_date,
            self.scheduled_time,
            self.all_day,
            self.repeat.currentData() or self.recurrence_value,
            self.reminder_minutes,
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            (
                self.scheduled_date,
                self.scheduled_time,
                self.all_day,
                self.recurrence_value,
                self.reminder_minutes,
            ) = dialog.value()
            self.repeat.setCurrentIndex(max(0, self.repeat.findData(self.recurrence_value)))
            self._update_summaries()

    def _toggle_notes(self) -> None:
        visible = not self.notes.isVisible()
        self.notes.setVisible(visible)
        if visible:
            self.notes.setFocus()
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(self.notes, 12, 12))

    def _update_summaries(self) -> None:
        self.date_value.setText(format_date_medium(self.scheduled_date) if self.scheduled_date else t("no_date"))
        if self.scheduled_date and self.scheduled_time and not self.all_day:
            summary = format_time_12(self.scheduled_time)
            reminder = reminder_label(self.reminder_minutes)
            if self.reminder_minutes is not None:
                summary += " · " + reminder
        else:
            summary = t("no_value")
        self.time_value.setText(summary)

    def _save(self) -> None:
        if not self.title.text().strip():
            show_warning(self, t("title_needed"), t("title_needed_message"))
            self.title.setFocus()
            return
        self.accept()

    def task_value(self) -> Task:
        subtasks = [
            value
            for position, row in enumerate(self.subtask_rows)
            if (value := row.value(position)) is not None
        ]
        return Task(
            id=self.original.id,
            title=self.title.text().strip(),
            notes=self.notes.toPlainText().strip(),
            category_id=self.category.currentData(),
            scheduled_date=self.scheduled_date,
            scheduled_time=self.scheduled_time if self.scheduled_date and not self.all_day else None,
            all_day=self.all_day if self.scheduled_date else True,
            recurrence=(self.repeat.currentData() or "none") if self.scheduled_date else "none",
            reminder_minutes=self.reminder_minutes if self.scheduled_date and not self.all_day else None,
            reminder_sent=self.original.reminder_sent,
            starred=self.original.starred,
            generated_from_id=self.original.generated_from_id,
            completed_at=self.original.completed_at,
            created_at=self.original.created_at,
            updated_at=self.original.updated_at,
            subtasks=subtasks,
        )


class CategoryDialog(ManagedDialog):
    FALLBACK_COLORS = ["#D88C6A", "#72AF95", "#8C86B8", "#D0A75E", "#6E9FB3", "#C77D91"]

    def __init__(self, parent=None):
        # Category creation is a small form, not a full-height navigation page.
        super().__init__(parent, page=False)
        compact = compact_dialog(parent)
        self._managed_preferred_width = 400
        self._managed_minimum_width = 304
        self._managed_minimum_height = 206
        self.setWindowTitle(t("new_category"))
        self.setModal(True)
        self.setMinimumWidth(0 if compact else 440)
        app = QApplication.instance()
        palette_name = app.property("themePaletteName") if app else None
        dark_mode = bool(app.property("themeDark")) if app else False
        self.colors = category_swatches(normalize_palette_name(palette_name), dark_mode)
        if len(self.colors) != 6:
            self.colors = list(self.FALLBACK_COLORS)
        self.color = self.colors[1]

        root_widget = QWidget()
        root_widget.setObjectName("dialogRoot")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(root_widget)
        layout = QVBoxLayout(root_widget)
        layout.setContentsMargins(*(18, 17, 18, 16) if compact else (28, 24, 28, 24))
        layout.setSpacing(13 if compact else 17)
        title = QLabel(t("create_category"))
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        self.name = QLineEdit()
        self.name.setPlaceholderText(t("category_name"))
        self.name.setMinimumHeight(44)
        layout.addWidget(self.name)

        color_row = QHBoxLayout()
        color_row.setSpacing(9)
        self.swatches: list[QPushButton] = []
        for color in self.colors:
            swatch = QPushButton()
            swatch.setFixedSize(31, 31)
            swatch.setCursor(Qt.CursorShape.PointingHandCursor)
            swatch.setProperty("swatchColor", color)
            swatch.clicked.connect(lambda checked=False, c=color: self._set_color(c))
            color_row.addWidget(swatch)
            self.swatches.append(swatch)
        custom = GlyphButton("plus", t("choose_color"), size=31)
        custom.clicked.connect(self._choose_color)
        color_row.addWidget(custom)
        color_row.addStretch()
        layout.addLayout(color_row)
        layout.addSpacing(2 if compact else 0)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        if not compact:
            actions.addStretch()
        cancel = QPushButton(t("cancel"))
        cancel.setObjectName("secondary")
        if compact:
            cancel.setMinimumHeight(46)
            cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            cancel.setFixedSize(110, 42)
        cancel.clicked.connect(self.reject)
        create = QPushButton(t("create"))
        create.setObjectName("primary")
        if compact:
            create.setMinimumHeight(46)
            create.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            create.setFixedSize(110, 42)
        create.clicked.connect(self._validate)
        actions.addWidget(cancel, 1 if compact else 0)
        actions.addWidget(create, 1 if compact else 0)
        layout.addLayout(actions)
        self._set_color(self.color)
        apply_text_input_direction(self)
        self.name.setFocus()

    def _set_color(self, color: str) -> None:
        self.color = color
        colors = theme_colors()
        for swatch in self.swatches:
            swatch_color = swatch.property("swatchColor")
            selected = swatch_color.lower() == color.lower()
            border = colors["text"] if selected else "transparent"
            width = 3 if selected else 1
            swatch.setStyleSheet(
                f"background:{swatch_color}; border-radius:15px; border:{width}px solid {border}; padding:0;"
            )

    def _choose_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.color), self, t("choose_category_color"))
        if color.isValid():
            self.color = color.name()
            self._set_color(self.color)

    def _validate(self) -> None:
        if not self.name.text().strip():
            show_warning(self, t("name_needed"), t("name_needed_message"))
            return
        self.accept()


class SettingsCategoryRow(QFrame):
    """Compact category row used only inside Settings."""

    def __init__(self, category: Category, delete_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsCategoryRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(10)

        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background:{category.color}; border-radius:5px;")
        layout.addWidget(dot)

        name = QLabel(category.name)
        name.setObjectName("settingsCategoryName")
        layout.addWidget(name, 1)

        remove = GlyphButton("trash", t("delete_category"), danger=True, size=38)
        remove.clicked.connect(lambda: delete_callback(category.id))
        layout.addWidget(remove)


class SettingsDialog(ManagedDialog):
    """Single home for language, appearance, and category management."""

    def __init__(
        self,
        *,
        dark: bool,
        palette_name: str,
        language_changer,
        theme_toggler,
        palette_changer,
        categories_provider,
        category_creator,
        category_deleter,
        parent=None,
    ):
        compact = compact_dialog(parent)
        super().__init__(parent, page=compact)
        self._dark = bool(dark)
        self._palette_name = normalize_palette_name(palette_name)
        self._language_changer = language_changer
        self._theme_toggler = theme_toggler
        self._palette_changer = palette_changer
        self._categories_provider = categories_provider
        self._category_creator = category_creator
        self._category_deleter = category_deleter
        self._managed_preferred_width = 560
        self._managed_minimum_width = 330
        self._managed_minimum_height = 420
        self.setWindowTitle(t("settings"))

        root_widget = QWidget()
        root_widget.setObjectName("settingsPage")
        shell = QVBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.addWidget(root_widget)
        root = QVBoxLayout(root_widget)
        root.setContentsMargins(*(16, 14, 16, 14) if compact else (24, 22, 24, 22))
        root.setSpacing(14)

        header = QHBoxLayout()
        self.back_button = GlyphButton("left", t("close_settings"), size=42)
        self.back_button.clicked.connect(self.reject)
        header.addWidget(self.back_button)
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        self.title_label = QLabel(t("settings"))
        self.title_label.setObjectName("dialogTitleCompact")
        self.subtitle_label = QLabel(t("settings_subtitle"))
        self.subtitle_label.setObjectName("pageSubtitle")
        self.subtitle_label.setWordWrap(True)
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box, 1)
        root.addLayout(header)

        self.scroll = VerticalOnlyScrollArea()
        self.scroll.setObjectName("settingsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        body = QWidget()
        body.setObjectName("settingsBody")
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(0, 2, 0, 8)
        self.body_layout.setSpacing(12)
        self.scroll.setWidget(body)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        root.addWidget(self.scroll, 1)

        self.language_section = self._section(t("language"))
        language_layout = self.language_section.layout()
        self.language_select = SoftSelect()
        self.language_select.setPopupFitToContents(True)
        for label, code in language_items():
            self.language_select.addItem(label, code)
        self.language_select.setCurrentIndex(max(0, self.language_select.findData(language())))
        self.language_select.currentIndexChanged.connect(self._language_changed)
        language_layout.addWidget(self.language_select)
        self.body_layout.addWidget(self.language_section)

        self.appearance_section = self._section(t("appearance"))
        appearance_layout = self.appearance_section.layout()
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("settingsAction")
        self.theme_button.setMinimumHeight(48)
        self.theme_button.clicked.connect(self._toggle_theme)
        appearance_layout.addWidget(self.theme_button)

        self.palette_label = QLabel(t("color_palette"))
        self.palette_label.setObjectName("paletteLabel")
        appearance_layout.addWidget(self.palette_label)
        self.palette_select = SoftSelect()
        self.palette_select.setPopupFitToContents(True)
        for key in PALETTE_KEYS:
            self.palette_select.addItem(t(f"palette_{key}"), key)
        self.palette_select.setCurrentIndex(
            max(0, self.palette_select.findData(self._palette_name))
        )
        self.palette_select.currentIndexChanged.connect(self._palette_changed)
        appearance_layout.addWidget(self.palette_select)
        self.palette_preview = QLabel(t("palette_preview_hint"))
        self.palette_preview.setObjectName("palettePreview")
        self.palette_preview.setWordWrap(True)
        appearance_layout.addWidget(self.palette_preview)
        self.body_layout.addWidget(self.appearance_section)

        categories = QFrame()
        categories.setObjectName("settingsSection")
        categories_layout = QVBoxLayout(categories)
        categories_layout.setContentsMargins(14, 13, 14, 14)
        categories_layout.setSpacing(10)
        category_header = QHBoxLayout()
        self.categories_title = QLabel(t("categories").title())
        self.categories_title.setObjectName("settingsSectionTitle")
        category_header.addWidget(self.categories_title)
        category_header.addStretch()
        self.add_category_button = GlyphButton("plus", t("add_category"), size=40, accent=True)
        self.add_category_button.clicked.connect(self._add_category)
        category_header.addWidget(self.add_category_button)
        categories_layout.addLayout(category_header)
        self.categories_hint = QLabel(t("categories_settings_hint"))
        self.categories_hint.setObjectName("settingsHint")
        self.categories_hint.setWordWrap(True)
        categories_layout.addWidget(self.categories_hint)
        self.category_host = QWidget()
        self.category_layout = QVBoxLayout(self.category_host)
        self.category_layout.setContentsMargins(0, 2, 0, 0)
        self.category_layout.setSpacing(7)
        categories_layout.addWidget(self.category_host)
        self.body_layout.addWidget(categories)
        self.body_layout.addStretch()

        self._sync_theme_button()
        self._rebuild_categories()

    def _section(self, title: str) -> QFrame:
        section = QFrame()
        section.setObjectName("settingsSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(14, 13, 14, 14)
        layout.setSpacing(9)
        label = QLabel(title)
        label.setObjectName("settingsSectionTitle")
        section._settings_title_label = label
        layout.addWidget(label)
        return section

    def _language_changed(self, index: int) -> None:
        if index < 0:
            return
        code = self.language_select.currentData()
        if isinstance(code, str) and code != language():
            self._language_changer(code)
            self._retranslate()

    def _toggle_theme(self) -> None:
        self._theme_toggler()
        self._dark = not self._dark
        self._sync_theme_button()

    def _palette_changed(self, index: int) -> None:
        if index < 0:
            return
        name = normalize_palette_name(self.palette_select.currentData())
        if name == self._palette_name:
            return
        self._palette_name = name
        self._palette_changer(name)

    def _sync_theme_button(self) -> None:
        self.theme_button.setText(t("light_appearance") if self._dark else t("dark_appearance"))

    def _add_category(self) -> None:
        dialog = CategoryDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        category = self._category_creator(dialog.name.text(), dialog.color, self)
        if category is not None:
            self._rebuild_categories()

    def _delete_category(self, category_id: int) -> None:
        category = next((item for item in self._categories_provider() if item.id == category_id), None)
        if category is None:
            return
        if not confirm_action(
            self,
            t("delete_category_title"),
            t("delete_category_message", name=category.name),
            t("delete"),
        ):
            return
        if self._category_deleter(category_id, self):
            self._rebuild_categories()

    def _rebuild_categories(self) -> None:
        clear_layout(self.category_layout)
        categories = list(self._categories_provider())
        if not categories:
            empty = QLabel(t("no_categories"))
            empty.setObjectName("settingsHint")
            self.category_layout.addWidget(empty)
        else:
            for category in categories:
                self.category_layout.addWidget(
                    SettingsCategoryRow(category, self._delete_category, self.category_host)
                )
        self.category_layout.addStretch()

    def _retranslate(self) -> None:
        self.setWindowTitle(t("settings"))
        self.title_label.setText(t("settings"))
        self.subtitle_label.setText(t("settings_subtitle"))
        self.language_section._settings_title_label.setText(t("language"))
        self.appearance_section._settings_title_label.setText(t("appearance"))
        self.palette_label.setText(t("color_palette"))
        self.palette_preview.setText(t("palette_preview_hint"))
        self.palette_select.blockSignals(True)
        self.palette_select.clear()
        for key in PALETTE_KEYS:
            self.palette_select.addItem(t(f"palette_{key}"), key)
        self.palette_select.setCurrentIndex(
            max(0, self.palette_select.findData(self._palette_name))
        )
        self.palette_select.blockSignals(False)
        self.categories_title.setText(t("categories").title())
        self.categories_hint.setText(t("categories_settings_hint"))
        self.add_category_button.setToolTip(t("add_category"))
        self.back_button.setToolTip(t("close_settings"))
        self.language_select.blockSignals(True)
        self.language_select.clear()
        for label, code in language_items():
            self.language_select.addItem(label, code)
        self.language_select.setCurrentIndex(max(0, self.language_select.findData(language())))
        self.language_select.blockSignals(False)
        self._sync_theme_button()
        self._rebuild_categories()
