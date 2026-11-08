import sys
from pathlib import Path
_BASE_DIR = str(Path(__file__).resolve().parent)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

import random
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, players_db, save_db
from utils import (
    get_age_str, track_message, clear_tracked_messages, fmt_money,
    get_wealth_status, get_stats_line, get_scene_visuals, get_cutscene_frames, play_cutscene
)
from data.avatars import get_person_emoji, ETHNIC_PROFILES
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
        return {"id":"fallback","title":"ЁЯУЕ ╨Ю╨▒╤Л╤З╨╜╤Л╨╣ ╨│╨╛╨┤","text":"╨Э╨╕╤З╨╡╨│╨╛ ╨╛╤Б╨╛╨▒╨╡╨╜╨╜╨╛╨│╨╛.",
                "choices":[{"text":"╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М","p":1,"success_effect":{"text":"╨б╨┐╨╛╨║╨╛╨╣╨╜╤Л╨╣ ╨│╨╛╨┤."}}]}
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
    if event_type == "birth": return ["ЁЯПе ЁЯСитАНтЪХя╕П ЁЯд░\n<i>╨Т╤А╨░╤З╨╕ ╨│╨╛╤В╨╛╨▓╤П╤В╤Б╤П...</i>","ЁЯС╢ тЬи ЁЯСитАНЁЯСйтАНЁЯСж\n<i>╨а╨░╨╖╨┤╨░╨╡╤В╤Б╤П ╨┐╨╡╤А╨▓╤Л╨╣ ╨║╤А╨╕╨║!</i>","ЁЯОЙ ЁЯН╝ ЁЯз╕\n<i>╨Э╨╛╨▓╨░╤П ╨╢╨╕╨╖╨╜╤М ╨╜╨░╤З╨░╨╗╨░╤Б╤М!</i>"]
    if event_type == "marry": return ["ЁЯТР ЁЯН╖ ЁЯСйтАНтЭдя╕ПтАНЁЯСи\n<i>╨а╨╛╨╝╨░╨╜╤В╨╕╤З╨╡╤Б╨║╨╕╨╣ ╤Г╨╢╨╕╨╜...</i>","ЁЯд╡ ЁЯС░ ЁЯТН\n<i>╨Я╤А╨╡╨┤╨╗╨╛╨╢╨╡╨╜╨╕╨╡ ╤А╤Г╨║╨╕ ╨╕ ╤Б╨╡╤А╨┤╤Ж╨░!</i>","ЁЯеВ ЁЯОЙ ЁЯТЦ\n<i>╨б╨▓╨░╨┤╤М╨▒╨░!</i>"]
    if event_type == "prison": return ["ЁЯЪФ ЁЯЪи ЁЯПГтАНтЩВя╕П\n<i>╨Я╨╛╨│╨╛╨╜╤П...</i>","ЁЯСотАНтЩВя╕П ЁЯФЧ ЁЯСи\n<i>╨Ч╨░╨┤╨╡╤А╨╢╨░╨╜╨╕╨╡...</i>","тЫУ ЁЯз▒ ЁЯЪк\n<i>╨Ф╨▓╨╡╤А╤М ╨║╨░╨╝╨╡╤А╤Л ╨╖╨░╤Е╨╗╨╛╨┐╨╜╤Г╨╗╨░╤Б╤М.</i>"]
    if event_type == "death": return ["ЁЯПе ЁЯЫМ ЁЯТФ\n<i>╨Ч╨┤╨╛╤А╨╛╨▓╤М╨╡ ╨┐╨╛╨┤╨▓╨╛╨┤╨╕╤В...</i>","ЁЯХпя╕П тШБя╕П\n<i>╨Я╨╛╤Б╨╗╨╡╨┤╨╜╨╕╨╣ ╨▓╨╖╨┤╨╛╤Е...</i>","ЁЯкж ЁЯеА ЁЯХКя╕П\n<i>╨Ц╨╕╨╖╨╜╤М ╨╛╨║╨╛╨╜╤З╨╡╨╜╨░.</i>"]
    return []

def get_scene_visuals(scene_type, gender, ethnicity=None, region=None, age=None):
    player = get_person_emoji("player", gender=gender, ethnicity=ethnicity, region=region, age=age)
    scenes = {"military":f"ЁЯОЦ ЁЯкЦ {player} ЁЯкЦ ЁЯЫб","criminal":f"ЁЯХ╢ ЁЯФл {player} ЁЯТ░ ЁЯТг","child":f"ЁЯПа ЁЯМ│ {player} ЁЯз╕ тШАя╕П","toddler":f"ЁЯН╝ ЁЯз╕ {player} ЁЯОИ ЁЯМЯ","school":f"ЁЯПл {player} ЁЯУЪ ЁЯОТ ЁЯНО","rich":f"ЁЯП░ ЁЯЪЧ ЁЯТ░ {player} ЁЯеВ ЁЯЫе","office":f"ЁЯПв ЁЯзСтАНЁЯТ╗ {player} ЁЯУК тШХ","office_angry":f"ЁЯПв ЁЯШб {player} ЁЯТв ЁЯУЙ","hospital":f"ЁЯПе ЁЯЫМ {player} ЁЯТЙ ЁЯй║","prison":f"тЫУ ЁЯз▒ {player} ЁЯЪФ ЁЯХ╢","fight":f"ЁЯСК ЁЯТе {player} ЁЯеК ЁЯдХ","love":f"тЭдя╕П {player} ЁЯМ╣ ЁЯТС ЁЯТР","wedding":f"ЁЯТН ЁЯд╡ ЁЯС░ {player} ЁЯОЙ","sad":f"ЁЯМз {player} тШВя╕П ЁЯШФ ЁЯТз","police":f"ЁЯЪФ ЁЯТ╡ {player} ЁЯЪи ЁЯШ░","money_win":f"ЁЯТ░ ЁЯдС {player} ЁЯТО ЁЯО░","money_lose":f"ЁЯТ╕ ЁЯШн {player} ЁЯХ│ ЁЯУЙ"}
    return scenes.get(scene_type, f"ЁЯМЖ {player} ЁЯПЩ ЁЯЪ╢")

def fmt_money(amount_usd, country):
    return f"{int(amount_usd * country[8]):,} {country[9]}".replace(",", " ")

def get_wealth_status(clean, dirty, l=None):
    total = clean + dirty
    if l and l.get("properties"): total += sum(p["value"] for p in l["properties"])
    if l and l.get("cars"): total += sum(c["value"] for c in l["cars"])
    if total < 0: return "ЁЯТ╕ ╨Т ╨┤╨╛╨╗╨│╨░╤Е"
    if total < 500: return "ЁЯеА ╨Э╨╕╤Й╨╕╨╣"
    if total < 5000: return "ЁЯСХ ╨С╨╡╨┤╨╜╤Л╨╣"
    if total < 20000: return "ЁЯФз ╨а╨░╨▒╨╛╤З╨╕╨╣ ╨║╨╗╨░╤Б╤Б"
    if total < 100000: return "ЁЯПа ╨б╤А╨╡╨┤╨╜╨╕╨╣ ╨║╨╗╨░╤Б╤Б"
    if total < 500000: return "ЁЯТ╝ ╨Ч╨░╨╢╨╕╤В╨╛╤З╨╜╤Л╨╣"
    if total < 2000000: return "ЁЯТО ╨С╨╛╨│╨░╤З"
    return "ЁЯСС ╨н╨╗╨╕╤В╨░"

def weighted_country():
    r = random.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def get_ethnicity(region):
    r = random.random() * 100; cum = 0
    for name, chance, prejudice in ETHNICITIES.get(region, [("╨Ь╨╡╤Б╤В╨╜╤Л╨╣",100,None)]):
        cum += chance
        if r <= cum: return name, prejudice
    return "╨Ь╨╡╤Б╤В╨╜╤Л╨╣", None

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
        if n["death_age"] < 3: return "╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ ╨╝╨╗╨░╨┤╨╡╨╜╤З╨╡╤Б╤В╨▓╨╡"
        elif n["death_age"] < 18: return f"╤Г╨╝╨╡╤А(╨╗╨░) ╨╛╤В ╨▒╨╛╨╗╨╡╨╖╨╜╨╕ ╨▓ {get_age_str(n['death_age'])}"
        elif n["trajectory"] == "criminal": return f"╨┐╨╛╨│╨╕╨▒(╨╗╨░) ╨▓ ╤А╨░╨╖╨▒╨╛╤А╨║╨╡ ╨▓ {get_age_str(n['death_age'])}"
        else: return f"╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ {get_age_str(n['death_age'])}"
    if age < 13:
        if n["trajectory"] == "unfortunate": return "╨╢╨╕╨▓╨╡╤В ╨▓ ╨▒╨╡╨┤╨╜╨╛╤Б╤В╨╕"
        elif n["trajectory"] == "prosperous": return "╤Е╨╛╨┤╨╕╤В ╨▓ ╤Н╨╗╨╕╤В╨╜╤Г╤О ╤И╨║╨╛╨╗╤Г"
        else: return "╤Е╨╛╨┤╨╕╤В ╨▓ ╤И╨║╨╛╨╗╤Г"
    elif age < 25:
        if n["trajectory"] == "criminal": return "╤Б╨▓╤П╨╖╨░╨╗╤Б╤П ╤Б ╨▒╨░╨╜╨┤╨╛╨╣" if g_m else "╤Б╨▓╤П╨╖╨░╨╗╨░╤Б╤М ╤Б ╨▒╨░╨╜╨┤╨╛╨╣"
        elif n["trajectory"] == "prosperous": return "╨┐╨╛╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ ╨▓╤Г╨╖" if g_m else "╨┐╨╛╤Б╤В╤Г╨┐╨╕╨╗╨░ ╨▓ ╨▓╤Г╨╖"
        else: return "╤А╨░╨▒╨╛╤В╨░╨╡╤В"
    elif age < 55:
        if n["trajectory"] == "criminal": return "╤Б╨╕╨┤╨╕╤В ╨▓ ╤В╤О╤А╤М╨╝╨╡"
        elif n["trajectory"] == "prosperous": return "╤Б╤В╨░╨╗ ╨▒╨╛╨│╨░╤В╤Л╨╝" if g_m else "╤Б╤В╨░╨╗╨░ ╨▒╨╛╨│╨░╤В╨╛╨╣"
        else: return "╤А╨░╨▒╨╛╤В╨░╨╡╤В ╨╜╨░ ╨╖╨░╨▓╨╛╨┤╨╡"
    return "╨╜╨░ ╨┐╨╡╨╜╤Б╨╕╨╕"

def get_neighbor_final(n):
    if n["death_age"] < 3: return "╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ ╨╝╨╗╨░╨┤╨╡╨╜╤З╨╡╤Б╤В╨▓╨╡"
    elif n["trajectory"] == "criminal": return f"╨┐╨╛╨│╨╕╨▒(╨╗╨░) ╨▓ ╤А╨░╨╖╨▒╨╛╤А╨║╨╡ ╨▓ {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "prosperous": return f"╤Г╨╝╨╡╤А(╨╗╨░) ╨▒╨╛╨│╨░╤В╤Л╨╝(╨╛╨╣) ╨▓ {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "unfortunate": return f"╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ ╨▒╨╡╨┤╨╜╨╛╤Б╤В╨╕ ╨▓ {get_age_str(n['death_age'])}"
    else: return f"╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ {get_age_str(n['death_age'])}"

# ================= NPC ╨Ш ╨Я╨а╨Х╨Ф╨л╨б╨в╨Ю╨а╨Ш╨п =================
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
            add_to_life_map(l, f"╨г╨╝╨╡╤А(╨╗╨░) {role_ru} {npc['name']}")
            if npc["role"] in ("mother","father","friend"):
                l["happiness"] = max(0, l["happiness"] - 5)

def get_npc_epilogue(npc):
    role_ru = NPC_ROLES_DESC.get(npc["role"], npc["role"])
    fate = f"╤Г╨╝╨╡╤А(╨╗╨░) ╨▓ {get_age_str(npc['death_age'])}" if npc["dead"] else "╨╢╨╕╨▓(╨░)"
    rel = npc["relation"]
    if rel >= 60: mood = "╨▒╤Л╨╗(╨░) ╤А╤П╨┤╨╛╨╝"
    elif rel >= 20: mood = "╤В╤С╨┐╨╗╤Л╨╡ ╨╛╤В╨╜╨╛╤И╨╡╨╜╨╕╤П"
    elif rel >= -20: mood = "╨╜╨╡╨╣╤В╤А╨░╨╗╤М╨╜╨╛"
    else: mood = "╨╕╤Б╨┐╨╛╤А╤В╨╕╨╗╨╕╤Б╤М"
    return f"тАв {role_ru} {npc['name']}: {fate} тАФ {mood}"

def generate_world_context(country):
    year = 2025 + random.randint(-5, 5)
    global_states = [
        {"icon":"ЁЯМН","title":"╨Ю╤В╨╜╨╛╤Б╨╕╤В╨╡╨╗╤М╨╜╨░╤П ╤Б╤В╨░╨▒╨╕╨╗╤М╨╜╨╛╤Б╤В╤М","desc":"╨Э╨╡╤В ╨║╤А╤Г╨┐╨╜╤Л╤Е ╨▓╨╛╨╣╨╜. ╨н╨║╨╛╨╜╨╛╨╝╨╕╨║╨░ ╤А╨░╤Б╤В╤С╤В."},
        {"icon":"тЪая╕П","title":"╨У╨╗╨╛╨▒╨░╨╗╤М╨╜╨░╤П ╨╜╨░╨┐╤А╤П╨╢╤С╨╜╨╜╨╛╤Б╤В╤М","desc":"╨б╨░╨╜╨║╤Ж╨╕╨╕, ╨║╨╛╨╜╤Д╨╗╨╕╨║╤В╤Л, ╨│╨╛╨╜╨║╨░ ╨▓╨╛╨╛╤А╤Г╨╢╨╡╨╜╨╕╨╣."},
        {"icon":"ЁЯУИ","title":"╨н╨║╨╛╨╜╨╛╨╝╨╕╤З╨╡╤Б╨║╨╕╨╣ ╨┐╨╛╨┤╤К╤С╨╝","desc":"╨а╤Л╨╜╨║╨╕ ╤А╨░╤Б╤В╤Г╤В, ╨╜╨╛╨▓╤Л╨╡ ╤В╨╡╤Е╨╜╨╛╨╗╨╛╨│╨╕╨╕."},
        {"icon":"ЁЯУЙ","title":"╨Ь╨╕╤А╨╛╨▓╨╛╨╣ ╨║╤А╨╕╨╖╨╕╤Б","desc":"╨Ш╨╜╤Д╨╗╤П╤Ж╨╕╤П, ╨▒╨╡╨╖╤А╨░╨▒╨╛╤В╨╕╤Ж╨░."},
        {"icon":"ЁЯжа","title":"╨Я╨╛╤Б╨╗╨╡ ╨┐╨░╨╜╨┤╨╡╨╝╨╕╨╕","desc":"╨Ь╨╕╤А ╨▓╨╛╤Б╤Б╤В╨░╨╜╨░╨▓╨╗╨╕╨▓╨░╨╡╤В╤Б╤П."},
    ]
    global_state = random.choice(global_states)
    region_news = {
        "south_asia":["ЁЯМ╛ ╨Р╨│╤А╨░╤А╨╜╤Л╨╣ ╤Б╨╡╨║╤В╨╛╤А ╨╝╨╛╨┤╨╡╤А╨╜╨╕╨╖╨╕╤А╤Г╨╡╤В╤Б╤П.","ЁЯПЩ ╨У╨╛╤А╨╛╨┤╨░ ╤А╨░╤Б╤В╤Г╤В ╤Б╤В╤А╨╡╨╝╨╕╤В╨╡╨╗╤М╨╜╨╛.","тЪЦя╕П ╨С╨╛╤А╤М╨▒╨░ ╤Б ╨▒╨╡╨┤╨╜╨╛╤Б╤В╤М╤О.","ЁЯЪВ ╨Э╨╛╨▓╤Л╨╡ ╨╢╨╡╨╗╨╡╨╖╨╜╤Л╨╡ ╨┤╨╛╤А╨╛╨│╨╕."],
        "east_asia":["ЁЯПн ╨Р╨▓╤В╨╛╨╝╨░╤В╨╕╨╖╨░╤Ж╨╕╤П ╤Б╨╛╨║╤А╨░╤Й╨░╨╡╤В ╤А╨░╨▒╨╛╤З╨╕╨╡ ╨╝╨╡╤Б╤В╨░.","ЁЯЪА ╨в╨╡╤Е╨╜╨╛╨╗╨╛╨│╨╕╤З╨╡╤Б╨║╨╕╨╣ ╨▒╤Г╨╝.","ЁЯС┤ ╨б╤В╨░╤А╨╡╨╜╨╕╨╡ ╨╜╨░╤Б╨╡╨╗╨╡╨╜╨╕╤П.","ЁЯУ▒ ╨Ь╨╛╨▒╨╕╨╗╤М╨╜╤Л╨╡ ╨┐╨╗╨░╤В╨╡╨╢╨╕."],
        "southeast_asia":["ЁЯПЦ ╨в╤Г╤А╨╕╨╖╨╝ ╨┐╤А╨╕╨╜╨╛╤Б╨╕╤В ╨┤╨╡╨╜╤М╨│╨╕.","ЁЯПЧ ╨б╤В╤А╨╛╨╕╤В╨╡╨╗╤М╤Б╤В╨▓╨╛ ╨╕╨╜╤Д╤А╨░╤Б╤В╤А╤Г╨║╤В╤Г╤А╤Л.","ЁЯТ╝ ╨Ь╨╜╨╛╨│╨╕╨╡ ╤Г╨╡╨╖╨╢╨░╤О╤В ╨╖╨░ ╨│╤А╨░╨╜╨╕╤Ж╤Г.","ЁЯМК ╨Э╨░╨▓╨╛╨┤╨╜╨╡╨╜╨╕╤П."],
        "africa":["ЁЯМН ╨Ь╨╛╨╗╨╛╨┤╨╛╨╡ ╨╜╨░╤Б╨╡╨╗╨╡╨╜╨╕╨╡.","ЁЯТО ╨С╨╛╨│╨░╤В╤Л╨╡ ╤А╨╡╤Б╤Г╤А╤Б╤Л.","тЪФя╕П ╨Т ╨╜╨╡╨║╨╛╤В╨╛╤А╤Л╤Е ╤А╨╡╨│╨╕╨╛╨╜╨░╤Е ╨╜╨╡╤Б╨┐╨╛╨║╨╛╨╣╨╜╨╛.","ЁЯУЪ ╨а╨░╤Б╤В╤С╤В ╨┤╨╛╤Б╤В╤Г╨┐ ╨║ ╨╛╨▒╤А╨░╨╖╨╛╨▓╨░╨╜╨╕╤О."],
        "arab":["ЁЯЫв ╨Э╨╡╤Д╤В╤М тАФ ╨│╨╗╨░╨▓╨╜╤Л╨╣ ╤А╨╡╤Б╤Г╤А╤Б.","ЁЯПЩ ╨Ф╤Г╨▒╨░╨╣ тАФ ╤Б╨╕╨╝╨▓╨╛╨╗ ╨▒╨╛╨│╨░╤В╤Б╤В╨▓╨░.","тЪЦя╕П ╨Ь╨╡╨╜╤П╤О╤Й╨╕╨╡╤Б╤П ╤В╤А╨░╨┤╨╕╤Ж╨╕╨╕.","ЁЯМЮ ╨б╨╛╨╗╨╜╨╡╤З╨╜╨░╤П ╤Н╨╜╨╡╤А╨│╨╡╤В╨╕╨║╨░."],
        "latam":["ЁЯТГ ╨Ц╨╕╨▓╨░╤П ╨║╤Г╨╗╤М╤В╤Г╤А╨░.","тЪая╕П ╨Я╤А╨╡╤Б╤В╤Г╨┐╨╜╨╛╤Б╤В╤М ╨▓ ╨│╨╛╤А╨╛╨┤╨░╤Е.","ЁЯМ│ ╨Т╤Л╤А╤Г╨▒╨║╨░ ╨╗╨╡╤Б╨╛╨▓.","ЁЯОн ╨д╨╡╤Б╤В╨╕╨▓╨░╨╗╨╕."],
        "europe":["ЁЯЗкЁЯЗ║ ╨Х╨┤╨╕╨╜╤Б╤В╨▓╨╛ ╨╕ ╤Б╤В╨░╨▒╨╕╨╗╤М╨╜╨╛╤Б╤В╤М.","тЩ╗я╕П ╨Ч╨╡╨╗╤С╨╜╨░╤П ╤Н╨╜╨╡╤А╨│╨╡╤В╨╕╨║╨░.","ЁЯС┤ ╨б╤В╨░╤А╨╡╨╜╨╕╨╡ ╨╕ ╨╝╨╕╨│╤А╨░╤Ж╨╕╤П.","ЁЯЪД ╨б╨║╨╛╤А╨╛╤Б╤В╨╜╤Л╨╡ ╨┐╨╛╨╡╨╖╨┤╨░."],
        "post_soviet":["ЁЯПЪ ╨Э╨░╤Б╨╗╨╡╨┤╨╕╨╡ ╨б╨б╨б╨а.","ЁЯТ╝ ╨Ь╨╛╨╗╨╛╨┤╤С╨╢╤М ╨╕╤Й╨╡╤В ╤А╨░╨▒╨╛╤В╤Г.","ЁЯУ║ ╨Т╨╗╨╕╤П╨╜╨╕╨╡ ╨│╨╛╤Б╤Г╨┤╨░╤А╤Б╤В╨▓╨░.","ЁЯЫг ╨б╤В╤А╨╛╨╕╤В╨╡╨╗╤М╤Б╤В╨▓╨╛ ╨┤╨╛╤А╨╛╨│."],
        "developed":["ЁЯТ╗ ╨в╨╡╤Е╨╜╨╛╨╗╨╛╨│╨╕╨╕ ╨╝╨╡╨╜╤П╤О╤В ╨╢╨╕╨╖╨╜╤М.","ЁЯПе ╨Ф╨╛╤Б╤В╤Г╨┐╨╜╨░╤П ╨╝╨╡╨┤╨╕╤Ж╨╕╨╜╨░.","ЁЯОУ ╨Т╤Л╤Б╨╛╨║╨╕╨╣ ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨╛╨▒╤А╨░╨╖╨╛╨▓╨░╨╜╨╕╤П.","ЁЯЪЧ ╨н╨╗╨╡╨║╤В╤А╨╛╨╝╨╛╨▒╨╕╨╗╨╕."],
    }
    positive_news = ["ЁЯОЙ ╨б╨┐╨╛╤А╤В╨╕╨▓╨╜╤Л╨╡ ╨╕╨│╤А╤Л.","ЁЯПЖ ╨Т╨░╨╢╨╜╨╛╨╡ ╨╛╤В╨║╤А╤Л╤В╨╕╨╡.","ЁЯМ╛ ╨е╨╛╤А╨╛╤И╨╕╨╣ ╤Г╤А╨╛╨╢╨░╨╣.","ЁЯЫг ╨Э╨╛╨▓╨░╤П ╨╝╨░╨│╨╕╤Б╤В╤А╨░╨╗╤М.","ЁЯУ▒ ╨в╨╡╤Е╨╜╨╛╨╗╨╛╨│╨╕╤З╨╡╤Б╨║╨╕╨╣ ╤Б╤В╨░╤А╤В╨░╨┐.","ЁЯОм ╨Э╨░╤Ж╨╕╨╛╨╜╨░╨╗╤М╨╜╤Л╨╣ ╤Д╨╕╨╗╤М╨╝ ╨┐╨╛╨╗╤Г╤З╨╕╨╗ ╨╜╨░╨│╤А╨░╨┤╤Г."]
    negative_news = ["тЪая╕П ╨б╨║╨░╨╜╨┤╨░╨╗ ╨▓ ╨┐╤А╨░╨▓╨╕╤В╨╡╨╗╤М╤Б╤В╨▓╨╡.","ЁЯМК ╨Э╨░╨▓╨╛╨┤╨╜╨╡╨╜╨╕╨╡.","ЁЯУЙ ╨а╨╛╤Б╤В ╤Ж╨╡╨╜.","ЁЯЪФ ╨Ю╨│╤А╨░╨▒╨╗╨╡╨╜╨╕╤П.","ЁЯПн ╨Ч╨░╨▒╨░╤Б╤В╨╛╨▓╨║╨░.","ЁЯФе ╨Ы╨╡╤Б╨╜╤Л╨╡ ╨┐╨╛╨╢╨░╤А╤Л."]
    return {
        "year": year, "global_icon": global_state["icon"], "global_title": global_state["title"], "global_desc": global_state["desc"],
        "region_news": random.choice(region_news.get(country[2], ["╨Ь╨╕╤А ╨╝╨╡╨╜╤П╨╡╤В╤Б╤П."])),
        "extra_news": random.choice(positive_news + negative_news),
    }

def generate_family_background(country, gender, start_cash):
    c_economy = country[7]
    if start_cash < c_economy * 0.5: wealth_class = "poor"
    elif start_cash < c_economy * 1.5: wealth_class = "middle"
    else: wealth_class = "rich"

    if wealth_class == "poor":
        father_occ = random.choice(["╤А╨░╨▒╨╛╤В╨░╨╡╤В ╨╜╨░ ╤Д╨░╨▒╤А╨╕╨║╨╡","╨│╤А╤Г╨╖╤З╨╕╨║ ╨▓ ╨┐╨╛╤А╤В╤Г","╨╝╨╡╨╗╨║╨╕╨╣ ╤Д╨╡╤А╨╝╨╡╤А","╨║╤Г╤А╤М╨╡╤А","╤Б╤В╨╛╤А╨╛╨╢ ╨╜╨░ ╤Б╨║╨╗╨░╨┤╨╡","╤А╨░╨╖╨╜╨╛╤А╨░╨▒╨╛╤З╨╕╨╣","╤З╨╕╤Б╤В╨╕╨╗╤М╤Й╨╕╨║ ╨╛╨▒╤Г╨▓╨╕","╨┐╤А╨╛╨┤╨░╨▓╨╡╤Ж ╨╜╨░ ╤А╤Л╨╜╨║╨╡"])
        mother_occ = random.choice(["╤А╨░╨▒╨╛╤В╨░╨╡╤В ╤Г╨▒╨╛╤А╤Й╨╕╤Ж╨╡╨╣","╤И╨▓╨╡╤П ╨╜╨░ ╨┤╨╛╨╝╤Г","╤В╨╛╤А╨│╤Г╨╡╤В ╨╜╨░ ╤А╤Л╨╜╨║╨╡","╨┐╨╛╤Б╤Г╨┤╨╛╨╝╨╛╨╣╨║╨░ ╨▓ ╨║╨░╤Д╨╡","╨┤╨╛╨╝╨╛╤Е╨╛╨╖╤П╨╣╨║╨░","╤Б╨╛╨▒╨╕╤А╨░╨╡╤В ╨┐╨╗╨░╤Б╤В╨╕╨║","╨┐╤А╨╕╤Б╨╗╤Г╨│╨░ ╨▓ ╨▒╨╛╨│╨░╤В╨╛╨╝ ╨┤╨╛╨╝╨╡"])
        housing = random.choice(["╨║╤А╨╛╤И╨╡╤З╨╜╨░╤П ╤Е╨╕╨╢╨╕╨╜╨░","╨║╨╛╨╝╨╜╨░╤В╨░ ╨▓ ╤В╤А╤Г╤Й╨╛╨▒╨░╤Е","╨┤╨╛╨╝╨╕╨║ ╨▓ ╨┤╨╡╤А╨╡╨▓╨╜╨╡","╨┐╨╛╨┤╨▓╨░╨╗","╨╛╨▒╤Й╨╡╨╢╨╕╤В╨╕╨╡ ╨┤╨╗╤П ╤А╨░╨▒╨╛╤З╨╕╤Е","╨║╨▓╨░╤А╤В╨╕╤А╨░-╤Б╤В╤Г╨┤╨╕╤П"])
        living = "╨в╨╡╤Б╨╜╨╛╨╡ ╨╢╨╕╨╗╨╕╤Й╨╡, ╨▓╨╛╨┤╨░ ╨╕╨╖ ╨║╨╛╨╗╨╛╨╜╨║╨╕."
        location = random.choice(["╨│╨╗╤Г╤Е╨░╤П ╨┤╨╡╤А╨╡╨▓╨╜╤П","╤В╤А╤Г╤Й╨╛╨▒╤Л ╨▒╨╛╨╗╤М╤И╨╛╨│╨╛ ╨│╨╛╤А╨╛╨┤╨░","╨╛╨║╤А╨░╨╕╨╜╨░ ╨╝╨╡╨│╨░╨┐╨╛╨╗╨╕╤Б╨░","╤А╨░╨▒╨╛╤З╨╕╨╣ ╨║╨▓╨░╤А╤В╨░╨╗","╨┐╨╛╤Б╤С╨╗╨╛╨║ ╤Г ╤Д╨░╨▒╤А╨╕╨║╨╕"])
    elif wealth_class == "middle":
        father_occ = random.choice(["╨╕╨╜╨╢╨╡╨╜╨╡╤А","╤Г╤З╨╕╤В╨╡╨╗╤М","╨▒╤Г╤Е╨│╨░╨╗╤В╨╡╤А","╨▓╤А╨░╤З ╨▓ ╨┐╨╛╨╗╨╕╨║╨╗╨╕╨╜╨╕╨║╨╡","╨╝╨╡╤Е╨░╨╜╨╕╨║","╨╝╨╡╨╜╨╡╨┤╨╢╨╡╤А ╨▓ ╨╛╤Д╨╕╤Б╨╡","╤В╨╛╤А╨│╨╛╨▓╤Л╨╣ ╨┐╤А╨╡╨┤╤Б╤В╨░╨▓╨╕╤В╨╡╨╗╤М","╨▓╨╛╨┤╨╕╤В╨╡╨╗╤М ╨░╨▓╤В╨╛╨▒╤Г╤Б╨░"])
        mother_occ = random.choice(["╤Г╤З╨╕╤В╨╡╨╗╤М╨╜╨╕╤Ж╨░","╨╝╨╡╨┤╤Б╨╡╤Б╤В╤А╨░","╨┐╤А╨╛╨┤╨░╨▓╨╡╤Ж ╨▓ ╨╝╨░╨│╨░╨╖╨╕╨╜╨╡","╨┐╨░╤А╨╕╨║╨╝╨░╤Е╨╡╤А","╨┐╨╛╨▓╨░╤А","╤Б╨╡╨║╤А╨╡╤В╨░╤А╤М","╨▒╨╕╨▒╨╗╨╕╨╛╤В╨╡╨║╨░╤А╤М"])
        housing = random.choice(["╨║╨▓╨░╤А╤В╨╕╤А╨░ ╨▓ ╨┐╨░╨╜╨╡╨╗╤М╨╜╨╛╨╝ ╨┤╨╛╨╝╨╡","╨╜╨╡╨▒╨╛╨╗╤М╤И╨╛╨╣ ╨┤╨╛╨╝ ╨╜╨░ ╨╛╨║╤А╨░╨╕╨╜╨╡","╨╢╨╕╨╗╤М╤С ╤Б ╨╕╨┐╨╛╤В╨╡╨║╨╛╨╣","╨┤╨▓╤Г╤Е╨║╨╛╨╝╨╜╨░╤В╨╜╨░╤П ╨║╨▓╨░╤А╤В╨╕╤А╨░"])
        living = "╨б╨║╤А╨╛╨╝╨╜╨░╤П, ╨╜╨╛ ╨╛╨┐╤А╤П╤В╨╜╨░╤П ╨║╨▓╨░╤А╤В╨╕╤А╨░."
        location = random.choice(["╤Б╨┐╨░╨╗╤М╨╜╤Л╨╣ ╤А╨░╨╣╨╛╨╜","╨┐╤А╨╕╨│╨╛╤А╨╛╨┤","╤А╨░╨▒╨╛╤З╨╕╨╣ ╨┐╤А╨╕╨│╨╛╤А╨╛╨┤","╨╜╨╡╨▒╨╛╨╗╤М╤И╨╛╨╣ ╨│╨╛╤А╨╛╨┤"])
    else:
        father_occ = random.choice(["╨▓╨╗╨░╨┤╨╡╨╗╨╡╤Ж ╤Д╨╕╤А╨╝╤Л","╨░╨┤╨▓╨╛╨║╨░╤В","╨║╤А╤Г╨┐╨╜╤Л╨╣ ╨▒╨╕╨╖╨╜╨╡╤Б╨╝╨╡╨╜","╨┤╨╡╨┐╤Г╤В╨░╤В ╨┐╨░╤А╨╗╨░╨╝╨╡╨╜╤В╨░","╤В╨╛╨┐-╨╝╨╡╨╜╨╡╨┤╨╢╨╡╤А ╨║╨╛╤А╨┐╨╛╤А╨░╤Ж╨╕╨╕","╨▓╤А╨░╤З-╤Е╨╕╤А╤Г╤А╨│ ╨▓ ╤З╨░╤Б╤В╨╜╨╛╨╣ ╨║╨╗╨╕╨╜╨╕╨║╨╡"])
        mother_occ = random.choice(["╤Г╨┐╤А╨░╨▓╨╗╤П╨╡╤В ╤Б╨╡╨╝╨╡╨╣╨╜╤Л╨╝ ╨▒╨╕╨╖╨╜╨╡╤Б╨╛╨╝","╨┤╨╕╨╖╨░╨╣╨╜╨╡╤А ╨╕╨╜╤В╨╡╤А╤М╨╡╤А╨╛╨▓","╨╕╨╖╨▓╨╡╤Б╤В╨╜╤Л╨╣ ╨▓╤А╨░╤З","╨┐╤А╨╛╤Д╨╡╤Б╤Б╨╛╤А ╤Г╨╜╨╕╨▓╨╡╤А╤Б╨╕╤В╨╡╤В╨░","╤Б╨▓╨╡╤В╤Б╨║╨░╤П ╨╗╤М╨▓╨╕╤Ж╨░","╨░╨┤╨▓╨╛╨║╨░╤В ╨┐╨╛ ╨▒╨╕╨╖╨╜╨╡╤Б╤Г"])
        housing = random.choice(["╤А╨╛╤Б╨║╨╛╤И╨╜╤Л╨╣ ╨╛╤Б╨╛╨▒╨╜╤П╨║","╨┐╨╡╨╜╤В╤Е╨░╤Г╤Б ╨▓ ╤Ж╨╡╨╜╤В╤А╨╡","╨┐╨╛╨╝╨╡╤Б╤В╤М╨╡ ╨╖╨░ ╨│╨╛╤А╨╛╨┤╨╛╨╝","╨┤╨╛╨╝ ╤Б ╨▒╨░╤Б╤Б╨╡╨╣╨╜╨╛╨╝ ╨╕ ╤Б╨░╨┤╨╛╨╝"])
        living = "╨Я╤А╨╛╤Б╤В╨╛╤А╨╜╤Л╨╣ ╨┤╨╛╨╝ ╤Б ╨┐╤А╨╕╤Б╨╗╤Г╨│╨╛╨╣."
        location = random.choice(["╨┐╤А╨╡╤Б╤В╨╕╨╢╨╜╤Л╨╣ ╤А╨░╨╣╨╛╨╜ ╤Б╤В╨╛╨╗╨╕╤Ж╤Л","╨╖╨░╨║╤А╤Л╤В╤Л╨╣ ╨║╨╛╤В╤В╨╡╨┤╨╢╨╜╤Л╨╣ ╨┐╨╛╤Б╤С╨╗╨╛╨║","╤Ж╨╡╨╜╤В╤А ╨│╨╛╤А╨╛╨┤╨░"])

    father_name = random.choice(NAMES[country[2]]["m"])
    mother_name = random.choice(NAMES[country[2]]["f"])
    sib_count = random.choices([0,1,2,3,4], weights=[20,35,25,15,5])[0]
    siblings = []
    for _ in range(sib_count):
        sg = random.choice(["m","f"]); sn = random.choice(NAMES[country[2]][sg])
        if wealth_class == "poor": st = random.choice(["╤Е╨╛╨┤╨╕╤В ╨▓ ╤И╨║╨╛╨╗╤Г, ╨┐╨╛╨╝╨╛╨│╨░╨╡╤В ╤А╨╛╨┤╨╕╤В╨╡╨╗╤П╨╝","╤А╨░╨▒╨╛╤В╨░╨╡╤В ╤Б 10 ╨╗╨╡╤В","╨┐╤А╨╕╤Б╨╝╨░╤В╤А╨╕╨▓╨░╨╡╤В ╨╖╨░ ╨╝╨╗╨░╨┤╤И╨╕╨╝╨╕"])
        elif wealth_class == "middle": st = random.choice(["╤Г╤З╨╕╤В╤Б╤П ╨▓ ╤И╨║╨╛╨╗╨╡","╤Е╨╛╨┤╨╕╤В ╨▓ ╨╝╤Г╨╖╤Л╨║╨░╨╗╤М╨╜╤Г╤О ╤И╨║╨╛╨╗╤Г","╨╖╨░╨╜╨╕╨╝╨░╨╡╤В╤Б╤П ╤Б╨┐╨╛╤А╤В╨╛╨╝"])
        else: st = random.choice(["╤Е╨╛╨┤╨╕╤В ╨▓ ╤З╨░╤Б╤В╨╜╤Г╤О ╤И╨║╨╛╨╗╤Г","╨╖╨░╨╜╨╕╨╝╨░╨╡╤В╤Б╤П ╤Б ╤А╨╡╨┐╨╡╤В╨╕╤В╨╛╤А╨░╨╝╨╕","╤Г╤З╨╕╤В╤Б╤П ╨╖╨░ ╨│╤А╨░╨╜╨╕╤Ж╨╡╨╣"])
        siblings.append({"name":sn,"gender":sg,"status":st,"age_diff":random.randint(-4,6)})
    grandparents = []
    for side in ["╨╝╨░╨╝╤Л","╨┐╨░╨┐╤Л"]:
        for role in ["╨┤╨╡╨┤╤Г╤И╨║╨░","╨▒╨░╨▒╤Г╤И╨║╨░"]:
            grandparents.append({"role":f"{role} ╨┐╨╛ ╨╗╨╕╨╜╨╕╨╕ {side}","alive":random.random()<0.55})
    return {"wealth_class":wealth_class,"father_name":father_name,"father_occupation":father_occ,"mother_name":mother_name,"mother_occupation":mother_occ,"housing":housing,"living_conditions":living,"siblings":siblings,"siblings_count":sib_count,"grandparents":grandparents,"location":location}

def format_backstory(l):
    family = l.get("family",{}); world = l.get("world_context",{}); c = l["country"]
    eth = l.get("ethnicity"); reg = c[2]
    world_text = (f"ЁЯМН <b>╨У╨╛╨┤ {world['year']}. ╨Ь╨╕╤А, ╨▓ ╨║╨╛╤В╨╛╤А╤Л╨╣ ╤В╤Л ╨┐╤А╨╕╤Е╨╛╨┤╨╕╤И╤М</b>\n\n"
                  f"{world['global_icon']} <b>{world['global_title']}</b>\n<i>{world['global_desc']}</i>\n\n"
                  f"<b>╨Т {c[1]} {c[0]}:</b>\n{world['region_news']}\n{world['extra_news']}\n\n"
                  f"<i>╨н╤В╨╛ ╨╝╨╕╤А, ╨▓ ╨║╨╛╤В╨╛╤А╨╛╨╝ ╤В╨╡╨▒╨╡ ╨┐╤А╨╡╨┤╤Б╤В╨╛╨╕╤В ╨╢╨╕╤В╤М.</i>")
    wealth_emoji = {"poor":"ЁЯеА","middle":"ЁЯПа","rich":"ЁЯСС"}
    wealth_ru = {"poor":"╨▒╨╡╨┤╨╜╨╛╨╣","middle":"╤Б╤А╨╡╨┤╨╜╨╡╨╣","rich":"╨▒╨╛╨│╨░╤В╨╛╨╣"}

    ic_father = get_person_emoji("father", "m", eth, reg)
    ic_mother = get_person_emoji("mother", "f", eth, reg)
    ic_me = get_person_emoji("player", l["gender"], eth, reg, age=0)

    family_text = (f"{wealth_emoji[family['wealth_class']]} <b>╨в╤Л ╤А╨╛╨┤╨╕╨╗╤Б╤П ╨▓ {wealth_ru[family['wealth_class']]} ╤Б╨╡╨╝╤М╨╡</b>\n\n"
                   f"{ic_father} <b>╨Ю╤В╨╡╤Ж:</b> {family['father_name']} тАФ {family['father_occupation']}\n"
                   f"{ic_mother} <b>╨Ь╨░╤В╤М:</b> {family['mother_name']} тАФ {family['mother_occupation']}\n\n"
                   f"ЁЯПб <b>╨Ц╨╕╨╗╨╕╤Й╨╡:</b> {family['housing']}\n{family['living_conditions']}\n"
                   f"ЁЯУН <b>╨Ь╨╡╤Б╤В╨╛:</b> {family['location']}\n\n"
                   f"{ic_me} <b>╨в╤Л:</b> {l['name']}, {l['ethnicity'].lower()}")
    sibs = family.get("siblings",[])
    if sibs:
        sib_text = "ЁЯСитАНЁЯСйтАНЁЯСзтАНЁЯСж <b>╨С╤А╨░╤В╤М╤П ╨╕ ╤Б╤С╤Б╤В╤А╤Л:</b>\n"
        for s in sibs:
            ic = get_person_emoji("sibling", s["gender"], eth, reg)
            ad = s.get("age_diff",0)
            rel = f"╤Б╤В╨░╤А╤И╨╡ ╨╜╨░ {ad} ╨│." if ad > 0 else f"╨╝╨╗╨░╨┤╤И╨╡ ╨╜╨░ {abs(ad)} ╨│." if ad < 0 else "╤А╨╛╨▓╨╡╤Б╨╜╨╕╨║"
            sib_text += f"  {ic} <b>{s['name']}</b> ({rel}) тАФ {s['status']}\n"
    else: sib_text = "ЁЯС╢ <b>╨С╤А╨░╤В╤М╨╡╨▓ ╨╕ ╤Б╨╡╤Б╤В╤С╤А ╨╜╨╡╤В</b> тАФ ╤В╤Л ╨╡╨┤╨╕╨╜╤Б╤В╨▓╨╡╨╜╨╜╤Л╨╣ ╤А╨╡╨▒╤С╨╜╨╛╨║.\n"
    gp_alive = [g for g in family.get("grandparents",[]) if g["alive"]]
    gp_dead = [g for g in family.get("grandparents",[]) if not g["alive"]]
    gp_text = ""
    if gp_alive:
        gp_text += "\nЁЯС╡ <b>╨Ц╨╕╨▓╤Л:</b>\n"
        for g in gp_alive:
            g_role = "grandpa" if "╨┤╨╡╨┤╤Г╤И╨║╨░" in g["role"] else "grandma"
            ic_gp = get_person_emoji(g_role, "m" if g_role == "grandpa" else "f", eth, reg)
            gp_text += f"  {ic_gp} {g['role']}\n"
    if gp_dead:
        gp_text += "\nЁЯкж <b>╨г╤И╨╗╨╕ ╨╕╨╖ ╨╢╨╕╨╖╨╜╨╕:</b>\n"
        for g in gp_dead: gp_text += f"  тЭМ {g['role']}\n"
    relatives_text = sib_text + gp_text + "\n<i>╨в╨▓╨╛╤П ╤Б╨╡╨╝╤М╤П тАФ ╤З╨░╤Б╤В╤М ╤В╨▓╨╛╨╡╨╣ ╨╕╤Б╤В╨╛╤А╨╕╨╕.</i>"
    return [world_text, family_text, relatives_text]

# ================= ╨Ю╨в╨Ы╨Ю╨Ц╨Х╨Э╨Э╨л╨Х ╨Я╨Ю╨б╨Ы╨Х╨Ф╨б╨в╨Т╨Ш╨п =================
def add_pending_consequence(l, years_ahead, event_data):
    l.setdefault("pending_consequences",[]).append({"fire_age":l["age"] + years_ahead,"event":event_data})

def get_due_consequence(l):
    due = [c for c in l.get("pending_consequences",[]) if c["fire_age"] <= l["age"]]
    if not due: return None
    consequence = due[0]; l["pending_consequences"].remove(consequence)
    event = dict(consequence["event"]); event["resolved"] = False
    return event

# ================= ╨Ф╨Ю╨б╨в╨Ш╨Ц╨Х╨Э╨Ш╨п ╨Ш ╨Ш╨в╨Ю╨У =================
def check_achievements(l):
    if "achievements" not in l: l["achievements"] = []
    if "ever_in_prison" not in l: l["ever_in_prison"] = False
    new_ones = []
    def has(aid): return aid in l["achievements"]
    def unlock(aid):
        if not has(aid): l["achievements"].append(aid); new_ones.append(ACHIEVEMENTS[aid])
    if l["age"] >= 1: unlock("first_word")
    if any(l["education"].startswith(ed) for ed in ["╨Э╨░╤З╨░╨╗╤М╨╜╨╛╨╡","╨б╤А╨╡╨┤╨╜╨╡╨╡","╨Т╤Л╤Б╤И╨╡╨╡"]): unlock("school")
    if any(l["education"].startswith(ed) for ed in ["╨б╤А╨╡╨┤╨╜╨╡╨╡","╨Т╤Л╤Б╤И╨╡╨╡"]): unlock("graduated")
    if l["education"].startswith("╨Т╤Л╤Б╤И╨╡╨╡"): unlock("university")
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
    text = f"ЁЯПЖ <b>╨Ъ╨╛╨╗╨╗╨╡╨║╤Ж╨╕╤П ╤Б╤Г╨┤╨╡╨▒</b>\n╨Ю╤В╨║╤А╤Л╤В╨╛: {len(earned)}/{total}\n\n"
    for aid, ach in ACHIEVEMENTS.items():
        mark = "тЬЕ" if aid in earned else "тмЬ"
        text += f"{mark} {ach['name']} тАФ <i>{ach['desc']}</i>\n"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤ ╨║ ╨╢╨╕╨╖╨╜╨╕", callback_data="refresh"))
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
    kws = ["╨а╨╛╨┤╨╕╨╗╤Б╤П","╨Я╨╛╤И╨╡╨╗ ╨▓ ╤И╨║╨╛╨╗╤Г","╨Ю╨║╨╛╨╜╤З╨╕╨╗ ╤И╨║╨╛╨╗╤Г","╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ ╨▓╤Г╨╖","╨Ц╨╡╨╜╨╕╨╗╤Б╤П","╨а╨░╨╖╨▓╨╛╨┤","╨Э╨░ ╤А╨░╨▒╨╛╤В╤Г","╨Т ╨┐╨╛╨╗╨╕╤Ж╨╕╨╕","╨Т ╨░╤А╨╝╨╕╨╕","╨Ъ╤А╨╕╨╝╨╕╨╜╨░╨╗","╨Я╨╛╨▓╤Л╤И╨╡╨╜╨╕╨╡","╨Я╨╛╨╜╨╕╨╢╨╡╨╜╨╕╨╡","╨Ъ╤Г╨┐╨╕╨╗","╨Ю╤В╨║╤А╤Л╨╗","╨г╨╝╨╡╤А"]
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
        "clean_cash":start_cash,"dirty_cash":0,"in_prison":0,"age":0,"alive":True,"faction":"╨Э╨╡╤В",
        "health":100,"happiness":50,"knowledge":50,"relationships":50,
        "education":"╨Э╨╡╤В","job":"╨С╨╡╨╖╤А╨░╨▒╨╛╤В╨╜╤Л╨╣","salary":0,"job_type":"none","career_xp":0,"career_rank":1,
        "married":False,"children":0,"diseases":[],"properties":[],"cars":[],"businesses":[],"investments":[],"political_reputation":50,"debt":0,
        "life_map":[],"neighbors":generate_neighbors(),"peer_lives":generate_peer_lives(),
        "test_data":None,"asked_tests":{1:[],2:[],3:[]},"current_event":None,"has_license":False,"job_years":0,"books_read":0,
        "seen_focus_events":{"health":[],"knowledge":[],"relationships":[],"happiness":[]},
        "seen_regular_events":[],"philosophy_answers":[],"wealth_history":[],
        "key_npcs":create_key_npcs(country, gender, family),
        "pending_consequences":[],"achievements":[],"ever_in_prison":False,"reputation":0,"vacation_count":0,
        "family":family,"world_context":world,"tracked_messages":[],
    }

def create_dynasty_heir(parent_life):
    heir = create_life(force_country=parent_life["country"])
    heir["name"] = f"{parent_life['name']} II (╨Э╨░╤Б╨╗╨╡╨┤╨╜╨╕╨║)"
    heir["age"] = 18
    heir["clean_cash"] = int(parent_life["clean_cash"] * 0.5)
    heir["properties"] = [dict(p) for p in parent_life.get("properties", [])]
    heir["businesses"] = [dict(b) for b in parent_life.get("businesses", [])]
    heir["investments"] = [dict(i) for i in parent_life.get("investments", [])]
    heir["political_reputation"] = parent_life.get("political_reputation", 50)
    heir["education"] = "╨б╤А╨╡╨┤╨╜╨╡╨╡ (╨╗╨╕╤Ж╨╡╨╣/╨║╨╛╨╗╨╗╨╡╨┤╨╢)"
    heir["mode"] = "dynasty"
    heir["life_map"] = ["18 ╨╗╨╡╤В: ╨Т╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ ╨┐╤А╨░╨▓╨░ ╨╜╨░╤Б╨╗╨╡╨┤╤Б╤В╨▓╨░ ╨▓╨╡╨╗╨╕╨║╨╛╨╣ ╨┤╨╕╨╜╨░╤Б╤В╨╕╨╕."]
    return heir

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
    return effect.get("text", "╨У╨╛╨┤ ╨┐╤А╨╛╤И╨╡╨╗.")

def show_peer_lives(l):
    if l["age"] % 5 != 0: return None
    text = "ЁЯСе <b>╨а╨╛╨▓╨╡╤Б╨╜╨╕╨║╨╕ (╤А╨╛╨┤╨╕╨╗╨╕╤Б╤М ╤Б ╤В╨╛╨▒╨╛╨╣ ╨▓ ╨╛╨┤╨╜╤Г ╤Б╨╡╨║╤Г╨╜╨┤╤Г):</b>\n\n"
    for i, p in enumerate(l.get("peer_lives",[])):
        if l["age"] >= p["death_age"]: status = "ЁЯТА ╤Г╨╝╨╡╤А(╨╗╨░)"
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
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤ ╨║ ╨╢╨╕╨╖╨╜╨╕", callback_data="refresh"))
    if not lb:
        msg = bot.send_message(chat_id, "ЁЯПЖ ╨а╨╡╨╣╤В╨╕╨╜╨│ ╨┐╤Г╤Б╤В.", reply_markup=kb, parse_mode="HTML")
        if highlight_user:
            l_ref = players_db.get(str(highlight_user))
            if l_ref: track_message(l_ref, chat_id, msg.message_id)
        return
    text = "ЁЯПЖ <b>╨в╨╛╨┐-10 ╨┐╤А╨╛╨╢╨╕╤В╤Л╤Е ╨╢╨╕╨╖╨╜╨╡╨╣</b>\n\n"
    medals = ["ЁЯеЗ","ЁЯеИ","ЁЯеЙ"]
    for i, e in enumerate(lb[:10]):
        prefix = medals[i] if i < 3 else f"{i+1}."
        mark = " ЁЯСИ" if highlight_user and e["user_id"] == str(highlight_user) else ""
        text += (f"{prefix} <b>{e['name']}</b> ({e['country']}){mark}\n"
                 f"    тнР {e['score']} ╨╛╤З╨║╨╛╨▓ ┬╖ {get_age_str(e['age'])} ┬╖ {e['wealth']}\n"
                 f"    ЁЯй║ {e['cause']}\n\n")
    text += f"\n<i>╨Т╤Б╨╡╨│╨╛ ╨╢╨╕╨╖╨╜╨╡╨╣ ╨┐╤А╨╛╨╢╨╕╤В╨╛: {len(lb)}</i>"
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    if highlight_user:
        l_ref = players_db.get(str(highlight_user))
        if l_ref: track_message(l_ref, chat_id, msg.message_id)

# ================= ╨Я╨Ю╨Ы╨Ш╨в╨Ш╨Ъ╨Р, ╨С╨Ш╨Ч╨Э╨Х╨б-╨Ъ╨а╨Ш╨Ч╨Ш╨б╨л ╨Ш ╨Ш╨Э╨Т╨Х╨б╨в╨Ш╨ж╨Ш╨Ш =================
def trigger_politics_event(l):
    if l["age"] >= 30 and l.get("job_type") != "politics" and random.random() < 0.25:
        seen = l.setdefault("seen_regular_events", [])
        if "politics_election" in seen[-5:]:
            return None
        seen.append("politics_election")
        curr_job = l.get("job", "╨С╨╡╨╖╤А╨░╨▒╨╛╤В╨╜╤Л╨╣")
        return {
            "id": "politics_election",
            "title": "ЁЯЧ│ ╨Т╤Л╨▒╨╛╤А╤Л ╨▓ ╨╝╤Г╨╜╨╕╤Ж╨╕╨┐╨░╨╗╤М╨╜╤Л╨╣ ╤Б╨╛╨▓╨╡╤В",
            "text": f"╨г ╨▓╨░╤Б ╨┐╨╛╤П╨▓╨╕╨╗╨░╤Б╤М ╨▓╨╛╨╖╨╝╨╛╨╢╨╜╨╛╤Б╤В╤М ╨▓╤Л╨┤╨▓╨╕╨╜╤Г╤В╤М ╤Б╨▓╨╛╤О ╨║╨░╨╜╨┤╨╕╨┤╨░╤В╤Г╤А╤Г ╨╜╨░ ╨▓╤Л╨▒╨╛╤А╨░╤Е. ╨Я╨╡╤А╨╡╤Е╨╛╨┤ ╨▓ ╨┐╨╛╨╗╨╕╤В╨╕╨║╤Г ╨┐╨╛╤В╤А╨╡╨▒╤Г╨╡╤В ╨╛╤Б╤В╨░╨▓╨╕╤В╤М ╤В╨╡╨║╤Г╤Й╤Г╤О ╨┤╨╡╤П╤В╨╡╨╗╤М╨╜╨╛╤Б╤В╤М ({curr_job})!",
            "choices": [
                {"text": "ЁЯЧ│ ╨С╨░╨╗╨╗╨╛╤В╨╕╤А╨╛╨▓╨░╤В╤М╤Б╤П", "p": 0.45, "success": "politics_win", "fail": "politics_fail"},
                {"text": "ЁЯЪ╢ ╨Ю╤В╨║╨░╨╖╨░╤В╤М╤Б╤П", "p": 1.0, "success_effect": {"text": "╨Т╤Л ╤А╨╡╤И╨╕╨╗╨╕ ╨╜╨╡ ╨╝╨╡╨╜╤П╤В╤М ╨┐╤А╨╛╤Д╨╡╤Б╤Б╨╕╤О ╨╕ ╨╜╨╡ ╨╗╨╡╨╖╤В╤М ╨▓ ╨┐╨╛╨╗╨╕╤В╨╕╨║╤Г."}}
            ]
        }
    return None

def trigger_business_crisis(l):
    bizs = l.get("businesses", [])
    if not bizs:
        return None
    
    c_econ = l["country"][7]
    is_poor_country = c_econ < 3000
    
    if random.random() < 0.09:
        biz = random.choice(bizs)
        crisis_pool = ["tax_audit", "supply_chain", "strike"]
        if is_poor_country or l.get("faction") == "╨г╨╗╨╕╤З╨╜╨░╤П ╨▒╨░╨╜╨┤╨░":
            crisis_pool.append("racket")
        else:
            crisis_pool.append("market_drop")
            
        crisis_type = random.choice(crisis_pool)
        
        if crisis_type == "tax_audit":
            fine = max(300, int(biz["value"] * random.uniform(0.04, 0.08)))
            l["clean_cash"] -= fine
            return f"ЁЯЪи <b>╨Э╨░╨╗╨╛╨│╨╛╨▓╨░╤П ╨╕╨╜╤Б╨┐╨╡╨║╤Ж╨╕╤П</b> ╨┐╤А╨╛╨▓╨╡╨╗╨░ ╨░╤Г╨┤╨╕╤В ╨▒╨╕╨╖╨╜╨╡╤Б╨░ ┬л{biz['type']}┬╗. ╨Т╤Л╨┐╨╕╤Б╨░╨╜ ╤И╤В╤А╨░╤Д ╨╕ ╨┤╨╛╨╜╨░╤З╨╕╤Б╨╗╨╡╨╜╨╕╤П: {fmt_money(fine, l['country'])}."
        elif crisis_type == "strike":
            loss = max(200, int(biz["value"] * random.uniform(0.03, 0.06)))
            l["clean_cash"] -= loss
            return f"ЁЯЫа <b>╨Ч╨░╨▒╨░╤Б╤В╨╛╨▓╨║╨░ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╗╨░</b> ╨╜╨░ ┬л{biz['type']}┬╗ ╨┐╨░╤А╨░╨╗╨╕╨╖╨╛╨▓╨░╨╗╨░ ╤А╨░╨▒╨╛╤В╤Г ╨╜╨░ ╨╜╨╡╨┤╨╡╨╗╤О. ╨г╨▒╤Л╤В╨╛╨║: {fmt_money(loss, l['country'])}."
        elif crisis_type == "racket":
            extortion = max(500, int(biz["value"] * 0.07))
            l["clean_cash"] -= extortion
            l["happiness"] = max(0, l["happiness"] - 5)
            return f"ЁЯХ╢ <b>╨Ь╨╡╤Б╤В╨╜╤Л╨╡ ╨║╤А╨╕╨╝╨╕╨╜╨░╨╗╤М╨╜╤Л╨╡ ╤Б╤В╤А╤Г╨║╤В╤Г╤А╤Л</b> ╨╛╨▒╨╗╨╛╨╢╨╕╨╗╨╕ ┬л{biz['type']}┬╗ ╨┤╨░╨╜╤М╤О. ╨Я╨╛╤В╨╡╤А╨╕: {fmt_money(extortion, l['country'])}."
        elif crisis_type == "market_drop":
            biz["value"] = max(500, int(biz["value"] * 0.88))
            return f"ЁЯУЙ <b>╨Я╨░╨┤╨╡╨╜╨╕╨╡ ╤А╤Л╨╜╨╛╤З╨╜╨╛╨│╨╛ ╤Б╨┐╤А╨╛╤Б╨░:</b> ╨║╨░╨┐╨╕╤В╨░╨╗╨╕╨╖╨░╤Ж╨╕╤П ╨┐╤А╨╡╨┤╨┐╤А╨╕╤П╤В╨╕╤П ┬л{biz['type']}┬╗ ╤Б╨╜╨╕╨╖╨╕╨╗╨░╤Б╤М ╨╜╨░ 12%."
        elif crisis_type == "supply_chain":
            delay_loss = max(250, int(biz["value"] * 0.04))
            l["clean_cash"] -= delay_loss
            return f"ЁЯУж <b>╨б╨▒╨╛╨╣ ╨▓ ╨╗╨╛╨│╨╕╤Б╤В╨╕╤З╨╡╤Б╨║╨╛╨╣ ╤Ж╨╡╨┐╨╛╤З╨║╨╡</b> ╤Б╤Л╤А╤М╤П ╨┤╨╗╤П ┬л{biz['type']}┬╗. ╨Э╨╡╤Г╤Б╤В╨╛╨╣╨║╨░ ╨║╨╗╨╕╨╡╨╜╤В╨░╨╝: {fmt_money(delay_loss, l['country'])}."
    return None

def process_investments(l):
    if not l.get("investments"):
        return ""
    report = "\n\nЁЯУИ <b>╨Ю╤В╤З╨╡╤В ╨┐╨╛ ╨╕╨╜╨▓╨╡╤Б╤В╨╕╤Ж╨╕╤П╨╝:</b>\n"
    for inv in list(l["investments"]):
        asset_name = inv["type"]
        amount = inv["amount"]
        props = INVESTMENT_ASSETS.get(asset_name, {"risk": 0.2, "min_return": 0.9, "max_return": 1.2})
        if random.random() < props["risk"] and random.random() < 0.5:
            multiplier = random.uniform(props["min_return"] * 0.5, 0.9)
            status = "ЁЯУЙ ╨┐╤А╨╛╤Б╨╡╨╗╨╕"
        else:
            multiplier = random.uniform(props["min_return"], props["max_return"])
            status = "ЁЯУИ ╨▓╤Л╤А╨╛╤Б╨╗╨╕"
        new_amt = max(0, int(amount * multiplier))
        inv["amount"] = new_amt
        report += f"тАв {asset_name}: {status} (╨▒╨░╨╗╨░╨╜╤Б: {fmt_money(new_amt, l['country'])})\n"
    return report

# ================= get_event =================
def get_event(l):
    age = l["age"]

    pol_evt = trigger_politics_event(l)
    if pol_evt:
        return pol_evt

    if age >= 18 and l["job_type"] == "none" and l["faction"] == "╨Э╨╡╤В" and l["in_prison"] == 0:
        return {"id":"path","title":"тЪб ╨Т╤Л╨▒╨╛╤А ╨┐╤Г╤В╨╕","text":"╨Я╨╛╤А╨░ ╨╛╨┐╤А╨╡╨┤╨╡╨╗╤П╤В╤М╤Б╤П.",
                "choices":[{"text":"ЁЯТ╝ ╨У╤А╨░╨╢╨┤╨░╨╜╨║╨░","p":1,"success":"job_civ","fail":"none"},
                           {"text":"ЁЯСо ╨Я╨╛╨╗╨╕╤Ж╨╕╤П","p":1 if l["education"].startswith("╨Т╤Л╤Б╤И╨╡╨╡") else 0,"success":"job_pol","fail":"none"},
                           {"text":"ЁЯОЦ ╨Р╤А╨╝╨╕╤П","p":1 if any(l["education"].startswith(ed) for ed in ["╨б╤А╨╡╨┤╨╜╨╡╨╡","╨Т╤Л╤Б╤И╨╡╨╡"]) else 0,"success":"job_mil","fail":"none"},
                           {"text":"ЁЯТК ╨Ъ╤А╨╕╨╝╨╕╨╜╨░╨╗","p":1,"success":"job_crim","fail":"none"}]}

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
        return {"id":"prej","title":"╨б╤В╨╛╨╗╨║╨╜╨╛╨▓╨╡╨╜╨╕╨╡ ╤Б ╨┐╤А╨╡╨┤╨▓╨╖╤П╤В╨╛╤Б╤В╤М╤О","text":f"{l['prejudice']}",
                "choices":[{"text":"тЬК ╨Ф╨╛╨║╨░╨╖╨░╤В╤М","p":0.4,"success":"prej_fight_win","fail":"prej_fight_fail"},
                           {"text":"ЁЯжК ╨Ш╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╤В╤М","p":0.7,"success":"prej_exploit","fail":"prej_exploit_fail"},
                           {"text":"ЁЯШФ ╨б╨╝╨╕╤А╨╕╤В╤М╤Б╤П","p":1,"success":"prej_accept","fail":"none"}]}

    if age >= 15 and random.random() < 0.05:
        we = random.choice(WORLD_EVENTS)
        if we.get("min_age",0) <= age:
            return {"id":we["id"],"title":we["title"],"text":we["text"],
                    "choices":[{"text":"╨Я╨╡╤А╨╡╨╢╨╕╤В╤М","p":1,"success_effect":{**we["effect"],"text":we["text"]}}]}

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
                return {"id":"npc_mother","title":"ЁЯУЮ ╨Ч╨▓╨╛╨╜╨╛╨║ ╨╝╨░╨╝╨╡","text":f"╨Ь╨░╨╝╨░ {nm} ╨╖╨▓╨╛╨╜╨╕╤В.",
                        "choices":[{"text":"╨Я╨╛╨│╨╛╨▓╨╛╤А╨╕╤В╤М","p":1,"success_effect":{"relationships":6,"happiness":5,"text":"╨в╤С╨┐╨╗╨░╤П ╨▒╨╡╤Б╨╡╨┤╨░."}},
                                   {"text":"╨С╤А╨╛╤Б╨╕╤В╤М","p":1,"success_effect":{"relationships":-8,"happiness":-3,"text":"╨Ь╨░╨╝╨░ ╤А╨░╤Б╤Б╤В╤А╨╛╨╕╨╗╨░╤Б╤М."}}]}
            if role == "friend" and age >= 10:
                return {"id":"npc_friend","title":"ЁЯдЭ ╨Ф╤А╤Г╨│ ╨┐╤А╨╛╤Б╨╕╤В ╨┐╨╛╨╝╨╛╤Й╨╕","text":f"╨Ф╤А╤Г╨│ {nm} ╨▓ ╨▒╨╡╨┤╨╡.",
                        "choices":[{"text":"╨Я╨╛╨╝╨╛╤З╤М","p":0.8,"success_effect":{"relationships":15,"happiness":5,"cash":-200,"text":"╨Ю╨╜ ╤В╨▓╨╛╨╣ ╨┤╨╛╨╗╨╢╨╜╨╕╨║."},"fail_effect":{"relationships":-5,"cash":-200,"text":"╨Э╨╡ ╨┐╨╛╨╗╤Г╤З╨╕╨╗╨╛╤Б╤М."}},
                                   {"text":"╨Ю╤В╨║╨░╨╖╨░╤В╤М","p":1,"success_effect":{"relationships":-15,"happiness":-5,"text":"╨Ю╨▒╨╕╨┤╨╡╨╗╤Б╤П."}}]}
            if role == "rival" and age >= 13:
                return {"id":"npc_rival","title":"тЪФя╕П ╨б╨╛╨┐╨╡╤А╨╜╨╕╨║","text":f"╨б╨╛╨┐╨╡╤А╨╜╨╕╨║ {nm} ╨▒╤А╨╛╤Б╨░╨╡╤В ╨▓╤Л╨╖╨╛╨▓.",
                        "choices":[{"text":"╨Я╤А╨╕╨╜╤П╤В╤М","p":0.5,"success_effect":{"happiness":10,"career_xp":15,"relationships":3,"text":"╨Я╨╛╨▒╨╡╨┤╨╕╨╗!"},"fail_effect":{"happiness":-5,"health":-5,"text":"╨Я╤А╨╛╨╕╨│╤А╨░╨╗."}},
                                   {"text":"╨Ю╤В╨║╨░╨╖╨░╤В╤М╤Б╤П","p":1,"success_effect":{"relationships":-3,"text":"╨в╤А╤Г╤Б."}}]}
            if role == "father" and age >= 20:
                return {"id":"npc_father","title":"ЁЯС┤ ╨Ю╤В╨╡╤Ж ╨╖╨╛╨▓╤С╤В","text":f"╨Ю╤В╨╡╤Ж {nm} ╨╜╨░ ╤Г╨╢╨╕╨╜.",
                        "choices":[{"text":"╨Я╨╛╨╣╤В╨╕","p":1,"success_effect":{"relationships":8,"happiness":5,"text":"╨Ю╤В╨╗╨╕╤З╨╜╤Л╨╣ ╨▓╨╡╤З╨╡╤А."}},
                                   {"text":"╨Ю╤В╨║╨░╨╖╨░╤В╤М╤Б╤П","p":1,"success_effect":{"relationships":-5,"text":"╨Ю╨▒╨╕╨┤╨╡╨╗╤Б╤П."}}]}

    if age >= 18 and l["job_type"] in ["civilian","police","military","criminal","politics"] and random.random() < 0.30:
        work_pool = [
            {"id":"work_ot","title":"💼 Овертайм","text":"Горящий проект требует сверхурочной работы на всю ночь.",
             "choices":[{"text":"Согласиться","p":0.75,"success_effect":{"career_xp":35,"happiness":-4,"health":-3,"text":"Проект завершен вовремя! XP +35."},"fail_effect":{"career_xp":10,"happiness":-8,"health":-5,"text":"Усталость сказалась, но работу сдали."}},
                        {"text":"Уйти домой","p":1.0,"success_effect":{"career_xp":-10,"happiness":5,"text":"Выбрал отдых. Шеф недоволен."}}]},
            {"id":"work_int","title":"📉 Офисные сплетни","text":"Коллеги распускают слухи за вашей спиной перед повышением.",
             "choices":[{"text":"Разобраться прямо","p":0.6,"success_effect":{"career_xp":30,"relationships":5,"text":"Поставил интриганов на место! Уважение в коллективе."},"fail_effect":{"career_xp":-15,"happiness":-5,"text":"Скандал дошел до начальства. XP -15."}},
                        {"text":"Игнорировать","p":1.0,"success_effect":{"happiness":2,"text":"Не обратил внимания и сфокусировался на задачах."}}]},
            {"id":"work_bonus","title":"💰 Премиальный фонд","text":"Руководство распределяет годовые бонусы лучшим сотрудникам.",
             "choices":[{"text":"Потребовать премию","p":0.7,"success_effect":{"cash":int(l['country'][7]*0.5),"career_xp":25,"happiness":10,"text":"Достижения признаны! Получена премия и уважение."},"fail_effect":{"happiness":-5,"career_xp":-5,"text":"Начальство посчитало вас слишком наглым."}},
                        {"text":"Скромно ждать","p":0.9,"success_effect":{"cash":int(l['country'][7]*0.2),"text":"Выписали стандартный скромный бонус."}}]},
            {"id":"work_headhunt","title":"💼 Оффер от конкурентов","text":"Конкурирующая фирма предлагает перейти к ним с повышением оклада.",
             "choices":[{"text":"Использовать оффер для торга","p":0.65,"success_effect":{"career_xp":30,"happiness":8,"text":"Текущее руководство повысило зарплату!"},"fail_effect":{"career_xp":-20,"text":"Шеф воспринял это как шантаж."}},
                        {"text":"Остаться верным компании","p":1.0,"success_effect":{"career_xp":15,"relationships":8,"text":"Преданность коллективу замечена начальством."}}]},
            {"id":"work_audit","title":"📋 Проверка отчетности","text":"Внезапный аудит проверяет результаты вашей работы за квартал.",
             "choices":[{"text":"Защитить каждый пункт","p":0.8,"success_effect":{"career_xp":30,"knowledge":5,"text":"Аудиторы не нашли ни единой ошибки! Репутация безупречна."},"fail_effect":{"career_xp":-15,"happiness":-4,"text":"Всплыли мелкие недочеты."}},
                        {"text":"Свалить на стажера","p":0.4,"success_effect":{"career_xp":10,"relationships":-10,"text":"Выкрутился, но коллектив осуждает."},"fail_effect":{"career_xp":-30,"relationships":-15,"happiness":-10,"text":"Обман раскрыт! Репутация подорвана."}}]},
        ]
        return pick_rotating(l, work_pool, max_recent=4)

    if age >= 18 and l["cars"] and random.random() < 0.15:
        if not l.get("has_license"):
            return {"id":"dps1","title":"ЁЯЪи ╨Ф╨Я╨б","text":"╨Я╤А╨╛╤Б╨╕╤В ╨┐╤А╨░╨▓╨░. ╨г ╤В╨╡╨▒╤П ╨╜╨╡╤В.",
                    "choices":[{"text":"ЁЯТ╡ ╨Т╨╖╤П╤В╨║╨░","p":0.7,"success":"bribe_dps","fail":"dps_jail"},{"text":"ЁЯШм ╨Ф╨╛╨│╨╛╨▓╨╛╤А╨╕╤В╤М╤Б╤П","p":0.2,"success":"dps_warning","fail":"dps_jail"}]}
        elif random.random() < 0.3:
            return {"id":"dps2","title":"ЁЯН╗ ╨Я╤М╤П╨╜╨░╤П ╨╡╨╖╨┤╨░","text":"╨Ч╨░╨┐╨░╤Е ╨┐╨╡╤А╨╡╨│╨░╤А╨░.",
                    "choices":[{"text":"ЁЯТ╡ ╨Т╨╖╤П╤В╨║╨░","p":0.5,"success":"bribe_dps_big","fail":"drunk_jail"},{"text":"ЁЯЪ╢ ╨Ю╤В╨║╨░╨╖","p":0.1,"success":"dps_warning","fail":"drunk_jail"},{"text":"ЁЯШн ╨б╨╝╨╕╤А╨╕╤В╤М╤Б╤П","p":1,"success":"drunk_jail","fail":"none"}]}

    if age < 13:
        pool = [e for e in CHILD_EVENTS if e["min_age"] <= age <= e["max_age"]]
        return pick_rotating(l, pool, max_recent=5)
    elif age < 18:
        return pick_rotating(l, TEEN_EVENTS, max_recent=6)
    else:
        return pick_rotating(l, adult_events_for(l), max_recent=8)

# ================= ╨б╨в╨Р╨в╨Ш╨б╨в╨Ш╨Ъ╨Р =================
def get_stats_line(l):
    return f"тЭдя╕П {l['health']}% | ЁЯШК {l['happiness']}% | ЁЯза {l['knowledge']}% | ЁЯдЭ {l['relationships']}%"

def apply_focus(l, focus):
    if focus == "health":
        l["health"] = min(100, l["health"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: ╨г╨┤╨╡╨╗╨╕╨╗ ╨▓╤А╨╡╨╝╤П ╨╖╨┤╨╛╤А╨╛╨▓╤М╤О")
    elif focus == "knowledge":
        l["knowledge"] = min(100, l["knowledge"] + random.randint(5,10)); l["happiness"] = max(0, l["happiness"] - random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: ╨г╤З╨╕╨╗╤Б╤П ╨╕ ╤А╨░╨╖╨▓╨╕╨▓╨░╨╗╤Б╤П")
    elif focus == "relationships":
        l["relationships"] = min(100, l["relationships"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: ╨г╨┤╨╡╨╗╨╕╨╗ ╨▓╤А╨╡╨╝╤П ╤Б╨╡╨╝╤М╨╡ ╨╕ ╨┤╤А╤Г╨╖╤М╤П╨╝")
    elif focus == "happiness":
        l["happiness"] = min(100, l["happiness"] + random.randint(10,15)); l["health"] = max(0, l["health"] - random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,5)); l["relationships"] = max(0, l["relationships"] - random.randint(0,5))
        l["life_map"].append(f"{get_age_str(l['age'])}: ╨Э╨░╤Б╨╗╨░╨╢╨┤╨░╨╗╤Б╤П ╨╢╨╕╨╖╨╜╤М╤О")
    elif focus == "work":
        l["happiness"] = max(0, l["happiness"] - random.randint(1,4))
        l["health"] = max(0, l["health"] - random.randint(0,3))
        l["knowledge"] = min(100, l["knowledge"] + random.randint(1,4))
        l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        # ╨д╨╛╨║╤Г╤Б ╨╜╨░ ╤А╨░╨▒╨╛╤В╤Г ╨┤╨░╤С╤В ╨│╨░╤А╨░╨╜╤В╨╕╤А╨╛╨▓╨░╨╜╨╜╤Л╨╣ ╨║╨░╤А╤М╨╡╤А╨╜╤Л╨╣ ╨╛╨┐╤Л╤В
        xp_gain = random.randint(25, 45)
        l["career_xp"] = l.get("career_xp", 0) + xp_gain
        l["life_map"].append(f"{get_age_str(l['age'])}: ╨г╤Б╨╡╤А╨┤╨╜╨╛ ╤А╨░╨▒╨╛╤В╨░╨╗ (+{xp_gain} XP ╨║╨░╤А╤М╨╡╤А╤Л)")

# ================= next_year =================
def next_year(user_id, chat_id):
    uid_str = str(user_id)
    if uid_str not in players_db: return bot.send_message(chat_id, "╨Э╨░╤З╨╜╨╕ ╨╖╨░╨╜╨╛╨▓╨╛: /start")
    l = players_db[uid_str]
    if not l["alive"]: return bot.send_message(chat_id, "╨в╤Л ╤Г╨╝╨╡╤А. /start")

    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1; save_db(players_db)
        if l["in_prison"] == 0:
            l["job"] = "╨С╨╡╨╖╤А╨░╨▒╨╛╤В╨╜╤Л╨╣"; l["salary"] = 0; l["job_type"] = "none"
            return send_scene(chat_id, l, "тЫУ <b>╨в╤Л ╨▓╤Л╤И╨╡╨╗ ╨╜╨░ ╤Б╨▓╨╛╨▒╨╛╨┤╤Г.</b>", kb_year(), "life")
        return send_scene(chat_id, l, f"тЫУ <b>╨в╤О╤А╤М╨╝╨░.</b> ╨Ю╤Б╤В╨░╨╗╨╛╤Б╤М: {get_age_str(l['in_prison'])}.", kb_year(), "prison")

    if l.get("focus"):
        l["last_focus"] = l["focus"]; apply_focus(l, l["focus"]); l["focus"] = None
    else: l["last_focus"] = None

    l["last_result"] = None
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

    # ╨Ю╤В╨╝╤Л╨▓╨░╨╜╨╕╨╡ ╨┤╨╡╨╜╨╡╨│ ╨║╤А╨╕╨╝╨╕╨╜╨░╨╗╨░ ╤З╨╡╤А╨╡╨╖ ╨▒╨╕╨╖╨╜╨╡╤Б
    launder_text = ""
    if l.get("job_type") == "criminal" and l.get("dirty_cash", 0) > 0 and l.get("businesses"):
        max_launder = sum(int(b["value"] * 0.4) for b in l["businesses"])
        laundered = min(l["dirty_cash"], max_launder)
        if laundered > 0:
            l["dirty_cash"] -= laundered
            l["clean_cash"] += laundered
            launder_text = f"\nЁЯз║ ╨Ю╤В╨╝╤Л╤В╨╛ ╤З╨╡╤А╨╡╨╖ ╤Б╨╛╨▒╤Б╤В╨▓╨╡╨╜╨╜╤Л╨╣ ╨▒╨╕╨╖╨╜╨╡╤Б: {fmt_money(laundered, l['country'])}."

    # ╨Ф╨╛╤Е╨╛╨┤ ╨║╤А╨╕╨╝╨╕╨╜╨░╨╗╨░
    if l.get("job_type") == "criminal":
        rank = l.get("career_rank", 1)
        crim_income = int(l["country"][7] * (0.4 + 0.25 * rank))
        l["dirty_cash"] += crim_income

    # ╨Я╨╡╨╜╤Б╨╕╨╛╨╜╨╜╤Л╨╣ ╨▓╨╛╨╖╤А╨░╤Б╤В ╨▓ 65 ╨╗╨╡╤В
    g_m = l.get("gender") == "m"
    if l["age"] == 65 and l.get("job_type") in ["civilian","police","military","politics"]:
        pension = max(300, int(l["salary"] * 0.6))
        l["job"] = "╨Я╨╡╨╜╤Б╨╕╨╛╨╜╨╡╤А"
        l["salary"] = pension
        l["job_type"] = "pensioner"
        ret_text = "╨▓╤Л╤И╨╡╨╗ ╨╜╨░ ╨┐╨╡╨╜╤Б╨╕╤О" if g_m else "╨▓╤Л╤И╨╗╨░ ╨╜╨░ ╨┐╨╡╨╜╤Б╨╕╤О"
        add_to_life_map(l, f"ЁЯС┤ {ret_text.capitalize()} (╨┐╨╡╨╜╤Б╨╕╤П: {fmt_money(pension, l['country'])}).")

    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian","police","military","politics"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    spend_mod = 1.0
    if l["prejudice"] and ("╤Б╨║╤Г╨┐╤Л╨╝" in l["prejudice"] or "╨┐╤А╨╡╨┤╨┐╤А╨╕╨╕╨╝╤З╨╕╨▓╤Л╨╝" in l["prejudice"]): spend_mod = 0.7
    elif l["prejudice"] and ("╨▒╨╡╨╖╨╖╨░╨▒╨╛╤В╨╜╤Л╨╝" in l["prejudice"] or "╨┐╤М╤П╨╜╨╕╤Ж╨╡╨╣" in l["prejudice"]): spend_mod = 1.3
    living = int(l["country"][7] * 0.2 * spend_mod + (300 * l["children"]))
    l["clean_cash"] += (l["salary"] - tax - med - living)
    if l["clean_cash"] < 0:
        l["debt"] += abs(l["clean_cash"]); l["clean_cash"] = 0

    l["wealth_history"].append(l["clean_cash"])
    if len(l["wealth_history"]) > 80: l["wealth_history"] = l["wealth_history"][-80:]

    if l["job_type"] in ["civilian","police","military","criminal","politics"]:
        l["job_years"] += 1
        # ╨Я╨╛╨▓╤Л╤И╨╡╨╜╨╕╨╡ ╨┐╤А╨╛╨╕╤Б╤Е╨╛╨┤╨╕╤В ╨┐╤А╨╕ ╨╜╨░╨║╨╛╨┐╨╗╨╡╨╜╨╕╨╕ 100 XP (╤В╤А╨╡╨▒╤Г╨╡╤В╤Б╤П ╨╛╤В 1 ╨│╨╛╨┤╨░ ╤Б╤В╨░╨╢╨░)
        if l["career_xp"] >= 100 and l["job_years"] >= 1:
            l["career_xp"] = 0
            if l["career_rank"] < 5:
                l["career_rank"] += 1
                l["salary"] = int(l["salary"] * 1.35)
                l["job_years"] = 0
                new_title = CAREER_TITLES.get(l["job_type"], {}).get(l["career_rank"], "╨Т╤Л╤Б╤И╨╕╨╣ ╤З╨╕╨╜")
                add_to_life_map(l, f"ЁЯОЦ ╨Я╨╛╨▓╤Л╤И╨╡╨╜╨╕╨╡ ╨▓ ╨║╨░╤А╤М╨╡╤А╨╡: {new_title}")
                l["happiness"] = min(100, l["happiness"] + 10)
        elif l["career_xp"] <= -50:
            l["career_xp"] = 0
            if l["career_rank"] > 1:
                l["career_rank"] -= 1
                l["salary"] = int(l["salary"] * 0.7)
                l["job_years"] = 0
                new_title = CAREER_TITLES.get(l["job_type"], {}).get(l["career_rank"], "╨Э╨╕╨╖╤И╨╕╨╣ ╤З╨╕╨╜")
                add_to_life_map(l, f"ЁЯУЙ ╨Я╨╛╨╜╨╕╨╢╨╡╨╜╨╕╨╡ ╨▓ ╨┤╨╛╨╗╨╢╨╜╨╛╤Б╤В╨╕: {new_title}")
                l["happiness"] = max(0, l["happiness"] - 10)

    echo_text = ""
    if l["age"] in [7,18,30,50]:
        n = random.choice(l["neighbors"])
        echo_text = f"\n\nЁЯСе <b>╨н╤Е╨╛:</b> ╨в╨▓╨╛╨╣ ╤А╨╛╨▓╨╡╤Б╨╜╨╕╨║ <b>{n['name']}</b> ({n['country'][1]}) тАФ {get_neighbor_echo(n, l['age'])}."
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
            5:{"q":"╨з╤В╨╛ ╨┤╨╗╤П ╤В╨╡╨▒╤П ╤Б╨╡╨╣╤З╨░╤Б ╤Б╨░╨╝╨╛╨╡ ╨▓╨░╨╢╨╜╨╛╨╡?","opts":["ЁЯСитАНЁЯСйтАНЁЯСз ╨б╨╡╨╝╤М╤П","ЁЯОо ╨Ш╨│╤А╤Л","ЁЯМН ╨г╨╖╨╜╨░╤В╤М ╨╝╨╕╤А"]},
            15:{"q":"╨Ъ╨╡╨╝ ╤В╤Л ╤Е╨╛╤З╨╡╤И╤М ╤Б╤В╨░╤В╤М?","opts":["ЁЯТ╝ ╨г╤Б╨┐╨╡╤И╨╜╤Л╨╝","тЭдя╕П ╨Ы╤О╨▒╨╕╨╝╤Л╨╝","ЁЯза ╨г╨╝╨╜╤Л╨╝"]},
            30:{"q":"╨з╤В╨╛ ╨┤╨╡╨╗╨░╨╡╤В ╨╢╨╕╨╖╨╜╤М ╨╛╤Б╨╝╤Л╤Б╨╗╨╡╨╜╨╜╨╛╨╣?","opts":["ЁЯТ░ ╨Ф╨╡╨╜╤М╨│╨╕","ЁЯдЭ ╨Ю╤В╨╜╨╛╤И╨╡╨╜╨╕╤П","ЁЯОп ╨ж╨╡╨╗╤М"]},
            50:{"q":"╨Ю ╤З╤С╨╝ ╤В╤Л ╨╢╨░╨╗╨╡╨╡╤И╤М?","opts":["тП░ ╨Ю ╨▓╤А╨╡╨╝╨╡╨╜╨╕","ЁЯТФ ╨Ю ╨╜╨╡╤Б╨┤╨╡╨╗╨░╨╜╨╜╨╛╨╝","ЁЯШФ ╨Э╨╕ ╨╛ ╤З╤С╨╝"]},
            70:{"q":"╨з╤В╨╛ ╤В╤Л ╨╛╤Б╤В╨░╨▓╨╕╤И╤М ╨┐╨╛╤Б╨╗╨╡ ╤Б╨╡╨▒╤П?","opts":["ЁЯСитАНЁЯСйтАНЁЯСз ╨Ф╨╡╤В╨╡╨╣","ЁЯУЪ ╨Ч╨╜╨░╨╜╨╕╤П","ЁЯТн ╨Т╨╛╤Б╨┐╨╛╨╝╨╕╨╜╨░╨╜╨╕╤П"]},
        }
        q = questions[l["age"]]
        l["current_event"] = {"id":f"phil_{l['age']}","title":f"ЁЯдФ ╨Т╨╛╨┐╤А╨╛╤Б ╨▓ {get_age_str(l['age'])}","text":q["q"],
                              "choices":[{"text":opt,"p":1,"success_effect":{"happiness":3,"text":f"╨в╤Л ╨▓╤Л╨▒╤А╨░╨╗: {opt}."}} for opt in q["opts"]],
                              "is_philosophy":True,"age":l["age"],"resolved":False}
        save_db(players_db)
        return send_scene(chat_id, l, format_event(l, l["current_event"]), kb_event(l["current_event"]["choices"]), "life")

    if l["age"] == 6: return start_exam(user_id, chat_id, 1, "╤И╨║╨╛╨╗╤Г")
    elif l["age"] == 12: return start_exam(user_id, chat_id, 2, "╨║╨╛╨╗╨╗╨╡╨┤╨╢")
    elif l["age"] == 18: return start_exam(user_id, chat_id, 3, "╤Г╨╜╨╕╨▓╨╡╤А╤Б╨╕╤В╨╡╤В")

    evt = get_event(l)
    if evt:
        evt["resolved"] = False
        l["current_event"] = evt
        sc = "life"
        if "╨Ю╨▓╨╡╤А╤В╨░╨╣╨╝" in evt["title"] or "╨Ш╨╜╤В╤А╨╕╨│╨╕" in evt["title"]: sc = "office_angry"
        elif "╨Ъ╤А╨╕╨╖╨╕╤Б" in evt["title"]: sc = "sad"
        elif "╨С╤А╨░╨║" in evt["title"]: sc = "love"
        elif "╨а╨░╨╖╨▓╨╛╨┤" in evt["title"]: sc = "sad"
        elif "╨Ь╨╛╤И╨╡╨╜╨╜╨╕╨║╨╕" in evt["title"]: sc = "money_lose"
        elif "╨Ы╨╛╤В╨╡╤А╨╡╤П" in evt["title"]: sc = "money_win"
        elif "╨Ф╨Я╨б" in evt["title"] or "╨╡╨╖╨┤╨░" in evt["title"]: sc = "police"
        elif evt["title"].startswith(("ЁЯН╝","ЁЯСг","ЁЯз╕ ╨Ы╤О╨▒╨╕╨╝╨░╤П")): sc = "toddler"
        send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]), sc)
    else:
        l["current_event"] = None
        send_scene(chat_id, l, format_year(l) + echo_text, kb_focus(l), "life")

    new_ach = check_achievements(l)
    for ach in new_ach:
        msg = bot.send_message(chat_id, f"ЁЯПЖ <b>╨Э╨╛╨▓╨╛╨╡ ╨┤╨╛╤Б╤В╨╕╨╢╨╡╨╜╨╕╨╡!</b>\n{ach['name']} тАФ {ach['desc']}", parse_mode="HTML")
        track_message(l, chat_id, msg.message_id)
    save_db(players_db)

def send_death(user_id, chat_id):
    l = players_db[str(user_id)]; l["alive"] = False; c = l["country"]
    l["current_event"] = None
    causes = []
    if l["age"] < 5: causes = ["╨Я╨╡╤А╨╕╨╜╨░╤В╨░╨╗╤М╨╜╤Л╨╡ ╨┐╤А╨╕╤З╨╕╨╜╤Л","╨Ш╨╜╤Д╨╡╨║╤Ж╨╕╨╕","╨Э╨╡╤Б╤З╨░╤Б╤В╨╜╤Л╨╣ ╤Б╨╗╤Г╤З╨░╨╣"]
    elif l["age"] < 15: causes = ["╨Ш╨╜╤Д╨╡╨║╤Ж╨╕╨╕","╨Э╨╡╤Б╤З╨░╤Б╤В╨╜╤Л╨╣ ╤Б╨╗╤Г╤З╨░╨╣","╨Т╤А╨╛╨╢╨┤╤С╨╜╨╜╤Л╨╡ ╨░╨╜╨╛╨╝╨░╨╗╨╕╨╕"]
    elif l["age"] < 30: causes = ["╨Э╨╡╤Б╤З╨░╤Б╤В╨╜╤Л╨╣ ╤Б╨╗╤Г╤З╨░╨╣","╨Э╨░╤Б╨╕╨╗╨╕╨╡","╨С╨╛╨╗╨╡╨╖╨╜╨╕"]
    elif l["age"] < 50: causes = ["╨б╨╡╤А╨┤╨╡╤З╨╜╨╛-╤Б╨╛╤Б╤Г╨┤╨╕╤Б╤В╤Л╨╡","╨Ю╨╜╨║╨╛╨╗╨╛╨│╨╕╤П","╨Э╨╡╤Б╤З╨░╤Б╤В╨╜╤Л╨╣ ╤Б╨╗╤Г╤З╨░╨╣"]
    elif l["age"] < 70: causes = ["╨Ю╨╜╨║╨╛╨╗╨╛╨│╨╕╤П","╨б╨╡╤А╨┤╨╡╤З╨╜╨╛-╤Б╨╛╤Б╤Г╨┤╨╕╤Б╤В╤Л╨╡","╨Ф╨╕╨░╨▒╨╡╤В"]
    else: causes = ["╨б╨╡╤А╨┤╨╡╤З╨╜╨╛-╤Б╨╛╤Б╤Г╨┤╨╕╤Б╤В╤Л╨╡","╨Ю╨╜╨║╨╛╨╗╨╛╨│╨╕╤П","╨б╤В╨░╤А╨╡╨╜╨╕╨╡"]
    if l["diseases"]: cause = f"╨Ю╤Б╨╗╨╛╨╢╨╜╨╡╨╜╨╕╨╡: {l['diseases'][-1]}"
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
    balance_text = (f"ЁЯУК <b>╨С╨░╨╗╨░╨╜╤Б ╨╢╨╕╨╖╨╜╨╕:</b>\n  ЁЯШК ╨б╤З╨░╤Б╤В╤М╨╡: {balance['happiness']}/100\n"
                    f"  ЁЯОп ╨б╨╝╤Л╤Б╨╗: {balance['meaning']}/100\n  ЁЯдЭ ╨б╨▓╤П╨╖╨╕: {balance['connections']}/100\n"
                    f"  ЁЯТ░ ╨Ф╨╛╤Б╤В╨░╤В╨╛╨║: {balance['wealth']}/100\n")
    headlines = get_cinematic_headlines(l)
    headlines_text = "ЁЯУЬ <b>╨Ы╨╡╤В╨╛╨┐╨╕╤Б╤М:</b>\n" + "\n".join([f"тАв {h}" for h in headlines]) if headlines else ""
    npc_text = "ЁЯТл <b>╨б╤Г╨┤╤М╨▒╤Л ╨▒╨╗╨╕╨╖╨║╨╕╤Е:</b>\n" + "\n".join([get_npc_epilogue(n) for n in l.get("key_npcs",[])])
    earned = l.get("achievements", [])
    ach_text = f"ЁЯПЖ <b>╨Ф╨╛╤Б╤В╨╕╨╢╨╡╨╜╨╕╤П:</b> {len(earned)}/{len(ACHIEVEMENTS)}"
    if final_ach: ach_text += "\n" + "\n".join([f"тАв {a['name']}" for a in final_ach])
    if l.get("wealth_history"):
        max_w = max(l["wealth_history"]) or 1
        chart = "".join(["тЦБ" if w < max_w*0.2 else "тЦГ" if w < max_w*0.5 else "тЦЕ" if w < max_w*0.8 else "тЦИ" for w in l["wealth_history"]])
        chart_text = f"\nЁЯУИ ╨Ъ╤А╨╕╨▓╨░╤П ╨┤╨╛╤Б╤В╨░╤В╨║╨░: {chart}\n"
    else: chart_text = ""
    top_text = "\nЁЯПЖ <b>╨в╨╛╨┐-5 ╨╢╨╕╨╖╨╜╨╡╨╣:</b>\n"
    for i, e in enumerate(lb[:5]):
        mark = "ЁЯСЙ" if e["user_id"] == str(user_id) and e["age"] == l["age"] else "  "
        top_text += f"{mark} {i+1}. <b>{e['name']}</b> ({e['country']}) тАФ {e['score']} ╨╛╤З╨║╨╛╨▓, {get_age_str(e['age'])}\n"
    msg = (f"ЁЯТА <b>╨б╨╝╨╡╤А╤В╤М ╨▓ {get_age_str(l['age'])}.</b>\nЁЯй║ ╨Я╤А╨╕╤З╨╕╨╜╨░: {cause}\n\n{balance_text}\n"
           f"тнР ╨Ю╤Ж╨╡╨╜╨║╨░ ╨╢╨╕╨╖╨╜╨╕: <b>{score} ╨╛╤З╨║╨╛╨▓</b> ┬╖ ╨╝╨╡╤Б╤В╨╛ <b>#{place} ╨╕╨╖ {total}</b>\n\n"
           f"{headlines_text}\n\n{npc_text}\n\n{ach_text}\n{chart_text}")
    kb = InlineKeyboardMarkup()
    for i, p in enumerate(l.get("peer_lives",[])):
        fate = get_neighbor_final({"trajectory":p["trajectory"],"death_age":p["death_age"]})
        msg += f"\nЁЯСе ╨а╨╛╨▓╨╡╤Б╨╜╨╕╨║ {p['name']} ({p['country'][1]}): {fate}"
        kb.add(InlineKeyboardButton(f"ЁЯОн ╨Я╤А╨╛╨╢╨╕╤В╤М ╨╢╨╕╨╖╨╜╤М {p['name']}", callback_data=f"play_peer_{i}"))
    msg += "\n\n" + top_text
    kb.add(InlineKeyboardButton("ЁЯПЖ ╨в╨╛╨┐ ╨╢╨╕╨╖╨╜╨╡╨╣", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("ЁЯУЦ ╨Ф╨╛╤Б╤В╨╕╨╢╨╡╨╜╨╕╤П", callback_data="achievements"))
    if l.get("children", 0) > 0 or l["clean_cash"] > 5000 or l["properties"] or l["businesses"]:
        kb.add(InlineKeyboardButton(f"ЁЯСС ╨Я╤А╨╛╨┤╨╛╨╗╨╢╨╕╤В╤М ╨┤╨╕╨╜╨░╤Б╤В╨╕╤О (╨Э╨░╤Б╨╗╨╡╨┤╨╜╨╕╨║)", callback_data="dynasty_continue"))
    kb.add(InlineKeyboardButton("ЁЯО▓ ╨Э╨░╤З╨░╤В╤М ╨╖╨░╨╜╨╛╨▓╨╛", callback_data="new"))
    play_cutscene(chat_id, l, get_cutscene_frames("death"), msg, kb)

def start_exam(user_id, chat_id, level, place):
    l = players_db[str(user_id)]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    
    # ╨Я╨╛╨┤╨▒╨╕╤А╨░╨╡╨╝ ╤Б╤В╤А╨╛╨│╨╛ ╤Б╨╛╨╛╤В╨▓╨╡╤В╤Б╤В╨▓╤Г╤О╤Й╨╡╨╡ ╤Г╤А╨╛╨▓╨╜╤О ╤Г╤З╨╡╨▒╨╜╨╛╨╡ ╨╖╨░╨▓╨╡╨┤╨╡╨╜╨╕╨╡
    inst_list = EDU_INSTITUTIONS.get(level, [])
    institution = random.choice(inst_list) if inst_list else f"╨г╤З╨╡╨▒╨╜╨╛╨╡ ╨╖╨░╨▓╨╡╨┤╨╡╨╜╨╕╨╡ ({place})"
    
    # ╨б╨╛╤Е╤А╨░╨╜╤П╨╡╨╝ ╨╖╨░╨▓╨╡╨┤╨╡╨╜╨╕╨╡ ╨▓ ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╢╨╡
    l["current_exam_institution"] = institution
    l["current_exam_level"] = level
    
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    msg = bot.send_message(chat_id, f"ЁЯУЭ <b>╨н╨║╨╖╨░╨╝╨╡╨╜ ╨┐╤А╨╕ ╨┐╨╛╤Б╤В╤Г╨┐╨╗╨╡╨╜╨╕╨╕: {institution}</b>\n╨г╤А╨╛╨▓╨╡╨╜╤М: <b>{place}</b>\n\n╨Т╨╛╨┐╤А╨╛╤Б: <b>{test['q']}</b>", reply_markup=kb, parse_mode="HTML")
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
    
    # ╨Ь╨╡╤Е╨░╨╜╨╕╨║╨░ ╨▓╨╗╨╕╤П╨╜╨╕╤П ╤Б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐╨╛╨▓ ╨╜╨░ ╤Н╨║╨╖╨░╨╝╨╡╨╜╨░╤Е
    if not success:
        # ╨Х╤Б╨╗╨╕ ╨╕╨│╤А╨╛╨║ ╨╛╤И╨╕╨▒╤Б╤П, ╨╜╨╛ ╨╛╨▒╤Й╨╡╤Б╤В╨▓╨╛ ╤Б╤З╨╕╤В╨░╨╡╤В ╨╡╨│╨╛ "╤Г╨╝╨╜╤Л╨╝"
        if l.get("prejudice") and "╤Г╨╝╨╜╤Л╨╝" in l["prejudice"]:
            if random.random() < 0.50:  # 50% ╤И╨░╨╜╤Б ╤Б╨╜╨╕╤Б╤Е╨╛╨╢╨┤╨╡╨╜╨╕╤П ╤Н╨║╨╖╨░╨╝╨╡╨╜╨░╤В╨╛╤А╨╛╨▓
                success = True
                saved_by_stereotype = True
        # ╨Ы╨╕╨▒╨╛ ╨╡╤Б╨╗╨╕ ╤Г ╨┐╨╡╤А╤Б╨╛╨╜╨░╨╢╨░ ╤Г╨╢╨╡ ╨╛╤З╨╡╨╜╤М ╨▓╤Л╤Б╨╛╨║╨╕╨╡ ╨╖╨╜╨░╨╜╨╕╤П (75+)
        elif l.get("knowledge", 50) >= 75 and random.random() < 0.35:
            success = True
            saved_by_knowledge = True
    else:
        # ╨Х╤Б╨╗╨╕ ╨╛╤В╨▓╨╡╤В╨╕╨╗ ╨┐╤А╨░╨▓╨╕╨╗╤М╨╜╨╛, ╨╜╨╛ ╨╡╤Б╤В╤М ╨╜╨╡╨│╨░╤В╨╕╨▓╨╜╤Л╨╣ ╤Б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐ ("╨┤╨╕╨║╨░╤А╤М" / "╤З╤Г╨╢╨╛╨╣")
        if l.get("prejudice") and any(bad in l["prejudice"] for bad in ["╨┤╨╕╨║╨░╤А╨╡╨╝", "╤З╤Г╨╢╨╕╨╝", "╨┐╨╛╨┤╨╛╨╖╤А╨╡╨╜╨╕╨╡╨╝"]):
            if random.random() < 0.15:  # 15% ╤А╨╕╤Б╨║ ╨┐╤А╨╡╨┤╨▓╨╖╤П╤В╨╛╤Б╤В╨╕ ╨║╨╛╨╝╨╕╤Б╤Б╨╕╨╕
                success = False
                bias_failed = True

    g_m = l.get("gender") == "m"
    correct_text = test["opts"][test["ans"]]

    institution = l.pop("current_exam_institution", None)
    l.pop("current_exam_level", None)

    if success:
        inst_label = f" ({institution})" if institution else ""
        if saved_by_stereotype:
            msg = (
                f"ЁЯза <b>╨б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐ ╤Б╨┐╨░╤Б ╤Н╨║╨╖╨░╨╝╨╡╨╜{inst_label}!</b>\n"
                f"╨в╤Л ╨▓╤Л╨▒╤А╨░╨╗ ╨╜╨╡╨┐╤А╨░╨▓╨╕╨╗╤М╨╜╤Л╨╣ ╨╛╤В╨▓╨╡╤В, ╨╜╨╛ ╨║╨╛╨╝╨╕╤Б╤Б╨╕╤П ╤Б ╨┤╨╡╤В╤Б╤В╨▓╨░ ╤Б╤З╨╕╤В╨░╨╡╤В ╨┐╤А╨╡╨┤╤Б╤В╨░╨▓╨╕╤В╨╡╨╗╨╡╨╣ ╤В╨▓╨╛╨╡╨╣ ╨╜╨░╤Ж╨╕╨╛╨╜╨░╨╗╤М╨╜╨╛╤Б╤В╨╕ (┬л{l.get('ethnicity', '')} тАФ ╤Б╤З╨╕╤В╨░╤О╤В ╤Г╨╝╨╜╤Л╨╝┬╗) ╨▓╤Г╨╜╨┤╨╡╤А╨║╨╕╨╜╨┤╨░╨╝╨╕. "
                f"╨н╨║╨╖╨░╨╝╨╡╨╜╨░╤В╨╛╤А╤Л ╤А╨╡╤И╨╕╨╗╨╕, ╤З╤В╨╛ ╤В╤Л ╨╛╨│╨╛╨▓╨╛╤А╨╕╨╗╤Б╤П ╨╕╨╗╨╕ ╨┐╤А╨╕╨╝╨╡╨╜╨╕╨╗ ╨╜╨╡╤Б╤В╨░╨╜╨┤╨░╤А╤В╨╜╤Г╤О ╨╗╨╛╨│╨╕╨║╤Г, ╨╕ ╨┐╨╛╤Б╤В╨░╨▓╨╕╨╗╨╕ ╨╖╨░╤З╤С╤В!\n"
                f"<i>(╨Я╤А╨░╨▓╨╕╨╗╤М╨╜╤Л╨╣ ╨╛╤В╨▓╨╡╤В ╨▒╤Л╨╗: {correct_text})</i>"
            )
            l["happiness"] = min(100, l["happiness"] + 8)
        elif saved_by_knowledge:
            msg = (
                f"ЁЯУЪ <b>╨а╨╡╨┐╤Г╤В╨░╤Ж╨╕╤П ╨╛╤В╨╗╨╕╤З╨╜╨╕╨║╨░{inst_label}!</b>\n"
                f"╨в╤Л ╨┤╨╛╨┐╤Г╤Б╤В╨╕╨╗ ╨╛╨┐╨╗╨╛╤И╨╜╨╛╤Б╤В╤М, ╨╜╨╛ ╤В╨▓╨╛╤П ╨▓╤Л╤Б╨╛╨║╨░╤П ╤Н╤А╤Г╨┤╨╕╤Ж╨╕╤П (╨╖╨╜╨░╨╜╨╕╤П {l['knowledge']}%) ╤Г╨▒╨╡╨┤╨╕╨╗╨░ ╨┐╤А╨╡╨┐╨╛╨┤╨░╨▓╨░╤В╨╡╨╗╨╡╨╣, ╤З╤В╨╛ ╤Н╤В╨╛ ╤Б╨╗╤Г╤З╨░╨╣╨╜╨░╤П ╨╛╨┐╨╕╤Б╨║╨░ ╨╛╤В ╨▓╨╛╨╗╨╜╨╡╨╜╨╕╤П. "
                f"╨Ч╨░╤З╤С╤В ╨▓╤Л╤Б╤В╨░╨▓╨╗╨╡╨╜!"
            )
            l["happiness"] = min(100, l["happiness"] + 5)
        else:
            msg = f"тЬЕ <b>╨н╨║╨╖╨░╨╝╨╡╨╜ ╤Б╨┤╨░╨╜ ╨╜╨░ ╨╛╤В╨╗╨╕╤З╨╜╨╛{inst_label}!</b>\n╨Я╤А╨░╨▓╨╕╨╗╤М╨╜╤Л╨╣ ╨╛╤В╨▓╨╡╤В: <b>{correct_text}</b>."

        if l["age"] == 6:
            inst_name = institution or "╤И╨║╨╛╨╗╨░"
            l["education"] = f"╨Э╨░╤З╨░╨╗╤М╨╜╨╛╨╡ ({inst_name})"
            l["knowledge"] += 10
            add_to_life_map(l, f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ {inst_name}" if g_m else f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗╨░ ╨▓ {inst_name}")
        elif l["age"] == 12:
            inst_name = institution or "╨╗╨╕╤Ж╨╡╨╣/╨║╨╛╨╗╨╗╨╡╨┤╨╢"
            l["education"] = f"╨б╤А╨╡╨┤╨╜╨╡╨╡ ({inst_name})"
            l["knowledge"] += 15
            add_to_life_map(l, f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ {inst_name}" if g_m else f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗╨░ ╨▓ {inst_name}")
        elif l["age"] == 18:
            inst_name = institution or "╤Г╨╜╨╕╨▓╨╡╤А╤Б╨╕╤В╨╡╤В"
            l["education"] = f"╨Т╤Л╤Б╤И╨╡╨╡ ({inst_name})"
            l["knowledge"] += 25
            add_to_life_map(l, f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗ ╨▓ {inst_name}" if g_m else f"╨Я╨╛╤Б╤В╤Г╨┐╨╕╨╗╨░ ╨▓ {inst_name}")
    else:
        if bias_failed:
            msg = (
                f"тЪая╕П <b>╨Я╤А╨╡╨┤╨▓╨╖╤П╤В╨╛╤Б╤В╤М ╤Н╨║╨╖╨░╨╝╨╡╨╜╨░╤В╨╛╤А╨╛╨▓!</b>\n"
                f"╨в╤Л ╨╛╤В╨▓╨╡╤В╨╕╨╗ ╨░╨▒╤Б╨╛╨╗╤О╤В╨╜╨╛ ╨┐╤А╨░╨▓╨╕╨╗╤М╨╜╨╛ (<b>{correct_text}</b>), ╨╜╨╛ ╨╕╨╖-╨╖╨░ ╨┐╤А╨╡╨┤╤А╨░╤Б╤Б╤Г╨┤╨║╨╛╨▓ (┬л{l.get('prejudice', '')}┬╗) ╨║╨╛╨╝╨╕╤Б╤Б╨╕╤П ╨╖╨░╨┐╨╛╨┤╨╛╨╖╤А╨╕╨╗╨░ ╤Б╨┐╨╕╤Б╤Л╨▓╨░╨╜╨╕╨╡, "
                f"╨╖╨░╨▓╨░╨╗╨╕╨╗╨░ ╨║╨░╨▓╨╡╤А╨╖╨╜╤Л╨╝╨╕ ╨┐╤А╨╕╨┤╨╕╤А╨║╨░╨╝╨╕ ╨╕ ╨╛╤В╨║╨░╨╖╨░╨╗╨░ ╨▓ ╨╖╨░╤З╤С╤В╨╡."
            )
            l["happiness"] = max(0, l["happiness"] - 12)
        else:
            msg = f"тЭМ <b>╨н╨║╨╖╨░╨╝╨╡╨╜ ╨┐╤А╨╛╨▓╨░╨╗╨╡╨╜!</b>\n╨Э╨╡╨▓╨╡╤А╨╜╤Л╨╣ ╨╛╤В╨▓╨╡╤В (╨┐╤А╨░╨▓╨╕╨╗╤М╨╜╨╛ ╨▒╤Л╨╗╨╛: <i>{correct_text}</i>). ╨Я╨╛╤Б╤В╤Г╨┐╨╕╤В╤М ╨╜╨░ ╤Н╤В╨╛╤В ╤Г╤А╨╛╨▓╨╡╨╜╤М ╨┐╨╛╨║╨░ ╨╜╨╡ ╤Г╨┤╨░╨╗╨╛╤Б╤М."
            l["happiness"] = max(0, l["happiness"] - 5)

    l["last_result"] = {
        "success": success,
        "text": msg.replace("<b>","").replace("</b>","").replace("<i>","").replace("</i>","")
    }
    save_db(players_db)
    send_scene(chat_id, l, format_year(l), kb_focus(l), "school")

def apply_outcome(l, outcome):
    vvp = l["country"][7]
    is_bad = l["prejudice"] and any(t in l["prejudice"] for t in BAD_TRAITS_LOCAL)
    if outcome == "politics_win":
        cost = max(1000, int(vvp * 0.4))
        l["clean_cash"] = max(0, l["clean_cash"] - cost)
        l["political_reputation"] = min(100, l.get("political_reputation", 50) + 15)
        # ╨Я╨╡╤А╨╡╤Е╨╛╨┤ ╨╜╨░ ╨┐╨╛╨╗╨╜╨╛╤Ж╨╡╨╜╨╜╤Г╤О ╨┐╨╛╨╗╨╕╤В╨╕╤З╨╡╤Б╨║╤Г╤О ╨┤╨╛╨╗╨╢╨╜╨╛╤Б╤В╤М
        l["job_type"] = "politics"
        l["faction"] = "╨Я╤А╨░╨▓╤П╤Й╨░╤П ╨║╨╛╨░╨╗╨╕╤Ж╨╕╤П"
        l["job"] = "╨Я╨╛╨╗╨╕╤В╨╕╨║"
        l["career_rank"] = 1
        l["career_xp"] = 20
        l["job_years"] = 0
        l["salary"] = int(vvp * 1.0)
        bonus = int(vvp * 1.2)
        l["clean_cash"] += bonus
        l["happiness"] = min(100, l["happiness"] + 15)
        add_to_life_map(l, "╨Ш╨╖╨▒╤А╨░╨╜ ╨┤╨╡╨┐╤Г╤В╨░╤В╨╛╨╝ ╤Б╨╛╨▓╨╡╤В╨░ (╨╜╨░╤З╨░╨╗╨╛ ╨║╨░╤А╤М╨╡╤А╤Л ╨▓ ╨┐╨╛╨╗╨╕╤В╨╕╨║╨╡)")
        return f"ЁЯПЖ ╨Я╨╛╨▒╨╡╨┤╨░ ╨╜╨░ ╨▓╤Л╨▒╨╛╤А╨░╤Е! ╨Т╤Л ╨╛╤Б╤В╨░╨▓╨╕╨╗╨╕ ╨┐╤А╨╡╨╢╨╜╤О╤О ╤Б╨╗╤Г╨╢╨▒╤Г, ╨┐╨╛╨╗╤Г╤З╨╕╨╗╨╕ ╨┤╨╡╨┐╤Г╤В╨░╤В╤Б╨║╨╕╨╣ ╨╝╨░╨╜╨┤╨░╤В ╨╕ ╨┐╤А╨╡╨╝╨╕╤О {fmt_money(bonus, l['country'])}!"
    if outcome == "politics_fail":
        cost = max(1000, int(vvp * 0.4))
        l["clean_cash"] = max(0, l["clean_cash"] - cost)
        l["political_reputation"] = max(0, l.get("political_reputation", 50) - 8)
        l["happiness"] = max(0, l["happiness"] - 6)
        return "╨Я╨╛╤А╨░╨╢╨╡╨╜╨╕╨╡ ╨╜╨░ ╨▓╤Л╨▒╨╛╤А╨░╤Е. ╨б╤А╨╡╨┤╤Б╤В╨▓╨░ ╨╜╨░ ╨║╨░╨╝╨┐╨░╨╜╨╕╤О ╨┐╨╛╤В╤А╨░╤З╨╡╨╜╤Л, ╨╕╨╖╨▒╨╕╤А╨░╤В╨╡╨╗╨╕ ╨┐╤А╨╡╨┤╨┐╨╛╤З╨╗╨╕ ╨╛╨┐╨┐╨╛╨╜╨╡╨╜╤В╨░."
    if outcome == "politics_fail_free":
        l["happiness"] = max(0, l["happiness"] - 4)
        return "╨Ъ╨░╨╝╨┐╨░╨╜╨╕╤П ╨▒╨╡╨╖ ╨▒╤О╨┤╨╢╨╡╤В╨░ ╨╜╨╡ ╤Б╨╝╨╛╨│╨╗╨░ ╨┐╤А╨╕╨▓╨╗╨╡╤З╤М ╨▓╨╜╨╕╨╝╨░╨╜╨╕╨╡ ╨┐╤А╨╡╤Б╤Б╤Л ╨╕ ╨╕╨╖╨▒╨╕╤А╨░╤В╨╡╨╗╨╡╨╣."
    if outcome == "toddler_mama": l["relationships"] += 5; return "╨б╨║╨░╨╖╨░╨╗ ┬л╨╝╨░╨╝╨░┬╗."
    if outcome == "toddler_papa": l["relationships"] += 5; return "╨б╨║╨░╨╖╨░╨╗ ┬л╨┐╨░╨┐╨░┬╗."
    if outcome == "toddler_walk": l["health"] += 5; l["happiness"] += 10; return "╨Я╨╡╤А╨▓╤Л╨╣ ╤И╨░╨│!"
    if outcome == "toddler_fall": l["health"] -= 2; return "╨г╨┐╨░╨╗."
    if outcome == "toddler_crawl": l["happiness"] += 2; return "╨Я╨╛╨╗╨╖╨░╨╡╤И╤М."
    if outcome == "toddler_hug": l["happiness"] += 8; return "╨Ь╨╕╤И╨║╨░ ╤Г╤Б╨┐╨╛╨║╨╛╨╕╨╗."
    if outcome == "toddler_break": l["happiness"] -= 5; return "╨б╨╗╨╛╨╝╨░╨╗ ╨╕╨│╤А╤Г╤И╨║╤Г."
    if outcome == "prej_fight_win": l["clean_cash"] += int(vvp*0.5); l["prejudice"] = None; l["happiness"] += 10; return "╨б╨╗╨╛╨╝╨░╨╗ ╤Б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐!"
    if outcome == "prej_fight_fail": l["clean_cash"] -= int(vvp*0.2); l["diseases"].append("╨Я╨в╨б╨а"); l["health"] -= 10; return "╨Я╨╛╤В╤А╨░╤В╨╕╨╗ ╤Б╨╕╨╗╤Л."
    if outcome == "prej_exploit":
        if is_bad: l["dirty_cash"] += int(vvp*0.8); l["happiness"] -= 5; return "╨Ш╤Б╨┐╨╛╨╗╤М╨╖╨╛╨▓╨░╨╗ ╨╜╨╡╨│╨░╤В╨╕╨▓╨╜╤Л╨╣."
        else: l["clean_cash"] += int(vvp*0.3); l["career_xp"] += 20; l["happiness"] += 5; return "╨Ю╤Б╨╡╨┤╨╗╨░╨╗ ╨┐╨╛╨╖╨╕╤В╨╕╨▓╨╜╤Л╨╣!"
    if outcome == "prej_exploit_fail":
        if is_bad: l["in_prison"] = 3; l["happiness"] -= 20; l["ever_in_prison"] = True; return "╨б╨╡╨╗."
        else: l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 10; return "╨Т╤Л╨│╨╛╤А╨╡╨╗."
    if outcome == "prej_accept": l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 5; return "╨б╨╝╨╕╤А╨╕╨╗╤Б╤П."
    if outcome == "marry":
        g_m = l.get("gender") == "m"
        l["married"] = True; l["happiness"] += 20; l["relationships"] += 15; add_to_life_map(l, "╨Ц╨╡╨╜╨╕╨╗╤Б╤П" if g_m else "╨Т╤Л╤И╨╗╨░ ╨╖╨░╨╝╤Г╨╢")
        if random.random() < 0.6: l["children"] = l.get("children",0) + 1; add_to_life_map(l, "╨а╨╛╨┤╨╕╨╗╤Б╤П ╤А╨╡╨▒╤С╨╜╨╛╨║")
        return "╨Я╨╛╨╢╨╡╨╜╨╕╨╗╨╕╤Б╤М!"
    if outcome == "divorce":
        l["married"] = False
        if l["clean_cash"] > 0: l["clean_cash"] = int(l["clean_cash"] / 2)
        l["happiness"] -= 15; l["relationships"] -= 20
        add_pending_consequence(l, 5, {"id":"conseq_ex","title":"ЁЯТФ ╨Т╤Б╤В╤А╨╡╤З╨░ ╤Б ╨▒╤Л╨▓╤И╨╕╨╝","text":"╨б╨╗╤Г╤З╨░╨╣╨╜╨░╤П ╨▓╤Б╤В╤А╨╡╤З╨░.",
                                       "choices":[{"text":"╨Я╨╛╨│╨╛╨▓╨╛╤А╨╕╤В╤М","p":0.5,"success_effect":{"happiness":5,"relationships":5,"text":"╨Ь╨╕╤А╨╜╨╛."},"fail_effect":{"happiness":-10,"text":"╨Я╨╛╤А╤Г╨│╨░╨╗╨╕╤Б╤М."}},{"text":"╨Ь╨╕╨╝╨╛","p":1,"success_effect":{"text":"╨Я╤А╨╛╤И╤С╨╗."}}]})
        return "╨а╨░╨╖╨▓╨╛╨┤."
    if outcome == "job_civ": l["job_type"] = "civilian"; l["job"] = "╨а╨░╨▒╨╛╤В╨╜╨╕╨║"; l["salary"] = int(vvp * 0.6); l["relationships"] += 5; add_to_life_map(l, "╨Э╨░ ╤А╨░╨▒╨╛╤В╤Г"); return "╨в╤Л ╨╜╨░ ╨│╤А╨░╨╢╨┤╨░╨╜╨║╨╡."
    if outcome == "job_pol": l["job_type"] = "police"; l["faction"] = "╨Я╨╛╨╗╨╕╤Ж╨╕╤П"; l["job"] = "╨Я╨╛╨╗╨╕╤Ж╨╡╨╣╤Б╨║╨╕╨╣"; l["salary"] = int(vvp * 0.5); l["relationships"] += 10; add_to_life_map(l, "╨Т ╨┐╨╛╨╗╨╕╤Ж╨╕╨╕"); return "╨в╤Л ╨▓ ╨┐╨╛╨╗╨╕╤Ж╨╕╨╕."
    if outcome == "job_mil": l["job_type"] = "military"; l["faction"] = "╨Р╤А╨╝╨╕╤П"; l["job"] = "╨Т╨╛╨╡╨╜╨╜╤Л╨╣"; l["salary"] = int(vvp * 0.4); l["relationships"] += 15; add_to_life_map(l, "╨Т ╨░╤А╨╝╨╕╨╕"); return "╨в╤Л ╨▓ ╨░╤А╨╝╨╕╨╕."
    if outcome == "job_crim": l["job_type"] = "criminal"; l["faction"] = "╨г╨╗╨╕╤З╨╜╨░╤П ╨▒╨░╨╜╨┤╨░"; l["job"] = "╨С╨░╨╜╨┤╨╕╤В"; l["dirty_cash"] += int(vvp*0.5); l["happiness"] -= 10; add_to_life_map(l, "╨Ъ╤А╨╕╨╝╨╕╨╜╨░╨╗"); return "╨Ъ╤А╨╕╨╝╨╕╨╜╨░╨╗."
    if outcome == "career_xp_up": l["career_xp"] += 30; l["happiness"] -= 5; return "XP +30."
    if outcome == "career_xp_down": l["career_xp"] -= 20; return "XP -20."
    if outcome == "career_fight_win": l["career_xp"] += 40; l["happiness"] -= 5; return "XP +40."
    if outcome == "career_grind": l["career_xp"] -= 10; return "XP -10."
    if outcome == "work_extra": l["clean_cash"] += int(vvp*0.1); l["career_xp"] += 10; l["health"] -= 5; return "╨Т╤В╨╛╤А╨░╤П ╤А╨░╨▒╨╛╤В╨░."
    if outcome == "family_time": l["career_xp"] -= 10; l["happiness"] += 10; return "╨Т╤А╨╡╨╝╤П ╤Б ╤Б╨╡╨╝╤М╨╡╨╣."
    if outcome == "burnout": l["diseases"].append("╨б╨╡╤А╨┤╨╡╤З╨╜╨░╤П ╨╜╨╡╨┤╨╛╤Б╤В╨░╤В╨╛╤З╨╜╨╛╤Б╤В╤М"); l["health"] -= 20; return "╨Т╤Л╨│╨╛╤А╨░╨╜╨╕╨╡."
    if outcome == "scammed":
        loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss; l["happiness"] -= 20
        add_pending_consequence(l, 3, {"id":"conseq_scam","title":"ЁЯЪи ╨Т╨╛╨╖╨╝╨╡╨╖╨┤╨╕╨╡","text":"╨Ь╨╛╤И╨╡╨╜╨╜╨╕╨║╨░ ╨┐╨╛╨╣╨╝╨░╨╗╨╕!",
                                       "choices":[{"text":"╨Я╨╛╨┤╨░╤В╤М ╨╕╤Б╨║","p":0.7,"success_effect":{"cash":5000,"happiness":10,"text":"╨Т╨╡╤А╨╜╤Г╨╗╨╕!"},"fail_effect":{"cash":-1000,"text":"╨Ш╨╖╨┤╨╡╤А╨╢╨║╨╕."}},{"text":"╨Ч╨░╨▒╤Л╤В╤М","p":1,"success_effect":{"text":"╨Э╨╡ ╤Б╤В╨░╨╗."}}]})
        return f"╨г╨║╤А╨░╨╗╨╕ {fmt_money(loss, l['country'])}."
    if outcome == "child_fight": l["happiness"] += 5; return "╨Ф╨░╨╗ ╤Б╨┤╨░╤З╨╕."
    if outcome == "child_tell": return "╨Я╨╛╨╢╨░╨╗╨╛╨▓╨░╨╗╤Б╤П."
    if outcome == "child_smart": l["books_read"] = l.get("books_read",0) + 1; l["knowledge"] += 10; l["happiness"] += 5; return "╨Ъ╨╜╨╕╨│╨░ ╤А╨░╤Б╤И╨╕╤А╨╕╨╗╨░ ╨║╤А╤Г╨│╨╛╨╖╨╛╤А."
    if outcome == "child_walk": l["health"] += 5; l["happiness"] += 5; return "╨е╨╛╤А╨╛╤И╨╛ ╨┐╨╛╨│╤Г╨╗╤П╨╗."
    if outcome == "child_sport": l["health"] += 5; l["happiness"] += 8; l["relationships"] += 3; return "╨Ю╤В╨╗╨╕╤З╨╜╨╛ ╨┐╨╛╨╕╨│╤А╨░╨╗."
    if outcome == "child_injury": l["health"] -= 5; return "╨в╤А╨░╨▓╨╝╨░."
    if outcome == "child_bday_big": l["happiness"] += 15; l["relationships"] += 10; return "╨Ю╤В╨╗╨╕╤З╨╜╤Л╨╣ ╨┐╤А╨░╨╖╨┤╨╜╨╕╨║!"
    if outcome == "child_bday_bad": l["happiness"] -= 8; return "╨Ф╤А╤Г╨╖╤М╤П ╨╜╨╡ ╨┐╤А╨╕╤И╨╗╨╕."
    if outcome == "child_bday_small": l["happiness"] += 6; return "╨в╨╕╤Е╨╛, ╨╜╨╛ ╤Е╨╛╤А╨╛╤И╨╛."
    if outcome == "child_circus": l["happiness"] += 10; return "╨Т╨╛╨╗╤И╨╡╨▒╤Б╤В╨▓╨╛!"
    if outcome == "child_swim_good": l["health"] += 4; l["happiness"] += 6; return "╨Э╨░╤Г╤З╨╕╨╗╤Б╤П ╨┐╨╗╨░╨▓╨░╤В╤М."
    if outcome == "child_swim_fear": l["happiness"] -= 4; return "╨Ш╤Б╨┐╤Г╨│╨░╨╗╤Б╤П."
    if outcome == "child_sick_treat": l["health"] += 6; return "╨Я╨╡╤А╨╡╨▒╨╛╨╗╨╡╨╗."
    if outcome == "child_sick_walk_ok": l["happiness"] += 3; return "╨Я╨╛╨│╤Г╨╗╤П╨╗."
    if outcome == "child_sick_walk_bad": l["health"] -= 8; return "╨С╨╛╨╗╨╡╨╖╨╜╤М ╤Г╤Б╨╕╨╗╨╕╨╗╨░╤Б╤М."
    if outcome == "child_draw_win": l["happiness"] += 10; l["knowledge"] += 3; return "╨Я╨╛╨▒╨╡╨┤╨╕╨╗!"
    if outcome == "child_draw_lose": l["happiness"] += 2; return "╨Я╨╛╤Г╤З╨░╤Б╤В╨▓╨╛╨▓╨░╨╗."
    if outcome == "child_bike_ok": l["health"] += 3; l["happiness"] += 8; return "╨Я╨╛╨║╨░╤В╨░╨╗╤Б╤П."
    if outcome == "child_bike_fall": l["health"] -= 5; return "╨г╨┐╨░╨╗."
    if outcome == "child_bike_learn": l["health"] += 2; return "╨Ю╤Б╨▓╨╛╨╕╨╗."
    if outcome == "child_dog_ok": l["happiness"] += 6; return "╨Я╨╛╨│╨╗╨░╨┤╨╕╨╗."
    if outcome == "child_dog_bite": l["health"] -= 10; l["diseases"].append("╨Р╨╜╨╡╨╝╨╕╤П"); return "╨г╨║╤Г╤Б╨╕╨╗╨░."
    if outcome == "child_dog_run": return "╨г╨▒╨╡╨╢╨░╨╗."
    if outcome == "child_theater_good": l["happiness"] += 10; l["relationships"] += 5; return "╨Ю╤В╨╗╨╕╤З╨╜╨░╤П ╤А╨╛╨╗╤М!"
    if outcome == "child_theater_shy": l["happiness"] -= 3; return "╨Я╨╛╤Б╤В╨╡╤Б╨╜╤П╨╗╤Б╤П."
    if outcome == "child_theater_tech": l["knowledge"] += 3; return "╨Я╨╛╨╝╨╛╨│╨░╨╗ ╨╖╨░ ╨║╤Г╨╗╨╕╤Б╨░╨╝╨╕."
    if outcome == "teen_smoke":
        l["diseases"].append("╨а╨░╨║ ╨╗╨╡╨│╨║╨╕╤Е"); l["health"] -= 15
        add_pending_consequence(l, 25, {"id":"conseq_smoke","title":"ЁЯЪм ╨а╨░╤Б╨┐╨╗╨░╤В╨░","text":"╨У╨╛╨┤╤Л ╨║╤Г╤А╨╡╨╜╨╕╤П ╨┤╨░╨╗╨╕ ╨╛ ╤Б╨╡╨▒╨╡ ╨╖╨╜╨░╤В╤М.",
                                        "choices":[{"text":"╨Ы╨╡╤З╨╕╤В╤М╤Б╤П","p":0.6,"success_effect":{"cash":-5000,"health":10,"text":"╨Ю╨▒╨╛╤И╨╗╨╛╤Б╤М."},"fail_effect":{"diseases":["╨а╨░╨║ ╨╗╨╡╨│╨║╨╕╤Е"],"health":-25,"text":"╨а╨░╨║ ╨╗╤С╨│╨║╨╕╤Е."}}]})
        return "╨Ъ╤Г╤А╨╕╨╗."
    if outcome == "teen_healthy": l["clean_cash"] += 200; l["health"] += 5; return "╨б╤Н╨║╨╛╨╜╨╛╨╝╨╕╨╗."
    if outcome == "teen_love": l["happiness"] += 15; l["relationships"] += 10; return "╨Т╨╖╨░╨╕╨╝╨╜╨░╤П ╨╗╤О╨▒╨╛╨▓╤М."
    if outcome == "teen_heartbreak": l["diseases"].append("╨Я╨в╨б╨а"); l["happiness"] -= 15; l["relationships"] -= 10; return "╨Ю╤В╨║╨░╨╖."
    if outcome == "teen_sport_good": l["health"] += 8; l["happiness"] += 5; return "╨б╨┐╨╛╤А╤В ╨┐╨╛╤И╤С╨╗ ╨╜╨░ ╨┐╨╛╨╗╤М╨╖╤Г."
    if outcome == "teen_sport_hurt": l["health"] -= 6; return "╨в╤А╨░╨▓╨╝╨░."
    if outcome == "teen_games_win": l["happiness"] += 8; l["relationships"] += 5; return "╨Я╨╛╨▒╨╡╨┤╨░!"
    if outcome == "teen_games_lose": l["happiness"] += 3; return "╨Я╤А╨╛╨╕╨│╤А╨░╨╗, ╨╜╨╛ ╨▓╨╡╤Б╨╡╨╗╨╛."
    if outcome == "teen_study": l["knowledge"] += 6; return "╨Я╨╛╨╖╨░╨╜╨╕╨╝╨░╨╗╤Б╤П."
    if outcome == "teen_fight_win": l["happiness"] += 8; l["relationships"] -= 3; return "╨Ф╨░╨╗ ╤Б╨┤╨░╤З╨╕."
    if outcome == "teen_fight_lose": l["health"] -= 8; return "╨Я╨╛╨╗╤Г╤З╨╕╨╗."
    if outcome == "teen_tell_teacher": l["relationships"] += 3; return "╨г╤З╨╕╤В╨╡╨╗╤М ╨▓╨╝╨╡╤И╨░╨╗╤Б╤П."
    if outcome == "teen_band": l["happiness"] += 10; l["relationships"] += 5; return "╨Ш╨│╤А╨░ ╨▓ ╨│╤А╤Г╨┐╨┐╨╡!"
    if outcome == "teen_license_ok": l["has_license"] = True; l["happiness"] += 10; return "╨Я╨╛╨╗╤Г╤З╨╕╨╗ ╨┐╤А╨░╨▓╨░!"
    if outcome == "teen_license_fail": l["happiness"] -= 3; return "╨Э╨╡ ╤Б╨┤╨░╨╗."
    if outcome == "lottery_win": l["clean_cash"] += int(vvp * 5); l["happiness"] += 30; return "╨Ф╨Ц╨Х╨Ъ╨Я╨Ю╨в!"
    if outcome == "lottery_lose": l["clean_cash"] -= 100; l["happiness"] -= 5; return "╨С╨╕╨╗╨╡╤В ╨┐╤Г╤Б╤В╨╛╨╣."
    if outcome == "bribe_dps": l["dirty_cash"] -= int(vvp*0.1); return "╨Я╤А╨╛╨╜╨╡╤Б╨╗╨╛."
    if outcome == "dps_jail": l["in_prison"] = 1; l["happiness"] -= 15; l["ever_in_prison"] = True; return "1 ╨│╨╛╨┤ ╤В╤О╤А╤М╨╝╤Л."
    if outcome == "dps_warning": return "╨Ш╨╜╤Б╨┐╨╡╨║╤В╨╛╤А ╨┐╤А╨╡╨┤╤Г╨┐╤А╨╡╨┤╨╕╨╗."
    if outcome == "bribe_dps_big": l["dirty_cash"] -= int(vvp*0.3); return "╨Ю╤В╨║╤Г╨┐╨╕╨╗╤Б╤П."
    if outcome == "drunk_jail": l["in_prison"] = 3; l["cars"] = []; l["happiness"] -= 30; l["ever_in_prison"] = True; return "3 ╨│╨╛╨┤╨░ + ╨║╨╛╨╜╤Д╨╕╤Б╨║╨░╤Ж╨╕╤П."
    return "╨У╨╛╨┤ ╨┐╤А╨╛╤И╨╡╨╗."

def resolve_choice(user_id, chat_id, i):
    l = players_db[str(user_id)]
    evt = l.get("current_event")
    if not evt: return
    if evt.get("resolved"): return
    if i < 0 or i >= len(evt["choices"]): return
    c = evt["choices"][i]
    success = random.random() < c["p"]
    
    # ╨б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐ "╤Б╤З╨╕╤В╨░╤О╤В ╤Г╨╝╨╜╤Л╨╝" ╨┐╨╛╨╝╨╛╨│╨░╨╡╤В ╨▓ ╨║╨╛╨╜╤В╤А╨╛╨╗╤М╨╜╤Л╤Е, ╤Н╨║╨╖╨░╨╝╨╡╨╜╨░╤Е ╨╕ ╨╛╨╗╨╕╨╝╨┐╨╕╨░╨┤╨░╤Е
    if not success and l.get("prejudice") and "╤Г╨╝╨╜╤Л╨╝" in l["prejudice"]:
        title_low = evt.get("title", "").lower()
        if any(term in title_low for term in ["╤Н╨║╨╖╨░╨╝╨╡╨╜", "╨╛╨╗╨╕╨╝╨┐╨╕╨░╨┤", "╤Г╤З╤С╨▒", "╤Г╨╜╨╕╨▓╨╡╤А", "╤И╨║╨╛╨╗", "╨║╨╛╨╜╤В╤А╨╛╨╗╤М╨╜", "╨║╤Г╤А╤Б", "╨┤╨╕╨┐╨╗╨╛╨╝"]):
            if random.random() < 0.45:
                success = True
                if "success_effect" in c:
                    c = dict(c)
                    eff = dict(c["success_effect"])
                    eff["text"] = "ЁЯза ╨б╤В╨╡╤А╨╡╨╛╤В╨╕╨┐ ╨┐╨╛╨╝╨╛╨│: " + eff.get("text", "")
                    c["success_effect"] = eff
    if "success_effect" in c:
        effect = c.get("success_effect") if success else c.get("fail_effect", {"text":"╨У╨╛╨┤ ╨┐╤А╨╛╤И╨╡╨╗."})
        text = apply_direct_effect(l, effect); outcome = "direct"
    else:
        outcome = c["success"] if success else c.get("fail", "none")
        text = apply_outcome(l, outcome) if outcome else "╨У╨╛╨┤ ╨┐╤А╨╛╤И╨╡╨╗."
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
    visuals = get_scene_visuals("life", l["gender"], ethnicity=l.get("ethnicity"), region=c[2], age=l.get("age"))
    parts = [f"<b>╨Т╨╛╨╖╤А╨░╤Б╤В: {get_age_str(l['age'])}</b>\n{visuals}"]
    if l.get("last_result"): parts.append(f"\n{'тЬЕ' if l['last_result']['success'] else 'тЭМ'} <i>{l['last_result']['text']}</i>")
    parts.append(f"\n{get_stats_line(l)}")
    parts.append(f"\nЁЯзм ╨Я╤А╨╛╨╕╤Б╤Е╨╛╨╢╨┤╨╡╨╜╨╕╨╡: <b>{l['ethnicity']}</b>")
    if l["prejudice"]: parts.append(f"тЪая╕П <i>╨Ю╨▒╤Й╨╡╤Б╤В╨▓╨╛: {l['prejudice']}</i>")
    parts.append(f"ЁЯТ░ ╨С╨░╨╗╨░╨╜╤Б: <b>{fmt_money(l['clean_cash'], c)}</b>")
    if l["age"] <= 6: parts.append("ЁЯСитАНЁЯСйтАНЁЯСз <i>╨Ц╨╕╨▓╤С╤И╤М ╨╜╨░ ╨╛╨▒╨╡╤Б╨┐╨╡╤З╨╡╨╜╨╕╨╕ ╤А╨╛╨┤╨╕╤В╨╡╨╗╨╡╨╣</i>")
    elif l["age"] <= 13: parts.append("ЁЯкЩ <i>╨Ъ╨░╤А╨╝╨░╨╜╨╜╤Л╨╡ ╨╛╤В ╤А╨╛╨┤╨╕╤В╨╡╨╗╨╡╨╣</i>")
    elif l["age"] <= 17: parts.append("ЁЯТ╝ <i>╨Я╨╛╨┤╤А╨░╨▒╨╛╤В╨║╨░ ╨┐╨╛╤Б╨╗╨╡ ╤Г╤З╤С╨▒╤Л</i>")
    if l["dirty_cash"] > 0: parts.append(f"ЁЯТ╝ ╨У╤А╤П╨╖╨╜╤Л╨╡: <b>{fmt_money(l['dirty_cash'], c)}</b>")
    if l["debt"] > 0: parts.append(f"ЁЯПж ╨Ф╨╛╨╗╨│: <b>{fmt_money(l['debt'], c)}</b>")
    parts.append(f"ЁЯСС ╨Ъ╨╗╨░╤Б╤Б: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian","police","military","criminal","politics"]:
        job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'],'')}, XP: {l['career_xp']}/100)"
    parts.append(f"ЁЯТ╝ {job}")
    if l["properties"]: parts.append("ЁЯПа " + ", ".join([p["type"] for p in l["properties"]]))
    if l["cars"]: parts.append("ЁЯЪЧ " + ", ".join([c["type"] for c in l["cars"]]))
    if l["businesses"]: parts.append("ЁЯПв " + ", ".join([b["type"] for b in l["businesses"]]))
    if l.get("investments"): parts.append("ЁЯУИ ╨Я╨╛╤А╤В╤Д╨╡╨╗╤М: " + ", ".join([f"{i['type']} ({fmt_money(i['amount'], c)})" for i in l["investments"]]))
    if l.get("political_reputation", 50) != 50 or l.get("job_type") == "civilian": parts.append(f"ЁЯПЫ ╨Я╨╛╨╗╨╕╤В╨╕╤З╨╡╤Б╨║╨╛╨╡ ╨▓╨╗╨╕╤П╨╜╨╕╨╡: {l.get('political_reputation', 50)}/100")
    if l["diseases"]: parts.append(f"ЁЯй║ {', '.join(l['diseases'])}")
    parts.append(f"ЁЯОУ {l['education']}")
    parts.append(f"ЁЯСитАНЁЯСйтАНЁЯСз ╨Ф╨╡╤В╨╕: {l['children']} | ╨С╤А╨░╨║: {'╨Ф╨░' if l['married'] else '╨Э╨╡╤В'}")
    return "\n".join(parts)

def format_event(l, evt):
    c = l.get("country", ["","","default"])
    visuals = get_scene_visuals("life", l["gender"], ethnicity=l.get("ethnicity"), region=c[2], age=l.get("age"))
    return f"<b>{get_age_str(l['age'])} ┬╖ {evt['title']}</b>\n{visuals}\n\n{get_stats_line(l)}\n\n{evt['text']}"

def send_scene(chat_id, l, text, kb, scene_type="life"):
    if not text.startswith("<b>"):
        c = l.get("country", ["","","default"])
        visuals = get_scene_visuals(scene_type, l["gender"], ethnicity=l.get("ethnicity"), region=c[2], age=l.get("age"))
        text = f"{visuals}\n\n{text}"
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("ЁЯО▓ ╨а╨╛╨┤╨╕╤В╤М╤Б╤П", callback_data="new"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("тЦ╢я╕П ╨б╨╗╨╡╨┤╤Г╤О╤Й╨╕╨╣ ╨│╨╛╨┤", callback_data="year")).add(InlineKeyboardButton("ЁЯЫТ ╨Ь╨░╨│╨░╨╖╨╕╨╜", callback_data="shop"))

def kb_focus(l=None):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("тЭдя╕П ╨Ч╨┤╨╛╤А╨╛╨▓╤М╨╡", callback_data="focus_health"), InlineKeyboardButton("ЁЯза ╨Ч╨╜╨░╨╜╨╕╤П", callback_data="focus_knowledge"))
    kb.add(InlineKeyboardButton("ЁЯдЭ ╨Ю╤В╨╜╨╛╤И╨╡╨╜╨╕╤П", callback_data="focus_relationships"), InlineKeyboardButton("ЁЯШК ╨б╤З╨░╤Б╤В╤М╨╡", callback_data="focus_happiness"))
    if l and l.get("job_type") in ("civilian","police","military","criminal"):
        kb.add(InlineKeyboardButton("ЁЯТ╝ ╨а╨░╨▒╨╛╤В╨░", callback_data="focus_work"))
    kb.add(InlineKeyboardButton("ЁЯПЖ ╨в╨╛╨┐ ╨╢╨╕╨╖╨╜╨╡╨╣", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("ЁЯУЦ ╨Ф╨╛╤Б╤В╨╕╨╢╨╡╨╜╨╕╤П", callback_data="achievements"))
    kb.add(InlineKeyboardButton("тЦ╢я╕П ╨Я╤А╨╛╨┐╤Г╤Б╤В╨╕╤В╤М", callback_data="year"))
    kb.add(InlineKeyboardButton("ЁЯЫТ ╨Ь╨░╨│╨░╨╖╨╕╨╜", callback_data="shop"))
    return kb

def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

def open_shop(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("ЁЯПа ╨Э╨╡╨┤╨▓╨╕╨╢╨╕╨╝╨╛╤Б╤В╤М", callback_data="shop_prop")
    ).add(
        InlineKeyboardButton("ЁЯЪЧ ╨Р╨▓╤В╨╛", callback_data="shop_car")
    ).add(
        InlineKeyboardButton("ЁЯПв ╨С╨╕╨╖╨╜╨╡╤Б╤Л", callback_data="shop_biz")
    ).add(
        InlineKeyboardButton("ЁЯУИ ╨Ш╨╜╨▓╨╡╤Б╤В╨╕╤Ж╨╕╨╕", callback_data="shop_invest")
    )
    if l.get("debt", 0) > 0:
        kb.add(InlineKeyboardButton(f"ЁЯТ│ ╨Я╨╛╨│╨░╤Б╨╕╤В╤М ╨┤╨╛╨╗╨│ ({fmt_money(l['debt'], c)})", callback_data="shop_pay_debt"))
    kb.add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤", callback_data="year"))
    msg = bot.send_message(chat_id, f"ЁЯЫТ <b>╨Ь╨░╨│╨░╨╖╨╕╨╜</b>\n╨С╨░╨╗╨░╨╜╤Б: {fmt_money(l['clean_cash'], c)}\n╨Ф╨╛╨╗╨│: {fmt_money(l.get('debt', 0), c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_prop_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items(): kb.add(InlineKeyboardButton(f"тЬЕ {name} тАФ {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤", callback_data="shop"))
    msg = bot.send_message(chat_id, f"ЁЯПа <b>╨Э╨╡╨┤╨▓╨╕╨╢╨╕╨╝╨╛╤Б╤В╤М</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_car_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items(): kb.add(InlineKeyboardButton(f"тЬЕ {name} тАФ {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    if not l.get("has_license"):
        lic_price = int(c[7] * 0.05)
        kb.add(InlineKeyboardButton(f"ЁЯкк ╨Ъ╤Г╨┐╨╕╤В╤М ╨┐╤А╨░╨▓╨░ тАФ {fmt_money(lic_price, c)}", callback_data="buy_license"))
    kb.add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤", callback_data="shop"))
    msg = bot.send_message(chat_id, f"ЁЯЪЧ <b>╨Р╨▓╤В╨╛</b>\n╨Э╨░╨╗╨╕╤З╨╕╨╡ ╨┐╤А╨░╨▓: {'╨Ф╨░' if l.get('has_license') else '╨Э╨╡╤В'}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)


def shop_invest_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, data in INVESTMENT_ASSETS.items():
        kb.add(InlineKeyboardButton(f"ЁЯУИ {name} тАФ {fmt_money(data['price'], c)}", callback_data=f"buy_invest_{name}"))
    kb.add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤", callback_data="shop"))
    msg = bot.send_message(chat_id, f"ЁЯУИ <b>╨Ш╨╜╨▓╨╡╤Б╤В╨╕╤Ж╨╕╨╛╨╜╨╜╤Л╨╣ ╤А╤Л╨╜╨╛╨║</b>\n╨Т╨║╨╗╨░╨┤╤Л╨▓╨░╨╣╤В╨╡ ╤Б╤А╨╡╨┤╤Б╤В╨▓╨░ ╨▓ ╨░╨║╤В╨╕╨▓╤Л ╨┤╨╗╤П ╨╡╨╢╨╡╨│╨╛╨┤╨╜╨╛╨╣ ╨┤╨╛╤Е╨╛╨┤╨╜╨╛╤Б╤В╨╕.\n╨С╨░╨╗╨░╨╜╤Б: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_biz_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items(): kb.add(InlineKeyboardButton(f"ЁЯПв {name} тАФ {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("тмЕя╕П ╨Э╨░╨╖╨░╨┤", callback_data="shop"))
    msg = bot.send_message(chat_id, f"ЁЯПв <b>╨С╨╕╨╖╨╜╨╡╤Б╤Л</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def process_buy(user_id, chat_id, cat, name):
    l = players_db[str(user_id)]; c = l["country"]
    if cat == "debt":
        debt = l.get("debt", 0)
        if debt <= 0:
            return bot.send_message(chat_id, "тЬЕ ╨г ╨▓╨░╤Б ╨╜╨╡╤В ╨┤╨╛╨╗╨│╨╛╨▓!", reply_markup=kb_year())
        if l["clean_cash"] <= 0:
            return bot.send_message(chat_id, "тЭМ ╨г ╨▓╨░╤Б ╨╜╨╡╤В ╤Б╨▓╨╛╨▒╨╛╨┤╨╜╤Л╤Е ╨┤╨╡╨╜╨╡╨│ ╨┤╨╗╤П ╨┐╨╛╨│╨░╤И╨╡╨╜╨╕╤П ╨┤╨╛╨╗╨│╨░!", reply_markup=kb_year())
        pay_amount = min(l["clean_cash"], debt)
        l["clean_cash"] -= pay_amount
        l["debt"] -= pay_amount
        save_db(players_db)
        if l["debt"] == 0:
            add_to_life_map(l, "╨Я╨╛╨╗╨╜╨╛╤Б╤В╤М╤О ╨▓╤Л╨┐╨╗╨░╤В╨╕╨╗ ╨┤╨╛╨╗╨│╨╕")
            return bot.send_message(chat_id, f"ЁЯОЙ <b>╨Ф╨╛╨╗╨│ ╨┐╨╛╨╗╨╜╨╛╤Б╤В╤М╤О ╨┐╨╛╨│╨░╤И╨╡╨╜!</b>\n╨Т╤Л╨┐╨╗╨░╤З╨╡╨╜╨╛: {fmt_money(pay_amount, c)}.", reply_markup=kb_year(), parse_mode="HTML")
        else:
            return bot.send_message(chat_id, f"ЁЯТ│ <b>╨з╨░╤Б╤В╤М ╨┤╨╛╨╗╨│╨░ ╨┐╨╛╨│╨░╤И╨╡╨╜╨░!</b>\n╨Т╤Л╨┐╨╗╨░╤З╨╡╨╜╨╛: {fmt_money(pay_amount, c)}.\n╨Ю╤Б╤В╨░╤В╨╛╨║ ╨┤╨╛╨╗╨│╨░: {fmt_money(l['debt'], c)}.", reply_markup=kb_year(), parse_mode="HTML")
    if cat == "license":
        price = int(c[7] * 0.05)
        if l["clean_cash"] < price: return bot.send_message(chat_id, "тЭМ ╨Ь╨░╨╗╨╛ ╨┤╨╡╨╜╨╡╨│ ╨╜╨░ ╨┐╤А╨░╨▓╨░!", reply_markup=kb_year())
        l["clean_cash"] -= price; l["has_license"] = True; save_db(players_db)
        return bot.send_message(chat_id, "ЁЯОЙ ╨в╤Л ╨┐╨╛╨╗╤Г╤З╨╕╨╗ ╨▓╨╛╨┤╨╕╤В╨╡╨╗╤М╤Б╨║╨╕╨╡ ╨┐╤А╨░╨▓╨░!", reply_markup=kb_year(), parse_mode="HTML")
    if cat == "prop": base = PROPERTIES[name]
    elif cat == "car": base = CARS[name]
    elif cat == "biz": base = BUSINESSES[name]
    elif cat == "invest": base = INVESTMENT_ASSETS[name]["price"]
    else: base = 0
    if l["clean_cash"] < base: return bot.send_message(chat_id, "тЭМ ╨Ь╨░╨╗╨╛ ╨┤╨╡╨╜╨╡╨│!", reply_markup=kb_year())
    l["clean_cash"] -= base
    if cat == "prop": l["properties"].append({"type":name,"value":base}); add_to_life_map(l, f"╨Ъ╤Г╨┐╨╕╨╗ {name}")
    elif cat == "car": l["cars"].append({"type":name,"value":base}); add_to_life_map(l, f"╨Ъ╤Г╨┐╨╕╨╗ {name}")
    elif cat == "biz": l["businesses"].append({"type":name,"value":base}); add_to_life_map(l, f"╨Ю╤В╨║╤А╤Л╨╗ {name}")
    elif cat == "invest":
        existing = next((i for i in l.setdefault("investments", []) if i["type"] == name), None)
        if existing: existing["amount"] += base
        else: l["investments"].append({"type": name, "amount": base})
        add_to_life_map(l, f"╨Ъ╤Г╨┐╨╕╨╗ ╨░╨║╤В╨╕╨▓╤Л: {name}")
    save_db(players_db)
    bot.send_message(chat_id, f"ЁЯОЙ ╨Ъ╤Г╨┐╨╗╨╡╨╜╨╛: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= ╨Ю╨С╨а╨Р╨С╨Ю╨в╨з╨Ш╨Ъ╨Ш =================
