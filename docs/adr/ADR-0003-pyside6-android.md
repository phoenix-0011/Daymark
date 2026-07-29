# ADR-0003: PySide6/Qt برای Android

- وضعیت: Accepted with constraints
- تاریخ: 2026-07-30

## زمینه

تیم به Python و Qt مسلط است و هدف، ارائه یک برنامه Android با رابط غنی و منطق قابل تست است.

## تصمیم

رابط با PySide6/Qt Widgets پیاده‌سازی و APK با ابزارهای PySide6 Android Deploy، Buildozer و python-for-android ساخته می‌شود.

## محدودیت‌ها

- Toolchain ساخت پیچیده‌تر از Android Native است.
- Build به Python 3.11، JDK 17، SDK/NDK و Wheelهای سازگار وابسته است.
- رفتار Keyboard، Back، Scroll و Lifecycle باید روی دستگاه واقعی تست شود.
- APK Debug برای ارائه مناسب است اما Production Release نیازمند Signing و فرآیند انتشار رسمی است.

## کنترل‌ها

- Build script نسخه ابزارها را Pin می‌کند.
- APK با ابزار Verify بررسی می‌شود.
- UAT دستگاه واقعی بخشی از Exit Criteria است.
