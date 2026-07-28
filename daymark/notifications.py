from __future__ import annotations

import platform
import subprocess


class Notifier:
    """Small native-notification adapter with a macOS-first implementation."""

    @staticmethod
    def send(title: str, message: str) -> bool:
        if platform.system() != "Darwin":
            return False
        safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
        safe_message = message.replace("\\", "\\\\").replace('"', '\\"')
        script = f'display notification "{safe_message}" with title "{safe_title}" sound name "Glass"'
        try:
            subprocess.Popen(
                ["osascript", "-e", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except OSError:
            return False

