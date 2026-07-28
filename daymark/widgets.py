from __future__ import annotations

from collections.abc import Callable
from time import monotonic

from .qt import (
    QAbstractButton,
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QColor,
    QEasingCurve,
    QEvent,
    QFont,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QGuiApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPoint,
    QPointF,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QPushButton,
    QRectF,
    QSize,
    QScrollArea,
    QStackedLayout,
    QStackedWidget,
    QScroller,
    QScrollerProperties,
    QSizePolicy,
    QTimer,
    QVariantAnimation,
    Qt,
    QVBoxLayout,
    QWidget,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    pyqtSignal,
)

from .models import Task
from .device import running_on_android
from .i18n import is_rtl, localize_digits, t
from .recurrence import recurrence_label


def theme_colors() -> dict[str, str]:
    app = QApplication.instance()
    colors = app.property("themeColors") if app else None
    return colors or {
        "window": "#F8F3ED",
        "surface": "#FFFCF8",
        "surface_alt": "#F5EEE7",
        "text": "#2E2B27",
        "muted": "#817A71",
        "faint": "#AAA196",
        "border": "#E5DED3",
        "surface_hover": "#F0E9DE",
        "accent": "#72AF95",
        "accent_pressed": "#558E76",
        "accent_soft": "#E0EFE8",
        "on_accent": "#183229",
        "danger": "#C56C62",
        "danger_soft": "#F8E5E1",
        "on_danger": "#FFFFFF",
    }


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            # Remove stale geometry immediately; deleteLater alone can leave old
            # week/calendar widgets visible during rapid refreshes.
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout():
            clear_layout(item.layout())


def enable_kinetic_scroll(
    area,
    *,
    mouse_fallback: bool = False,
    vertical_only: bool = False,
) -> None:
    """Enable light Android kinetic scrolling.

    ``vertical_only`` is used by phone pages whose complete surface must never
    pan sideways. It disables horizontal overshoot at the QScroller level and
    strongly locks diagonal drags to the vertical axis.
    """
    if not running_on_android():
        return
    viewport = area.viewport() if hasattr(area, "viewport") else area
    viewport.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
    viewport.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation, False)
    scroller = QScroller.scroller(viewport)
    properties = scroller.scrollerProperties()
    metric = QScrollerProperties.ScrollMetric
    properties.setScrollMetric(metric.MousePressEventDelay, 0.0)
    # A slightly larger drag threshold prevents accidental scroll starts while
    # tapping cards, while stronger velocity smoothing removes the "heavy"
    # start/stop feeling on Android touch screens.
    properties.setScrollMetric(metric.DragStartDistance, 0.0022)
    properties.setScrollMetric(metric.DragVelocitySmoothingFactor, 0.82)
    properties.setScrollMetric(metric.DecelerationFactor, 0.082)
    properties.setScrollMetric(metric.OvershootDragResistanceFactor, 0.72)
    properties.setScrollMetric(metric.OvershootScrollDistanceFactor, 0.07)
    properties.setScrollMetric(metric.AxisLockThreshold, 0.95 if vertical_only else 0.87)
    try:
        properties.setScrollMetric(
            metric.FrameRate, QScrollerProperties.FrameRates.Fps60
        )
    except (AttributeError, TypeError):
        # Older Qt builds do not expose the frame-rate metric. The remaining
        # metrics are still valid and should not prevent scrolling.
        pass
    if vertical_only:
        overshoot = QScrollerProperties.OvershootPolicy
        properties.setScrollMetric(
            metric.HorizontalOvershootPolicy, overshoot.OvershootAlwaysOff
        )
        properties.setScrollMetric(
            metric.VerticalOvershootPolicy, overshoot.OvershootWhenScrollable
        )
    properties.setScrollMetric(metric.ScrollingCurve, QEasingCurve(QEasingCurve.Type.OutQuart))
    properties.setScrollMetric(metric.MaximumClickThroughVelocity, 0.0)
    scroller.setScrollerProperties(properties)
    QScroller.ungrabGesture(viewport)
    QScroller.grabGesture(viewport, QScroller.ScrollerGestureType.TouchGesture)
    if mouse_fallback:
        QScroller.grabGesture(viewport, QScroller.ScrollerGestureType.LeftMouseButtonGesture)


def draw_glyph(painter: QPainter, name: str, rect: QRectF, color: QColor) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    cx, cy = rect.center().x(), rect.center().y()

    if name == "pencil":
        painter.drawLine(QPointF(cx - 5, cy + 4), QPointF(cx + 4, cy - 5))
        painter.drawLine(QPointF(cx - 3, cy + 6), QPointF(cx + 6, cy - 3))
        painter.drawLine(QPointF(cx - 5, cy + 4), QPointF(cx - 6, cy + 7))
        painter.drawLine(QPointF(cx - 6, cy + 7), QPointF(cx - 3, cy + 6))
        painter.drawLine(QPointF(cx + 4, cy - 5), QPointF(cx + 6, cy - 3))
    elif name == "trash":
        painter.drawRoundedRect(QRectF(cx - 4.5, cy - 3, 9, 10), 1.5, 1.5)
        painter.drawLine(QPointF(cx - 6, cy - 5), QPointF(cx + 6, cy - 5))
        painter.drawLine(QPointF(cx - 2.5, cy - 7), QPointF(cx + 2.5, cy - 7))
        painter.drawLine(QPointF(cx - 1.7, cy - 1), QPointF(cx - 1.7, cy + 4.5))
        painter.drawLine(QPointF(cx + 1.7, cy - 1), QPointF(cx + 1.7, cy + 4.5))
    elif name in {"up", "down", "left", "right"}:
        if name == "up":
            points = (QPointF(cx - 4, cy + 2), QPointF(cx, cy - 2), QPointF(cx + 4, cy + 2))
        elif name == "down":
            points = (QPointF(cx - 4, cy - 2), QPointF(cx, cy + 2), QPointF(cx + 4, cy - 2))
        elif name == "left":
            points = (QPointF(cx + 2, cy - 4), QPointF(cx - 2, cy), QPointF(cx + 2, cy + 4))
        else:
            points = (QPointF(cx - 2, cy - 4), QPointF(cx + 2, cy), QPointF(cx - 2, cy + 4))
        painter.drawPolyline(QPolygonF(points))
    elif name == "plus":
        painter.drawLine(QPointF(cx - 5, cy), QPointF(cx + 5, cy))
        painter.drawLine(QPointF(cx, cy - 5), QPointF(cx, cy + 5))
    elif name == "restore":
        tip = QPointF(cx - 5.2, cy - 3.0)
        path = QPainterPath(QPointF(cx + 4.8, cy + 4.2))
        path.cubicTo(cx + 7.2, cy - 1.8, cx + 1.5, cy - 7.0, tip.x(), tip.y())
        painter.drawPath(path)
        painter.drawLine(tip, QPointF(tip.x() + 4.5, tip.y() - 1.2))
        painter.drawLine(tip, QPointF(tip.x() + 1.0, tip.y() + 4.4))
    elif name == "repeat":
        top_left = QPointF(cx - 5.8, cy - 3.0)
        top_right = QPointF(cx + 5.0, cy - 3.0)
        bottom_right = QPointF(cx + 5.8, cy + 3.0)
        bottom_left = QPointF(cx - 5.0, cy + 3.0)
        painter.drawLine(top_left, top_right)
        painter.drawLine(top_right, QPointF(cx + 2.6, cy - 5.4))
        painter.drawLine(top_right, QPointF(cx + 2.6, cy - 0.6))
        painter.drawLine(bottom_right, bottom_left)
        painter.drawLine(bottom_left, QPointF(cx - 2.6, cy + 5.4))
        painter.drawLine(bottom_left, QPointF(cx - 2.6, cy + 0.6))
    elif name == "clock":
        face = QRectF(cx - 5.7, cy - 5.7, 11.4, 11.4)
        painter.drawEllipse(face)
        painter.drawLine(QPointF(cx, cy), QPointF(cx, cy - 3.2))
        painter.drawLine(QPointF(cx, cy), QPointF(cx + 2.7, cy + 1.6))
    elif name == "tasks":
        for offset in (-4.2, 0.0, 4.2):
            painter.drawPoint(QPointF(cx - 5.2, cy + offset))
            painter.drawLine(QPointF(cx - 1.9, cy + offset), QPointF(cx + 5.4, cy + offset))
    elif name == "planner":
        painter.drawRoundedRect(QRectF(cx - 5.8, cy - 5.2, 11.6, 11.0), 2.0, 2.0)
        painter.drawLine(QPointF(cx - 5.4, cy - 1.8), QPointF(cx + 5.4, cy - 1.8))
        painter.drawLine(QPointF(cx - 2.7, cy - 7.0), QPointF(cx - 2.7, cy - 4.0))
        painter.drawLine(QPointF(cx + 2.7, cy - 7.0), QPointF(cx + 2.7, cy - 4.0))
    elif name == "star":
        outer = 6.4
        inner = 2.8
        points = []
        import math
        for index in range(10):
            radius = outer if index % 2 == 0 else inner
            angle = -math.pi / 2 + index * math.pi / 5
            points.append(QPointF(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        polygon = QPolygonF(points)
        painter.drawPolygon(polygon)
    elif name == "calendar":
        painter.drawRoundedRect(QRectF(cx - 5.8, cy - 5.2, 11.6, 11.0), 2.0, 2.0)
        painter.drawLine(QPointF(cx - 5.4, cy - 1.8), QPointF(cx + 5.4, cy - 1.8))
        painter.drawLine(QPointF(cx - 2.7, cy - 7.0), QPointF(cx - 2.7, cy - 4.0))
        painter.drawLine(QPointF(cx + 2.7, cy - 7.0), QPointF(cx + 2.7, cy - 4.0))
        painter.drawPoint(QPointF(cx - 2.4, cy + 1.2))
        painter.drawPoint(QPointF(cx + 1.2, cy + 1.2))
        painter.drawPoint(QPointF(cx - 2.4, cy + 4.0))
    elif name == "subtask":
        painter.drawEllipse(QRectF(cx - 6.0, cy - 4.8, 3.4, 3.4))
        painter.drawLine(QPointF(cx - 0.8, cy - 3.1), QPointF(cx + 5.8, cy - 3.1))
        painter.drawEllipse(QRectF(cx - 6.0, cy + 1.4, 3.4, 3.4))
        painter.drawLine(QPointF(cx - 0.8, cy + 3.1), QPointF(cx + 5.8, cy + 3.1))
        painter.drawLine(QPointF(cx + 3.0, cy - 0.8), QPointF(cx + 3.0, cy + 0.8))
        painter.drawLine(QPointF(cx + 2.2, cy), QPointF(cx + 3.8, cy))
    elif name == "template":
        painter.drawRoundedRect(QRectF(cx - 6.0, cy - 6.0, 8.2, 8.2), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(cx - 1.8, cy - 1.8, 8.2, 8.2), 1.5, 1.5)
        painter.drawLine(QPointF(cx + 0.4, cy + 1.1), QPointF(cx + 4.2, cy + 1.1))
        painter.drawLine(QPointF(cx + 0.4, cy + 3.7), QPointF(cx + 4.2, cy + 3.7))
    elif name == "send":
        path = QPainterPath()
        path.moveTo(cx - 6.2, cy + 5.4)
        path.lineTo(cx + 6.0, cy)
        path.lineTo(cx - 6.2, cy - 5.4)
        path.lineTo(cx - 2.8, cy)
        path.closeSubpath()
        painter.drawPath(path)
    elif name == "sun":
        painter.drawEllipse(QRectF(cx - 3.5, cy - 3.5, 7, 7))
        for dx, dy in ((0, -7), (0, 7), (-7, 0), (7, 0), (-5, -5), (5, 5), (5, -5), (-5, 5)):
            length = 1.8
            scale = max(abs(dx), abs(dy)) or 1
            ux, uy = dx / scale, dy / scale
            painter.drawLine(QPointF(cx + dx - ux * length, cy + dy - uy * length), QPointF(cx + dx, cy + dy))
    elif name == "moon":
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        moon = QPainterPath()
        moon.addEllipse(QRectF(cx - 4.7, cy - 5.2, 9.4, 10.4))
        cut = QPainterPath()
        cut.addEllipse(QRectF(cx - 1.1, cy - 5.2, 8.6, 10.4))
        moon = moon.subtracted(cut)
        painter.drawPath(moon)
    elif name == "gear":
        import math
        painter.drawEllipse(QRectF(cx - 4.5, cy - 4.5, 9.0, 9.0))
        painter.drawEllipse(QRectF(cx - 1.6, cy - 1.6, 3.2, 3.2))
        for index in range(8):
            angle = index * math.pi / 4.0
            ux, uy = math.cos(angle), math.sin(angle)
            painter.drawLine(
                QPointF(cx + ux * 5.6, cy + uy * 5.6),
                QPointF(cx + ux * 7.0, cy + uy * 7.0),
            )
    elif name in {"return", "unarchive"}:
        painter.drawLine(QPointF(cx - 5.8, cy + 3.8), QPointF(cx + 5.8, cy + 3.8))
        painter.drawLine(QPointF(cx - 5.8, cy + 3.8), QPointF(cx - 5.8, cy + 6.2))
        painter.drawLine(QPointF(cx + 5.8, cy + 3.8), QPointF(cx + 5.8, cy + 6.2))
        path = QPainterPath(QPointF(cx + 5.2, cy + 0.8))
        path.cubicTo(cx + 3.4, cy - 4.8, cx - 2.0, cy - 5.0, cx - 4.4, cy - 1.2)
        painter.drawPath(path)
        painter.drawLine(QPointF(cx - 4.4, cy - 1.2), QPointF(cx - 4.2, cy - 5.1))
        painter.drawLine(QPointF(cx - 4.4, cy - 1.2), QPointF(cx - 0.7, cy - 1.8))
    elif name == "check":
        painter.drawLine(QPointF(cx - 5.3, cy + 0.1), QPointF(cx - 1.2, cy + 4.0))
        painter.drawLine(QPointF(cx - 1.2, cy + 4.0), QPointF(cx + 6.0, cy - 4.4))
    elif name == "person":
        painter.drawEllipse(QRectF(cx - 3.2, cy - 6.0, 6.4, 6.4))
        body = QPainterPath()
        body.moveTo(cx - 6.0, cy + 6.2)
        body.cubicTo(cx - 5.5, cy + 0.5, cx + 5.5, cy + 0.5, cx + 6.0, cy + 6.2)
        painter.drawPath(body)
    elif name == "circle":
        painter.drawEllipse(QRectF(cx - 5.2, cy - 5.2, 10.4, 10.4))
    painter.restore()


class SlidingHighlight(QFrame):
    """Single-owner selection indicator with interruption-safe motion.

    A new target starts from the indicator's current on-screen geometry. The
    previous animation is disposed immediately, so highlights never leave
    competing geometry animations alive.
    """

    def __init__(self, parent: QWidget, object_name: str):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._animation: QPropertyAnimation | None = None
        self._target: QWidget | None = None
        self.hide()
        self.lower()

    def _stop_animation(self) -> None:
        animation = self._animation
        self._animation = None
        if animation is not None:
            animation.stop()
            animation.deleteLater()

    def move_to(self, target: QWidget | None, animate: bool = True) -> None:
        self._target = target
        if target is None or not target.isVisible():
            self._stop_animation()
            self.hide()
            return

        end = target.geometry()
        if end.width() <= 0 or end.height() <= 0:
            QTimer.singleShot(0, lambda target=target, animate=animate: self.move_to(target, animate))
            return

        if self.geometry() == end and self.isVisible():
            self._stop_animation()
            self.lower()
            return

        start = self.geometry()
        self._stop_animation()
        if not self.isVisible() or not animate:
            self.setGeometry(end)
            self.show()
            self.lower()
            return

        self.show()
        self.lower()
        animation = QPropertyAnimation(self, b"geometry", self)
        animation.setDuration(165)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda animation=animation: self._animation_finished(animation))
        self._animation = animation
        animation.start()

    def _animation_finished(self, animation: QPropertyAnimation) -> None:
        if self._animation is animation:
            self._animation = None
        animation.deleteLater()
        if self._target is not None and self._target.isVisible():
            self.setGeometry(self._target.geometry())
        self.lower()

    def snap(self) -> None:
        self.move_to(self._target, False)


class _StackTransitionOverlay(QWidget):
    """Paint-only page transition.

    The live pages are never moved, reparented, faded, or assigned graphics
    effects. A screenshot of the outgoing page moves and fades above the
    already-laid-out destination page. This is substantially more stable for
    nested Qt layouts and Android scroll views than animating page widgets.
    """

    def __init__(self, parent: QWidget, style: str = "fade"):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self._style = style if style in {"fade", "slide"} else "fade"
        self._outgoing = None
        self._direction = 1
        self._progress = 0.0
        self._animation: QVariantAnimation | None = None
        self._finished_callback = None
        self.hide()

    def prepare(self, outgoing, direction: int) -> None:
        self.stop()
        self._outgoing = outgoing
        self._direction = 1 if direction >= 0 else -1
        self._progress = 0.0
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()
        self.update()

    def start(self, finished) -> None:
        self._finished_callback = finished
        animation = QVariantAnimation(self)
        animation.setDuration(145 if self._style == "fade" else 178)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.valueChanged.connect(self._set_progress)
        animation.finished.connect(self._complete)
        self._animation = animation
        animation.start()

    def _set_progress(self, value) -> None:
        self._progress = float(value)
        self.update()

    def stop(self) -> None:
        animation = self._animation
        self._animation = None
        if animation is not None:
            animation.stop()
            animation.deleteLater()
        self._finished_callback = None
        self._outgoing = None
        self.hide()

    def _complete(self) -> None:
        animation = self._animation
        self._animation = None
        if animation is not None:
            animation.deleteLater()
        callback = self._finished_callback
        self._finished_callback = None
        self.hide()
        self._outgoing = None
        if callback is not None:
            callback()

    def paintEvent(self, event) -> None:
        if self._outgoing is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # The live destination page is already visible underneath. Painting only
        # the outgoing snapshot halves the capture/paint cost on Android.
        distance = 0 if self._style == "fade" else max(6, min(12, self.width() // 48))
        offset = int(-self._direction * distance * self._progress)
        painter.setOpacity(max(0.0, 1.0 - self._progress))
        painter.drawPixmap(offset, 0, self._outgoing)


class AnimatedStack(QStackedWidget):
    """Serialized, screenshot-based stack transitions.

    Only one transition may exist at a time. Callers may coalesce additional
    taps to the newest destination, so page snapshots never overlap or compete.
    """

    transition_started = pyqtSignal(int)
    transition_finished = pyqtSignal(int)

    def __init__(self, parent=None, style: str = "fade"):
        super().__init__(parent)
        self._animating = False
        self._target_index: int | None = None
        self._transition_token = 0
        self._overlay = _StackTransitionOverlay(self, style=style)

    @property
    def is_animating(self) -> bool:
        return self._animating

    def animate_to(self, index: int, direction: int | None = None) -> bool:
        if not 0 <= index < self.count():
            return False
        current_index = self.currentIndex()
        if index == current_index:
            return False
        if self._animating:
            return False

        current = self.currentWidget()
        incoming = self.widget(index)
        if current is None or incoming is None or not self.isVisible() or self.width() < 2:
            self.setCurrentIndex(index)
            self.transition_finished.emit(index)
            return True

        logical_direction = direction if direction is not None else (1 if index > current_index else -1)
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            logical_direction *= -1

        self._animating = True
        self._target_index = index
        self._transition_token += 1
        token = self._transition_token

        # Capturing and blending a full page pixmap is one of the largest frame
        # spikes in a Qt Widgets Android app, especially when the page contains
        # nested scroll areas. On Android, switch the live page immediately and
        # complete on the next event-loop turn. The navigation indicator still
        # supplies restrained motion without blocking touch input or allocating
        # a screen-sized pixmap.
        if running_on_android():
            self.setCurrentIndex(index)
            incoming.updateGeometry()
            incoming.update()
            self.transition_started.emit(index)
            QTimer.singleShot(0, lambda: self._finish_transition(token, index))
            return True

        outgoing_snapshot = current.grab()
        if outgoing_snapshot.isNull():
            self.setCurrentIndex(index)
            self.transition_finished.emit(index)
            return True
        self._overlay.prepare(outgoing_snapshot, logical_direction)

        # Switch the real stack immediately. The outgoing snapshot covers it
        # until the destination has completed one layout/paint turn.
        self.setCurrentIndex(index)
        incoming.updateGeometry()
        incoming.update()
        self.transition_started.emit(index)
        QTimer.singleShot(0, lambda: self._begin_overlay_animation(token, index))
        return True

    def _begin_overlay_animation(self, token: int, index: int) -> None:
        if token != self._transition_token or not self._animating:
            return
        incoming = self.currentWidget()
        if incoming is None or self.currentIndex() != index:
            self.cancel_transition()
            return
        self._overlay.start(lambda: self._finish_transition(token, index))

    def _finish_transition(self, token: int, index: int) -> None:
        if token != self._transition_token:
            return
        self._animating = False
        self._target_index = None
        self.transition_finished.emit(index)

    def cancel_transition(self) -> None:
        if not self._animating:
            self._overlay.stop()
            return
        self._transition_token += 1
        self._overlay.stop()
        self._animating = False
        index = self.currentIndex()
        self._target_index = None
        self.transition_finished.emit(index)

    def resizeEvent(self, event) -> None:
        # Rotation/responsive relayout should finish immediately rather than
        # stretching stale snapshots over the new geometry.
        if self._animating:
            self.cancel_transition()
        super().resizeEvent(event)
        self._overlay.setGeometry(self.rect())
        if self._overlay.isVisible():
            self._overlay.raise_()


class GlyphButton(QAbstractButton):
    def __init__(self, glyph: str, tooltip: str = "", danger: bool = False, size: int = 32, parent=None, accent: bool = False):
        super().__init__(parent)
        self.glyph = glyph
        self.danger = danger
        self.accent = accent
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
        self.pressed.connect(self.update)
        self.released.connect(self._release_visual_state)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        hovered = self.underMouse() and not running_on_android()
        if self.accent:
            background = colors["accent_pressed"] if self.isDown() and "accent_pressed" in colors else colors["accent"]
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(background))
            inset = 2 if self.isDown() else 1
            painter.drawEllipse(QRectF(inset, inset, self.width() - inset * 2, self.height() - inset * 2))
        elif self.isDown() or hovered:
            background = colors.get("danger_soft") if self.danger else colors["surface_hover"]
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(background))
            inset = 2 if self.isDown() else 1
            painter.drawRoundedRect(QRectF(inset, inset, self.width() - inset * 2, self.height() - inset * 2), 8, 8)
        ink = colors.get("on_accent", "#FFFFFF") if self.accent else (colors["danger"] if self.danger else colors["muted"])
        if self.isDown() and not self.accent:
            ink = colors["text"] if not self.danger else colors["danger"]
        draw_glyph(painter, self.glyph, QRectF(7, 7, self.width() - 14, self.height() - 14), QColor(ink))

    def _release_visual_state(self) -> None:
        self.clearFocus()
        self.update()

    def enterEvent(self, event) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.update()
        super().leaveEvent(event)


class PopupSurface(QWidget):
    """Touch-first popup backed by a native item view.

    QListWidget keeps the selectable rows inside the scroll viewport instead of
    using child QPushButtons. This prevents a drag from being interpreted as an
    option click and makes kinetic scrolling reliable on Android.
    """

    def __init__(self, parent=None):
        flags = Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(parent, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        self.panel = QFrame()
        self.panel.setObjectName("popupSurface")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(6, 6, 6, 6)

        self.list = QListWidget()
        self.list.setObjectName("selectList")
        self.list.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if is_rtl() else Qt.LayoutDirection.LeftToRight
        )
        self.list.setFrameShape(QFrame.Shape.NoFrame)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.list.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.list.setUniformItemSizes(True)
        self.list.setSpacing(2)
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
        self.list.setMovement(QListWidget.Movement.Static)
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.list.setAutoScroll(False)
        enable_kinetic_scroll(self.list, mouse_fallback=True, vertical_only=True)
        panel_layout.addWidget(self.list)

        shadow = QGraphicsDropShadowEffect(self.panel)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 95))
        self.panel.setGraphicsEffect(shadow)
        outer.addWidget(self.panel)

    @property
    def option_height(self) -> int:
        return 44 if running_on_android() else 38

    def add_option(self, label: str, index: int) -> QListWidgetItem:
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, index)
        item.setTextAlignment(
            (Qt.AlignmentFlag.AlignRight if is_rtl() else Qt.AlignmentFlag.AlignLeft)
            | Qt.AlignmentFlag.AlignVCenter
        )
        item.setSizeHint(QSize(0, self.option_height))
        self.list.addItem(item)
        return item

    def set_option_count(self, count: int, scrollable: bool = True) -> None:
        self.list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded if scrollable else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        visible = max(1, count)
        target_height = visible * self.option_height + max(0, visible - 1) * self.list.spacing() + 4
        self.list.setFixedHeight(min(target_height, 430))

    def show_below(self, anchor: QWidget) -> None:
        inner_width = max(anchor.width(), 150)
        self.panel.setFixedWidth(inner_width)
        self.adjustSize()
        self.setFixedWidth(inner_width + 20)
        self.adjustSize()

        position = anchor.mapToGlobal(QPoint(-10, anchor.height() - 3))
        screen = QGuiApplication.screenAt(position)
        if screen:
            bounds = screen.availableGeometry()
            if self.height() > bounds.height() - 8:
                available_list_height = max(80, bounds.height() - 36)
                self.list.setFixedHeight(available_list_height)
                self.adjustSize()
            if position.y() + self.height() > bounds.bottom():
                position = anchor.mapToGlobal(QPoint(-10, -self.height() + 3))
            x = max(bounds.left(), min(position.x(), bounds.right() - self.width()))
            y = max(bounds.top(), min(position.y(), bounds.bottom() - self.height()))
            position = QPoint(x, y)

        self.move(position)
        self.show()
        self.raise_()

    def show_at(self, position: QPoint, width: int = 190) -> None:
        self.panel.setFixedWidth(width)
        self.adjustSize()
        self.setFixedWidth(width + 20)
        self.adjustSize()
        screen = QGuiApplication.screenAt(position)
        if screen:
            bounds = screen.availableGeometry()
            x = min(position.x() - 10, bounds.right() - self.width())
            y = min(position.y() - 10, bounds.bottom() - self.height())
            position = QPoint(max(bounds.left(), x), max(bounds.top(), y))
        self.move(position)
        self.show()
        self.raise_()


class SoftSelect(QAbstractButton):
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[tuple[str, object]] = []
        self._current_index = -1
        self._popup: PopupSurface | None = None
        self._popup_max_visible_items: int | None = None
        self._popup_fit_to_contents = False
        self.setMinimumHeight(44 if running_on_android() else 42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
        self.pressed.connect(self.update)
        self.released.connect(self._release_visual_state)
        self.clicked.connect(self._show_popup)

    def addItem(self, label: str, data=None) -> None:
        self._items.append((label, data))
        if self._current_index < 0:
            self._current_index = 0
        self.update()

    def clear(self) -> None:
        self._items.clear()
        self._current_index = -1
        self.update()

    def count(self) -> int:
        return len(self._items)

    def currentIndex(self) -> int:
        return self._current_index

    def currentData(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][1]
        return None

    def currentText(self) -> str:
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ""

    def findData(self, data) -> int:
        for index, (_, value) in enumerate(self._items):
            if value == data:
                return index
        return -1

    def setCurrentIndex(self, index: int) -> None:
        if not 0 <= index < len(self._items) or index == self._current_index:
            return
        self._current_index = index
        self.update()
        self.currentIndexChanged.emit(index)

    def setPopupMaxVisibleItems(self, count: int) -> None:
        self._popup_max_visible_items = max(1, count)

    def setPopupFitToContents(self, enabled: bool = True) -> None:
        self._popup_fit_to_contents = enabled

    def _show_popup(self) -> None:
        if not self._items:
            return
        if self._popup is not None:
            try:
                self._popup.close()
            except RuntimeError:
                pass

        popup = PopupSurface(self)
        for index, (label, _) in enumerate(self._items):
            popup.add_option(label, index)

        visible_count = (
            len(self._items)
            if self._popup_fit_to_contents
            else min(len(self._items), self._popup_max_visible_items or len(self._items))
        )
        popup.set_option_count(visible_count, scrollable=visible_count < len(self._items))
        popup.list.setCurrentRow(max(0, self._current_index))
        popup.list.itemActivated.connect(lambda item, p=popup: self._choose_item(item, p))
        popup.list.itemClicked.connect(lambda item, p=popup: self._choose_item(item, p))
        popup.destroyed.connect(lambda *_: self._clear_popup_reference(popup))
        self._popup = popup
        popup.show_below(self)

        selected = popup.list.currentItem()
        if selected is not None:
            popup.list.scrollToItem(selected, QAbstractItemView.ScrollHint.PositionAtCenter)

    def _clear_popup_reference(self, popup: PopupSurface) -> None:
        if self._popup is popup:
            self._popup = None

    def _choose_item(self, item: QListWidgetItem, popup: PopupSurface) -> None:
        # Some Qt styles emit both itemClicked and itemActivated for one tap.
        # Accept only the first signal so a closing popup is never used twice.
        if self._popup is not popup:
            return
        self._popup = None
        index = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(index, int):
            self.setCurrentIndex(index)
        popup.close()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():
            background, border, ink = colors["surface_alt"], colors["border"], colors["faint"]
        elif self.isDown():
            background, border, ink = colors["accent_soft"], colors["accent"], colors["text"]
        elif (self.underMouse() and not running_on_android()) or self.hasFocus():
            background, border, ink = colors["surface_hover"], colors["accent"], colors["text"]
        else:
            background, border, ink = colors["surface"], colors["border"], colors["text"]
        painter.setPen(QPen(QColor(border), 1.5 if self.hasFocus() else 1.0))
        painter.setBrush(QColor(background))
        painter.drawRoundedRect(QRectF(0.75, 0.75, self.width() - 1.5, self.height() - 1.5), 9, 9)
        painter.setPen(QColor(ink))
        rtl = is_rtl()
        text_rect = QRectF(36 if rtl else 12, 0, self.width() - 48, self.height())
        alignment = (Qt.AlignmentFlag.AlignRight if rtl else Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter
        painter.drawText(text_rect, alignment, self.currentText())
        arrow_x = 12 if rtl else self.width() - 28
        draw_glyph(
            painter,
            "down",
            QRectF(arrow_x, 10, 16, self.height() - 20),
            QColor(colors["muted"]),
        )

    def _release_visual_state(self) -> None:
        self.setDown(False)
        self.clearFocus()
        self.update()

    def enterEvent(self, event) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.update()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self.update()
        super().focusOutEvent(event)


class ActionPopover(QWidget):
    def __init__(self, label: str, callback, danger: bool = False, parent=None):
        flags = Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(parent, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(7, 7, 7, 7)
        panel = QFrame()
        panel.setObjectName("popupSurface")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(4, 4, 4, 4)

        button = QPushButton(label)
        button.setObjectName("popoverDanger" if danger else "popoverAction")
        button.setProperty("rtl", is_rtl())
        button.setLayoutDirection(
            Qt.LayoutDirection.RightToLeft if is_rtl() else Qt.LayoutDirection.LeftToRight
        )
        button.setFixedHeight(34)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(self.close)
        button.clicked.connect(callback)
        button.ensurePolished()
        button.setFixedWidth(max(132, button.sizeHint().width()))
        panel_layout.addWidget(button)

        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 85))
        panel.setGraphicsEffect(shadow)
        outer.addWidget(panel)
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def show_at(self, position: QPoint) -> None:
        screen = QGuiApplication.screenAt(position)
        if screen:
            bounds = screen.availableGeometry()
            x = min(position.x() - 7, bounds.right() - self.width())
            y = min(position.y() - 7, bounds.bottom() - self.height())
            position = QPoint(max(bounds.left(), x), max(bounds.top(), y))
        self.move(position)
        self.show()
        self.raise_()


class HoverCheck(QAbstractButton):
    def __init__(self, checked: bool = False, size: int = 22, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(1.5, 1.5, self.width() - 3, self.height() - 3)
        painter.setPen(QPen(QColor(colors["accent"] if self.isChecked() else colors["faint"]), 1.5))
        painter.setBrush(QColor(colors["accent_soft"] if self.isChecked() else colors["surface"]))
        painter.drawRoundedRect(box, 6, 6)
        if self.isChecked() or self.underMouse():
            color = QColor(colors["accent"] if self.isChecked() else colors["faint"])
            if not self.isChecked():
                color.setAlpha(145)
            painter.setPen(QPen(color, 2.1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(QPointF(5.5, self.height() * 0.52), QPointF(9.2, self.height() * 0.69))
            painter.drawLine(QPointF(9.2, self.height() * 0.69), QPointF(self.width() - 5, 6.2))

    def _release_visual_state(self) -> None:
        self.clearFocus()
        self.update()

    def enterEvent(self, event) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.update()
        super().leaveEvent(event)


class CheckOption(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, text: str, checked: bool = False, parent=None):
        super().__init__(parent)
        self.check = HoverCheck(checked, 21)
        self.label = QLabel(text)
        self.label.setObjectName("optionLabel")
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)
        layout.addWidget(self.check)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check.toggled.connect(self.toggled)

    def isChecked(self) -> bool:
        return self.check.isChecked()

    def setChecked(self, checked: bool) -> None:
        self.check.setChecked(checked)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.check.setEnabled(enabled)
        self.label.setEnabled(enabled)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.check.toggle()
        super().mouseReleaseEvent(event)


class BrandMark(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["accent"]))
        painter.drawRoundedRect(QRectF(0, 0, 36, 36), 11, 11)
        font = QFont("SF Pro Display", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(colors.get("on_accent", "#FFFFFF")))
        painter.drawText(QRectF(0, -0.5, 36, 36), Qt.AlignmentFlag.AlignCenter, "D")


class NavButton(QPushButton):
    def __init__(self, text: str, glyph: str | None = None, parent=None):
        self.glyph = glyph
        self._label = text
        super().__init__(self._composed_text(), parent)
        self.setObjectName("navButton")
        self.setProperty("active", False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)

    def _composed_text(self) -> str:
        if not self.glyph:
            return self._label
        return (self._label + "     ") if is_rtl() else ("     " + self._label)

    def set_label(self, text: str) -> None:
        self._label = text
        self.setText(self._composed_text())

    def set_glyph(self, glyph: str | None) -> None:
        self.glyph = glyph
        self.setText(self._composed_text())
        self.update()

    def set_rtl(self, rtl: bool) -> None:
        self.setProperty("rtl", rtl)
        self.setText(self._composed_text())
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.setDown(False)
        self.clearFocus()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if not self.glyph:
            return
        colors = theme_colors()
        painter = QPainter(self)
        draw_glyph(
            painter,
            self.glyph,
            QRectF(self.width() - 28 if is_rtl() else 10, (self.height() - 18) / 2, 18, 18),
            QColor(colors["text"] if self.property("active") else colors["muted"]),
        )


class MobileNavButton(QPushButton):
    def __init__(self, text: str, glyph: str, parent=None):
        super().__init__(text, parent)
        self.glyph = glyph
        self.setObjectName("mobileNavButton")
        self.setProperty("active", False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(58)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.setDown(False)
        self.clearFocus()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        colors = theme_colors()
        painter = QPainter(self)
        draw_glyph(
            painter,
            self.glyph,
            QRectF((self.width() - 18) / 2, 7, 18, 18),
            QColor(colors["accent"] if self.property("active") else colors["muted"]),
        )


class SegmentedControl(QFrame):
    changed = pyqtSignal(str)

    def __init__(self, items: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setObjectName("segmentBar")
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(3, 3, 3, 3)
        self._layout.setSpacing(2)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}
        self._locked = False
        self.indicator = SlidingHighlight(self, "segmentIndicator")
        for index, (key, label) in enumerate(items):
            button = QPushButton(label)
            button.setObjectName("segment")
            button.setCheckable(True)
            button.setMinimumHeight(36)
            button.setMinimumWidth(68)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus if running_on_android() else Qt.FocusPolicy.StrongFocus)
            button.setProperty("active", index == 0)
            button.setChecked(index == 0)
            button.clicked.connect(lambda checked=False, k=key: self._select(k))
            self.group.addButton(button)
            self.buttons[key] = button
            self._layout.addWidget(button)
        QTimer.singleShot(0, lambda: self.indicator.move_to(next(iter(self.buttons.values())), False))

    def _select(self, key: str, emit: bool = True, animate: bool = True) -> None:
        if self._locked:
            return
        target = self.buttons.get(key)
        if target is None:
            return
        for name, button in self.buttons.items():
            active = name == key
            button.setChecked(active)
            button.setDown(False)
            button.setProperty("active", active)
            button.clearFocus()
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        QTimer.singleShot(0, lambda: self.indicator.move_to(target, animate))
        if emit:
            self.changed.emit(key)

    def select(self, key: str, emit: bool = True, animate: bool = True) -> None:
        self._select(key, emit=emit, animate=animate)

    def set_locked(self, locked: bool) -> None:
        self._locked = locked
        if not locked:
            for button in self.buttons.values():
                button.setDown(False)
                button.clearFocus()
                button.update()

    def snap_indicator(self) -> None:
        self._snap_indicator()

    def set_labels(self, labels: dict[str, str]) -> None:
        for key, label in labels.items():
            if key in self.buttons:
                self.buttons[key].setText(label)
        QTimer.singleShot(0, self._snap_indicator)

    def _snap_indicator(self) -> None:
        target = next((button for button in self.buttons.values() if button.property("active")), None)
        self.indicator.move_to(target, False)

    def set_compact(self, compact: bool) -> None:
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding if compact else QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        for button in self.buttons.values():
            button.setMinimumWidth(0 if compact else 68)
            button.setProperty("compact", compact)
            button.style().unpolish(button)
            button.style().polish(button)
        QTimer.singleShot(0, self._snap_indicator)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        QTimer.singleShot(0, self._snap_indicator)


class GlyphIcon(QWidget):
    def __init__(self, glyph: str, size: int = 42, parent=None):
        super().__init__(parent)
        self.glyph = glyph
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        draw_glyph(painter, self.glyph, QRectF(8, 8, self.width() - 16, self.height() - 16), QColor(colors["accent"]))


class EmptyState(QWidget):
    def __init__(self, title: str, message: str, symbol: str = "check", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        known_glyphs = {"check", "circle", "planner", "sun", "return", "unarchive", "clock", "tasks"}
        if symbol in known_glyphs:
            icon = GlyphIcon(symbol)
            layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignHCenter)
        else:
            icon = QLabel(symbol)
            icon.setObjectName("emptyIcon")
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon)
        heading = QLabel(title)
        heading.setObjectName("emptyTitle")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy = QLabel(message)
        copy.setObjectName("muted")
        copy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy.setWordWrap(True)
        copy.setMaximumWidth(300)
        layout.addWidget(heading)
        layout.addWidget(copy)


class SwipeActionButton(QAbstractButton):
    def __init__(self, glyph: str, label: str, role: str = "neutral", parent=None):
        super().__init__(parent)
        self.glyph = glyph
        self.label = label
        self.role = role
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumWidth(66)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        if self.role == "danger":
            background = colors["danger"]
            ink = QColor(colors.get("on_danger", "#FFFFFF"))
        elif self.role == "accent":
            background = colors["accent"]
            ink = QColor(colors.get("on_accent", "#FFFFFF"))
        else:
            background = colors.get("accent_soft", colors["surface_hover"])
            ink = QColor(colors["text"])
        if self.isDown():
            background = colors.get("accent_pressed", colors["border"]) if self.role != "danger" else colors["danger"]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(background))
        inset = 2 if self.isDown() else 1
        painter.drawRoundedRect(
            QRectF(inset, inset, self.width() - inset * 2, self.height() - inset * 2),
            11,
            11,
        )
        draw_glyph(painter, self.glyph, QRectF((self.width() - 24) / 2, 12, 24, 24), ink)
        painter.setPen(ink)
        font = painter.font()
        font.setPointSizeF(max(8.0, font.pointSizeF() - 1.0))
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(
            QRectF(3, 41, self.width() - 6, max(20, self.height() - 44)),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self.label,
        )


class TaskCard(QFrame):
    completed = pyqtSignal(int)
    restored = pyqtSignal(int)
    edit_requested = pyqtSignal(int)
    details_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    star_requested = pyqtSignal(int, bool)
    date_requested = pyqtSignal(int)
    swipe_opened = pyqtSignal(object)
    _open_card = None

    def __init__(self, task: Task, mode: str = "all", parent=None):
        super().__init__(parent)
        self.task = task
        self.mode = mode
        self._removal_animation = None
        self._swipe_animation = None
        self._press_x = 0.0
        self._press_y = 0.0
        self._surface_start_x = 0
        self._press_started = 0.0
        self._dragging = False
        self._vertical_gesture = False
        self._revealed = False
        self._swipe_enabled = running_on_android() and mode in {"all", "day"}
        self._action_width = 198
        self.setObjectName("taskCardHost" if self._swipe_enabled else "taskCard")
        self.setProperty("compact", mode == "week")
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored if mode == "week" else QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if mode in {"all", "day", "week"}
            else Qt.CursorShape.ArrowCursor
        )

        if self._swipe_enabled:
            self.actions = QFrame(self)
            self.actions.setObjectName("swipeActions")
            actions_layout = QHBoxLayout(self.actions)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            star = SwipeActionButton("star", t("unstar") if task.starred else t("star"), "neutral")
            date_button = SwipeActionButton("calendar", t("change_date"), "accent")
            delete = SwipeActionButton("trash", t("delete"), "danger")
            star.clicked.connect(self._toggle_star)
            date_button.clicked.connect(self._change_date)
            delete.clicked.connect(self._delete_from_swipe)
            actions_layout.addWidget(star, 1)
            actions_layout.addWidget(date_button, 1)
            actions_layout.addWidget(delete, 1)

            self.actions.hide()

            self.surface = QFrame(self)
            self.surface.setObjectName("taskCardSurface")
            self.surface.setProperty("compact", mode == "week")
            self.surface.installEventFilter(self)
            self._build_surface(self.surface)
            self.setMinimumHeight(max(76, self.surface.sizeHint().height()))
            self.destroyed.connect(self._clear_open_reference)
            QTimer.singleShot(0, self._sync_height)
        else:
            self.surface = self
            self._build_surface(self)

    @classmethod
    def close_open_card(cls, immediate: bool = False) -> None:
        card = cls._open_card
        cls._open_card = None
        if card is None:
            return
        try:
            if immediate:
                card._stop_swipe_animation()
                card._revealed = False
                if card._swipe_enabled:
                    card.surface.move(0, 0)
                    card.actions.hide()
            else:
                card.close_actions()
        except RuntimeError:
            pass

    def _clear_open_reference(self, *args) -> None:
        if TaskCard._open_card is self:
            TaskCard._open_card = None
        self._swipe_animation = None

    def _stop_swipe_animation(self) -> None:
        animation = self._swipe_animation
        self._swipe_animation = None
        if animation is not None:
            animation.stop()
            animation.deleteLater()

    def _calculated_action_width(self, width: int) -> int:
        # Keep all three actions usable on small phones without revealing more
        # than roughly 60% of the card.
        return max(168, min(216, int(width * 0.58)))

    def _build_surface(self, target: QWidget) -> None:
        compact = self.mode == "week"
        touch = running_on_android()
        outer = QHBoxLayout(target)
        outer.setContentsMargins(
            10 if compact else 14,
            10 if compact else 12,
            8 if compact else 10,
            10 if compact else 12,
        )
        outer.setSpacing(9 if compact else 11)

        if self.mode == "history":
            restore = GlyphButton("return", t("return_active"), size=42 if touch else 30)
            restore.clicked.connect(lambda: self.restored.emit(self.task.id or 0))
            outer.addWidget(restore, 0, Qt.AlignmentFlag.AlignTop)
        else:
            self.check = HoverCheck(False, 28 if touch else (22 if not compact else 21))
            self.check.clicked.connect(self._complete)
            outer.addWidget(self.check, 0, Qt.AlignmentFlag.AlignTop)

        content_widget = QWidget()
        content_widget.setMinimumWidth(0)
        content_widget.setSizePolicy(
            QSizePolicy.Policy.Ignored if compact else QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        content_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        content = QVBoxLayout(content_widget)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(3)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(5)
        title = QLabel(self.task.title)
        if compact:
            title.setObjectName("weekTaskTitleOverdue" if self.task.is_overdue else "weekTaskTitle")
        else:
            title.setObjectName("taskTitleDone" if self.task.is_completed else "taskTitle")
        title.setWordWrap(True)
        title.setMinimumWidth(0)
        title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        title_row.addWidget(title, 1)
        if self.task.starred and not compact:
            star_mark = GlyphIcon("star", 20)
            star_mark.setToolTip(t("starred"))
            title_row.addWidget(star_mark, 0, Qt.AlignmentFlag.AlignTop)
        content.addLayout(title_row)

        if not compact:
            meta_row = QHBoxLayout()
            meta_row.setContentsMargins(0, 0, 0, 0)
            meta_row.setSpacing(6)
            if self.task.category_color:
                dot = QLabel()
                dot.setFixedSize(7, 7)
                dot.setStyleSheet(f"background:{self.task.category_color}; border-radius:3px;")
                meta_row.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
            meta_bits: list[str] = []
            if self.task.category_name:
                meta_bits.append(self.task.category_name)
            meta_bits.append(self.task.schedule_label)
            meta = QLabel("  ·  ".join(meta_bits))
            meta.setObjectName("overdue" if self.task.is_overdue else "taskMeta")
            meta.setWordWrap(False)
            meta.setMinimumWidth(0)
            meta.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            meta_row.addWidget(meta, 1, Qt.AlignmentFlag.AlignVCenter)
            if self.task.recurrence != "none":
                repeat_icon = GlyphIcon("repeat", 16)
                repeat_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                meta_row.addWidget(repeat_icon, 0, Qt.AlignmentFlag.AlignVCenter)
                repeat_text = QLabel(recurrence_label(self.task.recurrence))
                repeat_text.setObjectName("taskMeta")
                repeat_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                meta_row.addWidget(repeat_text, 0, Qt.AlignmentFlag.AlignVCenter)
            content.addLayout(meta_row)

            if self.task.notes:
                notes = QLabel(self.task.notes)
                notes.setObjectName("taskNotes")
                notes.setWordWrap(True)
                notes.setMaximumHeight(40)
                notes.setMinimumWidth(0)
                notes.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
                content.addWidget(notes)

            if self.task.subtasks:
                done_count = sum(1 for item in self.task.subtasks if item.completed)
                subtask_summary = QLabel(
                    f"{done_count}/{len(self.task.subtasks)}  ·  "
                    + t("subtask_count_many", count=len(self.task.subtasks))
                )
                subtask_summary.setObjectName("taskMeta")
                content.addWidget(subtask_summary)
        outer.addWidget(content_widget, 1)

        if not self._swipe_enabled:
            if self.mode not in {"week"}:
                delete = GlyphButton(
                    "trash",
                    t("delete_task_tooltip"),
                    danger=True,
                    size=42 if touch else 32,
                )
                delete.clicked.connect(lambda: self.delete_requested.emit(self.task.id or 0))
                outer.addWidget(delete, 0, Qt.AlignmentFlag.AlignVCenter)

    def _sync_height(self) -> None:
        if not self._swipe_enabled:
            return
        height = max(76, self.surface.sizeHint().height())
        self.setMinimumHeight(height)
        self.updateGeometry()
        self.resizeEvent(None)

    def resizeEvent(self, event) -> None:
        if event is not None:
            super().resizeEvent(event)
        if not self._swipe_enabled:
            return
        width = self.width()
        height = self.height()
        next_action_width = self._calculated_action_width(width)
        if next_action_width != self._action_width:
            self._action_width = next_action_width
        self.actions.setGeometry(max(0, width - self._action_width), 0, self._action_width, height)
        x = self.surface.x()
        if not self._dragging:
            x = -self._action_width if self._revealed else 0
        self.surface.setGeometry(x, 0, width, height)

    @staticmethod
    def _point(event):
        position = event.position() if hasattr(event, "position") else event.pos()
        return float(position.x()), float(position.y())

    def eventFilter(self, watched, event) -> bool:
        if watched is not self.surface or not self._swipe_enabled:
            return super().eventFilter(watched, event)
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._press_x, self._press_y = self._point(event)
            self._surface_start_x = self.surface.x()
            self._press_started = monotonic()
            self._dragging = False
            self._vertical_gesture = False
            self._stop_swipe_animation()
            return False
        if event_type == QEvent.Type.MouseMove and event.buttons() & Qt.MouseButton.LeftButton:
            x, y = self._point(event)
            dx = x - self._press_x
            dy = y - self._press_y
            if not self._dragging and not self._vertical_gesture:
                threshold = max(8, QApplication.startDragDistance())
                if abs(dy) > threshold and abs(dy) > abs(dx) * 1.08:
                    self._vertical_gesture = True
                    TaskCard.close_open_card()
                elif abs(dx) > threshold and abs(dx) > abs(dy) * 1.20:
                    self._dragging = True
            if self._dragging:
                self.actions.show()
                self.actions.raise_()
                self.surface.raise_()
                target = max(-self._action_width, min(0, self._surface_start_x + int(dx)))
                self.surface.move(target, 0)
                return True
        if event_type == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if self._vertical_gesture:
                return False
            if self._dragging:
                x, _ = self._point(event)
                elapsed = max(0.025, monotonic() - self._press_started)
                velocity = (x - self._press_x) / elapsed
                open_it = (
                    self.surface.x() <= -self._action_width * 0.42
                    or velocity < -520
                )
                if velocity > 520:
                    open_it = False
                self._animate_swipe(-self._action_width if open_it else 0)
                return True
            if self._revealed:
                self.close_actions()
            else:
                self.edit_requested.emit(self.task.id or 0)
            return True
        return super().eventFilter(watched, event)

    def _animate_swipe(self, target_x: int, finished: Callable[[], None] | None = None) -> None:
        self._stop_swipe_animation()
        if target_x < 0:
            self.actions.show()
            self.actions.raise_()
            self.surface.raise_()
            previous = TaskCard._open_card
            if previous is not None and previous is not self:
                try:
                    previous.close_actions()
                except RuntimeError:
                    pass
            TaskCard._open_card = self
            self.swipe_opened.emit(self)
        elif TaskCard._open_card is self:
            TaskCard._open_card = None
        self._revealed = target_x < 0

        start_pos = self.surface.pos()
        end_pos = QPoint(target_x, 0)
        if start_pos == end_pos:
            self.surface.move(end_pos)
            if target_x == 0:
                self.actions.hide()
            if finished is not None:
                QTimer.singleShot(0, finished)
            return

        # Position-only animation avoids resize/layout work on every frame.
        animation = QPropertyAnimation(self.surface, b"pos", self)
        animation.setDuration(155 if running_on_android() else 185)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutQuart)

        def complete() -> None:
            if self._swipe_animation is animation:
                self._swipe_animation = None
            animation.deleteLater()
            if target_x == 0:
                self.actions.hide()
            if finished is not None:
                finished()

        animation.finished.connect(complete)
        self._swipe_animation = animation
        animation.start()

    def _close_then(self, callback: Callable[[], None]) -> None:
        if self._swipe_enabled and (self._revealed or self.surface.x() != 0):
            self._animate_swipe(0, callback)
        else:
            callback()

    def open_actions(self) -> None:
        if self._swipe_enabled:
            self._animate_swipe(-self._action_width)

    def close_actions(self) -> None:
        if self._swipe_enabled:
            self._animate_swipe(0)

    def _toggle_star(self) -> None:
        self._close_then(
            lambda: self.star_requested.emit(self.task.id or 0, not self.task.starred)
        )

    def _change_date(self) -> None:
        self._close_then(lambda: self.date_requested.emit(self.task.id or 0))

    def _delete_from_swipe(self) -> None:
        self._close_then(lambda: self.delete_requested.emit(self.task.id or 0))

    def _complete(self) -> None:
        self.check.setEnabled(False)
        self.completed.emit(self.task.id or 0)

    def mouseReleaseEvent(self, event) -> None:
        if not self._swipe_enabled and event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "week":
                self.details_requested.emit(self.task.id or 0)
            elif self.mode in {"all", "day"}:
                self.edit_requested.emit(self.task.id or 0)
        super().mouseReleaseEvent(event)

    def animate_out(self, callback: Callable[[], None]) -> None:
        if self._removal_animation is not None:
            self._removal_animation.stop()
            self._removal_animation.deleteLater()
            self._removal_animation = None
        TaskCard.close_open_card(immediate=True)
        start_height = max(self.height(), self.sizeHint().height())
        self.setMinimumHeight(0)
        self.setMaximumHeight(start_height)
        group = QParallelAnimationGroup(self)
        opacity_effect = None
        if not running_on_android():
            opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(opacity_effect)
            opacity = QPropertyAnimation(opacity_effect, b"opacity", self)
            opacity.setDuration(190)
            opacity.setStartValue(1.0)
            opacity.setEndValue(0.0)
            opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
            group.addAnimation(opacity)
        height = QPropertyAnimation(self, b"maximumHeight", self)
        height.setDuration(165 if running_on_android() else 235)
        height.setStartValue(start_height)
        height.setEndValue(0)
        height.setEasingCurve(QEasingCurve.Type.InOutCubic)
        group.addAnimation(height)

        def complete_removal() -> None:
            if self._removal_animation is group:
                self._removal_animation = None
            if opacity_effect is not None:
                self.setGraphicsEffect(None)
            group.deleteLater()
            callback()

        group.finished.connect(complete_removal)
        self._removal_animation = group
        group.start()


class Section(QWidget):
    def __init__(self, title: str, count: int, parent=None):
        super().__init__(parent)
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.setSpacing(8)
        heading = QHBoxLayout()
        label = QLabel(title)
        label.setObjectName("sectionTitle")
        number = QLabel(localize_digits(count))
        number.setObjectName("countPill")
        heading.addWidget(label)
        heading.addWidget(number)
        heading.addStretch()
        self.box.addLayout(heading)

    def add_card(self, card: TaskCard) -> None:
        self.box.addWidget(card)
