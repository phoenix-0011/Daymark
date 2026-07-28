from __future__ import annotations

from datetime import date, timedelta

from .analytics import InsightSnapshot, calculate_insights
from .database import Database
from .device import running_on_android
from .formatting import weekday_name
from .i18n import localize_digits, t
from .qt import (
    QColor,
    QFont,
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPainter,
    QPainterPath,
    QPen,
    QPointF,
    QRectF,
    QScrollArea,
    QSize,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
)
from .widgets import SoftSelect, enable_kinetic_scroll, theme_colors


class ConsistencyBadge(QWidget):
    """Minimal progress/check badge used in the Mine hero card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Soft rounded tile keeps the icon aligned with the rest of the report UI.
        tile = QRectF(1, 1, 46, 46)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["accent_soft"]))
        painter.drawRoundedRect(tile, 15, 15)

        # A nearly complete progress ring communicates consistency/streak.
        ring = QRectF(10, 10, 28, 28)
        ring_pen = QPen(
            QColor(colors["accent"]),
            2.4,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(ring_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(ring, 52 * 16, 286 * 16)

        # Crisp check mark in the centre.
        check_pen = QPen(
            QColor(colors["accent"]),
            2.7,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(check_pen)
        painter.drawLine(QPointF(17.2, 24.3), QPointF(22.0, 29.0))
        painter.drawLine(QPointF(22.0, 29.0), QPointF(31.2, 19.4))

        # Small endpoint dot gives the progress ring a finished, intentional look.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["accent"]))
        painter.drawEllipse(QRectF(34.0, 10.6, 3.6, 3.6))


class MetricCard(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("insightMetricCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(96)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        self.title = QLabel(title)
        self.title.setObjectName("insightMetricTitle")
        self.value = QLabel("0")
        self.value.setObjectName("insightMetricValue")
        self.note = QLabel("")
        self.note.setObjectName("insightMetricNote")
        self.note.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.note)

    def set_data(self, title: str, value: str, note: str = "") -> None:
        self.title.setText(title)
        self.value.setText(value)
        self.note.setText(note)
        self.note.setVisible(bool(note))


class InsightCard(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("insightCard")
        self.layout_box = QVBoxLayout(self)
        self.layout_box.setContentsMargins(15, 13, 15, 15)
        self.layout_box.setSpacing(10)
        header = QHBoxLayout()
        self.title = QLabel(title)
        self.title.setObjectName("insightCardTitle")
        self.meta = QLabel("")
        self.meta.setObjectName("insightCardMeta")
        header.addWidget(self.title, 1)
        header.addWidget(self.meta)
        self.layout_box.addLayout(header)

    def set_header(self, title: str, meta: str = "") -> None:
        self.title.setText(title)
        self.meta.setText(meta)
        self.meta.setVisible(bool(meta))


class AnnualHeatmap(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.year = date.today().year
        self.counts: dict[date, int] = {}
        self.setMinimumHeight(148)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:
        return QSize(520, 158)

    def set_data(self, year: int, counts: dict[date, int]) -> None:
        self.year = year
        self.counts = counts
        self.update()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = max(1, self.width())
        left = 31.0
        top = 13.0
        gap = 2.2
        columns = 53
        cell = min(11.0, max(4.0, (width - left - (columns - 1) * gap - 4) / columns))
        year_start = date(self.year, 1, 1)
        sunday_index = (year_start.weekday() + 1) % 7
        grid_start = year_start - timedelta(days=sunday_index)
        max_count = max((count for day, count in self.counts.items() if day.year == self.year), default=0)
        accent = QColor(colors["accent"])
        empty = QColor(colors["surface_alt"])

        painter.setFont(QFont(painter.font().family(), 7))
        painter.setPen(QColor(colors["faint"]))
        for row, key in ((0, "sun_short"), (2, "tue_short"), (4, "thu_short"), (6, "sat_short")):
            painter.drawText(QRectF(0, top + row * (cell + gap) - 2, 27, cell + 4), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, t(key))

        for column in range(columns):
            for row in range(7):
                day = grid_start + timedelta(days=column * 7 + row)
                if day.year != self.year:
                    color = QColor(colors["surface_alt"])
                    color.setAlpha(70)
                else:
                    count = self.counts.get(day, 0)
                    if count <= 0 or max_count <= 0:
                        color = empty
                    else:
                        level = min(4, max(1, round(count / max_count * 4)))
                        color = QColor(accent)
                        color.setAlpha(60 + level * 45)
                x = left + column * (cell + gap)
                y = top + row * (cell + gap)
                painter.setBrush(color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(x, y, cell, cell), 2.0, 2.0)

        month_marks = [(1, 0), (3, 9), (5, 18), (7, 27), (9, 36), (11, 44)]
        painter.setPen(QColor(colors["faint"]))
        for month, column in month_marks:
            x = left + column * (cell + gap)
            painter.drawText(QRectF(x, top + 7 * (cell + gap) + 5, 45, 14), Qt.AlignmentFlag.AlignLeft, t(f"month_short_{month}"))


class DonutChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percent = 0
        self.center_label = "0%"
        self.setMinimumSize(140, 140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_percent(self, percent: int) -> None:
        self.percent = max(0, min(100, percent))
        self.center_label = f"{localize_digits(self.percent)}%"
        self.update()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 24
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        pen = QPen(QColor(colors["surface_alt"]), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 0, 360 * 16)
        pen.setColor(QColor(colors["accent"]))
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -self.percent * 360 * 16 // 100)
        painter.setPen(QColor(colors["text"]))
        font = painter.font()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.center_label)


class WeeklyBars(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: tuple[int, ...] = (0,) * 7
        self.labels: tuple[str, ...] = ("",) * 7
        self.setMinimumHeight(165)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, values: tuple[int, ...], days: tuple[date, ...]) -> None:
        self.values = values
        self.labels = tuple(weekday_name(day, short=True) for day in days)
        self.update()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, right, top, bottom = 12.0, 8.0, 10.0, 28.0
        chart_width = max(1.0, self.width() - left - right)
        chart_height = max(1.0, self.height() - top - bottom)
        max_value = max(max(self.values, default=0), 1)
        slot = chart_width / 7
        bar_width = min(24.0, slot * 0.52)
        painter.setPen(QPen(QColor(colors["border"]), 1))
        for level in (0.25, 0.5, 0.75, 1.0):
            y = top + chart_height * (1 - level)
            painter.drawLine(int(left), int(y), int(left + chart_width), int(y))
        painter.setPen(Qt.PenStyle.NoPen)
        for index, value in enumerate(self.values):
            height = chart_height * value / max_value if value else 5
            x = left + index * slot + (slot - bar_width) / 2
            y = top + chart_height - height
            painter.setBrush(QColor(colors["accent"] if value else colors["surface_alt"]))
            painter.drawRoundedRect(QRectF(x, y, bar_width, height), bar_width / 2, bar_width / 2)
        painter.setFont(QFont(painter.font().family(), 8))
        painter.setPen(QColor(colors["muted"]))
        for index, label in enumerate(self.labels):
            x = left + index * slot
            painter.drawText(QRectF(x, top + chart_height + 7, slot, 18), Qt.AlignmentFlag.AlignCenter, label[:3])


class CategoryBars(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: tuple[tuple[str, int], ...] = ()
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, items: tuple[tuple[str, int], ...]) -> None:
        self.items = items
        self.setMinimumHeight(max(80, len(items) * 38 + 8))
        self.updateGeometry()
        self.update()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.items:
            painter.setPen(QColor(colors["muted"]))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, t("no_task_data"))
            return
        maximum = max(value for _, value in self.items) or 1
        row_height = 38
        for index, (name, value) in enumerate(self.items):
            y = index * row_height
            display_name = name or t("uncategorized")
            painter.setPen(QColor(colors["text"]))
            painter.drawText(QRectF(2, y, self.width() * 0.44, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_name)
            painter.setPen(QColor(colors["muted"]))
            painter.drawText(QRectF(self.width() - 38, y, 36, 18), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, localize_digits(value))
            bar_x = 2
            bar_y = y + 23
            bar_width = max(1, self.width() - 4)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(colors["surface_alt"]))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_width, 7), 3.5, 3.5)
            painter.setBrush(QColor(colors["accent"]))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_width * value / maximum, 7), 3.5, 3.5)


class UpcomingStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: tuple[int, ...] = (0,) * 7
        self.days: tuple[date, ...] = tuple(date.today() + timedelta(days=i) for i in range(7))
        self.setMinimumHeight(92)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_data(self, values: tuple[int, ...], days: tuple[date, ...]) -> None:
        self.values = values
        self.days = days
        self.update()

    def paintEvent(self, event) -> None:
        colors = theme_colors()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        slot = self.width() / 7 if self.width() else 1
        max_value = max(max(self.values, default=0), 1)
        for index, (day, value) in enumerate(zip(self.days, self.values)):
            x = index * slot
            bubble = QRectF(x + (slot - 35) / 2, 5, 35, 35)
            painter.setPen(Qt.PenStyle.NoPen)
            fill = QColor(colors["accent_soft"] if value else colors["surface_alt"])
            painter.setBrush(fill)
            painter.drawEllipse(bubble)
            painter.setPen(QColor(colors["accent"] if value else colors["muted"]))
            font = painter.font()
            font.setBold(bool(value))
            painter.setFont(font)
            painter.drawText(bubble, Qt.AlignmentFlag.AlignCenter, localize_digits(value))
            painter.setPen(QColor(colors["muted"]))
            font.setBold(False)
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(QRectF(x, 48, slot, 17), Qt.AlignmentFlag.AlignCenter, weekday_name(day, short=True)[:3])
            painter.setPen(QColor(colors["faint"]))
            painter.drawText(QRectF(x, 67, slot, 17), Qt.AlignmentFlag.AlignCenter, localize_digits(day.day))


class InsightsView(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.compact = False
        self.snapshot: InsightSnapshot | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        enable_kinetic_scroll(self.scroll, vertical_only=True)
        self.container = QWidget()
        self.container.setObjectName("insightsContent")
        self.content = QVBoxLayout(self.container)
        self.content.setContentsMargins(0, 2, 8, 24)
        self.content.setSpacing(12)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll)

        self.hero = QFrame()
        self.hero.setObjectName("insightHero")
        hero_layout = QHBoxLayout(self.hero)
        hero_layout.setContentsMargins(14, 13, 14, 13)
        hero_layout.setSpacing(12)
        hero_layout.addWidget(ConsistencyBadge())
        hero_text = QVBoxLayout()
        hero_text.setSpacing(2)
        self.hero_title = QLabel()
        self.hero_title.setObjectName("insightHeroTitle")
        self.hero_subtitle = QLabel(t("insight_hero_subtitle"))
        self.hero_subtitle.setObjectName("insightHeroSubtitle")
        hero_text.addWidget(self.hero_title)
        hero_text.addWidget(self.hero_subtitle)
        hero_layout.addLayout(hero_text, 1)
        self.content.addWidget(self.hero)

        self.metrics = QGridLayout()
        self.metrics.setHorizontalSpacing(10)
        self.metrics.setVerticalSpacing(10)
        self.completed_card = MetricCard()
        self.pending_card = MetricCard()
        self.overdue_card = MetricCard()
        self.rate_card = MetricCard()
        self.metrics.addWidget(self.completed_card, 0, 0)
        self.metrics.addWidget(self.pending_card, 0, 1)
        self.metrics.addWidget(self.overdue_card, 1, 0)
        self.metrics.addWidget(self.rate_card, 1, 1)
        self.content.addLayout(self.metrics)

        self.heatmap_card = InsightCard()
        self.year_select = SoftSelect()
        self.year_select.setPopupFitToContents(True)
        # Four digits plus the dropdown glyph need a little more breathing room
        # on Android font scaling; 92 px could clip the final digit by a few px.
        self.year_select.setFixedWidth(106 if running_on_android() else 98)
        header_layout = self.heatmap_card.layout_box.itemAt(0).layout()
        if header_layout is not None:
            header_layout.addWidget(self.year_select)
        self.heatmap = AnnualHeatmap()
        self.heatmap_card.layout_box.addWidget(self.heatmap)
        self.content.addWidget(self.heatmap_card)
        self.year_select.currentIndexChanged.connect(self._year_changed)

        self.report_grid = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.report_grid.setSpacing(12)
        self.status_card = InsightCard()
        self.donut = DonutChart()
        self.status_card.layout_box.addWidget(self.donut, 1)
        self.status_note = QLabel()
        self.status_note.setObjectName("insightCenteredNote")
        self.status_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_card.layout_box.addWidget(self.status_note)

        self.week_card = InsightCard()
        self.week_bars = WeeklyBars()
        self.week_card.layout_box.addWidget(self.week_bars)
        self.week_note = QLabel()
        self.week_note.setObjectName("insightCenteredNote")
        self.week_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.week_card.layout_box.addWidget(self.week_note)
        self.report_grid.addWidget(self.status_card, 1)
        self.report_grid.addWidget(self.week_card, 1)
        self.content.addLayout(self.report_grid)

        self.category_card = InsightCard()
        self.category_bars = CategoryBars()
        self.category_card.layout_box.addWidget(self.category_bars)
        self.content.addWidget(self.category_card)

        self.upcoming_card = InsightCard()
        self.upcoming_strip = UpcomingStrip()
        self.upcoming_card.layout_box.addWidget(self.upcoming_strip)
        self.upcoming_note = QLabel()
        self.upcoming_note.setObjectName("insightCenteredNote")
        self.upcoming_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upcoming_card.layout_box.addWidget(self.upcoming_note)
        self.content.addWidget(self.upcoming_card)
        self.content.addStretch()

        self._populate_years()
        self.retranslate()

    def _populate_years(self) -> None:
        previous_year = self.year_select.currentData()
        completed = self.db.tasks(completed=True)
        years = {date.today().year}
        years.update(task.completed_at.year for task in completed if task.completed_at)
        self.year_select.blockSignals(True)
        self.year_select.clear()
        for year in sorted(years, reverse=True):
            self.year_select.addItem(localize_digits(year), year)
        target_year = previous_year if isinstance(previous_year, int) and previous_year in years else date.today().year
        self.year_select.setCurrentIndex(max(0, self.year_select.findData(target_year)))
        self.year_select.blockSignals(False)

    def _year_changed(self, index: int) -> None:
        if self.snapshot is None:
            return
        selected = self.year_select.currentData()
        if isinstance(selected, int):
            self.heatmap.set_data(selected, self.snapshot.heatmap_counts)

    def set_compact(self, compact: bool) -> None:
        self.compact = compact
        self.content.setContentsMargins(0, 2, 0 if compact else 8, 24)
        self.report_grid.setDirection(
            QBoxLayout.Direction.TopToBottom if compact else QBoxLayout.Direction.LeftToRight
        )
        for card in (self.completed_card, self.pending_card, self.overdue_card, self.rate_card):
            card.setMinimumHeight(92 if compact else 100)

    def retranslate(self) -> None:
        self.hero_subtitle.setText(t("insight_hero_subtitle"))
        self.heatmap_card.set_header(t("annual_heatmap"))
        self.status_card.set_header(t("completion_status"), t("all_time"))
        self.week_card.set_header(t("daily_completed"), t("last_7_days"))
        self.category_card.set_header(t("category_breakdown"), t("completed_tasks"))
        self.upcoming_card.set_header(t("tasks_next_7_days"))
        self.refresh()

    def refresh(self) -> None:
        pending = self.db.tasks(completed=False)
        completed = self.db.tasks(completed=True)
        self.snapshot = calculate_insights(pending, completed)
        snapshot = self.snapshot
        self._populate_years()

        streak = localize_digits(snapshot.streak_days)
        self.hero_title.setText(
            t("kept_plan_day_one") if snapshot.streak_days == 1 else t("kept_plan_days", count=streak)
        )
        self.completed_card.set_data(t("completed_tasks"), localize_digits(snapshot.completed_total), t("all_time"))
        self.pending_card.set_data(t("pending_tasks"), localize_digits(snapshot.pending_total), t("active_now"))
        self.overdue_card.set_data(t("overdue_tasks"), localize_digits(snapshot.overdue_total), t("needs_attention"))
        self.rate_card.set_data(t("completion_rate"), f"{localize_digits(snapshot.completion_rate)}%", t("all_time"))

        selected_year = self.year_select.currentData()
        year = selected_year if isinstance(selected_year, int) else date.today().year
        self.heatmap.set_data(year, snapshot.heatmap_counts)
        self.donut.set_percent(snapshot.completion_rate)
        self.status_note.setText(t("completed_pending_summary", completed=localize_digits(snapshot.completed_total), pending=localize_digits(snapshot.pending_total)))
        self.week_bars.set_data(snapshot.daily_completed, snapshot.daily_labels)
        self.week_note.setText(t("week_completed_summary", count=localize_digits(snapshot.week_completed)))
        self.category_bars.set_data(snapshot.category_counts)
        self.upcoming_strip.set_data(snapshot.upcoming_counts, snapshot.upcoming_labels)
        upcoming_total = sum(snapshot.upcoming_counts)
        self.upcoming_note.setText(
            t("upcoming_summary", count=localize_digits(upcoming_total))
            if upcoming_total
            else t("no_upcoming_tasks")
        )
