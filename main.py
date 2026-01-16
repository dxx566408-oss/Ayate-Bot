import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import os
from flask import Flask
from threading import Thread

# 1. حل مشكلة Render (فتح البورت)
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# القاموس (أضف السور هنا بالأسماء الدقيقة)
surah_map = {
  "الفاتحة": 1, "البقرة": 2, "آل عمران": 3, "النساء": 4, "المائدة": 5,
    "الأنعام": 6, "الأعراف": 7, "الأنفال": 8, "التوبة": 9, "يونس": 10,
    "هود": 11, "يوسف": 12, "الرعد": 13, "إبراهيم": 14, "الحجر": 15,
    "النحل": 16, "الإسراء": 17, "الكهف": 18, "مريم": 19, "طه": 20,
    "الأنبياء": 21, "الحج": 22, "المؤمنون": 23, "النور": 24, "الفرقان": 25,
    "الشعراء": 26, "النمل": 27, "القصص": 28, "العنكبوت": 29, "الروم": 30,
    "لقمان": 31, "السجدة": 32, "الأحزاب": 33, "سبأ": 34, "فاطر": 35,
    "يس": 36, "الصافات": 37, "ص": 38, "الزمير": 39, "غافر": 40,
    "فصلت": 41, "الشورى": 42, "الزخرف": 43, "الدخان": 44, "الجاثية": 45,
    "الأحقاف": 46, "محمد": 47, "الفتح": 48, "الحجرات": 49, "ق": 50,
    "الذاريات": 51, "الطور": 52, "النجم": 53, "القمر": 54, "الرحمن": 55,
    "الواقعة": 56, "الحديد": 57, "المجادلة": 58, "الحشر": 59, "الممتحنة": 60,
    "الصف": 61, "الجمعة": 62, "المنافقون": 63, "التغابن": 64, "الطلاق": 65,
    "التحريم": 66, "الملك": 67, "القلم": 68, "الحاقة": 69, "المعارج": 70,
    "نوح": 71, "الجن": 72, "المزمل": 73, "المدثر": 74, "القيامة": 75,
    "الإنسان": 76, "المرسلات": 77, "النبأ": 78, "النازعات": 79, "عبس": 80,
    "التكوير": 81, "الانفطار": 82, "المطففين": 83, "الانشقاق": 84, "البروج": 85,
    "الطارق": 86, "الأعلى": 87, "الغاشية": 88, "الفجر": 89, "البلد": 90,
    "الشمس": 91, "الليل": 92, "الضحى": 93, "الشرح": 94, "التين": 95,
    "العلق": 96, "القدر": 97, "البينة": 98, "الزلزلة": 99, "العاديات": 100,
    "القارعة": 101, "التكاثر": 102, "العصر": 103, "الهمزة": 104, "الفيل": 105,
    "قريش": 106, "الماعون": 107, "الكوثر": 108, "الكافرون": 109, "النصر": 110,
    "المسد": 111, "الإخلاص": 112, "الفلق": 113, "الناس": 114
}
# 3. واجهة الأزرار (تفسير ونسخ)
class AyahActions(View):
    def __init__(self, surah_id, ayah_num, text):
        super().__init__(timeout=None)
        self.surah_id = surah_id
        self.ayah_num = ayah_num
        self.text = text

    @discord.ui.button(label="تفسير الآية", style=discord.ButtonStyle.primary, emoji="📖")
    async def tafsir_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # جلب التفسير (تفسير الميسر)
        url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.ibnkathir"
        if res.status_code == 200:
            tafsir_text = res.json()['data']['text']
            await interaction.response.send_message(f"📑 **التفسير:**\n{tafsir_text}", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ عذراً، لم أستطع جلب التفسير حالياً.", ephemeral=True)

    @discord.ui.button(label="نسخ الآية", style=discord.ButtonStyle.secondary, emoji="📋")
    async def copy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # إرسال النص في رسالة مخفية لسهولة النسخ
        await interaction.response.send_message(f"يمكنك نسخ النص من هنا:\n`{self.text}`", ephemeral=True)

async def on_message(message):
    if message.author == bot.user: return

    # التحقق من وجود النقطتين وأن الرسالة ليست مجرد رمز تعبيري أو كلام عشوائي
    if ":" in message.content:
        parts = message.content.split(":")
        
        # التأكد أن الرسالة مقسمة لجزئين فقط (قبل وبعد النقطتين)
        if len(parts) == 2:
            raw_surah = parts[0].strip()
            raw_ayah = parts[1].strip()

            # التحقق من أن ما بعد النقطتين هو رقم فعلي (رقم الآية)
            if raw_ayah.isdigit():
                ayah_num = raw_ayah
                
                # البحث عن اسم السورة في القاموس
                target_surah_id = None
                clean_input = clean_text(raw_surah)
                for name, s_id in surah_map.items():
                    if clean_text(name) == clean_input:
                        target_surah_id = s_id
                        real_name = name
                        break

                    # تنسيق الوصف: البسملة في سطر مستقل بخط صغير (Code Block)
                    # ثم نص الآية بخط عريض تحتها
                    if target_surah_id != 1 and target_surah_id != 9:
                        formatted_desc = f"`{basmala}`\n\n**{clean_ayah}**"
                    else:
                        # في الفاتحة (1) تظهر كآية، وفي التوبة (9) لا توجد بسملة
                        formatted_desc = f"**{ayah_text}**"

                    embed = discord.Embed(
                        title=f"📖 سورة {real_name} - آية {ayah_num}",
                        description=formatted_desc,
                        color=discord.Color.blue()
                    )
                    
                    # تأكد أن view تستخدم النص النظيف للنسخ
                    view = AyahActions(target_surah_id, ayah_num, clean_ayah, real_name)
                    await message.channel.send(embed=embed, view=view)
                else:
                    await message.channel.send("⚠️ لم أجد هذه الآية.", delete_after=5)
            else:
                await message.channel.send(f"⚠️ تأكد من كتابة اسم السورة بدقة بالهمزات (مثل: الإنسان : 1).", delete_after=10)
        except Exception as e:
            print(f"Error: {e}")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
