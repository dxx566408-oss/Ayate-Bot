import discord, requests, json, os, re, surahs, config
from discord.ext import commands
from discord.ui import View, Select, Button
from io import BytesIO
from web_panel import keep_alive

# 1. تحويل الأرقام لضمان الفهم
def ar_to_en_numbers(text):
    arabic_numbers = '٠١٢٣٤٥٦٧٨٩'
    english_numbers = '0123456789'
    return text.translate(str.maketrans(arabic_numbers, english_numbers))

def load_db():
    if not os.path.exists('database.json'): return {"users": {}, "guilds": {}}
    try:
        with open('database.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"users": {}, "guilds": {}}

def save_db(data):
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 2. القائمة المنسدلة مع زر "حفظ وتغيير"
class DynamicSelect(Select):
    def __init__(self, s_id, a_id, mode):
        self.mode = mode
        self.s_id, self.a_id = s_id, a_id
        source = config.RECITERS if mode == 'reciter' else config.TAFSIRS
        options = [discord.SelectOption(**o) for o in source]
        super().__init__(placeholder=f"اختر {'القارئ' if mode == 'reciter' else 'التفسير'}...", options=options)

    async def callback(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        val = self.values[0]
        label = next(item['label'] for item in (config.RECITERS if self.mode == 'reciter' else config.TAFSIRS) if item['value'] == val)
        
        # زر الاعتماد (لحفظ الاختيار أو تغييره)
        view = View()
        btn = Button(label=f"اعتماد {label} كافتراضي", style=discord.ButtonStyle.danger, emoji="✅")
        
        async def save_pref(i):
            db = load_db()
            uid = str(i.user.id)
            if uid not in db["users"]: db["users"][uid] = {}
            db["users"][uid][self.mode] = val # حفظ القيمة الجديدة (تغيير القارئ)
            save_db(db)
            await i.response.send_message(f"✅ تم تحديث إعداداتك إلى: **{label}**", ephemeral=True)
        
        btn.callback = save_pref
        view.add_item(btn)

        res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{val}").json()
        if self.mode == 'reciter':
            audio = requests.get(res['data']['audio']).content
            await itn.followup.send(content=f"🎙️ المختار: **{label}**", file=discord.File(BytesIO(audio), filename="q.mp3"), view=view, ephemeral=True)
        else:
            await itn.followup.send(content=f"📑 **{label}**:\n\n{res['data']['text']}", view=view, ephemeral=True)

# 3. الأزرار الرئيسية مع إصلاح "عن السورة"
class AyahActions(View):
    def __init__(self, s_id, a_id):
        super().__init__(timeout=None)
        self.s_id, self.a_id = s_id, a_id

    @discord.ui.button(label="استماع", style=discord.ButtonStyle.success, emoji="🎙️")
    async def listen(self, itn, btn):
        db = load_db(); uid = str(itn.user.id)
        # إذا وجد قارئ معتمد يرسله مع خيار التغيير
        if uid in db["users"] and "reciter" in db["users"][uid]:
            await itn.response.defer(ephemeral=True)
            rec = db["users"][uid]["reciter"]
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{rec}").json()
            
            v = View(); change = Button(label="تغيير القارئ", style=discord.ButtonStyle.gray)
            change.callback = lambda i: i.response.send_message("اختر قارئاً جديداً:", view=View().add_item(DynamicSelect(self.s_id, self.a_id, 'reciter')), ephemeral=True)
            v.add_item(change)
            
            await itn.followup.send(file=discord.File(BytesIO(requests.get(res['data']['audio']).content), filename="q.mp3"), view=v, ephemeral=True)
        else:
            await itn.response.send_message("اختر قارئاً:", view=View().add_item(DynamicSelect(self.s_id, self.a_id, 'reciter')), ephemeral=True)

    @discord.ui.button(label="تفسير", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir(self, itn, btn):
        db = load_db(); uid = str(itn.user.id)
        if uid in db["users"] and "tafsir" in db["users"][uid]:
            await itn.response.defer(ephemeral=True)
            taf = db["users"][uid]["tafsir"]
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{taf}").json()
            
            v = View(); change = Button(label="تغيير التفسير", style=discord.ButtonStyle.gray)
            change.callback = lambda i: i.response.send_message("اختر تفسيراً جديداً:", view=View().add_item(DynamicSelect(self.s_id, self.a_id, 'tafsir')), ephemeral=True)
            v.add_item(change)
            
            await itn.followup.send(content=f"📑 **التفسير المعتمد:**\n\n{res['data']['text']}", view=v, ephemeral=True)
        else:
            await itn.response.send_message("اختر التفسير:", view=View().add_item(DynamicSelect(self.s_id, self.a_id, 'tafsir')), ephemeral=True)

    @discord.ui.button(label="عن السورة", style=discord.ButtonStyle.secondary, emoji="✨")
    async def about_surah(self, itn, btn):
        await itn.response.defer(ephemeral=True)
        # محاولة جلب المعلومات من رابط بديل وأكثر دقة
        try:
            r = requests.get(f"https://api.quran.com/api/v4/surahs/{self.s_id}/info?language=ar").json()
            txt = re.sub(r'<[^>]*>', '', r['surah_info']['short_text'])
            await itn.followup.send(embed=discord.Embed(title="✨ نبذة عن السورة", description=txt[:2000], color=0x3498db), ephemeral=True)
        except:
            # إذا فشل الرابط، نستخدم API التلاوات لجلب اسم السورة ونوعها كبديل
            r = requests.get(f"https://api.alquran.cloud/v1/surah/{self.s_id}").json()
            d = r['data']
            msg = f"السورة: {d['name']}\nعدد الآيات: {d['numberOfAyahs']}\nالنوع: {d['revelationType']}"
            await itn.followup.send(msg, ephemeral=True)

# 4. تشغيل البوت
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_message(msg):
    if msg.author == bot.user: return
    content = ar_to_en_numbers(msg.content)
    if ":" in content:
        parts = content.split(":")
        s_name = surahs.clean_text(parts[0])
        a_num = parts[1].strip()
        
        sid = None
        for name, idx in surahs.surah_list.items():
            if surahs.clean_text(name) == s_name:
                sid = idx; break
        
        if sid and a_num.isdigit():
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{sid}:{a_num}/quran-simple").json()
            if 'data' in res:
                await msg.channel.send(embed=discord.Embed(title=f"📖 {res['data']['surah']['name']} - {a_num}", description=f"**{res['data']['text']}**", color=0x2ecc71), view=AyahActions(sid, a_num))

keep_alive()
bot.run(config.BOT_TOKEN)
