# کنترل نسخه و همکاری تیمی

## وضعیت قابل اثبات فعلی

Repository، `.gitignore`، README و Release وجود دارند. بااین‌حال، تاریخچه اولیه توسعه عمدتاً با Commit مستقیم ساخته شده و نمی‌توان به‌صورت صادقانه برای گذشته PR یا Review ساختگی ایجاد کرد.

## اصلاح اعمال‌شده

- `CONTRIBUTING.md`
- Pull Request Template
- Bug و Feature Issue Template
- CI روی Push و Pull Request
- الگوی Branch و Commit
- Definition of Done

## فرایند اجباری از این تغییر به بعد

```text
Issue/Requirement
      ↓
Feature Branch
      ↓
Commitهای معنادار
      ↓
Pull Request
      ↓
CI + Review
      ↓
Merge به main
      ↓
Release Checklist
```

## اولین PR پیشنهادی

این بسته را مستقیماً روی `main` Push نکنید. Branch بسازید:

```bash
git checkout -b docs/university-completion
git add .
git commit -m "docs(qa): complete university engineering evidence"
git push -u origin docs/university-completion
```

سپس PR به `main` بسازید و از یک عضو دیگر Review بگیرید. این PR اولین Evidence واقعی همکاری خواهد بود.

## Evidence موردنیاز

- URL Pull Request
- نتیجه CI
- Comment یا Approval بازبین
- Commit SHA نهایی
- ارتباط با Requirement/Test Case
