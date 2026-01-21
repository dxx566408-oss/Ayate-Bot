import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import requests
import json
import os
from io import BytesIO
from web_panel import keep_alive

# --- 1. إعدادات البوت والبيانات ---
TOKEN = os.getenv('DISCORD_TOKEN') # تأكد من وضع التوكن في البيئة أو هنا مباشرة

# قاعدة البيانات لحفظ (تفضيلات المستخدمين + القنوات المفعلة للسيرفرات)
DB_FILE = 'database.json'

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": {}, "guilds": {}}, f)
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- 2. دوال معالجة النصوص ---
def clean_text(text):
    """تنظيف نص اسم السورة للبحث"""
    return text.strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace(" ", "")

def convert_to_english_nums(text):
    """تحويل الأرقام العربية إلى إنجليزية"""
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    table = str.maketrans(arabic_nums, english_nums)
    return text.translate(table)

# قائمة السور الـ 114 كاملة
surah_map = {
    "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4, "المائدة": 5, "الأنعام": 6, "الأعراف": 7, "الأنفال": 8, "التوبة": 9, "يونس": 10,
    "هود": 11, "يوسف": 12, "الرعد": 13, "إبراهيم": 14, "الحجر": 15, "النحل": 16, "الإسراء": 17, "الكهف": 18, "مريم": 19, "طه": 20,
    "الأنبياء": 21, "الحج": 22, "المؤمنون": 23, "النور": 24, "الفرقان": 25, "الشعراء": 26, "النمل": 27, "القصص": 28, "العنكبوت": 29, "الروم": 30,
    "لقمان": 31, "السجدة": 32, "الأحزاب": 33, "سبأ": 34, "فاطر": 35, "يس": 36, "الصافات": 37, "ص": 38, "الزمر": 39, "غافر": 40,
    "فصلت": 41, "الشورى": 42, "الزخرف": 43, "الدخان": 44, "الجاثية": 45, "الأحقاف": 46, "محمد": 47, "الفتح": 48, "الحجرات": 49, "ق": 50,
    "الذاريات": 51, "الطور": 52, "النجم": 53, "القمر": 54, "الرحمن": 55, "الواقعة": 56, "الحديد": 57, "المجادلة": 58, "الحشر": 59, "الممتحنة": 60,
    "الصف": 61, "الجمعة": 62, "المنافقون": 63, "التغابن": 64, "الطلاق": 65, "التحريم": 66, "الملك": 67, "القلم": 68, "الحاقة": 69, "المعارج": 70,
    "نوح": 71, "الجن": 72, "المزمل": 73, "المدثر": 74, "القيامة": 75, "الإنسان": 76, "المرسلات": 77, "النبأ": 78, "النازعات": 79, "عبس": 80,
    "التكوير": 81, "الانفطار": 82, "المطففين": 83, "الانشقاق": 84, "البروج": 85, "الطارق": 86, "الأعلى": 87, "الغاشية": 88, "الفجر": 89, "البلد": 90,
    "الشمس": 91, "الليل": 92, "الضحى": 93, "الشرح": 94, "التين": 95, "العلق": 96, "القدر": 97, "البينة": 98, "الزلزلة": 99, "العاديات": 100,
    "القارعة": 101, "التكاثر": 102, "العصر": 103, "الهمزة": 104, "الفيل": 105, "قريش": 106, "الماعون": 107, "الكوثر": 108, "الكافرون": 109, "النصر": 110,
    "المسد": 111, "الإخلاص": 112, "الفلق": 113, "الناس": 114
}

# --- 3. مكونات واجهة المستخدم (Select Menus) ---

class ReciterSelect(Select):
    """قائمة منسدلة لاختيار القراء"""
    def __init__(self, surah_id, ayah_num):
        options = [
            discord.SelectOption(label="مشاري العفاسي", value="ar.alafasy", emoji="🎙️"),
            discord.SelectOption(label="عبدالباسط عبدالصمد (مجود)", value="ar.abdulsamad", emoji="🎙️"),
            discord.SelectOption(label="محمد صديق المنشاوي", value="ar.minshawi", emoji="🎙️"),
            discord.SelectOption(label="ماهر المعيقلي", value="ar.mahermuaiqly", emoji="🎙️"),
            discord.SelectOption(label="ياسر الدوسري", value="ar.yasseraddossari", emoji="🎙️"),
            discord.SelectOption(label="ناصر القطامي", value="ar.nasseratalqatami", emoji="🎙️"),
            discord.SelectOption(label="سعود الشريم", value="ar.saoodshuraym", emoji="🎙️")
        ]
        super().__init__(placeholder="اختر القارئ المفضل لديك...", options=options)
        self.surah_id = surah_id
        self.ayah_num = ayah_num

    async def callback(self, interaction: discord.Interaction):
        reciter_code = self.values[0]
        await interaction.response.defer(ephemeral=True)
        
        # جلب الصوت وتشغيله مرة واحدة
        url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/{reciter_code}"
        res = requests.get(url).json()
        audio_url = res['data']['audio']
        audio_content = requests.get(audio_url).content
        
        view = View()
        # زر الاعتماد
        adopt_btn = Button(label="اعتماد هذا القارئ لطلباتي القادمة", style=discord.ButtonStyle.primary, emoji="✅")
        
        async def adopt_cb(itn):
            db = load_db()
            uid = str(itn.user.id)
            if uid not in db["users"]: db["users"][uid] = {}
            db["users"][uid]["reciter"] = reciter_code
            save_db(db)
            await itn.response.send_message("✅ تم حفظ اختيارك. سيتم تشغيل هذا القارئ مباشرة في المرات القادمة.", ephemeral=True)
            
        adopt_btn.callback = adopt_cb
        view.add_item(adopt_btn)
        
        file = discord.File(BytesIO(audio_content), filename="audio.mp3")
        await interaction.followup.send(content="🔊 استمع للتلاوة بصوت المختار:", file=file, view=view, ephemeral=True)

class TafsirSelect(Select):
    """قائمة منسدلة لاختيار التفاسير"""
    def __init__(self, surah_id, ayah_num):
        options = [
            discord.SelectOption(label="تفسير الميسر", value="ar.muyassar", emoji="📖"),
            discord.SelectOption(label="تفسير الجلالين", value="ar.jalalayn", emoji="📖"),
            discord.SelectOption(label="تفسير ابن كثير", value="ar.qortobi", emoji="📖"), # القرطبي كمثال إضافي
        ]
        super().__init__(placeholder="اختر التفسير المفضل لديك...", options=options)
        self.surah_id = surah_id
        self.ayah_num = ayah_num

    async def callback(self, interaction: discord.Interaction):
        tafsir_code = self.values[0]
        url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/{tafsir_code}"
        res = requests.get(url).json()
        tafsir_text = res['data']['text']
        
        view = View()
        adopt_btn = Button(label="اعتماد هذا التفسير دائماً", style=discord.ButtonStyle.primary, emoji="✅")
        
        async def adopt_cb(itn):
            db = load_db()
            uid = str(itn.user.id)
            if uid not in db["users"]: db["users"][uid] = {}
            db["users"][uid]["tafsir"] = tafsir_code
            save_db(db)
            await itn.response.send_message("✅ تم اعتماد نوع التفسير لجميع طلباتك.", ephemeral=True)
            
        adopt_btn.callback = adopt_cb
        view.add_item(adopt_btn)
        
        await interaction.response.send_message(content=f"📑 **التفسير:**\n{tafsir_text}", view=view, ephemeral=True)

# --- 4. الأزرار الأساسية أسفل الآية ---

class AyahActions(View):
    def __init__(self, surah_id, ayah_num, real_name):
        super().__init__(timeout=None)
        self.surah_id = surah_id
        self.ayah_num = ayah_num
        self.real_name = real_name

    @discord.ui.button(label="استماع صوتي", style=discord.ButtonStyle.success, emoji="🎙️")
    async def audio_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = load_db()
        uid = str(interaction.user.id)
        
        # إذا كان لديه قارئ معتمد مسبقاً
        if uid in db["users"] and "reciter" in db["users"][uid]:
            await interaction.response.defer(ephemeral=True)
            reciter = db["users"][uid]["reciter"]
            url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/{reciter}"
            res = requests.get(url).json()
            audio_url = res['data']['audio']
            file = discord.File(BytesIO(requests.get(audio_url).content), filename="audio.mp3")
            
            # زر تغيير القارئ المعتمد يظهر دائماً مع الصوت
            v = View()
            change_btn = Button(label="تغيير القارئ المعتمد", style=discord.ButtonStyle.secondary)
            async def change_cb(itn):
                nv = View(); nv.add_item(ReciterSelect(self.surah_id, self.ayah_num))
                await itn.response.send_message("اختر قارئاً جديداً من القائمة:", view=nv, ephemeral=True)
            change_btn.callback = change_cb
            v.add_item(change_btn)
            
            await interaction.followup.send(content=f"🔊 تلاوة قارئك المفضل ({reciter}):", file=file, view=v, ephemeral=True)
        else:
            # عرض القائمة إذا لم يسبق له الاختيار
            view = View()
            view.add_item(ReciterSelect(self.surah_id, self.ayah_num))
            await interaction.response.send_message("اختر القارئ الذي تود سماع الآية بصوته:", view=view, ephemeral=True)

    @discord.ui.button(label="تفسير الآية", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = load_db()
        uid = str(interaction.user.id)
        
        if uid in db["users"] and "tafsir" in db["users"][uid]:
            tafsir_code = db["users"][uid]["tafsir"]
            url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/{tafsir_code}"
            res = requests.get(url).json()
            
            v = View()
            change_btn = Button(label="تغيير نوع التفسير", style=discord.ButtonStyle.secondary)
            async def change_cb(itn):
                nv = View(); nv.add_item(TafsirSelect(self.surah_id, self.ayah_num))
                await itn.response.send_message("اختر التفسير الجديد:", view=nv, ephemeral=True)
            change_btn.callback = change_cb
            v.add_item(change_btn)
            
            await interaction.response.send_message(content=f"📑 **التفسير المعتمد لديك:**\n{res['data']['text']}", view=v, ephemeral=True)
        else:
            view = View()
            view.add_item(TafsirSelect(self.surah_id, self.ayah_num))
            await interaction.response.send_message("اختر نوع التفسير:", view=view, ephemeral=True)

# --- 5. منطق البوت الأساسي ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    # نظام صلاحيات الرومات (القنوات) من لوحة التحكم
    db = load_db()
    gid = str(message.guild.id)
    cid = str(message.channel.id)
    
    # التحقق: إذا كان السيرفر مسجلاً في لوحة التحكم، يجب أن تكون القناة مفعلة (علامة ✓)
    if gid in db["guilds"]:
        if cid not in db["guilds"][gid]:
            return # القناة معطلة (×)، البوت لا يرد هنا

    if ":" in message.content:
        try:
            parts = message.content.split(":")
            if len(parts) == 2:
                raw_surah = parts[0].strip()
                ayah_num = convert_to_english_nums(parts[1].strip())
                
                if ayah_num.isdigit():
                    clean_input = clean_text(raw_surah)
                    target_id, real_name = None, ""
                    
                    for name, s_id in surah_map.items():
                        if clean_text(name) == clean_input:
                            target_id, real_name = s_id, name
                            break
                    
                    if target_id:
                        res = requests.get(f"https://api.alquran.cloud/v1/ayah/{target_id}:{ayah_num}/quran-simple").json()
                        if 'data' in res:
                            text = res['data']['text'].replace("بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ", "").strip()
                            embed = discord.Embed(
                                title=f"📖 {real_name} - الآية {ayah_num}",
                                description=f"✨ **{text}**",
                                color=discord.Color.gold()
                            )
                            embed.set_footer(text="استخدم الأزرار بالأسفل للتفسير أو الاستماع")
                            
                            await message.channel.send(embed=embed, view=AyahActions(target_id, ayah_num, real_name))
                        else:
                            await message.channel.send(f"❌ لم أجد الآية رقم {ayah_num} في سورة {real_name}.")
        except Exception as e:
            print(f"Error logic: {e}")

@bot.event
async def on_ready():
    print(f'✅ البوت يعمل الآن باسم: {bot.user}')
    print('✅ نظام التفضيلات ولوحة التحكم مفعل.')

# تشغيل نظام البقاء حياً (الموقع)
keep_alive()

# تشغيل البوت
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ خطأ: لم يتم العثور على توكن البوت!")
