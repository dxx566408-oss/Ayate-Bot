from flask import Flask, request, redirect, render_template_string
import json
import os
from threading import Thread

app = Flask('')

# دالات لقراءة وحفظ الإعدادات من ملف JSON
def get_config():
    with open('settings.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('settings.json', 'w') as f:
        json.dump(config, f, indent=4)

@app.route('/')
def home():
    config = get_config()
    # تصميم الواجهة الاحترافية
    return render_template_string(f"""
    <dir dir="rtl" style="margin:0; padding:0; background: #2c2f33; color: white; font-family: sans-serif; height: 100vh; display: flex; align-items: center; justify-content: center;">
        <div style="background: #23272a; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 450px;">
            <h1 style="color: #7289da;">لوحة التحكم</h1>
            <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 25px;">
                <a href="https://discord.com/api/oauth2/authorize?client_id={{ config['client_id'] }}&response_type=code&scope=identify" 
                   style="background: #5865f2; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-size: 14px;">🔐 دخول ديسكورد</a>
                
                <a href="{{ config['invite_link'] }}" target="_blank"
                   style="background: #43b581; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-size: 14px;">➕ دعوة البوت</a>
            </div>

            <form action="/update" method="post" style="text-align: right; background: #2c2f33; padding: 20px; border-radius: 10px;">
                <label>القارئ الحالي في البوت:</label>
                <select name="reciter" style="width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; background: #23272a; color: white; border: 1px solid #7289da;">
                    <option value="ar.alafasy" {"selected" if config['reciter'] == "ar.alafasy" else ""}>مشاري العفاسي</option>
                    <option value="ar.minshawi" {"selected" if config['reciter'] == "ar.minshawi" else ""}>المنشاوي</option>
                    <option value="ar.abdulsamad" {"selected" if config['reciter'] == "ar.abdulsamad" else ""}>عبدالباسط عبدالصمد</option>
                </select>
                <button type="submit" style="width: 100%; background: #faa61a; color: white; padding: 12px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">حفظ التغييرات</button>
            </form>
        </div>
    </dir>
    """, config=config)

@app.route('/update', methods=['POST'])
def update():
    config = get_config()
    config['reciter'] = request.form.get("reciter")
    save_config(config)
    return redirect("/")

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
