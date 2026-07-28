"""Platform and breakpoint helpers kept free of Qt for easy testing."""

from __future__ import annotations

import os
import sys


MOBILE_BREAKPOINT = 760


def running_on_android() -> bool:
    return sys.platform.startswith("android") or bool(os.environ.get("ANDROID_ARGUMENT"))


def use_compact_layout(width: int, force_android: bool | None = None) -> bool:
    android = running_on_android() if force_android is None else force_android
    return android or width < MOBILE_BREAKPOINT
