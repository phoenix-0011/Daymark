# راهنمای کاربر Daymark

## نصب

1. فایل APK را از GitHub Releases دریافت کنید.
2. فایل را روی دستگاه Android باز کنید.
3. در صورت نیاز، اجازه نصب از همان منبع را فعال کنید.
4. برنامه را نصب و اجرا کنید.

> نسخه دانشگاهی فعلی خارج از Google Play و به‌صورت Debug منتشر شده است؛ نمایش هشدار امنیتی هنگام نصب مستقیم ممکن است.

## ایجاد وظیفه

- دکمه `+` را بزنید.
- عنوان وظیفه را وارد کنید.
- در صورت نیاز زیرکار، یادداشت، Category و Schedule اضافه کنید.
- گزینه Add/Save را بزنید.

عنوان خالی یا فقط شامل Space نباید ذخیره شود.

## زمان‌بندی

در Schedule می‌توان تاریخ، زمان، Reminder و Repeat را تعیین کرد. با حذف Date، Time، Reminder و Recurrence وابسته نیز پاک می‌شوند.

## وظایف تکرارشونده

حالت‌های فعلی:

- Every day
- Every weekday
- Every week
- Every month

با تکمیل Task تکرارشونده، رخداد بعدی ساخته می‌شود. Restore باید رخداد تولیدشده متناظر را بدون حذف Task دستی مشابه مدیریت کند.

## Category، Search و Filter

- Categoryها از Settings مدیریت می‌شوند.
- حذف Category نباید Taskهای آن را حذف کند.
- Search عنوان، Note و متن Subtask را بررسی می‌کند.

## Planner

- Day: برنامه یک روز
- Week: هفت روز به‌صورت مناسب موبایل
- Month: تقویم ماهانه و دسترسی به Agenda روز

## History

Task کامل‌شده به History منتقل می‌شود. Restore آن را به فهرست فعال بازمی‌گرداند.

## Mine/Insights

این بخش آمار تکمیل، Streak و Heatmap را نمایش می‌دهد. هدف آن ارائه بازخورد است، نه ایجاد فشار یا قضاوت درباره کاربر.

## Settings

- Language: English یا Turkish
- Appearance: Light یا Dark
- Palette: Warm Sage، Sky Blue یا Aristocratic Green
- Categories

## داده و حریم خصوصی

اطلاعات در SQLite محلی ذخیره می‌شود و قابلیت اصلی به اینترنت نیاز ندارد. برای حذف کامل داده می‌توان Storage برنامه را پاک یا برنامه را Uninstall کرد.

## محدودیت Reminder

در نسخه فعلی، Reminder درون‌برنامه‌ای هنگام اجرای Daymark بررسی می‌شود. سرویس اعلان پس‌زمینه Store-ready در دامنه فعلی نیست.

## رفع مشکل

- برنامه باز نمی‌شود: نسخه Android و معماری ARM64 را بررسی کنید.
- Keyboard یا Back رفتار نادرست دارد: Build و مدل دستگاه را همراه Screenshot گزارش کنید.
- داده پس از Upgrade مشکل دارد: قبل از ادامه، از Database موجود Backup بگیرید و Migration را گزارش کنید.
