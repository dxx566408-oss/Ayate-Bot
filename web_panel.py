from flask import Flask, request, redirect, session, render_template_string
import json
import os
from threading import Thread

app = Flask('')
app.secret_key = 'ayate_secret_key_123' # مفتاح عشوائي لتأمين الجلسة

# دالات مساعدة للتعامل مع البيانات
def load_db():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    if 'user' not in session:
        # صفحة تسجيل الدخول الأولى (كما طلبت: لا يظهر شيء سوى الزر)
        return """
        <body style="background: #2c2f33; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; margin:0;">
            <div style="text-align: center; color: white; background: #23272a; padding: 50px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h1 style="margin-bottom: 30px;">مرحباً بك في لوحة تحكم آيات</h1>
                <a href="/login" style="background: #5865f2; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 20px; transition: 0.3s;">
                    🔐 تسجيل الدخول بحساب ديسكورد
                </a>
            </div>
        </body>
        """
    return redirect('/dashboard')

@app.route('/login')
def login():
    # --- ضع بياناتك هنا مباشرة ---
    CLIENT_ID = "1461289210123260038" 
    REDIRECT_URI = "https://ayate-bot.onrender.com/login/callback"
    # ----------------------------

    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    return redirect(auth_url)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect('/')
    # هنا ستعرض السيرفرات والقنوات (هيكل تجريبي للواجهة)
    return f"""
    <body style="background: #2c2f33; color: white; font-family: sans-serif; padding: 20px; direction: rtl;">
        <h1>لوحة تحكم السيرفرات</h1>
        <p>أهلاً بك يا {session['user']['username']}</p>
        <hr>
        <div style="background: #23272a; padding: 20px; border-radius: 10px;">
            <h3>تفعيل/تعطيل الرومات (القنوات)</h3>
            <p style="color: gray;">هنا تظهر قائمة القنوات بجانبها ✓ للتشغيل و × للتعطيل</p>
            <button onclick="alert('تم الحفظ')" style="background: #43b581; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">حفظ التغييرات</button>
        </div>
        <br>
        <a href="/logout" style="color: #f04747;">تسجيل الخروج</a>
    </body>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# --- دالة الـ Uptime الهامة جداً ---
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
