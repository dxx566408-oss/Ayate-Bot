import discord, requests, json, os, surahs, config
from discord.ext import commands
from discord.ui import View, Select, Button
from io import BytesIO
from web_panel import keep_alive

# --- كلاس اختيار القارئ أو التفسير مع ذكر الاسم ---
class DynamicSelect(Select):
    def __init__(self, s_id, a_id, mode):
        self.mode = mode
        self.s_id, self.a_id = s_id, a_id
        # جلب الخيارات من config
        self.options_source = config.RECITERS if mode == 'reciter' else config.TAFSIRS
        options = [discord.SelectOption(**o) for o in self.options_source]
        super().__init__(placeholder=f"اختر {'القارئ' if mode == 'reciter' else 'التفسير'}...", options=options)

    async def callback(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        selection_value = self.values[0]
        
        # إيجاد الاسم (Label) المختار لإظهاره للمستخدم
        selected_label = next(item['label'] for item in self.options_source if item['value'] == selection_value)
        
        url = f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{selection_value}"
        res = requests.get(url).json()

        if self.mode == 'reciter':
            audio_url = res['data']['audio']
            file = discord.File(BytesIO(requests.get(audio_url).content), filename="audio.mp3")
            await itn.followup.send(content=f"🎙️ تلاوة القارئ: **{selected_label}**", file=file, ephemeral=True)
        else:
            await itn.followup.send(content=f"📑 **{selected_label}:**\n\n{res['data']['text']}", ephemeral=True)

# --- واجهة الأزرار مع زر "عن السورة" ---
class AyahActions(View):
    def __init__(self, s_id, a_id):
        super().__init__(timeout=None)
        self.s_id, self.a_id = s_id, a_id

    @discord.ui.button(label="استماع", style=discord.ButtonStyle.success, emoji="🎙️")
    async def listen(self, itn, btn):
        v = View(); v.add_item(DynamicSelect(self.s_id, self.a_id, 'reciter'))
        await itn.response.send_message("اختر القارئ المفضل:", view=v, ephemeral=True)

    @discord.ui.button(label="تفسير", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir(self, itn, btn):
        v = View(); v.add_item(DynamicSelect(self.s_id, self.a_id, 'tafsir'))
        await itn.response.send_message("اختر نوع التفسير:", view=v, ephemeral=True)

    @discord.ui.button(label="عن السورة", style=discord.ButtonStyle.secondary, emoji="✨")
    async def about_surah(self, itn, btn):
        await itn.response.defer(ephemeral=True)
        # جلب معلومات السورة من API Quran.com
        info_url = f"https://api.quran.com/api/v4/surah_informations/{self.s_id}?language=ar"
        info_res = requests.get(info_url).json()
        
        # تنظيف النص من أكواد HTML التي قد تأتي من الـ API
        import re
        clean_info = re.sub('<[^<]+?>', '', info_res['surah_information']['short_text'])
        
        embed = discord.Embed(title=f"✨ معلومات حول السورة", color=0x3498db)
        embed.description = clean_info if clean_info else "لا تتوفر معلومات مفصلة حالياً."
        embed.set_footer(text="المصدر: Quran.com")
        await itn.followup.send(embed=embed, ephemeral=True)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_message(msg):
    if msg.author == bot.user: return
    
    if ":" in msg.content:
        parts = msg.content.split(":")
        s_input = surahs.clean_text(parts[0])
        a_num = parts[1].strip()
        
        target_id = None
        for name, sid in surahs.surah_list.items():
            if surahs.clean_text(name) == s_input:
                target_id = sid
                break
        
        if target_id and a_num.isdigit():
            # جلب الآية والاسم الصحيح للسورة
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{target_id}:{a_num}/ar.alafasy").json()
            if 'data' in res:
                s_name_correct = res['data']['surah']['name'] # الاسم العربي الصحيح من الـ API
                embed = discord.Embed(title=f"📖 {s_name_correct} - آية {a_num}", 
                                      description=f"**{res['data']['text']}**", color=0x27ae60)
                await msg.channel.send(embed=embed, view=AyahActions(target_id, a_num))

keep_alive()
bot.run(config.BOT_TOKEN)
