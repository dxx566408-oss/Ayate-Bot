import discord
from discord.ext import commands
import requests
import os
from flask import Flask
from threading import Thread

# سيرفر ويب بسيط لإبقاء البوت حياً (يتماشى مع الرابط في Cron-job)
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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is connected and ready!')

@bot.event
async def on_message(message):
    # تجاهل رسائل البوت نفسه
    if message.author == bot.user:
        return

    # البحث عن النقطتين : لضمان أن المستخدم يطلب آية
    if ":" in message.content:
        try:
            # تقسيم الرسالة (مثال: الفاتحة : 1)
            parts = message.content.split(":")
            surah_name = parts[0].strip()
            ayah_num = parts[1].strip()

            # جلب الآية من API القرآن الكريم بصوت العفاسي (نصي)
            url = f"https://api.alquran.cloud/v1/ayah/{surah_name}:{ayah_num}/ar.alafasy"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()['data']
                # تنسيق الرد بشكل جميل
                reply = f"📖 **{data['surah']['name']}** (آية {data['numberInSurah']}):\n> {data['text']}"
                await message.channel.send(reply)
            else:
                # إذا لم يجد السورة أو الآية
                await message.channel.send("⚠️ لم أجد هذه الآية. تأكد من كتابة: (اسم السورة : رقم الآية).")
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)

# تشغيل الويب ثم البوت
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
