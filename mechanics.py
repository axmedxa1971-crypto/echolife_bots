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
        return {"id":"fallback","title":"рџ“… РћР±С‹С‡РЅС‹Р№ РіРѕРґ","text":"РќРёС‡РµРіРѕ РѕСЃРѕР±РµРЅРЅРѕРіРѕ.",
                "choices":[{"text":"РџСЂРѕРґРѕР»Р¶РёС‚СЊ","p":1,"success_effect":{"text":"РЎРїРѕРєРѕР№РЅС‹Р№ РіРѕРґ."}}]}
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
    if event_type == "birth": return ["рџЏҐ рџ‘ЁвЂЌвљ•пёЏ рџ¤°\n<i>Р’СЂР°С‡Рё РіРѕС‚РѕРІСЏС‚СЃСЏ...</i>","рџ‘¶ вњЁ рџ‘ЁвЂЌрџ‘©вЂЌрџ‘¦\n<i>Р Р°Р·РґР°РµС‚СЃСЏ РїРµСЂРІС‹Р№ РєСЂРёРє!</i>","рџЋ‰ рџЌј рџ§ё\n<i>РќРѕРІР°СЏ Р¶РёР·РЅСЊ РЅР°С‡Р°Р»Р°СЃСЊ!</i>"]
    if event_type == "marry": return ["рџ’ђ рџЌ· рџ‘©вЂЌвќ¤пёЏвЂЌрџ‘Ё\n<i>Р РѕРјР°РЅС‚РёС‡РµСЃРєРёР№ СѓР¶РёРЅ...</i>","рџ¤µ рџ‘° рџ’Ќ\n<i>РџСЂРµРґР»РѕР¶РµРЅРёРµ СЂСѓРєРё Рё СЃРµСЂРґС†Р°!</i>","рџҐ‚ рџЋ‰ рџ’–\n<i>РЎРІР°РґСЊР±Р°!</i>"]
    if event_type == "prison": return ["рџљ” рџљЁ рџЏѓвЂЌв™‚пёЏ\n<i>РџРѕРіРѕРЅСЏ...</i>","рџ‘®вЂЌв™‚пёЏ рџ”— рџ‘Ё\n<i>Р—Р°РґРµСЂР¶Р°РЅРёРµ...</i>","в›“ рџ§± рџљЄ\n<i>Р”РІРµСЂСЊ РєР°РјРµСЂС‹ Р·Р°С…Р»РѕРїРЅСѓР»Р°СЃСЊ.</i>"]
    if event_type == "death": return ["рџЏҐ рџ›Њ рџ’”\n<i>Р—РґРѕСЂРѕРІСЊРµ РїРѕРґРІРѕРґРёС‚...</i>","рџ•ЇпёЏ вЃпёЏ\n<i>РџРѕСЃР»РµРґРЅРёР№ РІР·РґРѕС…...</i>","рџЄ¦ рџҐЂ рџ•ЉпёЏ\n<i>Р–РёР·РЅСЊ РѕРєРѕРЅС‡РµРЅР°.</i>"]
    return []

def get_scene_visuals(scene_type, gender, ethnicity=None, region=None, age=None):
    player = get_person_emoji("player", gender=gender, ethnicity=ethnicity, region=region, age=age)
    scenes = {"military":f"рџЋ– рџЄ– {player} рџЄ– рџ›Ў","criminal":f"рџ•¶ рџ”« {player} рџ’° рџ’Ј","child":f"рџЏ  рџЊі {player} рџ§ё вЂпёЏ","toddler":f"рџЌј рџ§ё {player} рџЋ€ рџЊџ","school":f"рџЏ« {player} рџ“љ рџЋ’ рџЌЋ","rich":f"рџЏ° рџљ— рџ’° {player} рџҐ‚ рџ›Ґ","office":f"рџЏў рџ§‘вЂЌрџ’» {player} рџ“Љ в•","office_angry":f"рџЏў рџЎ {player} рџ’ў рџ“‰","hospital":f"рџЏҐ рџ›Њ {player} рџ’‰ рџ©є","prison":f"в›“ рџ§± {player} рџљ” рџ•¶","fight":f"рџ‘Љ рџ’Ґ {player} рџҐЉ рџ¤•","love":f"вќ¤пёЏ {player} рџЊ№ рџ’‘ рџ’ђ","wedding":f"рџ’Ќ рџ¤µ рџ‘° {player} рџЋ‰","sad":f"рџЊ§ {player} в‚пёЏ рџ” рџ’§","police":f"рџљ” рџ’µ {player} рџљЁ рџ°","money_win":f"рџ’° рџ¤‘ {player} рџ’Ћ рџЋ°","money_lose":f"рџ’ё рџ­ {player} рџ•і рџ“‰"}
    return scenes.get(scene_type, f"рџЊ† {player} рџЏ™ рџљ¶")

def fmt_money(amount_usd, country):
    return f"{int(amount_usd * country[8]):,} {country[9]}".replace(",", " ")

def get_wealth_status(clean, dirty, l=None):
    total = clean + dirty
    if l and l.get("properties"): total += sum(p["value"] for p in l["properties"])
    if l and l.get("cars"): total += sum(c["value"] for c in l["cars"])
    if total < 0: return "рџ’ё Р’ РґРѕР»РіР°С…"
    if total < 500: return "рџҐЂ РќРёС‰РёР№"
    if total < 5000: return "рџ‘• Р‘РµРґРЅС‹Р№"
    if total < 20000: return "рџ”§ Р Р°Р±РѕС‡РёР№ РєР»Р°СЃСЃ"
    if total < 100000: return "рџЏ  РЎСЂРµРґРЅРёР№ РєР»Р°СЃСЃ"
    if total < 500000: return "рџ’ј Р—Р°Р¶РёС‚РѕС‡РЅС‹Р№"
    if total < 2000000: return "рџ’Ћ Р‘РѕРіР°С‡"
    return "рџ‘‘ Р­Р»РёС‚Р°"

def weighted_country():
    r = random.random() * TOTAL_WEIGHT
    for c in COUNTRIES:
        r -= c[3]
        if r <= 0: return c
    return COUNTRIES[0]

def get_ethnicity(region):
    r = random.random() * 100; cum = 0
    for name, chance, prejudice in ETHNICITIES.get(region, [("РњРµСЃС‚РЅС‹Р№",100,None)]):
        cum += chance
        if r <= cum: return name, prejudice
    return "РњРµСЃС‚РЅС‹Р№", None

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
        if n["death_age"] < 3: return "СѓРјРµСЂ(Р»Р°) РІ РјР»Р°РґРµРЅС‡РµСЃС‚РІРµ"
        elif n["death_age"] < 18: return f"СѓРјРµСЂ(Р»Р°) РѕС‚ Р±РѕР»РµР·РЅРё РІ {get_age_str(n['death_age'])}"
        elif n["trajectory"] == "criminal": return f"РїРѕРіРёР±(Р»Р°) РІ СЂР°Р·Р±РѕСЂРєРµ РІ {get_age_str(n['death_age'])}"
        else: return f"СѓРјРµСЂ(Р»Р°) РІ {get_age_str(n['death_age'])}"
    if age < 13:
        if n["trajectory"] == "unfortunate": return "Р¶РёРІРµС‚ РІ Р±РµРґРЅРѕСЃС‚Рё"
        elif n["trajectory"] == "prosperous": return "С…РѕРґРёС‚ РІ СЌР»РёС‚РЅСѓСЋ С€РєРѕР»Сѓ"
        else: return "С…РѕРґРёС‚ РІ С€РєРѕР»Сѓ"
    elif age < 25:
        if n["trajectory"] == "criminal": return "СЃРІСЏР·Р°Р»СЃСЏ СЃ Р±Р°РЅРґРѕР№" if g_m else "СЃРІСЏР·Р°Р»Р°СЃСЊ СЃ Р±Р°РЅРґРѕР№"
        elif n["trajectory"] == "prosperous": return "РїРѕСЃС‚СѓРїРёР» РІ РІСѓР·" if g_m else "РїРѕСЃС‚СѓРїРёР»Р° РІ РІСѓР·"
        else: return "СЂР°Р±РѕС‚Р°РµС‚"
    elif age < 55:
        if n["trajectory"] == "criminal": return "СЃРёРґРёС‚ РІ С‚СЋСЂСЊРјРµ"
        elif n["trajectory"] == "prosperous": return "СЃС‚Р°Р» Р±РѕРіР°С‚С‹Рј" if g_m else "СЃС‚Р°Р»Р° Р±РѕРіР°С‚РѕР№"
        else: return "СЂР°Р±РѕС‚Р°РµС‚ РЅР° Р·Р°РІРѕРґРµ"
    return "РЅР° РїРµРЅСЃРёРё"

def get_neighbor_final(n):
    if n["death_age"] < 3: return "СѓРјРµСЂ(Р»Р°) РІ РјР»Р°РґРµРЅС‡РµСЃС‚РІРµ"
    elif n["trajectory"] == "criminal": return f"РїРѕРіРёР±(Р»Р°) РІ СЂР°Р·Р±РѕСЂРєРµ РІ {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "prosperous": return f"СѓРјРµСЂ(Р»Р°) Р±РѕРіР°С‚С‹Рј(РѕР№) РІ {get_age_str(n['death_age'])}"
    elif n["trajectory"] == "unfortunate": return f"СѓРјРµСЂ(Р»Р°) РІ Р±РµРґРЅРѕСЃС‚Рё РІ {get_age_str(n['death_age'])}"
    else: return f"СѓРјРµСЂ(Р»Р°) РІ {get_age_str(n['death_age'])}"

# ================= NPC Р РџР Р•Р”Р«РЎРўРћР РРЇ =================
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
            add_to_life_map(l, f"РЈРјРµСЂ(Р»Р°) {role_ru} {npc['name']}")
            if npc["role"] in ("mother","father","friend"):
                l["happiness"] = max(0, l["happiness"] - 5)

def get_npc_epilogue(npc):
    role_ru = NPC_ROLES_DESC.get(npc["role"], npc["role"])
    fate = f"СѓРјРµСЂ(Р»Р°) РІ {get_age_str(npc['death_age'])}" if npc["dead"] else "Р¶РёРІ(Р°)"
    rel = npc["relation"]
    if rel >= 60: mood = "Р±С‹Р»(Р°) СЂСЏРґРѕРј"
    elif rel >= 20: mood = "С‚С‘РїР»С‹Рµ РѕС‚РЅРѕС€РµРЅРёСЏ"
    elif rel >= -20: mood = "РЅРµР№С‚СЂР°Р»СЊРЅРѕ"
    else: mood = "РёСЃРїРѕСЂС‚РёР»РёСЃСЊ"
    return f"вЂў {role_ru} {npc['name']}: {fate} вЂ” {mood}"

def generate_world_context(country):
    year = 2025 + random.randint(-5, 5)
    global_states = [
        {"icon":"рџЊЌ","title":"РћС‚РЅРѕСЃРёС‚РµР»СЊРЅР°СЏ СЃС‚Р°Р±РёР»СЊРЅРѕСЃС‚СЊ","desc":"РќРµС‚ РєСЂСѓРїРЅС‹С… РІРѕР№РЅ. Р­РєРѕРЅРѕРјРёРєР° СЂР°СЃС‚С‘С‚."},
        {"icon":"вљ пёЏ","title":"Р“Р»РѕР±Р°Р»СЊРЅР°СЏ РЅР°РїСЂСЏР¶С‘РЅРЅРѕСЃС‚СЊ","desc":"РЎР°РЅРєС†РёРё, РєРѕРЅС„Р»РёРєС‚С‹, РіРѕРЅРєР° РІРѕРѕСЂСѓР¶РµРЅРёР№."},
        {"icon":"рџ“€","title":"Р­РєРѕРЅРѕРјРёС‡РµСЃРєРёР№ РїРѕРґСЉС‘Рј","desc":"Р С‹РЅРєРё СЂР°СЃС‚СѓС‚, РЅРѕРІС‹Рµ С‚РµС…РЅРѕР»РѕРіРёРё."},
        {"icon":"рџ“‰","title":"РњРёСЂРѕРІРѕР№ РєСЂРёР·РёСЃ","desc":"РРЅС„Р»СЏС†РёСЏ, Р±РµР·СЂР°Р±РѕС‚РёС†Р°."},
        {"icon":"рџ¦ ","title":"РџРѕСЃР»Рµ РїР°РЅРґРµРјРёРё","desc":"РњРёСЂ РІРѕСЃСЃС‚Р°РЅР°РІР»РёРІР°РµС‚СЃСЏ."},
    ]
    global_state = random.choice(global_states)
    region_news = {
        "south_asia":["рџЊѕ РђРіСЂР°СЂРЅС‹Р№ СЃРµРєС‚РѕСЂ РјРѕРґРµСЂРЅРёР·РёСЂСѓРµС‚СЃСЏ.","рџЏ™ Р“РѕСЂРѕРґР° СЂР°СЃС‚СѓС‚ СЃС‚СЂРµРјРёС‚РµР»СЊРЅРѕ.","вљ–пёЏ Р‘РѕСЂСЊР±Р° СЃ Р±РµРґРЅРѕСЃС‚СЊСЋ.","рџљ‚ РќРѕРІС‹Рµ Р¶РµР»РµР·РЅС‹Рµ РґРѕСЂРѕРіРё."],
        "east_asia":["рџЏ­ РђРІС‚РѕРјР°С‚РёР·Р°С†РёСЏ СЃРѕРєСЂР°С‰Р°РµС‚ СЂР°Р±РѕС‡РёРµ РјРµСЃС‚Р°.","рџљЂ РўРµС…РЅРѕР»РѕРіРёС‡РµСЃРєРёР№ Р±СѓРј.","рџ‘ґ РЎС‚Р°СЂРµРЅРёРµ РЅР°СЃРµР»РµРЅРёСЏ.","рџ“± РњРѕР±РёР»СЊРЅС‹Рµ РїР»Р°С‚РµР¶Рё."],
        "southeast_asia":["рџЏ– РўСѓСЂРёР·Рј РїСЂРёРЅРѕСЃРёС‚ РґРµРЅСЊРіРё.","рџЏ— РЎС‚СЂРѕРёС‚РµР»СЊСЃС‚РІРѕ РёРЅС„СЂР°СЃС‚СЂСѓРєС‚СѓСЂС‹.","рџ’ј РњРЅРѕРіРёРµ СѓРµР·Р¶Р°СЋС‚ Р·Р° РіСЂР°РЅРёС†Сѓ.","рџЊЉ РќР°РІРѕРґРЅРµРЅРёСЏ."],
        "africa":["рџЊЌ РњРѕР»РѕРґРѕРµ РЅР°СЃРµР»РµРЅРёРµ.","рџ’Ћ Р‘РѕРіР°С‚С‹Рµ СЂРµСЃСѓСЂСЃС‹.","вљ”пёЏ Р’ РЅРµРєРѕС‚РѕСЂС‹С… СЂРµРіРёРѕРЅР°С… РЅРµСЃРїРѕРєРѕР№РЅРѕ.","рџ“љ Р Р°СЃС‚С‘С‚ РґРѕСЃС‚СѓРї Рє РѕР±СЂР°Р·РѕРІР°РЅРёСЋ."],
        "arab":["рџ›ў РќРµС„С‚СЊ вЂ” РіР»Р°РІРЅС‹Р№ СЂРµСЃСѓСЂСЃ.","рџЏ™ Р”СѓР±Р°Р№ вЂ” СЃРёРјРІРѕР» Р±РѕРіР°С‚СЃС‚РІР°.","вљ–пёЏ РњРµРЅСЏСЋС‰РёРµСЃСЏ С‚СЂР°РґРёС†РёРё.","рџЊћ РЎРѕР»РЅРµС‡РЅР°СЏ СЌРЅРµСЂРіРµС‚РёРєР°."],
        "latam":["рџ’ѓ Р–РёРІР°СЏ РєСѓР»СЊС‚СѓСЂР°.","вљ пёЏ РџСЂРµСЃС‚СѓРїРЅРѕСЃС‚СЊ РІ РіРѕСЂРѕРґР°С….","рџЊі Р’С‹СЂСѓР±РєР° Р»РµСЃРѕРІ.","рџЋ­ Р¤РµСЃС‚РёРІР°Р»Рё."],
        "europe":["рџ‡Єрџ‡є Р•РґРёРЅСЃС‚РІРѕ Рё СЃС‚Р°Р±РёР»СЊРЅРѕСЃС‚СЊ.","в™»пёЏ Р—РµР»С‘РЅР°СЏ СЌРЅРµСЂРіРµС‚РёРєР°.","рџ‘ґ РЎС‚Р°СЂРµРЅРёРµ Рё РјРёРіСЂР°С†РёСЏ.","рџљ„ РЎРєРѕСЂРѕСЃС‚РЅС‹Рµ РїРѕРµР·РґР°."],
        "post_soviet":["рџЏљ РќР°СЃР»РµРґРёРµ РЎРЎРЎР .","рџ’ј РњРѕР»РѕРґС‘Р¶СЊ РёС‰РµС‚ СЂР°Р±РѕС‚Сѓ.","рџ“є Р’Р»РёСЏРЅРёРµ РіРѕСЃСѓРґР°СЂСЃС‚РІР°.","рџ›Ј РЎС‚СЂРѕРёС‚РµР»СЊСЃС‚РІРѕ РґРѕСЂРѕРі."],
        "developed":["рџ’» РўРµС…РЅРѕР»РѕРіРёРё РјРµРЅСЏСЋС‚ Р¶РёР·РЅСЊ.","рџЏҐ Р”РѕСЃС‚СѓРїРЅР°СЏ РјРµРґРёС†РёРЅР°.","рџЋ“ Р’С‹СЃРѕРєРёР№ СѓСЂРѕРІРµРЅСЊ РѕР±СЂР°Р·РѕРІР°РЅРёСЏ.","рџљ— Р­Р»РµРєС‚СЂРѕРјРѕР±РёР»Рё."],
    }
    positive_news = ["рџЋ‰ РЎРїРѕСЂС‚РёРІРЅС‹Рµ РёРіСЂС‹.","рџЏ† Р’Р°Р¶РЅРѕРµ РѕС‚РєСЂС‹С‚РёРµ.","рџЊѕ РҐРѕСЂРѕС€РёР№ СѓСЂРѕР¶Р°Р№.","рџ›Ј РќРѕРІР°СЏ РјР°РіРёСЃС‚СЂР°Р»СЊ.","рџ“± РўРµС…РЅРѕР»РѕРіРёС‡РµСЃРєРёР№ СЃС‚Р°СЂС‚Р°Рї.","рџЋ¬ РќР°С†РёРѕРЅР°Р»СЊРЅС‹Р№ С„РёР»СЊРј РїРѕР»СѓС‡РёР» РЅР°РіСЂР°РґСѓ."]
    negative_news = ["вљ пёЏ РЎРєР°РЅРґР°Р» РІ РїСЂР°РІРёС‚РµР»СЊСЃС‚РІРµ.","рџЊЉ РќР°РІРѕРґРЅРµРЅРёРµ.","рџ“‰ Р РѕСЃС‚ С†РµРЅ.","рџљ” РћРіСЂР°Р±Р»РµРЅРёСЏ.","рџЏ­ Р—Р°Р±Р°СЃС‚РѕРІРєР°.","рџ”Ґ Р›РµСЃРЅС‹Рµ РїРѕР¶Р°СЂС‹."]
    return {
        "year": year, "global_icon": global_state["icon"], "global_title": global_state["title"], "global_desc": global_state["desc"],
        "region_news": random.choice(region_news.get(country[2], ["РњРёСЂ РјРµРЅСЏРµС‚СЃСЏ."])),
        "extra_news": random.choice(positive_news + negative_news),
    }

def generate_family_background(country, gender, start_cash):
    c_economy = country[7]
    if start_cash < c_economy * 0.5: wealth_class = "poor"
    elif start_cash < c_economy * 1.5: wealth_class = "middle"
    else: wealth_class = "rich"

    if wealth_class == "poor":
        father_occ = random.choice(["СЂР°Р±РѕС‚Р°РµС‚ РЅР° С„Р°Р±СЂРёРєРµ","РіСЂСѓР·С‡РёРє РІ РїРѕСЂС‚Сѓ","РјРµР»РєРёР№ С„РµСЂРјРµСЂ","РєСѓСЂСЊРµСЂ","СЃС‚РѕСЂРѕР¶ РЅР° СЃРєР»Р°РґРµ","СЂР°Р·РЅРѕСЂР°Р±РѕС‡РёР№","С‡РёСЃС‚РёР»СЊС‰РёРє РѕР±СѓРІРё","РїСЂРѕРґР°РІРµС† РЅР° СЂС‹РЅРєРµ"])
        mother_occ = random.choice(["СЂР°Р±РѕС‚Р°РµС‚ СѓР±РѕСЂС‰РёС†РµР№","С€РІРµСЏ РЅР° РґРѕРјСѓ","С‚РѕСЂРіСѓРµС‚ РЅР° СЂС‹РЅРєРµ","РїРѕСЃСѓРґРѕРјРѕР№РєР° РІ РєР°С„Рµ","РґРѕРјРѕС…РѕР·СЏР№РєР°","СЃРѕР±РёСЂР°РµС‚ РїР»Р°СЃС‚РёРє","РїСЂРёСЃР»СѓРіР° РІ Р±РѕРіР°С‚РѕРј РґРѕРјРµ"])
        housing = random.choice(["РєСЂРѕС€РµС‡РЅР°СЏ С…РёР¶РёРЅР°","РєРѕРјРЅР°С‚Р° РІ С‚СЂСѓС‰РѕР±Р°С…","РґРѕРјРёРє РІ РґРµСЂРµРІРЅРµ","РїРѕРґРІР°Р»","РѕР±С‰РµР¶РёС‚РёРµ РґР»СЏ СЂР°Р±РѕС‡РёС…","РєРІР°СЂС‚РёСЂР°-СЃС‚СѓРґРёСЏ"])
        living = "РўРµСЃРЅРѕРµ Р¶РёР»РёС‰Рµ, РІРѕРґР° РёР· РєРѕР»РѕРЅРєРё."
        location = random.choice(["РіР»СѓС…Р°СЏ РґРµСЂРµРІРЅСЏ","С‚СЂСѓС‰РѕР±С‹ Р±РѕР»СЊС€РѕРіРѕ РіРѕСЂРѕРґР°","РѕРєСЂР°РёРЅР° РјРµРіР°РїРѕР»РёСЃР°","СЂР°Р±РѕС‡РёР№ РєРІР°СЂС‚Р°Р»","РїРѕСЃС‘Р»РѕРє Сѓ С„Р°Р±СЂРёРєРё"])
    elif wealth_class == "middle":
        father_occ = random.choice(["РёРЅР¶РµРЅРµСЂ","СѓС‡РёС‚РµР»СЊ","Р±СѓС…РіР°Р»С‚РµСЂ","РІСЂР°С‡ РІ РїРѕР»РёРєР»РёРЅРёРєРµ","РјРµС…Р°РЅРёРє","РјРµРЅРµРґР¶РµСЂ РІ РѕС„РёСЃРµ","С‚РѕСЂРіРѕРІС‹Р№ РїСЂРµРґСЃС‚Р°РІРёС‚РµР»СЊ","РІРѕРґРёС‚РµР»СЊ Р°РІС‚РѕР±СѓСЃР°"])
        mother_occ = random.choice(["СѓС‡РёС‚РµР»СЊРЅРёС†Р°","РјРµРґСЃРµСЃС‚СЂР°","РїСЂРѕРґР°РІРµС† РІ РјР°РіР°Р·РёРЅРµ","РїР°СЂРёРєРјР°С…РµСЂ","РїРѕРІР°СЂ","СЃРµРєСЂРµС‚Р°СЂСЊ","Р±РёР±Р»РёРѕС‚РµРєР°СЂСЊ"])
        housing = random.choice(["РєРІР°СЂС‚РёСЂР° РІ РїР°РЅРµР»СЊРЅРѕРј РґРѕРјРµ","РЅРµР±РѕР»СЊС€РѕР№ РґРѕРј РЅР° РѕРєСЂР°РёРЅРµ","Р¶РёР»СЊС‘ СЃ РёРїРѕС‚РµРєРѕР№","РґРІСѓС…РєРѕРјРЅР°С‚РЅР°СЏ РєРІР°СЂС‚РёСЂР°"])
        living = "РЎРєСЂРѕРјРЅР°СЏ, РЅРѕ РѕРїСЂСЏС‚РЅР°СЏ РєРІР°СЂС‚РёСЂР°."
        location = random.choice(["СЃРїР°Р»СЊРЅС‹Р№ СЂР°Р№РѕРЅ","РїСЂРёРіРѕСЂРѕРґ","СЂР°Р±РѕС‡РёР№ РїСЂРёРіРѕСЂРѕРґ","РЅРµР±РѕР»СЊС€РѕР№ РіРѕСЂРѕРґ"])
    else:
        father_occ = random.choice(["РІР»Р°РґРµР»РµС† С„РёСЂРјС‹","Р°РґРІРѕРєР°С‚","РєСЂСѓРїРЅС‹Р№ Р±РёР·РЅРµСЃРјРµРЅ","РґРµРїСѓС‚Р°С‚ РїР°СЂР»Р°РјРµРЅС‚Р°","С‚РѕРї-РјРµРЅРµРґР¶РµСЂ РєРѕСЂРїРѕСЂР°С†РёРё","РІСЂР°С‡-С…РёСЂСѓСЂРі РІ С‡Р°СЃС‚РЅРѕР№ РєР»РёРЅРёРєРµ"])
        mother_occ = random.choice(["СѓРїСЂР°РІР»СЏРµС‚ СЃРµРјРµР№РЅС‹Рј Р±РёР·РЅРµСЃРѕРј","РґРёР·Р°Р№РЅРµСЂ РёРЅС‚РµСЂСЊРµСЂРѕРІ","РёР·РІРµСЃС‚РЅС‹Р№ РІСЂР°С‡","РїСЂРѕС„РµСЃСЃРѕСЂ СѓРЅРёРІРµСЂСЃРёС‚РµС‚Р°","СЃРІРµС‚СЃРєР°СЏ Р»СЊРІРёС†Р°","Р°РґРІРѕРєР°С‚ РїРѕ Р±РёР·РЅРµСЃСѓ"])
        housing = random.choice(["СЂРѕСЃРєРѕС€РЅС‹Р№ РѕСЃРѕР±РЅСЏРє","РїРµРЅС‚С…Р°СѓСЃ РІ С†РµРЅС‚СЂРµ","РїРѕРјРµСЃС‚СЊРµ Р·Р° РіРѕСЂРѕРґРѕРј","РґРѕРј СЃ Р±Р°СЃСЃРµР№РЅРѕРј Рё СЃР°РґРѕРј"])
        living = "РџСЂРѕСЃС‚РѕСЂРЅС‹Р№ РґРѕРј СЃ РїСЂРёСЃР»СѓРіРѕР№."
        location = random.choice(["РїСЂРµСЃС‚РёР¶РЅС‹Р№ СЂР°Р№РѕРЅ СЃС‚РѕР»РёС†С‹","Р·Р°РєСЂС‹С‚С‹Р№ РєРѕС‚С‚РµРґР¶РЅС‹Р№ РїРѕСЃС‘Р»РѕРє","С†РµРЅС‚СЂ РіРѕСЂРѕРґР°"])

    father_name = random.choice(NAMES[country[2]]["m"])
    mother_name = random.choice(NAMES[country[2]]["f"])
    sib_count = random.choices([0,1,2,3,4], weights=[20,35,25,15,5])[0]
    siblings = []
    for _ in range(sib_count):
        sg = random.choice(["m","f"]); sn = random.choice(NAMES[country[2]][sg])
        if wealth_class == "poor": st = random.choice(["С…РѕРґРёС‚ РІ С€РєРѕР»Сѓ, РїРѕРјРѕРіР°РµС‚ СЂРѕРґРёС‚РµР»СЏРј","СЂР°Р±РѕС‚Р°РµС‚ СЃ 10 Р»РµС‚","РїСЂРёСЃРјР°С‚СЂРёРІР°РµС‚ Р·Р° РјР»Р°РґС€РёРјРё"])
        elif wealth_class == "middle": st = random.choice(["СѓС‡РёС‚СЃСЏ РІ С€РєРѕР»Рµ","С…РѕРґРёС‚ РІ РјСѓР·С‹РєР°Р»СЊРЅСѓСЋ С€РєРѕР»Сѓ","Р·Р°РЅРёРјР°РµС‚СЃСЏ СЃРїРѕСЂС‚РѕРј"])
        else: st = random.choice(["С…РѕРґРёС‚ РІ С‡Р°СЃС‚РЅСѓСЋ С€РєРѕР»Сѓ","Р·Р°РЅРёРјР°РµС‚СЃСЏ СЃ СЂРµРїРµС‚РёС‚РѕСЂР°РјРё","СѓС‡РёС‚СЃСЏ Р·Р° РіСЂР°РЅРёС†РµР№"])
        siblings.append({"name":sn,"gender":sg,"status":st,"age_diff":random.randint(-4,6)})
    grandparents = []
    for side in ["РјР°РјС‹","РїР°РїС‹"]:
        for role in ["РґРµРґСѓС€РєР°","Р±Р°Р±СѓС€РєР°"]:
            grandparents.append({"role":f"{role} РїРѕ Р»РёРЅРёРё {side}","alive":random.random()<0.55})
    return {"wealth_class":wealth_class,"father_name":father_name,"father_occupation":father_occ,"mother_name":mother_name,"mother_occupation":mother_occ,"housing":housing,"living_conditions":living,"siblings":siblings,"siblings_count":sib_count,"grandparents":grandparents,"location":location}

def format_backstory(l):
    family = l.get("family",{}); world = l.get("world_context",{}); c = l["country"]
    eth = l.get("ethnicity"); reg = c[2]
    world_text = (f"рџЊЌ <b>Р“РѕРґ {world['year']}. РњРёСЂ, РІ РєРѕС‚РѕСЂС‹Р№ С‚С‹ РїСЂРёС…РѕРґРёС€СЊ</b>\n\n"
                  f"{world['global_icon']} <b>{world['global_title']}</b>\n<i>{world['global_desc']}</i>\n\n"
                  f"<b>Р’ {c[1]} {c[0]}:</b>\n{world['region_news']}\n{world['extra_news']}\n\n"
                  f"<i>Р­С‚Рѕ РјРёСЂ, РІ РєРѕС‚РѕСЂРѕРј С‚РµР±Рµ РїСЂРµРґСЃС‚РѕРёС‚ Р¶РёС‚СЊ.</i>")
    wealth_emoji = {"poor":"рџҐЂ","middle":"рџЏ ","rich":"рџ‘‘"}
    wealth_ru = {"poor":"Р±РµРґРЅРѕР№","middle":"СЃСЂРµРґРЅРµР№","rich":"Р±РѕРіР°С‚РѕР№"}

    ic_father = get_person_emoji("father", "m", eth, reg)
    ic_mother = get_person_emoji("mother", "f", eth, reg)
    ic_me = get_person_emoji("player", l["gender"], eth, reg, age=0)

    family_text = (f"{wealth_emoji[family['wealth_class']]} <b>РўС‹ СЂРѕРґРёР»СЃСЏ РІ {wealth_ru[family['wealth_class']]} СЃРµРјСЊРµ</b>\n\n"
                   f"{ic_father} <b>РћС‚РµС†:</b> {family['father_name']} вЂ” {family['father_occupation']}\n"
                   f"{ic_mother} <b>РњР°С‚СЊ:</b> {family['mother_name']} вЂ” {family['mother_occupation']}\n\n"
                   f"рџЏЎ <b>Р–РёР»РёС‰Рµ:</b> {family['housing']}\n{family['living_conditions']}\n"
                   f"рџ“Ќ <b>РњРµСЃС‚Рѕ:</b> {family['location']}\n\n"
                   f"{ic_me} <b>РўС‹:</b> {l['name']}, {l['ethnicity'].lower()}")
    sibs = family.get("siblings",[])
    if sibs:
        sib_text = "рџ‘ЁвЂЌрџ‘©вЂЌрџ‘§вЂЌрџ‘¦ <b>Р‘СЂР°С‚СЊСЏ Рё СЃС‘СЃС‚СЂС‹:</b>\n"
        for s in sibs:
            ic = get_person_emoji("sibling", s["gender"], eth, reg)
            ad = s.get("age_diff",0)
            rel = f"СЃС‚Р°СЂС€Рµ РЅР° {ad} Рі." if ad > 0 else f"РјР»Р°РґС€Рµ РЅР° {abs(ad)} Рі." if ad < 0 else "СЂРѕРІРµСЃРЅРёРє"
            sib_text += f"  {ic} <b>{s['name']}</b> ({rel}) вЂ” {s['status']}\n"
    else: sib_text = "рџ‘¶ <b>Р‘СЂР°С‚СЊРµРІ Рё СЃРµСЃС‚С‘СЂ РЅРµС‚</b> вЂ” С‚С‹ РµРґРёРЅСЃС‚РІРµРЅРЅС‹Р№ СЂРµР±С‘РЅРѕРє.\n"
    gp_alive = [g for g in family.get("grandparents",[]) if g["alive"]]
    gp_dead = [g for g in family.get("grandparents",[]) if not g["alive"]]
    gp_text = ""
    if gp_alive:
        gp_text += "\nрџ‘µ <b>Р–РёРІС‹:</b>\n"
        for g in gp_alive:
            g_role = "grandpa" if "РґРµРґСѓС€РєР°" in g["role"] else "grandma"
            ic_gp = get_person_emoji(g_role, "m" if g_role == "grandpa" else "f", eth, reg)
            gp_text += f"  {ic_gp} {g['role']}\n"
    if gp_dead:
        gp_text += "\nрџЄ¦ <b>РЈС€Р»Рё РёР· Р¶РёР·РЅРё:</b>\n"
        for g in gp_dead: gp_text += f"  вќЊ {g['role']}\n"
    relatives_text = sib_text + gp_text + "\n<i>РўРІРѕСЏ СЃРµРјСЊСЏ вЂ” С‡Р°СЃС‚СЊ С‚РІРѕРµР№ РёСЃС‚РѕСЂРёРё.</i>"
    return [world_text, family_text, relatives_text]

# ================= РћРўР›РћР–Р•РќРќР«Р• РџРћРЎР›Р•Р”РЎРўР’РРЇ =================
def add_pending_consequence(l, years_ahead, event_data):
    l.setdefault("pending_consequences",[]).append({"fire_age":l["age"] + years_ahead,"event":event_data})

def get_due_consequence(l):
    due = [c for c in l.get("pending_consequences",[]) if c["fire_age"] <= l["age"]]
    if not due: return None
    consequence = due[0]; l["pending_consequences"].remove(consequence)
    event = dict(consequence["event"]); event["resolved"] = False
    return event

# ================= Р”РћРЎРўРР–Р•РќРРЇ Р РРўРћР“ =================
def check_achievements(l):
    if "achievements" not in l: l["achievements"] = []
    if "ever_in_prison" not in l: l["ever_in_prison"] = False
    new_ones = []
    def has(aid): return aid in l["achievements"]
    def unlock(aid):
        if not has(aid): l["achievements"].append(aid); new_ones.append(ACHIEVEMENTS[aid])
    if l["age"] >= 1: unlock("first_word")
    if any(l["education"].startswith(ed) for ed in ["РќР°С‡Р°Р»СЊРЅРѕРµ","РЎСЂРµРґРЅРµРµ","Р’С‹СЃС€РµРµ"]): unlock("school")
    if any(l["education"].startswith(ed) for ed in ["РЎСЂРµРґРЅРµРµ","Р’С‹СЃС€РµРµ"]): unlock("graduated")
    if l["education"].startswith("Р’С‹СЃС€РµРµ"): unlock("university")
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
    text = f"рџЏ† <b>РљРѕР»Р»РµРєС†РёСЏ СЃСѓРґРµР±</b>\nРћС‚РєСЂС‹С‚Рѕ: {len(earned)}/{total}\n\n"
    for aid, ach in ACHIEVEMENTS.items():
        mark = "вњ…" if aid in earned else "в¬њ"
        text += f"{mark} {ach['name']} вЂ” <i>{ach['desc']}</i>\n"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ Рє Р¶РёР·РЅРё", callback_data="refresh"))
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
    kws = ["Р РѕРґРёР»СЃСЏ","РџРѕС€РµР» РІ С€РєРѕР»Сѓ","РћРєРѕРЅС‡РёР» С€РєРѕР»Сѓ","РџРѕСЃС‚СѓРїРёР» РІ РІСѓР·","Р–РµРЅРёР»СЃСЏ","Р Р°Р·РІРѕРґ","РќР° СЂР°Р±РѕС‚Сѓ","Р’ РїРѕР»РёС†РёРё","Р’ Р°СЂРјРёРё","РљСЂРёРјРёРЅР°Р»","РџРѕРІС‹С€РµРЅРёРµ","РџРѕРЅРёР¶РµРЅРёРµ","РљСѓРїРёР»","РћС‚РєСЂС‹Р»","РЈРјРµСЂ"]
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
        "clean_cash":start_cash,"dirty_cash":0,"in_prison":0,"age":0,"alive":True,"faction":"РќРµС‚",
        "health":100,"happiness":50,"knowledge":50,"relationships":50,
        "education":"РќРµС‚","job":"Р‘РµР·СЂР°Р±РѕС‚РЅС‹Р№","salary":0,"job_type":"none","career_xp":0,"career_rank":1,
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
    heir["name"] = f"{parent_life['name']} II (РќР°СЃР»РµРґРЅРёРє)"
    heir["age"] = 18
    heir["clean_cash"] = int(parent_life["clean_cash"] * 0.5)
    heir["properties"] = [dict(p) for p in parent_life.get("properties", [])]
    heir["businesses"] = [dict(b) for b in parent_life.get("businesses", [])]
    heir["investments"] = [dict(i) for i in parent_life.get("investments", [])]
    heir["political_reputation"] = parent_life.get("political_reputation", 50)
    heir["education"] = "РЎСЂРµРґРЅРµРµ (Р»РёС†РµР№/РєРѕР»Р»РµРґР¶)"
    heir["mode"] = "dynasty"
    heir["life_map"] = ["18 Р»РµС‚: Р’СЃС‚СѓРїРёР» РІ РїСЂР°РІР° РЅР°СЃР»РµРґСЃС‚РІР° РІРµР»РёРєРѕР№ РґРёРЅР°СЃС‚РёРё."]
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
    return effect.get("text", "Р“РѕРґ РїСЂРѕС€РµР».")

def show_peer_lives(l):
    if l["age"] % 5 != 0: return None
    text = "рџ‘Ґ <b>Р РѕРІРµСЃРЅРёРєРё (СЂРѕРґРёР»РёСЃСЊ СЃ С‚РѕР±РѕР№ РІ РѕРґРЅСѓ СЃРµРєСѓРЅРґСѓ):</b>\n\n"
    for i, p in enumerate(l.get("peer_lives",[])):
        if l["age"] >= p["death_age"]: status = "рџ’Ђ СѓРјРµСЂ(Р»Р°)"
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
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ Рє Р¶РёР·РЅРё", callback_data="refresh"))
    if not lb:
        msg = bot.send_message(chat_id, "рџЏ† Р РµР№С‚РёРЅРі РїСѓСЃС‚.", reply_markup=kb, parse_mode="HTML")
        if highlight_user:
            l_ref = players_db.get(str(highlight_user))
            if l_ref: track_message(l_ref, chat_id, msg.message_id)
        return
    text = "рџЏ† <b>РўРѕРї-10 РїСЂРѕР¶РёС‚С‹С… Р¶РёР·РЅРµР№</b>\n\n"
    medals = ["рџҐ‡","рџҐ€","рџҐ‰"]
    for i, e in enumerate(lb[:10]):
        prefix = medals[i] if i < 3 else f"{i+1}."
        mark = " рџ‘€" if highlight_user and e["user_id"] == str(highlight_user) else ""
        text += (f"{prefix} <b>{e['name']}</b> ({e['country']}){mark}\n"
                 f"    в­ђ {e['score']} РѕС‡РєРѕРІ В· {get_age_str(e['age'])} В· {e['wealth']}\n"
                 f"    рџ©є {e['cause']}\n\n")
    text += f"\n<i>Р’СЃРµРіРѕ Р¶РёР·РЅРµР№ РїСЂРѕР¶РёС‚Рѕ: {len(lb)}</i>"
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    if highlight_user:
        l_ref = players_db.get(str(highlight_user))
        if l_ref: track_message(l_ref, chat_id, msg.message_id)

# ================= РџРћР›РРўРРљРђ, Р‘РР—РќР•РЎ-РљР РР—РРЎР« Р РРќР’Р•РЎРўРР¦РР =================
def trigger_politics_event(l):
    if l["age"] >= 30 and l.get("job_type") != "politics" and random.random() < 0.25:
        seen = l.setdefault("seen_regular_events", [])
        if "politics_election" in seen[-5:]:
            return None
        seen.append("politics_election")
        curr_job = l.get("job", "Р‘РµР·СЂР°Р±РѕС‚РЅС‹Р№")
        return {
            "id": "politics_election",
            "title": "рџ—і Р’С‹Р±РѕСЂС‹ РІ РјСѓРЅРёС†РёРїР°Р»СЊРЅС‹Р№ СЃРѕРІРµС‚",
            "text": f"РЈ РІР°СЃ РїРѕСЏРІРёР»Р°СЃСЊ РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊ РІС‹РґРІРёРЅСѓС‚СЊ СЃРІРѕСЋ РєР°РЅРґРёРґР°С‚СѓСЂСѓ РЅР° РІС‹Р±РѕСЂР°С…. РџРµСЂРµС…РѕРґ РІ РїРѕР»РёС‚РёРєСѓ РїРѕС‚СЂРµР±СѓРµС‚ РѕСЃС‚Р°РІРёС‚СЊ С‚РµРєСѓС‰СѓСЋ РґРµСЏС‚РµР»СЊРЅРѕСЃС‚СЊ ({curr_job})!",
            "choices": [
                {"text": "рџ—і Р‘Р°Р»Р»РѕС‚РёСЂРѕРІР°С‚СЊСЃСЏ", "p": 0.45, "success": "politics_win", "fail": "politics_fail"},
                {"text": "рџљ¶ РћС‚РєР°Р·Р°С‚СЊСЃСЏ", "p": 1.0, "success_effect": {"text": "Р’С‹ СЂРµС€РёР»Рё РЅРµ РјРµРЅСЏС‚СЊ РїСЂРѕС„РµСЃСЃРёСЋ Рё РЅРµ Р»РµР·С‚СЊ РІ РїРѕР»РёС‚РёРєСѓ."}}
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
        if is_poor_country or l.get("faction") == "РЈР»РёС‡РЅР°СЏ Р±Р°РЅРґР°":
            crisis_pool.append("racket")
        else:
            crisis_pool.append("market_drop")
            
        crisis_type = random.choice(crisis_pool)
        
        if crisis_type == "tax_audit":
            fine = max(300, int(biz["value"] * random.uniform(0.04, 0.08)))
            l["clean_cash"] -= fine
            return f"рџљЁ <b>РќР°Р»РѕРіРѕРІР°СЏ РёРЅСЃРїРµРєС†РёСЏ</b> РїСЂРѕРІРµР»Р° Р°СѓРґРёС‚ Р±РёР·РЅРµСЃР° В«{biz['type']}В». Р’С‹РїРёСЃР°РЅ С€С‚СЂР°С„ Рё РґРѕРЅР°С‡РёСЃР»РµРЅРёСЏ: {fmt_money(fine, l['country'])}."
        elif crisis_type == "strike":
            loss = max(200, int(biz["value"] * random.uniform(0.03, 0.06)))
            l["clean_cash"] -= loss
            return f"рџ›  <b>Р—Р°Р±Р°СЃС‚РѕРІРєР° РїРµСЂСЃРѕРЅР°Р»Р°</b> РЅР° В«{biz['type']}В» РїР°СЂР°Р»РёР·РѕРІР°Р»Р° СЂР°Р±РѕС‚Сѓ РЅР° РЅРµРґРµР»СЋ. РЈР±С‹С‚РѕРє: {fmt_money(loss, l['country'])}."
        elif crisis_type == "racket":
            extortion = max(500, int(biz["value"] * 0.07))
            l["clean_cash"] -= extortion
            l["happiness"] = max(0, l["happiness"] - 5)
            return f"рџ•¶ <b>РњРµСЃС‚РЅС‹Рµ РєСЂРёРјРёРЅР°Р»СЊРЅС‹Рµ СЃС‚СЂСѓРєС‚СѓСЂС‹</b> РѕР±Р»РѕР¶РёР»Рё В«{biz['type']}В» РґР°РЅСЊСЋ. РџРѕС‚РµСЂРё: {fmt_money(extortion, l['country'])}."
        elif crisis_type == "market_drop":
            biz["value"] = max(500, int(biz["value"] * 0.88))
            return f"рџ“‰ <b>РџР°РґРµРЅРёРµ СЂС‹РЅРѕС‡РЅРѕРіРѕ СЃРїСЂРѕСЃР°:</b> РєР°РїРёС‚Р°Р»РёР·Р°С†РёСЏ РїСЂРµРґРїСЂРёСЏС‚РёСЏ В«{biz['type']}В» СЃРЅРёР·РёР»Р°СЃСЊ РЅР° 12%."
        elif crisis_type == "supply_chain":
            delay_loss = max(250, int(biz["value"] * 0.04))
            l["clean_cash"] -= delay_loss
            return f"рџ“¦ <b>РЎР±РѕР№ РІ Р»РѕРіРёСЃС‚РёС‡РµСЃРєРѕР№ С†РµРїРѕС‡РєРµ</b> СЃС‹СЂСЊСЏ РґР»СЏ В«{biz['type']}В». РќРµСѓСЃС‚РѕР№РєР° РєР»РёРµРЅС‚Р°Рј: {fmt_money(delay_loss, l['country'])}."
    return None

def process_investments(l):
    if not l.get("investments"):
        return ""
    report = "\n\nрџ“€ <b>РћС‚С‡РµС‚ РїРѕ РёРЅРІРµСЃС‚РёС†РёСЏРј:</b>\n"
    for inv in list(l["investments"]):
        asset_name = inv["type"]
        amount = inv["amount"]
        props = INVESTMENT_ASSETS.get(asset_name, {"risk": 0.2, "min_return": 0.9, "max_return": 1.2})
        if random.random() < props["risk"] and random.random() < 0.5:
            multiplier = random.uniform(props["min_return"] * 0.5, 0.9)
            status = "рџ“‰ РїСЂРѕСЃРµР»Рё"
        else:
            multiplier = random.uniform(props["min_return"], props["max_return"])
            status = "рџ“€ РІС‹СЂРѕСЃР»Рё"
        new_amt = max(0, int(amount * multiplier))
        inv["amount"] = new_amt
        report += f"вЂў {asset_name}: {status} (Р±Р°Р»Р°РЅСЃ: {fmt_money(new_amt, l['country'])})\n"
    return report

# ================= get_event =================
def get_event(l):
    age = l["age"]

    pol_evt = trigger_politics_event(l)
    if pol_evt:
        return pol_evt

    if age >= 18 and l["job_type"] == "none" and l["faction"] == "РќРµС‚" and l["in_prison"] == 0:
        return {"id":"path","title":"вљЎ Р’С‹Р±РѕСЂ РїСѓС‚Рё","text":"РџРѕСЂР° РѕРїСЂРµРґРµР»СЏС‚СЊСЃСЏ.",
                "choices":[{"text":"рџ’ј Р“СЂР°Р¶РґР°РЅРєР°","p":1,"success":"job_civ","fail":"none"},
                           {"text":"рџ‘® РџРѕР»РёС†РёСЏ","p":1 if l["education"].startswith("Р’С‹СЃС€РµРµ") else 0,"success":"job_pol","fail":"none"},
                           {"text":"рџЋ– РђСЂРјРёСЏ","p":1 if any(l["education"].startswith(ed) for ed in ["РЎСЂРµРґРЅРµРµ","Р’С‹СЃС€РµРµ"]) else 0,"success":"job_mil","fail":"none"},
                           {"text":"рџ’Љ РљСЂРёРјРёРЅР°Р»","p":1,"success":"job_crim","fail":"none"}]}

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
        return {"id":"prej","title":"РЎС‚РѕР»РєРЅРѕРІРµРЅРёРµ СЃ РїСЂРµРґРІР·СЏС‚РѕСЃС‚СЊСЋ","text":f"{l['prejudice']}",
                "choices":[{"text":"вњЉ Р”РѕРєР°Р·Р°С‚СЊ","p":0.4,"success":"prej_fight_win","fail":"prej_fight_fail"},
                           {"text":"рџ¦Љ РСЃРїРѕР»СЊР·РѕРІР°С‚СЊ","p":0.7,"success":"prej_exploit","fail":"prej_exploit_fail"},
                           {"text":"рџ” РЎРјРёСЂРёС‚СЊСЃСЏ","p":1,"success":"prej_accept","fail":"none"}]}

    if age >= 15 and random.random() < 0.05:
        we = random.choice(WORLD_EVENTS)
        if we.get("min_age",0) <= age:
            return {"id":we["id"],"title":we["title"],"text":we["text"],
                    "choices":[{"text":"РџРµСЂРµР¶РёС‚СЊ","p":1,"success_effect":{**we["effect"],"text":we["text"]}}]}

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
                return {"id":"npc_mother","title":"рџ“ћ Р—РІРѕРЅРѕРє РјР°РјРµ","text":f"РњР°РјР° {nm} Р·РІРѕРЅРёС‚.",
                        "choices":[{"text":"РџРѕРіРѕРІРѕСЂРёС‚СЊ","p":1,"success_effect":{"relationships":6,"happiness":5,"text":"РўС‘РїР»Р°СЏ Р±РµСЃРµРґР°."}},
                                   {"text":"Р‘СЂРѕСЃРёС‚СЊ","p":1,"success_effect":{"relationships":-8,"happiness":-3,"text":"РњР°РјР° СЂР°СЃСЃС‚СЂРѕРёР»Р°СЃСЊ."}}]}
            if role == "friend" and age >= 10:
                return {"id":"npc_friend","title":"рџ¤ќ Р”СЂСѓРі РїСЂРѕСЃРёС‚ РїРѕРјРѕС‰Рё","text":f"Р”СЂСѓРі {nm} РІ Р±РµРґРµ.",
                        "choices":[{"text":"РџРѕРјРѕС‡СЊ","p":0.8,"success_effect":{"relationships":15,"happiness":5,"cash":-200,"text":"РћРЅ С‚РІРѕР№ РґРѕР»Р¶РЅРёРє."},"fail_effect":{"relationships":-5,"cash":-200,"text":"РќРµ РїРѕР»СѓС‡РёР»РѕСЃСЊ."}},
                                   {"text":"РћС‚РєР°Р·Р°С‚СЊ","p":1,"success_effect":{"relationships":-15,"happiness":-5,"text":"РћР±РёРґРµР»СЃСЏ."}}]}
            if role == "rival" and age >= 13:
                return {"id":"npc_rival","title":"вљ”пёЏ РЎРѕРїРµСЂРЅРёРє","text":f"РЎРѕРїРµСЂРЅРёРє {nm} Р±СЂРѕСЃР°РµС‚ РІС‹Р·РѕРІ.",
                        "choices":[{"text":"РџСЂРёРЅСЏС‚СЊ","p":0.5,"success_effect":{"happiness":10,"career_xp":15,"relationships":3,"text":"РџРѕР±РµРґРёР»!"},"fail_effect":{"happiness":-5,"health":-5,"text":"РџСЂРѕРёРіСЂР°Р»."}},
                                   {"text":"РћС‚РєР°Р·Р°С‚СЊСЃСЏ","p":1,"success_effect":{"relationships":-3,"text":"РўСЂСѓСЃ."}}]}
            if role == "father" and age >= 20:
                return {"id":"npc_father","title":"рџ‘ґ РћС‚РµС† Р·РѕРІС‘С‚","text":f"РћС‚РµС† {nm} РЅР° СѓР¶РёРЅ.",
                        "choices":[{"text":"РџРѕР№С‚Рё","p":1,"success_effect":{"relationships":8,"happiness":5,"text":"РћС‚Р»РёС‡РЅС‹Р№ РІРµС‡РµСЂ."}},
                                   {"text":"РћС‚РєР°Р·Р°С‚СЊСЃСЏ","p":1,"success_effect":{"relationships":-5,"text":"РћР±РёРґРµР»СЃСЏ."}}]}

    if age >= 18 and l["job_type"] in ["civilian","police","military","criminal","politics"] and random.random() < 0.30:
        work_pool = [
            {"id":"work_ot","title":"?? ЋўҐав ©¬","text":"ѓ®апйЁ© Їа®ҐЄв ваҐЎгҐв бўҐаега®з­®© а Ў®вл ­  ўбо ­®зм.",
             "choices":[{"text":"‘®Ј« бЁвмбп","p":0.75,"success_effect":{"career_xp":35,"happiness":-4,"health":-3,"text":"Џа®ҐЄв § ўҐаиҐ­ ў®ўаҐ¬п! XP +35."},"fail_effect":{"career_xp":10,"happiness":-8,"health":-5,"text":"“бв «®бвм бЄ § « бм, ­® а Ў®вг б¤ «Ё."}},
                        {"text":"“©вЁ ¤®¬®©","p":1.0,"success_effect":{"career_xp":-10,"happiness":5,"text":"‚лЎа « ®в¤ле. Ґд ­Ґ¤®ў®«Ґ­."}}]},
            {"id":"work_int","title":"?? ЋдЁб­лҐ бЇ«Ґв­Ё","text":"Љ®««ҐЈЁ а бЇгбЄ ов б«геЁ §  ў иҐ© бЇЁ­®© ЇҐаҐ¤ Ї®ўлиҐ­ЁҐ¬.",
             "choices":[{"text":"ђ §®Ўа вмбп Їап¬®","p":0.6,"success_effect":{"career_xp":30,"relationships":5,"text":"Џ®бв ўЁ« Ё­ваЁЈ ­®ў ­  ¬Ґбв®! “ў ¦Ґ­ЁҐ ў Є®««ҐЄвЁўҐ."},"fail_effect":{"career_xp":-15,"happiness":-5,"text":"‘Є ­¤ « ¤®иҐ« ¤® ­ з «мбвў . XP -15."}},
                        {"text":"€Ј­®аЁа®ў вм","p":1.0,"success_effect":{"happiness":2,"text":"ЌҐ ®Ўа вЁ« ў­Ё¬ ­Ёп Ё бд®ЄгбЁа®ў «бп ­  § ¤ з е."}}]},
            {"id":"work_bonus","title":"?? ЏаҐ¬Ё «м­л© д®­¤","text":"ђгЄ®ў®¤бвў® а бЇаҐ¤Ґ«пҐв Ј®¤®ўлҐ Ў®­гбл «гзиЁ¬ б®ваг¤­ЁЄ ¬.",
             "choices":[{"text":"Џ®ваҐЎ®ў вм ЇаҐ¬Ёо","p":0.7,"success_effect":{"cash":int(l['country'][7]*0.5),"career_xp":25,"happiness":10,"text":"„®бвЁ¦Ґ­Ёп ЇаЁ§­ ­л! Џ®«гзҐ­  ЇаҐ¬Ёп Ё гў ¦Ґ­ЁҐ."},"fail_effect":{"happiness":-5,"career_xp":-5,"text":"Ќ з «мбвў® Ї®бзЁв «® ў б б«ЁиЄ®¬ ­ Ј«л¬."}},
                        {"text":"‘Єа®¬­® ¦¤ вм","p":0.9,"success_effect":{"cash":int(l['country'][7]*0.2),"text":"‚лЇЁб «Ё бв ­¤ ав­л© бЄа®¬­л© Ў®­гб."}}]},
            {"id":"work_headhunt","title":"?? ЋддҐа ®в Є®­ЄгаҐ­в®ў","text":"Љ®­ЄгаЁагой п дЁа¬  ЇаҐ¤« Ј Ґв ЇҐаҐ©вЁ Є ­Ё¬ б Ї®ўлиҐ­ЁҐ¬ ®Є« ¤ .",
             "choices":[{"text":"€бЇ®«м§®ў вм ®ддҐа ¤«п в®аЈ ","p":0.65,"success_effect":{"career_xp":30,"happiness":8,"text":"’ҐЄгйҐҐ агЄ®ў®¤бвў® Ї®ўлбЁ«® § аЇ« вг!"},"fail_effect":{"career_xp":-20,"text":"Ґд ў®бЇаЁ­п« нв® Є Є и ­в ¦."}},
                        {"text":"Ћбв вмбп ўҐа­л¬ Є®¬Ї ­ЁЁ","p":1.0,"success_effect":{"career_xp":15,"relationships":8,"text":"ЏаҐ¤ ­­®бвм Є®««ҐЄвЁўг § ¬ҐзҐ­  ­ з «мбвў®¬."}}]},
            {"id":"work_audit","title":"?? Џа®ўҐаЄ  ®взҐв­®бвЁ","text":"‚­Ґ§ Ї­л©  г¤Ёв Їа®ўҐапҐв аҐ§г«мв вл ў иҐ© а Ў®вл §  Єў ав «.",
             "choices":[{"text":"‡ йЁвЁвм Є ¦¤л© Їг­Єв","p":0.8,"success_effect":{"career_xp":30,"knowledge":5,"text":"Ђг¤Ёв®ал ­Ґ ­ и«Ё ­Ё Ґ¤Ё­®© ®иЁЎЄЁ! ђҐЇгв жЁп ЎҐ§гЇаҐз­ ."},"fail_effect":{"career_xp":-15,"happiness":-4,"text":"‚бЇ«л«Ё ¬Ґ«ЄЁҐ ­Ґ¤®зҐвл."}},
                        {"text":"‘ў «Ёвм ­  бв ¦Ґа ","p":0.4,"success_effect":{"career_xp":10,"relationships":-10,"text":"‚лЄагвЁ«бп, ­® Є®««ҐЄвЁў ®бг¦¤ Ґв."},"fail_effect":{"career_xp":-30,"relationships":-15,"happiness":-10,"text":"ЋЎ¬ ­ а бЄалв! ђҐЇгв жЁп Ї®¤®аў ­ ."}}]},
        ]
        return pick_rotating(l, work_pool, max_recent=4)

    if age >= 18 and l["cars"] and random.random() < 0.15:
        if not l.get("has_license"):
            return {"id":"dps1","title":"рџљЁ Р”РџРЎ","text":"РџСЂРѕСЃРёС‚ РїСЂР°РІР°. РЈ С‚РµР±СЏ РЅРµС‚.",
                    "choices":[{"text":"рџ’µ Р’Р·СЏС‚РєР°","p":0.7,"success":"bribe_dps","fail":"dps_jail"},{"text":"рџ¬ Р”РѕРіРѕРІРѕСЂРёС‚СЊСЃСЏ","p":0.2,"success":"dps_warning","fail":"dps_jail"}]}
        elif random.random() < 0.3:
            return {"id":"dps2","title":"рџЌ» РџСЊСЏРЅР°СЏ РµР·РґР°","text":"Р—Р°РїР°С… РїРµСЂРµРіР°СЂР°.",
                    "choices":[{"text":"рџ’µ Р’Р·СЏС‚РєР°","p":0.5,"success":"bribe_dps_big","fail":"drunk_jail"},{"text":"рџљ¶ РћС‚РєР°Р·","p":0.1,"success":"dps_warning","fail":"drunk_jail"},{"text":"рџ­ РЎРјРёСЂРёС‚СЊСЃСЏ","p":1,"success":"drunk_jail","fail":"none"}]}

    if age < 13:
        pool = [e for e in CHILD_EVENTS if e["min_age"] <= age <= e["max_age"]]
        return pick_rotating(l, pool, max_recent=5)
    elif age < 18:
        return pick_rotating(l, TEEN_EVENTS, max_recent=6)
    else:
        return pick_rotating(l, adult_events_for(l), max_recent=8)

# ================= РЎРўРђРўРРЎРўРРљРђ =================
def get_stats_line(l):
    return f"вќ¤пёЏ {l['health']}% | рџЉ {l['happiness']}% | рџ§  {l['knowledge']}% | рџ¤ќ {l['relationships']}%"

def apply_focus(l, focus):
    if focus == "health":
        l["health"] = min(100, l["health"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: РЈРґРµР»РёР» РІСЂРµРјСЏ Р·РґРѕСЂРѕРІСЊСЋ")
    elif focus == "knowledge":
        l["knowledge"] = min(100, l["knowledge"] + random.randint(5,10)); l["happiness"] = max(0, l["happiness"] - random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: РЈС‡РёР»СЃСЏ Рё СЂР°Р·РІРёРІР°Р»СЃСЏ")
    elif focus == "relationships":
        l["relationships"] = min(100, l["relationships"] + random.randint(5,10)); l["happiness"] = min(100, l["happiness"] + random.randint(0,5))
        l["health"] = max(0, l["health"] - random.randint(0,3)); l["knowledge"] = max(0, l["knowledge"] - random.randint(0,3))
        l["life_map"].append(f"{get_age_str(l['age'])}: РЈРґРµР»РёР» РІСЂРµРјСЏ СЃРµРјСЊРµ Рё РґСЂСѓР·СЊСЏРј")
    elif focus == "happiness":
        l["happiness"] = min(100, l["happiness"] + random.randint(10,15)); l["health"] = max(0, l["health"] - random.randint(0,5))
        l["knowledge"] = max(0, l["knowledge"] - random.randint(0,5)); l["relationships"] = max(0, l["relationships"] - random.randint(0,5))
        l["life_map"].append(f"{get_age_str(l['age'])}: РќР°СЃР»Р°Р¶РґР°Р»СЃСЏ Р¶РёР·РЅСЊСЋ")
    elif focus == "work":
        l["happiness"] = max(0, l["happiness"] - random.randint(1,4))
        l["health"] = max(0, l["health"] - random.randint(0,3))
        l["knowledge"] = min(100, l["knowledge"] + random.randint(1,4))
        l["relationships"] = max(0, l["relationships"] - random.randint(0,3))
        # Р¤РѕРєСѓСЃ РЅР° СЂР°Р±РѕС‚Сѓ РґР°С‘С‚ РіР°СЂР°РЅС‚РёСЂРѕРІР°РЅРЅС‹Р№ РєР°СЂСЊРµСЂРЅС‹Р№ РѕРїС‹С‚
        xp_gain = random.randint(25, 45)
        l["career_xp"] = l.get("career_xp", 0) + xp_gain
        l["life_map"].append(f"{get_age_str(l['age'])}: РЈСЃРµСЂРґРЅРѕ СЂР°Р±РѕС‚Р°Р» (+{xp_gain} XP РєР°СЂСЊРµСЂС‹)")

# ================= next_year =================
def next_year(user_id, chat_id):
    uid_str = str(user_id)
    if uid_str not in players_db: return bot.send_message(chat_id, "РќР°С‡РЅРё Р·Р°РЅРѕРІРѕ: /start")
    l = players_db[uid_str]
    if not l["alive"]: return bot.send_message(chat_id, "РўС‹ СѓРјРµСЂ. /start")

    if l["in_prison"] > 0:
        l["in_prison"] -= 1; l["age"] += 1; save_db(players_db)
        if l["in_prison"] == 0:
            l["job"] = "Р‘РµР·СЂР°Р±РѕС‚РЅС‹Р№"; l["salary"] = 0; l["job_type"] = "none"
            return send_scene(chat_id, l, "в›“ <b>РўС‹ РІС‹С€РµР» РЅР° СЃРІРѕР±РѕРґСѓ.</b>", kb_year(), "life")
        return send_scene(chat_id, l, f"в›“ <b>РўСЋСЂСЊРјР°.</b> РћСЃС‚Р°Р»РѕСЃСЊ: {get_age_str(l['in_prison'])}.", kb_year(), "prison")

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

    # РћС‚РјС‹РІР°РЅРёРµ РґРµРЅРµРі РєСЂРёРјРёРЅР°Р»Р° С‡РµСЂРµР· Р±РёР·РЅРµСЃ
    launder_text = ""
    if l.get("job_type") == "criminal" and l.get("dirty_cash", 0) > 0 and l.get("businesses"):
        max_launder = sum(int(b["value"] * 0.4) for b in l["businesses"])
        laundered = min(l["dirty_cash"], max_launder)
        if laundered > 0:
            l["dirty_cash"] -= laundered
            l["clean_cash"] += laundered
            launder_text = f"\nрџ§є РћС‚РјС‹С‚Рѕ С‡РµСЂРµР· СЃРѕР±СЃС‚РІРµРЅРЅС‹Р№ Р±РёР·РЅРµСЃ: {fmt_money(laundered, l['country'])}."

    # Р”РѕС…РѕРґ РєСЂРёРјРёРЅР°Р»Р°
    if l.get("job_type") == "criminal":
        rank = l.get("career_rank", 1)
        crim_income = int(l["country"][7] * (0.4 + 0.25 * rank))
        l["dirty_cash"] += crim_income

    # РџРµРЅСЃРёРѕРЅРЅС‹Р№ РІРѕР·СЂР°СЃС‚ РІ 65 Р»РµС‚
    g_m = l.get("gender") == "m"
    if l["age"] == 65 and l.get("job_type") in ["civilian","police","military","politics"]:
        pension = max(300, int(l["salary"] * 0.6))
        l["job"] = "РџРµРЅСЃРёРѕРЅРµСЂ"
        l["salary"] = pension
        l["job_type"] = "pensioner"
        ret_text = "РІС‹С€РµР» РЅР° РїРµРЅСЃРёСЋ" if g_m else "РІС‹С€Р»Р° РЅР° РїРµРЅСЃРёСЋ"
        add_to_life_map(l, f"рџ‘ґ {ret_text.capitalize()} (РїРµРЅСЃРёСЏ: {fmt_money(pension, l['country'])}).")

    tax = int(l["salary"] * 0.2) if l["job_type"] in ["civilian","police","military","politics"] else 0
    med = sum(DISEASES[d]["cash"] for d in l["diseases"])
    spend_mod = 1.0
    if l["prejudice"] and ("СЃРєСѓРїС‹Рј" in l["prejudice"] or "РїСЂРµРґРїСЂРёРёРјС‡РёРІС‹Рј" in l["prejudice"]): spend_mod = 0.7
    elif l["prejudice"] and ("Р±РµР·Р·Р°Р±РѕС‚РЅС‹Рј" in l["prejudice"] or "РїСЊСЏРЅРёС†РµР№" in l["prejudice"]): spend_mod = 1.3
    living = int(l["country"][7] * 0.2 * spend_mod + (300 * l["children"]))
    l["clean_cash"] += (l["salary"] - tax - med - living)
    if l["clean_cash"] < 0:
        l["debt"] += abs(l["clean_cash"]); l["clean_cash"] = 0

    l["wealth_history"].append(l["clean_cash"])
    if len(l["wealth_history"]) > 80: l["wealth_history"] = l["wealth_history"][-80:]

    if l["job_type"] in ["civilian","police","military","criminal","politics"]:
        l["job_years"] += 1
        # РџРѕРІС‹С€РµРЅРёРµ РїСЂРѕРёСЃС…РѕРґРёС‚ РїСЂРё РЅР°РєРѕРїР»РµРЅРёРё 100 XP (С‚СЂРµР±СѓРµС‚СЃСЏ РѕС‚ 1 РіРѕРґР° СЃС‚Р°Р¶Р°)
        if l["career_xp"] >= 100 and l["job_years"] >= 1:
            l["career_xp"] = 0
            if l["career_rank"] < 5:
                l["career_rank"] += 1
                l["salary"] = int(l["salary"] * 1.35)
                l["job_years"] = 0
                new_title = CAREER_TITLES.get(l["job_type"], {}).get(l["career_rank"], "Р’С‹СЃС€РёР№ С‡РёРЅ")
                add_to_life_map(l, f"рџЋ– РџРѕРІС‹С€РµРЅРёРµ РІ РєР°СЂСЊРµСЂРµ: {new_title}")
                l["happiness"] = min(100, l["happiness"] + 10)
        elif l["career_xp"] <= -50:
            l["career_xp"] = 0
            if l["career_rank"] > 1:
                l["career_rank"] -= 1
                l["salary"] = int(l["salary"] * 0.7)
                l["job_years"] = 0
                new_title = CAREER_TITLES.get(l["job_type"], {}).get(l["career_rank"], "РќРёР·С€РёР№ С‡РёРЅ")
                add_to_life_map(l, f"рџ“‰ РџРѕРЅРёР¶РµРЅРёРµ РІ РґРѕР»Р¶РЅРѕСЃС‚Рё: {new_title}")
                l["happiness"] = max(0, l["happiness"] - 10)

    echo_text = ""
    if l["age"] in [7,18,30,50]:
        n = random.choice(l["neighbors"])
        echo_text = f"\n\nрџ‘Ґ <b>Р­С…Рѕ:</b> РўРІРѕР№ СЂРѕРІРµСЃРЅРёРє <b>{n['name']}</b> ({n['country'][1]}) вЂ” {get_neighbor_echo(n, l['age'])}."
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
            5:{"q":"Р§С‚Рѕ РґР»СЏ С‚РµР±СЏ СЃРµР№С‡Р°СЃ СЃР°РјРѕРµ РІР°Р¶РЅРѕРµ?","opts":["рџ‘ЁвЂЌрџ‘©вЂЌрџ‘§ РЎРµРјСЊСЏ","рџЋ® РРіСЂС‹","рџЊЌ РЈР·РЅР°С‚СЊ РјРёСЂ"]},
            15:{"q":"РљРµРј С‚С‹ С…РѕС‡РµС€СЊ СЃС‚Р°С‚СЊ?","opts":["рџ’ј РЈСЃРїРµС€РЅС‹Рј","вќ¤пёЏ Р›СЋР±РёРјС‹Рј","рџ§  РЈРјРЅС‹Рј"]},
            30:{"q":"Р§С‚Рѕ РґРµР»Р°РµС‚ Р¶РёР·РЅСЊ РѕСЃРјС‹СЃР»РµРЅРЅРѕР№?","opts":["рџ’° Р”РµРЅСЊРіРё","рџ¤ќ РћС‚РЅРѕС€РµРЅРёСЏ","рџЋЇ Р¦РµР»СЊ"]},
            50:{"q":"Рћ С‡С‘Рј С‚С‹ Р¶Р°Р»РµРµС€СЊ?","opts":["вЏ° Рћ РІСЂРµРјРµРЅРё","рџ’” Рћ РЅРµСЃРґРµР»Р°РЅРЅРѕРј","рџ” РќРё Рѕ С‡С‘Рј"]},
            70:{"q":"Р§С‚Рѕ С‚С‹ РѕСЃС‚Р°РІРёС€СЊ РїРѕСЃР»Рµ СЃРµР±СЏ?","opts":["рџ‘ЁвЂЌрџ‘©вЂЌрџ‘§ Р”РµС‚РµР№","рџ“љ Р—РЅР°РЅРёСЏ","рџ’­ Р’РѕСЃРїРѕРјРёРЅР°РЅРёСЏ"]},
        }
        q = questions[l["age"]]
        l["current_event"] = {"id":f"phil_{l['age']}","title":f"рџ¤” Р’РѕРїСЂРѕСЃ РІ {get_age_str(l['age'])}","text":q["q"],
                              "choices":[{"text":opt,"p":1,"success_effect":{"happiness":3,"text":f"РўС‹ РІС‹Р±СЂР°Р»: {opt}."}} for opt in q["opts"]],
                              "is_philosophy":True,"age":l["age"],"resolved":False}
        save_db(players_db)
        return send_scene(chat_id, l, format_event(l, l["current_event"]), kb_event(l["current_event"]["choices"]), "life")

    if l["age"] == 6: return start_exam(user_id, chat_id, 1, "С€РєРѕР»Сѓ")
    elif l["age"] == 12: return start_exam(user_id, chat_id, 2, "РєРѕР»Р»РµРґР¶")
    elif l["age"] == 18: return start_exam(user_id, chat_id, 3, "СѓРЅРёРІРµСЂСЃРёС‚РµС‚")

    evt = get_event(l)
    if evt:
        evt["resolved"] = False
        l["current_event"] = evt
        sc = "life"
        if "РћРІРµСЂС‚Р°Р№Рј" in evt["title"] or "РРЅС‚СЂРёРіРё" in evt["title"]: sc = "office_angry"
        elif "РљСЂРёР·РёСЃ" in evt["title"]: sc = "sad"
        elif "Р‘СЂР°Рє" in evt["title"]: sc = "love"
        elif "Р Р°Р·РІРѕРґ" in evt["title"]: sc = "sad"
        elif "РњРѕС€РµРЅРЅРёРєРё" in evt["title"]: sc = "money_lose"
        elif "Р›РѕС‚РµСЂРµСЏ" in evt["title"]: sc = "money_win"
        elif "Р”РџРЎ" in evt["title"] or "РµР·РґР°" in evt["title"]: sc = "police"
        elif evt["title"].startswith(("рџЌј","рџ‘Ј","рџ§ё Р›СЋР±РёРјР°СЏ")): sc = "toddler"
        send_scene(chat_id, l, format_event(l, evt) + echo_text, kb_event(evt["choices"]), sc)
    else:
        l["current_event"] = None
        send_scene(chat_id, l, format_year(l) + echo_text, kb_focus(l), "life")

    new_ach = check_achievements(l)
    for ach in new_ach:
        msg = bot.send_message(chat_id, f"рџЏ† <b>РќРѕРІРѕРµ РґРѕСЃС‚РёР¶РµРЅРёРµ!</b>\n{ach['name']} вЂ” {ach['desc']}", parse_mode="HTML")
        track_message(l, chat_id, msg.message_id)
    save_db(players_db)

def send_death(user_id, chat_id):
    l = players_db[str(user_id)]; l["alive"] = False; c = l["country"]
    l["current_event"] = None
    causes = []
    if l["age"] < 5: causes = ["РџРµСЂРёРЅР°С‚Р°Р»СЊРЅС‹Рµ РїСЂРёС‡РёРЅС‹","РРЅС„РµРєС†РёРё","РќРµСЃС‡Р°СЃС‚РЅС‹Р№ СЃР»СѓС‡Р°Р№"]
    elif l["age"] < 15: causes = ["РРЅС„РµРєС†РёРё","РќРµСЃС‡Р°СЃС‚РЅС‹Р№ СЃР»СѓС‡Р°Р№","Р’СЂРѕР¶РґС‘РЅРЅС‹Рµ Р°РЅРѕРјР°Р»РёРё"]
    elif l["age"] < 30: causes = ["РќРµСЃС‡Р°СЃС‚РЅС‹Р№ СЃР»СѓС‡Р°Р№","РќР°СЃРёР»РёРµ","Р‘РѕР»РµР·РЅРё"]
    elif l["age"] < 50: causes = ["РЎРµСЂРґРµС‡РЅРѕ-СЃРѕСЃСѓРґРёСЃС‚С‹Рµ","РћРЅРєРѕР»РѕРіРёСЏ","РќРµСЃС‡Р°СЃС‚РЅС‹Р№ СЃР»СѓС‡Р°Р№"]
    elif l["age"] < 70: causes = ["РћРЅРєРѕР»РѕРіРёСЏ","РЎРµСЂРґРµС‡РЅРѕ-СЃРѕСЃСѓРґРёСЃС‚С‹Рµ","Р”РёР°Р±РµС‚"]
    else: causes = ["РЎРµСЂРґРµС‡РЅРѕ-СЃРѕСЃСѓРґРёСЃС‚С‹Рµ","РћРЅРєРѕР»РѕРіРёСЏ","РЎС‚Р°СЂРµРЅРёРµ"]
    if l["diseases"]: cause = f"РћСЃР»РѕР¶РЅРµРЅРёРµ: {l['diseases'][-1]}"
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
    balance_text = (f"рџ“Љ <b>Р‘Р°Р»Р°РЅСЃ Р¶РёР·РЅРё:</b>\n  рџЉ РЎС‡Р°СЃС‚СЊРµ: {balance['happiness']}/100\n"
                    f"  рџЋЇ РЎРјС‹СЃР»: {balance['meaning']}/100\n  рџ¤ќ РЎРІСЏР·Рё: {balance['connections']}/100\n"
                    f"  рџ’° Р”РѕСЃС‚Р°С‚РѕРє: {balance['wealth']}/100\n")
    headlines = get_cinematic_headlines(l)
    headlines_text = "рџ“њ <b>Р›РµС‚РѕРїРёСЃСЊ:</b>\n" + "\n".join([f"вЂў {h}" for h in headlines]) if headlines else ""
    npc_text = "рџ’« <b>РЎСѓРґСЊР±С‹ Р±Р»РёР·РєРёС…:</b>\n" + "\n".join([get_npc_epilogue(n) for n in l.get("key_npcs",[])])
    earned = l.get("achievements", [])
    ach_text = f"рџЏ† <b>Р”РѕСЃС‚РёР¶РµРЅРёСЏ:</b> {len(earned)}/{len(ACHIEVEMENTS)}"
    if final_ach: ach_text += "\n" + "\n".join([f"вЂў {a['name']}" for a in final_ach])
    if l.get("wealth_history"):
        max_w = max(l["wealth_history"]) or 1
        chart = "".join(["в–Ѓ" if w < max_w*0.2 else "в–ѓ" if w < max_w*0.5 else "в–…" if w < max_w*0.8 else "в–€" for w in l["wealth_history"]])
        chart_text = f"\nрџ“€ РљСЂРёРІР°СЏ РґРѕСЃС‚Р°С‚РєР°: {chart}\n"
    else: chart_text = ""
    top_text = "\nрџЏ† <b>РўРѕРї-5 Р¶РёР·РЅРµР№:</b>\n"
    for i, e in enumerate(lb[:5]):
        mark = "рџ‘‰" if e["user_id"] == str(user_id) and e["age"] == l["age"] else "  "
        top_text += f"{mark} {i+1}. <b>{e['name']}</b> ({e['country']}) вЂ” {e['score']} РѕС‡РєРѕРІ, {get_age_str(e['age'])}\n"
    msg = (f"рџ’Ђ <b>РЎРјРµСЂС‚СЊ РІ {get_age_str(l['age'])}.</b>\nрџ©є РџСЂРёС‡РёРЅР°: {cause}\n\n{balance_text}\n"
           f"в­ђ РћС†РµРЅРєР° Р¶РёР·РЅРё: <b>{score} РѕС‡РєРѕРІ</b> В· РјРµСЃС‚Рѕ <b>#{place} РёР· {total}</b>\n\n"
           f"{headlines_text}\n\n{npc_text}\n\n{ach_text}\n{chart_text}")
    kb = InlineKeyboardMarkup()
    for i, p in enumerate(l.get("peer_lives",[])):
        fate = get_neighbor_final({"trajectory":p["trajectory"],"death_age":p["death_age"]})
        msg += f"\nрџ‘Ґ Р РѕРІРµСЃРЅРёРє {p['name']} ({p['country'][1]}): {fate}"
        kb.add(InlineKeyboardButton(f"рџЋ­ РџСЂРѕР¶РёС‚СЊ Р¶РёР·РЅСЊ {p['name']}", callback_data=f"play_peer_{i}"))
    msg += "\n\n" + top_text
    kb.add(InlineKeyboardButton("рџЏ† РўРѕРї Р¶РёР·РЅРµР№", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("рџ“– Р”РѕСЃС‚РёР¶РµРЅРёСЏ", callback_data="achievements"))
    if l.get("children", 0) > 0 or l["clean_cash"] > 5000 or l["properties"] or l["businesses"]:
        kb.add(InlineKeyboardButton(f"рџ‘‘ РџСЂРѕРґРѕР»Р¶РёС‚СЊ РґРёРЅР°СЃС‚РёСЋ (РќР°СЃР»РµРґРЅРёРє)", callback_data="dynasty_continue"))
    kb.add(InlineKeyboardButton("рџЋІ РќР°С‡Р°С‚СЊ Р·Р°РЅРѕРІРѕ", callback_data="new"))
    play_cutscene(chat_id, l, get_cutscene_frames("death"), msg, kb)

def start_exam(user_id, chat_id, level, place):
    l = players_db[str(user_id)]
    available = [t for t in TESTS[level] if t["q"] not in [a["q"] for a in l["asked_tests"][level]]]
    if not available: l["asked_tests"][level] = []; available = TESTS[level]
    test = random.choice(available); l["asked_tests"][level].append(test); l["test_data"] = test
    
    # РџРѕРґР±РёСЂР°РµРј СЃС‚СЂРѕРіРѕ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РµРµ СѓСЂРѕРІРЅСЋ СѓС‡РµР±РЅРѕРµ Р·Р°РІРµРґРµРЅРёРµ
    inst_list = EDU_INSTITUTIONS.get(level, [])
    institution = random.choice(inst_list) if inst_list else f"РЈС‡РµР±РЅРѕРµ Р·Р°РІРµРґРµРЅРёРµ ({place})"
    
    # РЎРѕС…СЂР°РЅСЏРµРј Р·Р°РІРµРґРµРЅРёРµ РІ РїРµСЂСЃРѕРЅР°Р¶Рµ
    l["current_exam_institution"] = institution
    l["current_exam_level"] = level
    
    kb = InlineKeyboardMarkup()
    for i, opt in enumerate(test["opts"]): kb.add(InlineKeyboardButton(opt, callback_data=f"ans_{i}"))
    msg = bot.send_message(chat_id, f"рџ“ќ <b>Р­РєР·Р°РјРµРЅ РїСЂРё РїРѕСЃС‚СѓРїР»РµРЅРёРё: {institution}</b>\nРЈСЂРѕРІРµРЅСЊ: <b>{place}</b>\n\nР’РѕРїСЂРѕСЃ: <b>{test['q']}</b>", reply_markup=kb, parse_mode="HTML")
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
    
    # РњРµС…Р°РЅРёРєР° РІР»РёСЏРЅРёСЏ СЃС‚РµСЂРµРѕС‚РёРїРѕРІ РЅР° СЌРєР·Р°РјРµРЅР°С…
    if not success:
        # Р•СЃР»Рё РёРіСЂРѕРє РѕС€РёР±СЃСЏ, РЅРѕ РѕР±С‰РµСЃС‚РІРѕ СЃС‡РёС‚Р°РµС‚ РµРіРѕ "СѓРјРЅС‹Рј"
        if l.get("prejudice") and "СѓРјРЅС‹Рј" in l["prejudice"]:
            if random.random() < 0.50:  # 50% С€Р°РЅСЃ СЃРЅРёСЃС…РѕР¶РґРµРЅРёСЏ СЌРєР·Р°РјРµРЅР°С‚РѕСЂРѕРІ
                success = True
                saved_by_stereotype = True
        # Р›РёР±Рѕ РµСЃР»Рё Сѓ РїРµСЂСЃРѕРЅР°Р¶Р° СѓР¶Рµ РѕС‡РµРЅСЊ РІС‹СЃРѕРєРёРµ Р·РЅР°РЅРёСЏ (75+)
        elif l.get("knowledge", 50) >= 75 and random.random() < 0.35:
            success = True
            saved_by_knowledge = True
    else:
        # Р•СЃР»Рё РѕС‚РІРµС‚РёР» РїСЂР°РІРёР»СЊРЅРѕ, РЅРѕ РµСЃС‚СЊ РЅРµРіР°С‚РёРІРЅС‹Р№ СЃС‚РµСЂРµРѕС‚РёРї ("РґРёРєР°СЂСЊ" / "С‡СѓР¶РѕР№")
        if l.get("prejudice") and any(bad in l["prejudice"] for bad in ["РґРёРєР°СЂРµРј", "С‡СѓР¶РёРј", "РїРѕРґРѕР·СЂРµРЅРёРµРј"]):
            if random.random() < 0.15:  # 15% СЂРёСЃРє РїСЂРµРґРІР·СЏС‚РѕСЃС‚Рё РєРѕРјРёСЃСЃРёРё
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
                f"рџ§  <b>РЎС‚РµСЂРµРѕС‚РёРї СЃРїР°СЃ СЌРєР·Р°РјРµРЅ{inst_label}!</b>\n"
                f"РўС‹ РІС‹Р±СЂР°Р» РЅРµРїСЂР°РІРёР»СЊРЅС‹Р№ РѕС‚РІРµС‚, РЅРѕ РєРѕРјРёСЃСЃРёСЏ СЃ РґРµС‚СЃС‚РІР° СЃС‡РёС‚Р°РµС‚ РїСЂРµРґСЃС‚Р°РІРёС‚РµР»РµР№ С‚РІРѕРµР№ РЅР°С†РёРѕРЅР°Р»СЊРЅРѕСЃС‚Рё (В«{l.get('ethnicity', '')} вЂ” СЃС‡РёС‚Р°СЋС‚ СѓРјРЅС‹РјВ») РІСѓРЅРґРµСЂРєРёРЅРґР°РјРё. "
                f"Р­РєР·Р°РјРµРЅР°С‚РѕСЂС‹ СЂРµС€РёР»Рё, С‡С‚Рѕ С‚С‹ РѕРіРѕРІРѕСЂРёР»СЃСЏ РёР»Рё РїСЂРёРјРµРЅРёР» РЅРµСЃС‚Р°РЅРґР°СЂС‚РЅСѓСЋ Р»РѕРіРёРєСѓ, Рё РїРѕСЃС‚Р°РІРёР»Рё Р·Р°С‡С‘С‚!\n"
                f"<i>(РџСЂР°РІРёР»СЊРЅС‹Р№ РѕС‚РІРµС‚ Р±С‹Р»: {correct_text})</i>"
            )
            l["happiness"] = min(100, l["happiness"] + 8)
        elif saved_by_knowledge:
            msg = (
                f"рџ“љ <b>Р РµРїСѓС‚Р°С†РёСЏ РѕС‚Р»РёС‡РЅРёРєР°{inst_label}!</b>\n"
                f"РўС‹ РґРѕРїСѓСЃС‚РёР» РѕРїР»РѕС€РЅРѕСЃС‚СЊ, РЅРѕ С‚РІРѕСЏ РІС‹СЃРѕРєР°СЏ СЌСЂСѓРґРёС†РёСЏ (Р·РЅР°РЅРёСЏ {l['knowledge']}%) СѓР±РµРґРёР»Р° РїСЂРµРїРѕРґР°РІР°С‚РµР»РµР№, С‡С‚Рѕ СЌС‚Рѕ СЃР»СѓС‡Р°Р№РЅР°СЏ РѕРїРёСЃРєР° РѕС‚ РІРѕР»РЅРµРЅРёСЏ. "
                f"Р—Р°С‡С‘С‚ РІС‹СЃС‚Р°РІР»РµРЅ!"
            )
            l["happiness"] = min(100, l["happiness"] + 5)
        else:
            msg = f"вњ… <b>Р­РєР·Р°РјРµРЅ СЃРґР°РЅ РЅР° РѕС‚Р»РёС‡РЅРѕ{inst_label}!</b>\nРџСЂР°РІРёР»СЊРЅС‹Р№ РѕС‚РІРµС‚: <b>{correct_text}</b>."

        if l["age"] == 6:
            inst_name = institution or "С€РєРѕР»Р°"
            l["education"] = f"РќР°С‡Р°Р»СЊРЅРѕРµ ({inst_name})"
            l["knowledge"] += 10
            add_to_life_map(l, f"РџРѕСЃС‚СѓРїРёР» РІ {inst_name}" if g_m else f"РџРѕСЃС‚СѓРїРёР»Р° РІ {inst_name}")
        elif l["age"] == 12:
            inst_name = institution or "Р»РёС†РµР№/РєРѕР»Р»РµРґР¶"
            l["education"] = f"РЎСЂРµРґРЅРµРµ ({inst_name})"
            l["knowledge"] += 15
            add_to_life_map(l, f"РџРѕСЃС‚СѓРїРёР» РІ {inst_name}" if g_m else f"РџРѕСЃС‚СѓРїРёР»Р° РІ {inst_name}")
        elif l["age"] == 18:
            inst_name = institution or "СѓРЅРёРІРµСЂСЃРёС‚РµС‚"
            l["education"] = f"Р’С‹СЃС€РµРµ ({inst_name})"
            l["knowledge"] += 25
            add_to_life_map(l, f"РџРѕСЃС‚СѓРїРёР» РІ {inst_name}" if g_m else f"РџРѕСЃС‚СѓРїРёР»Р° РІ {inst_name}")
    else:
        if bias_failed:
            msg = (
                f"вљ пёЏ <b>РџСЂРµРґРІР·СЏС‚РѕСЃС‚СЊ СЌРєР·Р°РјРµРЅР°С‚РѕСЂРѕРІ!</b>\n"
                f"РўС‹ РѕС‚РІРµС‚РёР» Р°Р±СЃРѕР»СЋС‚РЅРѕ РїСЂР°РІРёР»СЊРЅРѕ (<b>{correct_text}</b>), РЅРѕ РёР·-Р·Р° РїСЂРµРґСЂР°СЃСЃСѓРґРєРѕРІ (В«{l.get('prejudice', '')}В») РєРѕРјРёСЃСЃРёСЏ Р·Р°РїРѕРґРѕР·СЂРёР»Р° СЃРїРёСЃС‹РІР°РЅРёРµ, "
                f"Р·Р°РІР°Р»РёР»Р° РєР°РІРµСЂР·РЅС‹РјРё РїСЂРёРґРёСЂРєР°РјРё Рё РѕС‚РєР°Р·Р°Р»Р° РІ Р·Р°С‡С‘С‚Рµ."
            )
            l["happiness"] = max(0, l["happiness"] - 12)
        else:
            msg = f"вќЊ <b>Р­РєР·Р°РјРµРЅ РїСЂРѕРІР°Р»РµРЅ!</b>\nРќРµРІРµСЂРЅС‹Р№ РѕС‚РІРµС‚ (РїСЂР°РІРёР»СЊРЅРѕ Р±С‹Р»Рѕ: <i>{correct_text}</i>). РџРѕСЃС‚СѓРїРёС‚СЊ РЅР° СЌС‚РѕС‚ СѓСЂРѕРІРµРЅСЊ РїРѕРєР° РЅРµ СѓРґР°Р»РѕСЃСЊ."
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
        # РџРµСЂРµС…РѕРґ РЅР° РїРѕР»РЅРѕС†РµРЅРЅСѓСЋ РїРѕР»РёС‚РёС‡РµСЃРєСѓСЋ РґРѕР»Р¶РЅРѕСЃС‚СЊ
        l["job_type"] = "politics"
        l["faction"] = "РџСЂР°РІСЏС‰Р°СЏ РєРѕР°Р»РёС†РёСЏ"
        l["job"] = "РџРѕР»РёС‚РёРє"
        l["career_rank"] = 1
        l["career_xp"] = 20
        l["job_years"] = 0
        l["salary"] = int(vvp * 1.0)
        bonus = int(vvp * 1.2)
        l["clean_cash"] += bonus
        l["happiness"] = min(100, l["happiness"] + 15)
        add_to_life_map(l, "РР·Р±СЂР°РЅ РґРµРїСѓС‚Р°С‚РѕРј СЃРѕРІРµС‚Р° (РЅР°С‡Р°Р»Рѕ РєР°СЂСЊРµСЂС‹ РІ РїРѕР»РёС‚РёРєРµ)")
        return f"рџЏ† РџРѕР±РµРґР° РЅР° РІС‹Р±РѕСЂР°С…! Р’С‹ РѕСЃС‚Р°РІРёР»Рё РїСЂРµР¶РЅСЋСЋ СЃР»СѓР¶Р±Сѓ, РїРѕР»СѓС‡РёР»Рё РґРµРїСѓС‚Р°С‚СЃРєРёР№ РјР°РЅРґР°С‚ Рё РїСЂРµРјРёСЋ {fmt_money(bonus, l['country'])}!"
    if outcome == "politics_fail":
        cost = max(1000, int(vvp * 0.4))
        l["clean_cash"] = max(0, l["clean_cash"] - cost)
        l["political_reputation"] = max(0, l.get("political_reputation", 50) - 8)
        l["happiness"] = max(0, l["happiness"] - 6)
        return "РџРѕСЂР°Р¶РµРЅРёРµ РЅР° РІС‹Р±РѕСЂР°С…. РЎСЂРµРґСЃС‚РІР° РЅР° РєР°РјРїР°РЅРёСЋ РїРѕС‚СЂР°С‡РµРЅС‹, РёР·Р±РёСЂР°С‚РµР»Рё РїСЂРµРґРїРѕС‡Р»Рё РѕРїРїРѕРЅРµРЅС‚Р°."
    if outcome == "politics_fail_free":
        l["happiness"] = max(0, l["happiness"] - 4)
        return "РљР°РјРїР°РЅРёСЏ Р±РµР· Р±СЋРґР¶РµС‚Р° РЅРµ СЃРјРѕРіР»Р° РїСЂРёРІР»РµС‡СЊ РІРЅРёРјР°РЅРёРµ РїСЂРµСЃСЃС‹ Рё РёР·Р±РёСЂР°С‚РµР»РµР№."
    if outcome == "toddler_mama": l["relationships"] += 5; return "РЎРєР°Р·Р°Р» В«РјР°РјР°В»."
    if outcome == "toddler_papa": l["relationships"] += 5; return "РЎРєР°Р·Р°Р» В«РїР°РїР°В»."
    if outcome == "toddler_walk": l["health"] += 5; l["happiness"] += 10; return "РџРµСЂРІС‹Р№ С€Р°Рі!"
    if outcome == "toddler_fall": l["health"] -= 2; return "РЈРїР°Р»."
    if outcome == "toddler_crawl": l["happiness"] += 2; return "РџРѕР»Р·Р°РµС€СЊ."
    if outcome == "toddler_hug": l["happiness"] += 8; return "РњРёС€РєР° СѓСЃРїРѕРєРѕРёР»."
    if outcome == "toddler_break": l["happiness"] -= 5; return "РЎР»РѕРјР°Р» РёРіСЂСѓС€РєСѓ."
    if outcome == "prej_fight_win": l["clean_cash"] += int(vvp*0.5); l["prejudice"] = None; l["happiness"] += 10; return "РЎР»РѕРјР°Р» СЃС‚РµСЂРµРѕС‚РёРї!"
    if outcome == "prej_fight_fail": l["clean_cash"] -= int(vvp*0.2); l["diseases"].append("РџРўРЎР "); l["health"] -= 10; return "РџРѕС‚СЂР°С‚РёР» СЃРёР»С‹."
    if outcome == "prej_exploit":
        if is_bad: l["dirty_cash"] += int(vvp*0.8); l["happiness"] -= 5; return "РСЃРїРѕР»СЊР·РѕРІР°Р» РЅРµРіР°С‚РёРІРЅС‹Р№."
        else: l["clean_cash"] += int(vvp*0.3); l["career_xp"] += 20; l["happiness"] += 5; return "РћСЃРµРґР»Р°Р» РїРѕР·РёС‚РёРІРЅС‹Р№!"
    if outcome == "prej_exploit_fail":
        if is_bad: l["in_prison"] = 3; l["happiness"] -= 20; l["ever_in_prison"] = True; return "РЎРµР»."
        else: l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 10; return "Р’С‹РіРѕСЂРµР»."
    if outcome == "prej_accept": l["clean_cash"] -= int(vvp*0.1); l["happiness"] -= 5; return "РЎРјРёСЂРёР»СЃСЏ."
    if outcome == "marry":
        g_m = l.get("gender") == "m"
        l["married"] = True; l["happiness"] += 20; l["relationships"] += 15; add_to_life_map(l, "Р–РµРЅРёР»СЃСЏ" if g_m else "Р’С‹С€Р»Р° Р·Р°РјСѓР¶")
        if random.random() < 0.6: l["children"] = l.get("children",0) + 1; add_to_life_map(l, "Р РѕРґРёР»СЃСЏ СЂРµР±С‘РЅРѕРє")
        return "РџРѕР¶РµРЅРёР»РёСЃСЊ!"
    if outcome == "divorce":
        l["married"] = False
        if l["clean_cash"] > 0: l["clean_cash"] = int(l["clean_cash"] / 2)
        l["happiness"] -= 15; l["relationships"] -= 20
        add_pending_consequence(l, 5, {"id":"conseq_ex","title":"рџ’” Р’СЃС‚СЂРµС‡Р° СЃ Р±С‹РІС€РёРј","text":"РЎР»СѓС‡Р°Р№РЅР°СЏ РІСЃС‚СЂРµС‡Р°.",
                                       "choices":[{"text":"РџРѕРіРѕРІРѕСЂРёС‚СЊ","p":0.5,"success_effect":{"happiness":5,"relationships":5,"text":"РњРёСЂРЅРѕ."},"fail_effect":{"happiness":-10,"text":"РџРѕСЂСѓРіР°Р»РёСЃСЊ."}},{"text":"РњРёРјРѕ","p":1,"success_effect":{"text":"РџСЂРѕС€С‘Р»."}}]})
        return "Р Р°Р·РІРѕРґ."
    if outcome == "job_civ": l["job_type"] = "civilian"; l["job"] = "Р Р°Р±РѕС‚РЅРёРє"; l["salary"] = int(vvp * 0.6); l["relationships"] += 5; add_to_life_map(l, "РќР° СЂР°Р±РѕС‚Сѓ"); return "РўС‹ РЅР° РіСЂР°Р¶РґР°РЅРєРµ."
    if outcome == "job_pol": l["job_type"] = "police"; l["faction"] = "РџРѕР»РёС†РёСЏ"; l["job"] = "РџРѕР»РёС†РµР№СЃРєРёР№"; l["salary"] = int(vvp * 0.5); l["relationships"] += 10; add_to_life_map(l, "Р’ РїРѕР»РёС†РёРё"); return "РўС‹ РІ РїРѕР»РёС†РёРё."
    if outcome == "job_mil": l["job_type"] = "military"; l["faction"] = "РђСЂРјРёСЏ"; l["job"] = "Р’РѕРµРЅРЅС‹Р№"; l["salary"] = int(vvp * 0.4); l["relationships"] += 15; add_to_life_map(l, "Р’ Р°СЂРјРёРё"); return "РўС‹ РІ Р°СЂРјРёРё."
    if outcome == "job_crim": l["job_type"] = "criminal"; l["faction"] = "РЈР»РёС‡РЅР°СЏ Р±Р°РЅРґР°"; l["job"] = "Р‘Р°РЅРґРёС‚"; l["dirty_cash"] += int(vvp*0.5); l["happiness"] -= 10; add_to_life_map(l, "РљСЂРёРјРёРЅР°Р»"); return "РљСЂРёРјРёРЅР°Р»."
    if outcome == "career_xp_up": l["career_xp"] += 30; l["happiness"] -= 5; return "XP +30."
    if outcome == "career_xp_down": l["career_xp"] -= 20; return "XP -20."
    if outcome == "career_fight_win": l["career_xp"] += 40; l["happiness"] -= 5; return "XP +40."
    if outcome == "career_grind": l["career_xp"] -= 10; return "XP -10."
    if outcome == "work_extra": l["clean_cash"] += int(vvp*0.1); l["career_xp"] += 10; l["health"] -= 5; return "Р’С‚РѕСЂР°СЏ СЂР°Р±РѕС‚Р°."
    if outcome == "family_time": l["career_xp"] -= 10; l["happiness"] += 10; return "Р’СЂРµРјСЏ СЃ СЃРµРјСЊРµР№."
    if outcome == "burnout": l["diseases"].append("РЎРµСЂРґРµС‡РЅР°СЏ РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕСЃС‚СЊ"); l["health"] -= 20; return "Р’С‹РіРѕСЂР°РЅРёРµ."
    if outcome == "scammed":
        loss = int(l["clean_cash"] * 0.5); l["clean_cash"] -= loss; l["happiness"] -= 20
        add_pending_consequence(l, 3, {"id":"conseq_scam","title":"рџљЁ Р’РѕР·РјРµР·РґРёРµ","text":"РњРѕС€РµРЅРЅРёРєР° РїРѕР№РјР°Р»Рё!",
                                       "choices":[{"text":"РџРѕРґР°С‚СЊ РёСЃРє","p":0.7,"success_effect":{"cash":5000,"happiness":10,"text":"Р’РµСЂРЅСѓР»Рё!"},"fail_effect":{"cash":-1000,"text":"РР·РґРµСЂР¶РєРё."}},{"text":"Р—Р°Р±С‹С‚СЊ","p":1,"success_effect":{"text":"РќРµ СЃС‚Р°Р»."}}]})
        return f"РЈРєСЂР°Р»Рё {fmt_money(loss, l['country'])}."
    if outcome == "child_fight": l["happiness"] += 5; return "Р”Р°Р» СЃРґР°С‡Рё."
    if outcome == "child_tell": return "РџРѕР¶Р°Р»РѕРІР°Р»СЃСЏ."
    if outcome == "child_smart": l["books_read"] = l.get("books_read",0) + 1; l["knowledge"] += 10; l["happiness"] += 5; return "РљРЅРёРіР° СЂР°СЃС€РёСЂРёР»Р° РєСЂСѓРіРѕР·РѕСЂ."
    if outcome == "child_walk": l["health"] += 5; l["happiness"] += 5; return "РҐРѕСЂРѕС€Рѕ РїРѕРіСѓР»СЏР»."
    if outcome == "child_sport": l["health"] += 5; l["happiness"] += 8; l["relationships"] += 3; return "РћС‚Р»РёС‡РЅРѕ РїРѕРёРіСЂР°Р»."
    if outcome == "child_injury": l["health"] -= 5; return "РўСЂР°РІРјР°."
    if outcome == "child_bday_big": l["happiness"] += 15; l["relationships"] += 10; return "РћС‚Р»РёС‡РЅС‹Р№ РїСЂР°Р·РґРЅРёРє!"
    if outcome == "child_bday_bad": l["happiness"] -= 8; return "Р”СЂСѓР·СЊСЏ РЅРµ РїСЂРёС€Р»Рё."
    if outcome == "child_bday_small": l["happiness"] += 6; return "РўРёС…Рѕ, РЅРѕ С…РѕСЂРѕС€Рѕ."
    if outcome == "child_circus": l["happiness"] += 10; return "Р’РѕР»С€РµР±СЃС‚РІРѕ!"
    if outcome == "child_swim_good": l["health"] += 4; l["happiness"] += 6; return "РќР°СѓС‡РёР»СЃСЏ РїР»Р°РІР°С‚СЊ."
    if outcome == "child_swim_fear": l["happiness"] -= 4; return "РСЃРїСѓРіР°Р»СЃСЏ."
    if outcome == "child_sick_treat": l["health"] += 6; return "РџРµСЂРµР±РѕР»РµР»."
    if outcome == "child_sick_walk_ok": l["happiness"] += 3; return "РџРѕРіСѓР»СЏР»."
    if outcome == "child_sick_walk_bad": l["health"] -= 8; return "Р‘РѕР»РµР·РЅСЊ СѓСЃРёР»РёР»Р°СЃСЊ."
    if outcome == "child_draw_win": l["happiness"] += 10; l["knowledge"] += 3; return "РџРѕР±РµРґРёР»!"
    if outcome == "child_draw_lose": l["happiness"] += 2; return "РџРѕСѓС‡Р°СЃС‚РІРѕРІР°Р»."
    if outcome == "child_bike_ok": l["health"] += 3; l["happiness"] += 8; return "РџРѕРєР°С‚Р°Р»СЃСЏ."
    if outcome == "child_bike_fall": l["health"] -= 5; return "РЈРїР°Р»."
    if outcome == "child_bike_learn": l["health"] += 2; return "РћСЃРІРѕРёР»."
    if outcome == "child_dog_ok": l["happiness"] += 6; return "РџРѕРіР»Р°РґРёР»."
    if outcome == "child_dog_bite": l["health"] -= 10; l["diseases"].append("РђРЅРµРјРёСЏ"); return "РЈРєСѓСЃРёР»Р°."
    if outcome == "child_dog_run": return "РЈР±РµР¶Р°Р»."
    if outcome == "child_theater_good": l["happiness"] += 10; l["relationships"] += 5; return "РћС‚Р»РёС‡РЅР°СЏ СЂРѕР»СЊ!"
    if outcome == "child_theater_shy": l["happiness"] -= 3; return "РџРѕСЃС‚РµСЃРЅСЏР»СЃСЏ."
    if outcome == "child_theater_tech": l["knowledge"] += 3; return "РџРѕРјРѕРіР°Р» Р·Р° РєСѓР»РёСЃР°РјРё."
    if outcome == "teen_smoke":
        l["diseases"].append("Р Р°Рє Р»РµРіРєРёС…"); l["health"] -= 15
        add_pending_consequence(l, 25, {"id":"conseq_smoke","title":"рџљ¬ Р Р°СЃРїР»Р°С‚Р°","text":"Р“РѕРґС‹ РєСѓСЂРµРЅРёСЏ РґР°Р»Рё Рѕ СЃРµР±Рµ Р·РЅР°С‚СЊ.",
                                        "choices":[{"text":"Р›РµС‡РёС‚СЊСЃСЏ","p":0.6,"success_effect":{"cash":-5000,"health":10,"text":"РћР±РѕС€Р»РѕСЃСЊ."},"fail_effect":{"diseases":["Р Р°Рє Р»РµРіРєРёС…"],"health":-25,"text":"Р Р°Рє Р»С‘РіРєРёС…."}}]})
        return "РљСѓСЂРёР»."
    if outcome == "teen_healthy": l["clean_cash"] += 200; l["health"] += 5; return "РЎСЌРєРѕРЅРѕРјРёР»."
    if outcome == "teen_love": l["happiness"] += 15; l["relationships"] += 10; return "Р’Р·Р°РёРјРЅР°СЏ Р»СЋР±РѕРІСЊ."
    if outcome == "teen_heartbreak": l["diseases"].append("РџРўРЎР "); l["happiness"] -= 15; l["relationships"] -= 10; return "РћС‚РєР°Р·."
    if outcome == "teen_sport_good": l["health"] += 8; l["happiness"] += 5; return "РЎРїРѕСЂС‚ РїРѕС€С‘Р» РЅР° РїРѕР»СЊР·Сѓ."
    if outcome == "teen_sport_hurt": l["health"] -= 6; return "РўСЂР°РІРјР°."
    if outcome == "teen_games_win": l["happiness"] += 8; l["relationships"] += 5; return "РџРѕР±РµРґР°!"
    if outcome == "teen_games_lose": l["happiness"] += 3; return "РџСЂРѕРёРіСЂР°Р», РЅРѕ РІРµСЃРµР»Рѕ."
    if outcome == "teen_study": l["knowledge"] += 6; return "РџРѕР·Р°РЅРёРјР°Р»СЃСЏ."
    if outcome == "teen_fight_win": l["happiness"] += 8; l["relationships"] -= 3; return "Р”Р°Р» СЃРґР°С‡Рё."
    if outcome == "teen_fight_lose": l["health"] -= 8; return "РџРѕР»СѓС‡РёР»."
    if outcome == "teen_tell_teacher": l["relationships"] += 3; return "РЈС‡РёС‚РµР»СЊ РІРјРµС€Р°Р»СЃСЏ."
    if outcome == "teen_band": l["happiness"] += 10; l["relationships"] += 5; return "РРіСЂР° РІ РіСЂСѓРїРїРµ!"
    if outcome == "teen_license_ok": l["has_license"] = True; l["happiness"] += 10; return "РџРѕР»СѓС‡РёР» РїСЂР°РІР°!"
    if outcome == "teen_license_fail": l["happiness"] -= 3; return "РќРµ СЃРґР°Р»."
    if outcome == "lottery_win": l["clean_cash"] += int(vvp * 5); l["happiness"] += 30; return "Р”Р–Р•РљРџРћРў!"
    if outcome == "lottery_lose": l["clean_cash"] -= 100; l["happiness"] -= 5; return "Р‘РёР»РµС‚ РїСѓСЃС‚РѕР№."
    if outcome == "bribe_dps": l["dirty_cash"] -= int(vvp*0.1); return "РџСЂРѕРЅРµСЃР»Рѕ."
    if outcome == "dps_jail": l["in_prison"] = 1; l["happiness"] -= 15; l["ever_in_prison"] = True; return "1 РіРѕРґ С‚СЋСЂСЊРјС‹."
    if outcome == "dps_warning": return "РРЅСЃРїРµРєС‚РѕСЂ РїСЂРµРґСѓРїСЂРµРґРёР»."
    if outcome == "bribe_dps_big": l["dirty_cash"] -= int(vvp*0.3); return "РћС‚РєСѓРїРёР»СЃСЏ."
    if outcome == "drunk_jail": l["in_prison"] = 3; l["cars"] = []; l["happiness"] -= 30; l["ever_in_prison"] = True; return "3 РіРѕРґР° + РєРѕРЅС„РёСЃРєР°С†РёСЏ."
    return "Р“РѕРґ РїСЂРѕС€РµР»."

def resolve_choice(user_id, chat_id, i):
    l = players_db[str(user_id)]
    evt = l.get("current_event")
    if not evt: return
    if evt.get("resolved"): return
    if i < 0 or i >= len(evt["choices"]): return
    c = evt["choices"][i]
    success = random.random() < c["p"]
    
    # РЎС‚РµСЂРµРѕС‚РёРї "СЃС‡РёС‚Р°СЋС‚ СѓРјРЅС‹Рј" РїРѕРјРѕРіР°РµС‚ РІ РєРѕРЅС‚СЂРѕР»СЊРЅС‹С…, СЌРєР·Р°РјРµРЅР°С… Рё РѕР»РёРјРїРёР°РґР°С…
    if not success and l.get("prejudice") and "СѓРјРЅС‹Рј" in l["prejudice"]:
        title_low = evt.get("title", "").lower()
        if any(term in title_low for term in ["СЌРєР·Р°РјРµРЅ", "РѕР»РёРјРїРёР°Рґ", "СѓС‡С‘Р±", "СѓРЅРёРІРµСЂ", "С€РєРѕР»", "РєРѕРЅС‚СЂРѕР»СЊРЅ", "РєСѓСЂСЃ", "РґРёРїР»РѕРј"]):
            if random.random() < 0.45:
                success = True
                if "success_effect" in c:
                    c = dict(c)
                    eff = dict(c["success_effect"])
                    eff["text"] = "рџ§  РЎС‚РµСЂРµРѕС‚РёРї РїРѕРјРѕРі: " + eff.get("text", "")
                    c["success_effect"] = eff
    if "success_effect" in c:
        effect = c.get("success_effect") if success else c.get("fail_effect", {"text":"Р“РѕРґ РїСЂРѕС€РµР»."})
        text = apply_direct_effect(l, effect); outcome = "direct"
    else:
        outcome = c["success"] if success else c.get("fail", "none")
        text = apply_outcome(l, outcome) if outcome else "Р“РѕРґ РїСЂРѕС€РµР»."
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
    parts = [f"<b>Р’РѕР·СЂР°СЃС‚: {get_age_str(l['age'])}</b>\n{visuals}"]
    if l.get("last_result"): parts.append(f"\n{'вњ…' if l['last_result']['success'] else 'вќЊ'} <i>{l['last_result']['text']}</i>")
    parts.append(f"\n{get_stats_line(l)}")
    parts.append(f"\nрџ§¬ РџСЂРѕРёСЃС…РѕР¶РґРµРЅРёРµ: <b>{l['ethnicity']}</b>")
    if l["prejudice"]: parts.append(f"вљ пёЏ <i>РћР±С‰РµСЃС‚РІРѕ: {l['prejudice']}</i>")
    parts.append(f"рџ’° Р‘Р°Р»Р°РЅСЃ: <b>{fmt_money(l['clean_cash'], c)}</b>")
    if l["age"] <= 6: parts.append("рџ‘ЁвЂЌрџ‘©вЂЌрџ‘§ <i>Р–РёРІС‘С€СЊ РЅР° РѕР±РµСЃРїРµС‡РµРЅРёРё СЂРѕРґРёС‚РµР»РµР№</i>")
    elif l["age"] <= 13: parts.append("рџЄ™ <i>РљР°СЂРјР°РЅРЅС‹Рµ РѕС‚ СЂРѕРґРёС‚РµР»РµР№</i>")
    elif l["age"] <= 17: parts.append("рџ’ј <i>РџРѕРґСЂР°Р±РѕС‚РєР° РїРѕСЃР»Рµ СѓС‡С‘Р±С‹</i>")
    if l["dirty_cash"] > 0: parts.append(f"рџ’ј Р“СЂСЏР·РЅС‹Рµ: <b>{fmt_money(l['dirty_cash'], c)}</b>")
    if l["debt"] > 0: parts.append(f"рџЏ¦ Р”РѕР»Рі: <b>{fmt_money(l['debt'], c)}</b>")
    parts.append(f"рџ‘‘ РљР»Р°СЃСЃ: {get_wealth_status(l['clean_cash'], l['dirty_cash'], l)}")
    job = l["job"]
    if l["job_type"] in ["civilian","police","military","criminal","politics"]:
        job += f" ({CAREER_TITLES[l['job_type']].get(l['career_rank'],'')}, XP: {l['career_xp']}/100)"
    parts.append(f"рџ’ј {job}")
    if l["properties"]: parts.append("рџЏ  " + ", ".join([p["type"] for p in l["properties"]]))
    if l["cars"]: parts.append("рџљ— " + ", ".join([c["type"] for c in l["cars"]]))
    if l["businesses"]: parts.append("рџЏў " + ", ".join([b["type"] for b in l["businesses"]]))
    if l.get("investments"): parts.append("рџ“€ РџРѕСЂС‚С„РµР»СЊ: " + ", ".join([f"{i['type']} ({fmt_money(i['amount'], c)})" for i in l["investments"]]))
    if l.get("political_reputation", 50) != 50 or l.get("job_type") == "civilian": parts.append(f"рџЏ› РџРѕР»РёС‚РёС‡РµСЃРєРѕРµ РІР»РёСЏРЅРёРµ: {l.get('political_reputation', 50)}/100")
    if l["diseases"]: parts.append(f"рџ©є {', '.join(l['diseases'])}")
    parts.append(f"рџЋ“ {l['education']}")
    parts.append(f"рџ‘ЁвЂЌрџ‘©вЂЌрџ‘§ Р”РµС‚Рё: {l['children']} | Р‘СЂР°Рє: {'Р”Р°' if l['married'] else 'РќРµС‚'}")
    return "\n".join(parts)

def format_event(l, evt):
    c = l.get("country", ["","","default"])
    visuals = get_scene_visuals("life", l["gender"], ethnicity=l.get("ethnicity"), region=c[2], age=l.get("age"))
    return f"<b>{get_age_str(l['age'])} В· {evt['title']}</b>\n{visuals}\n\n{get_stats_line(l)}\n\n{evt['text']}"

def send_scene(chat_id, l, text, kb, scene_type="life"):
    if not text.startswith("<b>"):
        c = l.get("country", ["","","default"])
        visuals = get_scene_visuals(scene_type, l["gender"], ethnicity=l.get("ethnicity"), region=c[2], age=l.get("age"))
        text = f"{visuals}\n\n{text}"
    msg = bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def kb_intro(): return InlineKeyboardMarkup().add(InlineKeyboardButton("рџЋІ Р РѕРґРёС‚СЊСЃСЏ", callback_data="new"))
def kb_year(): return InlineKeyboardMarkup().add(InlineKeyboardButton("в–¶пёЏ РЎР»РµРґСѓСЋС‰РёР№ РіРѕРґ", callback_data="year")).add(InlineKeyboardButton("рџ›’ РњР°РіР°Р·РёРЅ", callback_data="shop"))

def kb_focus(l=None):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("вќ¤пёЏ Р—РґРѕСЂРѕРІСЊРµ", callback_data="focus_health"), InlineKeyboardButton("рџ§  Р—РЅР°РЅРёСЏ", callback_data="focus_knowledge"))
    kb.add(InlineKeyboardButton("рџ¤ќ РћС‚РЅРѕС€РµРЅРёСЏ", callback_data="focus_relationships"), InlineKeyboardButton("рџЉ РЎС‡Р°СЃС‚СЊРµ", callback_data="focus_happiness"))
    if l and l.get("job_type") in ("civilian","police","military","criminal"):
        kb.add(InlineKeyboardButton("рџ’ј Р Р°Р±РѕС‚Р°", callback_data="focus_work"))
    kb.add(InlineKeyboardButton("рџЏ† РўРѕРї Р¶РёР·РЅРµР№", callback_data="leaderboard"))
    kb.add(InlineKeyboardButton("рџ“– Р”РѕСЃС‚РёР¶РµРЅРёСЏ", callback_data="achievements"))
    kb.add(InlineKeyboardButton("в–¶пёЏ РџСЂРѕРїСѓСЃС‚РёС‚СЊ", callback_data="year"))
    kb.add(InlineKeyboardButton("рџ›’ РњР°РіР°Р·РёРЅ", callback_data="shop"))
    return kb

def kb_event(choices):
    kb = InlineKeyboardMarkup()
    for i, c in enumerate(choices): kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

def open_shop(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("рџЏ  РќРµРґРІРёР¶РёРјРѕСЃС‚СЊ", callback_data="shop_prop")
    ).add(
        InlineKeyboardButton("рџљ— РђРІС‚Рѕ", callback_data="shop_car")
    ).add(
        InlineKeyboardButton("рџЏў Р‘РёР·РЅРµСЃС‹", callback_data="shop_biz")
    ).add(
        InlineKeyboardButton("рџ“€ РРЅРІРµСЃС‚РёС†РёРё", callback_data="shop_invest")
    )
    if l.get("debt", 0) > 0:
        kb.add(InlineKeyboardButton(f"рџ’і РџРѕРіР°СЃРёС‚СЊ РґРѕР»Рі ({fmt_money(l['debt'], c)})", callback_data="shop_pay_debt"))
    kb.add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="year"))
    msg = bot.send_message(chat_id, f"рџ›’ <b>РњР°РіР°Р·РёРЅ</b>\nР‘Р°Р»Р°РЅСЃ: {fmt_money(l['clean_cash'], c)}\nР”РѕР»Рі: {fmt_money(l.get('debt', 0), c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_prop_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items(): kb.add(InlineKeyboardButton(f"вњ… {name} вЂ” {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="shop"))
    msg = bot.send_message(chat_id, f"рџЏ  <b>РќРµРґРІРёР¶РёРјРѕСЃС‚СЊ</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_car_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items(): kb.add(InlineKeyboardButton(f"вњ… {name} вЂ” {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    if not l.get("has_license"):
        lic_price = int(c[7] * 0.05)
        kb.add(InlineKeyboardButton(f"рџЄЄ РљСѓРїРёС‚СЊ РїСЂР°РІР° вЂ” {fmt_money(lic_price, c)}", callback_data="buy_license"))
    kb.add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="shop"))
    msg = bot.send_message(chat_id, f"рџљ— <b>РђРІС‚Рѕ</b>\nРќР°Р»РёС‡РёРµ РїСЂР°РІ: {'Р”Р°' if l.get('has_license') else 'РќРµС‚'}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)


def shop_invest_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, data in INVESTMENT_ASSETS.items():
        kb.add(InlineKeyboardButton(f"рџ“€ {name} вЂ” {fmt_money(data['price'], c)}", callback_data=f"buy_invest_{name}"))
    kb.add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="shop"))
    msg = bot.send_message(chat_id, f"рџ“€ <b>РРЅРІРµСЃС‚РёС†РёРѕРЅРЅС‹Р№ СЂС‹РЅРѕРє</b>\nР’РєР»Р°РґС‹РІР°Р№С‚Рµ СЃСЂРµРґСЃС‚РІР° РІ Р°РєС‚РёРІС‹ РґР»СЏ РµР¶РµРіРѕРґРЅРѕР№ РґРѕС…РѕРґРЅРѕСЃС‚Рё.\nР‘Р°Р»Р°РЅСЃ: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_biz_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items(): kb.add(InlineKeyboardButton(f"рџЏў {name} вЂ” {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("в¬…пёЏ РќР°Р·Р°Рґ", callback_data="shop"))
    msg = bot.send_message(chat_id, f"рџЏў <b>Р‘РёР·РЅРµСЃС‹</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def process_buy(user_id, chat_id, cat, name):
    l = players_db[str(user_id)]; c = l["country"]
    if cat == "debt":
        debt = l.get("debt", 0)
        if debt <= 0:
            return bot.send_message(chat_id, "вњ… РЈ РІР°СЃ РЅРµС‚ РґРѕР»РіРѕРІ!", reply_markup=kb_year())
        if l["clean_cash"] <= 0:
            return bot.send_message(chat_id, "вќЊ РЈ РІР°СЃ РЅРµС‚ СЃРІРѕР±РѕРґРЅС‹С… РґРµРЅРµРі РґР»СЏ РїРѕРіР°С€РµРЅРёСЏ РґРѕР»РіР°!", reply_markup=kb_year())
        pay_amount = min(l["clean_cash"], debt)
        l["clean_cash"] -= pay_amount
        l["debt"] -= pay_amount
        save_db(players_db)
        if l["debt"] == 0:
            add_to_life_map(l, "РџРѕР»РЅРѕСЃС‚СЊСЋ РІС‹РїР»Р°С‚РёР» РґРѕР»РіРё")
            return bot.send_message(chat_id, f"рџЋ‰ <b>Р”РѕР»Рі РїРѕР»РЅРѕСЃС‚СЊСЋ РїРѕРіР°С€РµРЅ!</b>\nР’С‹РїР»Р°С‡РµРЅРѕ: {fmt_money(pay_amount, c)}.", reply_markup=kb_year(), parse_mode="HTML")
        else:
            return bot.send_message(chat_id, f"рџ’і <b>Р§Р°СЃС‚СЊ РґРѕР»РіР° РїРѕРіР°С€РµРЅР°!</b>\nР’С‹РїР»Р°С‡РµРЅРѕ: {fmt_money(pay_amount, c)}.\nРћСЃС‚Р°С‚РѕРє РґРѕР»РіР°: {fmt_money(l['debt'], c)}.", reply_markup=kb_year(), parse_mode="HTML")
    if cat == "license":
        price = int(c[7] * 0.05)
        if l["clean_cash"] < price: return bot.send_message(chat_id, "вќЊ РњР°Р»Рѕ РґРµРЅРµРі РЅР° РїСЂР°РІР°!", reply_markup=kb_year())
        l["clean_cash"] -= price; l["has_license"] = True; save_db(players_db)
        return bot.send_message(chat_id, "рџЋ‰ РўС‹ РїРѕР»СѓС‡РёР» РІРѕРґРёС‚РµР»СЊСЃРєРёРµ РїСЂР°РІР°!", reply_markup=kb_year(), parse_mode="HTML")
    if cat == "prop": base = PROPERTIES[name]
    elif cat == "car": base = CARS[name]
    elif cat == "biz": base = BUSINESSES[name]
    elif cat == "invest": base = INVESTMENT_ASSETS[name]["price"]
    else: base = 0
    if l["clean_cash"] < base: return bot.send_message(chat_id, "вќЊ РњР°Р»Рѕ РґРµРЅРµРі!", reply_markup=kb_year())
    l["clean_cash"] -= base
    if cat == "prop": l["properties"].append({"type":name,"value":base}); add_to_life_map(l, f"РљСѓРїРёР» {name}")
    elif cat == "car": l["cars"].append({"type":name,"value":base}); add_to_life_map(l, f"РљСѓРїРёР» {name}")
    elif cat == "biz": l["businesses"].append({"type":name,"value":base}); add_to_life_map(l, f"РћС‚РєСЂС‹Р» {name}")
    elif cat == "invest":
        existing = next((i for i in l.setdefault("investments", []) if i["type"] == name), None)
        if existing: existing["amount"] += base
        else: l["investments"].append({"type": name, "amount": base})
        add_to_life_map(l, f"РљСѓРїРёР» Р°РєС‚РёРІС‹: {name}")
    save_db(players_db)
    bot.send_message(chat_id, f"рџЋ‰ РљСѓРїР»РµРЅРѕ: <b>{name}</b>!", reply_markup=kb_year(), parse_mode="HTML")

# ================= РћР‘Р РђР‘РћРўР§РРљР =================
