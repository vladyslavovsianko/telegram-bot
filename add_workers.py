#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_FILE = "bot_database.db"

WORKERS = [
    (12313213131321, "Test"),
    (610220736, "Михаил"),
    (645070075, "Влад"),
    (625971673, "Виталий"),
    (5442618444, "Миша"),
    (419890021, "Олег"),
]

def add_workers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("📋 Текущие работники в базе:")
    cursor.execute("SELECT user_id, name, counter FROM workers")
    for user_id, name, counter in cursor.fetchall():
        print(f"   {name} (ID: {user_id}) - Счетчик: {counter}")
    
    print("\n➕ Добавляем новых работников...")
    
    for user_id, name in WORKERS:
        cursor.execute("SELECT user_id FROM workers WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            print(f"   ⏭  {name} (ID: {user_id}) - уже есть")
        else:
            cursor.execute("INSERT INTO workers (user_id, name, counter) VALUES (?, ?, ?)", (user_id, name, 0))
            print(f"   ✅ {name} (ID: {user_id}) - добавлен!")
    
    conn.commit()
    
    print("\n📋 Итоговый список:")
    cursor.execute("SELECT user_id, name, counter FROM workers")
    for user_id, name, counter in cursor.fetchall():
        first_letter = name[0].upper() if name else "X"
        next_id = f"{first_letter}{counter + 1}"
        print(f"   {name} - Следующий ID: {next_id}")
    
    conn.close()
    print("\n✅ Готово!")

if __name__ == "__main__":
    add_workers()
