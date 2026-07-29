# Release Checklist

> برای هر Release یک کپی از این فایل تهیه و Build، Commit و مسئولان را ثبت کنید.

## مشخصات

- Version:
- Tag:
- Commit SHA:
- APK filename:
- تاریخ:
- مسئول Release:

## Source و Repository

- [ ] Working tree پاک است.
- [ ] تغییر از طریق PR بازبینی شده است.
- [ ] CI پاس شده است.
- [ ] Secret، Database، Log و Signing Material Commit نشده‌اند.
- [ ] README، Changelog و Release Notes به‌روز شده‌اند.

## Test

- [ ] تمام Testهای خودکار پاس شده‌اند.
- [ ] Core Coverage حداقل 90% است.
- [ ] تمام Test Caseهای P0 اجرا شده‌اند.
- [ ] Defect Critical یا High باز وجود ندارد.
- [ ] UAT Device Checklist تکمیل شده است.
- [ ] Migration روی Database قبلی بررسی شده است.

## Android Build

- [ ] Python 3.11
- [ ] JDK 17
- [ ] SDK/NDK صحیح
- [ ] Icon مربع و معتبر
- [ ] معماری ARM64-v8a
- [ ] APK با `tools/verify_apk.py` بررسی شده است.
- [ ] نصب تمیز موفق است.
- [ ] Upgrade نصب‌شده و داده حفظ شده است.
- [ ] Crash اولیه در Logcat دیده نمی‌شود.

## Security و Privacy

- [ ] Permissionهای APK مرور شده‌اند.
- [ ] Dependency Audit مرور شده است.
- [ ] Log حاوی داده خصوصی نیست.
- [ ] Debug/Release بودن Build در توضیحات صریح است.
- [ ] Keystore و رمزها خارج از Repository هستند.

## Release Assets

- [ ] APK نام واضح دارد.
- [ ] Release Notes کامل است.
- [ ] Minimum Android و Architecture ذکر شده است.
- [ ] محدودیت Play Protect و Debug Build ذکر شده است.
- [ ] لینک دانلود آزمایش شده است.

## تأیید

| حوزه | نام | نتیجه | تاریخ |
|---|---|---|---|
| معماری و Core | | | |
| UI | | | |
| UX | | | |
| Database | | | |
| Release | | | |
