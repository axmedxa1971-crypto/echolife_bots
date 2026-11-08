import os
import json
from pathlib import Path
import telebot

def load_env_file(dotenv_path=".env"):
    try:
        p = Path(dotenv_path)
        if not p.is_file():
            p = Path(__file__).resolve().parent / ".env"
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception as e:
        print(f"Ошибка загрузки .env: {e}")

load_env_file()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Токен бота не найден! Укажите BOT_TOKEN в файле .env или переменных окружения.")

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

DB_FILE = "players.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения базы данных: {e}")
    return {}

def save_db(data):
    try:
        temp_file = DB_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        if os.path.exists(temp_file):
            os.replace(temp_file, DB_FILE)
    except Exception as e:
        print(f"Ошибка сохранения базы данных: {e}")

players_db = load_db()

# Очистка устаревших полей
for _uid, _p in list(players_db.items()):
    if isinstance(_p, dict) and "auto_mode" in _p:
        _p.pop("auto_mode", None)

if "_leaderboard" not in players_db:
    players_db["_leaderboard"] = []
    save_db(players_db)
