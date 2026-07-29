# راهنمای اعمال بسته روی Repository

این ZIP یک **Overlay Update** است؛ یعنی فایل‌های داخل آن را روی پروژه موجود کپی می‌کنید. فایل‌های شخصی موجود مانند `icon.png` حذف نمی‌شوند.

## روش پیشنهادی و قابل دفاع

از ریشه Repository:

```bash
git checkout main
git pull
git checkout -b docs/university-completion
```

ZIP را Extract و محتوای پوشه `Daymark_University_Completion_Update` را داخل ریشه پروژه کپی کنید.

سپس:

```bash
chmod +x tools/run_quality_checks.sh
python -m pip install -r requirements.txt -r requirements-dev.txt
./tools/run_quality_checks.sh
git status
```

مطمئن شوید APK، Database، Log، Keystore یا Virtual Environment در تغییرات نیست.

Commit:

```bash
git add .
git commit -m "docs(qa): complete university engineering evidence"
git push -u origin docs/university-completion
```

در GitHub یک Pull Request از `docs/university-completion` به `main` بسازید. این کار اولین Evidence واقعی Branch، PR، CI و Review خواهد بود.

## نکات صادقانه

- Testهای خودکار و Coverage در این بسته واقعاً اجرا شده‌اند.
- Testهای دستگاه واقعی بدون اجرای شما PASS ثبت نشده‌اند.
- Workflow CI پس از Push به GitHub برای اولین بار اجرا می‌شود.
- Bandit و pip-audit در CI Advisory هستند؛ نتیجه آنها باید بررسی شود.
- Production Signing و Google Play در این بسته انجام نشده است.
