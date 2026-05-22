# app.py — Vest Smm Site на Python (Flask)
import os
import psycopg2
import psycopg2.extras
import bcrypt
import requests
import uuid
from flask import Flask, request, session, redirect, render_template_string
from datetime import datetime

# ============================================================
# НАСТРОЙКИ
# ============================================================
DATABASE_URL = 'postgresql://bothost_db_3922cbdd94ea:0PIMXZ_cAjqsfgZsBEjCCy2bJqDKiq33XF31PnjAhfE@node1.pghost.ru:15709/bothost_db_3922cbdd94ea'
YOOMONEY_WALLET = '4100119286550472'
SMM_API_URL = 'https://smmway.ru/api/v2'
SUPPORT_USERNAME = 'VestSmmSupport'
BOT_URL = 'https://t.me/Vestsmmmbot'
ADMIN_EMAIL = 'femilianferuk@gmail.com'
ADMIN_PASSWORD = 'admin55337q'
SERVICE_MARGIN = 1.15

# ============================================================
# БАЗА ДАННЫХ
# ============================================================
def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_database():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS site_users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            balance DECIMAL(10,2) DEFAULT 0.00,
            total_deposit DECIMAL(10,2) DEFAULT 0.00,
            total_orders INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS site_orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            order_id INTEGER,
            link TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS site_payments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            payment_id TEXT UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS site_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cur.execute("INSERT INTO site_settings (key, value) VALUES ('smm_api_key', '') ON CONFLICT (key) DO NOTHING")
    hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO site_users (email, password_hash, balance) VALUES (%s, %s, 999999) ON CONFLICT (email) DO NOTHING", (ADMIN_EMAIL, hashed))
    conn.commit()
    cur.close()
    conn.close()
    print('DB initialized')

def get_setting(key):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT value FROM site_settings WHERE key = %s', (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else ''

def set_setting(key, value):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO site_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s', (key, value, value))
    conn.commit()
    cur.close()
    conn.close()

# ============================================================
# FLASK
# ============================================================
app = Flask(__name__)
app.secret_key = 'vest-smm-site-secret-key'

def require_auth():
    if 'user_id' not in session:
        return redirect('/?error=login')

def require_admin():
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        return 'Access denied', 403

# ============================================================
# CSS
# ============================================================
CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#08080f;color:#e2e8f0;min-height:100vh}
.header{background:linear-gradient(135deg,#3b0764,#6d28d9);padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:20px;font-weight:800}
.header a{color:#c4b5fd;text-decoration:none;margin-left:12px;font-size:14px}
.container{max-width:800px;margin:0 auto;padding:16px}
.card{background:#111122;border:1px solid #252548;border-radius:14px;padding:16px;margin-bottom:12px}
.card h3{font-size:16px;margin-bottom:8px;color:#a78bfa}
.btn{display:inline-block;padding:10px 20px;border-radius:10px;border:none;cursor:pointer;font-size:14px;font-weight:600;text-decoration:none;color:#fff;text-align:center}
.btn-primary{background:#6d28d9}
.btn-success{background:#059669}
.btn-danger{background:#dc2626}
.btn-sm{padding:6px 14px;font-size:12px}
input,select{width:100%;padding:10px 14px;border-radius:10px;border:1px solid #252548;background:#1a1a35;color:#fff;font-size:14px;margin-bottom:10px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.price{color:#34d399;font-weight:700}
.badge{background:#2d2050;color:#a78bfa;padding:4px 10px;border-radius:20px;font-size:11px}
.footer{text-align:center;padding:20px;color:#4b3f6b;font-size:12px;margin-top:40px}
.footer a{color:#8b5cf6}
.auth-wrap{display:flex;justify-content:center;align-items:center;min-height:100vh}
.auth-card{background:#111122;border:1px solid #252548;border-radius:16px;padding:24px;width:100%;max-width:380px}
.auth-card h1{text-align:center;margin-bottom:16px}
.tabs{display:flex;gap:8px;margin-bottom:16px}
.tab{flex:1;padding:8px;border-radius:10px;border:1px solid #252548;background:#1a1a35;color:#94a3b8;cursor:pointer;text-align:center}
.tab.active{background:#6d28d9;color:#fff;border-color:#6d28d9}
'''

HEADER_HTML = '''
<div class="header">
    <h1>⚡ Vest Smm</h1>
    <div>
        <a href="/catalog">🛒 Каталог</a>
        <a href="/orders">📦 Заказы</a>
        <a href="/profile">👤 Профиль</a>
        <a href="/logout">🚪 Выход</a>
    </div>
</div>
<div class="container">
'''

FOOTER_HTML = f'''
</div>
<div class="footer">
    Vest Smm 2026 | <a href="{BOT_URL}">Наш бот</a> | <a href="https://t.me/{SUPPORT_USERNAME}">Поддержка</a>
</div>
'''

# ============================================================
# ГЛАВНАЯ (ВХОД/РЕГИСТРАЦИЯ)
# ============================================================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/catalog')
    return render_template_string('''
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Vest Smm — Вход</title><style>''' + CSS + '''</style></head><body>
<div class="auth-wrap"><div class="auth-card"><h1>⚡ Vest Smm</h1>
<div class="tabs"><button class="tab active" onclick="showTab('login')">Вход</button><button class="tab" onclick="showTab('register')">Регистрация</button></div>
<div id="login-form"><h2>Вход</h2><input type="email" id="lemail" placeholder="Email"><input type="password" id="lpass" placeholder="Пароль"><button class="btn btn-primary" style="width:100%" onclick="auth('login')">Войти</button></div>
<div id="register-form" style="display:none"><h2>Регистрация</h2><input type="email" id="remail" placeholder="Email"><input type="password" id="rpass" placeholder="Пароль (мин 6 символов)"><button class="btn btn-primary" style="width:100%" onclick="auth('register')">Зарегистрироваться</button></div>
<p id="error" style="color:#ef4444;margin-top:10px"></p></div></div>
<script>
function showTab(t){document.getElementById('login-form').style.display=t==='login'?'block':'none';document.getElementById('register-form').style.display=t==='register'?'block':'none';document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.textContent.toLowerCase().includes(t)))}
async function auth(type){const email=document.getElementById(type==='login'?'lemail':'remail').value;const password=document.getElementById(type==='login'?'lpass':'rpass').value;const res=await fetch('/api/auth/'+type,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});const data=await res.json();if(data.error)document.getElementById('error').textContent=data.error;else window.location='/catalog'}
</script></body></html>''')

# ============================================================
# API AUTH
# ============================================================
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    if not email or len(password) < 6:
        return {'error': 'Email и пароль обязательны. Пароль минимум 6 символов.'}
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM site_users WHERE email = %s', (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return {'error': 'Пользователь с такой почтой уже существует'}
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute('INSERT INTO site_users (email, password_hash) VALUES (%s, %s) RETURNING id, email', (email, hashed))
    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    session['user_id'] = user[0]
    session['email'] = user[1]
    return {'success': True}

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_users WHERE email = %s', (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return {'error': 'Неверная почта или пароль'}
    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return {'error': 'Неверная почта или пароль'}
    session['user_id'] = user['id']
    session['email'] = user['email']
    return {'success': True}

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ============================================================
# КАТАЛОГ
# ============================================================
@app.route('/catalog')
def catalog():
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    api_key = get_setting('smm_api_key')
    services = []
    try:
        resp = requests.get(f'{SMM_API_URL}?action=services&key={api_key}', timeout=10)
        services = resp.json() if resp.status_code == 200 else []
    except:
        pass
    
    platforms = {}
    for s in services:
        n = s.get('name', '').lower()
        p = 'Другие'
        if 'instagram' in n: p = 'Instagram'
        elif 'telegram' in n: p = 'Telegram'
        elif 'youtube' in n: p = 'YouTube'
        elif 'twitch' in n: p = 'Twitch'
        elif 'tiktok' in n: p = 'TikTok'
        elif 'facebook' in n: p = 'Facebook'
        elif 'twitter' in n or 'x ' in n: p = 'Twitter/X'
        elif 'vk' in n or 'вк' in n: p = 'VK'
        elif 'discord' in n: p = 'Discord'
        if p not in platforms:
            platforms[p] = []
        platforms[p].append(s)
    
    items_html = ''
    for p, ss in sorted(platforms.items()):
        items_html += f'<a href="/catalog/{p}" class="card" style="text-align:center;text-decoration:none;color:#e2e8f0"><h3>{p}</h3><span class="badge">{len(ss)} услуг</span></a>'
    
    return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Каталог</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>🛒 Выберите соцсеть</h2><div class="grid">{items_html}</div>{FOOTER_HTML}</body></html>'

@app.route('/catalog/<platform>')
def catalog_platform(platform):
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    api_key = get_setting('smm_api_key')
    services = []
    try:
        resp = requests.get(f'{SMM_API_URL}?action=services&key={api_key}', timeout=10)
        services = resp.json() if resp.status_code == 200 else []
    except:
        pass
    
    filtered = []
    for s in services:
        n = s.get('name', '').lower()
        if platform == 'Instagram' and 'instagram' in n: filtered.append(s)
        elif platform == 'Telegram' and 'telegram' in n: filtered.append(s)
        elif platform == 'YouTube' and 'youtube' in n: filtered.append(s)
        elif platform == 'Twitch' and 'twitch' in n: filtered.append(s)
        elif platform == 'TikTok' and 'tiktok' in n: filtered.append(s)
        elif platform == 'Facebook' and 'facebook' in n: filtered.append(s)
        elif platform == 'Twitter/X' and ('twitter' in n or 'x ' in n): filtered.append(s)
        elif platform == 'VK' and ('vk' in n or 'вк' in n): filtered.append(s)
        elif platform == 'Discord' and 'discord' in n: filtered.append(s)
        elif platform == 'Другие': filtered.append(s)
    
    services_html = ''
    for s in filtered:
        price = round(float(s.get('rate', 0)) * SERVICE_MARGIN, 2)
        services_html += f'''<div class="card"><h3>{s['name']}</h3><span style="color:#94a3b8;font-size:12px">Мин: {s['min']} | Макс: {s['max']}</span><br><span class="price">{price} ₽ / 1000</span><br><a href="/order/{s['service']}?name={s['name']}&price={price}&min={s['min']}&max={s['max']}" class="btn btn-primary btn-sm" style="margin-top:8px">Заказать</a></div>'''
    
    return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{platform}</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>📱 {platform}</h2><a href="/catalog" style="color:#a78bfa;font-size:13px">← Назад</a><br><br>{services_html}{FOOTER_HTML}</body></html>'

# ============================================================
# ЗАКАЗ
# ============================================================
@app.route('/order/<int:service_id>')
def order_page(service_id):
    if 'user_id' not in session:
        return redirect('/?error=login')
    name = request.args.get('name', '')
    price = request.args.get('price', '0')
    min_q = request.args.get('min', '1')
    max_q = request.args.get('max', '100')
    
    return f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Заказ</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>📋 {name}</h2><p class="price">{price} ₽ / 1000</p><p>Мин: {min_q} | Макс: {max_q}</p>
<form action="/api/order" method="POST">
<input type="hidden" name="service_id" value="{service_id}">
<input type="hidden" name="service_name" value="{name}">
<input type="hidden" name="price" value="{price}">
<input type="text" name="link" placeholder="Ссылка на пост/аккаунт" required>
<input type="number" name="quantity" placeholder="Количество" min="{min_q}" max="{max_q}" required>
<button class="btn btn-primary" style="width:100%">Подтвердить заказ</button>
</form>{FOOTER_HTML}</body></html>'''

@app.route('/api/order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    service_id = request.form.get('service_id')
    service_name = request.form.get('service_name')
    link = request.form.get('link')
    quantity = request.form.get('quantity')
    price = float(request.form.get('price', '0'))
    amount = round(price * int(quantity) / 1000, 2)
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    if float(user['balance']) < amount:
        cur.close()
        conn.close()
        return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Ошибка</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>❌ Недостаточно средств</h3><p>Баланс: {user["balance"]} ₽</p><p>Необходимо: {amount} ₽</p><a href="/topup" class="btn btn-success">Пополнить баланс</a></div>{FOOTER_HTML}</body></html>'
    
    api_key = get_setting('smm_api_key')
    try:
        resp = requests.get(f'{SMM_API_URL}?action=add&service={service_id}&link={link}&quantity={quantity}&key={api_key}', timeout=15)
        data = resp.json()
        if 'order' in data:
            cur.execute('UPDATE site_users SET balance = balance - %s, total_orders = total_orders + 1 WHERE id = %s', (amount, session['user_id']))
            cur.execute('INSERT INTO site_orders (user_id, service_id, service_name, order_id, link, quantity, amount) VALUES (%s,%s,%s,%s,%s,%s,%s)', (session['user_id'], service_id, service_name, data['order'], link, quantity, amount))
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/orders')
    except:
        pass
    
    cur.close()
    conn.close()
    return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Ошибка</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>❌ Ошибка создания заказа</h3><a href="/catalog" class="btn btn-primary">Назад в каталог</a></div>{FOOTER_HTML}</body></html>'

# ============================================================
# МОИ ЗАКАЗЫ
# ============================================================
@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_orders WHERE user_id = %s ORDER BY created_at DESC LIMIT 30', (session['user_id'],))
    orders_list = cur.fetchall()
    cur.close()
    conn.close()
    
    html = ''
    if not orders_list:
        html = '<p>Нет заказов</p>'
    for o in orders_list:
        html += f'<div class="card"><h3>#{o["order_id"] or "—"} — {o["service_name"]}</h3><p>Ссылка: {o["link"]}</p><p>Количество: {o["quantity"]} | Сумма: <b>{o["amount"]} ₽</b></p><span class="badge">{o["status"]}</span><p style="font-size:11px;color:#64748b">{o["created_at"].strftime("%d.%m.%Y %H:%M")}</p></div>'
    
    return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Мои заказы</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>📦 Мои покупки</h2>{html}{FOOTER_HTML}</body></html>'

# ============================================================
# ПРОФИЛЬ
# ============================================================
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    admin_btn = ''
    if session.get('email') == ADMIN_EMAIL:
        admin_btn = '<a href="/admin" class="btn btn-primary" style="width:100%;display:block;margin-top:10px">⚙️ Админ-панель</a>'
    
    return f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Профиль</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>👤 Профиль</h2>
<div class="card"><p>Email: {user["email"]}</p><p>Баланс: <b>{user["balance"]} ₽</b></p><p>Пополнено всего: {user["total_deposit"]} ₽</p><p>Всего заказов: {user["total_orders"]}</p><p>Регистрация: {user["created_at"].strftime("%d.%m.%Y")}</p></div>
<a href="/topup" class="btn btn-success" style="width:100%;display:block;margin-top:10px">💰 Пополнить баланс</a>
{admin_btn}{FOOTER_HTML}</body></html>'''

# ============================================================
# ПОПОЛНЕНИЕ ЮMONEY
# ============================================================
@app.route('/topup')
def topup():
    if 'user_id' not in session:
        return redirect('/?error=login')
    return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Пополнение</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>💰 Пополнение через ЮMoney</h2><div class="card"><form action="/api/payment/create" method="POST"><input type="number" name="amount" placeholder="Сумма в рублях" min="10" required><button class="btn btn-success" style="width:100%">Создать счёт</button></form></div>{FOOTER_HTML}</body></html>'

@app.route('/api/payment/create', methods=['POST'])
def create_payment():
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    amount = float(request.form.get('amount', '0'))
    if amount < 10:
        return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Ошибка</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>❌ Минимальная сумма 10 ₽</h3><a href="/topup" class="btn btn-primary">Назад</a></div>{FOOTER_HTML}</body></html>'
    
    payment_id = 'PAY' + str(uuid.uuid4()).replace('-', '')[:16].upper()
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO site_payments (user_id, payment_id, amount) VALUES (%s, %s, %s)', (session['user_id'], payment_id, amount))
    conn.commit()
    cur.close()
    conn.close()
    
    yoomoney_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver={YOOMONEY_WALLET}&sum={amount}&label={payment_id}&quickpay-form=shop'
    
    return f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Оплата</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>💳 Оплата</h2><div class="card">
<p>Сумма к оплате: <b>{amount} ₽</b></p><p>ID платежа: <code>{payment_id}</code></p>
<a href="{yoomoney_url}" target="_blank" class="btn btn-success" style="display:block;margin:10px 0">Оплатить через ЮMoney</a>
<a href="/api/payment/check/{payment_id}" class="btn btn-primary" style="display:block">Проверить оплату</a></div>{FOOTER_HTML}</body></html>'''

@app.route('/api/payment/check/<payment_id>')
def check_payment(payment_id):
    if 'user_id' not in session:
        return redirect('/?error=login')
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_payments WHERE payment_id = %s AND user_id = %s', (payment_id, session['user_id']))
    payment = cur.fetchone()
    cur.close()
    conn.close()
    
    if not payment:
        return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Ошибка</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>❌ Платёж не найден</h3><a href="/topup" class="btn btn-primary">Назад</a></div>{FOOTER_HTML}</body></html>'
    
    if payment['status'] == 'completed':
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT balance FROM site_users WHERE id = %s', (session['user_id'],))
        balance = cur.fetchone()[0]
        cur.close()
        conn.close()
        return f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Успех</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>✅ Платёж уже зачислен</h3><p>Баланс: <b>{balance} ₽</b></p><a href="/profile" class="btn btn-primary">В профиль</a></div>{FOOTER_HTML}</body></html>'
    
    return f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Проверка оплаты</title><style>{CSS}</style></head><body>{HEADER_HTML}<div class="card"><h3>🔍 Проверка оплаты</h3>
<p>Сумма: <b>{payment["amount"]} ₽</b></p><p>ID: <code>{payment["payment_id"]}</code></p>
<p>Для подтверждения оплаты обратитесь в поддержку:</p>
<a href="https://t.me/{SUPPORT_USERNAME}" class="btn btn-primary" style="display:block;margin:10px 0">📞 Написать в поддержку</a>
<p style="color:#94a3b8;font-size:13px">Сообщите ID платежа при обращении.</p>
<a href="/topup" class="btn btn-primary">Создать новый платёж</a></div>{FOOTER_HTML}</body></html>'''

# ============================================================
# АДМИН-ПАНЕЛЬ
# ============================================================
@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        return 'Access denied', 403
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM site_users')
    users_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM site_orders')
    orders_count = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM site_payments WHERE status = 'completed'")
    revenue = cur.fetchone()[0]
    cur.close()
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_payments ORDER BY created_at DESC LIMIT 10')
    payments = cur.fetchall()
    cur.close()
    conn.close()
    
    current_key = get_setting('smm_api_key')
    
    payments_html = ''
    for p in payments:
        payments_html += f'<p><code>{p["payment_id"]}</code> — {p["amount"]} ₽ — {p["status"]} <a href="/admin/confirm-payment/{p["payment_id"]}" class="btn btn-sm btn-success">Подтвердить</a></p>'
    
    return f'''<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Админ</title><style>{CSS}</style></head><body>{HEADER_HTML}<h2>⚙️ Админ-панель</h2>
<div class="card"><h3>📊 Статистика</h3><p>Пользователей: {users_count}</p><p>Заказов: {orders_count}</p><p>Оборот: {revenue} ₽</p></div>
<div class="card"><h3>🔑 SMM API Ключ</h3><form action="/admin/api-key" method="POST"><input type="text" name="api_key" value="{current_key}" placeholder="Введите API ключ"><button class="btn btn-primary" style="width:100%">Сохранить</button></form></div>
<div class="card"><h3>💰 Управление балансом</h3><form action="/admin/add-balance" method="POST"><input type="email" name="user_email" placeholder="Email пользователя" required><input type="number" name="amount" placeholder="Сумма (минус для списания)" required><button class="btn btn-success" style="width:100%">Изменить баланс</button></form></div>
<div class="card"><h3>📋 Последние платежи</h3>{payments_html}</div>{FOOTER_HTML}</body></html>'''

@app.route('/admin/api-key', methods=['POST'])
def admin_api_key():
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        return 'Access denied', 403
    set_setting('smm_api_key', request.form.get('api_key', ''))
    return redirect('/admin')

@app.route('/admin/add-balance', methods=['POST'])
def admin_add_balance():
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        return 'Access denied', 403
    email = request.form.get('user_email')
    amount = float(request.form.get('amount', '0'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE site_users SET balance = balance + %s WHERE email = %s', (amount, email))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')

@app.route('/admin/confirm-payment/<payment_id>')
def admin_confirm_payment(payment_id):
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        return 'Access denied', 403
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM site_payments WHERE payment_id = %s', (payment_id,))
    payment = cur.fetchone()
    if payment and payment['status'] == 'pending':
        cur.execute("UPDATE site_payments SET status = 'completed' WHERE payment_id = %s", (payment_id,))
        cur.execute('UPDATE site_users SET balance = balance + %s, total_deposit = total_deposit + %s WHERE id = %s', (payment['amount'], payment['amount'], payment['user_id']))
        conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=PORT, debug=False)
