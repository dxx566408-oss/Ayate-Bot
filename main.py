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
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if ":" in message.content:
        try:
            parts = message.content.split(":")
            # تنظيف النص من المسافات وأي حروف زائدة
            surah_input = parts[0].strip()
            ayah_num = parts[1].strip()

            # محاولة جلب البيانات (الـ API يدعم الاسم العربي مباشرة إذا كان دقيقاً)
            url = f"https://api.alquran.cloud/v1/ayah/{surah_input}:{ayah_num}/ar.alafasy"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()['data']
                reply = f"📖 **{data['surah']['name']}** (آية {data['numberInSurah']}):\n> {data['text']}"
                await message.channel.send(reply)
            else:
                # محاولة أخرى: إذا فشل بالاسم، ربما بسبب "الـ" التعريف، نقوم بحذفها وتجربة البحث مجدداً
                if surah_input.startswith("ال"):
                    alt_surah = surah_input[2:] # حذف "ال"
                    url = f"https://api.alquran.cloud/v1/ayah/{alt_surah}:{ayah_num}/ar.alafasy"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()['data']
                        await message.channel.send(f"📖 **{data['surah']['name']}** (آية {data['numberInSurah']}):\n> {data['text']}")
                        return
                
                await message.channel.send("⚠️ لم أجد هذه السورة. جرب كتابة الاسم بدون 'الـ' (مثلاً: فاتحة : 1) أو تأكد من الإملاء.")
        except Exception as e:
            print(f"Error: {e}")

    await bot.process_commands(message)

# تشغيل الويب ثم البوت
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
