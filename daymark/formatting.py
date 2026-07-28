from __future__ import annotations

from datetime import date, datetime, time

from .i18n import language, localize_digits

_GREGORIAN_MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "tr": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
}
_GREGORIAN_MONTHS_SHORT = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "tr": ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
}
_WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "tr": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"],
}
_WEEKDAYS_SHORT = {
    "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "tr": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
}


def month_names() -> list[str]:
    return list(_GREGORIAN_MONTHS[language()])


def weekday_name(value: date, short: bool = False) -> str:
    table = _WEEKDAYS_SHORT if short else _WEEKDAYS
    return table[language()][value.weekday()]


def month_name(value: date, short: bool = False) -> str:
    table = _GREGORIAN_MONTHS_SHORT if short else _GREGORIAN_MONTHS
    return table[language()][value.month - 1]


def display_ymd(value: date) -> tuple[int, int, int]:
    return value.year, value.month, value.day


def format_time_12(value: time | None, fallback: str = "—") -> str:
    if value is None:
        return fallback
    text = value.strftime("%I:%M %p").lstrip("0")
    return localize_digits(text)


def format_date_short(value: date) -> str:
    number = localize_digits(value.day)
    if language() == "en":
        return f"{weekday_name(value, short=True)}, {month_name(value, short=True)} {number}"
    return f"{weekday_name(value, short=True)}, {number} {month_name(value, short=True)}"


def format_date_medium(value: date) -> str:
    number = localize_digits(value.day)
    if language() == "en":
        return f"{weekday_name(value)}, {month_name(value)} {number}"
    return f"{weekday_name(value)}, {number} {month_name(value)}"


def format_date_full(value: date) -> str:
    number, year_text = localize_digits(value.day), localize_digits(value.year)
    if language() == "en":
        return f"{weekday_name(value)}, {month_name(value)} {number}, {year_text}"
    return f"{weekday_name(value)}, {number} {month_name(value)} {year_text}"


def format_month_day(value: date, short_month: bool = False) -> str:
    number = localize_digits(value.day)
    return f"{month_name(value, short_month)} {number}" if language() == "en" else f"{number} {month_name(value, short_month)}"


def format_month_year(value: date) -> str:
    return f"{month_name(value)} {localize_digits(value.year)}"


def format_week_header(value: date, vertical: bool) -> str:
    number = localize_digits(value.day)
    if vertical:
        date_part = f"{month_name(value, short=True)} {number}" if language() == "en" else f"{number} {month_name(value, short=True)}"
        return f"{weekday_name(value)}  ·  {date_part}"
    return f"{weekday_name(value, short=True)}\n{number}"


def format_week_range(start: date, end: date) -> str:
    sday, eday, eyear = localize_digits(start.day), localize_digits(end.day), localize_digits(end.year)
    if start.year == end.year and start.month == end.month:
        if language() == "en":
            return f"{month_name(start)} {sday}–{eday}, {eyear}"
        return f"{sday}–{eday} {month_name(start)}, {eyear}"
    if language() == "en":
        return f"{month_name(start, True)} {sday} – {month_name(end, True)} {eday}, {eyear}"
    return f"{sday} {month_name(start, True)} – {eday} {month_name(end, True)}, {eyear}"


def format_datetime_brief(value: datetime | None, fallback: str = "—") -> str:
    if value is None:
        return fallback
    day_text, year_text = localize_digits(value.day), localize_digits(value.year)
    if language() == "en":
        date_text = f"{month_name(value.date(), True)} {day_text}, {year_text}"
    else:
        date_text = f"{day_text} {month_name(value.date(), True)} {year_text}"
    return f"{date_text} · {format_time_12(value.time())}"
