// app.js — Vest Smm Site (полный)
const express = require('express');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const { Pool } = require('pg');
const axios = require('axios');
const crypto = require('crypto');

// ============================================================
// НАСТРОЙКИ
// ============================================================
const DATABASE_URL = 'postgresql://bothost_db_3922cbdd94ea:0PIMXZ_cAjqsfgZsBEjCCy2bJqDKiq33XF31PnjAhfE@node1.pghost.ru:15709/bothost_db_3922cbdd94ea';
const YOOMONEY_WALLET = '4100119286550472';
const SMM_API_URL = 'https://smmway.ru/api/v2';
const SUPPORT_USERNAME = 'VestSmmSupport';
const BOT_URL = 'https://t.me/Vestsmmmbot';
const ADMIN_EMAIL = 'femilianferuk@gmail.com';
const ADMIN_PASSWORD = 'admin55337q';
const SERVICE_MARGIN = 1.15;
const PORT = process.env.PORT || 3000;

// ============================================================
// БАЗА ДАННЫХ
// ============================================================
const pool = new Pool({ connectionString: DATABASE_URL, ssl: { rejectUnauthorized: false } });

async function initDB() {
    const c = await pool.connect();
    try {
        await c.query(`CREATE TABLE IF NOT EXISTS site_users (
            id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            balance DECIMAL(10,2) DEFAULT 0.00, total_deposit DECIMAL(10,2) DEFAULT 0.00,
            total_orders INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
        await c.query(`CREATE TABLE IF NOT EXISTS site_orders (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, service_id INTEGER NOT NULL,
            service_name TEXT NOT NULL, order_id INTEGER, link TEXT NOT NULL,
            quantity INTEGER NOT NULL, amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
        await c.query(`CREATE TABLE IF NOT EXISTS site_payments (
            id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, payment_id TEXT UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL, status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`);
        await c.query(`CREATE TABLE IF NOT EXISTS site_settings (key TEXT PRIMARY KEY, value TEXT)`);
        await c.query(`INSERT INTO site_settings (key, value) VALUES ('smm_api_key', '') ON CONFLICT (key) DO NOTHING`);
        const hash = await bcrypt.hash(ADMIN_PASSWORD, 10);
        await c.query(`INSERT INTO site_users (email, password_hash, balance) VALUES ($1,$2,999999) ON CONFLICT (email) DO NOTHING`, [ADMIN_EMAIL, hash]);
        console.log('DB ready');
    } finally { c.release(); }
}

async function getSetting(key) {
    const r = await pool.query('SELECT value FROM site_settings WHERE key=$1', [key]);
    return r.rows[0]?.value || '';
}
async function setSetting(key, value) {
    await pool.query('INSERT INTO site_settings (key,value) VALUES ($1,$2) ON CONFLICT(key) DO UPDATE SET value=$2', [key, value]);
}

// ============================================================
// EXPRESS
// ============================================================
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(session({ secret: 'vest-smm-site', resave: false, saveUninitialized: false, cookie: { maxAge: 30*24*60*60*1000 } }));

function auth(req, res, next) {
    if (!req.session.userId) return res.redirect('/?error=login');
    next();
}
function adminOnly(req, res, next) {
    if (!req.session.userId || req.session.email !== ADMIN_EMAIL) return res.status(403).send('Access denied');
    next();
}

// ============================================================
// СТИЛИ
// ============================================================
const CSS = `
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
`;

const HEAD = (title) => `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>${title}</title><style>${CSS}</style></head><body>`;
const HEADER = (user) => `<div class="header"><h1>⚡ Vest Smm</h1><div>${user ? `<a href="/catalog">🛒 Каталог</a><a href="/orders">📦 Заказы</a><a href="/profile">👤 Профиль</a><a href="/api/auth/logout">🚪 Выход</a>` : ''}</div></div><div class="container">`;
const FOOTER = `</div><div class="footer">Vest Smm 2026 | <a href="${BOT_URL}">Наш бот</a> | <a href="https://t.me/${SUPPORT_USERNAME}">Поддержка</a></div></body></html>`;

// ============================================================
// СТРАНИЦА ВХОДА/РЕГИСТРАЦИИ
// ============================================================
app.get('/', (req, res) => {
    if (req.session.userId) return res.redirect('/catalog');
    res.send(HEAD('Vest Smm — Вход') + `
<div class="auth-wrap"><div class="auth-card"><h1>⚡ Vest Smm</h1>
<div class="tabs"><button class="tab active" onclick="showTab('login')">Вход</button><button class="tab" onclick="showTab('register')">Регистрация</button></div>
<div id="login-form"><h2>Вход</h2><input type="email" id="lemail" placeholder="Email"><input type="password" id="lpass" placeholder="Пароль"><button class="btn btn-primary" style="width:100%" onclick="auth('login')">Войти</button></div>
<div id="register-form" style="display:none"><h2>Регистрация</h2><input type="email" id="remail" placeholder="Email"><input type="password" id="rpass" placeholder="Пароль (мин 6 символов)"><button class="btn btn-primary" style="width:100%" onclick="auth('register')">Зарегистрироваться</button></div>
<p id="error" style="color:#ef4444;margin-top:10px"></p></div></div>
<script>
function showTab(t){document.getElementById('login-form').style.display=t==='login'?'block':'none';document.getElementById('register-form').style.display=t==='register'?'block':'none';document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.textContent.toLowerCase().includes(t)))}
async function auth(type){const email=document.getElementById(type==='login'?'lemail':'remail').value;const password=document.getElementById(type==='login'?'lpass':'rpass').value;const res=await fetch('/api/auth/'+type,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});const data=await res.json();if(data.error)document.getElementById('error').textContent=data.error;else window.location='/catalog'}
</script></body></html>`);
});

// ============================================================
# API AUTH
# ============================================================
app.post('/api/auth/register', async (req, res) => {
    const { email, password } = req.body;
    if (!email || !password || password.length < 6) return res.json({ error: 'Email и пароль обязательны. Пароль минимум 6 символов.' });
    try {
        const existing = await pool.query('SELECT id FROM site_users WHERE email=$1', [email]);
        if (existing.rows.length > 0) return res.json({ error: 'Пользователь с такой почтой уже существует' });
        const hash = await bcrypt.hash(password, 10);
        const result = await pool.query('INSERT INTO site_users (email,password_hash) VALUES ($1,$2) RETURNING id,email', [email, hash]);
        req.session.userId = result.rows[0].id;
        req.session.email = result.rows[0].email;
        res.json({ success: true });
    } catch (e) { res.json({ error: 'Ошибка регистрации' }); }
});

app.post('/api/auth/login', async (req, res) => {
    const { email, password } = req.body;
    try {
        const result = await pool.query('SELECT * FROM site_users WHERE email=$1', [email]);
        const user = result.rows[0];
        if (!user) return res.json({ error: 'Неверная почта или пароль' });
        const valid = await bcrypt.compare(password, user.password_hash);
        if (!valid) return res.json({ error: 'Неверная почта или пароль' });
        req.session.userId = user.id;
        req.session.email = user.email;
        res.json({ success: true });
    } catch (e) { res.json({ error: 'Ошибка входа' }); }
});

app.get('/api/auth/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

// ============================================================
// КАТАЛОГ
// ============================================================
app.get('/catalog', auth, async (req, res) => {
    const apiKey = await getSetting('smm_api_key');
    let services = [];
    try { const resp = await axios.get(`${SMM_API_URL}?action=services&key=${apiKey}`, { timeout: 10 }); services = resp.data || []; } catch (e) {}
    
    const platforms = {};
    services.forEach(s => {
        const n = s.name.toLowerCase();
        let p = 'Другие';
        if (n.includes('instagram')) p = 'Instagram';
        else if (n.includes('telegram')) p = 'Telegram';
        else if (n.includes('youtube')) p = 'YouTube';
        else if (n.includes('twitch')) p = 'Twitch';
        else if (n.includes('tiktok')) p = 'TikTok';
        else if (n.includes('facebook')) p = 'Facebook';
        else if (n.includes('twitter')||n.includes('x ')) p = 'Twitter/X';
        else if (n.includes('vk')||n.includes('вк')) p = 'VK';
        else if (n.includes('discord')) p = 'Discord';
        if (!platforms[p]) platforms[p] = [];
        platforms[p].push(s);
    });

    let html = HEAD('Каталог') + HEADER({ email: req.session.email }) + '<h2>🛒 Выберите соцсеть</h2><div class="grid">';
    for (const [p, ss] of Object.entries(platforms).sort()) {
        html += `<a href="/catalog/${encodeURIComponent(p)}" class="card" style="text-align:center;text-decoration:none;color:#e2e8f0"><h3>${p}</h3><span class="badge">${ss.length} услуг</span></a>`;
    }
    html += '</div>' + FOOTER;
    res.send(html);
});

app.get('/catalog/:platform', auth, async (req, res) => {
    const apiKey = await getSetting('smm_api_key');
    let services = [];
    try { const resp = await axios.get(`${SMM_API_URL}?action=services&key=${apiKey}`, { timeout: 10 }); services = resp.data || []; } catch (e) {}
    
    const platform = req.params.platform;
    const filtered = services.filter(s => {
        const n = s.name.toLowerCase();
        if (platform === 'Instagram') return n.includes('instagram');
        if (platform === 'Telegram') return n.includes('telegram');
        if (platform === 'YouTube') return n.includes('youtube');
        if (platform === 'Twitch') return n.includes('twitch');
        if (platform === 'TikTok') return n.includes('tiktok');
        if (platform === 'Facebook') return n.includes('facebook');
        if (platform === 'Twitter/X') return n.includes('twitter')||n.includes('x ');
        if (platform === 'VK') return n.includes('vk')||n.includes('вк');
        if (platform === 'Discord') return n.includes('discord');
        return platform === 'Другие';
    });

    let html = HEAD(platform) + HEADER({ email: req.session.email }) + `<h2>📱 ${platform}</h2><a href="/catalog" style="color:#a78bfa;font-size:13px">← Назад</a><br><br>`;
    filtered.forEach(s => {
        const price = (parseFloat(s.rate) * SERVICE_MARGIN).toFixed(2);
        html += `<div class="card"><h3>${s.name}</h3><span style="color:#94a3b8;font-size:12px">Мин: ${s.min} | Макс: ${s.max}</span><br><span class="price">${price} ₽ / 1000</span><br><a href="/order/${s.service}?name=${encodeURIComponent(s.name)}&price=${price}&min=${s.min}&max=${s.max}" class="btn btn-primary btn-sm" style="margin-top:8px">Заказать</a></div>`;
    });
    html += FOOTER;
    res.send(html);
});

// ============================================================
// ЗАКАЗ
// ============================================================
app.get('/order/:serviceId', auth, (req, res) => {
    const { serviceId } = req.params;
    const { name, price, min, max } = req.query;
    let html = HEAD('Заказ') + HEADER({ email: req.session.email }) + `<h2>📋 ${name}</h2><p class="price">${price} ₽ / 1000</p><p>Мин: ${min} | Макс: ${max}</p>`;
    html += `<form action="/api/order" method="POST"><input type="hidden" name="service_id" value="${serviceId}"><input type="hidden" name="service_name" value="${name}"><input type="hidden" name="price" value="${price}"><input type="text" name="link" placeholder="Ссылка на пост/аккаунт" required><input type="number" name="quantity" placeholder="Количество" min="${min}" max="${max}" required><button class="btn btn-primary" style="width:100%">Подтвердить заказ</button></form>`;
    html += FOOTER;
    res.send(html);
});

app.post('/api/order', auth, async (req, res) => {
    const { service_id, service_name, link, quantity, price } = req.body;
    const amount = (parseFloat(price) * parseInt(quantity) / 1000).toFixed(2);
    const user = await pool.query('SELECT * FROM site_users WHERE id=$1', [req.session.userId]);
    if (parseFloat(user.rows[0].balance) < parseFloat(amount)) {
        return res.send(HEAD('Ошибка') + HEADER({ email: req.session.email }) + '<div class="card"><h3>❌ Недостаточно средств</h3><p>Ваш баланс: ' + user.rows[0].balance + ' ₽</p><p>Необходимо: ' + amount + ' ₽</p><a href="/topup" class="btn btn-success">Пополнить баланс</a></div>' + FOOTER);
    }
    const apiKey = await getSetting('smm_api_key');
    try {
        const resp = await axios.get(`${SMM_API_URL}?action=add&service=${service_id}&link=${encodeURIComponent(link)}&quantity=${quantity}&key=${apiKey}`, { timeout: 15 });
        if (resp.data && resp.data.order) {
            await pool.query('UPDATE site_users SET balance=balance-$1, total_orders=total_orders+1 WHERE id=$2', [amount, req.session.userId]);
            await pool.query('INSERT INTO site_orders (user_id,service_id,service_name,order_id,link,quantity,amount) VALUES ($1,$2,$3,$4,$5,$6,$7)', [req.session.userId, service_id, service_name, resp.data.order, link, quantity, amount]);
            res.redirect('/orders');
        } else {
            res.send(HEAD('Ошибка') + HEADER({ email: req.session.email }) + '<div class="card"><h3>❌ Ошибка создания заказа</h3><p>API не вернул ID заказа</p><a href="/catalog" class="btn btn-primary">Назад в каталог</a></div>' + FOOTER);
        }
    } catch (e) {
        res.send(HEAD('Ошибка') + HEADER({ email: req.session.email }) + '<div class="card"><h3>❌ Ошибка соединения с API</h3><p>Попробуйте позже</p><a href="/catalog" class="btn btn-primary">Назад в каталог</a></div>' + FOOTER);
    }
});

// ============================================================
// МОИ ЗАКАЗЫ
// ============================================================
app.get('/orders', auth, async (req, res) => {
    const orders = await pool.query('SELECT * FROM site_orders WHERE user_id=$1 ORDER BY created_at DESC LIMIT 30', [req.session.userId]);
    let html = HEAD('Мои заказы') + HEADER({ email: req.session.email }) + '<h2>📦 Мои покупки</h2>';
    if (orders.rows.length === 0) html += '<p>Нет заказов</p>';
    orders.rows.forEach(o => {
        html += `<div class="card"><h3>#${o.order_id || '—'} — ${o.service_name}</h3><p>Ссылка: ${o.link}</p><p>Количество: ${o.quantity} | Сумма: <b>${o.amount} ₽</b></p><span class="badge">${o.status}</span><p style="font-size:11px;color:#64748b">${new Date(o.created_at).toLocaleString('ru')}</p></div>`;
    });
    html += FOOTER;
    res.send(html);
});

// ============================================================
// ПРОФИЛЬ
// ============================================================
app.get('/profile', auth, async (req, res) => {
    const user = await pool.query('SELECT * FROM site_users WHERE id=$1', [req.session.userId]);
    const u = user.rows[0];
    let html = HEAD('Профиль') + HEADER({ email: req.session.email }) + `<h2>👤 Профиль</h2><div class="card"><p>Email: ${u.email}</p><p>Баланс: <b>${u.balance} ₽</b></p><p>Пополнено всего: ${u.total_deposit} ₽</p><p>Всего заказов: ${u.total_orders}</p><p>Дата регистрации: ${new Date(u.created_at).toLocaleString('ru')}</p></div><a href="/topup" class="btn btn-success" style="width:100%;display:block;margin-top:10px">💰 Пополнить баланс</a>`;
    if (req.session.email === ADMIN_EMAIL) html += '<a href="/admin" class="btn btn-primary" style="width:100%;display:block;margin-top:10px">⚙️ Админ-панель</a>';
    html += FOOTER;
    res.send(html);
});

// ============================================================
// ПОПОЛНЕНИЕ ЮMONEY
// ============================================================
app.get('/topup', auth, (req, res) => {
    let html = HEAD('Пополнение') + HEADER({ email: req.session.email }) + '<h2>💰 Пополнение через ЮMoney</h2><div class="card"><form action="/api/payment/create" method="POST"><input type="number" name="amount" placeholder="Сумма в рублях" min="10" required><button class="btn btn-success" style="width:100%">Создать счёт</button></form></div>' + FOOTER;
    res.send(html);
});

app.post('/api/payment/create', auth, async (req, res) => {
    const amount = parseFloat(req.body.amount);
    if (isNaN(amount) || amount < 10) {
        return res.send(HEAD('Ошибка') + HEADER({ email: req.session.email }) + '<div class="card"><h3>❌ Минимальная сумма 10 ₽</h3><a href="/topup" class="btn btn-primary">Назад</a></div>' + FOOTER);
    }
    const paymentId = 'PAY' + Date.now() + crypto.randomBytes(3).toString('hex').toUpperCase();
    await pool.query('INSERT INTO site_payments (user_id, payment_id, amount) VALUES ($1,$2,$3)', [req.session.userId, paymentId, amount]);
    const yoomoneyUrl = `https://yoomoney.ru/quickpay/confirm.xml?receiver=${YOOMONEY_WALLET}&sum=${amount}&label=${paymentId}&quickpay-form=shop`;
    let html = HEAD('Оплата') + HEADER({ email: req.session.email }) + `<h2>💳 Оплата</h2><div class="card"><p>Сумма к оплате: <b>${amount} ₽</b></p><p>ID платежа: <code>${paymentId}</code></p><a href="${yoomoneyUrl}" target="_blank" class="btn btn-success" style="display:block;margin:10px 0">Оплатить через ЮMoney</a><a href="/api/payment/check/${paymentId}" class="btn btn-primary" style="display:block">Проверить оплату</a></div>` + FOOTER;
    res.send(html);
});

app.get('/api/payment/check/:paymentId', auth, async (req, res) => {
    const { paymentId } = req.params;
    const payment = await pool.query('SELECT * FROM site_payments WHERE payment_id=$1 AND user_id=$2', [paymentId, req.session.userId]);
    if (!payment.rows[0]) {
        return res.send(HEAD('Ошибка') + HEADER({ email: req.session.email }) + '<div class="card"><h3>❌ Платёж не найден</h3><a href="/topup" class="btn btn-primary">Назад</a></div>' + FOOTER);
    }
    const p = payment.rows[0];
    if (p.status === 'completed') {
        const user = await pool.query('SELECT balance FROM site_users WHERE id=$1', [req.session.userId]);
        return res.send(HEAD('Успех') + HEADER({ email: req.session.email }) + `<div class="card"><h3>✅ Платёж уже зачислен</h3><p>Баланс: <b>${user.rows[0].balance} ₽</b></p><a href="/profile" class="btn btn-primary">В профиль</a></div>` + FOOTER);
    }
    let html = HEAD('Проверка оплаты') + HEADER({ email: req.session.email }) + `<div class="card"><h3>🔍 Проверка оплаты</h3><p>Сумма: <b>${p.amount} ₽</b></p><p>ID: <code>${p.payment_id}</code></p><p>Для подтверждения оплаты, пожалуйста, обратитесь в поддержку:</p><a href="https://t.me/${SUPPORT_USERNAME}" class="btn btn-primary" style="display:block;margin:10px 0">📞 Написать в поддержку</a><p style="color:#94a3b8;font-size:13px">Сообщите ID платежа при обращении. После проверки средства будут зачислены на ваш баланс.</p><a href="/topup" class="btn btn-primary">Создать новый платёж</a></div>` + FOOTER;
    res.send(html);
});

// ============================================================
// АДМИН-ПАНЕЛЬ
// ============================================================
app.get('/admin', adminOnly, async (req, res) => {
    const users = await pool.query('SELECT COUNT(*) as count FROM site_users');
    const orders = await pool.query('SELECT COUNT(*) as count FROM site_orders');
    const payments = await pool.query("SELECT COALESCE(SUM(amount),0) as total FROM site_payments WHERE status='completed'");
    const currentKey = await getSetting('smm_api_key');
    let html = HEAD('Админ-панель') + HEADER({ email: req.session.email }) + `<h2>⚙️ Админ-панель</h2>
    <div class="card"><h3>📊 Статистика</h3><p>Пользователей: ${users.rows[0].count}</p><p>Заказов: ${orders.rows[0].count}</p><p>Оборот: ${payments.rows[0].total} ₽</p></div>
    <div class="card"><h3>🔑 SMM API Ключ</h3><form action="/admin/api-key" method="POST"><input type="text" name="api_key" value="${currentKey}" placeholder="Введите API ключ от smmway.ru"><button class="btn btn-primary" style="width:100%">Сохранить</button></form></div>
    <div class="card"><h3>💰 Управление балансом</h3><form action="/admin/add-balance" method="POST"><input type="email" name="user_email" placeholder="Email пользователя" required><input type="number" name="amount" placeholder="Сумма (минус для списания)" required><button class="btn btn-success" style="width:100%">Изменить баланс</button></form></div>
    <div class="card"><h3>📋 Последние платежи</h3>`;
    const recentPayments = await pool.query('SELECT * FROM site_payments ORDER BY created_at DESC LIMIT 10');
    recentPayments.rows.forEach(p => {
        html += `<p><code>${p.payment_id}</code> — ${p.amount} ₽ — ${p.status} <a href="/admin/confirm-payment/${p.payment_id}" class="btn btn-sm btn-success">Подтвердить</a></p>`;
    });
    html += '</div>' + FOOTER;
    res.send(html);
});

app.post('/admin/api-key', adminOnly, async (req, res) => {
    await setSetting('smm_api_key', req.body.api_key);
    res.redirect('/admin');
});

app.post('/admin/add-balance', adminOnly, async (req, res) => {
    const { user_email, amount } = req.body;
    const amt = parseFloat(amount);
    if (isNaN(amt)) return res.redirect('/admin');
    await pool.query('UPDATE site_users SET balance=balance+$1 WHERE email=$2', [amt, user_email]);
    res.redirect('/admin');
});

app.get('/admin/confirm-payment/:paymentId', adminOnly, async (req, res) => {
    const { paymentId } = req.params;
    const payment = await pool.query('SELECT * FROM site_payments WHERE payment_id=$1', [paymentId]);
    if (payment.rows[0] && payment.rows[0].status === 'pending') {
        await pool.query("UPDATE site_payments SET status='completed' WHERE payment_id=$1", [paymentId]);
        await pool.query('UPDATE site_users SET balance=balance+$1, total_deposit=total_deposit+$1 WHERE id=$2', [payment.rows[0].amount, payment.rows[0].user_id]);
    }
    res.redirect('/admin');
});

// ============================================================
// ЗАПУСК
// ============================================================
initDB().then(() => {
    app.listen(PORT, () => console.log(`Vest Smm Site running on port ${PORT}`));
});
