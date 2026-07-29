# برنامه ارائه و Demo دانشگاهی

## زمان پیشنهادی

۸ تا ۱۰ دقیقه ارائه و ۳ تا ۵ دقیقه پرسش‌وپاسخ.

## ترتیب ارائه

### 1. مسئله و هدف — 45 ثانیه

مدیریت وظایف آفلاین، ساده و قابل استفاده روی Android بدون نیاز به حساب ابری.

### 2. تیم و تقسیم مسئولیت — 45 ثانیه

معرفی شش عضو و نقش‌های معماری، UI، UX و Database.

### 3. نیازمندی‌ها — 60 ثانیه

Task CRUD، Subtask، Schedule، Recurrence، Planner، History، Insights، Theme و Persistence.

### 4. معماری — 75 ثانیه

Modular Monolith با سه ناحیه Presentation، Domain و Persistence. نمایش Component و ER Diagram.

### 5. Demo — 3 تا 4 دقیقه

1. اجرای برنامه
2. ایجاد Task با Subtask و Category
3. تنظیم Date، Time و Repeat
4. مشاهده Task در Planner
5. Complete و مشاهده History
6. Restore
7. Search و Filter
8. تغییر Dark/Light و Palette
9. نمایش Mine/Insights

### 6. تست و کیفیت — 75 ثانیه

- ۴۲ تست خودکار پاس
- Coverage هسته با Branch Coverage برابر ۹۲٪
- ۳۱ Test Case رسمی
- RTM
- CI
- اشاره صادقانه به UATهای دستگاهی باقی‌مانده

### 7. امنیت و حریم خصوصی — 45 ثانیه

SQLite محلی، نبود حساب و Server، Query پارامتری، Transaction و نبود Network path در اجرای عادی.

### 8. Build و Release — 45 ثانیه

PySide6، Buildozer، APK ARM64 و GitHub Releases. نسخه فعلی Debug و دانشگاهی است.

### 9. محدودیت و آینده — 45 ثانیه

- Background Notification
- Backup/Export
- Store-signed Release
- تکمیل Test Matrix روی چند دستگاه
- افزایش UI automation

## Checklist قبل از Demo

- گوشی شارژ و Airplane Mode اختیاری برای اثبات Offline بودن
- APK همان Commit نصب‌شده
- داده نمونه از قبل آماده
- Keyboard و Back یک‌بار آزمایش شده
- Screen recording یا تصاویر پشتیبان
- Repository، Release و Test Report در Tabهای آماده
- اطلاعات شخصی و Notificationهای گوشی مخفی

## پاسخ کوتاه به سؤال‌های محتمل

**چرا SQLite؟** چون برنامه Local-first و تک‌کاربره است و Transaction و Query محلی نیاز دارد.

**چرا Microservice نیست؟** سرور وجود ندارد و Microservice پیچیدگی بدون ارزش ایجاد می‌کند.

**همه تست‌ها پاس‌اند؟** ۴۲ تست خودکار پاس‌اند؛ Testهای دستگاه واقعی در Checklist جداگانه ثبت می‌شوند و نباید بدون Evidence پاس اعلام شوند.

**آیا Production-ready است؟** نسخه دانشگاهی پایدار و قابل ارائه است، اما Production Release به Signing، Store pipeline و UAT گسترده‌تر نیاز دارد.
