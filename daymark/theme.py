from __future__ import annotations

from .qt import QColor, QPalette
from .device import running_on_android


PALETTE_WARM_SAGE = "warm_sage"
PALETTE_SKY_BLUE = "sky_blue"
PALETTE_ARISTOCRATIC_GREEN = "aristocratic_green"
DEFAULT_PALETTE = PALETTE_WARM_SAGE
PALETTE_KEYS = (
    PALETTE_WARM_SAGE,
    PALETTE_SKY_BLUE,
    PALETTE_ARISTOCRATIC_GREEN,
)


# Each palette is a complete semantic color system. Widgets never consume raw
# palette names; they consume these shared roles, which keeps Tasks, Planner,
# History, Mine, dialogs, charts, and navigation visually coherent.
PALETTES: dict[str, dict[str, dict[str, str]]] = {
    PALETTE_WARM_SAGE: {
        "light": {
            "window": "#F8F3ED",
            "sidebar": "#F1E9E0",
            "surface": "#FFFCF8",
            "surface_alt": "#F5EEE7",
            "surface_hover": "#EEE5DA",
            "text": "#332F2B",
            "muted": "#736B63",
            "faint": "#B0A69C",
            "border": "#E6DACE",
            "accent": "#72AF95",
            "accent_hover": "#629E85",
            "accent_pressed": "#558E76",
            "accent_soft": "#E0EFE8",
            "on_accent": "#183229",
            "peach": "#D88C6A",
            "danger": "#B95650",
            "danger_soft": "#F8E5E1",
            "on_danger": "#FFFFFF",
            "overlay": "#403B36",
            "category_1": "#D88C6A",
            "category_2": "#72AF95",
            "category_3": "#8C86B8",
            "category_4": "#D0A75E",
            "category_5": "#6E9FB3",
            "category_6": "#C77D91",
        },
        "dark": {
            "window": "#1D1C1A",
            "sidebar": "#24221F",
            "surface": "#2B2925",
            "surface_alt": "#33302B",
            "surface_hover": "#3B3731",
            "text": "#F2EEE7",
            "muted": "#B3ABA0",
            "faint": "#837C73",
            "border": "#464039",
            "accent": "#8CB69B",
            "accent_hover": "#9AC5A9",
            "accent_pressed": "#789E87",
            "accent_soft": "#35463C",
            "on_accent": "#14271D",
            "peach": "#E09A78",
            "danger": "#DF7C72",
            "danger_soft": "#4A312D",
            "on_danger": "#2B1110",
            "overlay": "#37332E",
            "category_1": "#E09A78",
            "category_2": "#8CB69B",
            "category_3": "#A39BD2",
            "category_4": "#DDB86E",
            "category_5": "#83B2C5",
            "category_6": "#D991A3",
        },
    },
    PALETTE_SKY_BLUE: {
        "light": {
            "window": "#F4F9FD",
            "sidebar": "#EAF4FA",
            "surface": "#FFFFFF",
            "surface_alt": "#EEF6FB",
            "surface_hover": "#E2F0F8",
            "text": "#163246",
            "muted": "#587488",
            "faint": "#9CB1C0",
            "border": "#D2E3ED",
            "accent": "#4B9FD1",
            "accent_hover": "#3B8FC1",
            "accent_pressed": "#2D7EAE",
            "accent_soft": "#DCEFF9",
            "on_accent": "#102E42",
            "peach": "#7188D6",
            "danger": "#B94F5D",
            "danger_soft": "#FBE7EA",
            "on_danger": "#FFFFFF",
            "overlay": "#223746",
            "category_1": "#4B9FD1",
            "category_2": "#7188D6",
            "category_3": "#54AAA7",
            "category_4": "#DCA35B",
            "category_5": "#718FA8",
            "category_6": "#C97FA3",
        },
        "dark": {
            "window": "#101B24",
            "sidebar": "#15232E",
            "surface": "#1B2B36",
            "surface_alt": "#223744",
            "surface_hover": "#2A4555",
            "text": "#EAF5FB",
            "muted": "#A4BBC8",
            "faint": "#6F8795",
            "border": "#324C5C",
            "accent": "#69B9E8",
            "accent_hover": "#7CC6F0",
            "accent_pressed": "#4FA2D3",
            "accent_soft": "#203F50",
            "on_accent": "#0D2A3A",
            "peach": "#8799E8",
            "danger": "#EE7C86",
            "danger_soft": "#4A2931",
            "on_danger": "#2C1015",
            "overlay": "#0B151C",
            "category_1": "#69B9E8",
            "category_2": "#8799E8",
            "category_3": "#69C3BE",
            "category_4": "#E2B36D",
            "category_5": "#8CB1C8",
            "category_6": "#DD92B2",
        },
    },
    PALETTE_ARISTOCRATIC_GREEN: {
        "light": {
            "window": "#F5F8F5",
            "sidebar": "#EAF1EC",
            "surface": "#FFFFFF",
            "surface_alt": "#EFF5F0",
            "surface_hover": "#E3EEE6",
            "text": "#18352A",
            "muted": "#587263",
            "faint": "#9AAF9F",
            "border": "#D4E2D7",
            "accent": "#2F7D5B",
            "accent_hover": "#276E4F",
            "accent_pressed": "#1E5D41",
            "accent_soft": "#DDEEE5",
            "on_accent": "#FFFFFF",
            "peach": "#B08A54",
            "danger": "#B95757",
            "danger_soft": "#F7E5E3",
            "on_danger": "#FFFFFF",
            "overlay": "#20372D",
            "category_1": "#2F7D5B",
            "category_2": "#557662",
            "category_3": "#7C6B98",
            "category_4": "#B08A54",
            "category_5": "#527982",
            "category_6": "#8B5E6E",
        },
        "dark": {
            "window": "#101A15",
            "sidebar": "#16231C",
            "surface": "#1B2C22",
            "surface_alt": "#23372B",
            "surface_hover": "#2C4435",
            "text": "#EDF5EF",
            "muted": "#A8BCAF",
            "faint": "#748A7C",
            "border": "#344D3D",
            "accent": "#62B58A",
            "accent_hover": "#74C79A",
            "accent_pressed": "#4A9B72",
            "accent_soft": "#254737",
            "on_accent": "#10251A",
            "peach": "#C5A46B",
            "danger": "#DF7A78",
            "danger_soft": "#492D2D",
            "on_danger": "#2B1010",
            "overlay": "#0C1510",
            "category_1": "#62B58A",
            "category_2": "#789B83",
            "category_3": "#A194BE",
            "category_4": "#C5A46B",
            "category_5": "#75A0A8",
            "category_6": "#B27D90",
        },
    },
}


def normalize_palette_name(name: str | None) -> str:
    return name if name in PALETTES else DEFAULT_PALETTE


def colors_for(palette_name: str = DEFAULT_PALETTE, dark: bool = False) -> dict[str, str]:
    name = normalize_palette_name(palette_name)
    mode = "dark" if dark else "light"
    return PALETTES[name][mode]


def category_swatches(palette_name: str = DEFAULT_PALETTE, dark: bool = False) -> list[str]:
    colors = colors_for(palette_name, dark)
    return [colors[f"category_{index}"] for index in range(1, 7)]


# Compatibility aliases retained for older imports and external scripts.
LIGHT = PALETTES[DEFAULT_PALETTE]["light"]
DARK = PALETTES[DEFAULT_PALETTE]["dark"]


def palette(dark: bool = False, palette_name: str = DEFAULT_PALETTE) -> QPalette:
    c = colors_for(palette_name, dark)
    result = QPalette()
    result.setColor(QPalette.ColorRole.Window, QColor(c["window"]))
    result.setColor(QPalette.ColorRole.WindowText, QColor(c["text"]))
    result.setColor(QPalette.ColorRole.Base, QColor(c["surface"]))
    result.setColor(QPalette.ColorRole.AlternateBase, QColor(c["surface_alt"]))
    result.setColor(QPalette.ColorRole.Text, QColor(c["text"]))
    result.setColor(QPalette.ColorRole.Button, QColor(c["surface"]))
    result.setColor(QPalette.ColorRole.ButtonText, QColor(c["text"]))
    result.setColor(QPalette.ColorRole.Highlight, QColor(c["accent"]))
    result.setColor(QPalette.ColorRole.HighlightedText, QColor(c["on_accent"]))
    result.setColor(QPalette.ColorRole.PlaceholderText, QColor(c["faint"]))
    return result


def stylesheet(dark: bool = False, palette_name: str = DEFAULT_PALETTE) -> str:
    c = colors_for(palette_name, dark)
    mobile_hover_overrides = ""
    if running_on_android():
        mobile_hover_overrides = f"""
    QPushButton:hover {{ background-color: transparent; }}
    QPushButton#primary:hover {{ background-color: {c['accent']}; }}
    QPushButton#dangerPrimary:hover {{ background-color: {c['danger']}; border: none; color: {c['on_danger']}; }}
    QPushButton#secondary:hover {{ background-color: {c['surface']}; border-color: {c['border']}; }}
    QPushButton#plannerToday:hover {{ background-color: {c['surface']}; border-color: {c['border']}; }}
    QPushButton#mobileNavButton:hover {{ background-color: transparent; color: {c['muted']}; }}
    QPushButton#navButton:hover {{ background-color: transparent; color: {c['muted']}; }}
    QPushButton#segment:hover {{ color: {c['muted']}; background-color: transparent; }}
    QPushButton#segment[active="true"],
    QPushButton#segment[active="true"]:hover,
    QPushButton#segment[active="true"]:pressed {{
        background-color: transparent; color: {c['text']}; font-weight: 650;
        padding: 7px 8px;
    }}
    QPushButton#weekDayHeader:hover {{ background-color: transparent; color: {c['muted']}; }}
    QPushButton#weekDayHeader[today="true"]:hover {{ background-color: transparent; color: {c['text']}; }}
    QPushButton#weekAdd:hover {{ background-color: transparent; color: {c['muted']}; }}
    QPushButton#weekAdd[today="true"]:hover {{ background-color: transparent; color: {c['text']}; }}
    QPushButton#categoryButton:hover {{ background-color: transparent; color: {c['muted']}; }}
    QFrame#taskCard:hover {{ border-color: {c['border']}; background-color: {c['surface']}; }}
    QFrame#calendarCell:hover {{ border-color: {c['border']}; background-color: {c['surface']}; }}
    QFrame#calendarCell[compact="true"]:hover {{ border: none; background: transparent; }}
    QPushButton#monthAgendaAdd:hover, QPushButton#monthAgendaEmptyAdd:hover {{ background: transparent; color: {c['accent']}; }}
    QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QDateEdit:hover, QTimeEdit:hover {{ border-color: {c['border']}; }}
    QListWidget#selectList::item:hover {{ background-color: transparent; }}
    QListWidget#selectList::item:selected:hover {{ background-color: {c['accent_soft']}; }}
    """
    return f"""
    * {{
        font-family: Roboto, "Noto Sans Arabic", "Noto Sans", -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
        color: {c['text']};
        font-size: 13px;
    }}
    QMainWindow, QDialog, QWidget#root {{ background-color: {c['window']}; color: {c['text']}; }}
    QWidget#sidebar {{ background-color: {c['sidebar']}; border-right: 1px solid {c['border']}; }}
    QWidget#sidebar[rtl="true"] {{ border-right: none; border-left: 1px solid {c['border']}; }}
    QWidget#content, QWidget#dialogRoot {{ background-color: {c['window']}; }}

    QLabel {{ background: transparent; color: {c['text']}; }}
    QLabel#brand {{ font-size: 21px; font-weight: 700; letter-spacing: -0.4px; color: {c['text']}; }}
    QLabel#eyebrow {{ color: {c['muted']}; font-size: 11px; font-weight: 650; }}
    QLabel#pageTitle {{ color: {c['text']}; font-size: 30px; font-weight: 700; letter-spacing: -0.8px; }}
    QLabel#pageTitle[compact="true"] {{ font-size: 23px; letter-spacing: -0.4px; }}
    QLabel#dialogTitle {{ color: {c['text']}; font-size: 25px; font-weight: 700; letter-spacing: -0.4px; }}
    QLabel#messageTitle {{ color: {c['text']}; font-size: 20px; font-weight: 700; }}
    QLabel#messageText {{ color: {c['muted']}; font-size: 13px; line-height: 1.35; }}
    QLabel#pageSubtitle, QLabel#muted {{ color: {c['muted']}; }}
    QLabel#sectionTitle {{ color: {c['text']}; font-size: 15px; font-weight: 650; }}
    QLabel#fieldLabel {{ color: {c['text']}; font-size: 13px; font-weight: 600; }}
    QLabel#optionLabel {{ color: {c['text']}; font-size: 13px; }}
    QLabel#optionLabel:disabled, QLabel#fieldLabel:disabled {{ color: {c['faint']}; }}
    QLabel#taskTitle {{ color: {c['text']}; font-size: 14px; font-weight: 620; }}
    QLabel#taskTitleDone {{ color: {c['muted']}; font-size: 14px; text-decoration: line-through; }}
    QLabel#taskMeta {{ color: {c['muted']}; font-size: 11px; }}
    QLabel#taskNotes {{ color: {c['muted']}; font-size: 11px; line-height: 1.25; }}
    QLabel#weekTaskTitle {{ color: {c['text']}; font-size: 13px; font-weight: 650; }}
    QLabel#weekTaskTitleOverdue {{ color: {c['danger']}; font-size: 13px; font-weight: 650; }}
    QLabel#weekEmpty {{ color: {c['faint']}; font-size: 12px; }}
    QLabel#overdue {{ color: {c['danger']}; font-size: 11px; font-weight: 620; }}
    QLabel#countPill {{ background: {c['surface_alt']}; color: {c['muted']}; border-radius: 9px; padding: 1px 7px; font-size: 11px; }}
    QLabel#emptyIcon {{ color: {c['accent']}; font-size: 31px; }}
    QLabel#emptyTitle {{ color: {c['text']}; font-size: 17px; font-weight: 650; }}
    QLabel#calendarDayNumber {{ color: {c['text']}; font-size: 12px; font-weight: 650; }}
    QLabel#calendarDayMuted {{ color: {c['faint']}; font-size: 12px; font-weight: 600; }}
    QLabel#calendarTask {{ background: {c['surface_alt']}; color: {c['muted']}; border-radius: 5px; padding: 2px 5px; font-size: 10px; }}
    QLabel#calendarTaskDot {{ color: {c['accent']}; font-size: 15px; font-weight: 700; }}
    QLabel#monthWeekday {{ color: {c['muted']}; font-size: 11px; font-weight: 620; }}
    QLabel#calendarDayBubble {{
        background: transparent; color: {c['text']}; border: none; border-radius: 17px;
        font-size: 13px; font-weight: 650;
    }}
    QLabel#calendarDayBubble[muted="true"] {{ color: {c['faint']}; }}
    QLabel#calendarDayBubble[today="true"] {{ border: 1px solid {c['accent']}; }}
    QLabel#calendarDayBubble[selected="true"] {{
        background-color: {c['accent']}; color: {c['on_accent']}; border: none; font-weight: 720;
    }}
    QLabel#calendarTaskDots {{ color: {c['accent']}; font-size: 9px; font-weight: 750; letter-spacing: 1px; }}
    QLabel#toastText {{ color: #FFFFFF; font-size: 14px; font-weight: 650; }}
    QLabel#detailTitle {{ color: {c['text']}; font-size: 24px; font-weight: 720; letter-spacing: -0.3px; }}
    QLabel#detailSection {{ color: {c['muted']}; font-size: 10px; font-weight: 700; letter-spacing: 0.7px; }}
    QLabel#detailBody {{ color: {c['text']}; font-size: 13px; line-height: 1.4; }}
    QLabel#detailPlaceholder {{ color: {c['faint']}; font-size: 13px; font-style: italic; }}
    QLabel#detailKey {{ color: {c['muted']}; font-size: 12px; font-weight: 600; }}
    QLabel#detailValue {{ color: {c['text']}; font-size: 13px; }}
    QLabel#detailStatus {{ background-color: {c['accent_soft']}; color: {c['accent']}; border-radius: 9px; padding: 4px 10px; font-size: 11px; font-weight: 650; }}
    QLabel#detailOverdue {{ background-color: {c['danger_soft']}; color: {c['danger']}; border-radius: 9px; padding: 4px 10px; font-size: 11px; font-weight: 650; }}

    QPushButton {{
        border: none; border-radius: 9px; padding: 8px 12px;
        background-color: transparent; color: {c['text']};
        outline: none;
    }}
    QPushButton:focus {{ outline: none; }}
    QPushButton:hover {{ background-color: {c['surface_hover']}; }}
    QPushButton:pressed {{ background-color: {c['border']}; padding-top: 9px; padding-bottom: 7px; }}
    QPushButton:disabled {{ color: {c['faint']}; }}
    QPushButton#primary {{ background-color: {c['accent']}; color: {c['on_accent']}; font-weight: 650; padding: 10px 16px; }}
    QPushButton#primary:hover {{ background-color: {c['accent_hover']}; }}
    QPushButton#primary:pressed {{ background-color: {c['accent_pressed']}; padding-top: 11px; padding-bottom: 9px; }}
    QPushButton#dangerPrimary {{ background-color: {c['danger']}; color: {c['on_danger']}; font-weight: 650; padding: 10px 16px; }}
    QPushButton#dangerPrimary:hover {{ background-color: {c['danger']}; border: 2px solid {c['text']}; }}
    QPushButton#dangerPrimary:pressed {{ background-color: {c['danger_soft']}; color: {c['danger']}; border: 1px solid {c['danger']}; padding-top: 11px; padding-bottom: 9px; }}
    QPushButton#secondary {{ background-color: {c['surface']}; border: 1px solid {c['border']}; font-weight: 600; }}
    QPushButton#secondary:hover {{ background-color: {c['surface_hover']}; border-color: {c['accent']}; }}
    QPushButton#secondary:pressed {{ background-color: {c['accent_soft']}; border-color: {c['accent']}; }}
    QPushButton#dialogAction {{ min-width: 110px; min-height: 40px; max-height: 40px; }}
    QPushButton#navButton {{ text-align: left; padding: 9px 12px; color: {c['muted']}; }}
    QPushButton#navButton:hover {{ background-color: {c['surface_hover']}; color: {c['text']}; }}
    QPushButton#navButton[active="true"] {{ background-color: transparent; color: {c['text']}; font-weight: 650; }}
    QPushButton#navButton[rtl="true"] {{ text-align: right; }}
    QFrame#mobileNav {{ background-color: {c['sidebar']}; border: 1px solid {c['border']}; border-radius: 15px; }}
    QFrame#mobileNavIndicator {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 11px; }}
    QFrame#sidebarNavIndicator {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 10px; }}
    QFrame#plannerNavBar {{ background-color: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 11px; }}
    QPushButton#plannerToday {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 7px 14px; font-weight: 650; }}
    QPushButton#plannerToday:hover {{ background-color: {c['surface_hover']}; border-color: {c['accent']}; }}
    QPushButton#plannerToday:pressed {{ background-color: {c['accent_soft']}; border-color: {c['accent']}; padding: 7px 14px; }}
    QPushButton#plannerToday[touch="true"]:hover {{ background-color: {c['surface']}; border-color: {c['border']}; }}
    QPushButton#mobileNavButton {{ color: {c['muted']}; border-radius: 11px; padding: 27px 4px 5px 4px; font-size: 10px; }}
    QPushButton#mobileNavButton:hover {{ background-color: {c['surface_hover']}; color: {c['text']}; }}
    QPushButton#mobileNavButton[active="true"] {{ background-color: transparent; color: {c['text']}; font-weight: 650; }}
    QPushButton#mobileIconButton {{ background-color: {c['surface']}; border: 1px solid {c['border']}; padding: 0; font-size: 17px; }}
    QAbstractButton#mobileLanguageSelect {{ min-height: 44px; max-height: 44px; }}
    QPushButton#mobileIconButton:pressed {{ background-color: {c['accent_soft']}; padding: 1px 0 0 0; }}
    QPushButton#categoryButton {{ text-align: left; padding: 7px 4px; color: {c['muted']}; }}
    QPushButton#categoryButton[rtl="true"] {{ text-align: right; }}
    QPushButton#categoryButton:hover {{ background-color: transparent; color: {c['text']}; }}
    QPushButton#segment {{ color: {c['muted']}; border-radius: 8px; padding: 7px 16px; font-size: 13px; }}
    QPushButton#segment[compact="true"] {{ padding: 7px 8px; font-size: 13px; }}
    QPushButton#segment:hover {{ color: {c['text']}; background-color: {c['surface_hover']}; }}
    QPushButton#segment[active="true"] {{ background-color: transparent; color: {c['text']}; font-weight: 650; }}
    QPushButton#weekDayHeader {{ min-height: 42px; padding: 6px 7px; font-weight: 650; color: {c['muted']}; text-align: left; }}
    QPushButton#weekDayHeader[rtl="true"] {{ text-align: right; }}
    QPushButton#weekDayHeader:hover {{ background-color: {c['accent_soft']}; color: {c['text']}; }}
    QPushButton#weekDayHeader[today="true"] {{ background-color: transparent; color: {c['text']}; font-weight: 700; }}
    QPushButton#weekAdd {{ color: {c['muted']}; padding: 7px 10px; min-height: 32px; font-weight: 600; }}
    QPushButton#weekAdd:hover {{ background-color: {c['accent_soft']}; color: {c['text']}; }}
    QPushButton#weekAdd[today="true"] {{ background-color: transparent; color: {c['text']}; font-weight: 650; }}
    QPushButton#monthAgendaAdd {{
        color: {c['accent']}; background: transparent; min-height: 34px; padding: 6px 9px; font-weight: 680;
    }}
    QPushButton#monthAgendaAdd:pressed {{ background-color: {c['accent_soft']}; }}
    QPushButton#monthAgendaEmptyAdd {{
        color: {c['accent']}; background: transparent; min-height: 34px; padding: 5px 9px; font-weight: 680;
    }}
    QPushButton#monthAgendaEmptyAdd:pressed {{ background-color: {c['accent_soft']}; }}

    QFrame#card, QFrame#panel, QWidget#card {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 13px; }}
    QFrame#taskCard {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 11px; }}
    QFrame#taskCard:hover {{ border-color: {c['accent']}; background-color: {c['surface']}; }}
    QFrame#taskCard[compact="true"] {{ border-radius: 9px; }}
    QFrame#weekPanel {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 12px; }}
    QFrame#weekPanel[today="true"] {{ border: 1.5px solid {c['accent']}; }}
    QFrame#weekHeaderStrip {{ background: transparent; border: none; }}
    QFrame#weekHeaderStrip[today="true"] {{ background-color: {c['accent_soft']}; border-radius: 10px; }}
    QFrame#segmentBar {{ background-color: {c['surface_alt']}; border-radius: 9px; }}
    QFrame#segmentIndicator {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 8px; }}
    QFrame#divider {{ background-color: {c['border']}; max-height: 1px; }}
    QFrame#calendarCell {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 9px; }}
    QFrame#calendarCell:hover {{ border-color: {c['accent']}; background-color: {c['surface_hover']}; }}
    QFrame#calendarCell[today="true"] {{ border: 2px solid {c['accent']}; }}
    QFrame#calendarCell[muted="true"] {{ background-color: {c['surface_alt']}; }}
    QFrame#calendarCell[compact="true"],
    QFrame#calendarCell[compact="true"][today="true"],
    QFrame#calendarCell[compact="true"][muted="true"] {{
        background: transparent; border: none; border-radius: 22px;
    }}
    QFrame#calendarCell[compact="true"]:pressed {{ background-color: {c['accent_soft']}; }}
    QWidget#monthContent, QWidget#monthCalendar, QWidget#monthAgenda {{ background: transparent; border: none; }}
    QFrame#monthAgendaHeader {{
        background: transparent; border: none; border-top: 1px solid {c['border']};
    }}
    QFrame#monthAgendaEmpty {{
        background-color: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 11px;
    }}
    QWidget#insightsContent {{ background: transparent; border: none; }}
    QFrame#insightHero {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 15px;
    }}
    QLabel#insightHeroTitle {{ color: {c['text']}; font-size: 16px; font-weight: 700; }}
    QLabel#insightHeroSubtitle {{ color: {c['muted']}; font-size: 12px; }}
    QFrame#insightMetricCard {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 14px;
    }}
    QLabel#insightMetricTitle {{ color: {c['muted']}; font-size: 11px; font-weight: 650; }}
    QLabel#insightMetricValue {{ color: {c['text']}; font-size: 25px; font-weight: 750; }}
    QLabel#insightMetricNote {{ color: {c['faint']}; font-size: 10px; }}
    QFrame#insightCard {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 15px;
    }}
    QLabel#insightCardTitle {{ color: {c['text']}; font-size: 14px; font-weight: 700; }}
    QLabel#insightCardMeta {{ color: {c['muted']}; font-size: 10px; }}
    QLabel#insightCenteredNote {{ color: {c['muted']}; font-size: 11px; padding: 2px 0 0 0; }}

    QFrame#toast {{ background-color: {c['overlay']}; border: none; border-radius: 14px; }}
    QFrame#detailPanel {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 12px; }}
    QFrame#detailChip {{ background-color: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 9px; }}
    QFrame#detailChip QLabel {{ color: {c['muted']}; font-size: 11px; font-weight: 620; }}
    QFrame#popupSurface {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 11px; }}
    QListWidget#selectList {{
        background-color: transparent; color: {c['text']}; border: none; outline: 0; padding: 0;
    }}
    QListWidget#selectList::item {{
        border: none; border-radius: 7px; padding: 0 10px; color: {c['text']};
    }}
    QListWidget#selectList::item:hover {{ background-color: {c['surface_hover']}; }}
    QListWidget#selectList::item:selected {{
        background-color: {c['accent_soft']}; color: {c['text']}; font-weight: 620;
    }}
    QScrollArea#popupScroll, QWidget#popupContent {{ background-color: transparent; border: none; }}

    QPushButton#selectOption, QPushButton#popoverAction, QPushButton#popoverDanger {{
        min-height: 34px; text-align: left; border-radius: 7px; padding: 4px 10px;
        background-color: transparent; color: {c['text']};
    }}
    QPushButton#selectOption[rtl="true"], QPushButton#popoverAction[rtl="true"],
    QPushButton#popoverDanger[rtl="true"] {{ text-align: right; }}
    QPushButton#selectOption:hover, QPushButton#popoverAction:hover {{ background-color: {c['surface_hover']}; }}
    QPushButton#selectOption:pressed, QPushButton#popoverAction:pressed {{ background-color: {c['accent_soft']}; padding-top: 5px; padding-bottom: 3px; }}
    QPushButton#selectOption[selected="true"] {{ background-color: {c['accent_soft']}; font-weight: 620; }}
    QPushButton#popoverDanger {{ color: {c['danger']}; font-weight: 620; }}
    QPushButton#popoverDanger:hover {{ background-color: {c['danger_soft']}; }}
    QPushButton#popoverDanger:pressed {{ background-color: {c['danger']}; color: {c['on_danger']}; padding-top: 5px; padding-bottom: 3px; }}

    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateEdit, QTimeEdit {{
        background-color: {c['surface']}; color: {c['text']};
        border: 1px solid {c['border']}; border-radius: 9px;
        min-height: 22px; padding: 9px 11px;
        selection-background-color: {c['accent']}; selection-color: {c['on_accent']};
    }}
    QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QDateEdit:hover, QTimeEdit:hover {{ border-color: {c['faint']}; }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {{ border: 2px solid {c['accent']}; padding: 8px 10px; }}
    QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QTimeEdit:disabled {{ background-color: {c['surface_alt']}; color: {c['faint']}; }}
    QLineEdit#search {{ background-color: {c['surface_alt']}; border: 1px solid transparent; padding-left: 13px; }}
    QLineEdit#search[rtlInput="true"] {{ padding-left: 32px; padding-right: 13px; }}
    QLineEdit#search:focus {{ border: 1px solid {c['accent']}; }}
    QLineEdit#search[rtlInput="true"]:focus {{ padding-left: 31px; padding-right: 12px; }}
    QTextEdit {{ padding: 11px 12px; }}

    QComboBox {{ min-width: 190px; padding-right: 32px; }}
    QComboBox::drop-down, QDateEdit::drop-down {{ border: none; background: transparent; width: 30px; }}
    QComboBox::down-arrow, QDateEdit::down-arrow {{ width: 9px; height: 9px; }}
    QComboBox QAbstractItemView {{
        background-color: {c['surface']}; color: {c['text']};
        border: 1px solid {c['border']}; border-radius: 9px;
        padding: 6px; outline: 0; selection-background-color: {c['accent_soft']};
        selection-color: {c['text']};
    }}
    QComboBox QAbstractItemView::item {{ min-height: 30px; padding: 4px 9px; border-radius: 6px; }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QScrollBar:vertical {{ width: 7px; background: transparent; margin: 3px 1px; }}
    QScrollBar::handle:vertical {{ background: {c['border']}; border-radius: 3px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {c['faint']}; }}
    QScrollBar:horizontal {{ height: 0px; background: transparent; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}

    QMenu {{ background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 9px; padding: 6px; }}
    QMenu::separator {{ height: 1px; background: {c['border']}; margin: 5px 7px; }}
    QMenu::item {{ border-radius: 6px; padding: 8px 26px 8px 11px; }}
    QMenu::item:selected {{ background-color: {c['accent_soft']}; color: {c['text']}; }}
    QToolTip {{ background-color: {c['text']}; color: {c['surface']}; border: none; border-radius: 5px; padding: 5px 7px; }}

    QCalendarWidget QWidget {{ background-color: {c['surface']}; color: {c['text']}; alternate-background-color: {c['surface_alt']}; }}
    QCalendarWidget QAbstractItemView:enabled {{ background-color: {c['surface']}; color: {c['text']}; selection-background-color: {c['accent']}; selection-color: {c['on_accent']}; }}

    QWidget#persistentHeader {{ background: transparent; border: none; }}
    QDialog#taskComposerDialog {{ background: transparent; }}
    QFrame#managedDialogPage, QFrame#taskComposerSheet, QFrame#templatePreview,
    QWidget#templateLibrary, QWidget#taskEditPage, QWidget#dialogRoot, QWidget#settingsPage {{
        background-color: {c['surface']}; border: 1px solid {c['border']};
        border-radius: 15px;
    }}
    QLabel#dialogTitleCompact, QLabel#composerHeaderTitle {{
        color: {c['text']}; font-size: 17px; font-weight: 740;
    }}
    QScrollArea#settingsScroll, QWidget#settingsBody {{ background: transparent; border: none; }}
    QFrame#settingsSection {{
        background-color: {c['surface_alt']}; border: 1px solid {c['border']}; border-radius: 13px;
    }}
    QLabel#settingsSectionTitle {{ color: {c['text']}; font-size: 14px; font-weight: 700; }}
    QLabel#settingsHint {{ color: {c['muted']}; font-size: 12px; }}
    QFrame#settingsCategoryRow {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 10px;
    }}
    QLabel#settingsCategoryName {{ color: {c['text']}; font-size: 14px; font-weight: 620; }}
    QPushButton#settingsAction {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 10px;
        text-align: left; padding: 10px 13px; font-weight: 620;
    }}
    QPushButton#settingsAction:pressed {{ background-color: {c['accent_soft']}; border-color: {c['accent']}; }}
    QLabel#paletteLabel {{ color: {c['muted']}; font-size: 12px; font-weight: 650; margin-top: 2px; }}
    QLabel#palettePreview {{
        background-color: {c['accent_soft']}; color: {c['accent']};
        border: 1px solid {c['accent']}; border-radius: 9px;
        padding: 7px 10px; font-size: 12px; font-weight: 650;
    }}
    QFrame#taskComposerSheet {{ background-color: {c['surface']}; }}
    QLineEdit#composerTitle {{
        background-color: {c['surface_alt']}; border: 1px solid transparent;
        border-radius: 13px; font-size: 17px; padding: 12px 14px;
    }}
    QLineEdit#composerTitle:focus {{ border: 2px solid {c['accent']}; padding: 11px 13px; }}
    QScrollArea#composerSubtasks {{ background: transparent; border: none; }}
    QScrollArea#composerSubtasks > QWidget > QWidget {{ background: transparent; }}
    QFrame#subtaskEditorRow {{ background: transparent; border: none; }}
    QLabel#subtaskMarker {{ color: {c['faint']}; font-size: 22px; }}
    QLineEdit#subtaskInput {{ background: transparent; border: none; border-bottom: 1px solid {c['border']}; border-radius: 0; padding: 7px 4px; }}
    QLineEdit#subtaskInput:focus {{ border: none; border-bottom: 2px solid {c['accent']}; padding: 7px 4px 6px 4px; }}
    QPushButton#subtaskRemove {{ background: transparent; color: {c['faint']}; border: none; border-radius: 18px; font-size: 21px; }}
    QPushButton#subtaskRemove:pressed {{ background-color: {c['surface_hover']}; color: {c['text']}; }}
    QPushButton#composerNotesToggle {{ background: transparent; color: {c['accent']}; padding: 4px 2px; text-align: left; font-weight: 600; }}
    QTextEdit#composerNotes {{ background-color: {c['surface_alt']}; border: 1px solid transparent; border-radius: 11px; padding: 8px 10px; }}
    QTextEdit#composerNotes:focus {{ border: 1px solid {c['accent']}; }}
    QLabel#composerScheduleSummary {{ color: {c['muted']}; padding: 2px 5px; font-size: 12px; }}

    QFrame#scheduleSheet {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 15px;
    }}
    QLabel#scheduleMonthTitle {{ font-size: 16px; font-weight: 700; }}
    QLabel#calendarWeekday {{ color: {c['muted']}; font-weight: 650; font-size: 12px; }}
    QPushButton#scheduleDay {{ background: transparent; border: none; border-radius: 18px; padding: 0; }}
    QPushButton#scheduleDay[outsideMonth="true"] {{ color: {c['faint']}; }}
    QPushButton#scheduleDay[today="true"] {{ border: 1px solid {c['accent']}; }}
    QPushButton#scheduleDay[selected="true"] {{ background-color: {c['accent']}; color: {c['on_accent']}; font-weight: 700; border: none; }}
    QPushButton#scheduleQuick {{ background-color: {c['surface_alt']}; color: {c['muted']}; border: 1px solid transparent; border-radius: 8px; padding: 8px 10px; }}
    QPushButton#scheduleQuick:pressed {{ background-color: {c['accent_soft']}; color: {c['text']}; }}
    QFrame#scheduleSeparator {{ background-color: {c['border']}; border: none; }}
    QLabel#scheduleRowLabel {{ font-size: 15px; font-weight: 620; }}

    QLabel#templateGroup {{ color: {c['muted']}; font-size: 12px; font-weight: 700; padding: 10px 3px 3px 3px; }}
    QPushButton#templateCard {{
        background-color: {c['surface_alt']}; border: 1px solid transparent; border-radius: 11px;
        text-align: left; padding: 10px 14px; font-size: 14px;
    }}
    QPushButton#templateCard:pressed {{ background-color: {c['accent_soft']}; border-color: {c['accent']}; }}
    QLabel#templateHeroEmoji {{ font-size: 64px; padding: 8px; }}
    QLineEdit#templateTitleInput {{ font-size: 18px; font-weight: 700; background-color: {c['surface_alt']}; border: 1px solid transparent; }}
    QLabel#templateDescription {{ color: {c['muted']}; font-size: 14px; line-height: 1.35; }}
    QPushButton#templateAddSubtask {{ background: transparent; color: {c['accent']}; text-align: left; padding: 8px; font-weight: 650; }}


    QScrollArea#categoryChipScroll, QWidget#categoryChipHost {{
        background: transparent; border: none;
    }}
    QPushButton#categoryChip {{
        background-color: {c['surface_alt']}; color: {c['muted']};
        border: 1px solid transparent; border-radius: 19px;
        padding: 7px 16px; font-size: 13px; font-weight: 620;
    }}
    QPushButton#categoryChip:pressed {{ background-color: {c['accent_soft']}; color: {c['text']}; }}
    QPushButton#categoryChip[active="true"] {{
        background-color: {c['accent']}; color: {c['on_accent']}; border-color: {c['accent']}; font-weight: 700;
    }}
    QPushButton#categoryAddChip {{
        background-color: {c['surface_alt']}; color: {c['accent']};
        border: 1px solid {c['border']}; border-radius: 19px; font-size: 20px; font-weight: 600;
        padding: 0;
    }}
    QPushButton#categoryAddChip:pressed {{ background-color: {c['accent_soft']}; }}

    QFrame#taskCardHost {{ background-color: {c['surface']}; border: none; border-radius: 13px; }}
    QFrame#swipeActions {{ background: transparent; border: none; border-radius: 13px; }}
    QFrame#taskCardSurface {{
        background-color: {c['surface']}; border: 1px solid {c['border']}; border-radius: 13px;
    }}

    QWidget#taskEditContent {{ background-color: {c['surface']}; border: none; }}
    QPushButton#editTaskDone {{
        background: transparent; color: {c['accent']}; font-weight: 750; padding: 8px 10px;
    }}
    QAbstractButton#taskEditCategory {{ min-width: 150px; max-width: 220px; }}
    QLineEdit#taskEditTitle {{
        background: transparent; border: none; border-radius: 0;
        padding: 8px 5px; font-size: 30px; font-weight: 760;
    }}
    QLineEdit#taskEditTitle:focus {{ border: none; padding: 8px 5px; }}
    QPushButton#taskEditAddSubtask {{
        background: transparent; color: {c['accent']}; text-align: left;
        padding: 10px 4px; font-size: 15px; font-weight: 650;
    }}
    QPushButton#taskEditRow, QFrame#taskEditRow {{
        background: transparent; border: none; border-bottom: 1px solid {c['border']};
        border-radius: 0; padding: 0;
    }}
    QPushButton#taskEditRow:pressed {{ background-color: {c['surface_hover']}; }}
    QLabel#taskEditRowLabel {{ color: {c['muted']}; font-size: 16px; font-weight: 590; }}
    QLabel#taskEditRowValue {{ color: {c['muted']}; font-size: 13px; }}
    QLabel#taskEditChevron {{ color: {c['faint']}; font-size: 24px; }}
    QTextEdit#taskEditNotes {{
        background-color: {c['surface_alt']}; border: 1px solid transparent; border-radius: 11px;
    }}

    {mobile_hover_overrides}
    """
