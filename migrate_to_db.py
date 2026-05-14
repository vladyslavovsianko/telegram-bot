#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт миграции — запустить ОДИН РАЗ на сервере.
Переносит EMPLOYEES_CONFIG и .env в bot_database.db.

Команда:
    python3 migrate_to_db.py
"""
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_FILE = 'bot_database.db'

# ──────────────────────────────────────────────────────────────────────────────
# Все данные из EMPLOYEES_CONFIG (было в bot_full.py)
# ──────────────────────────────────────────────────────────────────────────────
EMPLOYEES_CONFIG = {
    12313213131321: {
        "name": "Test",
        "prefix": "T",
        "clients": {
            "#Test": -5069461222, "#1": -5069461222, "#2": -5069461222,
            "#3": -5069461222, "#4": -5069461222, "#5": -5069461222,
            "#6": -5069461222, "#7": -5069461222, "#8": -5069461222,
            "#9": -5069461222, "#10": -5069461222, "#11": -5069461222,
            "#12": -5069461222, "#13": -5069461222, "#14": -5069461222,
            "#15": -5069461222, "#16": -5069461222, "#17": -5069461222,
            "#18": -5069461222, "#19": -5069461222, "#20": -5069461222,
        }
    },
    610220736: {
        "name": "Михаил",
        "prefix": "MM",
        "clients": {
            "#1": -5182586637, "#2": -5105834721, "#3": -5029226279,
            "#4": -5069461222, "#5": -5069461222, "#6": -5069461222,
            "#7": -5069461222, "#8": -5069461222, "#9": -5069461222,
            "#10": -5069461222, "#11": -5069461222, "#12": -5069461222,
            "#13": -5069461222, "#14": -5069461222, "#15": -5069461222,
            "#16": -5069461222, "#17": -5069461222, "#18": -5069461222,
            "#19": -5069461222, "#20": -5069461222, "#136": -5295466035,
        }
    },
    645070075: {
        "name": "Влад",
        "prefix": "VL",
        "clients": {
            "#96": -5238109092, "#137": -5265690494, "#140": -5102101973,
            "#145": -5101810449, "#148": -5247473724, "Toy17": -4995762095,
            "Toy21": -5291979002, "Toy23": -5142004346, "Toy40": -5229699686,
            "Toy44": -5086915437, "Toy46": -5173644458, "Toy67": -5234402500,
            "#151": -5179525022, "Toy74": -5287917185,
        }
    },
    625971673: {
        "name": "Виталий",
        "prefix": "VIT",
        "clients": {
            "#79": -5148667064, "#85": -5016013600, "#87": -5171048824,
            "#93": -5006054596, "#97": -5148348191, "#99": -5033105513,
            "#107": -5180230828, "#111": -5176219649, "#113": -5212526001,
            "#124": -5121925059, "#131": -5291287861, "#139": -5143478306,
            "#146": -5242427630, "Toy26": -5256884020, "Toy27": -5251521211,
            "Toy31": -5239027986, "Toy34": -5278523032, "Toy38": -5200145003,
            "Toy49": -5267417206, "Toy55": -5117908085, "Toy59": -5298602440,
            "Toy60": -5298774186, "Toy73": -5021649061,
        }
    },
    5442618444: {
        "name": "Миша K",
        "prefix": "MK",
        "clients": {
            "#94": -5217474814, "#98": -4968185056, "#101": -5291170403,
            "#103": -5233036184, "#110": -5157805999, "#117": -5105853553,
            "#118": -5188694886, "#122": -5256550803, "#125": -5156346053,
            "#127": -5113224392, "#142": -5193651565, "#144": -5294989828,
            "#147": -5157970276, "Toy8": -5143325351, "Toy32": -5207210520,
            "Toy41": -5163315891, "Toy49": -5267417206, "Toy56": -5164434247,
            "Toy75": -5267574631, "Toy76": -5115911386,
        }
    },
    419890021: {
        "name": "Олег",
        "prefix": "O",
        "clients": {
            "#58": -5227727762, "#103": -5233036184, "#112": -5162450800,
            "#132": -5155828206, "#143": -5217200978, "Lex1": -5167889257,
            "Lex2": -5257148446, "Lex6": -5112242325, "Lex7": -5279607641,
            "Lex10": -5204094110, "Lex11/#63": -5083040356, "Lex19": -5254977860,
            "Lex28": -5269767297, "Lex33": -5121071814, "Lex35": -5290079522,
            "Lex48": -5259988260, "Lex51": -5102623265, "Lex52": -5189361497,
            "Lex54": -5120960431, "Lex58": -5064673874, "Lex69": -5170442208,
            "Lex72": -5252922911, "Lex80": -5039336421,
        }
    },
    6776561610: {
        "name": "Misha M",
        "prefix": "MM",
        "clients": {
            "#102": -5141670241, "#105": -5280848104, "#106": -5086400568,
            "#121": -5221766017, "#126": -4758469868, "#128": -5250840602,
            "#133": -5125987879, "#134": -5157432882, "#138": -5264463337,
            "#141": -5199206222, "#149": -5290810666, "Toy42": -5299629678,
            "Toy49": -5267417206, "Toy50": -5187555997, "Toy61": -5139479896,
            "Toy63": -5205007325, "Toy64": -5174345325, "Toy68": -5245264756,
            "Toy78": -5101378007, "Toy79": -5143216107,
        }
    },
}

# Настройки из .env
SETTINGS = [
    ("BOT_TOKEN",          os.getenv("BOT_TOKEN", ""),            "Токен бота от @BotFather"),
    ("API_ID",             os.getenv("API_ID", ""),               "Telegram API ID (my.telegram.org)"),
    ("API_HASH",           os.getenv("API_HASH", ""),             "Telegram API Hash"),
    ("MANAGER_IDS",        os.getenv("MANAGER_IDS", ""),          "ID главных менеджеров (через запятую)"),
    ("STATUS_MODERATORS",  os.getenv("STATUS_MODERATORS", ""),    "ID модераторов (через запятую)"),
    ("TARGET_CHANNEL_ID",  os.getenv("TARGET_CHANNEL_ID", ""),    "ID канала-витрины"),
    ("VIP_GROUP_ID",       os.getenv("VIP_GROUP_ID", "0"),        "ID VIP группы"),
    ("TARGET_CHAT_ID",     os.getenv("TARGET_CHAT_ID", "0"),      "ID чата по умолчанию"),
    ("CHANNEL_POST_DELAY", os.getenv("CHANNEL_POST_DELAY", "10"), "Задержка публикации в канал (секунды)"),
    ("OPENAI_API_KEY",     os.getenv("OPENAI_API_KEY", ""),       "OpenAI API ключ"),
    ("ADMIN_PASSWORD",     os.getenv("ADMIN_PASSWORD", "admin123"), "Пароль веб-панели (admin_panel.py)"),
]


def run():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    print("=" * 60)
    print("  МИГРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)

    # ── 1. Создать таблицу clients ────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id   INTEGER NOT NULL,
            client_tag    TEXT    NOT NULL,
            group_chat_id INTEGER,
            is_active     INTEGER DEFAULT 1,
            UNIQUE(employee_id, client_tag)
        )
    ''')
    print("\n✅ Таблица clients — готова")

    # ── 2. Создать таблицу settings ──────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key         TEXT PRIMARY KEY,
            value       TEXT,
            description TEXT
        )
    ''')
    print("✅ Таблица settings — готова")

    # ── 3. Добавить колонку prefix в workers (если нет) ───────────
    try:
        c.execute("ALTER TABLE workers ADD COLUMN prefix TEXT")
        print("✅ Колонка prefix добавлена в workers")
    except Exception:
        print("ℹ️  Колонка prefix уже существует")

    conn.commit()

    # ── 4. Заполнить workers + clients ───────────────────────────
    clients_added = 0
    clients_skipped = 0

    for emp_id, data in EMPLOYEES_CONFIG.items():
        name   = data["name"]
        prefix = data["prefix"]

        # Обновляем workers (INSERT OR IGNORE — не затрагивает счётчик)
        c.execute(
            "INSERT OR IGNORE INTO workers (user_id, name, counter, prefix) VALUES (?, ?, 0, ?)",
            (emp_id, name, prefix)
        )
        c.execute(
            "UPDATE workers SET prefix = ? WHERE user_id = ?",
            (prefix, emp_id)
        )

        # Добавляем клиентов
        for tag, gid in data["clients"].items():
            c.execute(
                "INSERT OR IGNORE INTO clients (employee_id, client_tag, group_chat_id) VALUES (?, ?, ?)",
                (emp_id, tag, gid)
            )
            if c.rowcount:
                clients_added += 1
            else:
                clients_skipped += 1

    print(f"\n✅ Клиенты: добавлено {clients_added}, уже было {clients_skipped}")

    # ── 5. Заполнить settings ────────────────────────────────────
    for key, value, desc in SETTINGS:
        c.execute(
            "INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)",
            (key, value, desc)
        )
    print(f"✅ Настройки: записано {len(SETTINGS)} параметров")

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("  ГОТОВО! Миграция завершена.")
    print("=" * 60)
    print("\nСледующий шаг:")
    print("  python3 admin_panel.py   →  открыть http://46.225.119.58:5001/admin")


if __name__ == "__main__":
    run()
