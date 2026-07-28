"""Small binding bridge: PySide6 on Android, with PyQt6 fallback for existing installs."""

from __future__ import annotations

try:
    from PySide6 import QtCore, QtGui, QtWidgets

    BINDING = "PySide6"
except ImportError:  # Keeps existing desktop PyQt6 environments working.
    from PyQt6 import QtCore, QtGui, QtWidgets

    BINDING = "PyQt6"


pyqtSignal = getattr(QtCore, "Signal", None) or QtCore.pyqtSignal


def __getattr__(name: str):
    if name == "pyqtSignal":
        return pyqtSignal
    for module in (QtCore, QtGui, QtWidgets):
        if hasattr(module, name):
            return getattr(module, name)
    raise AttributeError(name)
