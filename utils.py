import time
import random
from config import bot
from data.items import PROPERTIES, CARS, BUSINESSES

def get_age_str(age):
    if age % 10 == 1 and age % 100 != 11: return f"{age} год"
    elif age % 10 in (2,3,4) and age % 100 not in (12,13,14): return f"{age} года"
    return f"{age} лет"

def track_message(l, chat_id, msg_id):
    if l is None: return
    l.setdefault("tracked_messages", []).append({"chat_id": chat_id, "id": msg_id})

def clear_tracked_messages(l):
    if not l: return
    for m in l.get("tracked_messages", []):
        try: bot.delete_message(m["chat_id"], m["id"])
        except: pass
    l["tracked_messages"] = []

def fmt_money(amount_usd, country):
    return f"{int(amount_usd * country[8]):,} {country[9]}".replace(",", " ")

def get_wealth_status(clean, dirty, l=None):
    total = clean + dirty
    if l:
        if l.get("properties"): total += sum(p["value"] for p in l["properties"])
        if l.get("cars"): total += sum(c["value"] for c in l["cars"])
        if l.get("businesses"): total += sum(b["value"] for b in l["businesses"])
        if l.get("investments"): total += sum(i["amount"] for i in l["investments"])
        if l.get("debt"): total -= l["debt"]
    if total < 0: return "💸 В долгах"
    if total < 500: return "🥀 Нищий"
    if total < 5000: return "👕 Бедный"
    if total < 20000: return "🔧 Рабочий класс"
    if total < 100000: return "🏠 Средний класс"
    if total < 500000: return "💼 Зажиточный"
    if total < 2000000: return "💎 Богач"
    return "👑 Элита"

def get_stats_line(l):
    return f"❤️ {l['health']}% | 😊 {l['happiness']}% | 🧠 {l['knowledge']}% | 🤝 {l['relationships']}%"

def get_scene_visuals(scene_type, gender):
    male = ["👦","🧑","👨","🧔","👨‍💼","👨‍💻","👨‍🎓"]
    female = ["👧","👩","👩‍🦰","👩‍🦱","👩‍💼","👩‍💻","👩‍🎓"]
    player = random.choice(male) if gender == "m" else random.choice(female)
    scenes = {
        "military": f"🎖 🪖 {player} 🪖 🛡",
        "criminal": f"🕶 🔫 {player} 💰 💣",
        "child": f"🏠 🌳 {player} 🧸 ☀️",
        "toddler": f"🍼 🧸 {player} 🎈 🌟",
        "school": f"🏫 {player} 📚 🎒 🍎",
        "rich": f"🏰 🚗 💰 {player} 🥂 🛥",
        "office": f"🏢 🧑‍💻 {player} 📊 ☕",
        "office_angry": f"🏢 😡 {player} 💢 📉",
        "hospital": f"🏥 🛌 {player} 💉 🩺",
        "prison": f"⛓ 🧱 {player} 🚔 🕶",
        "fight": f"👊 💥 {player} 🥊 🤕",
        "love": f"❤️ {player} 🌹 💑 💐",
        "wedding": f"💍 🤵 👰 {player} 🎉",
        "sad": f"🌧 {player} ☂️ 😔 💧",
        "police": f"🚔 💵 {player} 🚨 😰",
        "money_win": f"💰 🤑 {player} 💎 🎰",
        "money_lose": f"💸 😭 {player} 🕳 📉"
    }
    return scenes.get(scene_type, f"🌆 {player} 🏙 🚶")

def get_cutscene_frames(event_type):
    if event_type == "birth": return ["🏥 👨‍⚕️ 🤰\n<i>Врачи готовятся...</i>","👶 ✨ 👨‍👩‍👦\n<i>Раздается первый крик!</i>","🎉 🍼 🧸\n<i>Новая жизнь началась!</i>"]
    if event_type == "marry": return ["💐 🍷 👩‍❤️‍👨\n<i>Романтический ужин...</i>","🤵 👰 💍\n<i>Предложение руки и сердца!</i>","🥂 🎉 💖\n<i>Свадьба!</i>"]
    if event_type == "prison": return ["🚔 🚨 🏃‍♂️\n<i>Погоня...</i>","👮‍♂️ 🔗 👨\n<i>Задержание...</i>","⛓ 🧱 🚪\n<i>Дверь камеры захлопнулась.</i>"]
    if event_type == "death": return ["🏥 🛌 💔\n<i>Здоровье подводит...</i>","🕯️ ☁️\n<i>Последний вздох...</i>","🪦 🥀 🕊️\n<i>Жизнь окончена.</i>"]
    return []

def play_cutscene(chat_id, l, frames, final_text, kb=None):
    if not frames:
        msg = bot.send_message(chat_id, final_text, reply_markup=kb, parse_mode="HTML")
        track_message(l, chat_id, msg.message_id)
        return
    msg = bot.send_message(chat_id, frames[0], parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)
    for frame in frames[1:]:
        time.sleep(0.5)
        try: bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="HTML")
        except: pass
    time.sleep(0.5)
    try: bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=final_text, reply_markup=kb, parse_mode="HTML")
    except:
        msg_new = bot.send_message(chat_id, final_text, reply_markup=kb, parse_mode="HTML")
        track_message(l, chat_id, msg_new.message_id)
