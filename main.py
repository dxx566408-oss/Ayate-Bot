import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import os
from flask import Flask
from threading import Thread
from io import BytesIO
import json
from flask import Flask, render_template_string, request

# 1. نظام إبقاء البوت يعمل + لوحة التحكم
app = Flask('')

# متغيرات لتخزين الإعدادات (يمكنك تعديلها من الموقع)
settings = {
    "reciter": "ar.alafasy",  # كود القارئ الافتراضي
    "status": "Online"
}

@app.route('/')
def home():
    # تصميم صفحة الموقع (HTML)
    return f"""
    <dir dir="rtl" style="text-align: center; font-family: sans-serif; background-color: #f4f4f4; padding: 50px;">
        <div style="background: white; padding: 20px; border-radius: 10px; display: inline-block; shadow: 0px 0px 10px #ccc;">
            <h1 style="color: #333;">لوحة تحكم بوت الآيات</h1>
            <p>حالة البوت: <span style="color: green; font-weight: bold;">{settings['status']}</span></p>
            <hr>
            <form action="/update" method="post">
                <p>تغيير القارئ (أدخل كود القارئ):</p>
                <input type="text" name="reciter_code" value="{settings['reciter']}" style="padding: 8px; width: 200px; border: 1px solid #ccc;">
                <br><br>
                <button type="submit" style="background-color: #2ecc71; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">حفظ التغييرات</button>
            </form>
            <p style="font-size: 12px; color: #666;">أكواد القراء المتاحة: ar.alafasy, ar.minshawi, ar.abdulsamad</p>
        </div>
    </dir>
    """

@app.route('/update', methods=['POST'])
def update():
    from flask import request
    # استقبال البيانات الجديدة من الموقع وتحديث متغير الإعدادات
    new_reciter = request.form.get("reciter_code")
    if new_reciter:
        settings['reciter'] = new_reciter
    return """
    <div style="text-align: center; padding-top: 50px; font-family: sans-serif;">
        <h2 style="color: green;">✅ تم التحديث بنجاح!</h2>
        <p>البوت الآن يستخدم القارئ الجديد. يمكنك إغلاق هذه الصفحة.</p>
        <a href="/">العودة للرئيسية</a>
    </div>
    """

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات ديسكورد
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# دالة تنظيف النصوص
def clean_text(text):
    return text.strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace(" ", "")

# دالة تحويل الأرقام العربية/الفارسية إلى إنجليزية
def convert_to_english_nums(text):
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    translation_table = str.maketrans(arabic_nums, english_nums)
    return text.translate(translation_table)

# --- قائمة السور (أكملها هنا) ---
surah_map = {
    "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4, "المائدة": 5,
    "الأنعام": 6, "الأعراف": 7, "الأنفال": 8, "التوبة": 9, "يونس": 10,
    "هود": 11, "يوسف": 12, "الرعد": 13, "إبراهيم": 14, "الحجر": 15,
    "النحل": 16, "الإسراء": 17, "الكهف": 18, "مريم": 19, "طه": 20,
    "الأنبياء": 21, "الحج": 22, "المؤمنون": 23, "النور": 24, "الفرقان": 25,
    "الشعراء": 26, "النمل": 27, "القصص": 28, "العنكبوت": 29, "الروم": 30,
    "لقمان": 31, "السجدة": 32, "الأحزاب": 33, "سبأ": 34, "فاطر": 35,
    "يس": 36, "الصافات": 37, "ص": 38, "الزمر": 39, "غافر": 40,
    "فصلت": 41, "الشورى": 42, "الزخرف": 43, "الدخان": 44, "الجاثية": 45,
    "الأحقاف": 46, "محمد": 47, "الفتح": 48, "الحجرات": 49, "ق": 50,
    "الذاريات": 51, "الطور": 52, "النجم": 53, "القمر": 54, "الرحمن": 55,
    "الواقعة": 56, "الحديد": 57, "المجادلة": 58, "الحشر": 59, "الممتحنة": 60,
    "الصف": 61, "الجمعة": 62, "المنافقون": 63, "التغابن": 64, "الطلاق": 65,
    "التحريم": 66, "الملك": 67, "القلم": 68, "الحاقة": 69, "المعارج": 70,
    "نوح": 71, "الجن": 72, "المزمل": 73, "المدثر": 74, "القيامة": 75,
    "الإنسان": 76, "المرسلات": 77, "النبأ": 78, "النازعات": 79, "عبس": 80,
    "التكوير": 81, "الانفطار": 82, "المطففين": 83, "الانشقاق": 84, "البروج": 85,
    "الطارق": 86, "الأعلى": 87, "الغاشية": 88, "الفجر": 89, "البلد": 90,
    "الشمس": 91, "الليل": 92, "الضحى": 93, "الشرح": 94, "التين": 95,
    "العلق": 96, "القدر": 97, "البينة": 98, "الزلزلة": 99, "العاديات": 100,
    "القارعة": 101, "التكاثر": 102, "العصر": 103, "الهمزة": 104, "الفيل": 105,
    "قريش": 106, "الماعون": 107, "الكوثر": 108, "الكافرون": 109, "النصر": 110,
    "المسد": 111, "الإخلاص": 112, "الفلق": 113, "الناس": 114
    }

# 3. واجهة الأزرار (تفسير الميسر + استماع صوتي)
class AyahActions(View):
    def __init__(self, surah_id, ayah_num, real_name):
        super().__init__(timeout=None)
        self.surah_id = surah_id
        self.ayah_num = ayah_num
        self.real_name = real_name

    @discord.ui.button(label="تفسير الميسر", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.muyassar"
        res = requests.get(url)
        if res.status_code == 200:
            tafsir_data = res.json()['data']['text']
            if len(tafsir_data) > 1900: tafsir_data = tafsir_data[:1900] + "..."
            await interaction.response.send_message(f"📑 **التفسير الميسر - {self.real_name} ({self.ayah_num}):**\n\n{tafsir_data}", ephemeral=True)

    @discord.ui.button(label="استماع للآية", style=discord.ButtonStyle.success, emoji="🎙️")
    async def audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        api_url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.alafasy"
        res = requests.get(api_url)
        
        if res.status_code == 200:
            audio_url = res.json()['data']['audio']
            audio_res = requests.get(audio_url)
            if audio_res.status_code == 200:
                audio_file = BytesIO(audio_res.content)
                filename = f"{self.surah_id}_{self.ayah_num}.mp3"
                file = discord.File(audio_file, filename=filename)
                await interaction.followup.send(
                    content=f"🔊 **تلاوة الآية بصوت الشيخ مشاري العفاسي:**",
                    file=file,
                    ephemeral=True
                )
            else:
                await interaction.followup.send("⚠️ تعذر تحميل ملف الصوت حالياً.", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ عذراً، لم أجد ملفاً صوتياً لهذه الآية.", ephemeral=True)

# 4. معالجة الرسائل
@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if ":" in message.content:
        try:
            parts = message.content.split(":")
            if len(parts) == 2:
                raw_surah = parts[0].strip()
                # تطبيق تحويل الأرقام هنا لتعمل الأرقام العربية
                ayah_num = convert_to_english_nums(parts[1].strip())

                if ayah_num.isdigit():
                    target_surah_id = None
                    real_name = ""
                    clean_input = clean_text(raw_surah)
                    
                    for name, s_id in surah_map.items():
                        if clean_text(name) == clean_input:
                            target_surah_id = s_id
                            real_name = name
                            break

                    if target_surah_id:
                        url = f"https://api.alquran.cloud/v1/ayah/{target_surah_id}:{ayah_num}/quran-simple"
                        res = requests.get(url)
                        
                        if res.status_code == 200:
                            data = res.json()['data']
                            ayah_text = data['text']
                            basmala = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
                            clean_ayah = ayah_text.replace(basmala, "").strip()

                            embed = discord.Embed(
                                title=f"📖 {real_name} - {ayah_num}",
                                description=f"**{clean_ayah}**",
                                color=discord.Color.blue()
                            )
                            
                            view = AyahActions(target_surah_id, ayah_num, real_name)
                            await message.channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"Error: {e}")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
