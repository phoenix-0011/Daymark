# مجموعه مستندات مهندسی نرم‌افزار Daymark

> **پروژه:** Daymark  
> **نوع محصول:** برنامه مدیریت وظایف و برنامه‌ریزی محلی برای Android  
> **فناوری‌های اصلی:** Python 3.11، PySide6/Qt، SQLite، Buildozer و python-for-android  
> **تیم:** شش نفر با تخصص معماری، منطق هسته، رابط کاربری، UI/UX و پایگاه داده

## اعضای تیم

| عضو تیم | نقش اصلی |
|---|---|
| علی ابراهیمی نیا | معمار نرم‌افزار و توسعه‌دهنده منطق هسته |
| امیرحسین رابعی | توسعه‌دهنده رابط کاربری |
| مهدی ابراهیم زاده | توسعه‌دهنده رابط کاربری |
| مجتبی محمودی | طراح UI/UX |
| علی رضا زاده | توسعه‌دهنده پایگاه داده |
| مهدی نریمانی | طراح UI/UX |


## فهرست اسناد

1. [`01_requirements_engineering.md`](01_requirements_engineering.md) — مهندسی نیازمندی‌ها و SRS
2. [`02_development_methodology.md`](02_development_methodology.md) — روش توسعه و تقسیم مسئولیت واقعی تیم
3. [`03_design_and_architecture.md`](03_design_and_architecture.md) — طراحی، معماری و مالکیت ماژول‌ها
4. [`04_implementation_best_practices.md`](04_implementation_best_practices.md) — استانداردهای پیاده‌سازی
5. [`05_testing_strategy.md`](05_testing_strategy.md) — راهبرد تست و مسئول هر حوزه
6. [`06_quality_assurance.md`](06_quality_assurance.md) — تضمین کیفیت و بازبینی کد
7. [`07_documentation_plan.md`](07_documentation_plan.md) — برنامه مستندسازی و مالکیت اسناد
8. [`08_deployment_and_devops.md`](08_deployment_and_devops.md) — ساخت، استقرار و انتشار Android
9. [`09_security_and_ethics.md`](09_security_and_ethics.md) — امنیت، حریم خصوصی، دسترس‌پذیری و اخلاق
10. [`10_team_contributions.md`](10_team_contributions.md) — شرح کامل فعالیت و خروجی هر عضو
11. [`11_test_cases.md`](11_test_cases.md) — ۳۱ Test Case رسمی با نتیجه واقعی و وضعیت
12. [`12_test_execution_report.md`](12_test_execution_report.md) — گزارش اجرای ۴۲ تست خودکار و Coverage
13. [`13_requirements_traceability_matrix.md`](13_requirements_traceability_matrix.md) — ماتریس ردیابی FR/NFR و Test Case
14. [`14_project_iterations.md`](14_project_iterations.md) — بازسازی صادقانه Iterationها و Retrospective
15. [`15_user_guide.md`](15_user_guide.md) — راهنمای استفاده از برنامه
16. [`16_presentation_and_demo.md`](16_presentation_and_demo.md) — ساختار ارائه و سناریوی Demo
17. [`17_release_checklist.md`](17_release_checklist.md) — Checklist انتشار
18. [`18_uat_device_checklist.md`](18_uat_device_checklist.md) — UAT و آزمون دستگاه واقعی
19. [`19_version_control_and_collaboration.md`](19_version_control_and_collaboration.md) — Git، Branch، PR و Evidence
20. [`20_security_verification.md`](20_security_verification.md) — کنترل‌های واقعی امنیت و حریم خصوصی
21. [`adr/`](adr) — تصمیم‌های معماری ثبت‌شده

## نمودارها

فایل‌های مستقل PlantUML در پوشه [`diagrams`](diagrams) قرار دارند. این مجموعه شامل نمودارهای Use Case، فرایند توسعه، Component، Class، Sequence، ER، وابستگی بسته‌ها، تست، CI، مستندات، استقرار، امنیت و مسئولیت تیم است.

برای تولید SVG:

```bash
plantuml -charset UTF-8 -tsvg diagrams/*.puml
```

## قاعده نگهداری

هر عضو مسئول به‌روز نگه‌داشتن بخش مربوط به حوزه تخصصی خود است. تغییر رفتار یا معماری بدون اصلاح سند مرتبط کامل محسوب نمی‌شود. بازبینی نهایی سازگاری اسناد با ساختار پروژه با مشارکت تیم و هماهنگی فنی علی ابراهیمی نیا انجام می‌شود.
