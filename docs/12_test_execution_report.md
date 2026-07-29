# گزارش اجرای تست Daymark

> **Test Cycle:** TC-2026-07-30-01  
> **تاریخ اجرا:** 2026-07-30  
> **کد بررسی‌شده:** محتوای `Daymark_Android_palette_system.zip`  
> **نوع اجرا:** Automated Unit، Integration و Static Regression  
> **وضعیت کلی:** مشروط؛ تست‌های خودکار موفق، UAT دستگاه واقعی ناقص

## 1. محیط اجرای خودکار

| مورد | مقدار |
|---|---|
| سیستم عامل | Linux AMD64 |
| Python | 3.13.5 |
| pytest | 9.0.2 |
| Coverage.py | 7.13.3 |
| تعداد تست جمع‌آوری‌شده | 42 |
| زمان اجرای ثبت‌شده | حدود 0.15 ثانیه |
| نتیجه | 42 PASS، 0 FAIL، 0 SKIP |

> نسخه هدف پروژه Python 3.11 است. تکرار اجرای خودکار در Python 3.11 پیش از Release نهایی لازم است.

## 2. دستورهای اجرا

```bash
cd Daymark_Android_palette_system
PYTHONPATH=. python -m pytest -v
```

Coverage:

```bash
PYTHONPATH=. python -m coverage run --source=daymark -m pytest -q
python -m coverage report -m
```

## 3. نتیجه اجرای خودکار

```text
collected 42 items
42 passed
0 failed
0 skipped
```

گروه‌های پاس‌شده:

- Analytics و Streak
- Recurrence و Month-end
- Database CRUD، Complete، Restore و Search
- Idempotency
- Reminder state
- Subtask persistence
- Quick Actions
- Calendar و Language
- Palette completeness و Contrast
- Static Regressionهای Stability، Geometry، Animation و Scroll

## 4. Coverage واقعی

Coverage با `branch = true` و حذف ماژول‌های کاملاً گرافیکی از Gate اندازه‌گیری شد. این عدد فقط هسته غیرگرافیکی را ارزیابی می‌کند.

| ماژول | Coverage |
|---|---:|
| `analytics.py` | 93% |
| `calendar_utils.py` | 91% |
| `database.py` | 92% |
| `device.py` | 89% |
| `formatting.py` | 91% |
| `i18n.py` | 89% |
| `models.py` | 98% |
| `recurrence.py` | 100% |
| **مجموع هسته غیرگرافیکی** | **92%** |

آمار Gate:

| معیار | مقدار |
|---|---:|
| Statements | 538 |
| Missing statements | 28 |
| Branches | 138 |
| Partial branches | 11 |
| Coverage نهایی | 92% |
| حداقل قابل قبول | 90% |

Viewها، Dialogها و Widgetهای Qt با Line Coverage هسته سنجیده نمی‌شوند و باید با Static Regression، Contract Test و UAT دستگاه واقعی ارزیابی شوند.

## 5. خلاصه وضعیت Test Caseهای رسمی

| وضعیت | تعداد |
|---|---:|
| PASS | 18 |
| PARTIAL | 7 |
| NOT RUN | 6 |
| FAIL | 0 |
| مجموع | 31 |

### Test Caseهای PASS

`TC-TASK-01`, `TC-TASK-02`, `TC-TASK-05`, `TC-SUB-01`, `TC-CAT-02`, `TC-SEARCH-01`, `TC-SCH-02`, `TC-REC-01`, `TC-REC-02`, `TC-REC-03`, `TC-REC-04`, `TC-REST-01`, `TC-REM-01`, `TC-SET-01`, `TC-PAL-01`, `TC-AN-01`, `TC-DB-01`, `TC-MIG-01`

### Test Caseهای PARTIAL

`TC-TASK-03`, `TC-TASK-04`, `TC-CAT-01`, `TC-SCH-03`, `TC-HIST-01`, `TC-SWIPE-01`, `TC-IME-02`

### Test Caseهای NOT RUN

`TC-SCH-01`, `TC-PLAN-01`, `TC-IME-01`, `TC-LIFE-01`, `TC-PERF-01`, `TC-BUILD-01`

## 6. موارد باقیمانده اجباری

پیش از اعلام «تمام تست‌های Android پاس شده‌اند» باید موارد زیر اجرا شوند:

1. تکمیل UI بخش `TC-TASK-03` و `TC-CAT-01`
2. `TC-SCH-01` و تکمیل دستگاهی `TC-SCH-03`
3. `TC-PLAN-01`، `TC-HIST-01` و `TC-SWIPE-01`
4. `TC-IME-01` و تکمیل دستگاهی `TC-IME-02`
5. `TC-LIFE-01`
6. `TC-PERF-01`
7. `TC-BUILD-01`
8. اجرای مجدد 42 تست در Python 3.11 و GitHub Actions
9. آزمون Upgrade APK با Database واقعی نسخه قبلی
10. ثبت UAT و Build Evidence برای APK نهایی

## 7. Defectهای کشف‌شده

در توسعه Testهای Migration یک Defect واقعی شناسایی شد: ساخت Index ستون `generated_from_id` پیش از افزودن ستون در Database قدیمی باعث `sqlite3.OperationalError` می‌شد. ترتیب Migration اصلاح و Regression Test اضافه شد. پس از اصلاح، Failure دیگری در مجموعه خودکار مشاهده نشد. این گزاره فقط به 42 تست خودکار محدود است و به معنی نبود Defect در UI یا Android واقعی نیست.

## 8. تصمیم Test Cycle

| Gate | وضعیت |
|---|---|
| تست خودکار بدون Failure | PASS |
| Core Coverage حداقل 90% | PASS — 92% با Branch Coverage |
| تمام P0ها اجرا شده‌اند | FAIL — چند P0 دستگاهی اجرا نشده |
| APK همان Commit نصب و اجرا شده | NOT VERIFIED |
| Migration Fixture قدیمی | PASS — Upgrade APK واقعی هنوز بررسی نشده |
| UAT روی دستگاه واقعی | NOT VERIFIED |
| Defect Critical/High باز | در اجرای خودکار مشاهده نشد |

### نتیجه

این Test Cycle از نظر خودکار موفق است، اما **Release از نظر QA هنوز Conditional است**. پس از اجرای موارد دستگاهی، Migration Upgrade و APK نهایی، گزارش باید بازبینی و امضا شود.

## 9. تأیید اعضا

| عضو | حوزه تأیید | امضا/تاریخ |
|---|---|---|
| علی ابراهیمی نیا | معماری، منطق و یکپارچه‌سازی | |
| امیرحسین رابعی | Tasks، History و Formها | |
| مهدی ابراهیم زاده | Planner، Settings، Mine و Android UI | |
| مجتبی محمودی | UX مدیریت وظایف | |
| علی رضا زاده | Database و Migration | |
| مهدی نریمانی | UX Planner، Theme و Accessibility | |
