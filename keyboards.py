from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import bot, players_db
from utils import fmt_money, track_message
from data.items import PROPERTIES, CARS, BUSINESSES, INVESTMENT_ASSETS

def kb_intro():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("🎲 Родиться", callback_data="new"))

def kb_year():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("▶️ Следующий год", callback_data="year")
    ).add(
        InlineKeyboardButton("🛒 Магазин", callback_data="shop")
    )

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
    for i, c in enumerate(choices):
        kb.add(InlineKeyboardButton(c['text'], callback_data=f"choice_{i}"))
    return kb

def open_shop(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🏠 Недвижимость", callback_data="shop_prop")
    ).add(
        InlineKeyboardButton("🚗 Авто", callback_data="shop_car")
    ).add(
        InlineKeyboardButton("🏢 Бизнесы", callback_data="shop_biz")
    ).add(
        InlineKeyboardButton("📈 Инвестиции", callback_data="shop_invest")
    ).add(
        InlineKeyboardButton("⬅️ Назад", callback_data="year")
    )
    msg = bot.send_message(chat_id, f"🛒 <b>Магазин</b>\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_prop_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in PROPERTIES.items():
        kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_prop_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🏠 <b>Недвижимость</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_car_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in CARS.items():
        kb.add(InlineKeyboardButton(f"✅ {name} — {fmt_money(price, c)}", callback_data=f"buy_car_{name}"))
    if not l.get("has_license"):
        lic_price = int(c[7] * 0.05)
        kb.add(InlineKeyboardButton(f"🪪 Купить права — {fmt_money(lic_price, c)}", callback_data="buy_license"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🚗 <b>Авто</b>\nНаличие прав: {'Да' if l.get('has_license') else 'Нет'}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_biz_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, price in BUSINESSES.items():
        kb.add(InlineKeyboardButton(f"🏢 {name} — {fmt_money(price, c)}", callback_data=f"buy_biz_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"🏢 <b>Бизнесы</b>", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)

def shop_invest_menu(user_id, chat_id):
    l = players_db[str(user_id)]; c = l["country"]
    kb = InlineKeyboardMarkup()
    for name, data in INVESTMENT_ASSETS.items():
        kb.add(InlineKeyboardButton(f"📈 {name} — {fmt_money(data['price'], c)}", callback_data=f"buy_invest_{name}"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="shop"))
    msg = bot.send_message(chat_id, f"📈 <b>Инвестиционный рынок</b>\nВкладывайте средства в активы для ежегодной доходности.\nБаланс: {fmt_money(l['clean_cash'], c)}", reply_markup=kb, parse_mode="HTML")
    track_message(l, chat_id, msg.message_id)
