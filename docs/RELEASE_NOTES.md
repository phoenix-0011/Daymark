# Release Notes — Unreleased University Completion Update

## کیفیت و تست

- ۴۲ تست خودکار، بدون Failure
- Coverage هسته غیرگرافیکی با Branch Coverage برابر ۹۲٪
- Migration قدیمی با Fixture واقعی تست شد
- Checklistهای UAT و Release اضافه شدند

## اصلاح مهم

Migration دیتابیس اکنون ستون `generated_from_id` را پیش از ساخت Index مربوط تضمین می‌کند. این اصلاح از Crash هنگام بازکردن بعضی Databaseهای قدیمی جلوگیری می‌کند.

## مستندات و همکاری

- CI
- CONTRIBUTING
- PR و Issue Template
- Privacy و Security
- User Guide
- ADR
- Presentation/Demo plan

## محدودیت

این بسته به‌تنهایی UAT دستگاه واقعی یا Production Signing را اثبات نمی‌کند. این موارد باید برای APK نهایی ثبت شوند.
