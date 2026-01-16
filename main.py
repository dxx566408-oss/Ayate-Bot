import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import os
from flask import Flask
from threading import Thread

# 1. إبقاء البوت يعمل
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

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

def clean_text(text):
    return text.strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace(" ", "")

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
# 3. واجهة الأزرار (تفسير + استماع)
class AyahActions(View):
    def __init__(self, surah_id, ayah_num, real_name, total_ayahs):
        super().__init__(timeout=None)
        self.surah_id = surah_id
        self.ayah_num = int(ayah_num)
        self.real_name = real_name
        self.total_ayahs = total_ayahs

        # تعطيل زر "السابقة" إذا كنا في الآية رقم 1
        if self.ayah_num <= 1:
            self.prev_button.disabled = True
        
        # تعطيل زر "التالية" إذا كنا في آخر آية بالسورة
        if self.ayah_num >= self.total_ayahs:
            self.next_button.disabled = True

    @discord.ui.button(label="آية سابقة", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.navigate_ayah(interaction, self.ayah_num - 1)

    @discord.ui.button(label="آية تالية", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.navigate_ayah(interaction, self.ayah_num + 1)
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
        # 1. تأجيل الرد لأن تحميل الملف قد يستغرق ثواني
        await interaction.response.defer(ephemeral=True)
        
        # 2. الحصول على رابط الصوت من الـ API
        api_url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.alafasy"
        res = requests.get(api_url)
        
        if res.status_code == 200:
            audio_url = res.json()['data']['audio']
            
            # 3. تحميل ملف الصوت برمجياً لإرساله كملف وليس كرابط
            audio_res = requests.get(audio_url)
            if audio_res.status_code == 200:
                from io import BytesIO
                audio_file = BytesIO(audio_res.content)
                
                # اسم الملف الذي سيظهر في ديسكورد
                filename = f"{self.surah_id}_{self.ayah_num}.mp3"
                
                # 4. إرسال الملف الصوتي كرسالة مخفية
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
            if len(parts) == 2 and parts[1].strip().isdigit():
                raw_surah = parts[0].strip()
                ayah_num = parts[1].strip()

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
