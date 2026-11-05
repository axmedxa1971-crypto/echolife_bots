import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, json, os
from datetime import datetime, timedelta

BOT_TOKEN = "9280691375:AAFKE--UbHjtBr4MBI6sWavaUFwWhXO9arc"
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
    ("Афганистан", "🇦🇫", "south_asia", 1000, import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, json, os
from datetime import datetime

try:
    import io
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ================= НАСТРОЙКА =================
BOT_TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН" # <--- ОБЯЗАТЕЛЬНО ЗАМЕНИ
bot = telebot.TeleBot(BOT_TOKEN)

# ================= СТАТИСТИКА =================
STATS_FILE = "stats.json"
def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"total_lives": 0}

def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(stats, f, ensure_ascii=False)
    except: pass

GLOBAL_STATS = load_stats()

# ================= СПРАВОЧНИКИ (85 СТРАН) =================
COUNTRIES = [
    ("Индия", "🇮🇳", "south_asia", 23000, 70, 0.026, 0.75, (0.55,0.35,0.10), 0.35, 2500, 83.5, "₹"),
    ("Пакистан", "🇵🇰", "south_asia", 6000, 66, 0.055, 0.55, (0.65,0.30,0.05), 0.37, 1500, 278.0, "₨"),
    ("Бангладеш", "🇧🇩", "south_asia", 3000, 74, 0.025, 0.75, (0.60,0.35,0.05), 0.40, 2000, 110.0, "৳"),
    ("Непал", "🇳🇵", "south_asia", 550, 70, 0.025, 0.65, (0.65,0.30,0.05), 0.21, 1200, 133.0, "₨"),
    ("Шри-Ланка", "🇱🇰", "south_asia", 320, 77, 0.006, 0.92, (0.45,0.45,0.10), 0.19, 3800, 300.0, "₨"),
    ("Афганистан", "🇦🇫", "south_asia", 1000, 65, 0.045, 0.40, (0.80,0.18,0.02), 0.26, 800, 70.0, "؋"),
    ("Китай", "🇨🇳", "east_asia", 9000, 78, 0.006, 0.95, (0.30,0.55,0.15), 0.65, 12000, 7.2, "¥"),
    ("Япония", "🇯🇵", "east_asia", 800, 84, 0.002, 0.99, (0.20,0.60,0.20), 0.92, 35000, 150.0, "¥"),
    ("Южная Корея", "🇰🇷", "east_asia", 250, 83, 0.003, 0.98, (0.20,0.60,0.20), 0.81, 33000, 1330.0, "₩"),
    ("Монголия", "🇲🇳", "east_asia", 80, 70, 0.015, 0.90, (0.55,0.38,0.07), 0.68, 4500, 3450.0, "₮"),
    ("Индонезия", "🇮🇩", "southeast_asia", 4500, 72, 0.018, 0.85, (0.50,0.40,0.10), 0.57, 4500, 15800.0, "Rp"),
    ("Филиппины", "🇵🇭", "southeast_asia", 2000, 71, 0.020, 0.85, (0.55,0.38,0.07), 0.48, 3500, 56.0, "₱"),
    ("Вьетнам", "🇻🇳", "southeast_asia", 1400, 75, 0.015, 0.92, (0.55,0.38,0.07), 0.40, 4000, 24500.0, "₫"),
    ("Таиланд", "🇹🇭", "southeast_asia", 500, 79, 0.007, 0.94, (0.35,0.55,0.10), 0.53, 7000, 35.0, "฿"),
    ("Малайзия", "🇲🇾", "southeast_asia", 450, 76, 0.007, 0.94, (0.30,0.55,0.15), 0.78, 11000, 4.7, "RM"),
    ("Мьянма", "🇲🇲", "southeast_asia", 850, 66, 0.035, 0.75, (0.60,0.35,0.05), 0.31, 1400, 2100.0, "K"),
    ("Нигерия", "🇳🇬", "africa", 8000, 55, 0.070, 0.55, (0.70,0.25,0.05), 0.52, 2000, 1500.0, "₦"),
    ("ДР Конго", "🇨🇩", "africa", 4000, 60, 0.065, 0.45, (0.80,0.18,0.02), 0.47, 600, 2800.0, "₣"),
    ("Эфиопия", "🇪🇹", "africa", 3800, 67, 0.040, 0.50, (0.75,0.22,0.03), 0.22, 1000, 57.0, "Br"),
    ("Кения", "🇰🇪", "africa", 1400, 66, 0.030, 0.65, (0.65,0.30,0.05), 0.29, 2000, 130.0, "KSh"),
    ("Танзания", "🇹🇿", "africa", 1300, 66, 0.035, 0.60, (0.70,0.27,0.03), 0.36, 1100, 2500.0, "TSh"),
    ("Уганда", "🇺🇬", "africa", 1000, 63, 0.035, 0.55, (0.75,0.22,0.03), 0.26, 900, 3800.0, "USh"),
    ("ЮАР", "🇿🇦", "africa", 900, 64, 0.030, 0.90, (0.50,0.42,0.08), 0.68, 6000, 18.0, "R"),
    ("Ангола", "🇦🇴", "africa", 800, 62, 0.045, 0.50, (0.75,0.22,0.03), 0.67, 2500, 830.0, "Kz"),
    ("Мозамбик", "🇲🇿", "africa", 750, 61, 0.050, 0.45, (0.80,0.18,0.02), 0.38, 500, 63.0, "MT"),
    ("Гана", "🇬🇭", "africa", 550, 64, 0.030, 0.75, (0.55,0.40,0.05), 0.58, 2200, 15.0, "₵"),
    ("Кот-д'Ивуар", "🇨🇮", "africa", 550, 59, 0.055, 0.55, (0.70,0.27,0.03), 0.53, 2300, 620.0, "CFA"),
    ("Камерун", "🇨🇲", "africa", 600, 60, 0.045, 0.70, (0.65,0.30,0.05), 0.59, 1500, 620.0, "FCFA"),
    ("Мадагаскар", "🇲🇬", "africa", 650, 65, 0.040, 0.60, (0.75,0.22,0.03), 0.40, 500, 4400.0, "Ar"),
    ("Мали", "🇲🇱", "africa", 850, 60, 0.060, 0.35, (0.85,0.13,0.02), 0.45, 800, 620.0, "CFA"),
    ("Нигер", "🇳🇪", "africa", 700, 62, 0.055, 0.30, (0.85,0.13,0.02), 0.17, 550, 620.0, "CFA"),
    ("Сенегал", "🇸🇳", "africa", 550, 68, 0.030, 0.50, (0.70,0.27,0.03), 0.49, 1600, 620.0, "CFA"),
    ("Сомали", "🇸🇴", "africa", 450, 56, 0.070, 0.25, (0.90,0.09,0.01), 0.47, 450, 570.0, "Sh"),
    ("Замбия", "🇿🇲", "africa", 500, 62, 0.040, 0.60, (0.75,0.22,0.03), 0.46, 1300, 26.0, "ZK"),
    ("Зимбабве", "🇿🇼", "africa", 400, 62, 0.040, 0.80, (0.75,0.22,0.03), 0.32, 1200, 360.0, "Z$"),
    ("Руанда", "🇷🇼", "africa", 350, 67, 0.030, 0.65, (0.70,0.27,0.03), 0.18, 800, 1300.0, "RF"),
    ("Египет", "🇪🇬", "arab", 1900, 72, 0.017, 0.80, (0.55,0.38,0.07), 0.43, 4000, 48.0, "E£"),
    ("Алжир", "🇩🇿", "arab", 800, 77, 0.015, 0.85, (0.45,0.45,0.10), 0.75, 4500, 135.0, "DA"),
    ("Марокко", "🇲🇦", "arab", 500, 74, 0.017, 0.75, (0.55,0.38,0.07), 0.65, 3500, 10.0, "DH"),
    ("Тунис", "🇹🇳", "arab", 170, 77, 0.012, 0.85, (0.45,0.45,0.10), 0.70, 4000, 3.1, "DT"),
    ("Ливия", "🇱🇾", "arab", 120, 73, 0.012, 0.85, (0.40,0.48,0.12), 0.81, 6500, 4.8, "LD"),
    ("Судан", "🇸🇩", "arab", 1100, 66, 0.045, 0.55, (0.70,0.27,0.03), 0.36, 700, 600.0, "SDG"),
    ("Ирак", "🇮🇶", "arab", 900, 71, 0.022, 0.75, (0.55,0.38,0.07), 0.71, 4500, 1310.0, "IQD"),
    ("Сирия", "🇸🇾", "arab", 500, 73, 0.015, 0.75, (0.65,0.30,0.05), 0.57, 1200, 13000.0, "S£"),
    ("Йемен", "🇾🇪", "arab", 700, 66, 0.045, 0.55, (0.75,0.22,0.03), 0.39, 800, 250.0, "YR"),
    ("Саудовская Аравия", "🇸🇦", "arab", 550, 76, 0.006, 0.95, (0.30,0.55,0.15), 0.84, 25000, 3.75, "SR"),
    ("Иордания", "🇯🇴", "arab", 200, 75, 0.014, 0.92, (0.40,0.48,0.12), 0.92, 4500, 0.71, "JD"),
    ("Ливан", "🇱🇧", "arab", 80, 79, 0.007, 0.92, (0.45,0.45,0.10), 0.89, 4500, 15000.0, "L£"),
    ("ОАЭ", "🇦🇪", "arab", 100, 78, 0.006, 0.95, (0.15,0.55,0.30), 0.87, 45000, 3.67, "DH"),
    ("Бразилия", "🇧🇷", "latam", 2600, 76, 0.013, 0.90, (0.40,0.45,0.15), 0.87, 8000, 5.1, "R$"),
    ("Мексика", "🇲🇽", "latam", 1800, 75, 0.012, 0.88, (0.45,0.42,0.13), 0.81, 9000, 17.0, "MX$"),
    ("Колумбия", "🇨🇴", "latam", 650, 77, 0.012, 0.88, (0.45,0.42,0.13), 0.82, 6000, 3900.0, "C$"),
    ("Аргентина", "🇦🇷", "latam", 500, 77, 0.009, 0.94, (0.35,0.50,0.15), 0.92, 12000, 350.0, "AR$"),
    ("Перу", "🇵🇪", "latam", 550, 77, 0.010, 0.88, (0.45,0.42,0.13), 0.78, 6500, 3.8, "S/"),
    ("Венесуэла", "🇻🇪", "latam", 450, 72, 0.015, 0.92, (0.55,0.38,0.07), 0.88, 3500, 36.0, "Bs"),
    ("Чили", "🇨🇱", "latam", 200, 80, 0.006, 0.95, (0.30,0.55,0.15), 0.88, 15000, 950.0, "CL$"),
    ("Эквадор", "🇪🇨", "latam", 300, 77, 0.012, 0.88, (0.45,0.42,0.13), 0.64, 6000, 1.0, "$"),
    ("Боливия", "🇧🇴", "latam", 250, 72, 0.022, 0.85, (0.55,0.38,0.07), 0.70, 3500, 6.9, "Bs"),
    ("Уругвай", "🇺🇾", "latam", 45, 78, 0.006, 0.96, (0.25,0.55,0.20), 0.96, 17000, 39.0, "U$"),
    ("Куба", "🇨🇺", "latam", 120, 79, 0.005, 0.99, (0.50,0.45,0.05), 0.77, 9000, 24.0, "CUP"),
    ("Гватемала", "🇬🇹", "latam", 350, 74, 0.020, 0.75, (0.60,0.35,0.05), 0.52, 4500, 7.8, "Q"),
    ("Гаити", "🇭🇹", "latam", 250, 64, 0.045, 0.60, (0.80,0.18,0.02), 0.57, 1700, 130.0, "G"),
    ("Германия", "🇩🇪", "europe", 800, 81, 0.003, 0.98, (0.20,0.55,0.25), 0.78, 45000, 0.92, "€"),
    ("Франция", "🇫🇷", "europe", 700, 82, 0.004, 0.98, (0.20,0.55,0.25), 0.81, 42000, 0.92, "€"),
    ("Великобритания", "🇬🇧", "europe", 700, 81, 0.004, 0.98, (0.20,0.55,0.25), 0.84, 46000, 0.79, "£"),
    ("Италия", "🇮🇹", "europe", 400, 83, 0.003, 0.98, (0.20,0.55,0.25), 0.71, 34000, 0.92, "€"),
    ("Испания", "🇪🇸", "europe", 350, 83, 0.003, 0.98, (0.20,0.55,0.25), 0.81, 30000, 0.92, "€"),
    ("Польша", "🇵🇱", "europe", 350, 78, 0.004, 0.98, (0.20,0.55,0.25), 0.60, 18000, 4.0, "zł"),
    ("Нидерланды", "🇳🇱", "europe", 170, 82, 0.003, 0.98, (0.15,0.55,0.30), 0.92, 55000, 0.92, "€"),
    ("Бельгия", "🇧🇪", "europe", 115, 82, 0.003, 0.98, (0.15,0.55,0.30), 0.98, 50000, 0.92, "€"),
    ("Швеция", "🇸🇪", "europe", 110, 83, 0.002, 0.98, (0.15,0.55,0.30), 0.88, 55000, 10.5, "kr"),
    ("Швейцария", "🇨🇭", "europe", 85, 84, 0.004, 0.98, (0.10,0.55,0.35), 0.74, 85000, 0.88, "CHF"),
    ("Норвегия", "🇳🇴", "europe", 55, 83, 0.002, 0.98, (0.10,0.55,0.35), 0.83, 80000, 10.5, "kr"),
    ("Португалия", "🇵🇹", "europe", 85, 82, 0.003, 0.98, (0.20,0.55,0.25), 0.66, 25000, 0.92, "€"),
    ("Греция", "🇬🇷", "europe", 85, 82, 0.003, 0.98, (0.20,0.55,0.25), 0.80, 20000, 0.92, "€"),
    ("Австрия", "🇦🇹", "europe", 85, 82, 0.003, 0.98, (0.15,0.55,0.30), 0.59, 50000, 0.92, "€"),
    ("Россия", "🇷🇺", "post_soviet", 1300, 73, 0.005, 0.98, (0.30,0.60,0.10), 0.75, 10000, 92.0, "₽"),
    ("Узбекистан", "🇺🇿", "post_soviet", 700, 72, 0.022, 0.90, (0.60,0.35,0.05), 0.50, 2500, 12600.0, "so'm"),
    ("Казахстан", "🇰🇿", "post_soviet", 400, 74, 0.008, 0.95, (0.35,0.55,0.10), 0.58, 10000, 450.0, "₸"),
    ("Украина", "🇺🇦", "post_soviet", 300, 72, 0.007, 0.98, (0.35,0.55,0.10), 0.70, 4000, 37.0, "₴"),
    ("Азербайджан", "🇦🇿", "post_soviet", 130, 74, 0.020, 0.90, (0.50,0.42,0.08), 0.57, 5500, 1.7, "₼"),
    ("Беларусь", "🇧🇾", "post_soviet", 100, 74, 0.005, 0.98, (0.30,0.60,0.10), 0.79, 7000, 3.3, "Br"),
    ("США", "🇺🇸", "developed", 3600, 79, 0.006, 0.95, (0.20,0.50,0.30), 0.83, 55000, 1.0, "$"),
    ("Канада", "🇨🇦", "developed", 380, 82, 0.004, 0.98, (0.15,0.55,0.30), 0.82, 50000, 1.36, "C$"),
    ("Австралия", "🇦🇺", "developed", 300, 83, 0.003, 0.98, (0.15,0.55,0.30), 0.86, 55000, 1.5, "A$"),
    ("Израиль", "🇮🇱", "developed", 180, 83, 0.003, 0.95, (0.20,0.50,0.30), 0.93, 45000, 3.7, "₪"),
    ("Сингапур", "🇸🇬", "developed", 40, 84, 0.002, 0.98, (0.10,0.55,0.35), 1.00, 65000, 1.35, "S$"),
    ("Катар", "🇶🇦", "developed", 30, 80, 0.006, 0.95, (0.10,0.50,0.40), 0.99, 60000, 3.64, "QR"),
    ("Новая Зеландия", "🇳🇿", "developed", 60, 82, 0.004, 0.98, (0.15,0.55,0.30), 0.86, 42000, 1.6, "NZ$"),
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

DISEASES = {
    "Астма": {"desc": "Хроническое воспаление дыхательных путей.", "mort": 1.1, "cash": 300, "fert": 0},
    "Диабет 1 типа": {"desc": "Инсулинозависимый диабет.", "mort": 1.4, "cash": 1500, "fert": -15},
    "Диабет 2 типа": {"desc": "Нарушение обмена веществ.", "mort": 1.2, "cash": 800, "fert": -10},
    "Гипертония": {"desc": "Повышенное давление.", "mort": 1.3, "cash": 400, "fert": 0},
    "Туберкулез": {"desc": "Инфекция легких.", "mort": 1.8, "cash": 1500, "fert": -20},
    "Сифилис": {"desc": "Венерическое заболевание.", "mort": 1.3, "cash": 500, "fert": -50},
    "ВИЧ/СПИД": {"desc": "Вирус иммунодефицита.", "mort": 1.5, "cash": 2000, "fert": -30},
    "Рак легких": {"desc": "Опухоль легких.", "mort": 3.0, "cash": 5000, "fert": -100},
    "ПТСР": {"desc": "Посттравматическое расстройство.", "mort": 1.4, "cash": 500, "fert": 0},
    "Депрессия": {"desc": "Стойкое снижение настроения.", "mort": 1.3, "cash": 400, "fert": 0},
    "Алкоголизм": {"desc": "Зависимость от алкоголя.", "mort": 1.8, "cash": 600, "fert": -20},
    "Сердечная недостаточность": {"desc": "Сердце не справляется.", "mort": 2.2, "cash": 1500, "fert": 0},
    "Инфаркт": {"desc": "Омертвение участка сердца.", "mort": 2.5, "cash": 3000, "fert": 0},
    "Цирроз печени": {"desc": "Печень разрушена.", "mort": 2.2, "cash": 1000, "fert": -20},
    "Бесплодие": {"desc": "Неспособность иметь детей.", "mort": 1.0, "cash": 0, "fert": -100},
}

ETHNICITIES = {
    "south_asia": [("Хиндустанец", 35, None),("Бенгалец", 15, "Общество считает тебя бедным."),("Тамил", 10, "Общество считает тебя хитрым."),("Мусульманин", 15, "Общество считает тебя агрессивным."),("Далит", 10, "Общество считает тебя грязным.")],
    "east_asia": [("Хань", 60, None),("Японец", 15, "Общество считает тебя трудоголиком."),("Кореец", 12, "Общество считает тебя умным."),("Монгол", 5, "Общество считает тебя дикарем.")],
    "southeast_asia": [("Яванец", 35, None),("Тайец", 20, None),("Вьетнамец", 15, "Общество считает тебя хитрым."),("Филиппинец", 15, "Общество считает тебя беззаботным.")],
    "africa": [("Йоруба", 20, None),("Игбо", 15, "Общество считает тебя предприимчивым."),("Хауса", 15, "Общество считает тебя фанатиком."),("Зулус", 10, "Общество считает тебя агрессивным.")],
    "arab": [("Араб", 55, None),("Египтянин", 20, None),("Бербер", 8, "Общество считает тебя дикарем."),("Курд", 5, "Общество считает тебя сепаратистом.")],
    "latam": [("Метис", 45, None),("Креол", 20, "Общество считает тебя снобом."),("Мулат", 15, None),("Индеец", 10, "Общество считает тебя дикарем.")],
    "europe": [("Немец", 12, None),("Француз", 12, None),("Итальянец", 8, "Считают, что ты связан с мафией."),("Еврей", 8, "Считают тебя скупым."),("Цыган", 8, "Считают тебя вором."),("Турок", 8, "Считают тебя чужаком.")],
    "post_soviet": [("Русский", 50, None),("Украинец", 15, None),("Белорус", 5, None),("Кавказец", 10, "Считают тебя бандитом."),("Еврей", 4, "Считают тебя скупым."),("Среднеазиат", 8, "Считают тебя гастарбайтером.")],
    "developed": [("WASP", 35, None),("Афроамериканец", 18, "Считают тебя агрессивным."),("Латиноамериканец", 15, "Считают тебя нелегалом."),("Азиат", 12, "Считают тебя умным."),("Еврей", 5, "Считают тебя скупым.")],
}

NAMES = {
    "south_asia": {"m": ["Арджун","Раджеш","Викрам","Адитья","Рохан","Кабир","Амир","Сунил","Деван"], "f": ["Прия","Айша","Рани","Дивья","Ниша","Приянка","Фатима","Сита","Лакшми"]},
    "east_asia": {"m": ["Вэй","Мин","Хиро","Джун","Кай","Тао","Юта","Хару","Чен"], "f": ["Юки","Сакура","Мэй","Ли","Линь","Хана","Ёко","Суа","Мина"]},
    "southeast_asia": {"m": ["Агус","Буди","Димас","Хуан","Хосе","Карло","Мигель","Анвар"], "f": ["Дези","Сри","Вина","Аю","Мария","Роза","Луз","Карла","Нур"]},
    "africa": {"m": ["Чинеду","Эмека","Кваме","Кофи","Аде","Олу","Муса","Абдул","Джамал"], "f": ["Нгози","Амара","Айша","Фатима","Амина","Зейнаб","Грейс","Мери","Танди"]},
    "arab": {"m": ["Мухаммед","Ахмед","Али","Омар","Хасан","Хусейн","Юсуф","Ибрагим","Халид"], "f": ["Фатима","Айша","Лейла","Марьям","Нур","Зейнаб","Сальма","Рания","Лина"]},
    "latam": {"m": ["Хуан","Карлос","Хосе","Педро","Луис","Мигель","Антонио","Франсиско","Диего"], "f": ["Мария","Кармен","Изабель","Лусия","Ана","София","Валентина","Камила","Марта"]},
    "europe": {"m": ["Томас","Лукас","Феликс","Пол","Пьер","Люк","Джеймс","Джек","Марко"], "f": ["Анна","Эмилия","Софи","Клара","Шарлотта","Мария","Лея","Луиза","Эмма"]},
    "post_soviet": {"m": ["Иван","Дмитрий","Александр","Сергей","Андрей","Михаил","Никита","Артём","Тимур"], "f": ["Анна","Мария","Елена","Ольга","Наташа","Катя","София","Даша","Алина"]},
    "developed": {"m": ["Джеймс","Джон","Майкл","Дэвид","Крис","Мэтт","Тайлер","Джек","Ноа"], "f": ["Эмили","Сара","Джессика","Эмма","Оливия","София","Ханна","Эбигейл","Миа"]},
}

CAREER_TITLES = {
    "civilian": {1: "Стажер", 2: "Специалист", 3: "Старший специалист", 4: "Менеджер", 5: "Директор"},
    "police": {1: "Курсант", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Полковник"},
    "military": {1: "Рядовой", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Генерал"},
    "criminal": {1: "Шестерка", 2: "Боец", 3: "Бригадир", 4: "Авторитет", 5: "Босс"},
}

SCHOOLS = {
    "south_asia": ["Начальная школа Раджа Капура", "Колледж Св. Ксавьера", "Университет Дели"],
    "east_asia": ["Школа №1", "Токийский колледж", "Университет Васэда"],
    "southeast_asia": ["Государственная школа", "Политехникум", "Университет Индонезии"],
    "africa": ["Деревенская школа", "Технический колледж", "Университет Кейптауна"],
    "arab": ["Школа Аль-Фараби", "Исламский колледж", "Университет Каира"],
    "latam": ["Школа Святой Марии", "Колледж Сан-Паулу", "Национальный Университет"],
    "europe": ["Гимназия им. Гёте", "Лицей Вольтера", "Оксфордский Университет"],
    "post_soviet": ["Средняя школа №15", "Колледж связи", "МГУ им. Ломоносова"],
    "developed": ["High School", "Community College", "MIT / Гарвард"],
}

TESTS = {
    1: [{"q": "5 + 7?", "opts": ["10", "12", "13"], "ans": 1},{"q": "Сколько цветов у радуги?", "opts": ["5", "7", "9"], "ans": 1}],
    2: [{"q": "x - 4 = 10, x?", "opts": ["6", "14", "40"], "ans": 1},{"q": "Столица Франции?", "opts": ["Лондон", "Париж", "Берлин"], "ans": 1}],
    3: [{"q": "Столица Австралии?", "opts": ["Сидней", "Мельбурн", "Канберра"], "ans": 2},{"q": "Производная x^2?", "opts": ["x", "2x", "x^3/3"], "ans": 1}],
}

PROPERTIES = {"Общага": 3000, "Квартира": 30000, "Дом": 200000, "Особняк": 1500000}
CARS = {"Скутер": 800, "Седан": 15000, "Внедорожник": 40000, "Спорткар": 200000}
BUSINESSES = {"Ларёк": 5000, "Кофейня": 25000, "Ресторан": 150000, "Завод": 2000000}

INCOME_LABELS = ["Бедная семья", "Средний класс", "Богатая семья"]
REACTIONS = ["🎲 Судьба сегодня была не в духе.", "🌧 Иногда кубик просто падает не туда.", "🕯 Мир несправедлив. Но ты был здесь.", "✨ Ты прожил жизнь. Это уже немало.", "💀 Смерть — единственное, что гарантировано."]

players = {}

# ================= ГРАФИКА =================
def generate_pixel_art(l, scene_type="life"):
    if not HAS_PIL: return None
    w, h = 100, 50
    img = Image.new('RGB', (w, h), color='#1a1a2e')
    d = ImageDraw.Draw(img)
    
    if scene_type == "prison" or (l and l["in_prison"] > 0):
        d.rectangle([0, 0, w, h], fill='#2b2b2b')
        for i in range(10, w, 15): d.line([(i, 0), (i, h)], fill='#555555', width=2)
        d.line([(0, 15), (w, 15)], fill='#555555', width=2)
        d.rectangle([10, 35, 40, 45], fill='#4a3b2b')
    elif scene_type == "hospital" or (l and l["diseases"] and random.random() < 0.3):
        d.rectangle([0, 0, w, h], fill='#e0e0e0')
        d.rectangle([0, 30, w, h], fill='#90a4ae')
        d.rectangle([30, 30, 70, 40], fill='#ffffff', outline='#9e9e9e')
        d.rectangle([45, 10, 55, 12], fill='#ff0000')
        d.rectangle([49, 6, 51, 16], fill='#ff0000')
    elif scene_type == "office" or (l and l["job_type"] in ["civilian", "police"]):
        d.rectangle([0, 0, w, 25], fill='#4fc3f7')
        d.rectangle([0, 25, w, h], fill='#8d6e63')
        d.rectangle([20, 30, 80, 40], fill='#5d4037')
    elif scene_type == "rich" or (l and l.get("clean_cash", 0) > 500000):
        d.rectangle([0, 0, w, 30], fill='#ff7043')
        d.ellipse([80, 5, 95, 20], fill='#ffca28')
        d.rectangle([0, 30, w, h], fill='#2e7d32')
        d.rectangle([15, 10, 85, 35], fill='#eceff1')
        d.polygon([(10, 10), (50, -5), (90, 10)], fill='#b71c1c')
        d.rectangle([60, 40, 90, 48], fill='#29b6f6')
    elif scene_type == "child" or (l and l["age"] < 13):
        d.rectangle([0, 0, w, 30], fill='#81d4fa')
        d.ellipse([80, 5, 90, 15], fill='#fff176')
        d.rectangle([0, 30, w, h], fill='#66bb6a')
        d.rectangle([10, 15, 35, 35], fill='#a1887f')
        d.polygon([(5, 15), (22, 5), (40, 15)], fill='#d32f2f')
    else:
        d.rectangle([0, 0, w, 30], fill='#1a237e')
        d.ellipse([80, 5, 90, 15], fill='#fff59d')
        d.rectangle([0, 30, w, h], fill='#424242')
        d.rectangle([20, 15, 22, 35], fill='#757575')
        d.ellipse([16, 10, 26, 18], fill='#ffff8d')

    if l:
        hero_color = '#4da6ff' if l["gender"] == "m" else '#ff66b2'
        if l["job_type"] == "criminal" or l["faction"] != "Нет": hero_color = '#212121'
        elif scene_type == "rich": hero_color = '#ffd700'
        d.rectangle([45, 28, 50, 36], fill=hero_color)
        d.rectangle([46, 23, 49, 28], fill='#ffcc99')
        if scene_type == "family" or (l["married"] and scene_type == "life"):
            d.rectangle([52, 29, 56, 36], fill='#9e9e9e')
            d.rectangle([53, 25, 55, 29], fill='#ffcc99')

    img = img.resize((w*5, h*5), resample=Image.NEAREST)
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def send_scene(chat_id, l, text, kb, scene_type=None):
    if not scene_type:
        if l and l["in_prison"] > 0: scene_type = "prison"
        elif l and l["diseases"] and random.random() < 0.3: scene_type = "hospital"
        elif l and l.get("clean_cash", 0) > 500000: scene_type = "rich"
        elif l and l["age"] < 13: scene_type = "child"
        elif l and l["job_type"] in ["civilian", "police"] and l["job"] != "Безработный": scene_type = "office"
        else: scene_type = "life"
        
    photo = generate_pixel_art(l, scene_type)
    if photo:
        try:
            bot.send_photo(chat_id, photo, caption=text, reply_markup=kb, parse_mode="HTML")
            return
        except: pass
    bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")

# ================= УТИЛИТЫ =================
def fmt_money(amount_usd, country):
    rate = country[10]; symbol = country[11]
    real_amount = int(amount_usd * rate)
    return f"{real_amount:,} {symbol}".replace(",", " ")

def get_wealth_status(clean, dirty, l=None):
    total = clean + dirty
    if l and l.get("properties"): total += sum(p["value"] for p in l["properties"])
    if l and l.get("cars"): total += sum(c["value"] for c in l["cars"])
    if total < 0: return "💸 В долгах"
    if total < 500: return "🥀 Нищий"
    if total < 5000: return "👕 Бедный"
    if total < 20000: return "🔧 Рабочий класс"
    if total < 100000: return "🏠 Средний класс"
    if total < 500000: return "💼 Зажиточный"
    if total < 2000000: return "💎 Богач"
    return "👑 Элита"

def weighted_country():
    r = random.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def weighted_income(country):
    r = random.random(); cum = 0
    for i, p in enumerate(country[7]):
        cum += p
        if r <= cum: return i
    return 0

def get_ethnicity(region):
    r = random.random() * 100; cum = 0
    for name, chance, prejudice in ETHNICITIES.get(region, [("Местный", 100, None)]):
        cum += chance
        if r <= cum: return name, prejudice
    return "Местный", None

def generate_neighbors(count=3):
    neighbors = []
    for _ in range(count):
        c = weighted_country(); inc = weighted_income(c); g = random.choice(["m", "f"])
        name = random.choice(NAMES[c[2]][g])
        death_age = int(random.gauss(c[4], 12))
        if death_age < 1: death_age = random.randint(1, 5)
        fate_roll = random.random()
        if fate_roll < 0.1: fate = "умер(ла) в младенчестве"
        elif fate_roll < 0.2: fate = "стал(а) богатым бизнесменом/политиком"
        elif fate_roll < 0.3: fate = "погиб(ла) в криминальной разборке"
        elif fate_roll < 0.4: fate = "получил(а) высшее образование и живет в достатке"
        elif fate_roll < 0.6: fate = "живет скромно, работает на заводе"
        else: fate = "обычная жизнь, умер(ла) от старости"
        neighbors.append({"name": name, "country": c, "gender": g, "income": inc, "death_age": death_age, "fate": fate})
    return neighbors

def create_life(force_country=None, force_income=None):
    country = force_country if force_country else weighted_country()
    income = force_income if force_income is not None else weighted_income(country)
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    ethnicity, prejudice = get_ethnicity(country[2])
    start_cash = country[9] * (0.1 if income == 0 else 1 if income == 1 else 5)
    start_cash = int(start_cash * random.uniform(0.5, 1.5))
    siblings = []
    for _ in range(random.randint(0, 4)):
        s_g = random.choice(["m", "f"])
        siblings.append({"name": random.choice(NAMES[country[2]][s_g]), "gender": s_g, "fate": "Жив(а)"})
    return {
        "country": country, "gender": gender, "name": name, "ethnicity": ethnicity, "prejudice": prejudice,
        "income": income, "clean_cash": start_cash, "dirty_cash": 0, "faction": "Нет", "rank": "-", "in_prison": 0,
        "age": 0, "alive": True, "death_age": None, "death_cause": None, "education": "Нет", "job": "Безработный", "salary": 0,
        "job_type": "none", "career_xp": 0, "career_rank": 1, "married": False, "children": 0, "diseases": [], "fertility": 100,
        "properties": [], "cars": [], "last_result": None, "current_event": None, "test_data": None,
        "asked_tests": {1: [], 2: [], 3: []}, "life_map": [], "siblings": siblings, "debt": 0
    }

def mortality_rate(l):
    age = l["age"]; base = 0.05 if age < 5 else 0.003
    if age > 60: base = 0.02
    if age > 80: base = 0.1
    if l["in_prison"] > 0: base *= 1.5
    if l["debt"] > 0: base *= 1.3
    for d in l["diseases"]: base *= DISEASES[d]["mort"]
    if l["job_type"] == "military": base *= 1.2
    if l["job_type"] == "criminal": base *= 1.4
    return min(0.9, base)

def add_to_life_map(l, text):
    if len(l["life_map"]) < 8: l["life_map"].append(f"{l['age']} лет: {text}")

# ================= СОБЫТИЯ =================
def get_event(l):
    age = l["age"]; c = l["country"]
    if random.random() < 0.45:
        if age < 13:
            return random.choice([
                {"title": "🧸 Детский сад", "text": "Тебя обижает ребенок.", "choices": [{"text": "Дать сдачи", "p": 0.5, "success": "child_fight", "fail": "child_beaten"}, {"text": "Пожаловаться", "p": 0.8, "success": "child_tell", "fail": "child_beaten"}]},
                {"title": "📚 Первая книга", "text": "Тебе подарили книгу.", "choices": [{"text": "Читать", "p": 0.8, "success": "child_smart", "fail": "none"}, {"text": "Гулять", "p": 1, "success": "child_walk", "fail": None}]}
            ])
        elif age < 18:
            return random.choice([
                {"title": "🚬 Сигарета", "text": "Старшеклассники предлагают закурить.", "choices": [{"text": "Попробовать", "p": 0.9, "success": "teen_smoke", "fail": "none"}, {"text": "Отказаться", "p": 1, "success": "teen_healthy", "fail": None}]},
                {"title": "💔 Любовь", "text": "Тебе нравится одноклассник(ца).", "choices": [{"text": "Признаться", "p": 0.4, "success": "teen_love", "fail": "teen_heartbreak"}, {"text": "Скрывать", "p": 1, "success": "none", "fail": None}]}
            ])
        else:
            vvp = c[9]; adult = []
            if l["married"] and l["children"] > 0:
                adult.append({"title": "👶 Кризис", "text": "Денег не хватает.", "choices": [{"text": "Вторую работу", "p": 0.7, "success": "work_extra", "fail": "burnout"}, {"text": "Семью", "p": 1, "success": "family_time", "fail": None}]})
            elif not l["married"] and age < 45:
                adult.append({"title": "💍 Брак", "text": "Партнер предлагает жениться.", "choices": [{"text": "Согласиться", "p": 0.8, "success": "marry", "fail": "none"}, {"text": "Отказаться", "p": 1, "success": "none", "fail": None}]})
            adult.append({"title": "📞 Мошенники", "text": "Звонят из 'банка'.", "choices": [{"text": "Дать код", "p": 1, "success": "scammed", "fail": None}, {"text": "Бросить", "p": 1, "success": "none", "fail": None}]})
            adult.append({"title": "💼 Интриги", "text": "Коллега подставил тебя.", "choices": [{"text": "Скандал", "p": 0.3, "success": "career_fight_win", "fail": "career_fight_fail"}, {"text": "Смириться", "p": 1, "success": "career_grind", "fail": None}]})
            return random.choice(adult)
    if age == 22 and l["job_type"] == "none" and l["faction"] == "Нет":
        vvp = c[9]; civ = int(vvp * (0.8 if l["education"]=="Высшее" else 0.35 if l["education"]=="Среднее" else 0.15))
        return {"title": "Выбор пути", "text": "Пора определяться.",
                "choices": [
                    {"text": f"💼 Гражданка ({fmt_money(civ, c)}/год)", "p": 1, "success": "choose_civilian", "fail": None},
                    {"text": f"👮 Полиция", "p": 1 if l["education"] == "Высшее" else 0, "success": "choose_police", "fail": None},
                    {"text": f"🎖 Армия", "p": 1 if l["education"] in ["Среднее", "Высшее"] else 0, "success": "choose_military", "fail": None},
                    {"text": "💊 Криминал", "p": 1, "success": "choose_criminal", "fail": None}
                ]}
    return None

def next_year(user_id, chat_id):
    p = players.get(user_id); l = p["you"]
    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1
        if l["in_prison"] == 0: return send_scene(chat_id, l, "⛓ <b>Ты вышел на свободу.</b>", kb_year())
        return send_scene(chat_id, l, f"⛓ <b>Тюрьма.</b> Осталось: {l['in_prison']} лет.", kb_year(), scene_type="prison")
    l["age"] += 1; l["last_result"] = None
    rent = sum(int(pr["value"] * 0.05) for pr in l["properties"]); l["clean_cash"] += rent
    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian", "police", "military"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    living = int(l["country"][9] * 0.2 + (500 if l["children"] else 0))
    l["clean_cash"] += (l["salary"] - tax - med - living)
    if l["clean_cash"] < 0: l["debt"] += abs(l["clean_cash"]); l["clean_cash"] = 0

    echo_text = ""
    if l["age"] in [7, 18, 30, 50]:
        n = random.choice(p["neighbors"])
        echo_text = f"\n\n👥 <b>Эхо:</b> Твой ровесник <b>{n['name']}</b> из {n['country'][1]}... "
        echo_text += "умер(ла)." if n["death_age"] < l["age"] else f"жив(а) и {n['fate']}."

    if random.random() < mortality_rate(l): return send_death(user_id, chat_id)
    if l["age"] == 6: return start_exam(user_id, chat_id, 1, "школу")
    elif l["age"] == 12: return start_exam(user_id, chat_id, 2, "колледж")
    elif l["age"] == 18: return start_exam(user_id, chat_id, 3, "университет")
    
    evt = get_event(l)
    if evt: l["current_event"] = evt; send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]))
    else: send_scene(chat_id, l, format_year(l) + echo_text, kb_year())

def send_death(user_id, chat_id, cause=None):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    l["alive"] = False; l["death_age"] = l["age"]; cause = cause or l.get("death_cause", "Болезнь или старость")
    
    life_map_text = "📜 <b>Карта жизни:</b>\n" + "\n".join([f"  • {e}" for e in l["life_map"]]) + "\n\n" if l["life_map"] else ""
    family_text = "👨‍👩‍👧 <b>Семья:</b>\n"
    for sib in l["siblings"]: family_text += f"  • {sib['name']}: {sib['fate']}\n"

    msg = (f"💀 <b>Твоя жизнь оборвалась в {l['age']} лет.</b>\nПричина: {cause}\n\n"
           f"👑 Итог: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}\n"
           f"Деньги: {fmt_money(l['clean_cash'], c)}\n\n{life_map_text}{family_text}\n"
           f"<i>{random.choice(REACTIONS)}</i>")
           
    kb = InlineKeyboardMarkup()
    for i, n in enumerate(p["neighbors"]):
        kb.add(InlineKeyboardButton(f"🎭 Прожить жизнь {n['name']} ({n['country'][1]})", callback_data=f"play_n_{i}"))
    kb.add(InlineKeyboardButton("🎲 Родиться заново", callback_data="new_life"))
    send_scene(chat_id, l, msg, kb, scene_type="hospital")

def start_exam(user_id, chat_id, level, place):
    p = players.get(user_id); l = p["you"]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    school = random.choice(SCHOOLS[l["country"][2]])
    msg = f"📝 <b>Экзамен в {place}!</b>\n{school}\n\nВопрос: <b>{test['q']}</b>"
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode="HTML")

def handle_exam_answer(user_id, chat_id, ans_idx):
    p = players.get(user_id); l = p["you"]; test = l.get("test_data")
    if not test: return
    success = (ans_idx == test["ans"]); l["test_data"] = None
    if success:
        if l["age"] == 6: l["education"] = "Начальное"; add_to_life_map(l, "Пошел в школу")
        elif l["age"] == 12: l["education"] = "Среднее"; add_to_life_map(l, "Окончил среднюю школу")
        elif l["age"] == 18: l["education"] = "Высшее"; add_to_life_map(l, "Поступил в университет")
        msg = "✅ Экзамен сдан!"
    else: msg = "❌ Провал. Учителя разочарованы."
    send_scene(chat_id, l, msg, kb_year())

def apply_outcome(l, outcome):
    vvp = l["country"][9]
    if outcome == "marry": l["married"] = True; add_to_life_map(l, "Женился"); return "Вы поженились!"
    if outcome == "choose_civilian": l["job_type"] = "civilian"; l["job"] = "Работник"; l["salary"] = int(vvp * (0.8 if l["education"]=="Высшее" else 0.35 if l["education"]=="Среднее" else 0.15)); add_to_life_map(l, "Устроился на работу"); return "Ты на гражданке."
    if outcome == "choose_police": l["job_type"] = "police"; l["job"] = "Полицейский"; l["salary"] = int(vvp * 0.6); add_to_life_map(l, "Устроился в полицию"); return "Ты в полиции."
    if outcome == "choose_military": l["job_type"] = "military"; l["job"] = "Военный"; l["salary"] = int(vvp * 0.5); add_to_life_map(l, "Пошел в армию"); return "Ты в армии."
    if outcome == "choose_criminal": l["job_type"] = "criminal"; l["faction"] = "Уличная банда"; l["job"] = "Бандит"; l["dirty_cash"] += 5000; add_to_life_map(l, "Связался с криминалом"); return "Криминал."
    if outcome == "career_fight_win": l["career_xp"] += 40; return "Отстоял место."
    if outcome == "career_fight_fail": l["career_xp"] -= 50; return "Виноват."
    if outcome == "career_grind": l["career_xp"] -= 10; return "Проглотил обиду."
    if outcome == "scammed": loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss; return f"Украли {fmt_money(loss, l['country'])}."
    if outcome == "work_extra": l["clean_cash"] += int(vvp * 0.2); return "Вторая работа."
    if outcome == "burnout": l["diseases"].append("Сердечная недостаточность"); return "Выгорание."
    if outcome == "family_time": return "Время с семьей."
    if outcome == "child_fight": l["clean_cash"] += 100; return "Дал сдачи."
    if outcome == "child_beaten": l["diseases"].append("ПТСР"); return "Травма."
    if outcome == "child_tell": return "Пожаловался."
    if outcome == "child_smart": l["education"] = "Начальное"; return "Стал умнее."
    if outcome == "child_walk": l["clean_cash"] += 50; return "Погулял."
    if outcome == "teen_smoke": l["diseases"].append("Рак легких"); return "Курил."
    if outcome == "teen_healthy": l["clean_cash"] += 200; return "Сэкономил."
    if outcome == "teen_love": return "Любовь."
    if outcome == "teen_heartbreak": l["diseases"].append("ПТСР"); return "Отказ."
    return "Год прошел."

def resolve_choice(user_id, chat_id, i):
    p = players.get(user_id); l = p["you"]; evt = l.get("current_event")
    if not evt: return
    c = evt["choices"][i]; success = random.random() < c["p"]
    outcome = c["success"] if success else c["fail"]
    text = apply_outcome(l, outcome) if outcome else "Год прошел."
    if l["job_type"] in ["civilian", "police", "military"]:
        titles = CAREER_TITLES.get(l["job_type"], {})
        if l["career_xp"] >= 100:
            l["career_xp"] = 0; l["career_rank"] = min(5, l["career_rank"] + 1); l["salary"] = int(l["salary"] * 1.5)
            text += f"\n🎉 <b>ПОВЫШЕНИЕ!</b> Ты теперь {titles.get(l['career_rank'], 'Босс')}."
            add_to_life_map(l, f"Повышение")
    l["last_result"] = {"success": success, "text": text}
    send_scene(chat_id, l, format_year(l), kb_year())

def format_year(l):
    c = l["country"]; parts = [f"<b>Возраст: {l['age']}</b>"]
    if l["last_result"]: parts.append(f"{'✅' if l['last_result']['success'] else '❌'} <i>{l['last_result']['text']}</i>")
    parts.append("")
    parts.append(f"💰 Чистые: <b>{fmt_money(l['clean_cash'], c)}</b>")
    parts.append(f"👑 Класс: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian", "police", "military"]: job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'], '')})"
    parts.append(f"💼 {job}")
    if l["diseases"]: parts.append(f"🩺 Болезни: {', '.join(l['diseases'])}")
    parts.append(f"🎓 Образование: {l['education']}")
    return "\n".join(parts)

def format_event(l, evt): return f"<b>{l['age']} лет · {evt['title']}</b>\n\n{evt['text']}"
def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new_life"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("▶️ Следующий год", callback_data="year")).add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

# ================= МАГАЗИН =================
def open_shop(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    msg = f"🛒 <b>Магазин</b>\nБаланс: {fmt_money(l['clean_cash'], c)}"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 Недвижимость", callback_data="shop_prop")).add(InlineKeyboardButton("🚗 Авто", callback_data="shop_car")).add(InlineKeyboardButton("⬅️ Назад", callback_data="year"))
    bot.send_message(chat_id, msg, reply_markup=kb, parse_mode="HTML")

def shop_prop_menu(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🏠 <b>Недвижимость</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")

def shop_car_menu(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🚗 <b>Авто</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")

def process_buy(user_id, chat_id, cat, name):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    base = PROPERTIES[name] if cat == "prop" else CARS[name]
    if l["clean_cash"] < base: return bot.send_message(chat_id, "❌ Мало денег!", reply_markup=kb_year())
    l["clean_cash"] -= base
    if cat == "prop": l["properties"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    else: l["cars"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    bot.send_message(chat_id, f"🎉 Куплено: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= СТАРТ =================
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    text = "🎲 <b>1 из 8: Эхо</b>\n\nТы — один из 5 детей, родившихся в эту секунду. Сможешь ли ты выжить и оставить след?"
    bot.send_message(msg.chat.id, text, reply_markup=kb_intro(), parse_mode="HTML")

@bot.message_handler(commands=["test"])
def cmd_test(msg):
    test_l = {"in_prison": 0, "diseases": [], "clean_cash": 1000000, "age": 25, "job_type": "civilian", "job": "Тест", "married": False, "gender": "m"}
    try:
        photo = generate_pixel_art(test_l, "rich")
        if photo: bot.send_photo(msg.chat.id, photo, caption="✅ Картинки работают! Pillow установлен.")
        else: bot.send_message(msg.chat.id, "❌ Библиотека Pillow не импортировалась (HAS_PIL = False).")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ Ошибка: {e}")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id; chat_id = call.message.chat.id
    bot.answer_callback_query(call.id); d = call.data

    if d == "new_life":
        l = create_life(); neighbors = generate_neighbors(3)
        players[uid] = {"you": l, "neighbors": neighbors}
        msg = f"👶 <b>Ты родился!</b>\n👤 <b>{l['name']}</b>\n👨‍👩‍👧 Семья: {INCOME_LABELS[l['income']]}\n\n<i>Нажми 'Следующий год'.</i>"
        add_to_life_map(l, "Родился")
        send_scene(chat_id, l, msg, kb_year(), scene_type="child")
    elif d == "year": next_year(uid, chat_id)
    elif d.startswith("choice_"): resolve_choice(uid, chat_id, int(d.split("_")[1]))
    elif d.startswith("ans_"): handle_exam_answer(uid, chat_id, int(d.split("_")[1]))
    elif d == "shop": open_shop(uid, chat_id)
    elif d == "shop_prop": shop_prop_menu(uid, chat_id)
    elif d == "shop_car": shop_car_menu(uid, chat_id)
    elif d.startswith("buy_prop_"): process_buy(uid, chat_id, "prop", d.replace("buy_prop_", ""))
    elif d.startswith("buy_car_"): process_buy(uid, chat_id, "car", d.replace("buy_car_", ""))
    elif d.startswith("play_n_"):
        n_idx = int(d.split("_")[2]); n = players[uid]["neighbors"][n_idx]
        l = create_life(force_country=n["country"], force_income=n["income"])
        l["name"] = n["name"]; players[uid] = {"you": l, "neighbors": generate_neighbors(3)}
        msg = f"🎭 <b>Жизнь соседа!</b>\n👤 <b>{l['name']}</b>\n🌍 {l['country'][1]} {l['country'][0]}\n\n<i>Сможешь изменить судьбу?</i>"
        send_scene(chat_id, l, msg, kb_year(), scene_type="child")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()65, 0.045, 0.40, (0.80,0.18,0.02), 0.26),
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
