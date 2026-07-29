# راهنمای مشارکت در Daymark

## اصل همکاری

هر تغییر باید قابل ردیابی، کوچک، قابل بازبینی و همراه با تست یا Checklist مناسب باشد. تغییر مستقیم روی `main` برای کارهای جدید توصیه نمی‌شود.

## Branchها

از `main` یک Branch جدید بسازید:

```bash
git checkout main
git pull
git checkout -b type/short-description
```

الگوهای پیشنهادی:

```text
feat/task-templates
fix/database-migration
ui/planner-spacing
docs/testing-report
test/category-lifecycle
```

## Commit Message

قالب:

```text
type(scope): short imperative description
```

نمونه:

```text
fix(database): migrate legacy generated_from column safely
test(core): cover category deletion and reminder queries
docs(qa): add UAT and release checklists
ci(python): run tests and core coverage on pull requests
```

انواع اصلی: `feat`، `fix`، `ui`، `test`، `docs`، `ci`، `refactor` و `chore`.

## Pull Request

هر Pull Request باید شامل این موارد باشد:

- مسئله و دلیل تغییر
- فایل‌ها و رفتارهای تغییرکرده
- Requirement یا Test Case مرتبط
- روش تست و Evidence
- Screenshot برای تغییر UI
- اثر احتمالی روی Database یا Build
- Checklist تکمیل‌شده

حداقل یک عضو مرتبط باید تغییر را بازبینی کند:

| حوزه | بازبین اصلی |
|---|---|
| معماری و منطق | علی ابراهیمی نیا |
| رابط Tasks/History | امیرحسین رابعی یا مهدی ابراهیم زاده |
| Planner/Settings/Mine | مهدی ابراهیم زاده یا امیرحسین رابعی |
| UI/UX | مجتبی محمودی یا مهدی نریمانی |
| Database/Migration | علی رضا زاده و علی ابراهیمی نیا |

## Definition of Done

- کد Compile می‌شود.
- تست‌های مرتبط پاس می‌شوند.
- Core Coverage کمتر از 90% نمی‌شود.
- CI پاس می‌شود یا Failure آن مستند و پذیرفته شده است.
- مستندات و RTM در صورت تغییر رفتار به‌روز شده‌اند.
- فایل Build، Database، Log، Secret یا Key Commit نشده است.
- تغییر UI روی حداقل یک دستگاه یا اندازه هدف بررسی شده است.

## بررسی محلی

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
./tools/run_quality_checks.sh
```

## گزارش باگ

از Issue Template استفاده کنید و Build، دستگاه، Android، مراحل بازتولید، Expected، Actual و Evidence را ثبت کنید.
