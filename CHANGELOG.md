# Changelog

تمام تغییرات مهم پروژه در این فایل ثبت می‌شوند.

## Unreleased

### Added

- GitHub Actions CI برای Compile، تست، Coverage و بررسی‌های کیفیت
- ۹ تست Core جدید؛ مجموع تست‌های خودکار از ۳۳ به ۴۲ رسید
- Coverage هسته غیرگرافیکی با Branch Coverage برابر ۹۲٪
- Test Caseهای رسمی، گزارش اجرا و ماتریس ردیابی
- راهنمای مشارکت، Privacy، Security، User Guide، ADR و Checklistهای UAT/Release
- Screenshotهای واقعی برنامه در مستندات

### Fixed

- اصلاح Migration دیتابیس قدیمی: Index مربوط به `generated_from_id` اکنون پس از اطمینان از وجود ستون ساخته می‌شود. پیش از این، بازکردن بعضی Databaseهای قدیمی می‌توانست با `sqlite3.OperationalError` متوقف شود.

### Changed

- ساختار مستندات برای تیم شش‌نفره و Android-only یکپارچه شد.
- خروجی‌های Build، Database، Log و Signing Material در `.gitignore` کامل‌تر شدند.

## v1.0.0

- نسخه دانشگاهی اولیه Android
- انتشار Debug APK برای ارائه و آزمایش
