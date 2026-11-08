import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, players_db, save_db
from utils import (
    get_age_str, track_message, clear_tracked_messages, fmt_money,
    get_wealth_status, get_stats_line, get_scene_visuals, get_cutscene_frames, play_cutscene
)
from data.countries import COUNTRIES, TOTAL_WEIGHT, ETHNICITIES, NAMES
from data.items import (
    DISEASES, CURABLE_DISEASES, CAREER_TITLES, PROPERTIES, CARS, BUSINESSES,
    INVESTMENT_ASSETS, BAD_TRAITS_LOCAL, ACHIEVEMENTS, NPC_ROLES_DESC, EDU_INSTITUTIONS
)
from data.tests import TESTS
from data.events import (
    FOCUS_EVENTS, CHILD_EVENTS, TEEN_EVENTS, WORLD_EVENTS, LIFE_TWISTS, adult_events_for
)
from keyboards import (
    kb_intro, kb_year, kb_focus, kb_event,
    open_shop, shop_prop_menu, shop_car_menu, shop_biz_menu, shop_invest_menu
)

def pick_rotating(l, pool, max_recent=6):
    if not pool:
        return {"id":"fallback","title":"📅 Обычный год","text":"Ничего особенного.",
                "choices":[{"text":"Продолжить","p":1,"success_effect":{"text":"Спокойный год."}}]}
    seen = l.setdefault("seen_regular_events", [])
    recent = seen[-max_recent:] if len(seen) >= max_recent else seen
    available = [e for e in pool if e.get("id") not in recent]
    if not available: available = pool
    weights = [e.get("weight", 1.0) for e in available]
    evt = random.choices(available, weights=weights, k=1)[0]
    if evt.get("id"):
        seen.append(evt["id"])
        if len(seen) > 80: l["seen_regular_events"] = seen[-60:]
    return evt

def play_cutscene(chat_id, l, frames, final_text, kb=None):
    msg = bot.send_message(chat_id, frames[0], parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)
    for frame in frames[1:]:
        time.sleep(1.2)
        try: bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="HTML")
        except: pass
    time.sleep(1.2)
    try: bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=final_text, reply_markup=kb, parse_mode="HTML")
    except: bot.send_message(chat_id, final_text, reply_markup=kb, parse_mode="HTML")

def get_cutscene_frames(event_type):
    if event_type == "birth": return ["🏥 👨‍⚕️ 🤰\n<i>Врачи готовятся...</i>","👶 ✨ 👨‍👩‍👦\n<i>Раздается первый крик!</i>","🎉 🍼 🧸\n<i>Новая жизнь началась!</i>"]
    if event_type == "marry": return ["💐 🍷 👩‍❤️‍👨\n<i>Романтический ужин...</i>","🤵 👰 💍\n<i>Предложение руки и сердца!</i>","🥂 🎉 💖\n<i>Свадьба!</i>"]
    if event_type == "prison": return ["🚔 🚨 🏃‍♂️\n<i>Погоня...</i>","👮‍♂️ 🔗 👨\n<i>Задержание...</i>","⛓ 🧱 🚪\n<i>Дверь камеры захлопнулась.</i>"]
    if event_type == "death": return ["🏥 🛌 💔\n<i>Здоровье подводит...</i>","🕯️ ☁️\n<i>Последний вздох...</i>","🪦 🥀 🕊️\n<i>Жизнь окончена.</i>"]
    return []

def get_scene_visuals(scene_type, gender):
    male = ["👦","🧑","👨","🧔","👨‍💼","👨‍💻","👨‍🎓"]
    female = ["👧","👩","👩‍🦰","👩‍🦱","👩‍💼","👩‍💻","👩‍🎓"]
    player = random.choice(male) if gender == "m" else random.choice(female)
    scenes = {"military":f"🎖 🪖 {player} 🪖 🛡","criminal":f"🕶 🔫 {player} 💰 💣","child":f"🏠 🌳 {player} 🧸 ☀️","toddler":f"🍼 🧸 {player} 🎈 🌟","school":f"🏫 {player} 📚 🎒 🍎","rich":f"🏰 🚗 💰 {player} 🥂 🛥","office":f"🏢 🧑‍💻 {player} 📊 ☕","office_angry":f"🏢 😡 {player} 💢 📉","hospital":f"🏥 🛌 {player} 💉 🩺","prison":f"⛓ 🧱 {player} 🚔 🕶","fight":f"👊 💥 {player} 🥊 🤕","love":f"❤️ {player} 🌹 💑 💐","wedding":f"💍 🤵 👰 {player} 🎉","sad":f"🌧 {player} ☂️ 😔 💧","police":f"🚔 💵 {player} 🚨 😰","money_win":f"💰 🤑 {player} 💎 🎰","money_lose":f"💸 😭 {player} 🕳 📉"}
    return scenes.get(scene_type, f"🌆 {player} 🏙 🚶")

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
    for name, chance, prejudice in ETHNICITIES.get(region, [("Местный",100,None)]):
        cum += chance
        if r <= cum: return name, prejudice
    return "Местный", None

def generate_neighbors(count=3):
    neighbors = []
    for _ in range(count):
        c = weighted_country(); g = random.choice(["m","f"])
        name = random.choice(NAMES[c[2]][g])
        trajectory = random.choice(["prosperous","criminal","ordinary","unfortunate"])
        if trajectory == "criminal": death_age = random.randint(20,45)
        elif trajectory == "unfortunate": death_age = random.randint(1,15)
        else:
            death_age = int(random.gauss(c[4], 10))
            if death_age < 1: death_age = random.randint(1,5)
        neighbors.append({"name":name,"country":c,"gender":g,"trajectory":trajectory,"death_age":death_age})
    return neighbors

def generate_peer_lives(count=4):
    peer_lives = []
    for _ in range(count):
        pc = weighted_country(); pg = random.choice(["m","f"])
        pname = random.choice(NAMES[pc[2]][pg])
        peer_lives.append({"name":pname,"country":pc,"gender":pg,"trajectory":random.choice(["prosperous","criminal","ordinary","unfortunate"]),"death_age":random.randint(1,90)})
    return peer_lives

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

# ================= NPC И ПРЕДЫСТОРИЯ =================
def create_key_npcs(country, gender, family=None):
    if family:
        mother_name = family["mother_name"]; father_name = family["father_name"]
    else:
        mother_name = random.choice(NAMES[country[2]]["f"]); father_name = random.choice(NAMES[country[2]]["m"])
    friend_name = random.choice(NAMES[country[2]][gender])
    rival_gender = "f" if gender == "m" else "m"
    rival_name = random.choice(NAMES[country[2]][rival_gender])
    return [
        {"role":"mother","name":mother_name,"relation":70,"memories":[],"dead":False,"death_age":random.randint(60,90)},
        {"role":"father","name":father_name,"relation":60,"memories":[],"dead":False,"death_age":random.randint(55,85)},
        {"role":"friend","name":friend_name,"relation":50,"memories":[],"dead":False,"death_age":random.randint(50,90)},
        {"role":"rival","name":rival_name,"relation":0,"memories":[],"dead":False,"death_age":random.randint(40,85)},
    ]

def get_npc_by_role(l, role):
    for npc in l.get("key_npcs", []):
        if npc["role"] == role: return npc
    return None

def check_npc_deaths(l):
    for npc in l.get("key_npcs", []):
        if not npc["dead"] and l["age"] >= npc.get("death_age", 999):
            npc["dead"] = True
            role_ru = NPC_ROLES_DESC.get(npc["role"], npc["role"])
            add_to_life_map(l, f"Умер(ла) {role_ru} {npc['name']}")
            if npc["role"] in ("mother","father","friend"):
                l["happiness"] = max(0, l["happiness"] - 5)

def get_npc_epilogue(npc):
    role_ru = NPC_ROLES_DESC.get(npc["role"], npc["role"])
    fate = f"умер(ла) в {get_age_str(npc['death_age'])}" if npc["dead"] else "жив(а)"
    rel = npc["relation"]
    if rel >= 60: mood = "был(а) рядом"
    elif rel >= 20: mood = "тёплые отношения"
    elif rel >= -20: mood = "нейтрально"
    else: mood = "испортились"
    return f"• {role_ru} {npc['name']}: {fate} — {mood}"

def generate_world_context(country):
    year = 2025 + random.randint(-5, 5)
    global_states = [
        {"icon":"🌍","title":"Относительная стабильность","desc":"Нет крупных войн. Экономика растёт."},
        {"icon":"⚠️","title":"Глобальная напряжённость","desc":"Санкции, конфликты, гонка вооружений."},
        {"icon":"📈","title":"Экономический подъём","desc":"Рынки растут, новые технологии."},
        {"icon":"📉","title":"Мировой кризис","desc":"Инфляция, безработица."},
        {"icon":"🦠","title":"После пандемии","desc":"Мир восстанавливается."},
    ]
    global_state = random.choice(global_states)
    region_news = {
        "south_asia":["🌾 Аграрный сектор модернизируется.","🏙 Города растут стремительно.","⚖️ Борьба с бедностью.","🚂 Новые железные дороги."],
        "east_asia":["🏭 Автоматизация сокращает рабочие места.","🚀 Технологический бум.","👴 Старение населения.","📱 Мобильные платежи."],
        "southeast_asia":["🏖 Туризм приносит деньги.","🏗 Строительство инфраструктуры.","💼 Многие уезжают за границу.","🌊 Наводнения."],
        "africa":["🌍 Молодое население.","💎 Богатые ресурсы.","⚔️ В некоторых регионах неспокойно.","📚 Растёт доступ к образованию."],
        "arab":["🛢 Нефть — главный ресурс.","🏙 Дубай — символ богатства.","⚖️ Меняющиеся традиции.","🌞 Солнечная энергетика."],
        "latam":["💃 Живая культура.","⚠️ Преступность в городах.","🌳 Вырубка лесов.","🎭 Фестивали."],
        "europe":["🇪🇺 Единство и стабильность.","♻️ Зелёная энергетика.","👴 Старение и миграция.","🚄 Скоростные поезда."],
        "post_soviet":["🏚 Наследие СССР.","💼 Молодёжь ищет работу.","📺 Влияние государства.","🛣 Строительство дорог."],
        "developed":["💻 Технологии меняют жизнь.","🏥 Доступная медицина.","🎓 Высокий уровень образования.","🚗 Электромобили."],
    }
    positive_news = ["🎉 Спортивные игры.","🏆 Важное открытие.","🌾 Хороший урожай.","🛣 Новая магистраль.","📱 Технологический стартап.","🎬 Национальный фильм получил награду."]
    negative_news = ["⚠️ Скандал в правительстве.","🌊 Наводнение.","📉 Рост цен.","🚔 Ограбления.","🏭 Забастовка.","🔥 Лесные пожары."]
    return {
        "year": year, "global_icon": global_state["icon"], "global_title": global_state["title"], "global_desc": global_state["desc"],
        "region_news": random.choice(region_news.get(country[2], ["Мир меняется."])),
        "extra_news": random.choice(positive_news + negative_news),
    }

def generate_family_background(country, gender, start_cash):
    c_economy = country[7]
    if start_cash < c_economy * 0.5: wealth_class = "poor"
    elif start_cash < c_economy * 1.5: wealth_class = "middle"
    else: wealth_class = "rich"

    if wealth_class == "poor":
        father_occ = random.choice(["работает на фабрике","грузчик в порту","мелкий фермер","курьер","сторож на складе","разнорабочий","чистильщик обуви","продавец на рынке"])
        mother_occ = random.choice(["работает уборщицей","швея на дому","торгует на рынке","посудомойка в кафе","домохозяйка","собирает пластик","прислуга в богатом доме"])
        housing = random.choice(["крошечная хижина","комната в трущобах","домик в деревне","подвал","общежитие для рабочих","квартира-студия"])
        living = "Тесное жилище, вода из колонки."
        location = random.choice(["глухая деревня","трущобы большого города","окраина мегаполиса","рабочий квартал","посёлок у фабрики"])
    elif wealth_class == "middle":
        father_occ = random.choice(["инженер","учитель","бухгалтер","врач в поликлинике","механик","менеджер в офисе","торговый представитель","водитель автобуса"])
        mother_occ = random.choice(["учительница","медсестра","продавец в магазине","парикмахер","повар","секретарь","библиотекарь"])
        housing = random.choice(["квартира в панельном доме","небольшой дом на окраине","жильё с ипотекой","двухкомнатная квартира"])
        living = "Скромная, но опрятная квартира."
        location = random.choice(["спальный район","пригород","рабочий пригород","небольшой город"])
    else:
        father_occ = random.choice(["владелец фирмы","адвокат","крупный бизнесмен","депутат парламента","топ-менеджер корпорации","врач-хирург в частной клинике"])
        mother_occ = random.choice(["управляет семейным бизнесом","дизайнер интерьеров","известный врач","профессор университета","светская львица","адвокат по бизнесу"])
        housing = random.choice(["роскошный особняк","пентхаус в центре","поместье за городом","дом с бассейном и садом"])
        living = "Просторный дом с прислугой."
        location = random.choice(["престижный район столицы","закрытый коттеджный посёлок","центр города"])

    father_name = random.choice(NAMES[country[2]]["m"])
    mother_name = random.choice(NAMES[country[2]]["f"])
    sib_count = random.choices([0,1,2,3,4], weights=[20,35,25,15,5])[0]
    siblings = []
    for _ in range(sib_count):
        sg = random.choice(["m","f"]); sn = random.choice(NAMES[country[2]][sg])
        if wealth_class == "poor": st = random.choice(["ходит в школу, помогает родителям","работает с 10 лет","присматривает за младшими"])
        elif wealth_class == "middle": st = random.choice(["учится в школе","ходит в музыкальную школу","занимается спортом"])
        else: st = random.choice(["ходит в частную школу","занимается с репетиторами","учится за границей"])
        siblings.append({"name":sn,"gender":sg,"status":st,"age_diff":random.randint(-4,6)})
    grandparents = []
    for side in ["мамы","папы"]:
        for role in ["дедушка","бабушка"]:
            grandparents.append({"role":f"{role} по линии {side}","alive":random.random()<0.55})
    return {"wealth_class":wealth_class,"father_name":father_name,"father_occupation":father_occ,"mother_name":mother_name,"mother_occupation":mother_occ,"housing":housing,"living_conditions":living,"siblings":siblings,"siblings_count":sib_count,"grandparents":grandparents,"location":location}

def format_backstory(l):
    family = l.get("family",{}); world = l.get("world_context",{}); c = l["country"]
    world_text = (f"🌍 <b>Год {world['year']}. Мир, в который ты приходишь</b>\n\n"
                  f"{world['global_icon']} <b>{world['global_title']}</b>\n<i>{world['global_desc']}</i>\n\n"
                  f"<b>В {c[1]} {c[0]}:</b>\n{world['region_news']}\n{world['extra_news']}\n\n"
                  f"<i>Это мир, в котором тебе предстоит жить.</i>")
    wealth_emoji = {"poor":"🥀","middle":"🏠","rich":"👑"}
    wealth_ru = {"poor":"бедной","middle":"средней","rich":"богатой"}
    family_text = (f"{wealth_emoji[family['wealth_class']]} <b>Ты родился в {wealth_ru[family['wealth_class']]} семье</b>\n\n"
                   f"👨 <b>Отец:</b> {family['father_name']} — {family['father_occupation']}\n"
                   f"👩 <b>Мать:</b> {family['mother_name']} — {family['mother_occupation']}\n\n"
                   f"🏡 <b>Жилище:</b> {family['housing']}\n{family['living_conditions']}\n"
                   f"📍 <b>Место:</b> {family['location']}\n\n"
                   f"👶 <b>Ты:</b> {l['name']}, {l['ethnicity'].lower()}")
    sibs = family.get("siblings",[])
    if sibs:
        sib_text = "👦 <b>Братья и сёстры:</b>\n"
        for s in sibs:
            ic = "👦" if s["gender"] == "m" else "👧"
            ad = s.get("age_diff",0)
            rel = f"старше на {ad} г." if ad > 0 else f"младше на {abs(ad)} г." if ad < 0 else "ровесник"
            sib_text += f"  {ic} <b>{s['name']}</b> ({rel}) — {s['status']}\n"
    else: sib_text = "👦 <b>Братьев и сестёр нет</b> — ты единственный ребёнок.\n"
    gp_alive = [g for g in family.get("grandparents",[]) if g["alive"]]
    gp_dead = [g for g in family.get("grandparents",[]) if not g["alive"]]
    gp_text = ""
    if gp_alive:
        gp_text += "\n👴 <b>Живы:</b>\n"
        for g in gp_alive: gp_text += f"  ✅ {g['role']}\n"
    if gp_dead:
        gp_text += "\n🪦 <b>Ушли из жизни:</b>\n"
        for g in gp_dead: gp_text += f"  ❌ {g['role']}\n"
    relatives_text = sib_text + gp_text + "\n<i>Твоя семья — часть твоей истории.</i>"
    return [world_text, family_text, relatives_text]

# ================= ОТЛОЖЕННЫЕ ПОСЛЕДСТВИЯ =================
def add_pending_consequence(l, years_ahead, event_data):
    l.setdefault("pending_consequences",[]).append({"fire_age":l["age"] + years_ahead,"event":event_data})

def get_due_consequence(l):
    due = [c for c in l.get("pending_consequences",[]) if c["fire_age"] <= l["age"]]
    if not due: return None
    consequence = due[0]; l["pending_consequences"].remove(consequence)
    event = dict(consequence["event"]); event["resolved"] = False
    return event

# ================= ДОСТИЖЕНИЯ И ИТОГ =================
def check_achievements(l):
    if "achievements" not in l: l["achievements"] = []
    if "ever_in_prison" not in l: l["ever_in_prison"] = False
    new_ones = []
    def has(aid): return aid in l["achievements"]
    def unlock(aid):
        if not has(aid): l["achievements"].append(aid); new_ones.append(ACHIEVEMENTS[aid])
    if l["age"] >= 1: unlock("first_word")
    if any(l["education"].startswith(ed) for ed in ["Начальное","Среднее","Высшее"]): unlock("school")
    if any(l["education"].startswith(ed) for ed in ["Среднее","Высшее"]): unlock("graduated")
    if l["education"].startswith("Высшее"): unlock("university")
    if l["married"]: unlock("married")
    if l["children"] > 0: unlock("parent")
    if l["age"] >= 90: unlock("long_liver")
    if l["clean_cash"] >= 100000: unlock("rich")
    if l["clean_cash"] >= 2000000: unlock("elite")
    if l["job_type"] == "criminal": unlock("criminal")
    if l["ever_in_prison"]: unlock("prisoner")
    if l["career_rank"] >= 4: unlock("honest_worker")
    if len(l["diseases"]) >= 3: unlock("survivor")
    if l["knowledge"] >= 90: unlock("polyglot")
    if l["relationships"] >= 90: unlock("social")
    if l["properties"]: unlock("home_owner")
    if l["businesses"]: unlock("businessman")
    if l.get("vacation_count",0) >= 3: unlock("traveler")
    return new_ones

def show_achievements(chat_id, l):
    earned = l.get("achievements",[])
    total = len(ACHIEVEMENTS)
    text = f"🏆 <b>Коллекция судеб</b>\nОткрыто: {len(earned)}/{total}\n\n"
    for aid, ach in ACHIEVEMENTS.items():
        mark = "✅" if aid in earned else "⬜"
        text += f"{mark} {ach['name']} — <i>{ach['desc']}</i>\n"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Назад к жизни", callback_data="refresh"))
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def get_life_balance(l):
    happiness = l["happiness"]
    meaning = 30 + 15 * len(l.get("philosophy_answers",[]))
    meaning = min(100, meaning + l["relationships"] // 5)
    connections = l["relationships"]
    if l["married"]: connections = min(100, connections + 10)
    connections = min(100, connections + l["children"] * 5)
    if l["clean_cash"] >= 2000000: wealth_score = 100
    elif l["clean_cash"] >= 500000: wealth_score = 80
    elif l["clean_cash"] >= 100000: wealth_score = 60
    elif l["clean_cash"] >= 20000: wealth_score = 40
    elif l["clean_cash"] >= 5000: wealth_score = 20
    elif l["clean_cash"] >= 500: wealth_score = 10
    else: wealth_score = 0
    return {"happiness":happiness,"meaning":meaning,"connections":connections,"wealth":wealth_score}

def get_cinematic_headlines(l):
    kws = ["Родился","Пошел в школу","Окончил школу","Поступил в вуз","Женился","Развод","На работу","В полиции","В армии","Криминал","Повышение","Понижение","Купил","Открыл","Умер"]
    highlights = []
    for event in l["life_map"]:
        for kw in kws:
            if kw in event: highlights.append(event); break
    return highlights[-7:] if len(highlights) > 7 else highlights

# ================= create_life =================
def create_life(force_country=None):
    country = force_country if force_country else weighted_country()
    gender = "m" if random.random() < 0.51 else "f"
    name = random.choice(NAMES[country[2]][gender])
    ethnicity, prejudice = get_ethnicity(country[2])
    start_cash = int(country[7] * random.uniform(0.1, 2.0))
    family = generate_family_background(country, gender, start_cash)
    world = generate_world_context(country)
    return {
        "country":country,"gender":gender,"name":name,"ethnicity":ethnicity,"prejudice":prejudice,
        "clean_cash":start_cash,"dirty_cash":0,"in_prison":0,"age":0,"alive":True,"faction":"Нет",
        "health":100,"happiness":50,"knowledge":50,"relationships":50,
        "education":"Нет","job":"Безработный","salary":0,"job_type":"none","career_xp":0,"career_rank":1,
        "married":False,"children":0,"diseases":[],"properties":[],"cars":[],"businesses":[],"investments":[],"political_reputation":50,"debt":0,
        "life_map":[],"neighbors":generate_neighbors(),"peer_lives":generate_peer_lives(),
        "test_data":None,"asked_tests":{1:[],2:[],3:[]},"current_event":None,"has_license":False,"job_years":0,"books_read":0,
        "seen_focus_events":{"health":[],"knowledge":[],"relationships":[],"happiness":[]},
        "seen_regular_events":[],"philosophy_answers":[],"wealth_history":[],
        "key_npcs":create_key_npcs(country, gender, family),
        "pending_consequences":[],"achievements":[],"ever_in_prison":False,"reputation":0,"vacation_count":0,
        "family":family,"world_context":world,"tracked_messages":[],
    }

def add_to_life_map(l, text):
    if len(l["life_map"]) < 30: l["life_map"].append(f"{get_age_str(l['age'])}: {text}")

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

def apply_direct_effect(l, effect):
    is_child = l["age"] < 14
    for key, val in effect.items():
        if key == "text": continue
        if key == "cash":
            if is_child: continue
            l["clean_cash"] += val
        elif key == "dirty":
            if is_child: continue
            l["dirty_cash"] += val
        elif key == "debt":
            if is_child: continue
            l["debt"] = l.get("debt", 0) + val
        elif key in ("health","happiness","knowledge","relationships"):
            l[key] = max(0, min(100, l[key] + val))
        elif key == "career_xp": l["career_xp"] += val
        elif key == "diseases":
            for d in val:
                if d not in l["diseases"]: l["diseases"].append(d)
        elif key == "vacation": l["vacation_count"] = l.get("vacation_count",0) + val
        elif key == "in_prison": l["in_prison"] = val; l["ever_in_prison"] = True
        elif key == "job": l["job"] = val
        elif key == "education": l["education"] = val
    return effect.get("text", "Год прошел.")

def show_peer_lives(l):
    if l["age"] % 5 != 0: return None
    text = "👥 <b>Ровесники (родились с тобой в одну секунду):</b>\n\n"
    for i, p in enumerate(l.get("peer_lives",[])):
        if l["age"] >= p["death_age"]: status = "💀 умер(ла)"
        else: status = get_neighbor_echo({"trajectory":p["trajectory"],"gender":p["gender"],"death_age":p["death_age"]}, l["age"])
        text += f"{i+1}. <b>{p['name']}</b> ({p['country'][1]}): {status}\n"
    return text

def calculate_life_score(l):
    score = 0
    score += l["clean_cash"] // 500 + l["dirty_cash"] // 1000
    score += l["happiness"] + l["health"] // 2 + l["relationships"] // 2 + l["knowledge"] // 2
    score += l["age"] // 2
    score += len(l["properties"]) * 20 + len(l["cars"]) * 10 + len(l["businesses"]) * 40
    score += l["children"] * 15
    if l["married"]: score += 20
    score -= l["debt"] // 500
    score -= len(l["diseases"]) * 5
    return max(0, int(score))

def show_leaderboard(chat_id, highlight_user=None):
    lb = players_db.get("_leaderboard", [])
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("⬅️ Назад к жизни", callback_data="refresh"))
    if not lb:
        msg = bot.send_message(chat_id, "🏆 Рейтинг пуст.", reply_markup=kb, parse_mode="HTML")
        if highlight_user:
            l_ref = players_db.get(str(highlight_user))
            if l_ref: track_message(l_ref, chat_id, msg.message_id)
        return
    text = "🏆 <b>Топ-10 прожитых жизней</b>\n\n"
    medals = ["🥇","🥈","🥉"]
    for i, e in enumerate(lb[:10]):
        prefix = medals[i] if i < 3 else f"{i+1}."
        mark = " 👈" if highlight_user and e["user_id"] == str(highlight_user) else ""
        text += (f"{prefix} <b>{e['name']}</b> ({e['country']}){mark}\n"
                 f"    ⭐ {e['score']} очков · {get_age_str(e['age'])} · {e['wealth']}\n"
                 f"    🩺 {e['cause']}\n\n")
    text += f"\n<i>Всего жизней прожито: {len(lb)}</i>"
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    if highlight_user:
        l_ref = players_db.get(str(highlight_user))
        if l_ref: track_message(l_ref, chat_id, msg.message_id)

# ================= get_event =================
def get_event(l):
    age = l["age"]

    pol_evt = trigger_politics_event(l)
    if pol_evt:
        return pol_evt

    if age >= 18 and l["job_type"] == "none" and l["faction"] == "Нет" and l["in_prison"] == 0:
        return {"id":"path","title":"⚡ Выбор пути","text":"Пора определяться.",
                "choices":[{"text":"💼 Гражданка","p":1,"success":"job_civ","fail":"none"},
                           {"text":"👮 Полиция","p":1 if l["education"].startswith("Высшее") else 0,"success":"job_pol","fail":"none"},
                           {"text":"🎖 Армия","p":1 if any(l["education"].startswith(ed) for ed in ["Среднее","Высшее"]) else 0,"success":"job_mil","fail":"none"},
                           {"text":"💊 Криминал","p":1,"success":"job_crim","fail":"none"}]}

    lf = l.get("last_focus")
    if lf and lf in FOCUS_EVENTS and random.random() < 0.40:
        all_evts = [e for e in FOCUS_EVENTS[lf] if e.get("min_age",0) <= age <= e.get("max_age",999)]
        if all_evts:
            seen = l.setdefault("seen_focus_events",{}).setdefault(lf,[])
            recent = seen[-5:] if len(seen) >= 5 else seen
            available = [e for e in all_evts if e.get("id") not in recent]
            if not available: available = all_evts
            weights = [e.get("weight",1.0) for e in available]
            evt = random.choices(available, weights=weights, k=1)[0]
            if evt.get("id") and evt["id"] not in seen:
                seen.append(evt["id"])
                if len(seen) > 40: l["seen_focus_events"][lf] = seen[-30:]
            return evt

    if l["prejudice"] and 16 < age < 60 and random.random() < 0.15:
        return {"id":"prej","title":"Столкновение с предвзятостью","text":f"{l['prejudice']}",
                "choices":[{"text":"✊ Доказать","p":0.4,"success":"prej_fight_win","fail":"prej_fight_fail"},
                           {"text":"🦊 Использовать","p":0.7,"success":"prej_exploit","fail":"prej_exploit_fail"},
                           {"text":"😔 Смириться","p":1,"success":"prej_accept","fail":"none"}]}

    if age >= 15 and random.random() < 0.05:
        we = random.choice(WORLD_EVENTS)
        if we.get("min_age",0) <= age:
            return {"id":we["id"],"title":we["title"],"text":we["text"],
                    "choices":[{"text":"Пережить","p":1,"success_effect":{**we["effect"],"text":we["text"]}}]}

    if random.random() < 0.01:
        twists = [t for t in LIFE_TWISTS if t.get("min_age",0) <= age <= t.get("max_age",999) and (not t.get("requires_property") or bool(l["properties"]))]
        if twists:
            twist = random.choice(twists)
            return {"id":twist["id"],"title":twist["title"],"text":twist["text"],"choices":twist["choices"]}

    if age >= 5 and random.random() < 0.12:
        alive = [n for n in l.get("key_npcs",[]) if not n.get("dead")]
        if alive:
            npc = random.choice(alive); role = npc["role"]; nm = npc["name"]
            if role == "mother" and age >= 14:
                return {"id":"npc_mother","title":"📞 Звонок маме","text":f"Мама {nm} звонит.",
                        "choices":[{"text":"Поговорить","p":1,"success_effect":{"relationships":6,"happiness":5,"text":"Тёплая беседа."}},
                                   {"text":"Бросить","p":1,"success_effect":{"relationships":-8,"happiness":-3,"text":"Мама расстроилась."}}]}
            if role == "friend" and age >= 10:
                return {"id":"npc_friend","title":"🤝 Друг просит помощи","text":f"Друг {nm} в беде.",
                        "choices":[{"text":"Помочь","p":0.8,"success_effect":{"relationships":15,"happiness":5,"cash":-200,"text":"Он твой должник."},"fail_effect":{"relationships":-5,"cash":-200,"text":"Не получилось."}},
                                   {"text":"Отказать","p":1,"success_effect":{"relationships":-15,"happiness":-5,"text":"Обиделся."}}]}
            if role == "rival" and age >= 13:
                return {"id":"npc_rival","title":"⚔️ Соперник","text":f"Соперник {nm} бросает вызов.",
                        "choices":[{"text":"Принять","p":0.5,"success_effect":{"happiness":10,"career_xp":15,"relationships":3,"text":"Победил!"},"fail_effect":{"happiness":-5,"health":-5,"text":"Проиграл."}},
                                   {"text":"Отказаться","p":1,"success_effect":{"relationships":-3,"text":"Трус."}}]}
            if role == "father" and age >= 20:
                return {"id":"npc_father","title":"👴 Отец зовёт","text":f"Отец {nm} на ужин.",
                        "choices":[{"text":"Пойти","p":1,"success_effect":{"relationships":8,"happiness":5,"text":"Отличный вечер."}},
                                   {"text":"Отказаться","p":1,"success_effect":{"relationships":-5,"text":"Обиделся."}}]}

    if age >= 18 and l["job_type"] in ["civilian","police","military"] and random.random() < 0.25:
        if random.random() < 0.5:
            return {"id":"work_ot","title":"💼 Овертайм","text":"Горящий проект.",
                    "choices":[{"text":"Согласиться","p":0.7,"success":"career_xp_up","fail":"none"},{"text":"Уйти","p":1,"success":"career_xp_down","fail":"none"}]}
        else:
            return {"id":"work_int","title":"📉 Интриги","text":"Коллега подставил.",
                    "choices":[{"text":"Скандал","p":0.3,"success":"career_fight_win","fail":"career_grind"},{"text":"Смириться","p":1,"success":"career_grind","fail":"none"}]}

    if age >= 18 and l["cars"] and random.random() < 0.15:
        if not l.get("has_license"):
            return {"id":"dps1","title":"🚨 ДПС","text":"Просит права. У тебя нет.",
                    "choices":[{"text":"💵 Взятка","p":0.7,"success":"bribe_dps","fail":"dps_jail"},{"text":"😬 Договориться","p":0.2,"success":"dps_warning","fail":"dps_jail"}]}
        elif random.random() < 0.3:
            return {"id":"dps2","title":"🍻 Пьяная езда","text":"Запах перегара.",
                    "choices":[{"text":"💵 Взятка","p":0.5,"success":"bribe_dps_big","fail":"drunk_jail"},{"text":"🚶 Отказ","p":0.1,"success":"dps_warning","fail":"drunk_jail"},{"text":"😭 Смириться","p":1,"success":"drunk_jail","fail":"none"}]}

    if age < 13:
        pool = [e for e in CHILD_EVENTS if e["min_age"] <= age <= e["max_age"]]
        return pick_rotating(l, pool, max_recent=5)
    elif age < 18:
        return pick_rotating(l, TEEN_EVENTS, max_recent=6)
    else:
        return pick_rotating(l, adult_events_for(l), max_recent=8)

# ================= СТАТИСТИКА =================
def get_stats_line(l):
    return f"❤️ {l['health']}% | 😊 {l['happiness']}% | 🧠 {l['knowledge']}% | 🤝 {l['relationships']}%"

def apply_focus(l, focus):
    if focus == "health":
        l["health"] = min(100, l["health"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Уделил время здоровью")
    elif focus == "knowledge":
        l["knowledge"] = min(100, l["knowledge"] + random.randint(5,10)); l["happiness"] = max(0, l["happiness"] - random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Учился и развивался")
    elif focus == "relationships":
        l["relationships"] = min(100, l["relationships"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: Уделил время семье и друзьям")
    elif focus == "happiness":
        l["happiness"] = min(100, l["happiness"] + random.randint(10,15)); l["health"] = max(0, l["health"] - random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,5)); l["relationships"] = max(0, l["relationships"] - random.randint(0,5))
        l["life_map"].append(f"{get_age_str(l['age'])}: Наслаждался жизнью")
    elif focus == "work":
        l["happiness"] = max(0, l["happiness"] - random.randint(2,6)); l["health"] = max(0, l["health"] - random.randint(1,4))
        l["knowledge"] = min(100, l["knowledge"] + random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,4))
        l["life_map"].append(f"{get_age_str(l['age'])}: Работал не покладая рук")

# ================= next_year =================
def next_year(user_id, chat_id):
    uid_str = str(user_id)
    if uid_str not in players_db: return bot.send_message(chat_id, "Начни заново: /start")
    l = players_db[uid_str]
    if not l["alive"]: return bot.send_message(chat_id, "Ты умер. /start")

    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1; save_db(players_db)
        if l["in_prison"] == 0:
            l["job"] = "Безработный"; l["salary"] = 0; l["job_type"] = "none"
            return send_scene(chat_id, l, "⛓ <b>Ты вышел на свободу.</b>", kb_year(), "life")
        return send_scene(chat_id, l, f"⛓ <b>Тюрьма.</b> Осталось: {get_age_str(l['in_prison'])}.", kb_year(), "prison")

    if l.get("focus"):
        l["last_focus"] = l["focus"]; apply_focus(l, l["focus"]); l["focus"] = None
    else: l["last_focus"] = None

    l["age"] += 1

    if 7 <= l["age"] <= 13:
        base_pocket = int(l["country"][7] * 0.02)
        l["clean_cash"] += max(10, min(150, base_pocket))
    elif 14 <= l["age"] <= 17:
        base_job = int(l["country"][7] * 0.08)
        l["clean_cash"] += max(50, min(500, base_job))

    rent = sum(int(pr["value"] * 0.05) for pr in l["properties"])
    biz = sum(int(b["value"] * 0.15) for b in l["businesses"])
    biz_crisis_text = trigger_business_crisis(l)
    inv_report = process_investments(l)
    l["clean_cash"] += rent + biz

    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian","police","military"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    spend_mod = 1.0
    if l["prejudice"] and ("скупым" in l["prejudice"] or "предприимчивым" in l["prejudice"]): spend_mod = 0.7
    elif l["prejudice"] and ("беззаботным" in l["prejudice"] or "пьяницей" in l["prejudice"]): spend_mod = 1.3
    living = int(l["country"][7] * 0.2 * spend_mod + (300 * l["children"]))
    l["clean_cash"] += (l["salary"] - tax - med - living)
    if l["clean_cash"] < 0:
        l["debt"] += abs(l["clean_cash"]); l["clean_cash"] = 0

    l["wealth_history"].append(l["clean_cash"])
    if len(l["wealth_history"]) > 80: l["wealth_history"] = l["wealth_history"][-80:]

    if l["job_type"] in ["civilian","police","military","criminal"]:
        l["job_years"] += 1
        if l["career_xp"] >= 100 and l["job_years"] >= 2:
            l["career_xp"] = 0; l["career_rank"] = min(5, l["career_rank"] + 1); l["salary"] = int(l["salary"] * 1.3); l["job_years"] = 0
            add_to_life_map(l, f"Повышение до {CAREER_TITLES[l['job_type']][l['career_rank']]}")
        elif l["career_xp"] <= -50:
            l["career_xp"] = 0; l["career_rank"] = max(1, l["career_rank"] - 1); l["salary"] = int(l["salary"] * 0.7); l["job_years"] = 0
            add_to_life_map(l, f"Понижение до {CAREER_TITLES[l['job_type']][l['career_rank']]}")

    echo_text = ""
    if l["age"] in [7,18,30,50]:
        n = random.choice(l["neighbors"])
        echo_text = f"\n\n👥 <b>Эхо:</b> Твой ровесник <b>{n['name']}</b> ({n['country'][1]}) — {get_neighbor_echo(n, l['age'])}."
    peer_text = show_peer_lives(l)
    if peer_text: echo_text += "\n\n" + peer_text
    if biz_crisis_text: echo_text += "\n\n" + biz_crisis_text
    if inv_report: echo_text += inv_report
    if launder_text: echo_text += launder_text

    check_npc_deaths(l)

    if random.random() < mortality_rate(l):
        save_db(players_db); return send_death(user_id, chat_id)

    consequence_evt = get_due_consequence(l)
    if consequence_evt:
        l["current_event"] = consequence_evt; save_db(players_db)
        return send_scene(chat_id, l, format_event(l, consequence_evt), kb_event(consequence_evt["choices"]), "life")

    if l["age"] in (5,15,30,50,70) and l["age"] not in [a["age"] for a in l.get("philosophy_answers",[])]:
        questions = {
            5:{"q":"Что для тебя сейчас самое важное?","opts":["👨‍👩‍👧 Семья","🎮 Игры","🌍 Узнать мир"]},
            15:{"q":"Кем ты хочешь стать?","opts":["💼 Успешным","❤️ Любимым","🧠 Умным"]},
            30:{"q":"Что делает жизнь осмысленной?","opts":["💰 Деньги","🤝 Отношения","🎯 Цель"]},
            50:{"q":"О чём ты жалеешь?","opts":["⏰ О времени","💔 О несделанном","😔 Ни о чём"]},
            70:{"q":"Что ты оставишь после себя?","opts":["👨‍👩‍👧 Детей","📚 Знания","💭 Воспоминания"]},
        }
        q = questions[l["age"]]
        l["current_event"] = {"id":f"phil_{l['age']}","title":f"🤔 Вопрос в {get_age_str(l['age'])}","text":q["q"],
                              "choices":[{"text":opt,"p":1,"success_effect":{"happiness":3,"text":f"Ты выбрал: {opt}."}} for opt in q["opts"]],
                              "is_philosophy":True,"age":l["age"],"resolved":False}
        save_db(players_db)
        return send_scene(chat_id, l, format_event(l, l["current_event"]), kb_event(l["current_event"]["choices"]), "life")

    if l["age"] == 6: return start_exam(user_id, chat_id, 1, "школу")
    elif l["age"] == 12: return start_exam(user_id, chat_id, 2, "колледж")
    elif l["age"] == 18: return start_exam(user_id, chat_id, 3, "университет")

    evt = get_event(l)
    if evt:
        evt["resolved"] = False
        l["current_event"] = evt
        sc = "life"
        if "Овертайм" in evt["title"] or "Интриги" in evt["title"]: sc = "office_angry"
        elif "Кризис" in evt["title"]: sc = "sad"
        elif "Брак" in evt["title"]: sc = "love"
        elif "Развод" in evt["title"]: sc = "sad"
        elif "Мошенники" in evt["title"]: sc = "money_lose"
        elif "Лотерея" in evt["title"]: sc = "money_win"
        elif "ДПС" in evt["title"] or "езда" in evt["title"]: sc = "police"
        elif evt["title"].startswith(("🍼","👣","🧸 Любимая")): sc = "toddler"
        send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]), sc)
    else:
        l["current_event"] = None
        send_scene(chat_id, l, format_year(l) + echo_text, kb_focus(l), "life")

    new_ach = check_achievements(l)
    for ach in new_ach:
        msg = bot.send_message(chat_id, f"🏆 <b>Новое достижение!</b>\n{ach['name']} — {ach['desc']}", parse_mode="HTML")
        track_message(l, chat_id, msg.message_id)
    save_db(players_db)

def send_death(user_id, chat_id):
    l = players_db[str(user_id)]; l["alive"] = False; c = l["country"]
    l["current_event"] = None
    causes = []
    if l["age"] < 5: causes = ["Перинатальные причины","Инфекции","Несчастный случай"]
    elif l["age"] < 15: causes = ["Инфекции","Несчастный случай","Врождённые аномалии"]
    elif l["age"] < 30: causes = ["Несчастный случай","Насилие","Болезни"]
    elif l["age"] < 50: causes = ["Сердечно-сосудистые","Онкология","Несчастный случай"]
    elif l["age"] < 70: causes = ["Онкология","Сердечно-сосудистые","Диабет"]
    else: causes = ["Сердечно-сосудистые","Онкология","Старение"]
    if l["diseases"]: cause = f"Осложнение: {l['diseases'][-1]}"
    else: cause = random.choice(causes)
    final_ach = check_achievements(l)
    score = calculate_life_score(l)
    entry = {"name":l["name"],"country":f"{c[1]} {c[0]}","score":score,"age":l["age"],"cause":cause,
             "wealth":get_wealth_status(l["clean_cash"], l["dirty_cash"], l),"user_id":str(user_id)}
    lb = players_db.setdefault("_leaderboard", [])
    lb.append(entry); lb.sort(key=lambda x: x["score"], reverse=True)
    players_db["_leaderboard"] = lb[:50]
    save_db(players_db)
    place = next((i+1 for i, e in enumerate(lb) if e is entry), len(lb))
    total = len(lb)
    balance = get_life_balance(l)
    balance_text = (f"📊 <b>Баланс жизни:</b>\n  😊 Счастье: {balance['happiness']}/100\n"
                    f"  🎯 Смысл: {balance['meaning']}/100\n  🤝 Связи: {balance['connections']}/100\n"
                    f"  💰 Достаток: {balance['wealth']}/100\n")
    headlines = get_cinematic_headlines(l)
    headlines_text = "📜 <b>Летопись:</b>\n" + "\n".join([f"• {h}" for h in headlines]) if headlines else ""
    npc_text = "💫 <b>Судьбы близких:</b>\n" + "\n".join([get_npc_epilogue(n) for n in l.get("key_npcs",[])])
    earned = l.get("achievements", [])
    ach_text = f"🏆 <b>Достижения:</b> {len(earned)}/{len(ACHIEVEMENTS)}"
    if final_ach: ach_text += "\n" + "\n".join([f"• {a['name']}" for a in final_ach])
    if l.get("wealth_history"):
        max_w = max(l["wealth_history"]) or 1
        chart = "".join(["▁" if w < max_w*0.2 else "▃" if w < max_w*0.5 else "▅" if w < max_w*0.8 else "█" for w in l["wealth_history"]])
        chart_text = f"\n📈 Кривая достатка: {chart}\n"
    else: chart_text = ""
    top_text = "\n🏆 <b>Топ-5 жизней:</b>\n"
    for i, e in enumerate(lb[:5]):
        mark = "👉" if e["user_id"] == str(user_id) and e["age"] == l["age"] else "  "
        top_text += f"{mark} {i+1}. <b>{e['name']}</b> ({e['country']}) — {e['score']} очков, {get_age_str(e['age'])}\n"
    msg = (f"💀 <b>Смерть в {get_age_str(l['age'])}.</b>\n🩺 Причина: {cause}\n\n{balance_text}\n"
           f"⭐ Оценка жизни: <b>{score} очков</b> · место <b>#{place} из {total}</b>\n\n"
           f"{headlines_text}\n\n{npc_text}\n\n{ach_text}\n{chart_text}")
    kb = InlineKeyboardMarkup()
    for i, p in enumerate(l.get("peer_lives",[])):
        fate = get_neighbor_final({"trajectory":p["trajectory"],"death_age":p["death_age"]})
        msg += f"\n👥 Ровесник {p['name']} ({p['country'][1]}): {fate}"
        kb.add(InlineKeyboardButton(f"🎭 Прожить жизнь {p['name']}", callback_data=f"play_peer_{i}"))
    msg += "\n\n" + top_text
    kb.add(InlineKeyboardButton("🏆 Топ жизней", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("📖 Достижения", callback_data="achievements"))
    if l.get("children", 0) > 0 or l["clean_cash"] > 5000 or l["properties"] or l["businesses"]:
        kb.add(InlineKeyboardButton(f"👑 Продолжить династию (Наследник)", callback_data="dynasty_continue"))
    kb.add(InlineKeyboardButton("🎲 Начать заново", callback_data="new"))
    play_cutscene(chat_id, l, get_cutscene_frames("death"), msg, kb)

def start_exam(user_id, chat_id, level, place):
    l = players_db[str(user_id)]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    school = random.choice(["Школа №1","Гимназия","Колледж","Университет"])
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    msg = bot.send_message(chat_id, f"📝 <b>Экзамен в {place}!</b>\n{school}\n\nВопрос: <b>{test['q']}</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)
    save_db(players_db)

def handle_exam_answer(user_id, chat_id, ans_idx):
    l = players_db[str(user_id)]
    test = l.get("test_data")
    if not test: return
    
    is_correct = (ans_idx == test["ans"])
    l["test_data"] = None
    success = is_correct
    saved_by_stereotype = False
    saved_by_knowledge = False
    bias_failed = False
    
    # Механика влияния стереотипов на экзаменах
    if not success:
        # Если игрок ошибся, но общество считает его "умным"
        if l.get("prejudice") and "умным" in l["prejudice"]:
            if random.random() < 0.50:  # 50% шанс снисхождения экзаменаторов
                success = True
                saved_by_stereotype = True
        # Либо если у персонажа уже очень высокие знания (75+)
        elif l.get("knowledge", 50) >= 75 and random.random() < 0.35:
            success = True
            saved_by_knowledge = True
    else:
        # Если ответил правильно, но есть негативный стереотип ("дикарь" / "чужой")
        if l.get("prejudice") and any(bad in l["prejudice"] for bad in ["дикарем", "чужим", "подозрением"]):
            if random.random() < 0.15:  # 15% риск предвзятости комиссии
                success = False
                bias_failed = True

    g_m = l.get("gender") == "m"
    correct_text = test["opts"][test["ans"]]

    if success:
        if saved_by_stereotype:
            msg = (
                f"🧠 <b>Стереотип спас экзамен!</b>\n"
                f"Ты выбрал неправильный ответ, но комиссия с детства считает представителей твоей национальности («{l.get('ethnicity', '')} — считают умным») вундеркиндами. "
                f"Экзаменаторы решили, что ты оговорился или применил нестандартную логику, и поставили зачёт!\n"
                f"<i>(Правильный ответ был: {correct_text})</i>"
            )
            l["happiness"] = min(100, l["happiness"] + 8)
        elif saved_by_knowledge:
            msg = (
                f"📚 <b>Репутация отличника!</b>\n"
                f"Ты допустил оплошность, но твоя высокая эрудиция (знания {l['knowledge']}%) убедила преподавателей, что это случайная описка от волнения. "
                f"Зачёт выставлен!"
            )
            l["happiness"] = min(100, l["happiness"] + 5)
        else:
            msg = f"✅ <b>Экзамен сдан на отлично!</b>\nПравильный ответ: <b>{correct_text}</b>."

        if l["age"] == 6:
            l["education"] = "Начальное"
            l["knowledge"] += 10
            add_to_life_map(l, "Пошел в школу" if g_m else "Пошла в школу")
        elif l["age"] == 12:
            l["education"] = "Среднее (колледж/лицей)"
            l["knowledge"] += 15
            add_to_life_map(l, "Поступил в лицей/колледж" if g_m else "Поступила в лицей/колледж")
        elif l["age"] == 18:
            l["education"] = "Высшее (университет)"
            l["knowledge"] += 25
            add_to_life_map(l, "Поступил в университет" if g_m else "Поступила в университет")
    else:
        if bias_failed:
            msg = (
                f"⚠️ <b>Предвзятость экзаменаторов!</b>\n"
                f"Ты ответил абсолютно правильно (<b>{correct_text}</b>), но из-за предрассудков («{l.get('prejudice', '')}») комиссия заподозрила списывание, "
                f"завалила каверзными придирками и отказала в зачёте."
            )
            l["happiness"] = max(0, l["happiness"] - 12)
        else:
            msg = f"❌ <b>Экзамен провален!</b>\nНеверный ответ (правильно было: <i>{correct_text}</i>). Поступить на этот уровень пока не удалось."
            l["happiness"] = max(0, l["happiness"] - 5)

    l["last_result"] = {
        "success": success,
        "text": msg.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","")
    }
    save_db(players_db)
    send_scene(chat_id, l, msg + "\n\n" + format_year(l), kb_focus(l), "school")

def apply_outcome(l, outcome):
    vvp = l["country"][7]
    is_bad = l["prejudice"] and any(t in l["prejudice"] for t in BAD_TRAITS_LOCAL)
            if outcome == "politics_win":
        cost = max(1000, int(vvp * 0.4))
        l["clean_cash"] = max(0, l["clean_cash"] - cost)
        l["political_reputation"] = min(100, l.get("political_reputation", 50) + 15)
        # Дополнительная зарплата депутата/премия
        bonus = int(vvp * 1.2)
        l["clean_cash"] += bonus
        l["happiness"] = min(100, l["happiness"] + 15)
        add_to_life_map(l, "Избран депутатом совета")
        return f"🏆 Победа на выборах! Вы избраны депутатом, получили мандат и премию {fmt_money(bonus, l['country'])}!"
    if outcome == "politics_fail":
        cost = max(1000, int(vvp * 0.4))
        l["clean_cash"] = max(0, l["clean_cash"] - cost)
        l["political_reputation"] = max(0, l.get("political_reputation", 50) - 8)
        l["happiness"] = max(0, l["happiness"] - 6)
        return "Поражение на выборах. Средства на кампанию потрачены, избиратели предпочли оппонента."
    if outcome == "politics_fail_free":
        l["happiness"] = max(0, l["happiness"] - 4)
        return "Кампания без бюджета не смогла привлечь внимание прессы и избирателей."
    if outcome == "toddler_mama": l["relationships"] += 5; return "Сказал «мама»."
    if outcome == "toddler_papa": l["relationships"] += 5; return "Сказал «папа»."
    if outcome == "toddler_walk": l["health"] += 5; l["happiness"] += 10; return "Первый шаг!"
    if outcome == "toddler_fall": l["health"] -= 2; return "Упал."
    if outcome == "toddler_crawl": l["happiness"] += 2; return "Ползаешь."
    if outcome == "toddler_hug": l["happiness"] += 8; return "Мишка успокоил."
    if outcome == "toddler_break": l["happiness"] -= 5; return "Сломал игрушку."
    if outcome == "prej_fight_win": l["clean_cash"] += int(vvp*0.5); l["prejudice"] = None; l["happiness"] += 10; return "Сломал стереотип!"
    if outcome == "prej_fight_fail": l["clean_cash"] -= int(vvp*0.2); l["diseases"].append("ПТСР"); l["health"] -= 10; return "Потратил силы."
    if outcome == "prej_exploit":
        if is_bad: l["dirty_cash"] += int(vvp*0.8); l["happiness"] -= 5; return "Использовал негативный."
        else: l["clean_cash"] += int(vvp*0.3); l["career_xp"] += 20; l["happiness"] += 5; return "Оседлал позитивный!"
    if outcome == "prej_exploit_fail":
        if is_bad: l["in_prison"] = 3; l["happiness"] -= 20; l["ever_in_prison"] = True; return "Сел."
        else: l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 10; return "Выгорел."
    if outcome == "prej_accept": l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 5; return "Смирился."
    if outcome == "marry":
        g_m = l.get("gender") == "m"
        l["married"] = True; l["happiness"] += 20; l["relationships"] += 15; add_to_life_map(l, "Женился" if g_m else "Вышла замуж")
        if random.random() < 0.6: l["children"] = l.get("children",0) + 1; add_to_life_map(l, "Родился ребёнок")
        return "Поженились!"
    if outcome == "divorce":
        l["married"] = False
        if l["clean_cash"] > 0: l["clean_cash"] = int(l["clean_cash"] / 2)
        l["happiness"] -= 15; l["relationships"] -= 20
        add_pending_consequence(l, 5, {"id":"conseq_ex","title":"💔 Встреча с бывшим","text":"Случайная встреча.",
                                       "choices":[{"text":"Поговорить","p":0.5,"success_effect":{"happiness":5,"relationships":5,"text":"Мирно."},"fail_effect":{"happiness":-10,"text":"Поругались."}},{"text":"Мимо","p":1,"success_effect":{"text":"Прошёл."}}]})
        return "Развод."
    if outcome == "job_civ": l["job_type"] = "civilian"; l["job"] = "Работник"; l["salary"] = int(vvp * 0.6); l["relationships"] += 5; add_to_life_map(l, "На работу"); return "Ты на гражданке."
    if outcome == "job_pol": l["job_type"] = "police"; l["faction"] = "Полиция"; l["job"] = "Полицейский"; l["salary"] = int(vvp * 0.5); l["relationships"] += 10; add_to_life_map(l, "В полиции"); return "Ты в полиции."
    if outcome == "job_mil": l["job_type"] = "military"; l["faction"] = "Армия"; l["job"] = "Военный"; l["salary"] = int(vvp * 0.4); l["relationships"] += 15; add_to_life_map(l, "В армии"); return "Ты в армии."
    if outcome == "job_crim": l["job_type"] = "criminal"; l["faction"] = "Уличная банда"; l["job"] = "Бандит"; l["dirty_cash"] += int(vvp*0.5); l["happiness"] -= 10; add_to_life_map(l, "Криминал"); return "Криминал."
    if outcome == "career_xp_up": l["career_xp"] += 30; l["happiness"] -= 5; return "XP +30."
    if outcome == "career_xp_down": l["career_xp"] -= 20; return "XP -20."
    if outcome == "career_fight_win": l["career_xp"] += 40; l["happiness"] -= 5; return "XP +40."
    if outcome == "career_grind": l["career_xp"] -= 10; return "XP -10."
    if outcome == "work_extra": l["clean_cash"] += int(vvp*0.1); l["career_xp"] += 10; l["health"] -= 5; return "Вторая работа."
    if outcome == "family_time": l["career_xp"] -= 10; l["happiness"] += 10; return "Время с семьей."
    if outcome == "burnout": l["diseases"].append("Сердечная недостаточность"); l["health"] -= 20; return "Выгорание."
    if outcome == "scammed":
        loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss; l["happiness"] -= 20
        add_pending_consequence(l, 3, {"id":"conseq_scam","title":"🚨 Возмездие","text":"Мошенника поймали!",
                                       "choices":[{"text":"Подать иск","p":0.7,"success_effect":{"cash":5000,"happiness":10,"text":"Вернули!"},"fail_effect":{"cash":-1000,"text":"Издержки."}},{"text":"Забыть","p":1,"success_effect":{"text":"Не стал."}}]})
        return f"Украли {fmt_money(loss, l['country'])}."
    if outcome == "child_fight": l["happiness"] += 5; return "Дал сдачи."
    if outcome == "child_tell": return "Пожаловался."
    if outcome == "child_smart": l["books_read"] = l.get("books_read",0) + 1; l["knowledge"] += 10; l["happiness"] += 5; return "Книга расширила кругозор."
    if outcome == "child_walk": l["health"] += 5; l["happiness"] += 5; return "Хорошо погулял."
    if outcome == "child_sport": l["health"] += 5; l["happiness"] += 8; l["relationships"] += 3; return "Отлично поиграл."
    if outcome == "child_injury": l["health"] -= 5; return "Травма."
    if outcome == "child_bday_big": l["happiness"] += 15; l["relationships"] += 10; return "Отличный праздник!"
    if outcome == "child_bday_bad": l["happiness"] -= 8; return "Друзья не пришли."
    if outcome == "child_bday_small": l["happiness"] += 6; return "Тихо, но хорошо."
    if outcome == "child_circus": l["happiness"] += 10; return "Волшебство!"
    if outcome == "child_swim_good": l["health"] += 4; l["happiness"] += 6; return "Научился плавать."
    if outcome == "child_swim_fear": l["happiness"] -= 4; return "Испугался."
    if outcome == "child_sick_treat": l["health"] += 6; return "Переболел."
    if outcome == "child_sick_walk_ok": l["happiness"] += 3; return "Погулял."
    if outcome == "child_sick_walk_bad": l["health"] -= 8; return "Болезнь усилилась."
    if outcome == "child_draw_win": l["happiness"] += 10; l["knowledge"] += 3; return "Победил!"
    if outcome == "child_draw_lose": l["happiness"] += 2; return "Поучаствовал."
    if outcome == "child_bike_ok": l["health"] += 3; l["happiness"] += 8; return "Покатался."
    if outcome == "child_bike_fall": l["health"] -= 5; return "Упал."
    if outcome == "child_bike_learn": l["health"] += 2; return "Освоил."
    if outcome == "child_dog_ok": l["happiness"] += 6; return "Погладил."
    if outcome == "child_dog_bite": l["health"] -= 10; l["diseases"].append("Анемия"); return "Укусила."
    if outcome == "child_dog_run": return "Убежал."
    if outcome == "child_theater_good": l["happiness"] += 10; l["relationships"] += 5; return "Отличная роль!"
    if outcome == "child_theater_shy": l["happiness"] -= 3; return "Постеснялся."
    if outcome == "child_theater_tech": l["knowledge"] += 3; return "Помогал за кулисами."
    if outcome == "teen_smoke":
        l["diseases"].append("Рак легких"); l["health"] -= 15
        add_pending_consequence(l, 25, {"id":"conseq_smoke","title":"🚬 Расплата","text":"Годы курения дали о себе знать.",
                                        "choices":[{"text":"Лечиться","p":0.6,"success_effect":{"cash":-5000,"health":10,"text":"Обошлось."},"fail_effect":{"diseases":["Рак легких"],"health":-25,"text":"Рак лёгких."}}]})
        return "Курил."
    if outcome == "teen_healthy": l["clean_cash"] += 200; l["health"] += 5; return "Сэкономил."
    if outcome == "teen_love": l["happiness"] += 15; l["relationships"] += 10; return "Взаимная любовь."
    if outcome == "teen_heartbreak": l["diseases"].append("ПТСР"); l["happiness"] -= 15; l["relationships"] -= 10; return "Отказ."
    if outcome == "teen_sport_good": l["health"] += 8; l["happiness"] += 5; return "Спорт пошёл на пользу."
    if outcome == "teen_sport_hurt": l["health"] -= 6; return "Травма."
    if outcome == "teen_games_win": l["happiness"] += 8; l["relationships"] += 5; return "Победа!"
    if outcome == "teen_games_lose": l["happiness"] += 3; return "Проиграл, но весело."
    if outcome == "teen_study": l["knowledge"] += 6; return "Позанимался."
    if outcome == "teen_fight_win": l["happiness"] += 8; l["relationships"] -= 3; return "Дал сдачи."
    if outcome == "teen_fight_lose": l["health"] -= 8; return "Получил."
    if outcome == "teen_tell_teacher": l["relationships"] += 3; return "Учитель вмешался."
    if outcome == "teen_band": l["happiness"] += 10; l["relationships"] += 5; return "Игра в группе!"
    if outcome == "teen_license_ok": l["has_license"] = True; l["happiness"] += 10; return "Получил права!"
    if outcome == "teen_license_fail": l["happiness"] -= 3; return "Не сдал."
    if outcome == "lottery_win": l["clean_cash"] += int(vvp * 5); l["happiness"] += 30; return "ДЖЕКПОТ!"
    if outcome == "lottery_lose": l["clean_cash"] -= 100; l["happiness"] -= 5; return "Билет пустой."
    if outcome == "bribe_dps": l["dirty_cash"] -= int(vvp*0.1); return "Пронесло."
    if outcome == "dps_jail": l["in_prison"] = 1; l["happiness"] -= 15; l["ever_in_prison"] = True; return "1 год тюрьмы."
    if outcome == "dps_warning": return "Инспектор предупредил."
    if outcome == "bribe_dps_big": l["dirty_cash"] -= int(vvp*0.3); return "Откупился."
    if outcome == "drunk_jail": l["in_prison"] = 3; l["cars"] = []; l["happiness"] -= 30; l["ever_in_prison"] = True; return "3 года + конфискация."
    return "Год прошел."

def resolve_choice(user_id, chat_id, i):
    l = players_db[str(user_id)]
    evt = l.get("current_event")
    if not evt: return
    if evt.get("resolved"): return
    if i < 0 or i >= len(evt["choices"]): return
    c = evt["choices"][i]
    success = random.random() < c["p"]
    
    # Стереотип "считают умным" помогает в контрольных, экзаменах и олимпиадах
    if not success and l.get("prejudice") and "умным" in l["prejudice"]:
        title_low = evt.get("title", "").lower()
        if any(term in title_low for term in ["экзамен", "олимпиад", "учёб", "универ", "школ", "контрольн", "курс", "диплом"]):
            if random.random() < 0.45:
                success = True
                if "success_effect" in c:
                    c = dict(c)
                    eff = dict(c["success_effect"])
                    eff["text"] = "🧠 Стереотип помог: " + eff.get("text", "")
                    c["success_effect"] = eff
    if "success_effect" in c:
        effect = c.get("success_effect") if success else c.get("fail_effect", {"text":"Год прошел."})
        text = apply_direct_effect(l, effect); outcome = "direct"
    else:
        outcome = c["success"] if success else c.get("fail", "none")
        text = apply_outcome(l, outcome) if outcome else "Год прошел."
    l["last_result"] = {"success":success,"text":text}
    if evt.get("is_philosophy"):
        l.setdefault("philosophy_answers",[]).append({"age":evt["age"],"choice":c["text"]})
    evt["resolved"] = True
    l["current_event"] = None
    scene_map = {
        "child_fight":"fight","child_tell":"school","child_smart":"school","child_walk":"child",
        "child_sport":"child","child_injury":"hospital","child_bday_big":"rich","child_bday_bad":"sad","child_bday_small":"child",
        "child_circus":"child","child_swim_good":"child","child_swim_fear":"sad","child_sick_treat":"hospital",
        "child_sick_walk_ok":"child","child_sick_walk_bad":"hospital","child_draw_win":"child","child_draw_lose":"child",
        "child_bike_ok":"child","child_bike_fall":"hospital","child_bike_learn":"child","child_dog_ok":"child",
        "child_dog_bite":"hospital","child_dog_run":"child","child_theater_good":"child","child_theater_shy":"sad","child_theater_tech":"school",
        "toddler_mama":"toddler","toddler_papa":"toddler","toddler_walk":"toddler","toddler_fall":"toddler",
        "toddler_crawl":"toddler","toddler_hug":"toddler","toddler_break":"sad",
        "teen_love":"love","teen_heartbreak":"sad","teen_smoke":"sad","teen_sport_good":"child","teen_sport_hurt":"hospital",
        "teen_games_win":"child","teen_games_lose":"child","teen_study":"school","teen_fight_win":"fight","teen_fight_lose":"hospital",
        "teen_tell_teacher":"school","teen_band":"rich","teen_license_ok":"office","teen_license_fail":"sad",
        "career_xp_up":"office","career_fight_win":"office_angry","career_grind":"office_angry",
        "marry":"wedding","divorce":"sad","scammed":"money_lose","lottery_win":"money_win","lottery_lose":"sad",
        "job_civ":"office","job_pol":"police","job_mil":"military","job_crim":"criminal",
        "prej_fight_win":"office","prej_fight_fail":"sad","prej_exploit":"money_win","prej_exploit_fail":"prison","prej_accept":"sad",
        "bribe_dps":"police","dps_jail":"prison","dps_warning":"police","bribe_dps_big":"police","drunk_jail":"prison",
    }
    if outcome == "direct": sc = "life"
    elif outcome in ["prej_exploit","prej_exploit_fail"]:
        is_bad = l["prejudice"] and any(t in l["prejudice"] for t in BAD_TRAITS_LOCAL)
        if not is_bad: sc = "office" if outcome == "prej_exploit" else "sad"
        else: sc = "money_win" if outcome == "prej_exploit" else "prison"
    else: sc = scene_map.get(outcome, "life")
    save_db(players_db)
    if outcome == "marry":
        play_cutscene(chat_id, l, get_cutscene_frames("marry"), format_year(l), kb_focus(l))
    elif outcome in ["dps_jail","drunk_jail","prej_exploit_fail"]:
        play_cutscene(chat_id, l, get_cutscene_frames("prison"), format_year(l), kb_focus(l))
    else:
        send_scene(chat_id, l, format_year(l), kb_focus(l), sc)

def format_year(l):
    c = l["country"]
    visuals = get_scene_visuals("life", l["gender"])
    parts = [f"<b>Возраст: {get_age_str(l['age'])}</b>\n{visuals}"]
    if l.get("last_result"): parts.append(f"\n{'✅' if l['last_result']['success'] else '❌'} <i>{l['last_result']['text']}</i>")
    parts.append(f"\n{get_stats_line(l)}")
    parts.append(f"\n🧬 Происхождение: <b>{l['ethnicity']}</b>")
    if l["prejudice"]: parts.append(f"⚠️ <i>Общество: {l['prejudice']}</i>")
    parts.append(f"💰 Баланс: <b>{fmt_money(l['clean_cash'], c)}</b>")
    if l["age"] <= 6: parts.append("👨‍👩‍👧 <i>Живёшь на обеспечении родителей</i>")
    elif l["age"] <= 13: parts.append("🪙 <i>Карманные от родителей</i>")
    elif l["age"] <= 17: parts.append("💼 <i>Подработка после учёбы</i>")
    if l["dirty_cash"] > 0: parts.append(f"💼 Грязные: <b>{fmt_money(l['dirty_cash'], c)}</b>")
    if l["debt"] > 0: parts.append(f"🏦 Долг: <b>{fmt_money(l['debt'], c)}</b>")
    parts.append(f"👑 Класс: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian","police","military"]:
        job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'],'')}, XP: {l['career_xp']}/100)"
    parts.append(f"💼 {job}")
    if l["properties"]: parts.append("🏠 " + ", ".join([p["type"] for p in l["properties"]]))
    if l["cars"]: parts.append("🚗 " + ", ".join([c["type"] for c in l["cars"]]))
    if l["businesses"]: parts.append("🏢 " + ", ".join([b["type"] for b in l["businesses"]]))
    if l.get("investments"): parts.append("📈 Портфель: " + ", ".join([f"{i['type']} ({fmt_money(i['amount'], c)})" for i in l["investments"]]))
    if l.get("political_reputation", 50) != 50 or l.get("job_type") == "civilian": parts.append(f"🏛 Политическое влияние: {l.get('political_reputation', 50)}/100")
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
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("▶️ Следующий год", callback_data="year")).add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))

def kb_focus(l=None):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("❤️ Здоровье", callback_data="focus_health"), InlineKeyboardButton("🧠 Знания", callback_data="focus_knowledge"))
    kb.add(InlineKeyboardButton("🤝 Отношения", callback_data="focus_relationships"), InlineKeyboardButton("😊 Счастье", callback_data="focus_happiness"))
    if l and l.get("job_type") in ("civilian","police","military","criminal"):
        kb.add(InlineKeyboardButton("💼 Работа", callback_data="focus_work"))
    kb.add(InlineKeyboardButton("🏆 Топ жизней", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("📖 Достижения", callback_data="achievements"))
    kb.add(InlineKeyboardButton("▶️ Пропустить", callback_data="year"))
    kb.add(InlineKeyboardButton("🛒 Магазин", callback_data="shop"))
    return kb

def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

def open_shop(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("🏠 Недвижимость", callback_data="shop_prop")).add(InlineKeyboardButton("🚗 Авто", callback_data="shop_car")).add(InlineKeyboardButton("🏢 Бизнесы", callback_data="shop_biz")).add(InlineKeyboardButton("📈 Инвестиции", callback_data="shop_invest")).add(InlineKeyboardButton("⬅️ Назад", callback_data="year"))
    msg = bot.send_message(chat_id, f"🛒 <b>Магазин</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_prop_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🏠 <b>Недвижимость</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_car_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items(): kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    if not l.get("has_license"):
        lic_price = int(c[7] * 0.05)
        kb.add(InlineKeyboardButton(f"🪪 Купить права — {fmt_money(lic_price, c)}", callback_data="buy_license"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🚗 <b>Авто</b>\nНаличие прав: {'Да' if l.get('has_license') else 'Нет'}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)


def shop_invest_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, data in INVESTMENT_ASSETS.items():
        kb.add(InlineKeyboardButton(f"📈 {name} — {fmt_money(data['price'], c)}", callback_data=f"buy_invest_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"📈 <b>Инвестиционный рынок</b>\nВкладывайте средства в активы для ежегодной доходности.\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_biz_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items(): kb.add(InlineKeyboardButton(f"🏢 {name} — {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🏢 <b>Бизнесы</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def process_buy(user_id, chat_id, cat, name):
    l = players_db[str(user_id)]; c = l["country"]
    if cat == "license":
        price = int(c[7] * 0.05)
        if l["clean_cash"] < price: return bot.send_message(chat_id, "❌ Мало денег на права!", reply_markup=kb_year())
        l["clean_cash"] -= price; l["has_license"] = True; save_db(players_db)
        return bot.send_message(chat_id, "🎉 Ты получил водительские права!", reply_markup=kb_year(), parse_mode="HTML")
    if cat == "prop": base = PROPERTIES[name]
    elif cat == "car": base = CARS[name]
    else: base = BUSINESSES[name]
    if l["clean_cash"] < base: return bot.send_message(chat_id, "❌ Мало денег!", reply_markup=kb_year())
    l["clean_cash"] -= base
    if cat == "prop": l["properties"].append({"type":name,"value":base}); add_to_life_map(l, f"Купил {name}")
    elif cat == "car": l["cars"].append({"type":name,"value":base}); add_to_life_map(l, f"Купил {name}")
    elif cat == "biz": l["businesses"].append({"type":name,"value":base}); add_to_life_map(l, f"Открыл {name}")
    elif cat == "invest":
        existing = next((i for i in l.setdefault("investments", []) if i["type"] == name), None)
        if existing: existing["amount"] += base
        else: l["investments"].append({"type": name, "amount": base})
        add_to_life_map(l, f"Купил активы: {name}")
    save_db(players_db)
    bot.send_message(chat_id, f"🎉 Куплено: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= ОБРАБОТЧИКИ =================
