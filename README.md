# Daymark

Daymark یک برنامه مدیریت وظایف و برنامه‌ریزی شخصی برای Android است که با Python، PySide6، Qt و SQLite توسعه داده شده است. برنامه به‌صورت آفلاین کار می‌کند و اطلاعات کاربر را به‌صورت محلی روی دستگاه ذخیره می‌کند.

## اعضای تیم

| عضو تیم | نقش اصلی |
|---|---|
| علی ابراهیمی نیا | معمار نرم‌افزار و توسعه‌دهنده منطق هسته |
| امیرحسین رابعی | توسعه‌دهنده رابط کاربری |
| مهدی ابراهیم زاده | توسعه‌دهنده رابط کاربری |
| مجتبی محمودی | طراح UI/UX |
| علی رضا زاده | توسعه‌دهنده پایگاه داده |
| مهدی نریمانی | طراح UI/UX |


شرح کامل فعالیت هر عضو:

[مشاهده شرح فعالیت اعضای تیم](docs/10_team_contributions.md)

## قابلیت‌ها

- ایجاد، ویرایش، تکمیل، بازیابی و حذف وظیفه
- افزودن زیرکار و یادداشت
- زمان‌بندی براساس تاریخ و ساعت
- وظایف تکرارشونده
- دسته‌بندی، جست‌وجو و فیلتر
- برنامه‌ریزی روزانه، هفتگی و ماهانه
- تاریخچه وظایف
- آمار عملکرد و تقویم حرارتی سالانه
- حالت روشن و تاریک
- پالت‌های Warm Sage، Sky Blue و Aristocratic Green
- رابط انگلیسی و ترکی
- ذخیره محلی SQLite
- رابط واکنش‌گرا برای Android

## مستندات

[مشاهده مجموعه مستندات فارسی پروژه](docs/README.md)

## فناوری‌ها

- Python 3.11
- PySide6 / Qt
- SQLite
- python-for-android
- Buildozer
- PlantUML
- unittest / pytest

## ساختار پروژه

```text
Daymark/
├── daymark/
├── tests/
├── tools/
├── docs/
│   ├── diagrams/
│   ├── README.md
│   └── 01...10 Markdown documents
├── main.py
├── icon.png
├── build_android.sh
├── install_android.sh
├── requirements.txt
├── README.md
└── .gitignore
```

## اجرای تست‌ها

```bash
python -m unittest discover -s tests -v
```

## ساخت APK

```bash
chmod +x build_android.sh
./build_android.sh
```

خروجی:

```text
dist-android/Daymark-debug-arm64-v8a.apk
```

## دانلود APK

نسخه‌های قابل نصب از بخش Releases مخزن دریافت می‌شوند:

[مشاهده نسخه‌های منتشرشده](https://github.com/phoenix-0011/Daymark/releases)

## وضعیت پروژه

این نسخه برای ارائه دانشگاهی، بررسی کد، نمایش مستندات و آزمایش روی دستگاه Android آماده شده است.
