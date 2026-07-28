from __future__ import annotations

from dataclasses import dataclass

from .i18n import language


@dataclass(frozen=True, slots=True)
class TaskTemplate:
    key: str
    group_en: str
    group_tr: str
    title_en: str
    title_tr: str
    description_en: str
    description_tr: str
    emoji: str
    subtasks_en: tuple[str, ...] = ()
    subtasks_tr: tuple[str, ...] = ()
    category_hint: str | None = None
    recurrence: str = "none"

    @property
    def group(self) -> str:
        return self.group_tr if language() == "tr" else self.group_en

    @property
    def title(self) -> str:
        return self.title_tr if language() == "tr" else self.title_en

    @property
    def description(self) -> str:
        return self.description_tr if language() == "tr" else self.description_en

    @property
    def subtasks(self) -> tuple[str, ...]:
        return self.subtasks_tr if language() == "tr" else self.subtasks_en


TEMPLATES: tuple[TaskTemplate, ...] = (
    TaskTemplate(
        "morning_reset", "Health", "Sağlık", "Morning reset", "Sabah yenilenmesi",
        "Start the day with a calm, healthy routine.", "Güne sakin ve sağlıklı bir rutinle başlayın.", "☀",
        ("Drink a glass of water", "Stretch for five minutes", "Plan the top three priorities"),
        ("Bir bardak su iç", "Beş dakika esne", "En önemli üç işi planla"), "Wellbeing", "daily",
    ),
    TaskTemplate(
        "drink_water", "Health", "Sağlık", "Drink water, keep healthy", "Su iç, sağlıklı kal",
        "A simple hydration reminder for busy days.", "Yoğun günlerde su içmeyi hatırlatan basit bir görev.", "💧",
        ("Fill a water bottle", "Drink one glass now", "Refill before lunch"),
        ("Su şişesini doldur", "Şimdi bir bardak iç", "Öğle yemeğinden önce yeniden doldur"), "Wellbeing", "daily",
    ),
    TaskTemplate(
        "workout", "Health", "Sağlık", "Complete a workout", "Egzersiz yap",
        "A balanced short workout that is easy to repeat.", "Kolayca tekrarlanabilen dengeli ve kısa bir egzersiz.", "🏃",
        ("Warm up", "Main workout", "Cool down", "Drink water"),
        ("Isın", "Ana egzersiz", "Soğuma hareketleri", "Su iç"), "Wellbeing", "weekly",
    ),
    TaskTemplate(
        "medication", "Health", "Sağlık", "Medication reminder", "İlaç hatırlatıcısı",
        "Keep an important medication routine visible.", "Önemli ilaç düzeninizi görünür tutun.", "💊",
        ("Check the dosage", "Take medication", "Record completion"),
        ("Dozu kontrol et", "İlacı al", "Tamamlandığını kaydet"), "Wellbeing", "daily",
    ),
    TaskTemplate(
        "deep_work", "Life", "Yaşam", "Focused work session", "Odaklanmış çalışma",
        "Prepare and complete one distraction-free focus block.", "Dikkat dağıtmadan bir odaklanma oturumu hazırlayın ve tamamlayın.", "◎",
        ("Choose one outcome", "Silence notifications", "Work for 45 minutes", "Review the result"),
        ("Tek bir sonuç seç", "Bildirimleri sessize al", "45 dakika çalış", "Sonucu gözden geçir"), "Work",
    ),
    TaskTemplate(
        "study", "Life", "Yaşam", "Study session", "Ders çalışma oturumu",
        "Turn a broad study goal into a small, finishable session.", "Geniş bir çalışma hedefini küçük ve tamamlanabilir bir oturuma dönüştürün.", "📚",
        ("Choose the topic", "Review notes", "Practice questions", "Write a short summary"),
        ("Konuyu seç", "Notları gözden geçir", "Soruları çöz", "Kısa bir özet yaz"), "Study",
    ),
    TaskTemplate(
        "weekly_plan", "Life", "Yaşam", "Plan the week", "Haftayı planla",
        "Create a realistic overview of the coming week.", "Gelecek hafta için gerçekçi bir genel plan oluşturun.", "▦",
        ("Review unfinished tasks", "Add fixed appointments", "Choose weekly priorities", "Leave recovery time"),
        ("Bitmemiş görevleri gözden geçir", "Sabit randevuları ekle", "Haftalık öncelikleri seç", "Dinlenme zamanı bırak"), "Personal", "weekly",
    ),
    TaskTemplate(
        "shopping", "Life", "Yaşam", "Go shopping", "Alışveriş yap",
        "Prepare a quick shopping trip without forgotten items.", "Unutulan ürünler olmadan hızlı bir alışveriş hazırlayın.", "🛒",
        ("Check supplies", "Write the shopping list", "Take reusable bags", "Put items away"),
        ("Eksikleri kontrol et", "Alışveriş listesini yaz", "Bez çantaları al", "Ürünleri yerleştir"), "Personal",
    ),
    TaskTemplate(
        "clean_home", "Life", "Yaşam", "Clean the house", "Evi temizle",
        "A lightweight room-by-room reset.", "Oda oda hafif bir ev düzenleme rutini.", "⌂",
        ("Clear visible clutter", "Wipe surfaces", "Vacuum or sweep", "Take out the trash"),
        ("Görünen dağınıklığı topla", "Yüzeyleri sil", "Süpür", "Çöpü çıkar"), "Personal", "weekly",
    ),
    TaskTemplate(
        "walk", "Sports", "Spor", "Take a walk", "Yürüyüşe çık",
        "A short outdoor reset for energy and focus.", "Enerji ve odak için kısa bir açık hava molası.", "🚶",
        ("Choose a route", "Bring water", "Walk for 20 minutes"),
        ("Bir rota seç", "Su al", "20 dakika yürü"), "Wellbeing",
    ),
    TaskTemplate(
        "yoga", "Sports", "Spor", "Practice yoga", "Yoga yap",
        "A gentle sequence for mobility and relaxation.", "Hareketlilik ve rahatlama için yumuşak bir seri.", "◌",
        ("Prepare the mat", "Warm up", "Practice the sequence", "Rest for two minutes"),
        ("Matı hazırla", "Isın", "Seriyi uygula", "İki dakika dinlen"), "Wellbeing", "weekly",
    ),
    TaskTemplate(
        "journal", "Mind", "Zihin", "Write in the journal", "Günlük yaz",
        "Pause, reflect, and capture what matters today.", "Durun, düşünün ve bugün önemli olanları yazın.", "✎",
        ("Write one good thing", "Name the main challenge", "Choose tomorrow's first step"),
        ("İyi giden bir şeyi yaz", "Ana zorluğu belirt", "Yarının ilk adımını seç"), "Personal", "daily",
    ),
    TaskTemplate(
        "meditation", "Mind", "Zihin", "Meditate", "Meditasyon yap",
        "A short breathing practice to reset attention.", "Dikkati yenilemek için kısa bir nefes çalışması.", "✦",
        ("Choose a quiet place", "Set a 10-minute timer", "Breathe slowly", "Note how you feel"),
        ("Sessiz bir yer seç", "10 dakikalık zamanlayıcı kur", "Yavaş nefes al", "Nasıl hissettiğini not et"), "Wellbeing", "daily",
    ),
    TaskTemplate(
        "daily_review", "Mind", "Zihin", "Review today", "Bugünü değerlendir",
        "Close the day with a clear mind and a prepared tomorrow.", "Günü zihninizi boşaltarak ve yarına hazırlanarak kapatın.", "✓",
        ("Mark completed tasks", "Move unfinished work", "Write tomorrow's priority", "Clear the workspace"),
        ("Tamamlanan görevleri işaretle", "Bitmeyen işleri taşı", "Yarının önceliğini yaz", "Çalışma alanını düzenle"), "Personal", "daily",
    ),
    TaskTemplate(
        "digital_break", "Habits", "Alışkanlıklar", "Take a screen break", "Ekran molası ver",
        "Step away from the phone and reset your attention.", "Telefondan uzaklaşın ve dikkatinizi yenileyin.", "◐",
        ("Put the phone away", "Move for five minutes", "Look outside", "Return with one intention"),
        ("Telefonu uzağa koy", "Beş dakika hareket et", "Dışarı bak", "Tek bir niyetle geri dön"), "Wellbeing", "daily",
    ),
    TaskTemplate(
        "family_contact", "Habits", "Alışkanlıklar", "Keep in touch with family", "Ailenle iletişim kur",
        "Make regular contact easy to remember.", "Düzenli iletişimi hatırlamayı kolaylaştırın.", "♡",
        ("Choose who to contact", "Call or send a message", "Note anything to follow up"),
        ("Kiminle iletişim kurulacağını seç", "Ara veya mesaj gönder", "Takip edilecek bir şeyi not et"), "Personal", "weekly",
    ),
)


def grouped_templates() -> list[tuple[str, list[TaskTemplate]]]:
    groups: list[tuple[str, list[TaskTemplate]]] = []
    for template in TEMPLATES:
        if not groups or groups[-1][0] != template.group:
            groups.append((template.group, []))
        groups[-1][1].append(template)
    return groups
