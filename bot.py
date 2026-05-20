<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Vest Smm</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg: #08080f;
            --surface: #111122;
            --surface2: #1a1a35;
            --border: #252548;
            --purple: #8b5cf6;
            --purple-light: #a78bfa;
            --green: #34d399;
            --gold: #f59e0b;
            --diamond: #60a5fa;
            --text: #e2e8f0;
            --text-dim: #94a3b8;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            -webkit-tap-highlight-color: transparent;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #3b0764 0%, #5b21b6 50%, #6d28d9 100%);
            padding: 20px 18px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 20;
        }
        .header .logo { font-size: 20px; font-weight: 800; letter-spacing: 1px; }
        .header .step { font-size: 12px; color: #c4b5fd; margin-top: 4px; }

        /* Level Tabs */
        .level-tabs {
            display: flex;
            gap: 6px;
            padding: 10px 16px;
            background: var(--surface);
            justify-content: center;
            border-bottom: 1px solid var(--border);
        }
        .level-tab {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text-dim);
            transition: 0.2s;
        }
        .level-tab.active { color: #fff; }
        .level-tab.lite.active { background: #6b7280; border-color: #6b7280; }
        .level-tab.pro.active { background: var(--gold); border-color: var(--gold); color: #000; }
        .level-tab.max.active { background: var(--diamond); border-color: var(--diamond); }
        .level-info {
            text-align: center;
            padding: 6px 16px;
            font-size: 10px;
            color: var(--text-dim);
            background: var(--surface);
        }

        /* Breadcrumb */
        .breadcrumb {
            padding: 8px 16px;
            background: var(--surface);
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid var(--border);
        }
        .breadcrumb .back-btn {
            width: 30px; height: 30px;
            border-radius: 8px;
            background: var(--surface2);
            border: 1px solid var(--border);
            color: var(--purple-light);
            font-size: 15px;
            cursor: pointer;
        }
        .breadcrumb .path { font-size: 13px; color: var(--purple-light); }

        /* Search */
        .search-wrap { padding: 10px 16px; }
        .search-wrap input {
            width: 100%; padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text);
            font-size: 13px;
            outline: none;
        }
        .search-wrap input:focus { border-color: var(--purple); }
        .search-wrap input::placeholder { color: #4b5563; }

        /* Grid */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px 16px; }
        .p-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 10px;
            text-align: center;
            cursor: pointer;
            transition: 0.2s;
        }
        .p-card:active { background: #1e1b4b; border-color: var(--purple); transform: scale(0.96); }
        .p-card img { width: 40px; height: 40px; object-fit: contain; margin-bottom: 8px; }
        .p-card .p-name { font-size: 12px; font-weight: 600; }
        .p-card .p-count { font-size: 10px; color: var(--purple-light); margin-top: 2px; }

        /* Lists */
        .list { padding: 6px 16px; }
        .list-item {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 8px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: 0.2s;
        }
        .list-item:active { background: #1e1b4b; border-color: var(--purple); }
        .list-item .li-name { font-size: 14px; font-weight: 500; }
        .list-item .li-badge {
            background: #2d2050;
            color: var(--purple-light);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }

        /* Service Card */
        .s-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: 0.2s;
        }
        .s-card:active { background: #1e1b4b; border-color: var(--purple); }
        .s-card .s-name { font-size: 13px; font-weight: 500; margin-bottom: 8px; line-height: 1.3; }
        .s-card .s-prices { display: flex; gap: 8px; font-size: 11px; }
        .s-card .s-price-tag {
            flex: 1;
            text-align: center;
            padding: 4px 6px;
            border-radius: 6px;
            font-weight: 600;
        }
        .s-price-tag.lite { background: #1f2937; color: #9ca3af; }
        .s-price-tag.pro { background: #1f1a0a; color: var(--gold); }
        .s-price-tag.max { background: #0f1a2e; color: var(--diamond); }

        /* Detail */
        .detail-wrap { padding: 16px; }
        .detail-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
        }
        .detail-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 14px; }
        .detail-card .price-levels { display: flex; gap: 10px; margin-bottom: 16px; }
        .detail-card .price-block {
            flex: 1;
            text-align: center;
            padding: 12px 8px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        .price-block .pl-name { font-size: 10px; font-weight: 700; margin-bottom: 4px; }
        .price-block .pl-price { font-size: 16px; font-weight: 800; }
        .price-block.lite { background: #1f2937; }
        .price-block.pro { background: #1f1a0a; border-color: #92400e; }
        .price-block.max { background: #0f1a2e; border-color: #1e40af; }
        .pl-price.lite { color: #d1d5db; }
        .pl-price.pro { color: var(--gold); }
        .pl-price.max { color: var(--diamond); }
        .pl-save { font-size: 9px; color: var(--green); margin-top: 2px; }

        .detail-row {
            display: flex; justify-content: space-between;
            padding: 10px 0; border-bottom: 1px solid #1a1a30;
            font-size: 13px;
        }
        .detail-row .dl { color: var(--text-dim); }
        .detail-row .dv { color: var(--text); font-weight: 500; }

        .btn-order {
            display: block; width: 100%;
            margin-top: 16px; padding: 14px;
            background: linear-gradient(135deg, #6d28d9, #8b5cf6);
            border: none; border-radius: 12px;
            color: #fff; font-size: 15px; font-weight: 700;
            cursor: pointer;
        }
        .btn-order:active { opacity: 0.85; }

        /* Footer */
        .footer {
            text-align: center;
            padding: 20px 16px 28px;
            font-size: 11px;
            color: #4b3f6b;
        }
        .footer span { color: var(--purple); font-weight: 700; }

        .hidden { display: none !important; }
        .loader { text-align: center; padding: 60px; color: var(--purple-light); }
        .empty { text-align: center; padding: 60px; color: #4b5563; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Vest Smm</div>
        <div class="step" id="step-title">Выберите платформу</div>
    </div>

    <!-- Переключатель уровня -->
    <div class="level-tabs" id="level-tabs">
        <div class="level-tab lite active" onclick="setLevel('lite')">🪨 Lite</div>
        <div class="level-tab pro" onclick="setLevel('pro')">🥇 Pro</div>
        <div class="level-tab max" onclick="setLevel('max')">💎 Max</div>
    </div>
    <div class="level-info" id="level-info">Скидка Lite: 0% | Pro: 4% | Max: 10%</div>

    <div class="breadcrumb hidden" id="breadcrumb">
        <button class="back-btn" onclick="goBack()">←</button>
        <span class="path" id="breadcrumb-text"></span>
    </div>

    <div class="search-wrap hidden" id="search-box">
        <input type="text" id="search" placeholder="Поиск услуг..." oninput="filterServices()">
    </div>

    <div class="grid" id="platforms-screen"></div>
    <div class="list hidden" id="categories-screen"></div>
    <div class="list hidden" id="services-screen"></div>
    <div class="detail-wrap hidden" id="detail-screen"></div>
    <div class="loader hidden" id="loader">Загрузка...</div>
    <div class="footer">Powered by <span>Vest Smm</span></div>

    <script>
        const API_KEY = 'd2kALxwu1KIstaUHWXzeb8S2OzmgIg4ct0Z8WCe76I74lZS3bctT9ogN3Eex';
        const BOT_USERNAME = 'Vestsmmmbot';
        const API_URL = 'https://smmway.ru/api/v2';
        const MARGIN = 1.07;
        const DISCOUNTS = { lite: 0, pro: 4, max: 10 };

        let allServices = [];
        let platforms = {};
        let currentPlatform = '';
        let currentCategory = '';
        let currentServices = [];
        let currentLevel = 'lite';

        const tg = window.Telegram.WebApp;
        tg.ready();
        tg.expand();

        // Картинки соцсетей из Imgur
        const platformLogos = {
            'Instagram': 'https://i.imgur.com/6QjZq9C.png',
            'Telegram': 'https://i.imgur.com/8LZq6cW.png',
            'YouTube': 'https://i.imgur.com/fKq4WvQ.png',
            'Twitch': 'https://i.imgur.com/3PZq8dR.png',
            'TikTok': 'https://i.imgur.com/kBZq2mN.png',
            'Facebook': 'https://i.imgur.com/4XZq7gH.png',
            'Twitter/X': 'https://i.imgur.com/2JZq5pL.png',
            'VK': 'https://i.imgur.com/9NZq1tY.png',
            'Discord': 'https://i.imgur.com/7MZq3vF.png',
            'Spotify': 'https://i.imgur.com/1AZq8eS.png',
            'SoundCloud': 'https://i.imgur.com/5BZq4wK.png',
            'Другие': 'https://i.imgur.com/0CZq0xU.png'
        };

        function show(id) { document.getElementById(id).classList.remove('hidden'); }
        function hide(id) { document.getElementById(id).classList.add('hidden'); }
        function hideAll() { ['platforms-screen','categories-screen','services-screen','detail-screen','loader','search-box','breadcrumb'].forEach(hide); }

        function setLevel(level) {
            currentLevel = level;
            document.querySelectorAll('.level-tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`.level-tab.${level}`).classList.add('active');
            document.getElementById('level-info').textContent = `Скидка Lite: 0% | Pro: 4% | Max: 10% | Текущий: ${level.toUpperCase()} (${DISCOUNTS[level]}%)`;
            if (currentServices.length) displayServices(currentServices);
        }

        function getPrice(rate, level) {
            const base = parseFloat(rate) * MARGIN;
            const discount = DISCOUNTS[level] / 100;
            return (base * (1 - discount)).toFixed(2);
        }

        async function init() {
            hideAll(); show('loader');
            try {
                const r = await fetch(`${API_URL}?action=services&key=${API_KEY}`);
                allServices = await r.json();
                buildPlatforms();
                renderPlatforms();
            } catch(e) {
                document.getElementById('platforms-screen').innerHTML = '<div class="empty">Ошибка загрузки</div>';
            }
        }

        function buildPlatforms() {
            platforms = {};
            allServices.forEach(s => {
                const n = s.name.toLowerCase();
                let p = 'Другие';
                if (n.includes('instagram')) p = 'Instagram';
                else if (n.includes('telegram')) p = 'Telegram';
                else if (n.includes('youtube')) p = 'YouTube';
                else if (n.includes('twitch')) p = 'Twitch';
                else if (n.includes('tiktok')) p = 'TikTok';
                else if (n.includes('facebook')) p = 'Facebook';
                else if (n.includes('twitter') || n.includes('x ')) p = 'Twitter/X';
                else if (n.includes('vk') || n.includes('вк')) p = 'VK';
                else if (n.includes('discord')) p = 'Discord';
                else if (n.includes('spotify')) p = 'Spotify';
                else if (n.includes('soundcloud')) p = 'SoundCloud';
                if (!platforms[p]) platforms[p] = [];
                platforms[p].push(s);
            });
        }

        function getCategory(name) {
            const n = name.toLowerCase();
            if (n.includes('подписчик') || n.includes('subscriber') || n.includes('follow')) return 'Подписчики';
            if (n.includes('лайк') || n.includes('like')) return 'Лайки';
            if (n.includes('просмотр') || n.includes('view')) return 'Просмотры';
            if (n.includes('коммент') || n.includes('comment')) return 'Комментарии';
            if (n.includes('репост') || n.includes('repost') || n.includes('share')) return 'Репосты';
            return 'Другое';
        }

        function renderPlatforms() {
            hideAll(); show('platforms-screen');
            document.getElementById('step-title').textContent = 'Выберите платформу';
            const div = document.getElementById('platforms-screen');
            div.innerHTML = Object.keys(platforms).sort().map(p => `
                <div class="p-card" onclick="selectPlatform('${p}')">
                    <img src="${platformLogos[p] || platformLogos['Другие']}" alt="${p}">
                    <div class="p-name">${p}</div>
                    <div class="p-count">${platforms[p].length} услуг</div>
                </div>
            `).join('');
        }

        function selectPlatform(platform) {
            currentPlatform = platform;
            const cats = {};
            platforms[platform].forEach(s => {
                const c = getCategory(s.name);
                if (!cats[c]) cats[c] = [];
                cats[c].push(s);
            });
            window.cats = cats;
            renderCategories();
        }

        function renderCategories() {
            hideAll(); show('categories-screen'); show('breadcrumb');
            document.getElementById('breadcrumb-text').textContent = currentPlatform;
            document.getElementById('step-title').textContent = 'Выберите категорию';
            const div = document.getElementById('categories-screen');
            div.innerHTML = Object.keys(window.cats).map(c => `
                <div class="list-item" onclick="selectCategory('${c}')">
                    <span class="li-name">${c}</span>
                    <span class="li-badge">${window.cats[c].length}</span>
                </div>
            `).join('');
        }

        function selectCategory(category) {
            currentCategory = category;
            document.getElementById('search').value = '';
            currentServices = window.cats[category];
            renderServices();
        }

        function renderServices() {
            hideAll(); show('services-screen'); show('search-box'); show('breadcrumb');
            document.getElementById('breadcrumb-text').textContent = currentPlatform + ' › ' + currentCategory;
            document.getElementById('step-title').textContent = 'Выберите услугу';
            displayServices(currentServices);
        }

        function displayServices(services) {
            const div = document.getElementById('services-screen');
            if (!services.length) { div.innerHTML = '<div class="empty">Ничего не найдено</div>'; return; }
            div.innerHTML = services.map(s => `
                <div class="s-card" onclick="showDetail(${s.service}, '${esc(s.name)}', '${esc(s.rate)}', ${s.min}, ${s.max})">
                    <div class="s-name">${esc(s.name)}</div>
                    <div class="s-prices">
                        <span class="s-price-tag lite">${getPrice(s.rate, 'lite')} ₽</span>
                        <span class="s-price-tag pro">${getPrice(s.rate, 'pro')} ₽</span>
                        <span class="s-price-tag max">${getPrice(s.rate, 'max')} ₽</span>
                    </div>
                </div>
            `).join('');
        }

        function filterServices() {
            const q = document.getElementById('search').value.toLowerCase();
            displayServices(currentServices.filter(s => s.name.toLowerCase().includes(q)));
        }

        function showDetail(serviceId, name, rate, min, max) {
            hideAll(); show('detail-screen'); show('breadcrumb');
            document.getElementById('breadcrumb-text').textContent = name.substring(0, 35);
            document.getElementById('step-title').textContent = 'Детали услуги';
            const priceLite = getPrice(rate, 'lite');
            const pricePro = getPrice(rate, 'pro');
            const priceMax = getPrice(rate, 'max');
            const savePro = ((parseFloat(priceLite) - parseFloat(pricePro)) / 1000).toFixed(2);
            const saveMax = ((parseFloat(priceLite) - parseFloat(priceMax)) / 1000).toFixed(2);
            document.getElementById('detail-screen').innerHTML = `
                <div class="detail-card">
                    <h3>${name}</h3>
                    <div class="price-levels">
                        <div class="price-block lite">
                            <div class="pl-name">🪨 Lite (0%)</div>
                            <div class="pl-price lite">${priceLite} ₽</div>
                        </div>
                        <div class="price-block pro">
                            <div class="pl-name">🥇 Pro (4%)</div>
                            <div class="pl-price pro">${pricePro} ₽</div>
                            <div class="pl-save">-${savePro} ₽</div>
                        </div>
                        <div class="price-block max">
                            <div class="pl-name">💎 Max (10%)</div>
                            <div class="pl-price max">${priceMax} ₽</div>
                            <div class="pl-save">-${saveMax} ₽</div>
                        </div>
                    </div>
                    <div class="detail-row"><span class="dl">Мин. заказ</span><span class="dv">${min}</span></div>
                    <div class="detail-row"><span class="dl">Макс. заказ</span><span class="dv">${max}</span></div>
                    <button class="btn-order" onclick="orderService(${serviceId}, '${esc(name)}', '${priceLite}', ${min}, ${max})">Заказать</button>
                </div>`;
        }

        function orderService(serviceId, name, price, min, max) {
            const params = new URLSearchParams({ service_id: serviceId, name: name, price: price, min: min, max: max, level: currentLevel });
            tg.openTelegramLink(`https://t.me/${BOT_USERNAME}?start=mini_${params.toString()}`);
            tg.close();
        }

        function goBack() {
            if (!document.getElementById('detail-screen').classList.contains('hidden')) renderServices();
            else if (!document.getElementById('services-screen').classList.contains('hidden')) renderCategories();
            else if (!document.getElementById('categories-screen').classList.contains('hidden')) renderPlatforms();
        }

        function esc(t) { return (t||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

        init();
    </script>
</body>
</html>
