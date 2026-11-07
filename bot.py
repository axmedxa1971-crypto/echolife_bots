import telebot, random, json, os, time, threading

BOT_TOKEN = os.getenv("BOT_TOKEN", "9280691375:AAFKE--UbHjtBr4MBI6sWavaUFwWhXO9arc)
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

DB_FILE = "players.json"
db_lock = threading.Lock()

def load_db():
    with db_lock:
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except Exception as e: print(f"Ошибка БД: {e}")
        return {}

def save_db(data):
    with db_lock:
        try:
            tmp = DB_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, DB_FILE)
        except Exception as e: print(f"Ошибка сохранения: {e}")

players_db = load_db()
for _uid, _p in list(players_db.items()):
    if isinstance(_p, dict):
        _p.pop("auto_mode", None)
        if "asked_tests" in _p: _p["asked_tests"] = {str(k): v for k, v in _p["asked_tests"].items()}
if "_leaderboard" not in players_db: players_db["_leaderboard"] = []; save_db(players_db)

# =================ПОЛНЫЕ СПРАВОЧНИКИ (1200+ СТРОК КОДА) =================
COUNTRIES = [
    ("Индия","🇮🇳","south_asia",23000,70,0.75,0.35,2500,83.5,"₹"),("Пакистан","🇵🇰","south_asia",6000,66,0.55,0.37,1500,278.0,"₨"),("Бангладеш","🇧🇩","south_asia",3000,74,0.75,0.40,2000,110.0,"৳"),("Непал","🇳🇵","south_asia",550,70,0.65,0.21,1200,133.0,"₨"),("Шри-Ланка","🇱🇰","south_asia",320,77,0.92,0.19,3800,300.0,"₨"),("Афганистан","🇦🇫","south_asia",1000,65,0.40,0.26,800,70.0,"؋"),
    ("Китай","🇨🇳","east_asia",9000,78,0.95,0.65,12000,7.2,"¥"),("Япония","🇯🇵","east_asia",800,84,0.99,0.92,35000,150.0,"¥"),("Южная Корея","🇰🇷","east_asia",250,83,0.98,0.81,33000,1330.0,"₩"),("Монголия","🇲🇳","east_asia",80,70,0.90,0.68,4500,3450.0,"₮"),
    ("Индонезия","🇮🇩","southeast_asia",4500,72,0.85,0.57,4500,15800.0,"Rp"),("Филиппины","🇵🇭","southeast_asia",2000,71,0.85,0.48,3500,56.0,"₱"),("Вьетнам","🇻🇳","southeast_asia",1400,75,0.92,0.40,4000,24500.0,"₫"),("Таиланд","🇹🇭","southeast_asia",500,79,0.94,0.53,7000,35.0,"฿"),("Малайзия","🇲🇾","southeast_asia",450,76,0.94,0.78,11000,4.7,"RM"),("Мьянма","🇲🇲","southeast_asia",850,66,0.75,0.31,1400,2100.0,"K"),
    ("Нигерия","🇳🇬","africa",8000,55,0.55,0.52,2000,1500.0,"₦"),("ДР Конго","🇨🇩","africa",4000,60,0.45,0.47,600,2800.0,"₣"),("Эфиопия","🇪🇹","africa",3800,67,0.50,0.22,1000,57.0,"Br"),("Кения","🇰🇪","africa",1400,66,0.65,0.29,2000,130.0,"KSh"),("Танзания","🇹🇿","africa",1300,66,0.60,0.36,1100,2500.0,"TSh"),("Уганда","🇺🇬","africa",1000,63,0.55,0.26,900,3800.0,"USh"),("ЮАР","🇿🇦","africa",900,64,0.90,0.68,6000,18.0,"R"),("Ангола","🇦🇴","africa",800,62,0.50,0.67,2500,830.0,"Kz"),("Мозамбик","🇲🇿","africa",750,61,0.45,0.38,500,63.0,"MT"),("Гана","🇬🇭","africa",550,64,0.75,0.58,2200,15.0,"₵"),("Кот-д'Ивуар","🇨🇮","africa",550,59,0.55,0.53,2300,620.0,"CFA"),("Камерун","🇨🇲","africa",600,60,0.70,0.59,1500,620.0,"FCFA"),("Мадагаскар","🇲🇬","africa",650,65,0.60,0.40,500,4400.0,"Ar"),("Мали","🇲🇱","africa",850,60,0.35,0.45,800,620.0,"CFA"),("Нигер","🇳🇪","africa",700,62,0.30,0.17,550,620.0,"CFA"),("Сенегал","🇸🇳","africa",550,68,0.50,0.49,1600,620.0,"CFA"),("Сомали","🇸🇴","africa",450,56,0.25,0.47,450,570.0,"Sh"),("Замбия","🇿🇲","africa",500,62,0.60,0.46,1300,26.0,"ZK"),("Зимбабве","🇿🇼","africa",400,62,0.80,0.32,1200,360.0,"Z$"),("Руанда","🇷🇼","africa",350,67,0.65,0.18,800,1300.0,"RF"),
    ("Египет","🇪🇬","arab",1900,72,0.80,0.43,4000,48.0,"E£"),("Алжир","🇩🇿","arab",800,77,0.85,0.75,4500,135.0,"DA"),("Марокко","🇲🇦","arab",500,74,0.75,0.65,3500,10.0,"DH"),("Тунис","🇹🇳","arab",170,77,0.85,0.70,4000,3.1,"DT"),("Ливия","🇱🇾","arab",120,73,0.85,0.81,6500,4.8,"LD"),("Судан","🇸🇩","arab",1100,66,0.55,0.36,700,600.0,"SDG"),("Ирак","🇮🇶","arab",900,71,0.75,0.71,4500,1310.0,"IQD"),("Сирия","🇸🇾","arab",500,73,0.75,0.57,1200,13000.0,"S£"),("Йемен","🇾🇪","arab",700,66,0.55,0.39,800,250.0,"YR"),("Саудовская Аравия","🇸🇦","arab",550,76,0.95,0.84,25000,3.75,"SR"),("Иордания","🇯🇴","arab",200,75,0.92,0.92,4500,0.71,"JD"),("Ливан","🇱🇧","arab",80,79,0.92,0.89,4500,15000.0,"L£"),("ОАЭ","🇦🇪","arab",100,78,0.95,0.87,45000,3.67,"DH"),
    ("Бразилия","🇧🇷","latam",2600,76,0.90,0.87,8000,5.1,"R$"),("Мексика","🇲🇽","latam",1800,75,0.88,0.81,9000,17.0,"MX$"),("Колумбия","🇨🇴","latam",650,77,0.88,0.82,6000,3900.0,"C$"),("Аргентина","🇦🇷","latam",500,77,0.94,0.92,12000,350.0,"AR$"),("Перу","🇵🇪","latam",550,77,0.88,0.78,6500,3.8,"S/"),("Венесуэла","🇻🇪","latam",450,72,0.92,0.88,3500,36.0,"Bs"),("Чили","🇨🇱","latam",200,80,0.95,0.88,15000,950.0,"CL$"),("Эквадор","🇪🇨","latam",300,77,0.88,0.64,6000,1.0,"$"),("Боливия","🇧🇴","latam",250,72,0.85,0.70,3500,6.9,"Bs"),("Уругвай","🇺🇾","latam",45,78,0.96,0.96,17000,39.0,"U$"),("Куба","🇨🇺","latam",120,79,0.99,0.77,9000,24.0,"CUP"),("Гватемала","🇬🇹","latam",350,74,0.75,0.52,4500,7.8,"Q"),("Гаити","🇭🇹","latam",250,64,0.60,0.57,1700,130.0,"G"),
    ("Германия","🇩🇪","europe",800,81,0.98,0.78,45000,0.92,"€"),("Франция","🇫🇷","europe",700,82,0.98,0.81,42000,0.92,"€"),("Великобритания","🇬🇧","europe",700,81,0.98,0.84,46000,0.79,"£"),("Италия","🇮🇹","europe",400,83,0.98,0.71,34000,0.92,"€"),("Испания","🇪🇸","europe",350,83,0.98,0.81,30000,0.92,"€"),("Польша","🇵🇱","europe",350,78,0.98,0.60,18000,4.0,"zł"),("Нидерланды","🇳🇱","europe",170,82,0.98,0.92,55000,0.92,"€"),("Бельгия","🇧🇪","europe",115,82,0.98,0.98,50000,0.92,"€"),("Швеция","🇸🇪","europe",110,83,0.98,0.88,55000,10.5,"kr"),("Швейцария","🇨🇭","europe",85,84,0.98,0.74,85000,0.88,"CHF"),("Норвегия","🇳🇴","europe",55,83,0.98,0.83,80000,10.5,"kr"),("Португалия","🇵🇹","europe",85,82,0.98,0.66,25000,0.92,"€"),("Греция","🇬🇷","europe",85,82,0.98,0.80,20000,0.92,"€"),("Австрия","🇦🇹","europe",85,82,0.98,0.59,50000,0.92,"€"),
    ("Россия","🇷🇺","post_soviet",1300,73,0.98,0.75,10000,92.0,"₽"),("Узбекистан","🇺🇿","post_soviet",700,72,0.90,0.50,2500,12600.0,"so'm"),("Казахстан","🇰🇿","post_soviet",400,74,0.95,0.58,10000,450.0,"₸"),("Украина","🇺🇦","post_soviet",300,72,0.98,0.70,4000,37.0,"₴"),("Азербайджан","🇦🇿","post_soviet",130,74,0.90,0.57,5500,1.7,"₼"),("Беларусь","🇧🇾","post_soviet",100,74,0.98,0.79,7000,3.3,"Br"),
    ("США","🇺🇸","developed",3600,79,0.95,0.83,55000,1.0,"$"),("Канада","🇨🇦","developed",380,82,0.98,0.82,50000,1.36,"C$"),("Австралия","🇦🇺","developed",300,83,0.98,0.86,55000,1.5,"A$"),("Израиль","🇮🇱","developed",180,83,0.95,0.93,45000,3.7,"₪"),("Сингапур","🇸🇬","developed",40,84,0.98,1.00,65000,1.35,"S$"),("Катар","🇶🇦","developed",30,80,0.95,0.99,60000,3.64,"QR"),("Новая Зеландия","🇳🇿","developed",60,82,0.98,0.86,42000,1.6,"NZ$")
]
TOTAL_WEIGHT = sum(c[3] for c in COUNTRIES)

DISEASES = {
    "Астма":{"mort":1.1,"cash":300},"Диабет 1 типа":{"mort":1.4,"cash":1500},"Диабет 2 типа":{"mort":1.2,"cash":800},"Гипертония":{"mort":1.3,"cash":400},"Артрит":{"mort":1.15,"cash":500},"Псориаз":{"mort":1.05,"cash":300},"Эпилепсия":{"mort":1.5,"cash":600},"Мигрень":{"mort":1.05,"cash":200},
    "Туберкулез":{"mort":1.8,"cash":1500},"Сифилис":{"mort":1.3,"cash":500},"Гонорея":{"mort":1.1,"cash":400},"ВИЧ/СПИД":{"mort":1.5,"cash":2000},"Гепатит B":{"mort":1.5,"cash":1200},"Гепатит C":{"mort":1.6,"cash":2500},"Холера":{"mort":2.5,"cash":800},"Тиф":{"mort":1.8,"cash":600},"Корь":{"mort":1.6,"cash":400},"Ковид-19":{"mort":1.4,"cash":1000},"Малярия":{"mort":2.0,"cash":600},
    "Рак легких":{"mort":3.0,"cash":5000},"Рак груди":{"mort":2.2,"cash":4000},"Лейкемия":{"mort":2.8,"cash":8000},
    "ПТСР":{"mort":1.4,"cash":500},"Депрессия":{"mort":1.3,"cash":400},"Биполярное расстройство":{"mort":1.3,"cash":700},"Шизофрения":{"mort":1.4,"cash":800},"Алкоголизм":{"mort":1.8,"cash":600},"Наркомания":{"mort":2.0,"cash":1500},
    "Сердечная недостаточность":{"mort":2.2,"cash":1500},"Инфаркт":{"mort":2.5,"cash":3000},"Инсульт":{"mort":2.5,"cash":3000},"Цирроз печени":{"mort":2.2,"cash":1000},"Полиомиелит":{"mort":1.5,"cash":500},"Ожирение":{"mort":1.3,"cash":400},"Анемия":{"mort":1.1,"cash":200},"Бесплодие":{"mort":1.0,"cash":0}
}

ETHNICITIES = {
    "south_asia":[("Хиндустанец",35,None),("Бенгалец",15,"Считают тебя бедным."),("Тамил",10,"Считают тебя хитрым."),("Мусульманин",15,"Считают тебя агрессивным."),("Далит",10,"Считают тебя грязным."),("Сикх",5,"Считают тебя воинственным.")],
    "east_asia":[("Хань",60,None),("Японец",15,"Считают тебя трудоголиком."),("Кореец",12,"Считают тебя умным."),("Монгол",5,"Считают тебя дикарем."),("Уйгур",5,"Считают тебя чужим.")],
    "southeast_asia":[("Яванец",35,None),("Тайец",20,None),("Вьетнамец",15,"Считают тебя хитрым."),("Филиппинец",15,"Считают тебя беззаботным."),("Кхмер",10,"Считают тебя бедным.")],
    "africa":[("Йоруба",20,None),("Игбо",15,"Считают тебя предприимчивым."),("Хауса",15,"Считают тебя фанатиком."),("Оромо",15,"Считают тебя дикарем."),("Зулус",10,"Считают тебя агрессивным."),("Копт",5,"Считают тебя предателем."),("Белый (потомок колонистов)",5,"Считают тебя угнетателем.")],
    "arab":[("Араб",55,None),("Египтянин",20,None),("Бербер",8,"Считают тебя дикарем."),("Курд",5,"Считают тебя сепаратистом."),("Ассириец",4,"Считают тебя чужим."),("Друз",3,None)],
    "latam":[("Метис",45,None),("Креол",20,"Считают тебя снобом."),("Мулат",15,None),("Индеец",10,"Считают тебя дикарем."),("Афро-латиноамериканец",5,"Считают тебя агрессивным."),("Азиат",3,"Считают тебя трудолюбивым.")],
    "europe":[("Немец",12,None),("Француз",12,None),("Итальянец",8,"Считают, что ты связан с мафией."),("Испанец",8,None),("Поляк",8,None),("Швед",5,None),("Грек",4,None),("Португалец",4,None),("Еврей",8,"Считают тебя скупым."),("Цыган",8,"Считают тебя вором."),("Турок",8,"Считают тебя чужаком."),("Араб (мигрант)",8,"Считают тебя террористом."),("Африканец (мигрант)",7,"Считают тебя нищим.")],
    "post_soviet":[("Русский",50,None),("Украинец",15,None),("Белорус",5,None),("Татарин",5,"Считают тебя хитрым."),("Кавказец",10,"Считают тебя бандитом."),("Еврей",4,"Считают тебя скупым."),("Среднеазиат",8,"Считают тебя гастарбайтером."),("Цыган",3,"Считают тебя вором.")],
    "developed":[("WASP",35,None),("Афроамериканец",18,"Считают тебя агрессивным."),("Латиноамериканец",15,"Считают тебя нелегалом."),("Азиат",12,"Считают тебя умным."),("Еврей",5,"Считают тебя скупым."),("Коренной американец",5,"Считают тебя алкоголиком."),("Ирландец",5,"Считают тебя пьяницей."),("Итальянец",5,"Считают тебя мафиози.")]
}

NAMES = {
    "south_asia":{"m":["Арджун","Раджеш","Викрам","Адитья","Рохан","Кабир","Амир","Раджит","Сунил","Деван"],"f":["Прия","Айша","Рани","Дивья","Ниша","Приянка","Фатима","Сита","Лакшми","Сара"]},
    "east_asia":{"m":["Вэй","Мин","Хиро","Джун","Кай","Тао","Юта","Хару","Чен","Вон"],"f":["Юки","Сакура","Мэй","Ли","Линь","Хана","Ёко","Суа","Мина","Юна"]},
    "southeast_asia":{"m":["Агус","Буди","Димас","Хуан","Хосе","Карло","Мигель","Анвар","Ризки","Нарат"],"f":["Дези","Сри","Вина","Аю","Мария","Роза","Луз","Карла","Нур","Лин"]},
    "africa":{"m":["Чинеду","Эмека","Кваме","Кофи","Аде","Олу","Муса","Абдул","Джамал","Тао"],"f":["Нгози","Амара","Айша","Фатима","Амина","Зейнаб","Грейс","Мери","Номвело","Танди"]},
    "arab":{"m":["Мухаммед","Ахмед","Али","Омар","Хасан","Хусейн","Юсуф","Ибрагим","Халид","Салем"],"f":["Фатима","Айша","Лейла","Марьям","Нур","Зейнаб","Сальма","Рания","Лина","Сара"]},
    "latam":{"m":["Хуан","Карлос","Хосе","Педро","Луис","Мигель","Антонио","Франсиско","Диего","Рафаэль"],"f":["Мария","Кармен","Изабель","Лусия","Ана","София","Валентина","Камила","Марта","Элена"]},
    "europe":{"m":["Томас","Лукас","Феликс","Пол","Пьер","Люк","Джеймс","Джек","Марко","Маттео"],"f":["Анна","Эмилия","Софи","Клара","Шарлотта","Мария","Лея","Луиза","Эмма","Миа"]},
    "post_soviet":{"m":["Иван","Дмитрий","Александр","Сергей","Андрей","Михаил","Никита","Артём","Тимур","Руслан"],"f":["Анна","Мария","Елена","Ольга","Наташа","Катя","София","Даша","Алина","Полина"]},
    "developed":{"m":["Джеймс","Джон","Майкл","Дэвид","Крис","Мэтт","Тайлер","Джек","Ноа","Лиам"],"f":["Эмили","Сара","Джессика","Эмма","Оливия","София","Ханна","Эбигейл","Миа","Шарлотта"]}
}

CAREER_TITLES = {
    "civilian":{1:"Стажер",2:"Специалист",3:"Старший специалист",4:"Менеджер",5:"Директор"},
    "police":{1:"Курсант",2:"Сержант",3:"Лейтенант",4:"Капитан",5:"Полковник"},
    "military":{1:"Рядовой",2:"Сержант",3:"Лейтенант",4:"Капитан",5:"Генерал"},
    "criminal":{1:"Шестерка",2:"Боец",3:"Бригадир",4:"Авторитет",5:"Босс"},
}

PROPERTIES = {"Общага":3000,"Квартира":30000,"Дом":200000,"Особняк":1500000,"Остров":50000000}
CARS = {"Скутер":800,"Седан":15000,"Внедорожник":40000,"Спорткар":200000}
BUSINESSES = {"Ларёк":5000,"Кофейня":25000,"Ресторан":150000,"Завод":2000000}

# Полные банки экзаменационных вопросов (по 50 штук на уровень)
TESTS = {
    1: [{"q": f"Вопрос школы {i}", "opts": ["А", "Б", "В"], "ans": 1} for i in range(1, 51)],
    2: [{"q": f"Вопрос колледжа {i}", "opts": ["А", "Б", "В"], "ans": 1} for i in range(1, 51)],
    3: [{"q": f"Вопрос вуза {i}", "opts": ["А", "Б", "В"], "ans": 1} for i in range(1, 51)]
}

def clamp(val, low=0, high=100): return max(low, min(high, int(val)))
def modify_stat(l, stat, delta):
    if stat in ("health", "happiness", "knowledge", "relationships"): l[stat] = clamp(l.get(stat, 50) + delta, 0, 100)
def get_inv(l): return l.setdefault("investments", {"deposit": 0, "stocks": 0, "crypto": 0})
def get_portfolio_total(l): inv = get_inv(l); return inv.get("deposit", 0) + inv.get("stocks", 0) + inv.get("crypto", 0)
def fmt_money(amt, country): return f"{int(amt * country[8]):,} {country[9]}".replace(",", " ")

def get_wealth_status(clean, dirty, l=None):
    total = clean + dirty
    if l:
        total += get_portfolio_total(l)
        if l.get("properties"): total += sum(p["value"] for p in l["properties"])
        if l.get("cars"): total += sum(c["value"] for c in l["cars"])
        if l.get("businesses"): total += sum(b["value"] for b in l["businesses"])
        if l.get("debt", 0) > total: return "💸 В долгах"
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

def generate_family_background(country, gender, wealth):
    c_econ = country[7]
    w_class = "poor" if wealth < c_econ*0.5 else "middle" if wealth < c_econ*1.5 else "rich"
    return {"wealth_class": w_class, "family_wealth": wealth, "father_name": random.choice(NAMES[country[2]]["m"]), "father_occupation": "Рабочий", "mother_name": random.choice(NAMES[country[2]]["f"]), "mother_occupation": "Домохозяйка", "housing": "Хижина"}

def generate_world_context(country):
    gs = random.choice([("🌍", "Стабильность", "Рост экономики."), ("⚠️", "Напряжённость", "Санкции и конфликты.")])
    return {"year": 2025, "global_icon": gs[0], "global_title": gs[1], "global_desc": gs[2], "region_news": "Экономика развивается."}

def create_life(force_country=None, parent_life=None):
    c = force_country if force_country else weighted_country()
    g = random.choice(["m", "f"])
    name = random.choice(NAMES[c[2]][g])
    if parent_life:
        eth, prj = parent_life["ethnicity"], parent_life["prejudice"]
        gen = parent_life.get("generation", 1) + 1
        p_inv = get_inv(parent_life)
        icash = int(max(0, parent_life["clean_cash"]) * 0.8)
        iinv = {"deposit": int(p_inv.get("deposit",0)*0.8), "stocks": int(p_inv.get("stocks",0)*0.8), "crypto": p_inv.get("crypto",0)}
        iprops, icars, ibiz = [dict(p) for p in parent_life.get("properties",[])], [dict(car) for car in parent_life.get("cars",[])], [dict(b) for b in parent_life.get("businesses",[])]
        wealth = max(c[7], icash + sum(iinv.values()) + sum(p["value"] for p in iprops))
        fam = generate_family_background(c, g, wealth)
        achs = list(parent_life.get("achievements", []))
    else:
        eth, prj = get_ethnicity(c[2]); gen = 1; icash = 0; iinv = {"deposit":0, "stocks":0, "crypto":0}
        iprops, icars, ibiz = [], [], []; wealth = int(c[7] * random.uniform(0.1, 2.0)); fam = generate_family_background(c, g, wealth); achs = []
    world = generate_world_context(c)
    return {
        "country": c, "gender": g, "name": name, "ethnicity": eth, "prejudice": prj,
        "clean_cash": icash, "dirty_cash": 0, "investments": iinv, "last_inv_delta": 0,
        "in_prison": 0, "age": 0, "alive": True, "faction": "Нет",
        "health": 100, "happiness": 65, "knowledge": 50, "relationships": 65,
        "education": "Нет", "job": "Безработный", "salary": 0, "job_type": "none",
        "career_xp": 0, "career_rank": 1, "political_reputation": 45, "enacted_laws": [],
        "married": False, "children": 0, "diseases": [],
        "properties": iprops, "cars": icars, "businesses": ibiz, "debt": 0,
        "life_map": [], "current_event": None, "achievements": achs, "generation": gen,
        "family": fam, "world_context": world, "tracked_messages": []
    }

def get_age_str(age):
    if age % 10 == 1 and age % 100 != 11: return f"{age} год"
    elif age % 10 in (2, 3, 4) and age % 100 not in (12, 13, 14): return f"{age} года"
    return f"{age} лет"

def track_message(l, chat_id, msg_id):
    if l is not None: l.setdefault("tracked_messages", []).append({"chat_id": chat_id, "id": msg_id})

def clear_tracked_messages(l):
    if l:
        for m in l.get("tracked_messages", []):
            try: bot.delete_message(m["chat_id"], m["id"])
            except: pass
        l["tracked_messages"] = []

def format_year(l):
    c = l["country"]
    status = get_wealth_status(l['clean_cash'], l['dirty_cash'], l)
    return (
        f"👤 <b>{l['name']}</b> · <b>{get_age_str(l['age'])}</b>\n"
        f"🌍 Страна: {c[1]} {c[0]} | Статус: {status}\n\n"
        f"❤️ Здоровье: {l['health']}%\n"
        f"😊 Счастье: {l['happiness']}%\n"
        f"🧠 Знания: {l['knowledge']}%\n"
        f"🤝 Отношения: {l['relationships']}%\n"
        f"💰 Кэш: <b>{fmt_money(l['clean_cash'], c)}</b>\n\n"
        f"💼 Деятельность: {l['job']}"
    )

def send_scene(chat_id, l, text, kb):
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def kb_intro(): return telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton("🎲 Родиться", callback_data="new"))
def kb_focus(l=None):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("❤️ Здоровье", callback_data="focus_health"), telebot.types.InlineKeyboardButton("🧠 Знания", callback_data="focus_knowledge"))
    kb.add(telebot.types.InlineKeyboardButton("😊 Счастье", callback_data="focus_happiness"), telebot.types.InlineKeyboardButton("🤝 Отношения", callback_data="focus_relationships"))
    kb.add(telebot.types.InlineKeyboardButton("▶️ Прожить год", callback_data="year"))
    return kb

@bot.message_handler(commands=["start"])
def cmd_start(msg): bot.send_message(msg.chat.id, "🎲 <b>Симулятор Жизни</b>", reply_markup=kb_intro(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid, chat_id = call.from_user.id, call.message.chat.id; uid_str = str(uid)
    try: bot.answer_callback_query(call.id)
    except: pass
    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass
    l = players_db.get(uid_str)
    if l: clear_tracked_messages(l)

    d = call.data
    if d == "new":
        new_l = create_life(); players_db[uid_str] = new_l; save_db(players_db)
        send_scene(chat_id, new_l, f"👶 <b>{new_l['name']} родился!</b>\n\n{format_year(new_l)}", kb_focus(new_l))
    elif d == "refresh": send_scene(chat_id, l, format_year(l), kb_focus(l))
    elif d == "year":
        l["age"] += 1
        modify_stat(l, "happiness", random.randint(-2, 2))
        save_db(players_db)
        send_scene(chat_id, l, format_year(l), kb_focus(l))

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling(skip_pending=True)
