# Test Caseهای رسمی Daymark

> **نسخه سند:** 1.0  
> **تعداد Test Case:** 31  
> **تاریخ:** 2026-07-30  
> **اصل صحت گزارش:** Test Caseهای خودکار براساس اجرای واقعی ثبت شده‌اند؛ موارد دستگاهی که Evidence ندارند `NOT RUN` یا `PARTIAL` هستند.

## 1. خلاصه Test Caseها

| ID | عنوان | اولویت | وضعیت فعلی | مسئول |
|---|---|---|---|---|
| TC-TASK-01 | ایجاد وظیفه معتبر | P0 | PASS | امیرحسین رابعی |
| TC-TASK-02 | ویرایش وظیفه بدون ازدست‌رفتن داده | P0 | PASS | امیرحسین رابعی |
| TC-TASK-03 | رد عنوان خالی و فقط Space | P0 | PARTIAL | امیرحسین رابعی |
| TC-TASK-04 | تکمیل و بازیابی وظیفه | P0 | PARTIAL | امیرحسین رابعی |
| TC-TASK-05 | حذف وظیفه و زیرکارهای وابسته | P0 | PASS | علی رضا زاده |
| TC-SUB-01 | ذخیره، جست‌وجو و کپی زیرکارها در Recurrence | P1 | PASS | علی رضا زاده |
| TC-CAT-01 | ایجاد Category معتبر و جلوگیری از تکرار | P1 | PARTIAL | امیرحسین رابعی |
| TC-CAT-02 | حذف Category بدون حذف Task | P0 | PASS | علی رضا زاده |
| TC-SEARCH-01 | جست‌وجو در عنوان، یادداشت و زیرکار | P1 | PASS | علی رضا زاده |
| TC-SCH-01 | ثبت Date، Time و All-day | P0 | NOT RUN | امیرحسین رابعی |
| TC-SCH-02 | Quick Action تاریخ و پاک‌کردن Schedule وابسته | P1 | PASS | علی ابراهیمی نیا |
| TC-SCH-03 | Schedule بدون پرش، Scroll افقی و Clipping | P0 | PARTIAL | مهدی ابراهیم زاده |
| TC-REC-01 | ایجاد رخداد بعدی برای Daily/Weekly | P0 | PASS | علی ابراهیمی نیا |
| TC-REC-02 | تکرار Weekdays و عبور از آخر هفته | P1 | PASS | علی ابراهیمی نیا |
| TC-REC-03 | تکرار ماهانه در انتهای ماه | P0 | PASS | علی ابراهیمی نیا |
| TC-REC-04 | Idempotency در تکمیل Task تکرارشونده | P0 | PASS | علی ابراهیمی نیا |
| TC-REST-01 | Restore امن Task تکرارشونده | P0 | PASS | علی ابراهیمی نیا |
| TC-REM-01 | حفظ وضعیت Reminder در Edit غیرزمانی | P1 | PASS | علی ابراهیمی نیا |
| TC-PLAN-01 | نمایش وظایف در Day/Week/Month | P0 | NOT RUN | مهدی ابراهیم زاده |
| TC-HIST-01 | History و Restore از رابط | P1 | PARTIAL | امیرحسین رابعی |
| TC-SWIPE-01 | Swipe Action ایمن و مخفی در حالت بسته | P0 | PARTIAL | امیرحسین رابعی |
| TC-IME-01 | Back ابتدا Keyboard و Dialog را ببندد | P0 | NOT RUN | مهدی ابراهیم زاده |
| TC-IME-02 | ادامه تایپ پس از مکث بدون خروج کاذب | P0 | PARTIAL | مهدی ابراهیم زاده |
| TC-SET-01 | فقط English و Turkish در Runtime | P1 | PASS | مهدی ابراهیم زاده |
| TC-PAL-01 | کامل‌بودن Palette، Contrast و Persistence Hook | P1 | PASS | مهدی نریمانی |
| TC-AN-01 | محاسبه Streak و Insight Snapshot | P1 | PASS | علی ابراهیمی نیا |
| TC-DB-01 | Rollback و جلوگیری از Subtask orphan | P0 | PASS | علی رضا زاده |
| TC-MIG-01 | Migration و حفظ داده نسخه قبلی | P0 | PASS | علی رضا زاده |
| TC-LIFE-01 | Persistence و Lifecycle پس از Restart/Kill | P0 | NOT RUN | مهدی ابراهیم زاده |
| TC-PERF-01 | کارایی با 500 Task و 1000 Subtask | P1 | NOT RUN | علی ابراهیمی نیا |
| TC-BUILD-01 | ساخت، اعتبارسنجی، نصب و اجرای APK ARM64 | P0 | NOT RUN | علی ابراهیمی نیا |

## 2. قواعد ثبت نتیجه

- `PASS` فقط پس از مشاهده Evidence ثبت می‌شود.
- `PARTIAL` به معنی موفقیت بخش خودکار یا Static و باقی‌ماندن تست دستگاه است.
- برای هر اجرای دستی باید Build، Commit، دستگاه، Android، تاریخ و Evidence ثبت شود.
- هر `FAIL` باید Defect ID داشته باشد.
- پس از رفع Defect، همان Test Case به Regression Test تبدیل می‌شود.

## TC-TASK-01: ایجاد وظیفه معتبر

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-01, FR-19` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | علی ابراهیمی نیا |
| پیش‌شرط | Database آزمایشی خالی است. |
| داده آزمایشی | عنوان: Prepare study notes؛ یادداشت و Category معتبر |
| نتیجه مورد انتظار | Task دقیقاً یک‌بار ذخیره و در فهرست فعال دیده شود. |
| نتیجه واقعی | عملیات Save و بازیابی Task در مجموعه خودکار تأیید شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_core.py::DatabaseTests::test_save_complete_restore_and_search` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. فرم New Task را باز کنید.
2. عنوان و داده‌های معتبر را وارد کنید.
3. Save را بزنید.
4. فهرست و Database را بررسی کنید.

## TC-TASK-02: ویرایش وظیفه بدون ازدست‌رفتن داده

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-02, FR-04` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | علی ابراهیمی نیا |
| پیش‌شرط | یک Task دارای Note و Subtask وجود دارد. |
| داده آزمایشی | عنوان و زمان جدید |
| نتیجه مورد انتظار | فیلدهای ویرایش‌شده ذخیره و داده‌های دیگر حفظ شوند. |
| نتیجه واقعی | Edit عنوان و Persistence زیرکارها در تست‌های خودکار تأیید شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_save_complete_restore_and_search + test_subtasks_persist_search_and_copy_to_recurring_task` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Task را باز کنید.
2. عنوان یا Note را تغییر دهید.
3. ذخیره کنید.
4. Task و Subtaskها را دوباره بارگذاری کنید.

## TC-TASK-03: رد عنوان خالی و فقط Space

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-01, NFR-USABILITY` |
| نوع تست | System |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | مجتبی محمودی |
| پیش‌شرط | فرم New Task باز است. |
| داده آزمایشی | خالی، چند Space و Line break |
| نتیجه مورد انتظار | ذخیره انجام نشود و پیام اعتبارسنجی واضح نمایش داده شود. |
| نتیجه واقعی | رد Title خالی و Space-only در لایه Database پاس شد؛ نمایش پیام UI نیازمند UAT است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `tests/test_extended_core.py::test_task_validation_and_category_lifecycle` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Title را خالی بگذارید و Save کنید.
2. فقط Space وارد و دوباره Save کنید.

## TC-TASK-04: تکمیل و بازیابی وظیفه

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-13, FR-19` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | علی رضا زاده |
| پیش‌شرط | یک Task فعال وجود دارد. |
| داده آزمایشی | Task غیرتکرارشونده |
| نتیجه مورد انتظار | Task به History منتقل و پس از Restore دوباره فعال شود. |
| نتیجه واقعی | Complete و Restore در Database خودکار تأیید شد؛ View دستگاهی باقی است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `tests/test_core.py::DatabaseTests::test_save_complete_restore_and_search` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Task را Complete کنید.
2. History را بررسی کنید.
3. Restore را اجرا کنید.
4. فهرست فعال را بررسی کنید.

## TC-TASK-05: حذف وظیفه و زیرکارهای وابسته

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-03, FR-04` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی رضا زاده |
| بازبین | امیرحسین رابعی |
| پیش‌شرط | Task دارای چند Subtask وجود دارد. |
| داده آزمایشی | Task آزمایشی حذف‌پذیر |
| نتیجه مورد انتظار | Task و Subtaskهای وابسته حذف و هیچ Orphan باقی نماند. |
| نتیجه واقعی | حذف Task و Cascade زیرکارها در SQLite پاس شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_extended_core.py::test_task_validation_and_category_lifecycle` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Delete را انتخاب کنید.
2. تأیید حذف را انجام دهید.
3. جداول Task و Subtask را بررسی کنید.

## TC-SUB-01: ذخیره، جست‌وجو و کپی زیرکارها در Recurrence

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-04, FR-06, FR-10` |
| نوع تست | Integration |
| اولویت | `P1` |
| مسئول اجرا | علی رضا زاده |
| بازبین | علی ابراهیمی نیا |
| پیش‌شرط | Database آزمایشی آماده است. |
| داده آزمایشی | دو Subtask، یکی تکمیل‌شده |
| نتیجه مورد انتظار | Subtaskها ذخیره و قابل جست‌وجو باشند؛ رخداد بعدی Subtaskها را با وضعیت Reset دریافت کند. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_subtasks_persist_search_and_copy_to_recurring_task` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Task دارای Subtask ذخیره کنید.
2. با متن Subtask جست‌وجو کنید.
3. Task را Complete کنید.
4. رخداد بعدی را بارگذاری کنید.

## TC-CAT-01: ایجاد Category معتبر و جلوگیری از تکرار

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-05, NFR-USABILITY` |
| نوع تست | System |
| اولویت | `P1` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | مجتبی محمودی |
| پیش‌شرط | Settings یا Category Dialog باز است. |
| داده آزمایشی | Work و work |
| نتیجه مورد انتظار | Category اول ذخیره و مورد تکراری براساس سیاست محصول رد یا یکپارچه شود. |
| نتیجه واقعی | Trim نام، رد نام خالی و رد تکرار Case-insensitive در Database پاس شد؛ پیام UI نیازمند UAT است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `tests/test_extended_core.py::test_task_validation_and_category_lifecycle` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Category جدید ایجاد کنید.
2. نام تکراری با تفاوت حروف را ثبت کنید.

## TC-CAT-02: حذف Category بدون حذف Task

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-05, FR-07` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی رضا زاده |
| بازبین | امیرحسین رابعی |
| پیش‌شرط | Category دارای حداقل یک Task است. |
| داده آزمایشی | Category: Work |
| نتیجه مورد انتظار | Taskها باقی بمانند و category_id آنها NULL شود؛ Filter حذف‌شده نمایش داده نشود. |
| نتیجه واقعی | حذف Category و NULL شدن `category_id` بدون حذف Task پاس شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_extended_core.py::test_task_validation_and_category_lifecycle` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Category را حذف کنید.
2. Taskهای وابسته را بارگذاری کنید.
3. فیلترها را بررسی کنید.

## TC-SEARCH-01: جست‌وجو در عنوان، یادداشت و زیرکار

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-06` |
| نوع تست | Integration |
| اولویت | `P1` |
| مسئول اجرا | علی رضا زاده |
| بازبین | امیرحسین رابعی |
| پیش‌شرط | Taskهایی با متن متمایز وجود دارند. |
| داده آزمایشی | study، Chapter five، priorities |
| نتیجه مورد انتظار | Task مرتبط با Title، Note یا Subtask برگردانده شود. |
| نتیجه واقعی | Title و Subtask در تست خودکار تأیید شد؛ Note نیز در مسیر Save/Search پوشش دارد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_save_complete_restore_and_search + test_subtasks_persist_search_and_copy_to_recurring_task` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. هر عبارت را جداگانه جست‌وجو کنید.
2. نتایج را با داده Database مقایسه کنید.

## TC-SCH-01: ثبت Date، Time و All-day

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-08, FR-11` |
| نوع تست | System |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | مهدی نریمانی |
| پیش‌شرط | New Task و Schedule Dialog باز است. |
| داده آزمایشی | Date آینده، Time مشخص، All-day روشن/خاموش |
| نتیجه مورد انتظار | Schedule دقیق ذخیره و در Planner و فرم Edit یکسان نمایش داده شود. |
| نتیجه واقعی | نیازمند اجرای UI روی دستگاه. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Date انتخاب کنید.
2. Time و Reminder تعیین کنید.
3. Save کنید.
4. Task را دوباره باز کنید.

## TC-SCH-02: Quick Action تاریخ و پاک‌کردن Schedule وابسته

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-08, FR-11, FR-15` |
| نوع تست | Integration |
| اولویت | `P1` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Task دارای Date، Time و Reminder است. |
| داده آزمایشی | Date جدید و سپس No Date |
| نتیجه مورد انتظار | Date تغییر کند؛ در No Date، Time، Reminder و Recurrence وابسته پاک شوند. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_core.py::test_star_and_date_quick_actions` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Date را از Quick Action تغییر دهید.
2. مقادیر را بررسی کنید.
3. No Date را انتخاب کنید.

## TC-SCH-03: Schedule بدون پرش، Scroll افقی و Clipping

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-08, NFR-USABILITY, NFR-ANDROID` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | مهدی نریمانی |
| پیش‌شرط | Schedule Dialog روی گوشی باز است. |
| داده آزمایشی | Today، Tomorrow، Calendar Date و No Date |
| نتیجه مورد انتظار | Scroll position نپرد، حرکت افقی وجود نداشته باشد و Repeat کامل دیده شود. |
| نتیجه واقعی | Static regression مربوط به Width و Vertical Scroll پاس شده؛ مشاهده دستگاه باقی است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `test_schedule_refits_are_width_guarded + test_mobile_text_scrollers_are_vertical_only` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. گزینه‌ها را به‌ترتیب انتخاب کنید.
2. Repeat را باز و بسته کنید.
3. Scroll و Width را مشاهده کنید.

## TC-REC-01: ایجاد رخداد بعدی برای Daily/Weekly

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-09, FR-10` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Task تکرارشونده فعال وجود دارد. |
| داده آزمایشی | Daily و Weekly |
| نتیجه مورد انتظار | اصل Task کامل و فقط یک رخداد بعدی با تاریخ صحیح ساخته شود. |
| نتیجه واقعی | Weekly و مسیرهای Daily در تست‌های خودکار تأیید شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_completion_creates_next_recurring_instance + recurring restore tests` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Task را Complete کنید.
2. Taskهای Active و Completed را بررسی کنید.

## TC-REC-02: تکرار Weekdays و عبور از آخر هفته

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-09` |
| نوع تست | Unit |
| اولویت | `P1` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | تاریخ مبنا جمعه است. |
| داده آزمایشی | 2026-07-24 |
| نتیجه مورد انتظار | تاریخ بعدی دوشنبه 2026-07-27 باشد. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `RecurrenceTests::test_weekday_skips_weekend` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. next_date را با weekdays اجرا کنید.

## TC-REC-03: تکرار ماهانه در انتهای ماه

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-09, NFR-RELIABILITY` |
| نوع تست | Unit |
| اولویت | `P0` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | تاریخ مبنا روز 31 ماه است. |
| داده آزمایشی | 2026-01-31 |
| نتیجه مورد انتظار | تاریخ معتبر انتهای ماه مقصد تولید شود و Exception رخ ندهد. |
| نتیجه واقعی | خروجی 2026-02-28 و PASS. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `RecurrenceTests::test_month_end_is_safe` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. next_date را با monthly اجرا کنید.

## TC-REC-04: Idempotency در تکمیل Task تکرارشونده

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-10, NFR-RELIABILITY` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Task تکرارشونده هنوز کامل نشده است. |
| داده آزمایشی | Daily Task |
| نتیجه مورد انتظار | فقط بار اول رخداد بعدی ایجاد شود. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_completing_task_twice_is_idempotent` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Complete را دوبار اجرا کنید.
2. رخدادهای Active را بشمارید.

## TC-REST-01: Restore امن Task تکرارشونده

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-14, NFR-RELIABILITY` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Task اصلی، رخداد Generated و نسخه دستی مشابه وجود دارند. |
| داده آزمایشی | Daily planning |
| نتیجه مورد انتظار | رخداد Generated حذف؛ Task اصلی و نسخه دستی مشابه حفظ شوند. |
| نتیجه واقعی | هر دو حالت حذف Generated و حفظ Manual duplicate پاس شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_restoring_recurring_task_removes_generated_duplicate + test_restore_recurring_task_does_not_delete_manual_duplicate` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Task اصلی را Restore کنید.
2. شناسه Taskهای Active را بررسی کنید.

## TC-REM-01: حفظ وضعیت Reminder در Edit غیرزمانی

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-11` |
| نوع تست | Integration |
| اولویت | `P1` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Reminder قبلاً ارسال شده است. |
| داده آزمایشی | Edit Note و سپس تغییر Time |
| نتیجه مورد انتظار | Edit غیرزمانی وضعیت را حفظ؛ تغییر Schedule آن را Reset کند. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_edit_preserves_sent_reminder_until_schedule_changes` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. فقط Note را تغییر دهید.
2. reminder_sent را بررسی کنید.
3. Time را تغییر دهید.
4. دوباره بررسی کنید.

## TC-PLAN-01: نمایش وظایف در Day/Week/Month

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-12` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | مهدی نریمانی |
| پیش‌شرط | Taskهایی در چند تاریخ وجود دارند. |
| داده آزمایشی | امروز، دو روز بعد و ماه بعد |
| نتیجه مورد انتظار | هر Task در تاریخ صحیح و بدون تکرار یا حذف نمایش داده شود. |
| نتیجه واقعی | نیازمند اجرای دستگاه واقعی. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Day را باز کنید.
2. Week را بررسی کنید.
3. Month را بررسی و روز را انتخاب کنید.

## TC-HIST-01: History و Restore از رابط

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-13, FR-14` |
| نوع تست | System/UAT |
| اولویت | `P1` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | مجتبی محمودی |
| پیش‌شرط | Task کامل‌شده در History وجود دارد. |
| داده آزمایشی | Task ساده و Recurring |
| نتیجه مورد انتظار | Task از History حذف و در فهرست فعال با داده صحیح ظاهر شود. |
| نتیجه واقعی | منطق Database پاس شده؛ جریان رابط هنوز اجرا نشده است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `Database restore tests` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. History را باز کنید.
2. جزئیات را مشاهده کنید.
3. Restore را بزنید.
4. Tasks را بررسی کنید.

## TC-SWIPE-01: Swipe Action ایمن و مخفی در حالت بسته

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-15, NFR-USABILITY` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | امیرحسین رابعی |
| بازبین | مجتبی محمودی |
| پیش‌شرط | Task Card روی گوشی نمایش داده شده است. |
| داده آزمایشی | Swipe افقی، عمودی و Tap |
| نتیجه مورد انتظار | Axis Lock درست باشد؛ Actionها در حالت بسته دیده نشوند؛ Delete تصادفی رخ ندهد. |
| نتیجه واقعی | Position animation و قواعد Source پاس شده؛ Gesture دستگاهی باقی است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `test_swipe_uses_position_animation + source-level checks` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Scroll عمودی را شروع کنید.
2. Swipe افقی کوتاه و کامل انجام دهید.
3. Action Date و Star را اجرا کنید.
4. Delete را با تأیید بررسی کنید.

## TC-IME-01: Back ابتدا Keyboard و Dialog را ببندد

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-20, NFR-ANDROID` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | مهدی نریمانی |
| پیش‌شرط | Keyboard داخل Dialog باز است. |
| داده آزمایشی | Back متوالی |
| نتیجه مورد انتظار | اول Keyboard، سپس Dialog و بعد Navigation/Exit مدیریت شود. |
| نتیجه واقعی | نیازمند اجرای Android واقعی. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. یک‌بار Back بزنید.
2. بار دوم Back بزنید.
3. بار سوم رفتار Navigation/Exit را بررسی کنید.

## TC-IME-02: ادامه تایپ پس از مکث بدون خروج کاذب

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-20, NFR-USABILITY` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | مهدی نریمانی |
| پیش‌شرط | Title فعال و Keyboard باز است. |
| داده آزمایشی | متن، مکث 5 ثانیه و ادامه متن |
| نتیجه مورد انتظار | Keyboard بسته/باز نشود و پیام Exit کاذب ظاهر نشود. |
| نتیجه واقعی | Guardهای Source بررسی شده‌اند؛ رفتار دستگاه هنوز اجرا نشده است. |
| وضعیت | **PARTIAL** |
| Evidence / Automated Test | `test_child_dialog_guards_are_exception_safe + stability source checks` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. در Title تایپ کنید.
2. 5 ثانیه مکث کنید.
3. دوباره تایپ کنید.

## TC-SET-01: فقط English و Turkish در Runtime

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-17` |
| نوع تست | Unit/Integration |
| اولویت | `P1` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | مهدی نریمانی |
| پیش‌شرط | Language service قابل دسترسی است. |
| داده آزمایشی | en، tr و fa |
| نتیجه مورد انتظار | فقط en و tr قابل انتخاب؛ fa به en fallback شود. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_only_english_and_turkish_are_available + test_persian_runtime_hooks_are_removed` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Language list را بخوانید.
2. fa را Set کنید.
3. tr را Set و ترجمه Today را بررسی کنید.

## TC-PAL-01: کامل‌بودن Palette، Contrast و Persistence Hook

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-18, NFR-ACCESSIBILITY` |
| نوع تست | Static/Unit |
| اولویت | `P1` |
| مسئول اجرا | مهدی نریمانی |
| بازبین | مهدی ابراهیم زاده |
| پیش‌شرط | theme.py و Settings source موجود است. |
| داده آزمایشی | Warm Sage، Sky Blue، Aristocratic Green؛ Light/Dark |
| نتیجه مورد انتظار | هر 3 Palette در 2 Mode کامل؛ Contrast اصلی معتبر؛ Hookها موجود باشند. |
| نتیجه واقعی | تمام تست‌های Palette پاس شدند. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_palette_system.py` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Roleهای هر Palette را استخراج کنید.
2. Contrast را محاسبه کنید.
3. Hook ذخیره و بازیابی را بررسی کنید.

## TC-AN-01: محاسبه Streak و Insight Snapshot

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-16` |
| نوع تست | Unit |
| اولویت | `P1` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | مهدی ابراهیم زاده |
| پیش‌شرط | فهرست Taskهای Active و Completed آماده است. |
| داده آزمایشی | Completion امروز و سه روز متوالی |
| نتیجه مورد انتظار | Streak، Total، Today، Week و Upcoming counts صحیح باشند. |
| نتیجه واقعی | هر دو تست Analytics پاس شدند. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_analytics.py` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. completion_streak را اجرا کنید.
2. calculate_insights را اجرا کنید.

## TC-DB-01: Rollback و جلوگیری از Subtask orphan

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-21, NFR-RELIABILITY, NFR-SECURITY` |
| نوع تست | Integration |
| اولویت | `P0` |
| مسئول اجرا | علی رضا زاده |
| بازبین | علی ابراهیمی نیا |
| پیش‌شرط | شناسه Task ناموجود است. |
| داده آزمایشی | Task id=999999 با Subtask |
| نتیجه مورد انتظار | Transaction Rollback شود و هیچ Subtask orphan ایجاد نشود. |
| نتیجه واقعی | مطابق انتظار در تست خودکار. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `test_updating_missing_task_rolls_back_cleanly` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. Update را اجرا کنید.
2. Exception را دریافت کنید.
3. جدول Subtask را شمارش کنید.

## TC-MIG-01: Migration و حفظ داده نسخه قبلی

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-19, FR-21, NFR-RELIABILITY` |
| نوع تست | Integration/System |
| اولویت | `P0` |
| مسئول اجرا | علی رضا زاده |
| بازبین | علی ابراهیمی نیا |
| پیش‌شرط | Database نمونه با Schema قبلی و داده معتبر موجود است. |
| داده آزمایشی | Task، Subtask، Category و Settings نسخه قبلی |
| نتیجه مورد انتظار | Migration بدون حذف یا تغییر ناخواسته داده تکمیل شود. |
| نتیجه واقعی | Fixture Schema قدیمی اجرا شد؛ اشکال ترتیب Index شناسایی، اصلاح و Migration با حفظ Task پاس شد. |
| وضعیت | **PASS** |
| Evidence / Automated Test | `tests/test_extended_core.py::test_migration_adds_missing_columns_and_preserves_legacy_data` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. از Database نسخه پشتیبان بگیرید.
2. نسخه جدید را اجرا کنید.
3. Migration را بررسی کنید.
4. تمام داده‌ها و روابط را مقایسه کنید.

## TC-LIFE-01: Persistence و Lifecycle پس از Restart/Kill

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-19, NFR-ANDROID, NFR-RELIABILITY` |
| نوع تست | System/UAT |
| اولویت | `P0` |
| مسئول اجرا | مهدی ابراهیم زاده |
| بازبین | علی رضا زاده |
| پیش‌شرط | چند Task، Category و Settings ذخیره شده‌اند. |
| داده آزمایشی | Light/Dark، Palette، Taskهای Active/Completed |
| نتیجه مورد انتظار | داده و تنظیمات حفظ؛ Crash و Duplicate رخ ندهد. |
| نتیجه واقعی | نیازمند اجرای دستگاه واقعی. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. برنامه را Background و Foreground کنید.
2. Force Stop کنید.
3. دوباره اجرا کنید.
4. داده‌ها را مقایسه کنید.

## TC-PERF-01: کارایی با 500 Task و 1000 Subtask

| فیلد | مقدار |
|---|---|
| Requirement ID | `NFR-PERFORMANCE, NFR-SCALABILITY` |
| نوع تست | Performance |
| اولویت | `P1` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | علی رضا زاده |
| پیش‌شرط | Seed script یا Fixture حجیم آماده است. |
| داده آزمایشی | 500 Task و 1000 Subtask |
| نتیجه مورد انتظار | Freeze بالاتر از 1 ثانیه و ANR/Crash وجود نداشته باشد؛ UI قابل استفاده بماند. |
| نتیجه واقعی | Benchmark رسمی هنوز اجرا نشده است. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. داده را Seed کنید.
2. Startup، Search، Complete و Scroll را اندازه‌گیری کنید.
3. 30 دقیقه تعامل انجام دهید.

## TC-BUILD-01: ساخت، اعتبارسنجی، نصب و اجرای APK ARM64

| فیلد | مقدار |
|---|---|
| Requirement ID | `FR-22, NFR-ANDROID, NFR-SECURITY` |
| نوع تست | System/Release |
| اولویت | `P0` |
| مسئول اجرا | علی ابراهیمی نیا |
| بازبین | تمام اعضای تیم |
| پیش‌شرط | Python 3.11، JDK 17، SDK/NDK و دستگاه ARM64 آماده‌اند. |
| داده آزمایشی | Commit نهایی Release |
| نتیجه مورد انتظار | APK ARM64 معتبر ساخته، نصب و بدون Crash اولیه اجرا شود. |
| نتیجه واقعی | Build قبلی پروژه موجود است، اما برای این Test Cycle Evidence جدید ثبت نشده است. |
| وضعیت | **NOT RUN** |
| Evidence / Automated Test | `—` |
| Build / Commit | در اجرای رسمی تکمیل شود |
| دستگاه / Android | در تست دستی تکمیل شود |
| تاریخ اجرا | اجرای خودکار: 2026-07-30؛ دستی: ثبت نشده |
| Defect ID | در صورت FAIL ثبت شود |

### مراحل اجرا

1. build_android.sh را اجرا کنید.
2. APK را با verify_apk.py بررسی کنید.
3. روی دستگاه نصب کنید.
4. برنامه را اجرا و Logcat را بررسی کنید.


