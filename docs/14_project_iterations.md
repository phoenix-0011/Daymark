# بازسازی واقع‌گرایانه Iterationهای توسعه

> این سند از روی سورس، اسناد تغییرات، Testها و خروجی‌های موجود بازسازی شده است. این متن ادعا نمی‌کند که تمام مراسم Scrum در زمان توسعه واقعاً ثبت شده‌اند؛ بلکه برای ردیابی دانشگاهی، روند فنی قابل مشاهده را به Iterationهای منطقی تبدیل می‌کند.

## Iteration 1 — هسته و Persistence

### هدف

ایجاد مدل Task، Category و Subtask و ذخیره پایدار در SQLite.

### خروجی قابل مشاهده

- `models.py`
- `database.py`
- `recurrence.py`
- CRUD، Complete، Restore و Search
- Testهای اولیه Database و Recurrence

### مسئولان اصلی

علی ابراهیمی نیا و علی رضا زاده

## Iteration 2 — رابط اصلی وظایف

### هدف

پیاده‌سازی Tasks، History، فرم ایجاد/ویرایش، Category و تعامل‌های اصلی.

### خروجی قابل مشاهده

- `dialogs.py`
- `widgets.py`
- بخش‌های Tasks و History در `views.py`
- Task Composer و Swipe actions

### مسئولان اصلی

امیرحسین رابعی و مجتبی محمودی، با هماهنگی معماری

## Iteration 3 — Planner، Settings و Insights

### هدف

تکمیل Day/Week/Month، Settings، Theme/Palette و Mine.

### خروجی قابل مشاهده

- Planner در `views.py`
- `insights.py` و `analytics.py`
- `theme.py` و Palette System
- English/Turkish UI

### مسئولان اصلی

مهدی ابراهیم زاده و مهدی نریمانی، با همکاری علی ابراهیمی نیا

## Iteration 4 — پایداری Android

### هدف

رفع مشکلات Keyboard، Back، Scroll، Geometry، Animation و Build.

### Evidence موجود

- `SCHEDULE_VERTICAL_LOCK_FIX.md`
- `SCHEDULE_SELECTION_STABILITY_FIX.md`
- `COMPOSER_LAYOUT_STABILITY_FIX.md`
- `STABILITY_SMOOTHNESS_PASS.md`
- Testهای Static Regression در `tests/test_stability_pass.py`
- Build scripts و APK verifier

## Iteration 5 — QA، مستندات و انتشار دانشگاهی

### هدف

تکمیل اسناد، Test Case، RTM، Coverage، GitHub Release و ارائه.

### خروجی

- مستندات `01` تا `20`
- ۴۲ تست خودکار
- Coverage هسته با Branch Coverage برابر ۹۲٪
- CI Workflow
- User Guide، Privacy، Security، ADR و Release/UAT Checklist
- Release دانشگاهی Debug APK

## Retro صادقانه

### نقاط مثبت

- منطق Core از UI جدا و قابل تست است.
- Regressionهای Android به Testهای Source-level تبدیل شده‌اند.
- پایگاه داده از Transaction و Foreign Key استفاده می‌کند.

### مشکلات

- تاریخچه اولیه پروژه PR و Branch Evidence کافی ندارد.
- Testهای واقعی دستگاه به‌طور کامل در Repository ثبت نشده‌اند.
- Toolchain Android پیچیده و وابسته به محیط است.

### اقدام اصلاحی

- تغییرات بعدی فقط از طریق Feature Branch و PR انجام شوند.
- CI روی Push و PR اجرا شود.
- UAT و Release Checklist برای هر Build تکمیل شوند.
- Evidence شامل Screenshot، Log پاک‌سازی‌شده و Commit SHA باشد.
