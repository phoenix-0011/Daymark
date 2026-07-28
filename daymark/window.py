from __future__ import annotations

import sqlite3
import traceback
from datetime import date, datetime
from pathlib import Path

from .qt import (
    QApplication,
    QCloseEvent,
    QDialog,
    QEasingCurve,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QKeySequence,
    QLabel,
    QMainWindow,
    QParallelAnimationGroup,
    QPauseAnimation,
    QPropertyAnimation,
    QPushButton,
    QPoint,
    QRect,
    QScrollArea,
    QSequentialAnimationGroup,
    QSettings,
    QShortcut,
    QStandardPaths,
    QTimer,
    Qt,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

from .database import Database
from .device import running_on_android, use_compact_layout
from .dialogs import CategoryDialog, DateOnlyPickerDialog, SettingsDialog, TaskDetailsDialog, TaskDialog, TaskEditDialog, confirm_action, show_warning
from .formatting import format_date_medium, format_time_12
from .insights import InsightsView
from .i18n import (
    apply_text_input_direction,
    install_text_input_direction_support,
    is_rtl,
    language,
    language_items,
    localize_digits,
    set_language,
    t,
    task_count,
)
from .models import Category
from .notifications import Notifier
from .theme import DEFAULT_PALETTE, colors_for, normalize_palette_name, palette, stylesheet
from .views import AllTasksView, HistoryView, PlannerView
from .widgets import (
    ActionPopover,
    AnimatedStack,
    BrandMark,
    GlyphButton,
    MobileNavButton,
    NavButton,
    SlidingHighlight,
    SoftSelect,
    TaskCard,
    clear_layout,
    enable_kinetic_scroll,
)


class FeedbackToast(QFrame):
    def __init__(self, text: str, parent: QWidget, finished, parent_window=None):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedSize(150, 52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        label = QLabel(text)
        label.setObjectName("toastText")
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        desired_width = max(150, min(parent.width() - 24, label.sizeHint().width() + 40))
        self.setFixedSize(desired_width, 52)

        target_x = max(0, (parent.width() - self.width()) // 2)
        target_y = max(0, (parent.height() - self.height()) // 2)
        end_rect = QRect(target_x, target_y, self.width(), self.height())
        self.setGeometry(end_rect)

        self.timeline = QSequentialAnimationGroup(self)
        if running_on_android():
            # QGraphicsOpacityEffect on a top-level mobile surface repaints a
            # large region every frame. A stable timed toast is materially
            # smoother and cannot interfere with touch or scrolling.
            self.timeline.addAnimation(QPauseAnimation(1450, self))
        else:
            start_rect = end_rect.translated(0, 10)
            exit_rect = end_rect.translated(0, -7)
            self.setGeometry(start_rect)
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.0)
            self.setGraphicsEffect(effect)

            fade_in = QPropertyAnimation(effect, b"opacity", self)
            fade_in.setDuration(220)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            rise_in = QPropertyAnimation(self, b"geometry", self)
            rise_in.setDuration(220)
            rise_in.setStartValue(start_rect)
            rise_in.setEndValue(end_rect)
            rise_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            entrance = QParallelAnimationGroup(self)
            entrance.addAnimation(fade_in)
            entrance.addAnimation(rise_in)
            self.timeline.addAnimation(entrance)
            self.timeline.addAnimation(QPauseAnimation(1330, self))

            fade_out = QPropertyAnimation(effect, b"opacity", self)
            fade_out.setDuration(450)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
            rise_out = QPropertyAnimation(self, b"geometry", self)
            rise_out.setDuration(450)
            rise_out.setStartValue(end_rect)
            rise_out.setEndValue(exit_rect)
            rise_out.setEasingCurve(QEasingCurve.Type.InCubic)
            exit_group = QParallelAnimationGroup(self)
            exit_group.addAnimation(fade_out)
            exit_group.addAnimation(rise_out)
            self.timeline.addAnimation(exit_group)

        self.timeline.finished.connect(finished)
        self.timeline.finished.connect(self.deleteLater)
        self.show()
        self.raise_()
        self.timeline.start()


class CategoryRow(QWidget):
    selected = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self, category_id: int, name: str, color: str, count: int, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(11, 0, 9, 0)
        layout.setSpacing(8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background:{color}; border-radius:4px;")
        layout.addWidget(dot)
        button = QPushButton(name)
        button.setObjectName("categoryButton")
        button.setProperty("rtl", is_rtl())
        button.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if is_rtl() else Qt.LayoutDirection.LeftToRight
        )
        button.clicked.connect(lambda: self.selected.emit(category_id))
        layout.addWidget(button, 1)
        number = QLabel(localize_digits(count))
        number.setObjectName("taskMeta")
        layout.addWidget(number)

    def _menu(self, position) -> None:
        self._popover = ActionPopover(
            t("delete_category"),
            lambda: self.delete_requested.emit(self.category_id),
            danger=True,
            parent=self,
        )
        self._popover.show_at(self.mapToGlobal(position))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daymark")
        self.resize(1320, 820)
        self.setMinimumSize(320 if running_on_android() else 360, 480 if running_on_android() else 600)
        self._compact: bool | None = None
        self.settings = QSettings("Daymark", "Daymark")
        saved_language = self.settings.value("language", "en", type=str)
        self.language_code = set_language(saved_language)
        if saved_language != self.language_code:
            self.settings.setValue("language", self.language_code)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.dark = self.settings.value("darkMode", False, type=bool)
        saved_palette = self.settings.value("colorPalette", DEFAULT_PALETTE, type=str)
        self.palette_name = normalize_palette_name(saved_palette)
        if saved_palette != self.palette_name:
            self.settings.setValue("colorPalette", self.palette_name)
        self.current_page = "all"
        self._pending_page_request: tuple[str, int | None, str | None] | None = None
        self._action_in_progress = False
        self._toast = None
        self._refresh_include_categories = True
        self._category_refresh_signature: tuple = ()
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(16)
        self._refresh_timer.timeout.connect(self._perform_refresh_everything)
        self._layout_sync_timer = QTimer(self)
        self._layout_sync_timer.setSingleShot(True)
        self._layout_sync_timer.setInterval(0)
        self._layout_sync_timer.timeout.connect(self._sync_responsive_geometry)
        data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.db = Database(Path(data_dir) / "daymark.sqlite3")

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        self.outer = QHBoxLayout(root)
        self.outer.setContentsMargins(0, 0, 0, 0)
        self.outer.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setProperty("rtl", is_rtl())
        self.sidebar.setFixedWidth(228)
        self._build_sidebar()
        self.outer.addWidget(self.sidebar)

        self.content = QWidget()
        self.content.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(34, 28, 34, 26)
        self.content_layout.setSpacing(20)
        self._build_header(self.content_layout)

        self.stack = AnimatedStack(style="fade")
        self.all_tasks = AllTasksView(self.db)
        self.planner = PlannerView(self.db)
        self.history = HistoryView(self.db)
        self.insights = InsightsView(self.db)
        self.stack.addWidget(self.all_tasks)
        self.stack.addWidget(self.planner)
        self.stack.addWidget(self.history)
        self.stack.addWidget(self.insights)
        self.stack.transition_finished.connect(self._main_transition_finished)
        self.content_layout.addWidget(self.stack, 1)

        self.mobile_nav = QFrame()
        self.mobile_nav.setObjectName("mobileNav")
        mobile_nav_layout = QHBoxLayout(self.mobile_nav)
        mobile_nav_layout.setContentsMargins(5, 4, 5, 4)
        mobile_nav_layout.setSpacing(3)
        self.mobile_nav_buttons = {
            "all": MobileNavButton(t("tasks"), "tasks"),
            "planner": MobileNavButton(t("planner"), "planner"),
            "history": MobileNavButton(t("history"), "clock"),
            "mine": MobileNavButton(t("mine"), "person"),
        }
        for button in self.mobile_nav_buttons.values():
            mobile_nav_layout.addWidget(button, 1)
        self.mobile_nav_indicator = SlidingHighlight(self.mobile_nav, "mobileNavIndicator")
        self.content_layout.addWidget(self.mobile_nav)

        # The primary action lives above the Mine navigation coordinate instead
        # of competing with the persistent header controls. It is deliberately
        # parented to content rather than a layout so its position can track the
        # actual Mine button after every responsive relayout.
        self.add_fab = GlyphButton("plus", t("new_task"), size=56, parent=self.content, accent=True)
        self.add_fab.setObjectName("addTaskFab")
        self.add_fab.clicked.connect(lambda: self.add_task(None))
        self.add_fab.show()

        self.outer.addWidget(self.content, 1)

        for view in (self.all_tasks, self.planner, self.history):
            view.add_requested.connect(self.add_task)
            view.edit_requested.connect(self.edit_task)
            view.details_requested.connect(self.show_task_details)
            view.complete_requested.connect(self.complete_task)
            view.restore_requested.connect(self.restore_task)
            view.delete_requested.connect(self.delete_task)
            view.star_requested.connect(self.set_task_starred)
            view.date_requested.connect(self.edit_task_date)

        self.all_tasks.category_changed.connect(
            lambda category_id, name: self.show_page(
                "all", category_id, None if category_id is None else name
            )
        )

        self.nav_buttons["all"].clicked.connect(lambda: self.show_page("all"))
        self.nav_buttons["planner"].clicked.connect(lambda: self.show_page("planner"))
        self.nav_buttons["history"].clicked.connect(lambda: self.show_page("history"))
        self.nav_buttons["mine"].clicked.connect(lambda: self.show_page("mine"))
        self.mobile_nav_buttons["all"].clicked.connect(lambda: self.show_page("all"))
        self.mobile_nav_buttons["planner"].clicked.connect(lambda: self.show_page("planner"))
        self.mobile_nav_buttons["history"].clicked.connect(lambda: self.show_page("history"))
        self.mobile_nav_buttons["mine"].clicked.connect(lambda: self.show_page("mine"))
        self.settings_button.clicked.connect(self.open_settings)

        QShortcut(QKeySequence("Ctrl+N"), self, activated=lambda: self.add_task(None))
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self._focus_search)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.show_page("all"))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.show_page("planner"))
        QShortcut(QKeySequence("Ctrl+3"), self, activated=lambda: self.show_page("history"))
        QShortcut(QKeySequence("Ctrl+4"), self, activated=lambda: self.show_page("mine"))

        self.reminder_timer = QTimer(self)
        self.reminder_timer.setInterval(30_000)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start()
        QTimer.singleShot(1500, self.check_reminders)

        self.apply_theme()
        self._apply_responsive_layout(force=True)
        self.show_page("all")
        self.refresh_everything()
        install_text_input_direction_support()
        apply_text_input_direction(self)

    def _build_sidebar(self) -> None:
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(17, 24, 17, 18)
        layout.setSpacing(5)

        brand_row = QHBoxLayout()
        mark = BrandMark()
        brand = QLabel("Daymark")
        brand.setObjectName("brand")
        brand_row.addWidget(mark)
        brand_row.addWidget(brand)
        brand_row.addStretch()
        layout.addLayout(brand_row)
        layout.addSpacing(21)

        self.nav_buttons: dict[str, NavButton] = {
            "all": NavButton("○   " + t("all_tasks")),
            "planner": NavButton("⌑   " + t("planner")),
            "history": NavButton(t("history"), glyph="clock"),
            "mine": NavButton(t("mine"), glyph="person"),
        }
        for button in self.nav_buttons.values():
            button.set_rtl(is_rtl())
            layout.addWidget(button)
        self.sidebar_indicator = SlidingHighlight(self.sidebar, "sidebarNavIndicator")
        layout.addStretch()

    def _build_header(self, layout: QVBoxLayout) -> None:
        # The header is permanent app chrome: the brand stays on the left and a
        # single Settings entry stays on the right. Page actions never compete
        # with language/theme controls here.
        self.header_widget = QWidget(self.content)
        self.header_widget.setObjectName("persistentHeader")
        header = QHBoxLayout(self.header_widget)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.page_title = QLabel("Daymark")
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel()
        self.page_subtitle.setObjectName("pageSubtitle")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        header.addLayout(titles)
        header.addStretch()
        self.settings_button = GlyphButton("gear", t("settings"), size=44)
        self.settings_button.setObjectName("mobileIconButton")
        header.addWidget(self.settings_button, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.header_widget)

    def overlay_geometry(self) -> QRect:
        """Global geometry available to modal pages below the persistent header."""
        if not hasattr(self, "header_widget") or not self.header_widget.isVisible():
            return QRect()
        content_origin = self.content.mapToGlobal(QPoint(0, 0))
        top = self.header_widget.mapToGlobal(QPoint(0, self.header_widget.height())).y() + 4
        bottom = content_origin.y() + self.content.height()
        return QRect(
            content_origin.x(),
            top,
            max(1, self.content.width()),
            max(240, bottom - top),
        )

    def show_page(self, page: str, category_id: int | None = None, category_name: str | None = None) -> None:
        pages = {"all": 0, "planner": 1, "history": 2, "mine": 3}
        if page not in pages:
            return
        target_index = pages[page]
        previous_index = self.stack.currentIndex()
        TaskCard.close_open_card(immediate=True)

        # Navigation taps are never discarded. While one short transition is
        # finishing, keep only the latest destination, matching common mobile
        # tab-bar behavior. The highlight/title respond immediately.
        if target_index != previous_index and self.stack.is_animating:
            self._pending_page_request = (page, category_id, category_name)
            self._apply_page_chrome(
                page, category_id, category_name, animate_indicator=True, refresh_view=False
            )
            return

        self._pending_page_request = None
        self._apply_page_chrome(
            page, category_id, category_name, animate_indicator=previous_index != target_index
        )
        if target_index != previous_index:
            if not self.stack.animate_to(target_index, 1 if target_index > previous_index else -1):
                self.stack.setCurrentIndex(target_index)
        self._queue_layout_sync()

    def _apply_page_chrome(
        self,
        page: str,
        category_id: int | None,
        category_name: str | None,
        *,
        animate_indicator: bool,
        refresh_view: bool = True,
    ) -> None:
        self.current_page = page
        for key, button in self.nav_buttons.items():
            button.set_active(key == page and category_id is None)
        for key, button in self.mobile_nav_buttons.items():
            button.set_active(key == page)
        desktop_target = self.nav_buttons.get(page) if category_id is None else None
        QTimer.singleShot(
            0, lambda: self.sidebar_indicator.move_to(desktop_target, animate_indicator)
        )
        QTimer.singleShot(
            0,
            lambda: self.mobile_nav_indicator.move_to(
                self.mobile_nav_buttons.get(page), animate_indicator
            ),
        )

        # The persistent header is the application brand, not the current page.
        # Keep it stable across navigation, category filtering, language refreshes,
        # and animated transitions.
        self.page_title.setText("Daymark")

        if page == "all":
            self.all_tasks.set_category(category_id, refresh=refresh_view)
            self.page_subtitle.setText(t("everything_calm"))
        elif page == "planner":
            self.page_subtitle.setText(t("planner_subtitle"))
            if refresh_view:
                self.planner.refresh()
        elif page == "history":
            self.page_subtitle.setText(t("history_subtitle"))
            if refresh_view:
                self.history.refresh()
        else:
            self.page_subtitle.setText(t("insights_subtitle"))
            if refresh_view:
                self.insights.refresh()

        self._queue_layout_sync()

    def _main_transition_finished(self, _index: int) -> None:
        pending = self._pending_page_request
        self._pending_page_request = None
        if pending is not None:
            QTimer.singleShot(0, lambda request=pending: self.show_page(*request))

    def open_settings(self) -> None:
        dialog = SettingsDialog(
            dark=self.dark,
            palette_name=self.palette_name,
            language_changer=self.change_language,
            theme_toggler=self.toggle_theme,
            palette_changer=self.change_palette,
            categories_provider=self.db.categories,
            category_creator=self._create_category_from_composer,
            category_deleter=self._delete_category_from_settings,
            parent=self,
        )
        dialog.exec()
        self.refresh_categories()
        self._queue_layout_sync()

    def _position_add_fab(self) -> None:
        if not hasattr(self, "add_fab") or not self.add_fab.isVisible():
            return
        if self._compact and self.mobile_nav.isVisible():
            mine = self.mobile_nav_buttons["mine"]
            mine_center_global = mine.mapToGlobal(mine.rect().center())
            mine_center = self.content.mapFromGlobal(mine_center_global)
            nav_top_global = self.mobile_nav.mapToGlobal(QPoint(0, 0))
            nav_top = self.content.mapFromGlobal(nav_top_global).y()
            x = mine_center.x() - self.add_fab.width() // 2
            x = max(8, min(x, self.content.width() - self.add_fab.width() - 8))

            # Keep the floating action visually balanced against the lower-right
            # corner: the gap above the navigation bar is exactly the same as
            # the actual gap between the FAB and the right edge of the mobile
            # content. This replaces the old fixed 9 px gap, which left the
            # button too low on common Android phone widths.
            right_gap = self.content.width() - (x + self.add_fab.width())
            y = nav_top - self.add_fab.height() - right_gap
        else:
            x = self.content.width() - self.add_fab.width() - 26
            y = self.content.height() - self.add_fab.height() - 26
        x = max(8, min(x, self.content.width() - self.add_fab.width() - 8))
        y = max(self.header_widget.height() + 8, min(y, self.content.height() - self.add_fab.height() - 8))
        self.add_fab.move(x, y)
        self.add_fab.raise_()

    def add_task(self, initial_date=None) -> None:
        dialog = TaskDialog(
            self.db.categories(),
            initial_date=initial_date,
            category_creator=self._create_category_from_composer,
            parent=self,
        )
        if dialog.exec():
            ok, _ = self._try_data_change(lambda: self.db.save_task(dialog.task_value()))
            if ok:
                self._show_feedback(t("done"))
                # The sender may be a Month-agenda card that is still unwinding
                # its signal stack. Rebuild on the next event turn to avoid
                # deleting that hierarchy re-entrantly on Android.
                self.refresh_everything()

    def edit_task(self, task_id: int) -> None:
        task = self.db.task(task_id)
        if not task:
            return
        dialog = TaskEditDialog(
            self.db.categories(),
            task,
            category_creator=self._create_category_from_composer,
            parent=self,
        )
        if dialog.exec():
            ok, _ = self._try_data_change(lambda: self.db.save_task(dialog.task_value()))
            if ok:
                self._show_feedback(t("task_updated"))
                self.refresh_everything()

    def edit_task_date(self, task_id: int) -> None:
        task = self.db.task(task_id)
        if not task:
            return
        dialog = DateOnlyPickerDialog(task.scheduled_date, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ok, _ = self._try_data_change(lambda: self.db.set_task_date(task_id, dialog.value()))
            if ok:
                self._show_feedback(t("date_updated"))
                self.refresh_everything()

    def set_task_starred(self, task_id: int, starred: bool) -> None:
        ok, _ = self._try_data_change(lambda: self.db.set_task_starred(task_id, starred))
        if ok:
            self._show_feedback(t("starred") if starred else t("unstarred"))
            self.refresh_everything()

    def _create_category_from_composer(self, name: str, color: str, warning_parent=None) -> Category | None:
        try:
            category_id = self.db.add_category(name, color)
        except sqlite3.IntegrityError:
            show_warning(warning_parent or self, t("category_exists"), t("category_exists_message"))
            return None
        except (sqlite3.Error, ValueError):
            traceback.print_exc()
            if warning_parent is not None:
                show_warning(warning_parent, t("operation_failed"), t("operation_failed_message"))
            else:
                self._show_operation_error()
            return None
        category = Category(category_id, name.strip(), color)
        self.refresh_categories()
        return category

    def show_task_details(self, task_id: int) -> None:
        task = self.db.task(task_id)
        if task:
            TaskDetailsDialog(task, self).exec()

    def complete_task(self, task_id: int, card: TaskCard) -> None:
        if self._action_in_progress:
            card.check.setChecked(False)
            card.check.setEnabled(True)
            return
        self._feedback_then_remove(t("done"), card, lambda: self.db.complete_task(task_id))

    def restore_task(self, task_id: int) -> None:
        ok, _ = self._try_data_change(lambda: self.db.restore_task(task_id))
        if ok:
            self.refresh_everything()

    def delete_task(self, task_id: int, card: TaskCard) -> None:
        if self._action_in_progress:
            return
        task = self.db.task(task_id)
        if not task:
            return
        if self._confirm_delete(t("delete_task_title"), t("delete_task_message", title=task.title)):
            self._feedback_then_remove(t("deleted"), card, lambda: self.db.delete_task(task_id))

    def _feedback_then_remove(self, message: str, card: TaskCard, operation) -> None:
        self._action_in_progress = True
        try:
            operation()
        except Exception:
            traceback.print_exc()
            self._action_in_progress = False
            if hasattr(card, "check"):
                card.check.setChecked(False)
                card.check.setEnabled(True)
            self._show_operation_error()
            return

        self._show_feedback(message)

        def finish() -> None:
            self._action_in_progress = False
            self.refresh_everything()

        try:
            card.animate_out(finish)
        except RuntimeError:
            finish()

    def _try_data_change(self, operation):
        """Keep database failures at the UI boundary instead of terminating Android."""
        try:
            return True, operation()
        except Exception:
            traceback.print_exc()
            self._show_operation_error()
            return False, None

    def _show_operation_error(self) -> None:
        show_warning(self, t("operation_failed"), t("operation_failed_message"))

    def _show_feedback(self, message: str) -> None:
        if self._toast is not None:
            try:
                self._toast.timeline.stop()
                self._toast.deleteLater()
            except RuntimeError:
                pass
        toast = None

        def finished() -> None:
            if self._toast is toast:
                self._toast = None

        toast = FeedbackToast(message, self.centralWidget(), finished)
        self._toast = toast

    def add_category(self) -> None:
        dialog = CategoryDialog(self)
        if not dialog.exec():
            return
        try:
            self.db.add_category(dialog.name.text(), dialog.color)
        except sqlite3.IntegrityError:
            show_warning(self, t("category_exists"), t("category_exists_message"))
            return
        except (sqlite3.Error, ValueError):
            traceback.print_exc()
            self._show_operation_error()
            return
        self.refresh_everything()

    def _delete_category_from_settings(self, category_id: int, warning_parent=None) -> bool:
        category = next((item for item in self.db.categories() if item.id == category_id), None)
        if category is None:
            return False
        try:
            self.db.delete_category(category_id)
        except Exception:
            traceback.print_exc()
            show_warning(warning_parent or self, t("operation_failed"), t("operation_failed_message"))
            return False
        if self.current_page == "all" and self.all_tasks.category_id == category_id:
            self.show_page("all")
        self.refresh_everything()
        return True

    def delete_category(self, category_id: int) -> bool:
        category = next((item for item in self.db.categories() if item.id == category_id), None)
        if not category:
            return False
        if not self._confirm_delete(
            t("delete_category_title"),
            t("delete_category_message", name=category.name),
        ):
            return False
        ok, _ = self._try_data_change(lambda: self.db.delete_category(category_id))
        if not ok:
            return False
        if self.current_page == "all" and self.all_tasks.category_id == category_id:
            self.show_page("all")
        self.refresh_everything()
        return True

    def _confirm_delete(self, title: str, message: str) -> bool:
        return confirm_action(self, title, message, t("delete"))

    def refresh_categories(self) -> None:
        categories = self.db.categories()
        signature = tuple((item.id, item.name, item.color, item.position) for item in categories)
        available_ids = {item.id for item in categories}
        if self.all_tasks.category_id is not None and self.all_tasks.category_id not in available_ids:
            self.all_tasks.set_category(None, refresh=False)
        if signature != self._category_refresh_signature:
            self._category_refresh_signature = signature
            self.all_tasks.set_categories(categories)
        else:
            self.all_tasks._update_chip_selection()

    def refresh_everything(self, *, include_categories: bool = True) -> None:
        """Coalesce UI refresh requests into one frame-aligned rebuild."""
        self._refresh_include_categories = self._refresh_include_categories or include_categories
        self._refresh_timer.start()

    def _perform_refresh_everything(self) -> None:
        TaskCard.close_open_card(immediate=True)
        current = self.stack.currentIndex()
        active_view = (self.all_tasks, self.planner, self.history, self.insights)[current]
        active_view.setUpdatesEnabled(False)
        try:
            active_view.refresh()
        finally:
            active_view.setUpdatesEnabled(True)
            active_view.update()

        if self._refresh_include_categories:
            self.refresh_categories()
        self._refresh_include_categories = False
        today = format_date_medium(datetime.now().date())
        if current == 0 and self.all_tasks.category_id is None:
            active_count = getattr(self.all_tasks, "_last_rendered_count", None)
            if active_count is None:
                active_count = len(self.db.tasks())
            self.page_subtitle.setText(f"{today}  ·  {task_count(active_count, active=True)}")
        self.centralWidget().update()

    def change_language(self, code: str) -> None:
        if not isinstance(code, str) or code == language():
            return
        self._pending_page_request = None
        self.stack.cancel_transition()
        self.planner.cancel_animations()
        self.language_code = set_language(code)
        self.settings.setValue("language", self.language_code)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._retranslate_ui()
        self.apply_theme()
        self._apply_responsive_layout(force=True)
        apply_text_input_direction(self)
        self._queue_layout_sync()

    def _retranslate_ui(self) -> None:
        self.nav_buttons["all"].set_label("○   " + t("all_tasks"))
        self.nav_buttons["planner"].set_label("⌑   " + t("planner"))
        self.nav_buttons["history"].set_label(t("history"))
        self.nav_buttons["mine"].set_label(t("mine"))
        for button in self.nav_buttons.values():
            button.set_rtl(is_rtl())
        self.mobile_nav_buttons["all"].setText(t("tasks"))
        self.mobile_nav_buttons["planner"].setText(t("planner"))
        self.mobile_nav_buttons["history"].setText(t("history"))
        self.mobile_nav_buttons["mine"].setText(t("mine"))
        self.sidebar.setProperty("rtl", is_rtl())
        self.sidebar.style().unpolish(self.sidebar)
        self.sidebar.style().polish(self.sidebar)
        self.settings_button.setToolTip(t("settings"))
        self.add_fab.setToolTip(t("new_task"))
        self.all_tasks.retranslate()
        self.planner.retranslate()
        self.history.retranslate()
        self.insights.retranslate()
        self.refresh_categories()
        category_id = self.all_tasks.category_id if self.current_page == "all" else None
        category = next((item for item in self.db.categories() if item.id == category_id), None)
        self.show_page(self.current_page, category_id, category.name if category else None)

    def _snap_navigation_indicators(self) -> None:
        mobile_target = self.mobile_nav_buttons.get(self.current_page)
        desktop_target = self.nav_buttons.get(self.current_page)
        if self.current_page == "all" and self.all_tasks.category_id is not None:
            desktop_target = None
        self.mobile_nav_indicator.move_to(mobile_target, False)
        self.sidebar_indicator.move_to(desktop_target, False)

    def toggle_theme(self) -> None:
        self.dark = not self.dark
        self.settings.setValue("darkMode", self.dark)
        self.apply_theme()

    def change_palette(self, palette_name: str) -> None:
        normalized = normalize_palette_name(palette_name)
        if normalized == self.palette_name:
            return
        self.palette_name = normalized
        self.settings.setValue("colorPalette", self.palette_name)
        self.apply_theme()

    def apply_theme(self) -> None:
        app = QApplication.instance()
        if app:
            colors = colors_for(self.palette_name, self.dark)
            app.setProperty("themeColors", colors)
            app.setProperty("themePaletteName", self.palette_name)
            app.setProperty("themeDark", self.dark)
            app.setPalette(palette(self.dark, self.palette_name))
            app.setStyleSheet(stylesheet(self.dark, self.palette_name))
            # Custom-painted charts, glyphs, heatmaps, navigation highlights,
            # and task controls read themeColors directly. A palette switch is
            # rare, so explicitly repaint every live widget once to guarantee
            # a coherent same-frame transition across every section.
            for widget in app.allWidgets():
                widget.update()
        self.centralWidget().update()

    def _apply_responsive_layout(self, force: bool = False) -> None:
        compact = use_compact_layout(self.width())
        if not force and compact == self._compact:
            self._queue_layout_sync()
            return
        self._pending_page_request = None
        self.stack.cancel_transition()
        self.planner.cancel_animations()
        self._compact = compact
        self.sidebar.setVisible(not compact)
        self.mobile_nav.setVisible(compact)
        self.page_subtitle.setVisible(not compact)
        self.content_layout.setContentsMargins(*(10, 10, 10, 7) if compact else (34, 28, 34, 26))
        self.content_layout.setSpacing(10 if compact else 20)
        self.page_title.setProperty("compact", compact)
        self.page_title.style().unpolish(self.page_title)
        self.page_title.style().polish(self.page_title)
        fab_size = 56 if compact else 58
        self.add_fab.setFixedSize(fab_size, fab_size)
        self.add_fab.setVisible(True)
        self.all_tasks.set_compact(compact)
        self.planner.set_compact(compact)
        self.history.set_compact(compact)
        self.insights.set_compact(compact)
        self._queue_layout_sync()

    def _queue_layout_sync(self) -> None:
        if hasattr(self, "_layout_sync_timer"):
            self._layout_sync_timer.start()

    def _sync_responsive_geometry(self) -> None:
        if not hasattr(self, "mobile_nav"):
            return
        self._snap_navigation_indicators()
        self._position_add_fab()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "mobile_nav"):
            self._apply_responsive_layout()
            self._queue_layout_sync()

    def check_reminders(self) -> None:
        now = datetime.now()
        try:
            reminders = self.db.pending_reminders(now)
        except sqlite3.Error:
            traceback.print_exc()
            return
        for task in reminders:
            when = format_time_12(task.scheduled_time, t("soon"))
            delivered = Notifier.send(task.title, t("scheduled_for", time=when))
            if running_on_android():
                self._show_feedback(t("reminder_prefix", title=task.title))
                delivered = True
            if delivered:
                try:
                    self.db.mark_reminder_sent(task.id or 0)
                except sqlite3.Error:
                    traceback.print_exc()

    def _focus_search(self) -> None:
        if self.stack.currentIndex() == 2:
            self.history.search.setFocus()
        else:
            self.show_page("all")
            self.all_tasks.search.setFocus()

    def handle_back(self) -> None:
        """Single Android-back policy used by both the window and app filter."""
        TaskCard.close_open_card(immediate=True)
        if self.current_page != "all":
            self.show_page("all")
        else:
            self.close()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Back, Qt.Key.Key_Escape):
            # Consume Android Back ourselves. This avoids the platform's
            # double-back-to-exit toast and gives predictable in-app behavior.
            self.handle_back()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.reminder_timer.stop()
        self._refresh_timer.stop()
        self._layout_sync_timer.stop()
        self._pending_page_request = None
        self.stack.cancel_transition()
        self.planner.cancel_animations()
        TaskCard.close_open_card(immediate=True)
        self.db.close()
        super().closeEvent(event)
