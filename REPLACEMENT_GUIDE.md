# راهنمای جایگزینی فایل‌ها

این بسته برای جایگزینی مستندات فعلی پروژه Daymark آماده شده است.

## فایل‌های قابل جایگزینی

- `README.md` بسته → جایگزین `README.md` ریشه پروژه
- پوشه `docs` بسته → جایگزین پوشه `docs` پروژه

## مراحل

1. از پوشه فعلی پروژه یک نسخه پشتیبان بگیرید.
2. `README.md` جدید را در ریشه پروژه قرار دهید.
3. پوشه `docs` جدید را جایگزین پوشه فعلی کنید.
4. فایل‌های SVG قبلی را در صورت نیاز نگه دارید و فایل‌های PlantUML جدید را دوباره به SVG تبدیل کنید:

```bash
plantuml -charset UTF-8 -tsvg docs/diagrams/*.puml
```

5. تغییرات را بررسی و Commit کنید:

```bash
git status
git add README.md docs
git commit -m "Update documentation with team roles and contributions"
git push
```


## جایگزینی نسخه کامل تست

پوشه `docs` این بسته را جایگزین پوشه `docs` فعلی پروژه کنید. سپس:

```bash
plantuml -charset UTF-8 -tsvg docs/diagrams/*.puml

git add docs TESTING_UPDATE_SUMMARY.md
git commit -m "Complete test strategy, test cases and execution report"
git push
```
