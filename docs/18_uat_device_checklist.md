# UAT و Device Test Checklist

## اطلاعات اجرا

- Test Cycle:
- Version/Tag:
- Commit SHA:
- APK:
- Tester:
- تاریخ:
- Device:
- Android:
- Screen resolution:
- Keyboard:
- نصب تمیز یا Upgrade:

## Startup و Lifecycle

- [ ] نصب موفق
- [ ] اجرای اول بدون Crash
- [ ] Background و Foreground
- [ ] Force Stop و Relaunch
- [ ] حفظ Task، Category و Settings

## Task و Composer

- [ ] ایجاد Task ساده
- [ ] رد Title خالی و Space-only
- [ ] Edit بدون حذف Note/Subtask
- [ ] Add چندباره با Tap سریع رخ نمی‌دهد
- [ ] Save هنگام بازبودن Keyboard قابل دسترسی است

## Schedule و Recurrence

- [ ] Date و Time ذخیره می‌شوند
- [ ] No Date وابستگی‌های زمان را پاک می‌کند
- [ ] Scroll افقی وجود ندارد
- [ ] Repeat باز و بسته می‌شود
- [ ] Month-end recurrence معتبر است

## Navigation و Input

- [ ] Back ابتدا Keyboard را می‌بندد
- [ ] Back سپس Dialog را می‌بندد
- [ ] Exit کاذب هنگام تایپ رخ نمی‌دهد
- [ ] Scroll عمودی روان است
- [ ] Swipe با Scroll عمودی تداخل ندارد

## Planner، History و Mine

- [ ] Day/Week/Month داده صحیح دارند
- [ ] Complete به History منتقل می‌کند
- [ ] Restore صحیح است
- [ ] Mine/Heatmap Render می‌شود

## Theme و Accessibility

- [ ] Warm Sage Light/Dark
- [ ] Sky Blue Light/Dark
- [ ] Aristocratic Green Light/Dark
- [ ] متن بریده نمی‌شود
- [ ] Contrast و Target Size مناسب است
- [ ] English و Turkish بررسی شده‌اند

## Performance

- [ ] فهرست طولانی قابل استفاده است
- [ ] Freeze بیشتر از یک ثانیه در عملیات عادی دیده نمی‌شود
- [ ] تعامل ۳۰ دقیقه‌ای بدون ANR/Crash

## نتیجه

- Passed:
- Failed:
- Blocked:
- Defect IDs:
- Evidence paths:
- تصمیم Release: Approved / Conditional / Rejected
