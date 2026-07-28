from __future__ import annotations

import sys
import traceback
from datetime import datetime
from time import monotonic
from pathlib import Path

from daymark.qt import (
    QApplication, QAbstractSpinBox, QComboBox, QDialog, QEvent, QFont, QIcon,
    QLineEdit, QObject, QPlainTextEdit, QStandardPaths, QTextEdit, Qt,
)

from daymark.device import running_on_android
from daymark.window import MainWindow




class AndroidBackFilter(QObject):
    """Keep Android Back separate from IME/text-editing key events.

    Some Android keyboards briefly emit Back/Escape-like Qt events while an
    editor starts or resumes input. Treating those as Activity Back events can
    trigger python-for-android's "press again to exit" message. While a text
    editor or the input method is active, these events are consumed locally.
    A genuine Android Back key (native key code 4) first dismisses the keyboard;
    only a later Back press is allowed to navigate or exit.
    """

    _TEXT_INPUT_TYPES = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox)
    _ANDROID_BACK_KEYCODE = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_back_press = 0.0
        self._back_press_active = False

    @staticmethod
    def _native_key(event) -> int:
        try:
            return int(event.nativeVirtualKey())
        except (AttributeError, TypeError, ValueError):
            return 0

    @classmethod
    def _text_input_active(cls) -> bool:
        widget = QApplication.focusWidget()
        while widget is not None:
            if isinstance(widget, cls._TEXT_INPUT_TYPES):
                return True
            if isinstance(widget, QComboBox) and widget.isEditable():
                return True
            try:
                widget = widget.parentWidget()
            except AttributeError:
                break
        try:
            return bool(QApplication.inputMethod().isVisible())
        except Exception:
            return False

    def eventFilter(self, watched, event) -> bool:
        if not running_on_android():
            return super().eventFilter(watched, event)

        event_type = event.type()
        if event_type not in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            return super().eventFilter(watched, event)

        native_key = self._native_key(event)
        qt_key = event.key()
        is_back_candidate = (
            native_key == self._ANDROID_BACK_KEYCODE
            or qt_key in (Qt.Key.Key_Back, Qt.Key.Key_Escape)
        )
        if not is_back_candidate:
            return super().eventFilter(watched, event)

        # Consume the matching release as well. Letting it escape to the Android
        # Activity can still trigger the platform's double-back exit handler.
        if event_type == QEvent.Type.KeyRelease:
            self._back_press_active = False
            event.accept()
            return True

        # Back/Escape-like events generated while typing are never application
        # navigation. A genuine Android Back press dismisses the keyboard only.
        if self._text_input_active():
            if native_key == self._ANDROID_BACK_KEYCODE:
                try:
                    QApplication.inputMethod().hide()
                except Exception:
                    pass
            self._last_back_press = 0.0
            self._back_press_active = True
            event.accept()
            return True

        now = monotonic()
        if (
            self._back_press_active
            or (hasattr(event, "isAutoRepeat") and event.isAutoRepeat())
            or now - self._last_back_press < 0.22
        ):
            event.accept()
            return True

        self._back_press_active = True
        self._last_back_press = now
        modal = QApplication.activeModalWidget()
        if isinstance(modal, QDialog):
            modal.reject()
            event.accept()
            return True

        window = QApplication.activeWindow()
        if isinstance(window, MainWindow):
            window.handle_back()
            event.accept()
            return True

        # Never pass an Android Back candidate to PythonActivity. This is the
        # final guard against the platform "press again to exit" toast.
        event.accept()
        return True


class TooltipBlocker(QObject):
    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.ToolTip:
            return True
        return super().eventFilter(watched, event)


def _install_exception_log() -> None:
    previous_hook = sys.excepthook

    def log_exception(exc_type, exc_value, exc_traceback) -> None:
        try:
            directory = Path(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            )
            directory.mkdir(parents=True, exist_ok=True)
            report = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            with (directory / "daymark-crash.log").open("a", encoding="utf-8") as handle:
                handle.write(f"\n[{datetime.now().isoformat(timespec='seconds')}]\n{report}\n")
        except Exception:
            pass
        previous_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = log_exception


def main() -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
    for attribute_name in ("AA_CompressHighFrequencyEvents", "AA_CompressTabletEvents"):
        attribute = getattr(Qt.ApplicationAttribute, attribute_name, None)
        if attribute is not None:
            QApplication.setAttribute(attribute, True)
    app = QApplication(sys.argv)
    _install_exception_log()
    app.setStyle("Fusion")
    app.setApplicationName("Daymark")
    app.setApplicationDisplayName("Daymark")
    app.setOrganizationName("Daymark")
    app.setOrganizationDomain("daymark.local")
    icon_path = Path(__file__).resolve().with_name("icon.png")
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.tooltip_blocker = TooltipBlocker(app)
    app.android_back_filter = AndroidBackFilter(app)
    app.installEventFilter(app.tooltip_blocker)
    app.installEventFilter(app.android_back_filter)
    app.setFont(QFont("Roboto" if running_on_android() else "SF Pro Text", 13))
    window = MainWindow()
    if running_on_android():
        window.showMaximized()
    else:
        window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
