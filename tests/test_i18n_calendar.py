from datetime import date

from daymark.calendar_utils import (
    from_jalali,
    gregorian_to_jalali,
    jalali_month_length,
    to_jalali,
)
from daymark.formatting import month_names
from daymark.i18n import is_rtl, language, language_items, localize_digits, set_language, t


def test_calendar_conversion_library_roundtrip():
    # The conversion utility remains harmless internal code, but Persian is no
    # longer exposed as an application language.
    assert gregorian_to_jalali(2024, 3, 20) == (1403, 1, 1)
    for value in (date(2000, 1, 1), date(2024, 3, 20), date(2026, 7, 23)):
        assert from_jalali(*to_jalali(value)) == value


def test_jalali_month_lengths_utility():
    assert [jalali_month_length(1403, month) for month in range(1, 7)] == [31] * 6
    assert [jalali_month_length(1403, month) for month in range(7, 12)] == [30] * 5
    assert jalali_month_length(1403, 12) == 30
    assert jalali_month_length(1404, 12) == 29


def test_only_english_and_turkish_are_available():
    assert language_items() == [("English", "en"), ("Türkçe", "tr")]
    set_language("fa")
    assert language() == "en"
    assert not is_rtl()
    assert localize_digits(1405) == "1405"
    assert month_names()[0] == "January"

    set_language("tr")
    assert language() == "tr"
    assert not is_rtl()
    assert t("today") == "Bugün"
    assert month_names()[0] == "Ocak"
    set_language("en")


def test_persian_runtime_hooks_are_removed():
    import inspect
    from daymark import i18n

    source = inspect.getsource(i18n)
    assert '"fa"' not in source
    assert "QTextEdit" not in source
    assert "eventFilter" not in source
