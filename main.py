import discord, requests, json, os, re, surahs, config
from discord.ext import commands
from discord.ui import View, Select, Button
from io import BytesIO
from web_panel import keep_alive

def ar_to_en_numbers(text):
    arabic_numbers = '٠١٢٣٤٥٦٧٨٩'
    english_numbers = '0123456789'
    translation_table = str.maketrans(arabic_numbers, english_numbers)
    return text.translate(translation_table)

def load_db():
    if not os.path.exists('database.json'): return {"users": {}, "guilds": {}}
    with open('database.json', 'r', encoding='utf-8') as f: return json.load(f)

def save_db(data):
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- قائمة اختيار مع خيار الاعتماد ---
class DynamicSelect(Select):
    def __init__(self, s_id, a_id, mode):
        self.mode = mode
        self.s_id, self.a_id = s_id, a_id
        self.options_source = config.RECITERS if mode == 'reciter' else config.TAFSIRS
        options = [discord.SelectOption(**o) for o in self.options_source]
        super().__init__(placeholder=f"اختر {'القارئ' if mode == 'reciter' else 'التفسير'}...", options=options)

    async def callback(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        selection_value = self.values[0]
        selected_label = next(item['label'] for item in self.options_source if item['value'] == selection_value)
        
        # جلب البيانات
        res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{selection_value}").json()

        # زر الاعتماد (للمستقبل)
        view = View()
        adopt_btn = Button(label=f"اعتماد {selected_label}", style=discord.ButtonStyle.danger, emoji="✅")
        
        async def adopt_callback(interaction):
            db = load_db()
            u_id = str(interaction.user.id)
            if u_id not in db["users"]: db["users"][u_id] = {}
            # حفظ منفصل للقارئ والتفسير
            db["users"][u_id][self.mode] = selection_value
            save_db(db)
            await interaction.response.send_message(f"✅ تم اعتماد **{selected_label}** كاختيار افتراضي.", ephemeral=True)
        
        adopt_btn.callback = adopt_callback
        view.add_item(adopt_btn)

        if self.mode == 'reciter':
            audio = requests.get(res['data']['audio']).content
            await itn.followup.send(content=f"🎙️ **{selected_label}**", file=discord.File(BytesIO(audio), filename="q.mp3"), view=view, ephemeral=True)
        else:
            await itn.followup.send(content=f"📑 **{selected_label}**:\n\n{res['data']['text']}", view=view, ephemeral=True)

# --- الواجهة الرئيسية تحت الآية ---
class AyahActions(View):
    def __init__(self, s_id, a_id):
        super().__init__(timeout=None)
        self.s_id, self.a_id = s_id, a_id

    @discord.ui.button(label="استماع", style=discord.ButtonStyle.success, emoji="🎙️")
    async def listen(self, itn, btn):
        db = load_db(); u_id = str(itn.user.id)
        if u_id in db["users"] and "reciter" in db["users"][u_id]:
            await itn.response.defer(ephemeral=True)
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{db['users'][u_id]['reciter']}").json()
            # إضافة زر تغيير القارئ في الرد التلقائي
            v = View(); change_btn = Button(label="تغيير القارئ الافتراضي", style=discord.ButtonStyle.secondary)
            async def change_rec(i):
                v_new = View(); v_new.add_item(DynamicSelect(self.s_id, self.a_id, 'reciter'))
                await i.response.send_message("اختر قارئاً جديداً لاعتماده:", view=v_new, ephemeral=True)
            change_btn.callback = change_rec; v.add_item(change_btn)
            
            await itn.followup.send(file=discord.File(BytesIO(requests.get(res['data']['audio']).content), filename="q.mp3"), view=v, ephemeral=True)
        else:
            v = View(); v.add_item(DynamicSelect(self.s_id, self.a_id, 'reciter'))
            await itn.response.send_message("اختر قارئاً:", view=v, ephemeral=True)

    @discord.ui.button(label="تفسير", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir(self, itn, btn):
        db = load_db(); u_id = str(itn.user.id)
        if u_id in db["users"] and "tafsir" in db["users"][u_id]:
            await itn.response.defer(ephemeral=True)
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{db['users'][u_id]['tafsir']}").json()
            
            v = View(); change_btn = Button(label="تغيير التفسير الافتراضي", style=discord.ButtonStyle.secondary)
            async def change_taf(i):
                v_new = View(); v_new.add_item(DynamicSelect(self.s_id, self.a_id, 'tafsir'))
                await i.response.send_message("اختر تفسيراً جديداً لاعتماده:", view=v_new, ephemeral=True)
            change_btn.callback = change_taf; v.add_item(change_btn)
            
            await itn.followup.send(content=f"📑 **التفسير المعتمد لديك:**\n\n{res['data']['text']}", view=v, ephemeral=True)
        else:
            v = View(); v.add_item(DynamicSelect(self.s_id, self.a_id, 'tafsir'))
            await itn.response.send_message("اختر التفسير:", view=v, ephemeral=True)

    @discord.ui.button(label="عن السورة", style=discord.ButtonStyle.secondary, emoji="✨")
    async def about_surah(self, itn, btn):
        await itn.response.defer(ephemeral=True)
        # استخدام رابط الـ API البديل والأكثر استقراراً
        try:
            r = requests.get(f"https://api.quran.com/api/v4/surahs/{self.s_id}/info?language=ar").json()
            info_text = r['surah_info']['short_text']
            # تنظيف النص من أكواد HTML
            clean_info = re.sub(r'<[^>]*>', '', info_text)
            embed = discord.Embed(title="✨ نبذة عن السورة", description=clean_info[:2000], color=0x3498db)
            await itn.followup.send(embed=embed, ephemeral=True)
        except:
            # محاولة جلب وصف بسيط إذا فشل الرابط الأول
            await itn.followup.send("تعذر جلب تفاصيل السورة حالياً، يرجى المحاولة لاحقاً.", ephemeral=True)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_message(msg):
    if msg.author == bot.user: return
    content = ar_to_en_numbers(msg.content)
    if ":" in content:
        parts = content.split(":")
        s_input = surahs.clean_text(parts[0])
        a_input = parts[1].strip()
        target_id = None
        for name, sid in surahs.surah_list.items():
            if surahs.clean_text(name) == s_input:
                target_id = sid; break
        if target_id and a_input.isdigit():
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{target_id}:{a_input}/quran-simple").json()
            if 'data' in res:
                embed = discord.Embed(title=f"📖 {res['data']['surah']['name']} - {a_input}", description=f"**{res['data']['text']}**", color=0x2ecc71)
                await msg.channel.send(embed=embed, view=AyahActions(target_id, a_input))

keep_alive()
bot.run(config.BOT_TOKEN)
