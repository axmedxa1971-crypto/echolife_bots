import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os

try:
    import io
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ВСТАВЬ СЮДА СВОЙ ТОКЕН (с двоеточием!)
BOT_TOKEN = "9280691375:AAFKE--UbHjtBr4MBI6sWavaUFwWhXO9arc"
bot = telebot.TeleBot(BOT_TOKEN)

# ================= СПРАВОЧНИКИ =================
COUNTRIES = [
    ("Индия", "🇮🇳", "south_asia", 23000, 70, 0.75, 0.35, 2500, 83.5, "₹"),
    ("Пакистан", "🇵🇰", "south_asia", 6000, 66, 0.55, 0.37, 1500, 278.0, "₨"),
    ("Китай", "🇨🇳", "east_asia", 9000, 78, 0.95, 0.65, 12000, 7.2, "¥"),
    ("Япония", "🇯🇵", "east_asia", 800, 84, 0.99, 0.92, 35000, 150.0, "¥"),
    ("Нигерия", "🇳🇬", "africa", 8000, 55, 0.55, 0.52, 2000, 1500.0, "₦"),
    ("Эфиопия", "🇪🇹", "africa", 3800, 67, 0.50, 0.22, 1000, 57.0, "Br"),
    ("Египет", "🇪🇬", "arab", 1900, 72, 0.80, 0.43, 4000, 48.0, "E£"),
    ("Бразилия", "🇧🇷", "latam", 2600, 76, 0.90, 0.87, 8000, 5.1, "R$"),
    ("Германия", "🇩🇪", "europe", 800, 81, 0.98, 0.78, 45000, 0.92, "€"),
    ("США", "🇺🇸", "developed", 3600, 79, 0.95, 0.83, 55000, 1.0, "$"),
    ("Россия", "🇷🇺", "post_soviet", 1300, 73, 0.98, 0.75, 10000, 92.0, "₽"),
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

NAMES = {
    "south_asia": {"m": ["Арджун", "Раджеш", "Викрам"], "f": ["Прия", "Айша", "Рани"]},
    "east_asia": {"m": ["Вэй", "Мин", "Хиро"], "f": ["Юки", "Сакура", "Мэй"]},
    "africa": {"m": ["Чинеду", "Эмека", "Кваме"], "f": ["Нгози", "Амара", "Айша"]},
    "arab": {"m": ["Мухаммед", "Ахмед", "Али"], "f": ["Фатима", "Лейла", "Марьям"]},
    "latam": {"m": ["Хуан", "Карлос", "Хосе"], "f": ["Мария", "Кармен", "Изабель"]},
    "europe": {"m": ["Томас", "Лукас", "Феликс"], "f": ["Анна", "Эмилия", "Софи"]},
    "post_soviet": {"m": ["Иван", "Дмитрий", "Сергей"], "f": ["Анна", "Мария", "Елена"]},
    "developed": {"m": ["Джеймс", "Джон", "Майкл"], "f": ["Эмили", "Сара", "Джессика"]},
}

INCOME_LABELS = ["Бедная семья", "Средний класс", "Богатая семья"]

players = {}

# ================= УТИЛИТЫ =================
def fmt_money(amount_usd, country):
    rate = country[8]
    symbol = country[9]
    return f"{int(amount_usd * rate):,} {symbol}".replace(",", " ")

def get_status(cash):
    if cash < 0: return "💸 В долгах"
    if cash < 500: return "🥀 Нищий"
    if cash < 5000: return "👕 Бедный"
    if cash < 20000: return "🔧 Рабочий класс"
    if cash < 100000: return "🏠 Средний класс"
    if cash < 500000: return "💼 Зажиточный"
    return "👑 Элита"

def weighted_country():
    r = random.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def create_life(force_country=None):
    country = force_country if force_country else weighted_country()
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    start_cash = int(country[7] * random.uniform(0.1, 2.0))
    
    return {
        "country": country, "gender": gender, "name": name,
        "cash": start_cash, "in_prison": 0, "age": 0,
        "education": "Нет", "job": "Безработный", "salary": 0,
        "job_type": "none", "married": False, "diseases": [],
        "life_map": [], "alive": True
    }

def generate_neighbors(count=3):
    neighbors = []
    for _ in range(count):
        c = weighted_country()
        g = random.choice(["m", "f"])
        name = random.choice(NAMES[c[2]][g])
        death_age = int(random.gauss(c[4], 10))
        fate = random.choice(["умер(ла) в младенчестве", "стал(а) богатым бизнесменом", "погиб(ла) в криминальной разборке", "живет скромно на заводе", "обычная жизнь"])
        neighbors.append({"name": name, "country": c, "death_age": death_age, "fate": fate})
    return neighbors

def add_map(l, text):
    if len(l["life_map"]) < 5: l["life_map"].append(f"{l['age']} лет: {text}")

# ================= ГРАФИКА =================
def generate_pixel_art(l, scene_type="life"):
    if not HAS_PIL: return None
    w, h = 100, 50
    img = Image.new('RGB', (w, h), color='#1a1a2e')
    d = ImageDraw.Draw(img)
    
    if scene_type == "prison" or l["in_prison"] > 0:
        d.rectangle([0, 0, w, h], fill='#2b2b2b')
        for i in range(10, w, 15): d.line([(i, 0), (i, h)], fill='#555555', width=2)
    elif scene_type == "hospital" or l["diseases"]:
        d.rectangle([0, 0, w, h], fill='#e0e0e0')
        d.rectangle([30, 30, 70, 40], fill='#ffffff', outline='#9e9e9e')
        d.rectangle([45, 10, 55, 12], fill='#ff0000')
        d.rectangle([49, 6, 51, 16], fill='#ff0000')
    elif scene_type == "rich" or l["cash"] > 500000:
        d.rectangle([0, 0, w, 30], fill='#ff7043')
        d.rectangle([15, 10, 85, 35], fill='#eceff1')
        d.polygon([(10, 10), (50, -5), (90, 10)], fill='#b71c1c')
    elif scene_type == "child" or l["age"] < 13:
        d.rectangle([0, 0, w, 30], fill='#81d4fa')
        d.rectangle([0, 30, w, h], fill='#66bb6a')
        d.rectangle([10, 15, 35, 35], fill='#a1887f')
        d.polygon([(5, 15), (22, 5), (40, 15)], fill='#d32f2f')
    else:
        d.rectangle([0, 0, w, 30], fill='#1a237e')
        d.rectangle([0, 30, w, h], fill='#424242')

    hero_color = '#4da6ff' if l["gender"] == "m" else '#ff66b2'
    d.rectangle([45, 28, 50, 36], fill=hero_color)
    d.rectangle([46, 23, 49, 28], fill='#ffcc99')

    img = img.resize((w*5, h*5), resample=Image.NEAREST)
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def send_scene(chat_id, l, text, kb, scene_type="life"):
    if l["in_prison"] > 0: scene_type = "prison"
    elif l["diseases"]: scene_type = "hospital"
    elif l["cash"] > 500000: scene_type = "rich"
    elif l["age"] < 13: scene_type = "child"
    
    photo = generate_pixel_art(l, scene_type)
    if photo:
        try:
            bot.send_photo(chat_id, photo, caption=text, reply_markup=kb, parse_mode="HTML")
            return
        except: pass
    bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")

# ================= ИГРА =================
def next_year(user_id, chat_id):
    p = players.get(user_id); l = p["you"]
    l["age"] += 1
    
    if l["in_prison"] > 0:
        l["in_prison"] -= 1
        if l["in_prison"] == 0: return send_scene(chat_id, l, "⛓ <b>Ты вышел на свободу.</b>", kb_year())
        return send_scene(chat_id, l, f"⛓ <b>Тюрьма.</b> Осталось: {l['in_prison']} лет.", kb_year(), "prison")

    # Смерть
    if l["age"] > 60 and random.random() < (l["age"] - 60) * 0.03:
        return send_death(user_id, chat_id)

    # Эхо
    echo = ""
    if l["age"] in [7, 18, 30, 50]:
        n = random.choice(p["neighbors"])
        echo = f"\n\n👥 <b>Эхо:</b> {n['name']} ({n['country'][1]})... "
        echo += "умер(ла)." if n["death_age"] < l["age"] else f"жив(а) и {n['fate']}."

    if l["age"] == 22 and l["job_type"] == "none":
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("💼 Работа", callback_data="job_civ"),
            InlineKeyboardButton("💊 Криминал", callback_data="job_crim")
        )
        return send_scene(chat_id, l, "Выбор пути: как будешь зарабатывать?" + echo, kb)

    send_scene(chat_id, l, format_year(l) + echo, kb_year())

def send_death(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    map_text = "📜 <b>Карта жизни:</b>\n" + "\n".join([f"• {e}" for e in l["life_map"]]) if l["life_map"] else ""
    
    msg = (f"💀 <b>Ты умер в {l['age']} лет.</b>\n"
           f"Итог: {get_status(l['cash'])}\nДеньги: {fmt_money(l['cash'], c)}\n\n"
           f"{map_text}\n\n"
           f"<i>Твои ровесники:</i>\n")
    kb = InlineKeyboardMarkup()
    for i, n in enumerate(p["neighbors"]):
        msg += f"• {n['name']} ({n['country'][1]}): умер в {n['death_age']} ({n['fate']})\n"
        kb.add(InlineKeyboardButton(f"🎭 Прожить жизнь {n['name']}", callback_data=f"play_{i}"))
    
    kb.add(InlineKeyboardButton("🎲 Начать заново", callback_data="new"))
    send_scene(chat_id, l, msg, kb, "hospital")

def format_year(l):
    c = l["country"]
    return (f"<b>Возраст: {l['age']}</b>\n\n"
            f"💰 Баланс: <b>{fmt_money(l['cash'], c)}</b>\n"
            f"👑 Статус: {get_status(l['cash'])}\n"
            f"💼 Работа: {l['job']}\n"
            f"🎓 Образование: {l['education']}")

def kb_year():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("▶️ Следующий год", callback_data="year"))

# ================= ХЭНДЛЕРЫ =================
@bot.message_handler(commands=["start"])
def start(msg):
    text = "🎲 <b>1 из 8: Эхо</b>\n\nТы родишься в случайной точке Земли. Узнай свою судьбу!"
    bot.send_message(msg.chat.id, text, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new")), parse_mode="HTML")

@bot.message_handler(commands=["test"])
def test(msg):
    l = {"gender": "m", "cash": 1000000, "age": 25, "in_prison": 0, "diseases": []}
    p = generate_pixel_art(l, "rich")
    if p: bot.send_photo(msg.chat.id, p, caption="✅ Pillow работает!")
    else: bot.send_message(msg.chat.id, "❌ Pillow не установлен.")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id; chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    d = call.data

    if d == "new":
        l = create_life()
        players[uid] = {"you": l, "neighbors": generate_neighbors()}
        add_map(l, "Родился")
        msg = f"👶 <b>Ты родился!</b>\n👤 {l['name']} ({l['country'][1]} {l['country'][0]})"
        send_scene(chat_id, l, msg, kb_year(), "child")
        
    elif d == "year":
        next_year(uid, chat_id)
        
    elif d == "job_civ":
        l = players[uid]["you"]
        l["job_type"] = "civilian"; l["job"] = "Работник"; l["cash"] += 5000
        add_map(l, "Устроился на работу")
        send_scene(chat_id, l, "Ты устроился на работу.", kb_year())
        
    elif d == "job_crim":
        l = players[uid]["you"]
        l["job_type"] = "criminal"; l["job"] = "Бандит"; l["cash"] += 15000
        add_map(l, "Стал бандитом")
        send_scene(chat_id, l, "Ты связался с криминалом. Деньги есть, но риск велик.", kb_year())
        
    elif d.startswith("play_"):
        idx = int(d.split("_")[1])
        n = players[uid]["neighbors"][idx]
        l = create_life(force_country=n["country"])
        l["name"] = n["name"]
        players[uid] = {"you": l, "neighbors": generate_neighbors()}
        add_map(l, "Родился (смена судьбы)")
        msg = f"🎭 <b>Новая судьба!</b>\nТы теперь {l['name']} ({l['country'][1]})."
        send_scene(chat_id, l, msg, kb_year(), "child")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
