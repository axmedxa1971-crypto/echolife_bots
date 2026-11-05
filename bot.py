import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, json, os, time

# ================= НАСТРОЙКА =================
BOT_TOKEN = "9280691375:AAFKE--UbHjtBr4MBI6sWavaUFwWhXO9arc"
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ================= БАЗА ДАННЫХ =================
DB_FILE = "players.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
    except: pass

players_db = load_db()

# ================= СПРАВОЧНИКИ =================
COUNTRIES = [
    ("Индия", "🇮🇳", "south_asia", 23000, 70, 0.75, 0.35, 2500, 83.5, "₹"),("Пакистан", "🇵🇰", "south_asia", 6000, 66, 0.55, 0.37, 1500, 278.0, "₨"),("Бангладеш", "🇧🇩", "south_asia", 3000, 74, 0.75, 0.40, 2000, 110.0, "৳"),("Непал", "🇳🇵", "south_asia", 550, 70, 0.65, 0.21, 1200, 133.0, "₨"),("Шри-Ланка", "🇱🇰", "south_asia", 320, 77, 0.92, 0.19, 3800, 300.0, "₨"),("Афганистан", "🇦🇫", "south_asia", 1000, 65, 0.40, 0.26, 800, 70.0, "؋"),
    ("Китай", "🇨🇳", "east_asia", 9000, 78, 0.95, 0.65, 12000, 7.2, "¥"),("Япония", "🇯🇵", "east_asia", 800, 84, 0.99, 0.92, 35000, 150.0, "¥"),("Южная Корея", "🇰🇷", "east_asia", 250, 83, 0.98, 0.81, 33000, 1330.0, "₩"),("Монголия", "🇲🇳", "east_asia", 80, 70, 0.90, 0.68, 4500, 3450.0, "₮"),
    ("Индонезия", "🇮🇩", "southeast_asia", 4500, 72, 0.85, 0.57, 4500, 15800.0, "Rp"),("Филиппины", "🇵🇭", "southeast_asia", 2000, 71, 0.85, 0.48, 3500, 56.0, "₱"),("Вьетнам", "🇻🇳", "southeast_asia", 1400, 75, 0.92, 0.40, 4000, 24500.0, "₫"),("Таиланд", "🇹🇭", "southeast_asia", 500, 79, 0.94, 0.53, 7000, 35.0, "฿"),("Малайзия", "🇲🇾", "southeast_asia", 450, 76, 0.94, 0.78, 11000, 4.7, "RM"),("Мьянма", "🇲🇲", "southeast_asia", 850, 66, 0.75, 0.31, 1400, 2100.0, "K"),
    ("Нигерия", "🇳🇬", "africa", 8000, 55, 0.55, 0.52, 2000, 1500.0, "₦"),("ДР Конго", "🇨🇩", "africa", 4000, 60, 0.45, 0.47, 600, 2800.0, "₣"),("Эфиопия", "🇪🇹", "africa", 3800, 67, 0.50, 0.22, 1000, 57.0, "Br"),("Кения", "🇰🇪", "africa", 1400, 66, 0.65, 0.29, 2000, 130.0, "KSh"),("Танзания", "🇹🇿", "africa", 1300, 66, 0.60, 0.36, 1100, 2500.0, "TSh"),("Уганда", "🇺🇬", "africa", 1000, 63, 0.55, 0.26, 900, 3800.0, "USh"),("ЮАР", "🇿🇦", "africa", 900, 64, 0.90, 0.68, 6000, 18.0, "R"),("Ангола", "🇦🇴", "africa", 800, 62, 0.50, 0.67, 2500, 830.0, "Kz"),("Мозамбик", "🇲🇿", "africa", 750, 61, 0.45, 0.38, 500, 63.0, "MT"),("Гана", "🇬🇭", "africa", 550, 64, 0.75, 0.58, 2200, 15.0, "₵"),("Кот-д'Ивуар", "🇨🇮", "africa", 550, 59, 0.55, 0.53, 2300, 620.0, "CFA"),("Камерун", "🇨🇲", "africa", 600, 60, 0.70, 0.59, 1500, 620.0, "FCFA"),("Мадагаскар", "🇲🇬", "africa", 650, 65, 0.60, 0.40, 500, 4400.0, "Ar"),("Мали", "🇲🇱", "africa", 850, 60, 0.35, 0.45, 800, 620.0, "CFA"),("Нигер", "🇳🇪", "africa", 700, 62, 0.30, 0.17, 550, 620.0, "CFA"),("Сенегал", "🇸🇳", "africa", 550, 68, 0.50, 0.49, 1600, 620.0, "CFA"),("Сомали", "🇸🇴", "africa", 450, 56, 0.25, 0.47, 450, 570.0, "Sh"),("Замбия", "🇿🇲", "africa", 500, 62, 0.60, 0.46, 1300, 26.0, "ZK"),("Зимбабве", "🇿🇼", "africa", 400, 62, 0.80, 0.32, 1200, 360.0, "Z$"),("Руанда", "🇷🇼", "africa", 350, 67, 0.65, 0.18, 800, 1300.0, "RF"),
    ("Египет", "🇪🇬", "arab", 1900, 72, 0.80, 0.43, 4000, 48.0, "E£"),("Алжир", "🇩🇿", "arab", 800, 77, 0.85, 0.75, 4500, 135.0, "DA"),("Марокко", "🇲🇦", "arab", 500, 74, 0.75, 0.65, 3500, 10.0, "DH"),("Тунис", "🇹🇳", "arab", 170, 77, 0.85, 0.70, 4000, 3.1, "DT"),("Ливия", "🇱🇾", "arab", 120, 73, 0.85, 0.81, 6500, 4.8, "LD"),("Судан", "🇸🇩", "arab", 1100, 66, 0.55, 0.36, 700, 600.0, "SDG"),("Ирак", "🇮🇶", "arab", 900, 71, 0.75, 0.71, 4500, 1310.0, "IQD"),("Сирия", "🇸🇾", "arab", 500, 73, 0.75, 0.57, 1200, 13000.0, "S£"),("Йемен", "🇾🇪", "arab", 700, 66, 0.55, 0.39, 800, 250.0, "YR"),("Саудовская Аравия", "🇸🇦", "arab", 550, 76, 0.95, 0.84, 25000, 3.75, "SR"),("Иордания", "🇯🇴", "arab", 200, 75, 0.92, 0.92, 4500, 0.71, "JD"),("Ливан", "🇱🇧", "arab", 80, 79, 0.92, 0.89, 4500, 15000.0, "L£"),("ОАЭ", "🇦🇪", "arab", 100, 78, 0.95, 0.87, 45000, 3.67, "DH"),
    ("Бразилия", "🇧🇷", "latam", 2600, 76, 0.90, 0.87, 8000, 5.1, "R$"),("Мексика", "🇲🇽", "latam", 1800, 75, 0.88, 0.81, 9000, 17.0, "MX$"),("Колумбия", "🇨🇴", "latam", 650, 77, 0.88, 0.82, 6000, 3900.0, "C$"),("Аргентина", "🇦🇷", "latam", 500, 77, 0.94, 0.92, 12000, 350.0, "AR$"),("Перу", "🇵🇪", "latam", 550, 77, 0.88, 0.78, 6500, 3.8, "S/"),("Венесуэла", "🇻🇪", "latam", 450, 72, 0.92, 0.88, 3500, 36.0, "Bs"),("Чили", "🇨🇱", "latam", 200, 80, 0.95, 0.88, 15000, 950.0, "CL$"),("Эквадор", "🇪🇨", "latam", 300, 77, 0.88, 0.64, 6000, 1.0, "$"),("Боливия", "🇧🇴", "latam", 250, 72, 0.85, 0.70, 3500, 6.9, "Bs"),("Уругвай", "🇺🇾", "latam", 45, 78, 0.96, 0.96, 17000, 39.0, "U$"),("Куба", "🇨🇺", "latam", 120, 79, 0.99, 0.77, 9000, 24.0, "CUP"),("Гватемала", "🇬🇹", "latam", 350, 74, 0.75, 0.52, 4500, 7.8, "Q"),("Гаити", "🇭🇹", "latam", 250, 64, 0.60, 0.57, 1700, 130.0, "G"),
    ("Германия", "🇩🇪", "europe", 800, 81, 0.98, 0.78, 45000, 0.92, "€"),("Франция", "🇫🇷", "europe", 700, 82, 0.98, 0.81, 42000, 0.92, "€"),("Великобритания", "🇬🇧", "europe", 700, 81, 0.98, 0.84, 46000, 0.79, "£"),("Италия", "🇮🇹", "europe", 400, 83, 0.98, 0.71, 34000, 0.92, "€"),("Испания", "🇪🇸", "europe", 350, 83, 0.98, 0.81, 30000, 0.92, "€"),("Польша", "🇵🇱", "europe", 350, 78, 0.98, 0.60, 18000, 4.0, "zł"),("Нидерланды", "🇳🇱", "europe", 170, 82, 0.98, 0.92, 55000, 0.92, "€"),("Бельгия", "🇧🇪", "europe", 115, 82, 0.98, 0.98, 50000, 0.92, "€"),("Швеция", "🇸🇪", "europe", 110, 83, 0.98, 0.88, 55000, 10.5, "kr"),("Швейцария", "🇨🇭", "europe", 85, 84, 0.98, 0.74, 85000, 0.88, "CHF"),("Норвегия", "🇳🇴", "europe", 55, 83, 0.98, 0.83, 80000, 10.5, "kr"),("Португалия", "🇵🇹", "europe", 85, 82, 0.98, 0.66, 25000, 0.92, "€"),("Греция", "🇬🇷", "europe", 85, 82, 0.98, 0.80, 20000, 0.92, "€"),("Австрия", "🇦🇹", "europe", 85, 82, 0.98, 0.59, 50000, 0.92, "€"),
    ("Россия", "🇷🇺", "post_soviet", 1300, 73, 0.98, 0.75, 10000, 92.0, "₽"),("Узбекистан", "🇺🇿", "post_soviet", 700, 72, 0.90, 0.50, 2500, 12600.0, "so'm"),("Казахстан", "🇰🇿", "post_soviet", 400, 74, 0.95, 0.58, 10000, 450.0, "₸"),("Украина", "🇺🇦", "post_soviet", 300, 72, 0.98, 0.70, 4000, 37.0, "₴"),("Азербайджан", "🇦🇿", "post_soviet", 130, 74, 0.90, 0.57, 5500, 1.7, "₼"),("Беларусь", "🇧🇾", "post_soviet", 100, 74, 0.98, 0.79, 7000, 3.3, "Br"),
    ("США", "🇺🇸", "developed", 3600, 79, 0.95, 0.83, 55000, 1.0, "$"),("Канада", "🇨🇦", "developed", 380, 82, 0.98, 0.82, 50000, 1.36, "C$"),("Австралия", "🇦🇺", "developed", 300, 83, 0.98, 0.86, 55000, 1.5, "A$"),("Израиль", "🇮🇱", "developed", 180, 83, 0.95, 0.93, 45000, 3.7, "₪"),("Сингапур", "🇸🇬", "developed", 40, 84, 0.98, 1.00, 65000, 1.35, "S$"),("Катар", "🇶🇦", "developed", 30, 80, 0.95, 0.99, 60000, 3.64, "QR"),("Новая Зеландия", "🇳🇿", "developed", 60, 82, 0.98, 0.86, 42000, 1.6, "NZ$")
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

DISEASES = {
    "Астма": {"mort": 1.1, "cash": 300}, "Диабет 1 типа": {"mort": 1.4, "cash": 1500}, "Диабет 2 типа": {"mort": 1.2, "cash": 800}, "Гипертония": {"mort": 1.3, "cash": 400}, "Артрит": {"mort": 1.15, "cash": 500}, "Псориаз": {"mort": 1.05, "cash": 300}, "Эпилепсия": {"mort": 1.5, "cash": 600}, "Мигрень": {"mort": 1.05, "cash": 200},
    "Туберкулез": {"mort": 1.8, "cash": 1500}, "Сифилис": {"mort": 1.3, "cash": 500}, "Гонорея": {"mort": 1.1, "cash": 400}, "ВИЧ/СПИД": {"mort": 1.5, "cash": 2000}, "Гепатит B": {"mort": 1.5, "cash": 1200}, "Гепатит C": {"mort": 1.6, "cash": 2500}, "Холера": {"mort": 2.5, "cash": 800}, "Тиф": {"mort": 1.8, "cash": 600}, "Корь": {"mort": 1.6, "cash": 400}, "Ковид-19": {"mort": 1.4, "cash": 1000}, "Малярия": {"mort": 2.0, "cash": 600},
    "Рак легких": {"mort": 3.0, "cash": 5000}, "Рак груди": {"mort": 2.2, "cash": 4000}, "Лейкемия": {"mort": 2.8, "cash": 8000},
    "ПТСР": {"mort": 1.4, "cash": 500}, "Депрессия": {"mort": 1.3, "cash": 400}, "Биполярное расстройство": {"mort": 1.3, "cash": 700}, "Шизофрения": {"mort": 1.4, "cash": 800}, "Алкоголизм": {"mort": 1.8, "cash": 600}, "Наркомания": {"mort": 2.0, "cash": 1500},
    "Сердечная недостаточность": {"mort": 2.2, "cash": 1500}, "Инфаркт": {"mort": 2.5, "cash": 3000}, "Инсульт": {"mort": 2.5, "cash": 3000}, "Цирроз печени": {"mort": 2.2, "cash": 1000}, "Полиомиелит": {"mort": 1.5, "cash": 500}, "Ожирение": {"mort": 1.3, "cash": 400}, "Анемия": {"mort": 1.1, "cash": 200}, "Бесплодие": {"mort": 1.0, "cash": 0}
}

ETHNICITIES = {
    "south_asia": [("Хиндустанец", 35, None),("Бенгалец", 15, "Считают тебя бедным."),("Тамил", 10, "Считают тебя хитрым."),("Мусульманин", 15, "Считают тебя агрессивным."),("Далит", 10, "Считают тебя грязным."),("Сикх", 5, "Считают тебя воинственным.")],
    "east_asia": [("Хань", 60, None),("Японец", 15, "Считают тебя трудоголиком."),("Кореец", 12, "Считают тебя умным."),("Монгол", 5, "Считают тебя дикарем."),("Уйгур", 5, "Считают тебя чужим.")],
    "southeast_asia": [("Яванец", 35, None),("Тайец", 20, None),("Вьетнамец", 15, "Считают тебя хитрым."),("Филиппинец", 15, "Считают тебя беззаботным."),("Кхмер", 10, "Считают тебя бедным.")],
    "africa": [("Йоруба", 20, None),("Игбо", 15, "Считают тебя предприимчивым."),("Хауса", 15, "Считают тебя фанатиком."),("Оромо", 15, "Считают тебя дикарем."),("Зулус", 10, "Считают тебя агрессивным."),("Копт", 5, "Считают тебя предателем."),("Белый (потомок колонистов)", 5, "Считают тебя угнетателем.")],
    "arab": [("Араб", 55, None),("Египтянин", 20, None),("Бербер", 8, "Считают тебя дикарем."),("Курд", 5, "Считают тебя сепаратистом."),("Ассириец", 4, "Считают тебя чужим."),("Друз", 3, None)],
    "latam": [("Метис", 45, None),("Креол", 20, "Считают тебя снобом."),("Мулат", 15, None),("Индеец", 10, "Считают тебя дикарем."),("Афро-латиноамериканец", 5, "Считают тебя агрессивным."),("Азиат", 3, "Считают тебя трудолюбивым.")],
    "europe": [("Немец", 12, None),("Француз", 12, None),("Итальянец", 8, "Считают, что ты связан с мафией."),("Испанец", 8, None),("Поляк", 8, None),("Швед", 5, None),("Грек", 4, None),("Португалец", 4, None),("Еврей", 8, "Считают тебя скупым."),("Цыган", 8, "Считают тебя вором."),("Турок", 8, "Считают тебя чужаком."),("Араб (мигрант)", 8, "Считают тебя террористом."),("Африканец (мигрант)", 7, "Считают тебя нищим.")],
    "post_soviet": [("Русский", 50, None),("Украинец", 15, None),("Белорус", 5, None),("Татарин", 5, "Считают тебя хитрым."),("Кавказец", 10, "Считают тебя бандитом."),("Еврей", 4, "Считают тебя скупым."),("Среднеазиат", 8, "Считают тебя гастарбайтером."),("Цыган", 3, "Считают тебя вором.")],
    "developed": [("WASP", 35, None),("Афроамериканец", 18, "Считают тебя агрессивным."),("Латиноамериканец", 15, "Считают тебя нелегалом."),("Азиат", 12, "Считают тебя умным."),("Еврей", 5, "Считают тебя скупым."),("Коренной американец", 5, "Считают тебя алкоголиком."),("Ирландец", 5, "Считают тебя пьяницей."),("Итальянец", 5, "Считают тебя мафиози.")]
}

NAMES = {
    "south_asia": {"m": ["Арджун","Раджеш","Викрам","Адитья","Рохан","Кабир","Амир","Раджит","Сунил","Деван"], "f": ["Прия","Айша","Рани","Дивья","Ниша","Приянка","Фатима","Сита","Лакшми","Сара"]},
    "east_asia": {"m": ["Вэй","Мин","Хиро","Джун","Кай","Тао","Юта","Хару","Чен","Вон"], "f": ["Юки","Сакура","Мэй","Ли","Линь","Хана","Ёко","Суа","Мина","Юна"]},
    "southeast_asia": {"m": ["Агус","Буди","Димас","Хуан","Хосе","Карло","Мигель","Анвар","Ризки","Нарат"], "f": ["Дези","Сри","Вина","Аю","Мария","Роза","Луз","Карла","Нур","Лин"]},
    "africa": {"m": ["Чинеду","Эмека","Кваме","Кофи","Аде","Олу","Муса","Абдул","Джамал","Тао"], "f": ["Нгози","Амара","Айша","Фатима","Амина","Зейнаб","Грейс","Мери","Номвело","Танди"]},
    "arab": {"m": ["Мухаммед","Ахмед","Али","Омар","Хасан","Хусейн","Юсуф","Ибрагим","Халид","Салем"], "f": ["Фатима","Айша","Лейла","Марьям","Нур","Зейнаб","Сальма","Рания","Лина","Сара"]},
    "latam": {"m": ["Хуан","Карлос","Хосе","Педро","Луис","Мигель","Антонио","Франсиско","Диего","Рафаэль"], "f": ["Мария","Кармен","Изабель","Лусия","Ана","София","Валентина","Камила","Марта","Элена"]},
    "europe": {"m": ["Томас","Лукас","Феликс","Пол","Пьер","Люк","Джеймс","Джек","Марко","Маттео"], "f": ["Анна","Эмилия","Софи","Клара","Шарлотта","Мария","Лея","Луиза","Эмма","Миа"]},
    "post_soviet": {"m": ["Иван","Дмитрий","Александр","Сергей","Андрей","Михаил","Никита","Артём","Тимур","Руслан"], "f": ["Анна","Мария","Елена","Ольга","Наташа","Катя","София","Даша","Алина","Полина"]},
    "developed": {"m": ["Джеймс","Джон","Майкл","Дэвид","Крис","Мэтт","Тайлер","Джек","Ноа","Лиам"], "f": ["Эмили","Сара","Джессика","Эмма","Оливия","София","Ханна","Эбигейл","Миа","Шарлотта"]}
}

CAREER_TITLES = {
    "civilian": {1: "Стажер", 2: "Специалист", 3: "Старший специалист", 4: "Менеджер", 5: "Директор"},
    "police": {1: "Курсант", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Полковник"},
    "military": {1: "Рядовой", 2: "Сержант", 3: "Лейтенант", 4: "Капитан", 5: "Генерал"},
    "criminal": {1: "Шестерка", 2: "Боец", 3: "Бригадир", 4: "Авторитет", 5: "Босс"},
}

INCOME_LABELS = ["Бедная семья", "Средний класс", "Богатая семья"]
PROPERTIES = {"Общага": 3000, "Квартира": 30000, "Дом": 200000, "Особняк": 1500000, "Остров": 50000000}
CARS = {"Скутер": 800, "Седан": 15000, "Внедорожник": 40000, "Спорткар": 200000}
BUSINESSES = {"Ларёк": 5000, "Кофейня": 25000, "Ресторан": 150000, "Завод": 2000000}

TESTS = {
    1: [{"q": "Сколько будет 5 + 7?", "opts": ["10", "12", "13"], "ans": 1},{"q": "Сколько букв в слове 'МАМА'?", "opts": ["2", "4", "6"], "ans": 1},{"q": "Сколько цветов у радуги?", "opts": ["5", "7", "9"], "ans": 1},{"q": "Что больше: 3×3 или 2×5?", "opts": ["3×3", "2×5", "Равны"], "ans": 1},{"q": "Сколько месяцев в году?", "opts": ["10", "12", "14"], "ans": 1},{"q": "Какое животное мяукает?", "opts": ["Собака", "Кошка", "Корова"], "ans": 1},{"q": "Сколько ног у паука?", "opts": ["6", "8", "10"], "ans": 1},{"q": "Что тает на солнце?", "opts": ["Камень", "Снег", "Песок"], "ans": 1},{"q": "Сколько дней в неделе?", "opts": ["5", "7", "10"], "ans": 1},{"q": "Какого цвета трава?", "opts": ["Красная", "Зеленая", "Синяя"], "ans": 1}],
    2: [{"q": "Если x - 4 = 10, чему равен x?", "opts": ["6", "14", "40"], "ans": 1},{"q": "Какая планета ближе к Солнцу?", "opts": ["Венера", "Меркурий", "Земля"], "ans": 1},{"q": "Сколько градусов в прямом угле?", "opts": ["45", "90", "180"], "ans": 1},{"q": "Кто написал 'Войну и мир'?", "opts": ["Достоевский", "Толстой", "Пушкин"], "ans": 1},{"q": "Чему равен корень из 144?", "opts": ["10", "12", "14"], "ans": 1},{"q": "Что такое H2O?", "opts": ["Соль", "Вода", "Кислород"], "ans": 1},{"q": "Столица Франции?", "opts": ["Лондон", "Париж", "Берлин"], "ans": 1},{"q": "Сколько будет 15% от 200?", "opts": ["20", "30", "40"], "ans": 1},{"q": "Какой газ нужен растениям?", "opts": ["Кислород", "Углекислый газ", "Азот"], "ans": 1},{"q": "Кто открыл Америку?", "opts": ["Магеллан", "Колумб", "Васко да Гама"], "ans": 1}],
    3: [{"q": "Столица Австралии?", "opts": ["Сидней", "Мельбурн", "Канберра"], "ans": 2},{"q": "Производная от x^2?", "opts": ["x", "2x", "x^3/3"], "ans": 1},{"q": "Сколько планет в Солнечной системе?", "opts": ["7", "8", "9"], "ans": 1},{"q": "Кто открыл тяготение?", "opts": ["Эйнштейн", "Ньютон", "Галилей"], "ans": 1},{"q": "Что такое ДНК?", "opts": ["Белок", "Кислота", "Углевод"], "ans": 1},{"q": "Столица Японии?", "opts": ["Осака", "Токио", "Киото"], "ans": 1},{"q": "log(100) по основанию 10?", "opts": ["1", "2", "10"], "ans": 1},{"q": "Интеграл от 2x dx?", "opts": ["x^2 + C", "2x^2 + C", "x + C"], "ans": 0},{"q": "Кто написал 'Преступление и наказание'?", "opts": ["Толстой", "Достоевский", "Чехов"], "ans": 1},{"q": "Что такое фотон?", "opts": ["Квант света", "Частица атома", "Волна"], "ans": 0}]
}

# ================= УТИЛИТЫ ДЛЯ ТЕКСТА =================
def get_age_str(age):
    """Правильное склонение слова 'год' в зависимости от числа"""
    if age % 10 == 1 and age % 100 != 11:
        return f"{age} год"
    elif age % 10 in (2, 3, 4) and age % 100 not in (12, 13, 14):
        return f"{age} года"
    else:
        return f"{age} лет"

# ================= КАТ-СЦЕНЫ =================
def play_cutscene(chat_id, frames, final_text, kb=None):
    msg = bot.send_message(chat_id, frames[0], parse_mode="HTML")
    for frame in frames[1:]:
        time.sleep(1.2)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="HTML")
        except: pass
    time.sleep(1.2)
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=final_text, reply_markup=kb, parse_mode="HTML")
    except:
        bot.send_message(chat_id, final_text, reply_markup=kb, parse_mode="HTML")

def get_cutscene_frames(event_type):
    if event_type == "birth": return ["🏥 👨‍⚕️ 🤰\n<i>Врачи готовятся...</i>", "👶 ✨ 👨‍👩‍👦\n<i>Раздается первый крик!</i>", "🎉 🍼 🧸\n<i>Новая жизнь началась!</i>"]
    elif event_type == "marry": return ["💐 🍷 👩‍❤️‍👨\n<i>Романтический ужин...</i>", "🤵 👰 💍\n<i>Предложение руки и сердца!</i>", "🥂 🎉 💖\n<i>Свадьба!</i>"]
    elif event_type == "prison": return ["🚔 🚨 🏃‍♂️\n<i>Погоня...</i>", "👮‍♂️ 🔗 👨\n<i>Задержание...</i>", "⛓ 🧱 🚪\n<i>Дверь камеры захлопнулась.</i>"]
    elif event_type == "death": return ["🏥 🛌 💔\n<i>Здоровье подводит...</i>", "🕯️ ☁️\n<i>Последний вздох...</i>", "🪦 🥀 🕊️\n<i>Жизнь окончена.</i>"]
    return []

# ================= ЭМОДЗИ-СЦЕНЫ =================
def get_scene_visuals(scene_type, gender):
    male = ["👦", "🧑", "👨", "🧔", "👨‍💼", "👨‍💻", "👨‍🎓"]
    female = ["👧", "👩", "👩‍🦰", "👩‍🦱", "👩‍💼", "👩‍💻", "👩‍🎓"]
    player = random.choice(male) if gender == "m" else random.choice(female)
    
    if scene_type == "child": return f"🏠 🌳 {player} 🧸 ☀️"
    elif scene_type == "school": return f"🏫 {player} 📚 🎒 🍎"
    elif scene_type == "rich": return f"🏰 🚗 💰 {player} 🥂 🛥"
    elif scene_type == "office": return f"🏢 🧑‍💻 {player} 📊 ☕"
    elif scene_type == "office_angry": return f"🏢 😡 {player} 💢 📉"
    elif scene_type == "hospital": return f"🏥 🛌 {player} 💉 🩺"
    elif scene_type == "prison": return f"⛓ 🧱 {player} 🚔 🕶"
    elif scene_type == "fight": return f"👊 💥 {player} 🥊 🤕"
    elif scene_type == "love": return f"❤️ {player} 🌹 💑 💐"
    elif scene_type == "wedding": return f"💍 🤵 👰 {player} 🎉"
    elif scene_type == "sad": return f"🌧 {player} ☂️ 😔 💧"
    elif scene_type == "police": return f"🚔 💵 {player} 🚨 😰"
    elif scene_type == "money_win": return f"💰 🤑 {player} 💎 🎰"
    elif scene_type == "money_lose": return f"💸 😭 {player} 🕳 📉"
    return f"🌆 {player} 🏙 🚶"

# ================= УТИЛИТЫ =================
def fmt_money(amount_usd, country):
    return f"{int(amount_usd * country[8]):,} {country[9]}".replace(",", " ")

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
        trajectory = random.choice(["prosperous", "criminal", "ordinary", "unfortunate"])
        if trajectory == "criminal": death_age = random.randint(20, 45)
        elif trajectory == "unfortunate": death_age = random.randint(1, 15)
        else:
            death_age = int(random.gauss(c[4], 10))
            if death_age < 1: death_age = random.randint(1, 5)
        neighbors.append({"name": name, "country": c, "gender": g, "trajectory": trajectory, "death_age": death_age})
    return neighbors

def get_neighbor_echo(n, age):
    g_m = n["gender"] == "m"
    if age >= n["death_age"]:
        if n["death_age"] < 3: return "умер(ла) в младенчестве"
        elif n["death_age"] < 18: return f"умер(ла) от болезни в {get_age_str(n['death_age'])}"
        elif n["trajectory"] == "criminal": return f"погиб(ла) в разборке в {get_age_str(n['death_age'])}"
        else: return f"умер(ла) в {get_age_str(n['death_age'])}"
    if age < 13:
        if n["trajectory"] == "unfortunate": return "живет в бедности"
        elif n["trajectory"] == "prosperous": return "ходит в элитную школу"
        else: return "ходит в школу"
    elif age < 25:
        if n["trajectory"] == "criminal": return "связался с бандой" if g_m else "связалась с бандой"
        elif n["trajectory"] == "prosperous": return "поступил в вуз" if g_m else "поступила в вуз"
        else: return "работает"
    elif age < 55:
        if n["trajectory"] == "criminal": return "сидит в тюрьме"
        elif n["trajectory"] == "prosperous": return "стал богатым" if g_m else "стала богатой"
        else: return "работает на заводе"
    return "на пенсии"

def get_neighbor_final(n):
    if n["death_age"] < 3: return "умер(ла) в младенчестве"
    elif n["trajectory"] == "criminal": return f"погиб(ла) в разборке в {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "prosperous": return f"умер(ла) богатым(ой) в {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "unfortunate": return f"умер(ла) в бедности в {get_age_str(n['death_age'])}"
    else: return f"умер(ла) в {get_age_str(n['death_age'])}"

def create_life(force_country=None):
    country = force_country if force_country else weighted_country()
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    ethnicity, prejudice = get_ethnicity(country[2])
    start_cash = int(country[7] * random.uniform(0.1, 2.0))
    return {
        "country": country, "gender": gender, "name": name, "ethnicity": ethnicity, "prejudice": prejudice,
        "clean_cash": start_cash, "dirty_cash": 0, "in_prison": 0, "age": 0, "alive": True, "faction": "Нет",
        "health": 100, "happiness": 50, "knowledge": 50, "relationships": 50,
        "education": "Нет", "job": "Безработный", "salary": 0, "job_type": "none", "career_xp": 0, "career_rank": 1,
        "married": False, "children": 0, "diseases": [], "properties": [], "cars": [], "businesses": [], "debt": 0,
        "life_map": [], "neighbors": generate_neighbors(), "test_data": None, "asked_tests": {1: [], 2: [], 3: []}, "current_event": None,
        "has_license": False, "job_years": 0
    }

def add_to_life_map(l, text):
    if len(l["life_map"]) < 10: l["life_map"].append(f"{get_age_str(l['age'])}: {text}")

def mortality_rate(l):
    base = 0.05 if l["age"] < 5 else 0.003
    if l["age"] > 60: base = 0.02
    if l["age"] > 80: base = 0.1
    if l["in_prison"] > 0: base *= 1.5
    if l["debt"] > 0: base *= 1.3
    if l["health"] < 30: base *= 2.0
    elif l["health"] < 50: base *= 1.3
    for d in l["diseases"]: base *= DISEASES[d]["mort"]
    if l["job_type"] == "military": base *= 1.2
    if l["job_type"] == "criminal": base *= 1.4
    return min(0.9, base)

# ================= СОБЫТИЯ =================
def get_event(l):
    age = l["age"]
    g_m = l["gender"] == "m"

    if l["prejudice"] and 16 < age < 60 and random.random() < 0.15:
        return {"title": "Столкновение с предвзятостью", "text": f"{l['prejudice']}",
                "choices": [{"text": "✊ Доказать обратное", "p": 0.4, "success": "prej_fight_win", "fail": "prej_fight_fail"},
                            {"text": "🦊 Использовать стереотип", "p": 0.7, "success": "prej_exploit", "fail": "prej_exploit_fail"},
                            {"text": "😔 Смириться", "p": 1, "success": "prej_accept", "fail": "none"}]}
    
    if age >= 18 and l["job_type"] in ["civilian", "police", "military"] and random.random() < 0.3:
        if random.random() < 0.5:
            return {"title": "💼 Овертайм", "text": "Горящий проект. Начальник просит остаться.", "choices": [{"text": "Согласиться", "p": 0.7, "success": "career_xp_up", "fail": "none"}, {"text": "Уйти", "p": 1, "success": "career_xp_down", "fail": "none"}]}
        else:
            return {"title": "📉 Интриги", "text": "Коллега подставил тебя.", "choices": [{"text": "Скандал", "p": 0.3, "success": "career_fight_win", "fail": "career_grind"}, {"text": "Смириться", "p": 1, "success": "career_grind", "fail": "none"}]}

    if age >= 18 and l["cars"] and random.random() < 0.2:
        if not l.get("has_license"):
            return {"title": "🚨 Остановка ДПС", "text": "Инспектор просит права. У тебя их нет.", "choices": [{"text": "💵 Дать взятку", "p": 0.7, "success": "bribe_dps", "fail": "dps_jail"}, {"text": "😬 Договориться", "p": 0.2, "success": "dps_warning", "fail": "dps_jail"}]}
        elif random.random() < 0.3:
            return {"title": "🍻 Пьяная езда", "text": "Инспектор замечает запах перегара.", "choices": [{"text": "💵 Взятка", "p": 0.5, "success": "bribe_dps_big", "fail": "drunk_jail"}, {"text": "🚶 Отказ от теста", "p": 0.1, "success": "dps_warning", "fail": "drunk_jail"}, {"text": "😭 Смириться", "p": 1, "success": "drunk_jail", "fail": "none"}]}

    if random.random() < 0.45:
        if age < 13:
            return random.choice([
                {"title": "🧸 Детский сад", "text": "Тебя обижает ребенок.", "choices": [{"text": "Дать сдачи", "p": 0.5, "success": "child_fight", "fail": "none"}, {"text": "Пожаловаться", "p": 0.8, "success": "child_tell", "fail": "none"}]},
                {"title": "📚 Первая книга", "text": "Тебе подарили книгу.", "choices": [{"text": "Читать", "p": 0.8, "success": "child_smart", "fail": "none"}, {"text": "Гулять", "p": 1, "success": "child_walk", "fail": "none"}]}
            ])
        elif age < 18:
            return random.choice([
                {"title": "🚬 Сигарета", "text": "Старшеклассники предлагают закурить.", "choices": [{"text": "Попробовать", "p": 0.9, "success": "teen_smoke", "fail": "none"}, {"text": "Отказаться", "p": 1, "success": "teen_healthy", "fail": "none"}]},
                {"title": "💔 Любовь", "text": "Тебе нравится одноклассник(ца).", "choices": [{"text": "Признаться", "p": 0.4, "success": "teen_love", "fail": "none"}, {"text": "Скрывать", "p": 1, "success": "none", "fail": "none"}]}
            ])
        else:
            adult = []
            if l["married"] and l["children"] > 0:
                adult.append({"title": "👶 Кризис", "text": "Денег не хватает.", "choices": [{"text": "Вторую работу", "p": 0.7, "success": "work_extra", "fail": "burnout"}, {"text": "Семью", "p": 1, "success": "family_time", "fail": "none"}]})
            elif not l["married"] and 18 <= age < 45:
                adult.append({"title": "💍 Брак", "text": "Партнер предлагает жениться.", "choices": [{"text": "Согласиться", "p": 0.8, "success": "marry", "fail": "none"}, {"text": "Отказаться", "p": 1, "success": "none", "fail": "none"}]})
            elif l["married"]:
                adult.append({"title": "💔 Развод", "text": "Супруг подает на развод.", "choices": [{"text": "Смириться", "p": 1, "success": "divorce", "fail": "none"}]})
            
            adult.append({"title": "📞 Мошенники", "text": "Звонят из 'банка'.", "choices": [{"text": "Дать код", "p": 1, "success": "scammed", "fail": "none"}, {"text": "Бросить", "p": 1, "success": "none", "fail": "none"}]})
            
            if l["clean_cash"] >= 100:
                adult.append({"title": "🎰 Лотерея", "text": "Купил билет за 100.", "choices": [{"text": "Проверить", "p": 0.05, "success": "lottery_win", "fail": "lottery_lose"}]})
            
            return random.choice(adult)
            
    if age >= 22 and l["job_type"] == "none" and l["faction"] == "Нет" and l["in_prison"] == 0:
        return {"title": "Выбор пути", "text": "Пора определяться.",
                "choices": [
                    {"text": "💼 Гражданка", "p": 1, "success": "job_civ", "fail": "none"},
                    {"text": "👮 Полиция", "p": 1 if l["education"] == "Высшее" else 0, "success": "job_pol", "fail": "none"},
                    {"text": "🎖 Армия", "p": 1 if l["education"] in ["Среднее", "Высшее"] else 0, "success": "job_mil", "fail": "none"},
                    {"text": "💊 Криминал", "p": 1, "success": "job_crim", "fail": "none"}
                ]}
    return None

# ================= ХАРАКТЕРИСТИКИ =================
def get_stats_line(l):
    return f"❤️ Здоровье: {l['health']}% | 😊 Счастье: {l['happiness']}% | 🧠 Знания: {l['knowledge']}% | 🤝 Отношения: {l['relationships']}%"

def apply_focus(l, focus):
    if focus == "health":
        l["health"] = min(100, l["health"] + random.randint(5, 10))
        l["happiness"] = min(100, l["happiness"] + random.randint(0, 5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0, 3))
        l["relationships"] = max(0, l["relationships"] - random.randint(0, 3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Уделил время здоровью")
    elif focus == "knowledge":
        l["knowledge"] = min(100, l["knowledge"] + random.randint(5, 10))
        l["happiness"] = max(0, l["happiness"] - random.randint(0, 5))
        l["health"] = max(0, l["health"] - random.randint(0, 3))
        l["relationships"] = max(0, l["relationships"] - random.randint(0, 3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Учился и развивался")
    elif focus == "relationships":
        l["relationships"] = min(100, l["relationships"] + random.randint(5, 10))
        l["happiness"] = min(100, l["happiness"] + random.randint(0, 5))
        l["health"] = max(0, l["health"] - random.randint(0, 3))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0, 3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Уделил время семье и друзьям")
    elif focus == "happiness":
        l["happiness"] = min(100, l["happiness"] + random.randint(10, 15))
        l["health"] = max(0, l["health"] - random.randint(0, 5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0, 5))
        l["relationships"] = max(0, l["relationships"] - random.randint(0, 5))
        l["life_map"].append(f"{get_age_str(l['age'])}: Наслаждался жизнью")
    elif focus == "work":
        l["happiness"] = max(0, l["happiness"] - random.randint(2, 6))
        l["health"] = max(0, l["health"] - random.randint(1, 4))
        l["knowledge"] = min(100, l["knowledge"] + random.randint(0, 3))
        l["relationships"] = max(0, l["relationships"] - random.randint(0, 4))
        l["life_map"].append(f"{get_age_str(l['age'])}: Работал не покладая рук")

def next_year(user_id, chat_id):
    uid_str = str(user_id)
    if uid_str not in players_db: return bot.send_message(chat_id, "Начни заново: /start")
    l = players_db[uid_str]
    if not l["alive"]: return bot.send_message(chat_id, "Ты уже умер. Начни заново: /start")
        
    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1; save_db(players_db)
        if l["in_prison"] == 0: 
            l["job"] = "Безработный"; l["salary"] = 0; l["job_type"] = "none"
            return send_scene(chat_id, l, "⛓ <b>Ты вышел на свободу. Придется искать работу заново.</b>", kb_year(), "life")
        return send_scene(chat_id, l, f"⛓ <b>Тюрьма.</b> Осталось: {get_age_str(l['in_prison'])}.", kb_year(), "prison")
    
    if l.get("focus"):
        apply_focus(l, l["focus"])
        l["focus"] = None
    
    l["age"] += 1
    
    rent = sum(int(pr["value"] * 0.05) for pr in l["properties"])
    biz = sum(int(b["value"] * 0.15) for b in l["businesses"])
    l["clean_cash"] += rent + biz
    
    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian", "police", "military"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    
    spend_mod = 1.0
    if l["prejudice"] and ("скупым" in l["prejudice"] or "предприимчивым" in l["prejudice"]): spend_mod = 0.7
    elif l["prejudice"] and ("беззаботным" in l["prejudice"] or "пьяницей" in l["prejudice"]): spend_mod = 1.3
    
    living = int(l["country"][7] * 0.2 * spend_mod + (300 * l["children"]))
    l["clean_cash"] += (l["salary"] - tax - med - living)
    if l["clean_cash"] < 0: 
        l["debt"] += abs(l["clean_cash"]); l["clean_cash"] = 0

    if l["job_type"] in ["civilian", "police", "military"]:
        l["job_years"] += 1
        if l["career_xp"] >= 100 and l["job_years"] >= 2:
            l["career_xp"] = 0; l["career_rank"] = min(5, l["career_rank"] + 1); l["salary"] = int(l["salary"] * 1.3); l["job_years"] = 0
            add_to_life_map(l, f"Повышение до {CAREER_TITLES[l['job_type']][l['career_rank']]}")
        elif l["career_xp"] <= -50:
            l["career_xp"] = 0; l["career_rank"] = max(1, l["career_rank"] - 1); l["salary"] = int(l["salary"] * 0.7); l["job_years"] = 0
            add_to_life_map(l, f"Понижение до {CAREER_TITLES[l['job_type']][l['career_rank']]}")

    echo_text = ""
    if l["age"] in [7, 18, 30, 50]:
        n = random.choice(l["neighbors"])
        echo_text = f"\n\n👥 <b>Эхо:</b> Твой ровесник <b>{n['name']}</b> ({n['country'][1]}) — {get_neighbor_echo(n, l['age'])}."

    if random.random() < mortality_rate(l):
        save_db(players_db); return send_death(user_id, chat_id)

    if l["age"] == 6: return start_exam(user_id, chat_id, 1, "школу")
    elif l["age"] == 12: return start_exam(user_id, chat_id, 2, "колледж")
    elif l["age"] == 18: return start_exam(user_id, chat_id, 3, "университет")

    evt = get_event(l)
    if evt: 
        l["current_event"] = evt
        sc = "life"
        if "Овертайм" in evt["title"] or "Интриги" in evt["title"]: sc = "office_angry"
        elif "Кризис" in evt["title"]: sc = "sad"
        elif "Брак" in evt["title"]: sc = "love"
        elif "Развод" in evt["title"]: sc = "sad"
        elif "Мошенники" in evt["title"]: sc = "money_lose"
        elif "Лотерея" in evt["title"]: sc = "money_win"
        elif "ДПС" in evt["title"] or "езда" in evt["title"]: sc = "police"
        send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]), sc)
    else: 
        send_scene(chat_id, l, format_year(l) + echo_text, kb_focus(), "life")
    save_db(players_db)

def send_death(user_id, chat_id):
    l = players_db[str(user_id)]; l["alive"] = False; c = l["country"]
    map_text = "📜 <b>Карта жизни:</b>\n" + "\n".join([f"• {e}" for e in l["life_map"]]) if l["life_map"] else ""
    
    msg = (f"💀 <b>Ты умер в {get_age_str(l['age'])}.</b>\n"
           f"{get_stats_line(l)}\n\n"
           f"Итог: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}\n"
           f"Деньги: {fmt_money(l['clean_cash'], c)}\n\n{map_text}\n\n👥 <b>Соседи:</b>\n")
    kb = InlineKeyboardMarkup()
    for i, n in enumerate(l["neighbors"]):
        msg += f"• {n['name']} ({n['country'][1]}): {get_neighbor_final(n)}\n"
        kb.add(InlineKeyboardButton(f"🎭 Прожить жизнь {n['name']}", callback_data=f"play_{i}"))
    kb.add(InlineKeyboardButton("🎲 Начать заново", callback_data="new"))
    
    frames = get_cutscene_frames("death")
    play_cutscene(chat_id, frames, msg, kb)

def start_exam(user_id, chat_id, level, place):
    l = players_db[str(user_id)]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    school = random.choice(["Школа №1", "Гимназия", "Колледж", "Университет"])
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    bot.send_message(chat_id, f"📝 <b>Экзамен в {place}!</b>\n{school}\n\nВопрос: <b>{test['q']}</b>", reply_markup=kb, parse_mode="HTML")
    save_db(players_db)

def handle_exam_answer(user_id, chat_id, ans_idx):
    l = players_db[str(user_id)]; test = l.get("test_data")
    if not test: return
    success = (ans_idx == test["ans"]); l["test_data"] = None
    
    if l["prejudice"]:
        if "умным" in l["prejudice"] and not success:
            if random.random() < 0.4: success = True
        elif ("подозрением" in l["prejudice"] or "дикарем" in l["prejudice"]) and success:
            if random.random() < 0.4: success = False
            
    if success:
        if l["age"] == 6: l["education"] = "Начальное"; l["knowledge"] += 10; add_to_life_map(l, "Пошел в школу")
        elif l["age"] == 12: l["education"] = "Среднее"; l["knowledge"] += 15; add_to_life_map(l, "Окончил школу")
        elif l["age"] == 18: l["education"] = "Высшее"; l["knowledge"] += 25; add_to_life_map(l, "Поступил в вуз")
        msg = "✅ Экзамен сдан!"
    else: msg = "❌ Провал."
    save_db(players_db)
    send_scene(chat_id, l, msg, kb_year(), "school")

def apply_outcome(l, outcome):
    vvp = l["country"][7]
    BAD_TRAITS = ["вором", "бандитом", "скупым", "террористом", "агрессивным", "бедным", "грязным", "дикарем", "пьяницей", "алкоголиком", "фанатиком", "угнетателем", "мафией", "сепаратистом", "предателем"]
    is_bad = l["prejudice"] and any(t in l["prejudice"] for t in BAD_TRAITS)

    if outcome == "prej_fight_win": l["clean_cash"] += int(vvp*0.5); l["prejudice"] = None; l["happiness"] += 10; return "Ты сломал стереотип!"
    if outcome == "prej_fight_fail": l["clean_cash"] -= int(vvp*0.2); l["diseases"].append("ПТСР"); l["health"] -= 10; return "Ты потратил силы."
    
    if outcome == "prej_exploit":
        if is_bad: l["dirty_cash"] += int(vvp*0.8); l["happiness"] -= 5; return "Ты использовал негативный стереотип для обогащения."
        else: l["clean_cash"] += int(vvp*0.3); l["career_xp"] += 20; l["happiness"] += 5; return "Ты оседлал позитивный стереотип! Тебя повысили."
            
    if outcome == "prej_exploit_fail":
        if is_bad: l["in_prison"] = 3; l["happiness"] -= 20; return "Ты пытался провернуть махинацию и сел."
        else: l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 10; return "Ты слишком старался соответствовать и выгорел."
            
    if outcome == "prej_accept": l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 5; return "Ты смирился."
    
    if outcome == "marry": l["married"] = True; l["happiness"] += 20; l["relationships"] += 15; add_to_life_map(l, "Женился"); return "Вы поженились!"
    if outcome == "divorce": 
        l["married"] = False
        if l["clean_cash"] > 0: l["clean_cash"] = int(l["clean_cash"] / 2)
        l["happiness"] -= 15; l["relationships"] -= 20
        return "Развод."
    if outcome == "job_civ": l["job_type"] = "civilian"; l["job"] = "Работник"; l["salary"] = int(vvp * 0.6); l["relationships"] += 5; add_to_life_map(l, "На работу"); return "Ты на гражданке."
    if outcome == "job_pol": l["job_type"] = "police"; l["faction"] = "Полиция"; l["job"] = "Полицейский"; l["salary"] = int(vvp * 0.5); l["relationships"] += 10; add_to_life_map(l, "В полиции"); return "Ты в полиции."
    if outcome == "job_mil": l["job_type"] = "military"; l["faction"] = "Армия"; l["job"] = "Военный"; l["salary"] = int(vvp * 0.4); l["relationships"] += 15; add_to_life_map(l, "В армии"); return "Ты в армии."
    if outcome == "job_crim": l["job_type"] = "criminal"; l["faction"] = "Уличная банда"; l["job"] = "Бандит"; l["dirty_cash"] += int(vvp*0.5); l["happiness"] -= 10; add_to_life_map(l, "Криминал"); return "Криминал."
    if outcome == "career_xp_up": l["career_xp"] += 30; l["happiness"] -= 5; return "Переработал. XP +30."
    if outcome == "career_xp_down": l["career_xp"] -= 20; return "Ушел домой. XP -20."
    if outcome == "career_fight_win": l["career_xp"] += 40; l["happiness"] -= 5; return "Отстоял место. XP +40."
    if outcome == "career_grind": l["career_xp"] -= 10; return "Проглотил обиду. XP -10."
    if outcome == "work_extra": l["clean_cash"] += int(vvp*0.1); l["career_xp"] += 10; l["health"] -= 5; return "Вторая работа."
    if outcome == "family_time": l["career_xp"] -= 10; l["happiness"] += 10; return "Время с семьей. XP -10."
    if outcome == "burnout": l["diseases"].append("Сердечная недостаточность"); l["health"] -= 20; return "Выгорание."
    if outcome == "scammed": 
        loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss
        l["happiness"] -= 20
        return f"Украли {fmt_money(loss, l['country'])}."
    if outcome == "child_fight": l["clean_cash"] += 100; l["happiness"] += 5; return "Дал сдачи."
    if outcome == "child_tell": return "Пожаловался."
    if outcome == "teen_smoke": l["diseases"].append("Рак легких"); l["health"] -= 15; return "Курил."
    if outcome == "teen_healthy": l["clean_cash"] += 200; l["health"] += 5; return "Сэкономил."
    if outcome == "teen_love": l["happiness"] += 15; l["relationships"] += 10; return "Взаимная любовь."
    if outcome == "teen_heartbreak": l["diseases"].append("ПТСР"); l["happiness"] -= 15; l["relationships"] -= 10; return "Отказ."
    if outcome == "lottery_win": l["clean_cash"] += int(vvp * 5); l["happiness"] += 30; return "ДЖЕКПОТ!"
    if outcome == "lottery_lose": l["clean_cash"] -= 100; l["happiness"] -= 5; return "Билет пустой."
    if outcome == "bribe_dps": l["dirty_cash"] -= int(vvp*0.1); return "Взятка инспектору. Пронесло."
    if outcome == "dps_jail": l["in_prison"] = 1; l["happiness"] -= 15; return "1 год тюрьмы за езду без прав."
    if outcome == "dps_warning": return "Инспектор сделал предупреждение."
    if outcome == "bribe_dps_big": l["dirty_cash"] -= int(vvp*0.3); return "Откупился от пьяной езды."
    if outcome == "drunk_jail": l["in_prison"] = 3; l["cars"] = []; l["happiness"] -= 30; return "3 года тюрьмы + конфискация машины."
    return "Год прошел."

def resolve_choice(user_id, chat_id, i):
    l = players_db[str(user_id)]; evt = l.get("current_event")
    if not evt: return
    c = evt["choices"][i]; success = random.random() < c["p"]
    outcome = c["success"] if success else c.get("fail", "none")
    text = apply_outcome(l, outcome) if outcome else "Год прошел."
    l["last_result"] = {"success": success, "text": text}
    
    scene_map = {
        "child_fight": "fight", "child_tell": "school", "child_smart": "school", "child_walk": "child",
        "teen_love": "love", "teen_heartbreak": "sad", "teen_smoke": "sad",
        "career_xp_up": "office", "career_fight_win": "office_angry", "career_grind": "office_angry",
        "marry": "wedding", "divorce": "sad", "scammed": "money_lose", "lottery_win": "money_win", "lottery_lose": "sad",
        "job_civ": "office", "job_pol": "police", "job_mil": "military", "job_crim": "criminal",
        "prej_fight_win": "office", "prej_fight_fail": "sad", "prej_exploit": "money_win", "prej_exploit_fail": "prison", "prej_accept": "sad",
        "bribe_dps": "police", "dps_jail": "prison", "dps_warning": "police", "bribe_dps_big": "police", "drunk_jail": "prison"
    }
    
    if outcome in ["prej_exploit", "prej_exploit_fail"]:
        BAD_TRAITS = ["вором", "бандитом", "скупым", "террористом", "агрессивным", "бедным", "грязным", "дикарем", "пьяницей", "алкоголиком", "фанатиком", "угнетателем", "мафией", "сепаратистом", "предателем"]
        is_bad = l["prejudice"] and any(t in l["prejudice"] for t in BAD_TRAITS)
        if not is_bad: sc = "office" if outcome == "prej_exploit" else "sad"
        else: sc = "money_win" if outcome == "prej_exploit" else "prison"
    else:
        sc = scene_map.get(outcome, "life")
        
    save_db(players_db)
    
    if outcome == "marry":
        frames = get_cutscene_frames("marry")
        play_cutscene(chat_id, frames, format_year(l), kb_focus())
    elif outcome in ["dps_jail", "drunk_jail", "prej_exploit_fail"]:
        frames = get_cutscene_frames("prison")
        play_cutscene(chat_id, frames, format_year(l), kb_focus())
    else:
        send_scene(chat_id, l, format_year(l), kb_focus(), sc)

def format_year(l):
    c = l["country"]
    visuals = get_scene_visuals("life", l["gender"])
    parts = [f"<b>Возраст: {get_age_str(l['age'])}</b>\n{visuals}"]
    if l.get("last_result"): parts.append(f"\n{'✅' if l['last_result']['success'] else '❌'} <i>{l['last_result']['text']}</i>")
    parts.append(f"\n{get_stats_line(l)}")
    parts.append(f"\n🧬 Происхождение: <b>{l['ethnicity']}</b>")
    if l["prejudice"]: parts.append(f"⚠️ <i>Общество: {l['prejudice']}</i>")
    
    parts.append(f"💰 Баланс: <b>{fmt_money(l['clean_cash'], c)}</b>")
    if l["dirty_cash"] > 0: parts.append(f"💼 Грязные: <b>{fmt_money(l['dirty_cash'], c)}</b>")
    if l["debt"] > 0: parts.append(f"🏦 Долг: <b>{fmt_money(l['debt'], c)}</b>")
    
    parts.append(f"👑 Класс: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian", "police", "military"]:
        job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'], '')}, XP: {l['career_xp']}/100)"
    parts.append(f"💼 {job}")
    if l["properties"]: parts.append("🏠 " + ", ".join([p["type"] for p in l["properties"]]))
    if l["cars"]: parts.append("🚗 " + ", ".join([c["type"] for c in l["cars"]]))
    if l["businesses"]: parts.append("🏢 " + ", ".join([b["type"] for b in l["businesses"]]))
    if l["diseases"]: parts.append(f"🩺 {', '.join(l['diseases'])}")
    parts.append(f"🎓 {l['education']}")
    parts.append(f"👨‍👩‍👧 Дети: {l['children']} | Брак: {'Да' if l['married'] else 'Нет'}")
    return "\n".join(parts)

def format_event(l, evt): 
    visuals = get_scene_visuals("life", l["gender"])
    return f"<b>{get_age_str(l['age'])} · {evt['title']}</b>\n{visuals}\n\n{get_stats_line(l)}\n\n{evt['text']}"

def send_scene(chat_id, l, text, kb, scene_type="life"):
    if not text.startswith("<b>"): 
        visuals = get_scene_visuals(scene_type, l["gender"])
        text = f"{visuals}\n\n{text}"
    bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")

def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("▶️ Следующий год", callback_data="year")).add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
def kb_focus():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❤️ Здоровье", callback_data="focus_health"), InlineKeyboardButton("🧠 Знания", callback_data="focus_knowledge"))
    kb.add(InlineKeyboardButton("🤝 Отношения", callback_data="focus_relationships"), InlineKeyboardButton("😊 Счастье", callback_data="focus_happiness"))
    kb.add(InlineKeyboardButton("💼 Работа", callback_data="focus_work"))
    kb.add(InlineKeyboardButton("▶️ Пропустить", callback_data="year"))
    kb.add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
    return kb

def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

# ================= МАГАЗИН =================
def open_shop(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 Недвижимость", callback_data="shop_prop")).add(InlineKeyboardButton("🚗 Авто", callback_data="shop_car")).add(InlineKeyboardButton("🏢 Бизнесы", callback_data="shop_biz")).add(InlineKeyboardButton("⬅️ Назад", callback_data="year"))
    bot.send_message(chat_id, f"🛒 <b>Магазин</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")

def shop_prop_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🏠 <b>Недвижимость</b>", reply_markup=kb, parse_mode="HTML")

def shop_car_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    if not l.get("has_license"):
        lic_price = int(c[7] * 0.05)
        kb.add(InlineKeyboardButton(f"🪪 Купить права — {fmt_money(lic_price, c)}", callback_data="buy_license"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🚗 <b>Авто</b>\nНаличие прав: {'Да' if l.get('has_license') else 'Нет'}", reply_markup=kb, parse_mode="HTML")

def shop_biz_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items(): kb.add(InlineKeyboardButton(f"🏢 {name} — {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    bot.send_message(chat_id, f"🏢 <b>Бизнесы</b>", reply_markup=kb, parse_mode="HTML")

def process_buy(user_id, chat_id, cat, name):
    l = players_db[str(user_id)]; c = l["country"]
    
    if cat == "license":
        price = int(c[7] * 0.05)
        if l["clean_cash"] < price: return bot.send_message(chat_id, "❌ Мало денег на права!", reply_markup=kb_year())
        l["clean_cash"] -= price
        l["has_license"] = True
        save_db(players_db)
        return bot.send_message(chat_id, "🎉 Ты получил водительские права!", reply_markup=kb_year(), parse_mode="HTML")

    if cat == "prop": base = PROPERTIES[name]
    elif cat == "car": base = CARS[name]
    else: base = BUSINESSES[name]
    
    if l["clean_cash"] < base: return bot.send_message(chat_id, "❌ Мало денег!", reply_markup=kb_year())
    l["clean_cash"] -= base
    
    if cat == "prop": l["properties"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    elif cat == "car": l["cars"].append({"type": name, "value": base}); add_to_life_map(l, f"Купил {name}")
    else: l["businesses"].append({"type": name, "value": base}); add_to_life_map(l, f"Открыл {name}")
    
    save_db(players_db)
    bot.send_message(chat_id, f"🎉 Куплено: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= ОБРАБОТЧИКИ =================
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    text = "🎲 <b>1 из 8: Эхо</b>\n\nТы — один из 5 детей, родившихся в эту секунду. Сможешь ли ты выжить и оставить след?"
    bot.send_message(msg.chat.id, text, reply_markup=kb_intro(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id; uid_str = str(uid); chat_id = call.message.chat.id
    bot.answer_callback_query(call.id); d = call.data
    
    try:
        if d == "new":
            l = create_life()
            players_db[uid_str] = l
            add_to_life_map(l, "Родился")
            save_db(players_db)
            
            msg = f"👶 <b>Ты родился!</b>\n👤 {l['name']} ({l['country'][1]} {l['country'][0]})\n🧬 {l['ethnicity']}\n\n"
            if l["prejudice"]: msg += f"⚠️ <b>Внимание:</b> {l['prejudice']}\n\n"
            msg += f"{get_stats_line(l)}\n\n<i>Выбери свой первый фокус на год.</i>"
            
            frames = get_cutscene_frames("birth")
            play_cutscene(chat_id, frames, msg, kb_focus())
            
        elif d.startswith("focus_"):
            focus = d.replace("focus_", "")
            l = players_db[uid_str]
            l["focus"] = focus
            save_db(players_db)
            next_year(uid, chat_id)
            
        elif d == "year": 
            l = players_db[uid_str]
            l["focus"] = None
            save_db(players_db)
            next_year(uid, chat_id)
            
        elif d.startswith("job_"): 
            l = players_db[uid_str]
            text = apply_outcome(l, d)
            save_db(players_db)
            sc = "office" if "civ" in d else "police" if "pol" in d else "military" if "mil" in d else "criminal"
            send_scene(chat_id, l, text, kb_focus(), sc)
            
        elif d.startswith("choice_"): resolve_choice(uid, chat_id, int(d.split("_")[1]))
        elif d.startswith("ans_"): handle_exam_answer(uid, chat_id, int(d.split("_")[1]))
        elif d == "shop": open_shop(uid, chat_id)
        elif d == "shop_prop": shop_prop_menu(uid, chat_id)
        elif d == "shop_car": shop_car_menu(uid, chat_id)
        elif d == "shop_biz": shop_biz_menu(uid, chat_id)
        elif d == "buy_license": process_buy(uid, chat_id, "license", "")
        elif d.startswith("buy_prop_"): process_buy(uid, chat_id, "prop", d.replace("buy_prop_", ""))
        elif d.startswith("buy_car_"): process_buy(uid, chat_id, "car", d.replace("buy_car_", ""))
        elif d.startswith("buy_biz_"): process_buy(uid, chat_id, "biz", d.replace("buy_biz_", ""))
        
        elif d.startswith("play_"):
            idx = int(d.split("_")[1])
            n = players_db[uid_str]["neighbors"][idx]
            l = create_life(force_country=n["country"]); l["name"] = n["name"]
            players_db[uid_str] = l
            add_to_life_map(l, "Родился (смена судьбы)")
            save_db(players_db)
            
            msg = f"🎭 <b>Новая судьба!</b>\nТы теперь {l['name']} ({l['country'][1]}).\n\n{get_stats_line(l)}"
            frames = get_cutscene_frames("birth")
            play_cutscene(chat_id, frames, msg, kb_focus())
            
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {e}. Попробуйте нажать еще раз.")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
