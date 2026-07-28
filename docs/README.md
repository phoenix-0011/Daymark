<div dir="rtl">

# مجموعه مستندات مهندسی نرم‌افزار Daymark

> **پروژه:** Daymark  
> **نوع محصول:** برنامه مدیریت وظایف و برنامه‌ریزی محلی (Local-first) برای Android  
> **فناوری‌های اصلی:** Python 3.11، PySide6/Qt، SQLite، Buildozer و python-for-android  
> **دامنه فعلی:** تک‌کاربره، بدون حساب ابری و بدون انتقال داده به سرور


این پوشه، موارد مطرح‌شده در چک‌لیست مهندسی نرم‌افزار را به اسناد مستقل فارسی تبدیل می‌کند. متن‌ها بر مبنای وضعیت فعلی
پروژه Daymark نوشته شده‌اند، نه به‌صورت یک نمونه کاملاً عمومی.

## فهرست اسناد

1. [`01_requirements_engineering.md`](01_requirements_engineering.md) — مهندسی نیازمندی‌ها و SRS
2. [`02_development_methodology.md`](02_development_methodology.md) — روش توسعه پیشنهادی
3. [`03_design_and_architecture.md`](03_design_and_architecture.md) — طراحی سطح بالا و پایین
4. [`04_implementation_best_practices.md`](04_implementation_best_practices.md) — استانداردهای پیاده‌سازی
5. [`05_testing_strategy.md`](05_testing_strategy.md) — راهبرد تست
6. [`06_quality_assurance.md`](06_quality_assurance.md) — تضمین کیفیت و کیفیت کد
7. [`07_documentation_plan.md`](07_documentation_plan.md) — برنامه مستندسازی
8. [`08_deployment_and_devops.md`](08_deployment_and_devops.md) — استقرار و DevOps
9. [`09_security_and_ethics.md`](09_security_and_ethics.md) — امنیت، حریم خصوصی، دسترس‌پذیری و اخلاق

کد تمام نمودارها هم داخل فایل‌های Markdown و هم به‌صورت فایل مستقل در پوشه [`diagrams`](diagrams) قرار دارد.

## نمایش نمودارهای SVG در اسناد

تصاویر خروجی PlantUML با مسیر نسبی از پوشه `diagrams` مستقیماً در فایل‌های Markdown درج شده‌اند. بنابراین ساختار زیر
باید حفظ شود:

```text
Daymark_Persian_Software_Engineering_Docs/
├── 01_requirements_engineering.md
├── ...
└── diagrams/
    ├── 01_use_case.svg
    ├── 02_agile_flow.svg
    └── ...
```

نگاشت تصاویر به اسناد:

| تصویر SVG                                              | سند محل نمایش              |
|--------------------------------------------------------|----------------------------|
| `01_use_case.svg`                                      | مهندسی نیازمندی‌ها و SRS   |
| `02_agile_flow.svg`                                    | روش توسعه نرم‌افزار        |
| `03_component_architecture.svg` تا `06_er_diagram.svg` | طراحی و معماری             |
| `07_package_dependencies.svg`                          | بهترین رویه‌های پیاده‌سازی |
| `08_test_strategy.svg`                                 | راهبرد تست                 |
| `09_ci_quality.svg`                                    | تضمین کیفیت                |
| `10_documentation_map.svg`                             | برنامه مستندسازی           |
| `11_deployment.svg` و `12_release_pipeline.svg`        | استقرار و DevOps           |
| `13_security_boundary.svg`                             | امنیت و اخلاق              |

در هر بخش، تصویر SVG از مسیر `diagrams` نمایش داده می‌شود و سپس کد منبع PlantUML قرار دارد. فایل‌های SVG باید از
نسخه‌های Android-only موجود در همین بسته دوباره تولید شوند.

## تولید تصویر از PlantUML

با نصب PlantUML و Graphviz می‌توان تمام نمودارهای مخصوص نسخه Android را تولید کرد:

```bash
plantuml diagrams/*.puml
```

یا برای خروجی SVG:

```bash
plantuml -tsvg diagrams/*.puml
```

## فرض‌های اصلی

- برنامه در نسخه فعلی محلی و تک‌کاربره است.
- حساب کاربری، همگام‌سازی ابری و API شبکه در دامنه نسخه فعلی نیست.
- یادآور در نسخه فعلی Android درون‌برنامه‌ای است؛ برای اعلان قابل‌اعتماد در پس‌زمینه یا پس از بسته‌شدن برنامه، استفاده
  از سرویس بومی Android و زمان‌بندی سیستم لازم است.
- رابط فعلی انگلیسی و ترکی است، ولی این مجموعه مستندات به فارسی نوشته شده است.
- خروجی Android فعلی ARM64 است و زنجیره ساخت آن به Python 3.11، PySide6، JDK 17، Android SDK/NDK و Buildozer وابسته است.

</div>