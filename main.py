import discord
from discord.ext import commands
import requests
import os
from flask import Flask
from threading import Thread

# --- إبقاء البوت حياً ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# قاموس لترجمة أسماء السور لأرقام (أضفنا أشهرها ويمكنك زيادة الباقي)
surah_map = {
    "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4, "المائدة": 5,
    "الأنعام": 6, "الأعراف": 7, "الأنفال": 8, "التوبة": 9, "يونس": 10,
    "الكهف": 18, "مريم": 19, "طه": 20, "يس": 36, "الرحمن": 55, "الواقعة": 56,
    "الملك": 67, "النبأ": 78, "الإخلاص": 112, "الفلق": 113, "الناس": 114
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ready!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if ":" in message.content:
        try:
            parts = message.content.split(":")
            name = parts[0].strip()
            ayah = parts[1].strip()

            # تحويل الاسم لرقم إذا كان موجوداً في القاموس
            target = surah_map.get(name, name)

            url = f"https://api.alquran.cloud/v1/ayah/{target}:{ayah}/ar.alafasy"
            res = requests.get(url)
            
            if res.status_code == 200:
                data = res.json()['data']
                await message.channel.send(f"📖 **{data['surah']['name']}** (آية {data['numberInSurah']}):\n> {data['text']}")
            else:
                await message.channel.send("⚠️ تأكد من اسم السورة أو رقم الآية (مثال: الفاتحة : 1)")
        except: pass

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
