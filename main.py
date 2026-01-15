import discord
from discord.ext import commands
import requests
import os
from flask import Flask
from threading import Thread

# --- جزء الويب لإرضاء منصة Render ومنع توقف البوت ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()
# -----------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if ":" in message.content:
        try:
            parts = message.content.split(":")
            surah, ayah = parts[0].strip(), parts[1].strip()
            url = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar.alafasy"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()['data']
                await message.channel.send(f"📖 **{data['surah']['name']}** (آية {data['numberInSurah']}):\n> {data['text']}")
        except: pass
    await bot.process_commands(message)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
