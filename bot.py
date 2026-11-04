import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, json, os
from datetime import datetime, timedelta

BOT_TOKEN = "ВСТАВЬ_ТОКЕН_СЮДА"
bot = telebot.TeleBot(BOT_TOKEN)

LIVES_FILE = "lives.json"
SCORES_FILE = "scores.json"

# ============ СТРАНЫ ============
COUNTRIES = [
    ("Индия", "🇮🇳", "south_asia", 23000, 70, 0.026, 0.75, (0.55,0.35,0.10), 0.35),
    ("Пакистан", "🇵🇰", "south_asia", 6000, 66, 0.055, 0.55, (0.65,0.30,0.05), 0.37),
    ("Бангладеш", "🇧🇩", "south_asia", 3000, 74, 0.025, 0.75, (0.60,0.35,0.05), 0.40),
    ("Непал", "🇳🇵", "south_asia", 550, 70, 0.025, 0.65, (0.65,0.30,0.05), 0.21),
    ("Шри-Ланка", "🇱🇰", "south_asia", 320, 77, 0.006, 0.92, (0.45,0.45,0.10), 0.19),
    ("Афганистан", "🇦🇫", "south_asia", 1000, 65, 0.045, 0.40, (0.80,0.18,0.02), 0.26),
    ("Китай", "🇨🇳", "east_asia", 9000, 78, 0.006, 0.95, (0.30,0.55,0.15), 0.65),
    ("Япония", "🇯🇵", "east_asia", 800, 84, 0.002, 0.99, (0.20,0.60,0.20), 0.92),
    ("Южная Корея", "🇰🇷", "east_asia", 250, 83, 0.003, 0.98, (0.20,0.60,0.20), 0.81),
    ("Индонезия", "🇮🇩", "southeast_asia", 4500, 72, 0.018, 0.85, (0.50,0.40,0.10), 0.57),
    ("Филиппины", "🇵🇭", "southeast_asia", 2000, 71, 0.020, 0.85, (0.55,0.38,0.07), 0.48),
    ("Вьетнам", "🇻🇳", "southeast_asia", 1400, 75, 0.015, 0.92, (0.55,0.38,0.07), 0.40),
    ("Таиланд", "🇹🇭", "southeast_asia", 500, 79, 0.007, 0.94, (0.35,0.55,0.10), 0.53),
    ("Малайзия", "🇲🇾", "southeast_asia", 450, 76, 0.007, 0.94, (0.30,0.55,0.15), 0.78),
    ("Мьянма", "🇲🇲", "southeast_asia", 850, 66, 0.035, 0.75, (0.60,0.35,0.05), 0.31),
    ("Нигерия", "🇳🇬", "africa", 8000, 55, 0.070, 0.55, (0.70,0.25,0.05), 0.52),
    ("ДР Конго", "🇨🇩", "africa", 4000, 60, 0.065, 0.45, (0.80,0.18,0.02), 0.47),
    ("Эфиопия", "🇪🇹", "africa", 3800, 67, 0.040, 0.50, (0.75,0.22,0.03), 0.22),
    ("Кения", "🇰🇪", "africa", 1400, 66, 0.030, 0.65, (0.65,0.30,0.05), 0.29),
    ("Танзания", "🇹🇿", "africa", 1300, 66, 0.035, 0.60, (0.70,0.27,0.03), 0.36),
    ("Уганда", "🇺🇬", "africa", 1000, 63, 0.035, 0.55, (0.75,0.22,0.03), 0.26),
    ("ЮАР", "🇿🇦", "africa", 900, 64, 0.030, 0.90, (0.50,0.42,0.08), 0.68),
    ("Ангола", "🇦🇴", "africa", 800, 62, 0.045, 0.50, (0.75,0.22,0.03), 0.67),
    ("Мозамбик", "🇲🇿", "africa", 750, 61, 0.050, 0.45, (0.80,0.18,0.02), 0.38),
    ("Гана", "🇬🇭", "africa", 550, 64, 0.030, 0.75, (0.55,0.40,0.05), 0.58),
    ("Кот-д'Ивуар", "🇨🇮", "africa", 550, 59, 0.055, 0.55, (0.70,0.27,0.03), 0.53),
    ("Камерун", "🇨🇲", "africa", 600, 60, 0.045, 0.70, (0.65,0.30,0.05), 0.59),
    ("Мадагаскар", "🇲🇬", "africa", 650, 65, 0.040, 0.60, (0.75,0.22,0.03), 0.40),
    ("Мали", "🇲🇱", "africa", 850, 60, 0.060, 0.35, (0.85,0.13,0.02), 0.45),
    ("Нигер", "🇳🇪", "africa", 700, 62, 0.055, 0.30, (0.85,0.13,0.02), 0.17),
    ("Сенегал", "🇸🇳", "africa", 550, 68, 0.030, 0.50, (0.70,0.27,0.03), 0.49),
    ("Сомали", "🇸🇴", "africa", 450, 56, 0.070, 0.25, (0.90,0.09,0.01), 0.47),
    ("Чад", "🇹🇩", "africa", 550, 55, 0.070, 0.25, (0.90,0.09,0.01), 0.24),
    ("Малави", "🇲🇼", "africa", 650, 64, 0.035, 0.55, (0.80,0.18,0.02), 0.18),
    ("Замбия", "🇿🇲", "africa", 500, 62, 0.040, 0.60, (0.75,0.22,0.03), 0.46),
    ("Зимбабве", "🇿🇼", "africa", 400, 62, 0.040, 0.80, (0.75,0.22,0.03), 0.32),
    ("Руанда", "🇷🇼", "africa", 350, 67, 0.030, 0.65, (0.70,0.27,0.03), 0.18),
    ("Бурунди", "🇧🇮", "africa", 400, 62, 0.045, 0.50, (0.85,0.13,0.02), 0.14),
    ("Бенин", "🇧🇯", "africa", 400, 61, 0.050, 0.45, (0.80,0.18,0.02), 0.49),
    ("Гвинея", "🇬🇳", "africa", 450, 61, 0.055, 0.35, (0.85,0.13,0.02), 0.38),
    ("Южный Судан", "🇸🇸", "africa", 350, 58, 0.060, 0.30, (0.90,0.09,0.01), 0.21),
    ("Буркина-Фасо", "🇧🇫", "africa", 750, 60, 0.050, 0.35, (0.85,0.13,0.02), 0.32),
    ("Египет", "🇪🇬", "arab", 1900, 72, 0.017, 0.80, (0.55,0.38,0.07), 0.43),
    ("Алжир", "🇩🇿", "arab", 800, 77, 0.015, 0.85, (0.45,0.45,0.10), 0.75),
    ("Марокко", "🇲🇦", "arab", 500, 74, 0.017, 0.75, (0.55,0.38,0.07), 0.65),
    ("Тунис", "🇹🇳", "arab", 170, 77, 0.012, 0.85, (0.45,0.45,0.10), 0.70),
    ("Ливия", "🇱🇾", "arab", 120, 73, 0.012, 0.85, (0.40,0.48,0.12), 0.81),
    ("Судан", "🇸🇩", "arab", 1100, 66, 0.045, 0.55, (0.70,0.27,0.03), 0.36),
    ("Ирак", "🇮🇶", "arab", 900, 71, 0.022, 0.75, (0.55,0.38,0.07), 0.71),
    ("Сирия", "🇸🇾", "arab", 500, 73, 0.015, 0.75, (0.65,0.30,0.05), 0.57),
    ("Йемен", "🇾🇪", "arab", 700, 66, 0.045, 0.55, (0.75,0.22,0.03), 0.39),
    ("Саудовская Аравия", "🇸🇦", "arab", 550, 76, 0.006, 0.95, (0.30,0.55,0.15), 0.84),
    ("Иордания", "🇯🇴", "arab", 200, 75, 0.014, 0.92, (0.40,0.48,0.12), 0.92),
    ("Ливан", "🇱🇧", "arab", 80, 79, 0.007, 0.92, (0.45,0.45,0.10), 0.89),
    ("ОАЭ", "🇦🇪", "arab", 100, 78, 0.006, 0.95, (0.15,0.55,0.30), 0.87),
    ("Бразилия", "🇧🇷", "latam", 2600, 76, 0.013, 0.90, (0.40,0.45,0.15), 0.87),
    ("Мексика", "🇲🇽", "latam", 1800, 75, 0.012, 0.88, (0.45,0.42,0.13), 0.81),
    ("Колумбия", "🇨🇴", "latam", 650, 77, 0.012, 0.88, (0.45,0.42,0.13), 0.82),
    ("Аргентина", "🇦🇷", "latam", 500, 77, 0.009, 0.94, (0.35,0.50,0.15), 0.92),
    ("Перу", "🇵🇪", "latam", 550, 77, 0.010, 0.88, (0.45,0.42,0.13), 0.78),
    ("Венесуэла", "🇻🇪", "latam", 450, 72, 0.015, 0.92, (0.55,0.38,0.07), 0.88),
    ("Чили", "🇨🇱", "latam", 200, 80, 0.006, 0.95, (0.30,0.55,0.15), 0.88),
    ("Эквадор", "🇪🇨", "latam", 300, 77, 0.012, 0.88, (0.45,0.42,0.13), 0.64),
    ("Боливия", "🇧🇴", "latam", 250, 72, 0.022, 0.85, (0.55,0.38,0.07), 0.70),
    ("Уругвай", "🇺🇾", "latam", 45, 78, 0.006, 0.96, (0.25,0.55,0.20), 0.96),
    ("Куба", "🇨🇺", "latam", 120, 79, 0.005, 0.99, (0.50,0.45,0.05), 0.77),
    ("Гватемала", "🇬🇹", "latam", 350, 74, 0.020, 0.75, (0.60,0.35,0.05), 0.52),
    ("Гаити", "🇭🇹", "latam", 250, 64, 0.045, 0.60, (0.80,0.18,0.02), 0.57),
    ("Германия", "🇩🇪", "europe", 800, 81, 0.003, 0.98, (0.20,0.55,0.25), 0.78),
    ("Франция", "🇫🇷", "europe", 700, 82, 0.004, 0.98, (0.20,0.55,0.25), 0.81),
    ("Великобритания", "🇬🇧", "europe", 700, 81, 0.004, 0.98, (0.20,0.55,0.25), 0.84),
    ("Италия", "🇮🇹", "europe", 400, 83, 0.003, 0.98, (0.20,0.55,0.25), 0.71),
    ("Испания", "🇪🇸", "europe", 350, 83, 0.003, 0.98, (0.20,0.55,0.25), 0.81),
    ("Польша", "🇵🇱", "europe", 350, 78, 0.004, 0.98, (0.20,0.55,0.25), 0.60),
    ("Нидерланды", "🇳🇱", "europe", 170, 82, 0.003, 0.98, (0.15,0.55,0.30), 0.92),
    ("Бельгия", "🇧🇪", "europe", 115, 82, 0.003, 0.98, (0.15,0.55,0.30), 0.98),
    ("Швеция", "🇸🇪", "europe", 110, 83, 0.002, 0.98, (0.15,0.55,0.30), 0.88),
    ("Швейцария", "🇨🇭", "europe", 85, 84, 0.004, 0.98, (0.10,0.55,0.35), 0.74),
    ("Норвегия", "🇳🇴", "europe", 55, 83, 0.002, 0.98, (0.10,0.55,0.35), 0.83),
    ("Россия", "🇷🇺", "post_soviet", 1300, 73, 0.005, 0.98, (0.30,0.60,0.10), 0.75),
    ("Узбекистан", "🇺🇿", "post_soviet", 700, 72, 0.022, 0.90, (0.60,0.35,0.05), 0.50),
    ("Казахстан", "🇰🇿", "post_soviet", 400, 74, 0.008, 0.95, (0.35,0.55,0.10), 0.58),
    ("Украина", "🇺🇦", "post_soviet", 300, 72, 0.007, 0.98, (0.35,0.55,0.10), 0.70),
    ("Азербайджан", "🇦🇿", "post_soviet", 130, 74, 0.020, 0.90, (0.50,0.42,0.08), 0.57),
    ("США", "🇺🇸", "developed", 3600, 79, 0.006, 0.95, (0.20,0.50,0.30), 0.83),
    ("Канада", "🇨🇦", "developed", 380, 82, 0.004, 0.98, (0.15,0.55,0.30), 0.82),
    ("Австралия", "🇦🇺", "developed", 300, 83, 0.003, 0.98, (0.15,0.55,0.30), 0.86),
    ("Израиль", "🇮🇱", "developed", 180, 83, 0.003, 0.95, (0.20,0.50,0.30), 0.93),
    ("Сингапур", "🇸🇬", "developed", 40, 84, 0.002, 0.98, (0.10,0.55,0.35), 1.00),
    ("Катар", "🇶🇦", "developed", 30, 80, 0.006, 0.95, (0.10,0.50,0.40), 0.99),
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

NAMES = {
    "south_asia": {"m": ["Арджун","Раджеш","Викрам","Санджай","Адитья","Рохан","Кабир","Амир","Сунил","Деван","Нишан","Асиф","Фарук","Тарик","Раджит","Шахин"],
                   "f": ["Прия","Айша","Рани","Дивья","Ниша","Приянка","Сарита","Мила","Кали","Шанти","Фатима","Зара","Лайла","Надия","Самира","Тания"]},
    "east_asia": {"m": ["Вэй","Мин","Хиро","Джун","Кай","Тао","Юта","Хару","Минджун","Соджин","Чен","Джан","Вон","Хао","Кенджи","Рен"],
                  "f": ["Юки","Сакура","Мэй","Ли","Линь","Хана","Ёко","Суа","Мидзуки","Чжан","Минджи","Сора","Яна","Нгуен","Ти","Лан"]},
    "southeast_asia": {"m": ["Агус","Буди","Димас","Иван","Хуан","Хосе","Карло","Мигель","Нгуен","Тран","Ле","Фам","Сомчай","Нарат","Адитья","Ризал"],
                       "f": ["Дези","Сри","Вина","Аю","Мария","Роза","Луз","Карла","Линь","Май","Тху","Хоа","Плой","Ной","Аюни","Лала"]},
    "africa": {"m": ["Чинеду","Эмека","Кваме","Кофи","Джим","Аде","Олу","Муса","Абдул","Джон","Питер","Дэвид","Ибрагим","Мохамед","Самуэль","Джозеф"],
               "f": ["Нгози","Амара","Айша","Фатима","Амина","Зейнаб","Грейс","Мери","Джойс","Эстер","Номвело","Танди","Линда","Кейт","Ада","Чиома"]},
    "arab": {"m": ["Мухаммед","Ахмед","Али","Омар","Хасан","Хусейн","Юсуф","Ибрагим","Халид","Саид","Фейсал","Салем","Рашид","Тарик","Карим","Аднан"],
             "f": ["Фатима","Айша","Лейла","Марьям","Нур","Зейнаб","Сальма","Рания","Лина","Сара","Худа","Амаль","Ясмин","Сафия","Дана","Рим"]},
    "latam": {"m": ["Хуан","Карлос","Хосе","Педро","Луис","Мигель","Антонио","Франсиско","Хавьер","Диего","Рафаэль","Андрес","Пабло","Хорхе","Эдуардо","Роберто"],
              "f": ["Мария","Кармен","Изабель","Лусия","Ана","София","Валентина","Камила","Габриэла","Марта","Флоренсия","Элена","Роса","Пилар","Консуэло","Юлия"]},
    "europe": {"m": ["Томас","Максимилиан","Лукас","Феликс","Пол","Пьер","Люк","Джеймс","Джек","Оливер","Лео","Марко","Алессандро","Маттео","Жан","Иван"],
               "f": ["Анна","Эмилия","Софи","Клара","Шарлотта","Мария","Лея","Луиза","Эмма","Миа","Джулия","Кьяра","Изабель","Элена","Нора","Ханна"]},
    "post_soviet": {"m": ["Иван","Дмитрий","Александр","Сергей","Андрей","Михаил","Никита","Артём","Максим","Даниил","Тимур","Руслан","Егор","Кирилл","Глеб","Олег"],
                    "f": ["Анна","Мария","Елена","Ольга","Наташа","Катя","София","Даша","Алина","Полина","Кристина","Виктория","Юлия","Александра","Татьяна","Ксения"]},
    "developed": {"m": ["Джеймс","Джон","Майкл","Дэвид","Крис","Мэтт","Тайлер","Джек","Оливер","Ноа","Лиам","Итан","Мейсон","Лукас","Райан","Адам"],
                  "f": ["Эмили","Сара","Джессика","Эмма","Оливия","София","Ханна","Эбигейл","Миа","Шарлотта","Амелия","Харпер","Элла","Грейс","Хлоя","Лили"]},
}

INCOME_LABELS = ["Бедная семья", "Средний класс", "Богатая семья"]

REACTIONS = [
    "🎲 Судьба сегодня была не в духе.",
    "🌧 Иногда кубик просто падает не туда.",
    "🕯 Мир несправедлив. Но ты был здесь.",
    "✨ Ты прожил жизнь. Это уже немало.",
    "🌍 Где-то далеко кто-то прожил дольше. И это тоже ты мог быть.",
    "💫 Всё могло быть иначе. Но было так.",
    "🌱 Даже короткая жизнь — это целая жизнь.",
    "🎭 Занавес. Аплодисменты.",
]

players = {}

# ============ ПЕРСИСТЕНТНОСТЬ ============
def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    except Exception:
        pass

def add_to_memorial(user_id, life, mode="random", country_dict=None):
    lives = load_json(LIVES_FILE, [])
    rec = {
        "user_id": user_id,
        "name": life["name"],
        "country": life["country"][0],
        "flag": life["country"][1],
        "income": life["income"],
        "age": life["death_age"],
        "cause": life["death_cause"],
        "mode": mode,
        "date": datetime.utcnow().isoformat(),
    }
    lives.append(rec)
    lives = lives[-2000:]
    save_json(LIVES_FILE, lives)

def get_user_memorial(user_id, limit=10):
    lives = load_json(LIVES_FILE, [])
    mine = [x for x in lives if x["user_id"] == user_id]
    return list(reversed(mine[-limit:]))

def get_top(period_days=7, mode=None, limit=10):
    lives = load_json(LIVES_FILE, [])
    cutoff = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
    filtered = [x for x in lives if x["date"] >= cutoff]
    if mode:
        filtered = [x for x in filtered if x["mode"] == mode]
    # лучший результат по каждому user_id
    best = {}
    for r in filtered:
        uid = r["user_id"]
        if uid not in best or r["age"] > best[uid]["age"]:
            best[uid] = r
    ranked = sorted(best.values(), key=lambda x: x["age"], reverse=True)
    return ranked[:limit]

# ============ УТИЛИТЫ ============
def weighted_country(rng=random):
    r = rng.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def weighted_income(country, rng=random):
    r = rng.random()
    cum = 0
    for i, p in enumerate(country[7]):
        cum += p
        if r <= cum: return i
    return 0

def create_life(force_country=None, force_income=None):
    country = force_country or weighted_country()
    income = force_income if force_income is not None else weighted_income(country)
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    return {
        "country": country, "gender": gender, "name": name,
        "income": income, "urban": random.random() < country[8],
        "age": 0, "alive": True, "death_age": None, "death_cause": None,
        "education": "none", "job": None, "married": False, "children": 0,
        "chronic": False, "retired": False,
        "rerolled": False, "log": [], "last_result": None,
        "pending_echo": False, "saved": False, "phase": "birth",
        "mode": "random",
    }

def create_daily_life():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    rng = random.Random(today)
    country = weighted_country(rng)
    income = weighted_income(country, rng)
    gender = "m" if rng.random() < 0.51 else "f"
    name = rng.choice(NAMES[country[2]][gender])
    return {
        "country": country, "gender": gender, "name": name,
        "income": income, "urban": rng.random() < country[8],
        "age": 0, "alive": True, "death_age": None, "death_cause": None,
        "education": "none", "job": None, "married": False, "children": 0,
        "chronic": False, "retired": False,
        "rerolled": False, "log": [], "last_result": None,
        "pending_echo": False, "saved": False, "phase": "birth",
        "mode": "daily",
    }

def mortality_rate(l):
    age = l["age"]
    if age < 1: base = l["country"][5]
    elif age < 5: base = l["country"][5] / 3
    elif age < 40: base = 0.003
    elif age < 60: base = 0.008
    elif age < 70: base = 0.02
    elif age < 80: base = 0.05
    elif age < 90: base = 0.12
    else: base = 0.25
    if l["income"] == 0: base *= 1.4
    if l["income"] == 2: base *= 0.7
    if l["chronic"]: base *= 1.6
    return min(0.95, base)

def simulate_full(l):
    while l["alive"] and l["age"] < 110:
        l["age"] += 1
        if random.random() < mortality_rate(l):
            l["alive"] = False; l["death_age"] = l["age"]
            l["death_cause"] = "детская смертность" if l["age"] < 5 else ("болезнь" if l["age"] < 60 else "старость")
            break
        if l["age"] == 6: l["education"] = "primary" if random.random() < l["country"][6] else "none"
        if l["age"] == 15 and l["education"] == "primary" and random.random() < l["country"][6] * 0.9:
            l["education"] = "secondary"
        if l["age"] == 18 and l["education"] == "secondary" and random.random() < l["country"][6] * 0.4:
            l["education"] = "higher"
        if l["age"] == 22 and not l["job"]:
            l["job"] = "специалист" if l["education"] == "higher" else ("рабочий" if l["education"] == "secondary" else "подработка")
        if l["age"] == 28 and not l["married"] and random.random() < 0.55: l["married"] = True
        if 28 <= l["age"] <= 40 and l["married"] and random.random() < 0.15: l["children"] += 1
        if l["age"] == 65: l["retired"] = True
    if l["alive"]:
        l["alive"] = False; l["death_age"] = l["age"]; l["death_cause"] = "старость"

# ============ СОБЫТИЯ ============
def get_event(l):
    age = l["age"]
    if age == 6:
        return {"title": "Пора в школу",
                "text": f"Тебе шесть. {l['country'][1]} {l['country'][0]}. " + ("Школа рядом." if l["country"][6] > 0.85 else "Школ на всех не хватает.") + " Родители решают.",
                "choices": [{"text": "📚 Отдать в школу", "p": l["country"][6], "success": "edu_school", "fail": "edu_none"},
                            {"text": "🏠 Оставить дома", "p": 1, "success": "edu_none", "fail": None}]}
    if age == 15 and l["education"] == "primary":
        return {"title": "После начальной",
                "text": "Тебе пятнадцать. Средняя школа даст больше шансов, но семье нужны деньги.",
                "choices": [{"text": "📖 Продолжить учёбу", "p": l["country"][6] * 0.85, "success": "edu_secondary", "fail": "work_early"},
                            {"text": "💼 Пойти работать", "p": 1, "success": "work_early", "fail": None}]}
    if age == 18 and l["education"] == "secondary":
        uni_p = l["country"][6] * (0.7 if l["income"] == 2 else 0.4 if l["income"] == 1 else 0.15)
        return {"title": "После школы",
                "text": "Восемнадцать. Университет — или сразу работа.",
                "choices": [{"text": "🎓 Университет", "p": uni_p, "success": "edu_higher", "fail": "work"},
                            {"text": "💼 Работать", "p": 1, "success": "work", "fail": None}]}
    if age == 25 and not l["married"]:
        marry_p = max(0.05, 0.55 + (0.15 if l["income"] == 2 else -0.1 if l["income"] == 0 else 0))
        return {"title": "Отношения",
                "text": "Тебе двадцать пять. Встречаешь человека. Что дальше?",
                "choices": [{"text": "💍 Создать семью", "p": marry_p, "success": "married", "fail": "single"},
                            {"text": "⏳ Подождать", "p": 1, "success": "single", "fail": None}]}
    if age == 30 and l["married"] and l["children"] == 0:
        child_p = max(0.05, 0.8 - (0.2 if l["income"] == 0 else 0))
        return {"title": "Дети",
                "text": "Тридцать. Пора решать, будут ли дети.",
                "choices": [{"text": "👶 Завести ребёнка", "p": child_p, "success": "child", "fail": "nochild"},
                            {"text": "⏳ Не сейчас", "p": 1, "success": "nochild", "fail": None}]}
    if age == 50 and l["income"] == 0 and not l["chronic"]:
        return {"title": "Здоровье",
                "text": "Пятьдесят. Тело даёт сбой. Лечение стоит денег.",
                "choices": [{"text": "💊 Лечиться", "p": 0.5, "success": "healed", "fail": "chronic"},
                            {"text": "😣 Терпеть", "p": 1, "success": "chronic", "fail": None}]}
    if age == 65 and not l["retired"]:
        return {"title": "Старость",
                "text": "Шестьдесят пять. Работа или покой?",
                "choices": [{"text": "🌴 На пенсию", "p": 1, "success": "retire", "fail": None},
                            {"text": "💼 Работать дальше", "p": 1, "success": "work_old", "fail": None}]}
    return None

def apply_outcome(l, outcome):
    if outcome == "edu_school": l["education"] = "primary"; return "Ты пошёл в школу."
    if outcome == "edu_none": l["education"] = "none"; return "Школа прошла мимо."
    if outcome == "edu_secondary": l["education"] = "secondary"; return "Ты продолжил учёбу."
    if outcome == "work_early": l["education"] = "primary"; l["job"] = "подработка"; return "Ты начал работать рано."
    if outcome == "edu_higher": l["education"] = "higher"; return "Ты поступил в университет."
    if outcome == "work": l["job"] = "рабочий" if l["education"] == "secondary" else "подработка"; return "Ты начал работать."
    if outcome == "married": l["married"] = True; return "Ты создал семью."
    if outcome == "single": return "Ты остался один."
    if outcome == "child": l["children"] = 1; return "У тебя родился ребёнок."
    if outcome == "nochild": return "Детей не случилось."
    if outcome == "healed": return "Ты вылечился."
    if outcome == "chronic": l["chronic"] = True; return "Болезнь осталась с тобой."
    if outcome == "retire": l["retired"] = True; return "Ты вышел на пенсию."
    if outcome == "work_old": l["job"] = l["job"] or "рабочий"; return "Ты продолжаешь работать."
    return "Год прошёл."

def get_echo(l, n):
    age = l["age"]
    if age == 7:
        edu = "не пошёл в школу" if n["education"] == "none" else "пошёл в школу"
        return f"Твой сосед по судьбе живёт в {n['country'][1]} {n['country'][0]}. Он {edu}."
    if age == 30:
        if age >= n["death_age"]:
            return f"Твой сосед по судьбе уже умер — в {n['death_age']} лет. А ты ещё живёшь."
        fam = "в браке" if n["married"] else "один"
        ch = f"у него {n['children']} детей" if n["children"] else "без детей"
        return f"Твоему соседу тоже {age}. Он {fam}, {ch}. Живёт в {n['country'][0]}."
    if age == 60:
        if age >= n["death_age"]:
            return f"Твой сосед по судьбе умер в {n['death_age']} лет. А ты всё ещё здесь."
        work = f"работает — {n['job']}" if n["job"] else "без работы"
        pen = "На пенсии. " if n["retired"] else ""
        return f"Твоему соседу тоже {age}. Он {work}. {pen}Всё ещё в {n['country'][0]}."
    return ""

# ============ ФОРМАТИРОВАНИЕ ============
def rarity_percent(country): return country[3] / TOTAL_WEIGHT * 100
def rarity_tag(r): 
    if r < 0.1: return "🔥 легендарное рождение"
    if r < 1: return "✨ редкое рождение"
    if r < 5: return "🌟 необычное рождение"
    return "обычное рождение"
def edu_label(e): return {"none": "нет", "primary": "начальное", "secondary": "среднее", "higher": "высшее"}.get(e, "—")
def family_label(l):
    if not l["married"]: return "один"
    return f"в браке, {l['children']} детей" if l["children"] else "в браке, без детей"

def format_birth(l):
    rar = rarity_percent(l["country"])
    mode_tag = " · 📅 daily" if l["mode"] == "daily" else ""
    return (f"👶 <b>Ты родился</b>{mode_tag}\n\n"
            f"🌍 Страна: {l['country'][1]} <b>{l['country'][0]}</b>\n"
            f"👤 Имя: <b>{l['name']}</b>\n"
            f"👨‍👩‍👧 Семья: {INCOME_LABELS[l['income']]}\n"
            f"🏙 Место: {'Город' if l['urban'] else 'Деревня'}\n"
            f"🎲 Редкость: <b>{rar:.2f}%</b> — {rarity_tag(rar)}\n\n"
            f"🪞 В эту же секунду где-то родился твой <b>сосед по судьбе</b>. Ты узнаешь его позже.")

def format_year(l):
    parts = [f"<b>{l['age']} лет</b>"]
    if l["last_result"]:
        r = l["last_result"]
        parts.append(("✅ Удача" if r["success"] else "❌ Не повезло") + f" (шанс {r['chance']}%)")
        parts.append(r["text"])
    parts.append("")
    parts.append(f"📚 Учёба: {edu_label(l['education'])}")
    parts.append(f"💼 Работа: {l['job'] or '—'}")
    parts.append(f"💍 Семья: {family_label(l)}")
    parts.append(f"❤️ Здоровье: {'слабое' if l['chronic'] else 'норма'}")
    if l["log"]:
        parts.append("\n<i>Последнее:</i>")
        for e in l["log"][-3:]:
            parts.append(f"• {e['age']}: {e['text']}")
    return "\n".join(parts)

def format_event(l, evt):
    return (f"<b>{l['age']} лет · {evt['title']}</b>\n\n{evt['text']}\n\n"
            f"<i>🎲 Под каждой кнопкой — шанс. Ты не знаешь, выпадет ли.</i>")

# ============ КЛАВИАТУРЫ ============
def kb_intro():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎲 Родиться", callback_data="new_life"))
    kb.add(InlineKeyboardButton("📅 Daily-челлендж", callback_data="daily_life"))
    kb.add(InlineKeyboardButton("🏆 Рейтинг недели", callback_data="show_top"))
    return kb

def kb_birth():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("▶️ Жить", callback_data="year"))
    return kb

def kb_year():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("▶️ Следующий год", callback_data="year"))
    return kb

def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices):
        kb.add(InlineKeyboardButton(f"{c['text']}  ·  {int(c['p']*100)}%", callback_data=f"choice_{i}"))
    return kb

def kb_after_fail():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎁 Перебросить (1 раз)", callback_data="reroll"))
    kb.add(InlineKeyboardButton("▶️ Жить дальше", callback_data="year"))
    return kb

def kb_echo():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("▶️ Жить дальше", callback_data="year"))
    return kb

def kb_death():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🪞 Прожить жизнь соседа", callback_data="neighbor_life"))
    kb.add(InlineKeyboardButton("🎲 Новое рождение", callback_data="new_life"))
    kb.add(InlineKeyboardButton("📅 Daily-челлендж", callback_data="daily_life"))
    kb.add(InlineKeyboardButton("🕯 Мемориал", callback_data="show_memorial"))
    kb.add(InlineKeyboardButton("📤 Поделиться", callback_data="share"))
    return kb

# ============ ЛОГИКА ============
def start_new_life(user_id, force_country=None, force_income=None, daily=False):
    l = create_daily_life() if daily else create_life(force_country, force_income)
    n_country = weighted_country()
    guard = 0
    while n_country[0] == l["country"][0] and guard < 30:
        n_country = weighted_country(); guard += 1
    n = create_life(n_country)
    simulate_full(n)
    players[user_id] = {"you": l, "neighbor": n}
    return l, n

def step_year(user_id, chat_id):
    p = players.get(user_id)
    if not p:
        bot.send_message(chat_id, "Начни заново: /start"); return
    l = p["you"]

    if l.get("pending_echo"):
        l["pending_echo"] = False
        send_echo(user_id, chat_id); return

    l["age"] += 1
    l["last_result"] = None

    if random.random() < mortality_rate(l):
        l["alive"] = False
        l["death_age"] = l["age"]
        l["death_cause"] = "детская смертность" if l["age"] < 5 else ("болезнь" if l["age"] < 60 else "старость")
        send_death(user_id, chat_id); return

    evt = get_event(l)
    has_echo = l["age"] in (7, 30, 60)

    if evt:
        l["current_event"] = evt
        l["pending_echo"] = has_echo
        l["phase"] = "event"
        bot.send_message(chat_id, format_event(l, evt), reply_markup=kb_event(evt["choices"]), parse_mode="HTML")
    elif has_echo:
        send_echo(user_id, chat_id)
    else:
        l["phase"] = "year"
        bot.send_message(chat_id, format_year(l), reply_markup=kb_year(), parse_mode="HTML")

def resolve_choice(user_id, chat_id, i):
    p = players.get(user_id); l = p["you"]
    evt = l.get("current_event")
    if not evt: return
    c = evt["choices"][i]

    l["snapshot"] = {k: l[k] for k in ["education","job","married","children","chronic","retired"]}
    l["snapshot"]["log_len"] = len(l["log"])

    success = random.random() < c["p"]
    outcome = c["success"] if success else c["fail"]
    text = apply_outcome(l, outcome) if outcome else "Год прошёл."
    l["log"].append({"age": l["age"], "text": text})
    l["last_result"] = {"success": success, "text": text, "chance": int(c["p"]*100)}
    l["phase"] = "year"

    if not success and not l["rerolled"]:
        l["can_reroll"] = {"success": c["success"], "fail": c["fail"], "chance": c["p"]}
        msg = (f"🎲 <b>Не повезло</b> (шанс был {int(c['p']*100)}%)\n\n{text}\n\n"
               f"🎁 У тебя есть <b>один шанс за жизнь</b> изменить это. Потратить?")
        bot.send_message(chat_id, msg, reply_markup=kb_after_fail(), parse_mode="HTML")
    else:
        bot.send_message(chat_id, format_year(l), reply_markup=kb_year(), parse_mode="HTML")

def do_reroll(user_id, chat_id):
    p = players.get(user_id); l = p["you"]
    if l["rerolled"] or not l.get("can_reroll"):
        bot.send_message(chat_id, "Переброс недоступен.", reply_markup=kb_year()); return
    l["rerolled"] = True
    cr = l["can_reroll"]; l["can_reroll"] = None

    snap = l.get("snapshot", {})
    for k in ["education","job","married","children","chronic","retired"]:
        if k in snap: l[k] = snap[k]
    if "log_len" in snap: l["log"] = l["log"][:snap["log_len"]]

    success = random.random() < cr["chance"]
    outcome = cr["success"] if success else cr["fail"]
    text = apply_outcome(l, outcome) if outcome else "Год прошёл."
    l["log"].append({"age": l["age"], "text": "🎁 Переброс: " + text})

    if success: msg = f"🎁 <b>Переброс удался!</b>\n\n{text}"
    else: msg = f"😔 <b>Переброс не помог.</b>\n\n{text}"
    bot.send_message(chat_id, msg, reply_markup=kb_year(), parse_mode="HTML")

def send_echo(user_id, chat_id):
    p = players.get(user_id)
    text = get_echo(p["you"], p["neighbor"])
    bot.send_message(chat_id, f"🪞 <b>Тень соседа по судьбе</b>\n\n{text}", reply_markup=kb_echo(), parse_mode="HTML")

def send_death(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; n = p["neighbor"]

    # сохраняем в мемориал
    if not l.get("saved"):
        add_to_memorial(user_id, l, l.get("mode", "random"))
        l["saved"] = True

    def card(x):
        return "\n".join([
            f"<b>{x['name']}</b>",
            f"{x['country'][1]} {x['country'][0]} · {INCOME_LABELS[x['income']]}",
            f"⏳ Умер в {x['death_age']} лет",
            f"📚 {edu_label(x['education'])}",
            f"💼 {x['job'] or '—'}",
            f"💍 {family_label(x)}",
        ])

    diff = l["death_age"] - n["death_age"]
    if diff > 0: tail = f"Ты прожил на <b>{diff}</b> лет дольше."
    elif diff < 0: tail = f"Сосед прожил на <b>{-diff}</b> лет дольше."
    else: tail = "Вы умерли в одном возрасте."

    le = l["country"][4]
    if l["death_age"] >= le + 10: rank = "🔥 прожил дольше ожидаемого для своей страны"
    elif l["death_age"] >= le: rank = "✨ прожил свою норму"
    elif l["death_age"] >= le - 10: rank = "обычная продолжительность"
    else: rank = "😔 жизнь оборвалась рано"

    # проверка на топ-10
    top = get_top(7, mode=None, limit=10)
    in_top = any(t["user_id"] == user_id and t["age"] == l["death_age"] for t in top)
    top_line = "\n🏆 <b>Ты в топ-10 недели!</b>" if in_top else ""

    reaction = random.choice(REACTIONS)

    msg = (f"💀 <b>Жизнь прожита</b>\n\n{card(l)}\n\n"
           f"🪞 <b>Сосед по судьбе</b>\n{card(n)}\n\n"
           f"Вы родились в одну секунду. {tail}\n{rank}{top_line}\n\n"
           f"<i>{reaction}</i>")
    bot.send_message(chat_id, msg, reply_markup=kb_death(), parse_mode="HTML")

def show_memorial(chat_id, user_id):
    lives = get_user_memorial(user_id, 10)
    if not lives:
        bot.send_message(chat_id, "🕯 Твой мемориал пуст. Проживи жизнь — она здесь появится.")
        return
    lines = ["🕯 <b>Твой мемориал</b> · последние 10 жизней\n"]
    for r in lives:
        mode = "📅" if r.get("mode") == "daily" else ""
        lines.append(f"{r['flag']} <b>{r['name']}</b> · {r['country']}{mode} — {r['age']} лет ({r['cause']})")
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

def show_top(chat_id, mode=None):
    period = "за неделю" if not mode else "за сегодня (daily)"
    top = get_top(1 if mode == "daily" else 7, mode=mode, limit=10)
    if not top:
        bot.send_message(chat_id, f"🏆 Рейтинг {period} пуст. Стань первым!")
        return
    medals = ["🥇", "🥈", "🥉"]
    lines = [f"🏆 <b>Топ-10 {period}</b>\n"]
    for i, r in enumerate(top):
        pre = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{pre} {r['flag']} <b>{r['name']}</b> · {r['country']} — <b>{r['age']}</b> лет")
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

# ============ ХЭНДЛЕРЫ ============
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    text = ("🎲 <b>1 из 8: Эхо</b>\n<i>Симулятор случайной жизни</i>\n\n"
            "В эту секунду на Земле родилось около 5 детей.\n"
            "Ты — один из них. И ты не выбираешь, где.\n\n"
            "🪞 <b>Сосед по судьбе</b> — тот, кто родился в ту же секунду. Тень в 7, 30, 60 лет.\n"
            "🎁 <b>Кубик судьбы</b> — один переброс за жизнь.\n"
            "🎲 <b>Редкость рождения</b> — узнай, насколько повезло со страной.\n\n"
            "<i>Команды:</i>\n"
            "/daily — 📅 челлендж дня (одинаковый старт для всех)\n"
            "/memorial — 🕯 твои прошлые жизни\n"
            "/top — 🏆 рейтинг недели\n"
            "/top_daily — 🏆 рейтинг дня\n"
            "/help — справка\n\n"
            "Готов?")
    bot.send_message(msg.chat.id, text, reply_markup=kb_intro(), parse_mode="HTML")

@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = ("<b>Как играть</b>\n\n"
            "1. Жми «Родиться» — получишь случайную страну, семью, имя.\n"
            "2. Жми «Жить» — годы идут, события требуют выбора.\n"
            "3. Под каждой кнопкой — шанс. Кубик решает.\n"
            "4. Один раз за жизнь можешь перебросить неудачу.\n"
            "5. На 7, 30 и 60 годах — тень соседа по судьбе.\n"
            "6. Умрёшь — увидишь его жизнь рядом со своей. И сможешь прожить её.\n\n"
            "<b>Команды:</b>\n"
            "/start — начать\n/daily — челлендж дня\n/memorial — мемориал\n"
            "/top — рейтинг недели\n/top_daily — рейтинг дня")
    bot.send_message(msg.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=["daily"])
def cmd_daily(msg):
    l, n = start_new_life(msg.from_user.id, daily=True)
    bot.send_message(msg.chat.id, "📅 <b>Челлендж дня</b>\n<i>Старт одинаковый для всех. Кубики — честные.</i>\n\n" + format_birth(l),
                     reply_markup=kb_birth(), parse_mode="HTML")

@bot.message_handler(commands=["memorial"])
def cmd_memorial(msg):
    show_memorial(msg.chat.id, msg.from_user.id)

@bot.message_handler(commands=["top"])
def cmd_top(msg):
    show_top(msg.chat.id, mode=None)

@bot.message_handler(commands=["top_daily"])
def cmd_top_daily(msg):
    show_top(msg.chat.id, mode="daily")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    d = call.data

    if d == "new_life":
        l, n = start_new_life(uid, daily=False)
        bot.send_message(chat_id, format_birth(l), reply_markup=kb_birth(), parse_mode="HTML")
    elif d == "daily_life":
        l, n = start_new_life(uid, daily=True)
        bot.send_message(chat_id, "📅 <b>Челлендж дня</b>\n\n" + format_birth(l),
                         reply_markup=kb_birth(), parse_mode="HTML")
    elif d == "year":
        step_year(uid, chat_id)
    elif d.startswith("choice_"):
        resolve_choice(uid, chat_id, int(d.split("_")[1]))
    elif d == "reroll":
        do_reroll(uid, chat_id)
    elif d == "neighbor_life":
        p = players.get(uid)
        if p:
            nc = p["neighbor"]["country"]; ni = p["neighbor"]["income"]
            l, n = start_new_life(uid, nc, ni, daily=False)
            bot.send_message(chat_id, "🪞 <b>Теперь ты — сосед.</b>\n\n" + format_birth(l),
                             reply_markup=kb_birth(), parse_mode="HTML")
    elif d == "show_memorial":
        show_memorial(chat_id, uid)
    elif d == "show_top":
        show_top(chat_id, mode=None)
    elif d == "share":
        p = players.get(uid)
        if p:
            l = p["you"]; n = p["neighbor"]
            text = (f"Я родился в {l['country'][0]} ({INCOME_LABELS[l['income']].lower()}). "
                    f"Прожил {l['death_age']} лет.\n"
                    f"Мой сосед по судьбе — {n['country'][0]}, {n['death_age']} лет.\n"
                    f"Разница: {abs(l['death_age'] - n['death_age'])} лет. 🎲\n\n#1из8 #Эхо")
            bot.send_message(chat_id, f"<code>{text}</code>\n\n👆 скопируй и поделись", parse_mode="HTML")

print("Бот запущен...")
bot.infinity_polling()