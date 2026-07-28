from pathlib import Path


def _source(name: str) -> str:
    return (Path(__file__).parents[1] / name).read_text(encoding="utf-8")


def test_no_nested_process_events_in_dialogs():
    assert "QApplication.processEvents()" not in _source("daymark/dialogs.py")


def test_refresh_and_geometry_are_coalesced():
    window = _source("daymark/window.py")
    dialogs = _source("daymark/dialogs.py")
    assert "self._refresh_timer" in window
    assert "def _perform_refresh_everything" in window
    assert "self._layout_sync_timer" in window
    assert "self._geometry_sync_timer" in dialogs


def test_android_stack_avoids_full_page_snapshot():
    widgets = _source("daymark/widgets.py")
    direct_branch = widgets.index("if running_on_android():", widgets.index("def animate_to"))
    snapshot = widgets.index("outgoing_snapshot = current.grab()", widgets.index("def animate_to"))
    assert direct_branch < snapshot


def test_schedule_refits_are_width_guarded():
    dialogs = _source("daymark/dialogs.py")
    assert "self._last_schedule_fit_width == viewport_width" in dialogs
    assert "QTimer.singleShot(90, self._fit_schedule_to_viewport)" not in dialogs
    assert "QTimer.singleShot(120, self._fit_schedule_to_viewport)" not in dialogs


def test_swipe_uses_position_animation():
    widgets = _source("daymark/widgets.py")
    assert 'QPropertyAnimation(self.surface, b"pos"' in widgets
    assert 'QPropertyAnimation(self.surface, b"geometry"' not in widgets


def test_child_dialog_guards_are_exception_safe():
    dialogs = _source("daymark/dialogs.py")
    schedule = dialogs[dialogs.index("def _exec_schedule_dialog"):dialogs.index("def _open_templates")]
    templates = dialogs[dialogs.index("def _exec_templates_dialog"):dialogs.index("def _update_schedule_summary")]
    assert "finally:" in schedule
    assert "finally:" in templates


def test_android_toast_avoids_graphics_effect_path():
    window = _source("daymark/window.py")
    toast = window[window.index("class FeedbackToast"):window.index("class CategoryRow")]
    android_branch = toast.index("if running_on_android():")
    effect = toast.index("effect = QGraphicsOpacityEffect", android_branch)
    else_branch = toast.index("else:", android_branch)
    assert android_branch < else_branch < effect


def test_mobile_text_scrollers_are_vertical_only():
    dialogs = _source("daymark/dialogs.py")
    widgets = _source("daymark/widgets.py")
    assert "enable_kinetic_scroll(self.notes)" not in dialogs
    assert "enable_kinetic_scroll(self.list, mouse_fallback=True, vertical_only=True)" in widgets


def test_composer_has_no_delayed_geometry_nudge():
    dialogs = _source("daymark/dialogs.py")
    assert "QTimer.singleShot(120, self._schedule_keyboard_geometry_sync)" not in dialogs
