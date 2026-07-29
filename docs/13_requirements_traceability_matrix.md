# ماتریس ردیابی نیازمندی‌ها و تست‌ها

> **پروژه:** Daymark  
> **نسخه:** 1.0  
> **تاریخ:** 2026-07-30

## 1. هدف

این ماتریس نشان می‌دهد هر نیازمندی با کدام Test Case بررسی می‌شود و وضعیت پوشش فعلی آن چیست. `Covered` به معنی وجود و اجرای Evidence مربوط است؛ `Partial` یعنی بخشی اجرا شده و بخش دستی یا دستگاهی باقی است.

## 2. ماتریس

| Requirement ID | نیازمندی | Test Caseها | وضعیت پوشش |
|---|---|---|---|
| `FR-01` | ایجاد وظیفه | TC-TASK-01, TC-TASK-03 | Partial |
| `FR-02` | ویرایش وظیفه | TC-TASK-02 | Covered |
| `FR-03` | حذف وظیفه | TC-TASK-05 | Covered in core |
| `FR-04` | مدیریت زیرکار | TC-TASK-02, TC-TASK-05, TC-SUB-01 | Partial |
| `FR-05` | دسته‌بندی | TC-CAT-01, TC-CAT-02 | Covered in core; UI partial |
| `FR-06` | جست‌وجو | TC-SEARCH-01, TC-SUB-01 | Covered |
| `FR-07` | فیلتر | TC-CAT-02, TC-SEARCH-01 | Partial |
| `FR-08` | زمان‌بندی | TC-SCH-01, TC-SCH-02, TC-SCH-03 | Partial |
| `FR-09` | تکرار | TC-REC-01, TC-REC-02, TC-REC-03 | Covered |
| `FR-10` | رخداد بعدی | TC-REC-01, TC-REC-04 | Covered |
| `FR-11` | یادآور | TC-SCH-01, TC-SCH-02, TC-REM-01 | Partial |
| `FR-12` | نماهای Planner | TC-PLAN-01 | Not executed |
| `FR-13` | History | TC-TASK-04, TC-HIST-01 | Partial |
| `FR-14` | Restore امن | TC-REST-01, TC-HIST-01 | Covered in core |
| `FR-15` | Swipe actions | TC-SCH-02, TC-SWIPE-01 | Partial |
| `FR-16` | Mine/Insights | TC-AN-01, TC-PLAN-01 | Partial |
| `FR-17` | تنظیمات | TC-SET-01, TC-PAL-01, TC-LIFE-01 | Partial |
| `FR-18` | پالت | TC-PAL-01, TC-LIFE-01 | Partial |
| `FR-19` | ذخیره محلی | TC-TASK-01, TC-TASK-04, TC-MIG-01, TC-LIFE-01 | Partial |
| `FR-20` | رفتار Back | TC-IME-01, TC-IME-02 | Partial |
| `FR-21` | خطا و Transaction | TC-DB-01, TC-MIG-01 | Covered in core |
| `FR-22` | Android Build | TC-BUILD-01 | Not executed in cycle |
| `NFR-PERFORMANCE` | کارایی | TC-PERF-01 | Not executed |
| `NFR-SCALABILITY` | تحمل رشد داده محلی | TC-PERF-01 | Not executed |
| `NFR-RELIABILITY` | قابلیت اطمینان | TC-REC-03, TC-REC-04, TC-REST-01, TC-DB-01, TC-MIG-01, TC-LIFE-01 | Partial |
| `NFR-SECURITY` | امنیت و حریم خصوصی | TC-DB-01, TC-BUILD-01 | Partial |
| `NFR-USABILITY` | کاربردپذیری | TC-TASK-03, TC-CAT-01, TC-SCH-03, TC-SWIPE-01, TC-IME-02 | Partial |
| `NFR-MAINTAINABILITY` | نگهداری‌پذیری | Automated regression suite | Covered partially |
| `NFR-ANDROID` | سازگاری Android | TC-SCH-03, TC-IME-01, TC-LIFE-01, TC-BUILD-01 | Not fully executed |
| `NFR-ACCESSIBILITY` | دسترس‌پذیری | TC-PAL-01, Device UAT checklist | Partial |

## 3. قواعد Traceability

- هر Requirement جدید باید پیش از Merge حداقل یک Test Case داشته باشد.
- هر Defect باید به Requirement و Test Case Regression متصل شود.
- حذف یا تغییر Requirement باید اثر آن بر Test Caseها بررسی شود.
- وضعیت `Covered` فقط با Evidence قابل ثبت است.
- UAT دستگاهی باید Build و مدل گوشی را مشخص کند.

## 4. شکاف‌های فعلی

- FR-03، FR-05، FR-12 و FR-22 هنوز اجرای کامل ثبت‌شده ندارند.
- FR-08، FR-11، FR-13، FR-15، FR-17 تا FR-21 پوشش Partial دارند.
- NFRهای Performance، Android و Lifecycle نیازمند آزمون دستگاه واقعی‌اند.
- Core Coverage هسته غیرگرافیکی با Branch Coverage برابر 92% است و Gate 90% را پاس می‌کند.
