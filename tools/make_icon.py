from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


def render(svg: Path, output: Path, size: int) -> None:
    renderer = QSvgRenderer(QByteArray(svg.read_bytes()))
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    if not image.save(str(output), "PNG"):
        raise RuntimeError(f"Could not create {output}")


def main() -> int:
    QGuiApplication(sys.argv)
    root = Path(__file__).resolve().parents[1]
    svg = root / "assets" / "daymark.svg"
    iconset = root / "assets" / "daymark.iconset"
    output = root / "assets" / "daymark.icns"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    variants = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    for size, name in variants:
        render(svg, iconset / name, size)
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(output)], check=True)
    shutil.rmtree(iconset)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
