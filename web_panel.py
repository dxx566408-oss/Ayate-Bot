from flask import Flask, request, redirect, session, render_template_string
import requests, os, json, config
from threading import Thread

app = Flask('')
app.secret_key = 'ayate_secure_key'

def load_db():
    if not os.path.exists('database.json'): return {"users": {}, "guilds": {}}
    with open('database.json', 'r', encoding='utf-8') as f: return json.load(f)

def save_db(data):
    with open('database.json', 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    if 'user_id' not in session:
        return '<body style="background:#2c3e50;display:flex;justify-content:center;align-items:center;height:100vh;"><a href="/login" style="color:white;padding:15px 30px;background:#5865f2;text-decoration:none;border-radius:5px;font-family:sans-serif;">🔐 تسجيل الدخول للإدارة</a></body>'
    return redirect('/dashboard')

@app.route('/login')
def login():
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={config.CLIENT_ID}&redirect_uri={config.REDIRECT_URI}&response_type=code&scope=identify%20guilds"
    return redirect(auth_url)

@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    data = {'client_id': config.CLIENT_ID, 'client_secret': config.CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': config.REDIRECT_URI}
    r = requests.post('https://discord.com/api/v10/oauth2/token', data=data).json()
    token = r.get('access_token')
    user = requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': f'Bearer {token}'}).json()
    session['user_id'], session['access_token'], session['username'] = user['id'], token, user['username']
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect('/')
    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    guilds = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers).json()
    admin_guilds = [g for g in guilds if (int(g['permissions']) & 0x8) == 0x8]
    
    html = f'<body style="background:#2c2f33;color:white;font-family:sans-serif;direction:rtl;padding:20px;"><h2>أهلاً {session["username"]}</h2><p>اختر سيرفر لإدارة الرومات:</p>'
    for g in admin_guilds:
        html += f'<li><a href="/manage/{g["id"]}" style="color:#7289da;text-decoration:none;">⚙️ {g["name"]}</a></li>'
    return html + '</body>'

@app.route('/manage/<guild_id>', methods=['GET', 'POST'])
def manage(guild_id):
    if 'user_id' not in session: return redirect('/')
    db = load_db()
    if request.method == 'POST':
        db["guilds"][str(guild_id)] = request.form.getlist('channels')
        save_db(db)
        return '<h3>✅ تم الحفظ بنجاح! <a href="/dashboard">عودة</a></h3>'

    headers = {'Authorization': f'Bot {config.BOT_TOKEN}'}
    channels = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/channels', headers=headers).json()
    enabled = db["guilds"].get(str(guild_id), [])
    
    items = ""
    for c in channels:
        if c['type'] == 0:
            check = "checked" if str(c['id']) in enabled else ""
            items += f'<div style="background:#23272a;padding:10px;margin:5px;border-radius:5px;"><span># {c["name"]}</span> <input type="checkbox" name="channels" value="{c["id"]}" {check}></div>'
    return f'<body style="background:#2c2f33;color:white;font-family:sans-serif;direction:rtl;padding:20px;"><form method="POST"><h2>إدارة الرومات</h2>{items}<br><button type="submit" style="padding:10px 20px;background:#43b581;color:white;border:none;cursor:pointer;">حفظ</button></form></body>'

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))))
    t.start()
