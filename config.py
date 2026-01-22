import os

# بيانات الربط الأساسية
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
CLIENT_ID = "1461289210123260038"
CLIENT_SECRET = "QPCpakqnbkseafSsPQo8XnX4sg975ClZ"
REDIRECT_URI = "https://ayate-bot.onrender.com/login/callback"

# قائمة القراء - يمكنك إضافة أي قارئ جديد هنا بسهولة
RECITERS = [
    {"label": "مشاري العفاسي", "value": "ar.alafasy", "emoji": "🎙️"},
    {"label": "عبدالباسط عبدالصمد", "value": "ar.abdulsamad", "emoji": "🕌"},
    {"label": "محمد المنشاوي", "value": "ar.minshawi", "emoji": "📖"},
    {"label": "ماهر المعيقلي", "value": "ar.mahermuaiqly", "emoji": "🎧"},
    {"label": "ياسر الدوسري", "value": "ar.yasseraddossari", "emoji": "🎙️"}
]

# قائمة التفاسير - يمكنك إضافة المزيد هنا
TAFSIRS = [
    {"label": "تفسير الميسر", "value": "ar.muyassar", "emoji": "📑"},
    {"label": "تفسير الجلالين", "value": "ar.jalalayn", "emoji": "📚"},
    {"label": "تفسير السعدي", "value": "ar.saadi", "emoji": "🖋️"}
]
