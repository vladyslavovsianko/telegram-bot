"""
Синхронизирует client_tag из SQLite в Airtable (таблица Client Requests).
Добавляет только тех клиентов, которых ещё нет в Airtable.
Запускать с папки match: venv/bin/python sync_clients_to_airtable.py
"""
import os
import sqlite3
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
MAIN_DB_PATH     = os.getenv("MAIN_DB_PATH", "/opt/telegram-bot/bot_database.db")
TABLE_NAME       = "Client Requests"

# Исключаем: Test, дублирующий Misha M, дублирующий Vladyslav
EXCLUDE_EMPLOYEE_IDS = (12313213131321, 6776561610, 7948650630)

# 1. Берём все уникальные активные client_tag из SQLite (только нужные работники)
conn = sqlite3.connect(MAIN_DB_PATH)
placeholders = ",".join("?" * len(EXCLUDE_EMPLOYEE_IDS))
rows = conn.execute(
    f"SELECT DISTINCT client_tag FROM clients WHERE is_active = 1 AND employee_id NOT IN ({placeholders}) ORDER BY client_tag",
    EXCLUDE_EMPLOYEE_IDS
).fetchall()
conn.close()

all_tags = [r[0] for r in rows]
print(f"Клиентов в БД: {len(all_tags)}")

# 2. Получаем уже существующие Client ID из Airtable
api   = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, TABLE_NAME)

existing_records = table.all()
existing_ids = {r["fields"].get("Client ID", "") for r in existing_records}
print(f"Уже есть в Airtable: {len(existing_ids)}")

# 3. Добавляем только новых
to_add = [tag for tag in all_tags if tag not in existing_ids]
print(f"Нужно добавить: {len(to_add)}")

for tag in to_add:
    table.create({
        "Client ID": tag,
        "Status": "Active",
    })
    print(f"  ✅ Добавлен: {tag}")

print("Готово!")
