# گزارش کنترل امنیت و حریم خصوصی

## بررسی‌های واقعی انجام‌شده

- جست‌وجوی سورس برای کتابخانه‌ها و APIهای Network: مسیر ارسال داده کاربر در Runtime فعلی مشاهده نشد.
- تست Rollback برای Update ناموجود و جلوگیری از Subtask orphan پاس شد.
- Queryهای اصلی Database با Placeholder پارامتری اجرا می‌شوند.
- `.gitignore` برای Database، APK، Log، Key و Keystore کامل شد.
- Migration دیتابیس قدیمی با Fixture واقعی تست و یک اشکال ترتیب ساخت Index اصلاح شد.

## بررسی‌های خودکار اضافه‌شده

- Secret pattern scan وابستگی‌ندار
- ممنوعیت Artifactهای حساس در Repository
- Bandit در CI به‌صورت Advisory
- pip-audit در CI به‌صورت Advisory
- Compile و AST parse

## مواردی که هنوز نیازمند Evidence Release هستند

- Permissionهای APK نهایی
- امضای Production
- Dependency Audit همان روز Release
- بررسی Logcat روی دستگاه
- تست پاک‌کردن کامل داده
- تست Android Backup policy

## نتیجه

وضعیت امنیت برای پروژه دانشگاهی قابل دفاع است، اما نباید «ممیزی امنیتی مستقل» یا «Production hardened» ادعا شود.
