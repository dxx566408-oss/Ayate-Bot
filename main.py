import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import os
from flask import Flask
from threading import Thread

# 1. ط¥ط¨ظ‚ط§ط، ط§ظ„ط¨ظˆطھ ظٹط¹ظ…ظ„
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. ط¥ط¹ط¯ط§ط¯ط§طھ ط¯ظٹط³ظƒظˆط±ط¯
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def clean_text(text):
    return text.strip().replace("ط£", "ط§").replace("ط¥", "ط§").replace("ط¢", "ط§").replace("ط©", "ظ‡").replace(" ", "")

# --- ظ‚ط§ط¦ظ…ط© ط§ظ„ط³ظˆط± (ط£ظƒظ…ظ„ظ‡ط§ ظ‡ظ†ط§) ---
surah_map = {
    "ط§ظ„ظپط§طھط­ط©": 1, "ط§ظ„ط¨ظ‚ط±ط©": 2, "ط¢ظ„ ط¹ظ…ط±ط§ظ†": 3, "ط§ظ„ظ†ط³ط§ط،": 4, "ط§ظ„ظ…ط§ط¦ط¯ط©": 5,
    "ط§ظ„ط£ظ†ط¹ط§ظ…": 6, "ط§ظ„ط£ط¹ط±ط§ظپ": 7, "ط§ظ„ط£ظ†ظپط§ظ„": 8, "ط§ظ„طھظˆط¨ط©": 9, "ظٹظˆظ†ط³": 10,
    "ظ‡ظˆط¯": 11, "ظٹظˆط³ظپ": 12, "ط§ظ„ط±ط¹ط¯": 13, "ط¥ط¨ط±ط§ظ‡ظٹظ…": 14, "ط§ظ„ط­ط¬ط±": 15,
    "ط§ظ„ظ†ط­ظ„": 16, "ط§ظ„ط¥ط³ط±ط§ط،": 17, "ط§ظ„ظƒظ‡ظپ": 18, "ظ…ط±ظٹظ…": 19, "ط·ظ‡": 20,
    "ط§ظ„ط£ظ†ط¨ظٹط§ط،": 21, "ط§ظ„ط­ط¬": 22, "ط§ظ„ظ…ط¤ظ…ظ†ظˆظ†": 23, "ط§ظ„ظ†ظˆط±": 24, "ط§ظ„ظپط±ظ‚ط§ظ†": 25,
    "ط§ظ„ط´ط¹ط±ط§ط،": 26, "ط§ظ„ظ†ظ…ظ„": 27, "ط§ظ„ظ‚طµطµ": 28, "ط§ظ„ط¹ظ†ظƒط¨ظˆطھ": 29, "ط§ظ„ط±ظˆظ…": 30,
    "ظ„ظ‚ظ…ط§ظ†": 31, "ط§ظ„ط³ط¬ط¯ط©": 32, "ط§ظ„ط£ط­ط²ط§ط¨": 33, "ط³ط¨ط£": 34, "ظپط§ط·ط±": 35,
    "ظٹط³": 36, "ط§ظ„طµط§ظپط§طھ": 37, "طµ": 38, "ط§ظ„ط²ظ…ط±": 39, "ط؛ط§ظپط±": 40,
    "ظپطµظ„طھ": 41, "ط§ظ„ط´ظˆط±ظ‰": 42, "ط§ظ„ط²ط®ط±ظپ": 43, "ط§ظ„ط¯ط®ط§ظ†": 44, "ط§ظ„ط¬ط§ط«ظٹط©": 45,
    "ط§ظ„ط£ط­ظ‚ط§ظپ": 46, "ظ…ط­ظ…ط¯": 47, "ط§ظ„ظپطھط­": 48, "ط§ظ„ط­ط¬ط±ط§طھ": 49, "ظ‚": 50,
    "ط§ظ„ط°ط§ط±ظٹط§طھ": 51, "ط§ظ„ط·ظˆط±": 52, "ط§ظ„ظ†ط¬ظ…": 53, "ط§ظ„ظ‚ظ…ط±": 54, "ط§ظ„ط±ط­ظ…ظ†": 55,
    "ط§ظ„ظˆط§ظ‚ط¹ط©": 56, "ط§ظ„ط­ط¯ظٹط¯": 57, "ط§ظ„ظ…ط¬ط§ط¯ظ„ط©": 58, "ط§ظ„ط­ط´ط±": 59, "ط§ظ„ظ…ظ…طھط­ظ†ط©": 60,
    "ط§ظ„طµظپ": 61, "ط§ظ„ط¬ظ…ط¹ط©": 62, "ط§ظ„ظ…ظ†ط§ظپظ‚ظˆظ†": 63, "ط§ظ„طھط؛ط§ط¨ظ†": 64, "ط§ظ„ط·ظ„ط§ظ‚": 65,
    "ط§ظ„طھط­ط±ظٹظ…": 66, "ط§ظ„ظ…ظ„ظƒ": 67, "ط§ظ„ظ‚ظ„ظ…": 68, "ط§ظ„ط­ط§ظ‚ط©": 69, "ط§ظ„ظ…ط¹ط§ط±ط¬": 70,
    "ظ†ظˆط­": 71, "ط§ظ„ط¬ظ†": 72, "ط§ظ„ظ…ط²ظ…ظ„": 73, "ط§ظ„ظ…ط¯ط«ط±": 74, "ط§ظ„ظ‚ظٹط§ظ…ط©": 75,
    "ط§ظ„ط¥ظ†ط³ط§ظ†": 76, "ط§ظ„ظ…ط±ط³ظ„ط§طھ": 77, "ط§ظ„ظ†ط¨ط£": 78, "ط§ظ„ظ†ط§ط²ط¹ط§طھ": 79, "ط¹ط¨ط³": 80,
    "ط§ظ„طھظƒظˆظٹط±": 81, "ط§ظ„ط§ظ†ظپط·ط§ط±": 82, "ط§ظ„ظ…ط·ظپظپظٹظ†": 83, "ط§ظ„ط§ظ†ط´ظ‚ط§ظ‚": 84, "ط§ظ„ط¨ط±ظˆط¬": 85,
    "ط§ظ„ط·ط§ط±ظ‚": 86, "ط§ظ„ط£ط¹ظ„ظ‰": 87, "ط§ظ„ط؛ط§ط´ظٹط©": 88, "ط§ظ„ظپط¬ط±": 89, "ط§ظ„ط¨ظ„ط¯": 90,
    "ط§ظ„ط´ظ…ط³": 91, "ط§ظ„ظ„ظٹظ„": 92, "ط§ظ„ط¶ط­ظ‰": 93, "ط§ظ„ط´ط±ط­": 94, "ط§ظ„طھظٹظ†": 95,
    "ط§ظ„ط¹ظ„ظ‚": 96, "ط§ظ„ظ‚ط¯ط±": 97, "ط§ظ„ط¨ظٹظ†ط©": 98, "ط§ظ„ط²ظ„ط²ظ„ط©": 99, "ط§ظ„ط¹ط§ط¯ظٹط§طھ": 100,
    "ط§ظ„ظ‚ط§ط±ط¹ط©": 101, "ط§ظ„طھظƒط§ط«ط±": 102, "ط§ظ„ط¹طµط±": 103, "ط§ظ„ظ‡ظ…ط²ط©": 104, "ط§ظ„ظپظٹظ„": 105,
    "ظ‚ط±ظٹط´": 106, "ط§ظ„ظ…ط§ط¹ظˆظ†": 107, "ط§ظ„ظƒظˆط«ط±": 108, "ط§ظ„ظƒط§ظپط±ظˆظ†": 109, "ط§ظ„ظ†طµط±": 110,
    "ط§ظ„ظ…ط³ط¯": 111, "ط§ظ„ط¥ط®ظ„ط§طµ": 112, "ط§ظ„ظپظ„ظ‚": 113, "ط§ظ„ظ†ط§ط³": 114
}
# 3. ظˆط§ط¬ظ‡ط© ط§ظ„ط£ط²ط±ط§ط± (طھظپط³ظٹط± + ط§ط³طھظ…ط§ط¹)
class AyahActions(View):
    def __init__(self, surah_id, ayah_num, real_name):
        super().__init__(timeout=None)
        self.surah_id = surah_id
        self.ayah_num = ayah_num
        self.real_name = real_name

    @discord.ui.button(label="طھظپط³ظٹط± ط§ظ„ظ…ظٹط³ط±", style=discord.ButtonStyle.primary, emoji="ًں“–")
    async def tafsir_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.muyassar"
        res = requests.get(url)
        if res.status_code == 200:
            tafsir_data = res.json()['data']['text']
            if len(tafsir_data) > 1900: tafsir_data = tafsir_data[:1900] + "..."
            await interaction.response.send_message(f"ًں“‘ **ط§ظ„طھظپط³ظٹط± ط§ظ„ظ…ظٹط³ط± - {self.real_name} ({self.ayah_num}):**\n\n{tafsir_data}", ephemeral=True)

    @discord.ui.button(label="ط§ط³طھظ…ط§ط¹ ظ„ظ„ط¢ظٹط©", style=discord.ButtonStyle.success, emoji="ًںژ™ï¸ڈ")
    async def audio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. طھط£ط¬ظٹظ„ ط§ظ„ط±ط¯ ظ„ط£ظ† طھط­ظ…ظٹظ„ ط§ظ„ظ…ظ„ظپ ظ‚ط¯ ظٹط³طھط؛ط±ظ‚ ط«ظˆط§ظ†ظٹ
        await interaction.response.defer(ephemeral=True)
        
        # 2. ط§ظ„ط­طµظˆظ„ ط¹ظ„ظ‰ ط±ط§ط¨ط· ط§ظ„طµظˆطھ ظ…ظ† ط§ظ„ظ€ API
        api_url = f"https://api.alquran.cloud/v1/ayah/{self.surah_id}:{self.ayah_num}/ar.alafasy"
        res = requests.get(api_url)
        
        if res.status_code == 200:
            audio_url = res.json()['data']['audio']
            
            # 3. طھط­ظ…ظٹظ„ ظ…ظ„ظپ ط§ظ„طµظˆطھ ط¨ط±ظ…ط¬ظٹط§ظ‹ ظ„ط¥ط±ط³ط§ظ„ظ‡ ظƒظ…ظ„ظپ ظˆظ„ظٹط³ ظƒط±ط§ط¨ط·
            audio_res = requests.get(audio_url)
            if audio_res.status_code == 200:
                from io import BytesIO
                audio_file = BytesIO(audio_res.content)
                
                # ط§ط³ظ… ط§ظ„ظ…ظ„ظپ ط§ظ„ط°ظٹ ط³ظٹط¸ظ‡ط± ظپظٹ ط¯ظٹط³ظƒظˆط±ط¯
                filename = f"{self.surah_id}_{self.ayah_num}.mp3"
                
                # 4. ط¥ط±ط³ط§ظ„ ط§ظ„ظ…ظ„ظپ ط§ظ„طµظˆطھظٹ ظƒط±ط³ط§ظ„ط© ظ…ط®ظپظٹط©
                file = discord.File(audio_file, filename=filename)
                await interaction.followup.send(
                    content=f"ًں”ٹ **طھظ„ط§ظˆط© ط§ظ„ط¢ظٹط© ط¨طµظˆطھ ط§ظ„ط´ظٹط® ظ…ط´ط§ط±ظٹ ط§ظ„ط¹ظپط§ط³ظٹ:**",
                    file=file,
                    ephemeral=True
                )
            else:
                await interaction.followup.send("âڑ ï¸ڈ طھط¹ط°ط± طھط­ظ…ظٹظ„ ظ…ظ„ظپ ط§ظ„طµظˆطھ ط­ط§ظ„ظٹط§ظ‹.", ephemeral=True)
        else:
            await interaction.followup.send("âڑ ï¸ڈ ط¹ط°ط±ط§ظ‹طŒ ظ„ظ… ط£ط¬ط¯ ظ…ظ„ظپط§ظ‹ طµظˆطھظٹط§ظ‹ ظ„ظ‡ط°ظ‡ ط§ظ„ط¢ظٹط©.", ephemeral=True)

# 4. ظ…ط¹ط§ظ„ط¬ط© ط§ظ„ط±ط³ط§ط¦ظ„
@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if ":" in message.content:
        try:
            parts = message.content.split(":")
            if len(parts) == 2 and parts[1].strip().isdigit():
                raw_surah = parts[0].strip()
                ayah_num = parts[1].strip()

                target_surah_id = None
                real_name = ""
                clean_input = clean_text(raw_surah)
                
                for name, s_id in surah_map.items():
                    if clean_text(name) == clean_input:
                        target_surah_id = s_id
                        real_name = name
                        break

                if target_surah_id:
                    url = f"https://api.alquran.cloud/v1/ayah/{target_surah_id}:{ayah_num}/quran-simple"
                    res = requests.get(url)
                    
                    if res.status_code == 200:
                        data = res.json()['data']
                        ayah_text = data['text']
                        basmala = "ط¨ظگط³ظ’ظ…ظگ ط§ظ„ظ„ظ‘ظژظ‡ظگ ط§ظ„ط±ظ‘ظژط­ظ’ظ…ظژظ†ظگ ط§ظ„ط±ظ‘ظژط­ظگظٹظ…ظگ"
                        clean_ayah = ayah_text.replace(basmala, "").strip()

                        embed = discord.Embed(
                            title=f"ًں“– {real_name} - {ayah_num}",
                            description=f"**{clean_ayah}**",
                            color=discord.Color.blue()
                        )
                        
                        view = AyahActions(target_surah_id, ayah_num, real_name)
                        await message.channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"Error: {e}")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
