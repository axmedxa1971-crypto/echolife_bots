import telebot
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
BOT_TOKEN = "9280691375:AAFKE--UbHjtBr4MBI6sWavaUFwWhXO9arc"
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

# ================= СПРАВОЧНИКИ =================
COUNTRIES = [
    ("Индия", "🇮🇳", "south_asia", 23000, 70, 0.75, 0.35, 2500, 83.5, "₹"),
    ("Пакистан", "🇵🇰", "south_asia", 6000, 66, 0.55, 0.37, 1500, 278.0, "₨"),
    ("Бангладеш", "🇧🇩", "south_asia", 3000, 74, 0.75, 0.40, 2000, 110.0, "৳"),
    ("Непал", "🇳🇵", "south_asia", 550, 70, 0.65, 0.21, 1200, 133.0, "₨"),
    ("Шри-Ланка", "🇱🇰", "south_asia", 320, 77, 0.92, 0.19, 3800, 300.0, "₨"),
    ("Афганистан", "🇦🇫", "south_asia", 1000, 65, 0.40, 0.26, 800, 70.0, "؋"),
    ("Китай", "🇨🇳", "east_asia", 9000, 78, 0.95, 0.65, 12000, 7.2, "¥"),
    ("Япония", "🇯🇵", "east_asia", 800, 84, 0.99, 0.92, 35000, 150.0, "¥"),
    ("Южная Корея", "🇰🇷", "east_asia", 250, 83, 0.98, 0.81, 33000, 1330.0, "₩"),
    ("Монголия", "🇲🇳", "east_asia", 80, 70, 0.90, 0.68, 4500, 3450.0, "₮"),
    ("Индонезия", "🇮🇩", "southeast_asia", 4500, 72, 0.85, 0.57, 4500, 15800.0, "Rp"),
    ("Филиппины", "🇵🇭", "southeast_asia", 2000, 71, 0.85, 0.48, 3500, 56.0, "₱"),
    ("Вьетнам", "🇻🇳", "southeast_asia", 1400, 75, 0.92, 0.40, 4000, 24500.0, "₫"),
    ("Таиланд", "🇹🇭", "southeast_asia", 500, 79, 0.94, 0.53, 7000, 35.0, "฿"),
    ("Малайзия", "🇲🇾", "southeast_asia", 450, 76, 0.94, 0.78, 11000, 4.7, "RM"),
    ("Мьянма", "🇲🇲", "southeast_asia", 850, 66, 0.75, 0.31, 1400, 2100.0, "K"),
    ("Нигерия", "🇳🇬", "africa", 8000, 55, 0.55, 0.52, 2000, 1500.0, "₦"),
    ("ДР Конго", "🇨🇩", "africa", 4000, 60, 0.45, 0.47, 600, 2800.0, "₣"),
    ("Эфиопия", "🇪🇹", "africa", 3800, 67, 0.50, 0.22, 1000, 57.0, "Br"),
    ("Кения", "🇰🇪", "africa", 1400, 66, 0.65, 0.29, 2000, 130.0, "KSh"),
    ("Танзания", "🇹🇿", "africa", 1300, 66, 0.60, 0.36, 1100, 2500.0, "TSh"),
    ("Уганда", "🇺🇬", "africa", 1000, 63, 0.55, 0.26, 900, 3800.0, "USh"),
    ("ЮАР", "🇿🇦", "africa", 900, 64, 0.90, 0.68, 6000, 18.0, "R"),
    ("Ангола", "🇦🇴", "africa", 800, 62, 0.50, 0.67, 2500, 830.0, "Kz"),
    ("Мозамбик", "🇲🇿", "africa", 750, 61, 0.45, 0.38, 500, 63.0, "MT"),
    ("Гана", "🇬🇭", "africa", 550, 64, 0.75, 0.58, 2200, 15.0, "₵"),
    ("Кот-д'Ивуар", "🇨🇮", "africa", 550, 59, 0.55, 0.53, 2300, 620.0, "CFA"),
    ("Камерун", "🇨🇲", "africa", 600, 60, 0.70, 0.59, 1500, 620.0, "FCFA"),
    ("Мадагаскар", "🇲🇬", "africa", 650, 65, 0.60, 0.40, 500, 4400.0, "Ar"),
    ("Мали", "🇲🇱", "africa", 850, 60, 0.35, 0.45, 800, 620.0, "CFA"),
    ("Нигер", "🇳🇪", "africa", 700, 62, 0.30, 0.17, 550, 620.0, "CFA"),
    ("Сенегал", "🇸🇳", "africa", 550, 68, 0.50, 0.49, 1600, 620.0, "CFA"),
    ("Сомали", "🇸🇴", "africa", 450, 56, 0.25, 0.47, 450, 570.0, "Sh"),
    ("Замбия", "🇿🇲", "africa", 500, 62, 0.60, 0.46, 1300, 26.0, "ZK"),
    ("Зимбабве", "🇿🇼", "africa", 400, 62, 0.80, 0.32, 1200, 360.0, "Z$"),
    ("Руанда", "🇷🇼", "africa", 350, 67, 0.65, 0.18, 800, 1300.0, "RF"),
    ("Египет", "🇪🇬", "arab", 1900, 72, 0.80, 0.43, 4000, 48.0, "E£"),
    ("Алжир", "🇩🇿", "arab", 800, 77, 0.85, 0.75, 4500, 135.0, "DA"),
    ("Марокко", "🇲🇦", "arab", 500, 74, 0.75, 0.65, 3500, 10.0, "DH"),
    ("Тунис", "🇹🇳", "arab", 170, 77, 0.85, 0.70, 4000, 3.1, "DT"),
    ("Ливия", "🇱🇾", "arab", 120, 73, 0.85, 0.81, 6500, 4.8, "LD"),
    ("Судан", "🇸🇩", "arab", 1100, 66, 0.55, 0.36, 700, 600.0, "SDG"),
    ("Ирак", "🇮🇶", "arab", 900, 71, 0.75, 0.71, 4500, 1310.0, "IQD"),
    ("Сирия", "🇸🇾", "arab", 500, 73, 0.75, 0.57, 1200, 13000.0, "S£"),
    ("Йемен", "🇾🇪", "arab", 700, 66, 0.55, 0.39, 800, 250.0, "YR"),
    ("Саудовская Аравия", "🇸🇦", "arab", 550, 76, 0.95, 0.84, 25000, 3.75, "SR"),
    ("Иордания", "🇯🇴", "arab", 200, 75, 0.92, 0.92, 4500, 0.71, "JD"),
    ("Ливан", "🇱🇧", "arab", 80, 79, 0.92, 0.89, 4500, 15000.0, "L£"),
    ("ОАЭ", "🇦🇪", "arab", 100, 78, 0.95, 0.87, 45000, 3.67, "DH"),
    ("Бразилия", "🇧🇷", "latam", 2600, 76, 0.90, 0.87, 8000, 5.1, "R$"),
    ("Мексика", "🇲🇽", "latam", 1800, 75, 0.88, 0.81, 9000, 17.0, "MX$"),
    ("Колумбия", "🇨🇴", "latam", 650, 77, 0.88, 0.82, 6000, 3900.0, "C$"),
    ("Аргентина", "🇦🇷", "latam", 500, 77, 0.94, 0.92, 12000, 350.0, "AR$"),
    ("Перу", "🇵🇪", "latam", 550, 77, 0.88, 0.78, 6500, 3.8, "S/"),
    ("Венесуэла", "🇻🇪", "latam", 450, 72, 0.92, 0.88, 3500, 36.0, "Bs"),
    ("Чили", "🇨🇱", "latam", 200, 80, 0.95, 0.88, 15000, 950.0, "CL$"),
    ("Эквадор", "🇪🇨", "latam", 300, 77, 0.88, 0.64, 6000, 1.0, "$"),
    ("Боливия", "🇧🇴", "latam", 250, 72, 0.85, 0.70, 3500, 6.9, "Bs"),
    ("Уругвай", "🇺🇾", "latam", 45, 78, 0.96, 0.96, 17000, 39.0, "U$"),
    ("Куба", "🇨🇺", "latam", 120, 79, 0.99, 0.77, 9000, 24.0, "CUP"),
    ("Гватемала", "🇬🇹", "latam", 350, 74, 0.75, 0.52, 4500, 7.8, "Q"),
    ("Гаити", "🇭🇹", "latam", 250, 64, 0.60, 0.57, 1700, 130.0, "G"),
    ("Германия", "🇩🇪", "europe", 800, 81, 0.98, 0.78, 45000, 0.92, "€"),
    ("Франция", "🇫🇷", "europe", 700, 82, 0.98, 0.81, 42000, 0.92, "€"),
    ("Великобритания", "🇬🇧", "europe", 700, 81, 0.98, 0.84, 46000, 0.79, "£"),
    ("Италия", "🇮🇹", "europe", 400, 83, 0.98, 0.71, 34000, 0.92, "€"),
    ("Испания", "🇪🇸", "europe", 350, 83, 0.98, 0.81, 30000, 0.92, "€"),
    ("Польша", "🇵🇱", "europe", 350, 78, 0.98, 0.60, 18000, 4.0, "zł"),
    ("Нидерланды", "🇳🇱", "europe", 170, 82, 0.98, 0.92, 55000, 0.92, "€"),
    ("Бельгия", "🇧🇪", "europe", 115, 82, 0.98, 0.98, 50000, 0.92, "€"),
    ("Швеция", "🇸🇪", "europe", 110, 83, 0.98, 0.88, 55000, 10.5, "kr"),
    ("Швейцария", "🇨🇭", "europe", 85, 84, 0.98, 0.74, 85000, 0.88, "CHF"),
    ("Норвегия", "🇳🇴", "europe", 55, 83, 0.98, 0.83, 80000, 10.5, "kr"),
    ("Португалия", "🇵🇹", "europe", 85, 82, 0.98, 0.66, 25000, 0.92, "€"),
    ("Греция", "🇬🇷", "europe", 85, 82, 0.98, 0.80, 20000, 0.92, "€"),
    ("Австрия", "🇦🇹", "europe", 85, 82, 0.98, 0.59, 50000, 0.92, "€"),
    ("Россия", "🇷🇺", "post_soviet", 1300, 73, 0.98, 0.75, 10000, 92.0, "₽"),
    ("Узбекистан", "🇺🇿", "post_soviet", 700, 72, 0.90, 0.50, 2500, 12600.0, "so'm"),
    ("Казахстан", "🇰🇿", "post_soviet", 400, 74, 0.95, 0.58, 10000, 450.0, "₸"),
    ("Украина", "🇺🇦", "post_soviet", 300, 72, 0.98, 0.70, 4000, 37.0, "₴"),
    ("Азербайджан", "🇦🇿", "post_soviet", 130, 74, 0.90, 0.57, 5500, 1.7, "₼"),
    ("Беларусь", "🇧🇾", "post_soviet", 100, 74, 0.98, 0.79, 7000, 3.3, "Br"),
    ("США", "🇺🇸", "developed", 3600, 79, 0.95, 0.83, 55000, 1.0, "$"),
    ("Канада", "🇨🇦", "developed", 380, 82, 0.98, 0.82, 50000, 1.36, "C$"),
    ("Австралия", "🇦🇺", "developed", 300, 83, 0.98, 0.86, 55000, 1.5, "A$"),
    ("Израиль", "🇮🇱", "developed", 180, 83, 0.95, 0.93, 45000, 3.7, "₪"),
    ("Сингапур", "🇸🇬", "developed", 40, 84, 0.98, 1.00, 65000, 1.35, "S$"),
    ("Катар", "🇶🇦", "developed", 30, 80, 0.95, 0.99, 60000, 3.64, "QR"),
    ("Новая Зеландия", "🇳🇿", "developed", 60, 82, 0.98, 0.86, 42000, 1.6, "NZ$"),
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

DISEASES = {
    "Астма": {"desc": "Хроническое воспаление дыхательных путей.", "mort": 1.1, "cash": 300, "fert": 0},
    "Диабет 1 типа": {"desc": "Инсулинозависимый диабет.", "mort": 1.4, "cash": 1500, "fert": -15},
    "Диабет 2 типа": {"desc": "Нарушение обмена веществ.", "mort": 1.2, "cash": 800, "fert": -10},
    "Гипертония": {"desc": "Повышенное давление. Риск инфаркта.", "mort": 1.3, "cash": 400, "fert": 0},
    "Артрит": {"desc": "Воспаление суставов.", "mort": 1.15, "cash": 500, "fert": 0},
    "Псориаз": {"desc": "Кожное заболевание.", "mort": 1.05, "cash": 300, "fert": 0},
    "Эпилепсия": {"desc": "Судорожные приступы.", "mort": 1.5, "cash": 600, "fert": -10},
    "Мигрень": {"desc": "Сильные головные боли.", "mort": 1.05, "cash": 200, "fert": 0},
    "Туберкулез": {"desc": "Инфекция легких.", "mort": 1.8, "cash": 1500, "fert": -20},
    "Сифилис": {"desc": "Венерическое заболевание.", "mort": 1.3, "cash": 500, "fert": -50},
    "Гонорея": {"desc": "Венерическое заболевание.", "mort": 1.1, "cash": 400, "fert": -30},
    "ВИЧ/СПИД": {"desc": "Вирус иммунодефицита.", "mort": 1.5, "cash": 2000, "fert": -30},
    "Гепатит B": {"desc": "Вирусное поражение печени.", "mort": 1.5, "cash": 1200, "fert": -15},
    "Гепатит C": {"desc": "Хроническое поражение печени.", "mort": 1.6, "cash": 2500, "fert": -20},
    "Холера": {"desc": "Острая кишечная инфекция.", "mort": 2.5, "cash": 800, "fert": 0},
    "Тиф": {"desc": "Инфекция через воду.", "mort": 1.8, "cash": 600, "fert": 0},
    "Корь": {"desc": "Острая вирусная инфекция.", "mort": 1.6, "cash": 400, "fert": 0},
    "Ковид-19": {"desc": "Респираторная инфекция.", "mort": 1.4, "cash": 1000, "fert": 0},
    "Малярия": {"desc": "Передается через комаров.", "mort": 2.0, "cash": 600, "fert": -10},
    "Рак легких": {"desc": "Опухоль легких.", "mort": 3.0, "cash": 5000, "fert": -100},
    "Рак груди": {"desc": "Опухоль молочной железы.", "mort": 2.2, "cash": 4000, "fert": -100},
    "Лейкемия": {"desc": "Рак крови.", "mort": 2.8, "cash": 8000, "fert": -100},
    "ПТСР": {"desc": "Посттравматическое расстройство.", "mort": 1.4, "cash": 500, "fert": 0},
    "Депрессия": {"desc": "Стойкое снижение настроения.", "mort": 1.3, "cash": 400, "fert": 0},
    "Биполярное расстройство": {"desc": "Резкие перепады настроения.", "mort": 1.3, "cash": 700, "fert": -5},
    "Шизофрения": {"desc": "Психическое расстройство.", "mort": 1.4, "cash": 800, "fert": -10},
    "Алкоголизм": {"desc": "Зависимость от алкоголя.", "mort": 1.8, "cash": 600, "fert": -20},
    "Наркомания": {"desc": "Зависимость от наркотиков.", "mort": 2.0, "cash": 1500, "fert": -30},
    "Сердечная недостаточность": {"desc": "Сердце не справляется.", "mort": 2.2, "cash": 1500, "fert": 0},
    "Инфаркт": {"desc": "Омертвение участка сердца.", "mort": 2.5, "cash": 3000, "fert": 0},
    "Инсульт": {"desc": "Нарушение кровоснабжения мозга.", "mort": 2.5, "cash": 3000, "fert": -20},
    "Цирроз печени": {"desc": "Печень разрушена.", "mort": 2.2, "cash": 1000, "fert": -20},
    "Полиомиелит": {"desc": "Паралич.", "mort": 1.5, "cash": 500, "fert": -30},
    "Ожирение": {"desc": "Избыточный вес.", "mort": 1.3, "cash": 400, "fert": -10},
    "Анемия": {"desc": "Малокровие.", "mort": 1.1, "cash": 200, "fert": -5},
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

ORGS = {
    "Уличная банда": "Мелкие хулиганы. Грязные деньги.",
    "Синдикат 'Черная Роза'": "Мафия. Кодекс чести, контрабанда.",
    "Картель 'Сьерра'": "Наркокартель. Деньги и война.",
    "Братство Дракона": "Триада. Теневые схемы.",
    "Цифровой Синдикат": "Хакеры. Кража крипты.",
    "Орден Пустыни": "Террористы. Смертники.",
    "Красный Молот": "Экстремисты. Саботаж.",
    "Эко-Фронт": "Радикалы-экологи. Поджоги.",
    "Полиция": "Стражи порядка. Риск и коррупция.",
    "Армия": "Вооруженные силы. Дисциплина и риск.",
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
    1: [{"q": "5 + 7?", "opts": ["10", "12", "13"], "ans": 1},{"q": "Сколько цветов у радуги?", "opts": ["5", "7", "9"], "ans": 1},{"q": "Сколько дней в неделе?", "opts": ["5", "7", "10"], "ans": 1}],
    2: [{"q": "x - 4 = 10, x?", "opts": ["6", "14", "40"], "ans": 1},{"q": "Столица Франции?", "opts": ["Лондон", "Париж", "Берлин"], "ans": 1},{"q": "Корень из 144?", "opts": ["10", "12", "14"], "ans": 1}],
    3: [{"q": "Столица Австралии?", "opts": ["Сидней", "Мельбурн", "Канберра"], "ans": 2},{"q": "Производная x^2?", "opts": ["x", "2x", "x^3/3"], "ans": 1},{"q": "log(100) по осн 10?", "opts": ["1", "2", "10"], "ans": 1}],
}

PROPERTIES = {"Общага": 3000, "Квартира": 30000, "Дом": 200000, "Особняк": 1500000, "Остров": 50000000}
CARS = {"Скутер": 800, "Седан": 15000, "Внедорожник": 40000, "Спорткар": 200000, "Гиперкар": 2000000}
BUSINESSES = {"Ларёк": 5000, "Кофейня": 25000, "Ресторан": 150000, "Завод": 2000000, "Корпорация": 10000000}

CAREER_TITLES = {
    "civilian": {1: "Стажер", 2: "Специалист", 3: "Старший специалист", 4: "Менеджер", 5: "Директор"},
    "police": {1: "Курсант", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Полковник"},
    "military": {1: "Рядовой", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Генерал"},
    "criminal": {1: "Шестерка", 2: "Боец", 3: "Бригадир", 4: "Авторитет", 5: "Босс"},
}

INCOME_LABELS = ["Бедная семья", "Средний класс", "Богатая семья"]
REACTIONS = ["🎲 Судьба сегодня была не в духе.", "🌧 Иногда кубик просто падает не туда.", "🕯 Мир несправедлив. Но ты был здесь.", "✨ Ты прожил жизнь. Это уже немало.", "💀 Смерть — единственное, что гарантировано."]

players = {}

# ================= ГРАФИКА =================
def generate_pixel_art(l, scene_type="life"):
    if not HAS_PIL: return None
    w, h = 128, 64
    img = Image.new('RGB', (w, h), color='#0f172a')
    d = ImageDraw.Draw(img)
    
    if scene_type == "rich" or (l and l.get("clean_cash", 0) > 500000):
        d.rectangle([0, 0, w, 40], fill='#fca5a5')
        d.ellipse([90, 10, 110, 30], fill='#fbbf24')
        d.polygon([(0, 40), (30, 20), (60, 40)], fill='#f87171')
    elif scene_type == "prison" or (l and l["in_prison"] > 0):
        d.rectangle([0, 0, w, h], fill='#374151')
    elif scene_type == "hospital" or (l and l["diseases"]):
        d.rectangle([0, 0, w, h], fill='#e5e7eb')
        d.rectangle([50, 20, 70, 30], fill='#ef4444')
        d.rectangle([60, 10, 62, 40], fill='#ef4444')
    elif scene_type == "child" or (l and l["age"] < 13):
        d.rectangle([0, 0, w, 40], fill='#93c5fd')
        d.ellipse([100, 5, 120, 25], fill='#fde047')
        d.ellipse([10, 10, 20, 15], fill='#ffffff')
        d.ellipse([15, 8, 25, 15], fill='#ffffff')
        d.polygon([(0, 40), (40, 25), (80, 40)], fill='#60a5fa')
    else:
        d.rectangle([0, 0, w, 40], fill='#1e3a8a')
        d.ellipse([100, 5, 115, 20], fill='#fef08a')
        for x in range(10, 100, 20):
            d.point((x, 10), fill='#ffffff')
            d.point((x+5, 15), fill='#ffffff')

    if scene_type == "office": d.rectangle([0, 40, w, h], fill='#6b7280')
    elif scene_type == "rich": d.rectangle([0, 40, w, h], fill='#22c55e')
    else: d.rectangle([0, 40, w, h], fill='#475569')

    if scene_type == "rich":
        d.rectangle([40, 15, 90, 50], fill='#f3f4f6')
        d.polygon([(30, 15), (65, 0), (100, 15)], fill='#b91c1c')
        d.rectangle([60, 35, 70, 50], fill='#78350f')
        d.rectangle([45, 25, 55, 35], fill='#fef08a')
        d.rectangle([75, 25, 85, 35], fill='#fef08a')
    elif scene_type == "child":
        d.rectangle([40, 20, 70, 50], fill='#d97706')
        d.polygon([(35, 20), (55, 5), (75, 20)], fill='#991b1b')
        d.rectangle([50, 35, 60, 50], fill='#451a03')
    elif scene_type == "office":
        d.rectangle([20, 20, 100, 50], fill='#9ca3af')
        d.rectangle([30, 25, 50, 40], fill='#3b82f6')
        d.rectangle([60, 25, 80, 40], fill='#3b82f6')

    def draw_person(x, y, color_body, color_head='#fcd34d'):
        d.rectangle([x, y, x+6, y+12], fill=color_body)
        d.rectangle([x+1, y-6, x+5, y], fill=color_head)
        d.rectangle([x+1, y+12, x+2, y+16], fill='#1f2937')
        d.rectangle([x+4, y+12, x+5, y+16], fill='#1f2937')
        d.point((x+2, y-4), fill='#000000')
        d.point((x+4, y-4), fill='#000000')

    if scene_type == "rich":
        draw_person(65, 34, '#fbbf24'); draw_person(80, 34, '#e5e7eb'); draw_person(75, 40, '#93c5fd')
    elif scene_type == "office":
        draw_person(40, 34, '#3b82f6')
    elif scene_type == "child":
        draw_person(55, 34, '#3b82f6' if l and l["gender"]=="m" else '#ec4899')
        draw_person(35, 34, '#6b7280'); draw_person(75, 34, '#6b7280')
    elif scene_type == "hospital":
        d.rectangle([50, 35, 78, 50], fill='#ffffff', outline='#9ca3af')
        draw_person(60, 26, '#9ca3af')
    elif scene_type == "prison":
        draw_person(60, 34, '#212121')
    else:
        draw_person(60, 34, '#3b82f6' if l and l["gender"]=="m" else '#ec4899')

    img = img.resize((w*4, h*4), resample=Image.NEAREST)
    bio = io.BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def send_scene(chat_id, l, text, kb, scene_type=None):
    if not scene_type:
        if l and l["in_prison"] > 0: scene_type = "prison"
        elif l and l["diseases"]: scene_type = "hospital"
        elif l and l.get("clean_cash", 0) > 500000: scene_type = "rich"
        elif l and l["age"] < 13: scene_type = "child"
        elif l and l["job_type"] in ["civilian", "police", "military"] and l["job"] != "Безработный": scene_type = "office"
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
    rate = country[8]; symbol = country[9]
    return f"{int(amount_usd * rate):,} {symbol}".replace(",", " ")

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

def get_faction_status(l):
    if l["in_prison"] > 0: return f"⛓ Заключенный ({l['in_prison']} лет)"
    if l["faction"] != "Нет": return f"🕶 {l['faction']}"
    return "👤 Законопослушный"

def weighted_country():
    r = random.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def get_ethnicity(region):
    r = random.random() * 100; cum = 0
    for name, chance, prejudice in ETHNICITIES.get(region, [("Местный", 100, None)]):
        cum += chance
        if r <= cum: return name, prejudice
    return "Местный", None

def generate_neighbors(count=3):
    neighbors = []
    for _ in range(count):
        c = weighted_country(); g = random.choice(["m", "f"])
        name = random.choice(NAMES[c[2]][g])
        death_age = int(random.gauss(c[4], 12))
        if death_age < 1: death_age = random.randint(1, 5)
        fate_roll = random.random()
        if fate_roll < 0.1: fate = "умер(ла) в младенчестве"
        elif fate_roll < 0.2: fate = "стал(а) богатым бизнесменом"
        elif fate_roll < 0.3: fate = "погиб(ла) в криминальной разборке"
        elif fate_roll < 0.4: fate = "получил(а) высшее образование"
        elif fate_roll < 0.6: fate = "живет скромно, работает на заводе"
        else: fate = "обычная жизнь"
        neighbors.append({"name": name, "country": c, "gender": g, "death_age": death_age, "fate": fate})
    return neighbors

def create_life(force_country=None):
    country = force_country if force_country else weighted_country()
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    ethnicity, prejudice = get_ethnicity(country[2])
    start_cash = int(country[7] * random.uniform(0.1, 2.0))
    siblings = []
    for _ in range(random.randint(0, 4)):
        s_g = random.choice(["m", "f"])
        siblings.append({"name": random.choice(NAMES[country[2]][s_g]), "gender": s_g, "fate": "Жив(а)"})
    return {
        "country": country, "gender": gender, "name": name, "ethnicity": ethnicity, "prejudice": prejudice,
        "clean_cash": start_cash, "dirty_cash": 0, "in_prison": 0, "age": 0, "alive": True, "faction": "Нет",
        "education": "Нет", "job": "Безработный", "salary": 0, "job_type": "none", "career_xp": 0, "career_rank": 1,
        "married": False, "children": 0, "diseases": [], "properties": [], "cars": [], "businesses": [], "debt": 0,
        "life_map": [], "siblings": siblings, "test_data": None, "asked_tests": {1: [], 2: [], 3: []}, "current_event": None
    }

def add_to_life_map(l, text):
    if len(l["life_map"]) < 10: l["life_map"].append(f"{l['age']} лет: {text}")

def mortality_rate(l):
    base = 0.05 if l["age"] < 5 else 0.003
    if l["age"] > 60: base = 0.02
    if l["age"] > 80: base = 0.1
    if l["in_prison"] > 0: base *= 1.5
    if l["debt"] > 0: base *= 1.3
    for d in l["diseases"]: base *= DISEASES[d]["mort"]
    if l["job_type"] == "military": base *= 1.2
    if l["job_type"] == "criminal": base *= 1.4
    return min(0.9, base)

# ================= СОБЫТИЯ =================
def get_event(l):
    age = l["age"]; c = l["country"]
    if random.random() < 0.45:
        if age < 13:
            return random.choice([
                {"title": "🧸 Детский сад", "text": "Тебя обижает ребенок.", "choices": [{"text": "Дать сдачи", "p": 0.5, "success": "child_fight"}, {"text": "Пожаловаться", "p": 0.8, "success": "child_tell"}]},
                {"title": "📚 Первая книга", "text": "Тебе подарили книгу.", "choices": [{"text": "Читать", "p": 0.8, "success": "child_smart"}, {"text": "Гулять", "p": 1, "success": "child_walk"}]}
            ])
        elif age < 18:
            return random.choice([
                {"title": "🚬 Сигарета", "text": "Старшеклассники предлагают закурить.", "choices": [{"text": "Попробовать", "p": 0.9, "success": "teen_smoke"}, {"text": "Отказаться", "p": 1, "success": "teen_healthy"}]},
                {"title": "💔 Любовь", "text": "Тебе нравится одноклассник(ца).", "choices": [{"text": "Признаться", "p": 0.4, "success": "teen_love"}, {"text": "Скрывать", "p": 1, "success": "none"}]}
            ])
        else:
            vvp = c[7]; adult = []
            if l["married"] and l["children"] > 0:
                adult.append({"title": "👶 Кризис", "text": "Денег не хватает.", "choices": [{"text": "Вторую работу", "p": 0.7, "success": "work_extra"}, {"text": "Семью", "p": 1, "success": "family_time"}]})
            elif not l["married"] and age < 45:
                adult.append({"title": "💍 Брак", "text": "Партнер предлагает жениться.", "choices": [{"text": "Согласиться", "p": 0.8, "success": "marry"}, {"text": "Отказаться", "p": 1, "success": "none"}]})
            elif l["married"]:
                adult.append({"title": "💔 Развод", "text": "Супруг подает на развод.", "choices": [{"text": "Смириться", "p": 1, "success": "divorce"}]})
            adult.append({"title": "📞 Мошенники", "text": "Звонят из 'банка'.", "choices": [{"text": "Дать код", "p": 1, "success": "scammed"}, {"text": "Бросить", "p": 1, "success": "none"}]})
            adult.append({"title": "💼 Интриги", "text": "Коллега подставил тебя.", "choices": [{"text": "Скандал", "p": 0.3, "success": "career_fight_win"}, {"text": "Смириться", "p": 1, "success": "career_grind"}]})
            return random.choice(adult)
    if age == 22 and l["job_type"] == "none" and l["faction"] == "Нет":
        vvp = c[7]
        return {"title": "Выбор пути", "text": "Пора определяться.",
                "choices": [
                    {"text": "💼 Гражданка", "p": 1, "success": "job_civ"},
                    {"text": "👮 Полиция", "p": 1 if l["education"] == "Высшее" else 0, "success": "job_pol"},
                    {"text": "🎖 Армия", "p": 1 if l["education"] in ["Среднее", "Высшее"] else 0, "success": "job_mil"},
                    {"text": "💊 Криминал", "p": 1, "success": "job_crim"}
                ]}
    return None

def next_year(user_id, chat_id):
    p = players.get(user_id); l = p["you"]
    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1
        if l["in_prison"] == 0: return send_scene(chat_id, l, "⛓ <b>Ты вышел на свободу.</b>", kb_year())
        return send_scene(chat_id, l, f"⛓ <b>Тюрьма.</b> Осталось: {l['in_prison']} лет.", kb_year(), "prison")
    
    l["age"] += 1
    rent = sum(int(pr["value"] * 0.05) for pr in l["properties"])
    biz = sum(int(b["value"] * 0.15) for b in l["businesses"])
    l["clean_cash"] += rent + biz
    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian", "police", "military"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    living = int(l["country"][7] * 0.2 + (500 if l["children"] else 0))
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
    if evt: 
        l["current_event"] = evt
        send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]))
    else: 
        send_scene(chat_id, l, format_year(l) + echo_text, kb_year())

def send_death(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    map_text = "📜 <b>Карта жизни:</b>\n" + "\n".join([f"• {e}" for e in l["life_map"]]) if l["life_map"] else ""
    msg = (f"💀 <b>Ты умер в {l['age']} лет.</b>\nИтог: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}\nДеньги: {fmt_money(l['clean_cash'], c)}\n\n{map_text}\n\n👥 <b>Соседи:</b>\n")
    kb = InlineKeyboardMarkup()
    for i, n in enumerate(p["neighbors"]):
        msg += f"• {n['name']} ({n['country'][1]}): умер в {n['death_age']} ({n['fate']})\n"
        kb.add(InlineKeyboardButton(f"🎭 Прожить жизнь {n['name']}", callback_data=f"play_{i}"))
    kb.add(InlineKeyboardButton("🎲 Начать заново", callback_data="new"))
    send_scene(chat_id, l, msg, kb, "hospital")

def start_exam(user_id, chat_id, level, place):
    p = players.get(user_id); l = p["you"]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    school = random.choice(SCHOOLS[l["country"][2]])
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    bot.send_message(chat_id, f"📝 <b>Экзамен в {place}!</b>\n{school}\n\nВопрос: <b>{test['q']}</b>", reply_markup=kb, parse_mode="HTML")

def handle_exam_answer(user_id, chat_id, ans_idx):
    p = players.get(user_id); l = p["you"]; test = l.get("test_data")
    if not test: return
    success = (ans_idx == test["ans"]); l["test_data"] = None
    if success:
        if l["age"] == 6: l["education"] = "Начальное"; add_to_life_map(l, "Пошел в школу")
        elif l["age"] == 12: l["education"] = "Среднее"; add_to_life_map(l, "Окончил школу")
        elif l["age"] == 18: l["education"] = "Высшее"; add_to_life_map(l, "Поступил в вуз")
        msg = "✅ Экзамен сдан!"
    else: msg = "❌ Провал."
    send_scene(chat_id, l, msg, kb_year())

def apply_outcome(l, outcome):
    vvp = l["country"][7]
    if outcome == "marry": l["married"] = True; add_to_life_map(l, "Женился"); return "Вы поженились!"
    if outcome == "divorce": l["married"] = False; l["clean_cash"] = int(l["clean_cash"] / 2); return "Развод."
    if outcome == "job_civ": l["job_type"] = "civilian"; l["job"] = "Работник"; l["salary"] = int(vvp * 0.6); add_to_life_map(l, "На работу"); return "Ты на гражданке."
    if outcome == "job_pol": l["job_type"] = "police"; l["faction"] = "Полиция"; l["job"] = "Полицейский"; l["salary"] = int(vvp * 0.5); add_to_life_map(l, "В полиции"); return "Ты в полиции."
    if outcome == "job_mil": l["job_type"] = "military"; l["faction"] = "Армия"; l["job"] = "Военный"; l["salary"] = int(vvp * 0.4); add_to_life_map(l, "В армии"); return "Ты в армии."
    if outcome == "job_crim": l["job_type"] = "criminal"; l["faction"] = "Уличная банда"; l["job"] = "Бандит"; l["dirty_cash"] += 5000; add_to_life_map(l, "Криминал"); return "Криминал."
    if outcome == "scammed": loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss; return f"Украли {fmt_money(loss, l['country'])}."
    if outcome == "child_fight": l["clean_cash"] += 100; return "Дал сдачи."
    if outcome == "child_tell": return "Пожаловался."
    if outcome == "teen_smoke": l["diseases"].append("Рак легких"); return "Курил."
    if outcome == "teen_healthy": l["clean_cash"] += 200; return "Сэкономил."
    return "Год прошел."

def resolve_choice(user_id, chat_id, i):
    p = players.get(user_id); l = p["you"]; evt = l.get("current_event")
    if not evt: return
    c = evt["choices"][i]; success = random.random() < c["p"]
    outcome = c["success"] if success else c["fail"]
    text = apply_outcome(l, outcome) if outcome else "Год прошел."
    l["last_result"] = {"success": success, "text": text}
    send_scene(chat_id, l, format_year(l), kb_year())

def format_year(l):
    c = l["country"]; parts = [f"<b>Возраст: {l['age']}</b>"]
    if l.get("last_result"): parts.append(f"{'✅' if l['last_result']['success'] else '❌'} <i>{l['last_result']['text']}</i>")
    parts.append(f"\n💰 Баланс: <b>{fmt_money(l['clean_cash'], c)}</b>")
    parts.append(f"👑 Класс: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian", "police", "military"]: job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'], '')})"
    parts.append(f"💼 {job}")
    if l["diseases"]: parts.append(f"🩺 {', '.join(l['diseases'])}")
    parts.append(f"🎓 {l['education']}")
    return "\n".join(parts)

def format_event(l, evt): return f"<b>{l['age']} лет · {evt['title']}</b>\n\n{evt['text']}"
def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("▶️ Следующий год", callback_data="year")).add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

# ================= МАГАЗИН =================
def open_shop(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 Недвижимость", callback_data="shop_prop")).add(InlineKeyboardButton("🚗 Авто", callback_data="shop_car")).add(InlineKeyboardButton("🏢 Бизнесы", callback_data="shop_biz")).add(InlineKeyboardButton("⬅️ Назад", callback_data="year"))
    bot.send_message(chat_id, f"🛒 <b>Магазин</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")

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

def shop_biz_menu(user_id, chat_id):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items(): kb.add(InlineKeyboardButton(f"🏢 {name} — {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🏢 <b>Бизнесы</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")

def process_buy(user_id, chat_id, cat, name):
    p = players.get(user_id); l = p["you"]; c = l["country"]
    if cat == "prop": base = PROPERTIES[name]
    elif cat == "car": base = CARS[name]
    else: base = BUSINESSES[name]
    if l["clean_cash"] < base: return bot.send_message(chat_id, "❌ Мало денег!", reply_markup=kb_year())
    l["clean_cash"] -= base
    if cat == "prop": l["properties"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    elif cat == "car": l["cars"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    else: l["businesses"].append({"type": name, "value": base}); add_to_life_map(l, f"Открыл {name}")
    bot.send_message(chat_id, f"🎉 Куплено: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= ХЭНДЛЕРЫ =================
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    text = "🎲 <b>1 из 8: Эхо</b>\n\nТы — один из 5 детей, родившихся в эту секунду. Сможешь ли ты выжить и оставить след?"
    bot.send_message(msg.chat.id, text, reply_markup=kb_intro(), parse_mode="HTML")

@bot.message_handler(commands=["test"])
def cmd_test(msg):
    test_l = {"in_prison": 0, "diseases": [], "clean_cash": 1000000, "age": 25, "job_type": "civilian", "job": "Тест", "married": False, "gender": "m"}
    photo = generate_pixel_art(test_l, "rich")
    if photo: bot.send_photo(msg.chat.id, photo, caption="✅ Графика работает!")
    else: bot.send_message(msg.chat.id, "❌ Pillow не установлен.")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id; chat_id = call.message.chat.id
    bot.answer_callback_query(call.id); d = call.data

    if d == "new":
        l = create_life(); neighbors = generate_neighbors()
        players[uid] = {"you": l, "neighbors": neighbors}
        add_to_life_map(l, "Родился")
        msg = f"👶 <b>Ты родился!</b>\n👤 {l['name']} ({l['country'][1]} {l['country'][0]})\n👨‍👩‍👧 {INCOME_LABELS[random.randint(0,2)]}\n\n<i>Нажми 'Следующий год'.</i>"
        send_scene(chat_id, l, msg, kb_year(), "child")
    elif d == "year": next_year(uid, chat_id)
    elif d.startswith("job_"): 
        text = apply_outcome(players[uid]["you"], d)
        send_scene(chat_id, players[uid]["you"], text, kb_year())
    elif d.startswith("choice_"): resolve_choice(uid, chat_id, int(d.split("_")[1]))
    elif d.startswith("ans_"): handle_exam_answer(uid, chat_id, int(d.split("_")[1]))
    elif d == "shop": open_shop(uid, chat_id)
    elif d == "shop_prop": shop_prop_menu(uid, chat_id)
    elif d == "shop_car": shop_car_menu(uid, chat_id)
    elif d == "shop_biz": shop_biz_menu(uid, chat_id)
    elif d.startswith("buy_prop_"): process_buy(uid, chat_id, "prop", d.replace("buy_prop_", ""))
    elif d.startswith("buy_car_"): process_buy(uid, chat_id, "car", d.replace("buy_car_", ""))
    elif d.startswith("buy_biz_"): process_buy(uid, chat_id, "biz", d.replace("buy_biz_", ""))
    elif d.startswith("play_"):
        idx = int(d.split("_")[1]); n = players[uid]["neighbors"][idx]
        l = create_life(force_country=n["country"]); l["name"] = n["name"]
        players[uid] = {"you": l, "neighbors": generate_neighbors()}
        add_to_life_map(l, "Родился (смена судьбы)")
        msg = f"🎭 <b>Новая судьба!</b>\nТы теперь {l['name']} ({l['country'][1]})."
        send_scene(chat_id, l, msg, kb_year(), "child")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
