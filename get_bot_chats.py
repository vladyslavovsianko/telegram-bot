#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверяет доступность всех чатов из БД.
Новые чаты можно добавлять прямо через аргументы командной строки.

Использование:
    python3 get_bot_chats.py              # проверить все чаты из БД
    python3 get_bot_chats.py --add        # интерактивно добавить новый клиент в БД
"""
import asyncio
import os
import sqlite3
import argparse
from aiogram import Bot

DB_FILE = 'bot_database.db'

def _get_setting(key, default=""):
    try:
        conn = sqlite3.connect(DB_FILE)
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return os.getenv(key, default)

TOKEN = _get_setting("BOT_TOKEN")


def db_get_all_chat_ids():
    """Возвращает все уникальные group_chat_id из таблицы clients."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT DISTINCT group_chat_id FROM clients WHERE group_chat_id IS NOT NULL"
    ).fetchall()
    # Дополнительно читаем системные чаты из settings
    settings_keys = ('TARGET_CHANNEL_ID', 'VIP_GROUP_ID', 'TARGET_CHAT_ID')
    for key in settings_keys:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if row and row[0]:
            try:
                rows.append((int(row[0]),))
            except ValueError:
                pass
    conn.close()
    ids = {r[0] for r in rows if r[0] and r[0] != 0}
    return ids


def db_add_client(employee_id: int, client_tag: str, group_chat_id: int):
    """Добавляет нового клиента в БД."""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO clients (employee_id, client_tag, group_chat_id, is_active) "
            "VALUES (?, ?, ?, 1)",
            (employee_id, client_tag, group_chat_id)
        )
        conn.commit()
        print(f"✅ Клиент '{client_tag}' (chat_id={group_chat_id}) добавлен сотруднику {employee_id}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        conn.close()


def db_list_workers():
    """Возвращает список (user_id, name) всех работников."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT user_id, name FROM workers ORDER BY name").fetchall()
    conn.close()
    return rows


async def check_chats():
    bot = Bot(token=TOKEN)
    me  = await bot.get_me()

    print("=" * 70)
    print(f"  BOT CHATS CHECK — @{me.username} (ID: {me.id})")
    print("=" * 70)

    all_ids = db_get_all_chat_ids()
    print(f"\nЧатов в БД: {len(all_ids)}\n")

    groups      = []
    supergroups = []
    channels    = []
    errors      = []

    for chat_id in sorted(all_ids):
        try:
            chat  = await bot.get_chat(chat_id)
            title = chat.title or "N/A"
            ctype = chat.type
            try:
                member = await bot.get_chat_member(chat_id, me.id)
                role   = member.status
            except Exception:
                role = "?"
            info = {"id": chat_id, "title": title, "type": ctype, "role": role}
            if ctype == "supergroup":
                supergroups.append(info)
            elif ctype == "group":
                groups.append(info)
            elif ctype == "channel":
                channels.append(info)
        except Exception as e:
            errors.append({"id": chat_id, "error": str(e)})

    if supergroups:
        print(f"SUPERGROUPS ({len(supergroups)})")
        print("-" * 70)
        for c in supergroups:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()

    if groups:
        print(f"GROUPS ({len(groups)}) — нужно конвертировать в supergroup!")
        print("-" * 70)
        for c in groups:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()

    if channels:
        print(f"CHANNELS ({len(channels)})")
        print("-" * 70)
        for c in channels:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()

    if errors:
        print(f"ОШИБКИ ({len(errors)}) — бот не в этих чатах или чат удалён")
        print("-" * 70)
        for c in errors:
            print(f"  {c['id']:<20} {c['error']}")
        print()

    total = len(supergroups) + len(groups) + len(channels)
    print("=" * 70)
    print(f"Доступно: {total}  |  Supergroups: {len(supergroups)}  |  "
          f"Groups: {len(groups)}  |  Channels: {len(channels)}  |  Ошибки: {len(errors)}")

    await bot.session.close()


def interactive_add():
    """Интерактивное добавление нового клиента в БД."""
    workers = db_list_workers()
    if not workers:
        print("❌ Нет сотрудников в БД. Сначала запустите migrate_to_db.py")
        return

    print("\n=== Добавление нового клиента ===\n")
    print("Сотрудники:")
    for i, (uid, name) in enumerate(workers, 1):
        print(f"  {i}. {name} (ID: {uid})")

    try:
        choice = int(input("\nНомер сотрудника: ")) - 1
        emp_id, emp_name = workers[choice]
    except (ValueError, IndexError):
        print("❌ Неверный выбор")
        return

    client_tag    = input("Тег клиента (например #152 или Toy80): ").strip()
    group_chat_id = int(input("ID группового чата (например -5069461222): ").strip())

    db_add_client(emp_id, client_tag, group_chat_id)
    print(f"\nТеперь сотрудник {emp_name} видит клиента '{client_tag}' в боте.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Проверка и управление чатами бота')
    parser.add_argument('--add', action='store_true', help='Добавить нового клиента в БД')
    args = parser.parse_args()

    if args.add:
        interactive_add()
    else:
        asyncio.run(check_chats())
