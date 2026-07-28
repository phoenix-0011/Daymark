from __future__ import annotations

from datetime import date

# Compact, dependency-free conversion used only at the presentation boundary.
# Dates remain Gregorian in SQLite so sorting, reminders and recurrence remain stable.

def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        355666
        + 365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        + gd
    )
    for index in range(gm - 1):
        days += g_days_in_month[index]
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += (jm - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_lengths = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in month_lengths:
        if gd <= length:
            break
        gd -= length
        gm += 1
    return gy, gm, gd


def to_jalali(value: date) -> tuple[int, int, int]:
    return gregorian_to_jalali(value.year, value.month, value.day)


def from_jalali(year: int, month: int, day: int) -> date:
    gy, gm, gd = jalali_to_gregorian(year, month, day)
    return date(gy, gm, gd)


def is_jalali_leap(year: int) -> bool:
    start = from_jalali(year, 1, 1)
    following = from_jalali(year + 1, 1, 1)
    return (following - start).days == 366


def jalali_month_length(year: int, month: int) -> int:
    if 1 <= month <= 6:
        return 31
    if 7 <= month <= 11:
        return 30
    if month == 12:
        return 30 if is_jalali_leap(year) else 29
    raise ValueError("month must be in 1..12")


def add_jalali_month(value: date, amount: int) -> date:
    jy, jm, jd = to_jalali(value)
    absolute = jy * 12 + (jm - 1) + amount
    target_year, month_index = divmod(absolute, 12)
    target_month = month_index + 1
    target_day = min(jd, jalali_month_length(target_year, target_month))
    return from_jalali(target_year, target_month, target_day)
