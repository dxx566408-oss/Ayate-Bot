import discord, requests, json, os, surahs, config
from discord.ext import commands
from discord.ui import View, Select, Button
from io import BytesIO
from web_panel import keep_alive

def load_db():
    if not os.path.exists('database.json'): return {"users": {}, "guilds": {}}
    with open('database.json', 'r', encoding='utf-8') as f: return json.load(f)

def save_db(data):
    with open('database.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

class DynamicSelect(Select):
    def __init__(self, s_id, a_id, mode):
        self.mode = mode # 'reciter' or 'tafsir'
        self.s_id, self.a_id = s_id, a_id
        options = [discord.SelectOption(**o) for o in (config.RECITERS if mode == 'reciter' else config.TAFSIRS)]
        super().__init__(placeholder=f"اختر {'القارئ' if mode == 'reciter' else 'التفسير'}...", options=options)

    async def callback(self, itn: discord.Interaction):
        await itn.response.defer(ephemeral=True)
        selection = self.values[0]
        url = f"https://api.alquran.cloud/v1/ayah/{self.s_id}:{self.a_id}/{selection}"
        res = requests.get(url).json()

        if self.mode == 'reciter':
            audio = requests.get(res['data']['audio']).content
            await itn.followup.send(content="🔊 تلاوة الآية:", file=discord.File(BytesIO(audio), filename="audio.mp3"), ephemeral=True)
        else:
            await itn.followup.send(content=f"📑 **التفسير:**\n{res['data']['text']}", ephemeral=True)

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

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_message(msg):
    if msg.author == bot.user: return
    db = load_db()
    gid, cid = str(msg.guild.id), str(msg.channel.id)
    if gid in db["guilds"] and cid not in db["guilds"][gid]: return

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
            res = requests.get(f"https://api.alquran.cloud/v1/ayah/{target_id}:{a_num}/quran-simple").json()
            if 'data' in res:
                embed = discord.Embed(title=f"📖 آية قرآنية", description=f"**{res['data']['text']}**", color=0x27ae60)
                await msg.channel.send(embed=embed, view=AyahActions(target_id, a_num))

keep_alive()
bot.run(config.BOT_TOKEN)
