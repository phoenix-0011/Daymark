# ADR-0002: Modular Monolith

- وضعیت: Accepted
- تاریخ: 2026-07-30

## زمینه

محصول یک برنامه محلی Android است و Microservice یا Client-server برای آن پیچیدگی غیرضروری ایجاد می‌کند.

## تصمیم

برنامه به‌صورت یک Process و یک Package اصلی اجرا می‌شود، اما مسئولیت‌ها به لایه‌های Presentation، Domain/Application و Persistence تقسیم شده‌اند.

## قواعد

- UI نباید SQL مستقیم اجرا کند.
- مدل‌ها و قواعد Recurrence مستقل از View باشند.
- SQLite از طریق `Database` در دسترس باشد.
- رفتارهای Platform-specific در Adapter یا ماژول محدود قرار گیرند.

## پیامدها

- Build و Debug ساده‌تر است.
- مرز ماژول‌ها باید با Code Review و تست حفظ شود.
- رشد بسیار بزرگ محصول ممکن است نیازمند بازنگری معماری باشد.
