import time
from config import bot, players_db, save_db
from utils import get_stats_line, get_cutscene_frames, play_cutscene, clear_tracked_messages, fmt_money, track_message
from keyboards import (
    kb_intro, kb_focus, kb_year, open_shop, shop_prop_menu, shop_car_menu, shop_biz_menu, shop_invest_menu
)
from mechanics import (
    create_life, create_dynasty_heir, format_backstory, add_to_life_map, format_year,
    next_year, resolve_choice, handle_exam_answer, process_buy, show_leaderboard,
    show_achievements, send_scene, send_death, apply_outcome
)

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    text = "🎲 <b>1 из 8: Эхо</b>\n\nТы — один из 5 детей, родившихся в эту секунду на планете. Сможешь ли ты выжить, построить карьеру и оставить след в истории?"
    bot.send_message(msg.chat.id, text, reply_markup=kb_intro(), parse_mode="HTML")

@bot.message_handler(commands=["top", "leaderboard"])
def cmd_top(msg):
    show_leaderboard(msg.chat.id, highlight_user=msg.from_user.id)

@bot.message_handler(commands=["achievements"])
def cmd_achievements(msg):
    l = players_db.get(str(msg.from_user.id))
    if l: show_achievements(msg.chat.id, l)
    else: bot.send_message(msg.chat.id, "Сначала начни жизнь: /start")

@bot.message_handler(commands=["stats", "profile", "me"])
def cmd_stats(msg):
    l = players_db.get(str(msg.from_user.id))
    if l and l.get("alive"):
        send_scene(msg.chat.id, l, format_year(l), kb_focus(l), "life")
    elif l and not l.get("alive"):
        send_death(msg.from_user.id, msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "Жизнь еще не начата. Нажмите /start, чтобы родиться!")

@bot.message_handler(commands=["help"])
def cmd_help(msg):
    text = (
        "📖 <b>Справка по игре '1 из 8: Эхо'</b>\n\n"
        "🎮 <b>Команды:</b>\n"
        "• /start — Начать новую жизнь\n"
        "• /stats — Посмотреть текущее состояние персонажа\n"
        "• /top — Зал славы и таблица рекордов\n"
        "• /achievements — Список достижений\n\n"
        "💡 <i>Каждый год делайте выбор фокуса (Здоровье, Знания, Отношения, Счастье, Работа) и участвуйте в событиях!</i>"
    )
    bot.send_message(msg.chat.id, text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: True)
def handle(call):
    uid = call.from_user.id
    uid_str = str(uid)
    chat_id = call.message.chat.id
    d = call.data

    try: bot.answer_callback_query(call.id)
    except: pass
    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass

    l_existing = players_db.get(uid_str)
    if l_existing:
        clear_tracked_messages(l_existing)

    try:
        if d == "new":
            l = create_life()
            players_db[uid_str] = l
            g_m = l.get("gender") == "m"
            add_to_life_map(l, "Родился" if g_m else "Родилась")
            save_db(players_db)

            backstory_msgs = format_backstory(l)
            for txt in backstory_msgs:
                time.sleep(0.5)
                m_b = bot.send_message(chat_id, txt, parse_mode="HTML")
                track_message(l, chat_id, m_b.message_id)

            time.sleep(0.5)
            msg = (
                f"👶 <b>Ты родился!</b>\n"
                f"👤 {l['name']} ({l['country'][1]} {l['country'][0]})\n"
                f"🧬 {l['ethnicity']}\n\n"
            )
            if l["prejudice"]:
                msg += f"⚠️ <b>Внимание:</b> {l['prejudice']}\n\n"
            msg += f"{get_stats_line(l)}\n\n<i>Выбери свой первый фокус на год.</i>"
            play_cutscene(chat_id, l, get_cutscene_frames("birth"), msg, kb_focus(l))

        elif d == "refresh":
            l = players_db.get(uid_str)
            if not l: return
            if not l.get("alive"):
                send_death(uid, chat_id)
                return
            send_scene(chat_id, l, format_year(l), kb_focus(l), "life")

        elif d.startswith("focus_"):
            l = players_db.get(uid_str)
            if not l: return
            focus = d.replace("focus_", "")
            if focus == "work" and l.get("job_type") not in ("civilian","police","military","criminal"):
                send_scene(chat_id, l, "❌ У тебя нет работы — сначала найди её.", kb_focus(l), "sad")
                return
            l["focus"] = focus
            save_db(players_db)
            next_year(uid, chat_id)

        elif d == "year":
            l = players_db.get(uid_str)
            if not l: return
            l["focus"] = None
            save_db(players_db)
            next_year(uid, chat_id)

        elif d == "leaderboard":
            show_leaderboard(chat_id, highlight_user=uid)

        elif d == "achievements":
            l = players_db.get(uid_str)
            if l: show_achievements(chat_id, l)

        elif d.startswith("choice_"):
            resolve_choice(uid, chat_id, int(d.split("_")[1]))

        elif d.startswith("ans_"):
            handle_exam_answer(uid, chat_id, int(d.split("_")[1]))

        elif d == "shop":
            open_shop(uid, chat_id)

        elif d == "shop_prop":
            shop_prop_menu(uid, chat_id)

        elif d == "shop_car":
            shop_car_menu(uid, chat_id)

        elif d == "shop_biz":
            shop_biz_menu(uid, chat_id)

        elif d == "shop_invest":
            shop_invest_menu(uid, chat_id)

        elif d.startswith("buy_invest_"):
            process_buy(uid, chat_id, "invest", d.replace("buy_invest_", ""))

        elif d == "dynasty_continue":
            parent = players_db.get(uid_str)
            if not parent: return
            heir = create_dynasty_heir(parent)
            players_db[uid_str] = heir
            save_db(players_db)
            msg = (
                f"👑 <b>Династия продолжается!</b>\n"
                f"Вы теперь <b>{heir['name']}</b>.\n"
                f"Унаследовано капитала: {fmt_money(heir['clean_cash'], heir['country'])}, недвижимость и бизнес семьи.\n\n"
                f"{get_stats_line(heir)}"
            )
            play_cutscene(chat_id, heir, get_cutscene_frames("birth"), msg, kb_focus(heir))

        elif d == "buy_license":
            process_buy(uid, chat_id, "license", "")

        elif d.startswith("buy_prop_"):
            process_buy(uid, chat_id, "prop", d.replace("buy_prop_", ""))

        elif d.startswith("buy_car_"):
            process_buy(uid, chat_id, "car", d.replace("buy_car_", ""))

        elif d.startswith("buy_biz_"):
            process_buy(uid, chat_id, "biz", d.replace("buy_biz_", ""))

        elif d.startswith("play_peer_"):
            idx = int(d.split("_")[2])
            l = players_db.get(uid_str)
            if not l: return
            peers = l.get("peer_lives", [])
            if idx >= len(peers): return
            p = peers[idx]
            new_l = create_life(force_country=p["country"])
            new_l["name"] = p["name"]
            players_db[uid_str] = new_l
            add_to_life_map(new_l, "Родился (судьба ровесника)")
            save_db(players_db)

            backstory_msgs = format_backstory(new_l)
            for txt in backstory_msgs:
                time.sleep(0.5)
                m_b = bot.send_message(chat_id, txt, parse_mode="HTML")
                track_message(new_l, chat_id, m_b.message_id)

            time.sleep(0.5)
            msg = f"🎭 <b>Судьба ровесника!</b>\nТы теперь {new_l['name']} ({new_l['country'][1]}).\n\n{get_stats_line(new_l)}"
            play_cutscene(chat_id, new_l, get_cutscene_frames("birth"), msg, kb_focus(new_l))

        elif d.startswith("play_neighbor_"):
            idx = int(d.split("_")[2])
            l = players_db.get(uid_str)
            if not l: return
            neighbors = l.get("neighbors", [])
            if idx >= len(neighbors): return
            n = neighbors[idx]
            new_l = create_life(force_country=n["country"])
            new_l["name"] = n["name"]
            players_db[uid_str] = new_l
            add_to_life_map(new_l, "Родился (смена судьбы)")
            save_db(players_db)

            backstory_msgs = format_backstory(new_l)
            for txt in backstory_msgs:
                time.sleep(0.5)
                m_b = bot.send_message(chat_id, txt, parse_mode="HTML")
                track_message(new_l, chat_id, m_b.message_id)

            time.sleep(0.5)
            msg = f"🎭 <b>Новая судьба!</b>\nТы теперь {new_l['name']} ({new_l['country'][1]}).\n\n{get_stats_line(new_l)}"
            play_cutscene(chat_id, new_l, get_cutscene_frames("birth"), msg, kb_focus(new_l))

    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка: {e}. Попробуйте нажать еще раз.")
        print(f"Error in handle: {e}")

if __name__ == "__main__":
    print("Бот успешно запущен (модульная архитектура)...")
    bot.infinity_polling()
