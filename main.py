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
    if message.author == bot.user:
        return
    
    # سيقوم البوت بالرد على أي رسالة ترسلها بكلمة "وصلت"
    await message.channel.send(f"وصلت رسالتك: {message.content}")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
