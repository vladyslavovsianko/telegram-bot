#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления имен работников
"""
import sqlite3

DB_FILE = "bot_database.db"

# ID: (отображаемое имя)
WORKERS_UPDATE = {
    610220736: "Misha M",
    5442618444: "Misha K",
    645070075: "Vladyslav",
    625971673: "Vitalij",
    419890021: "Oleh",
}

def update_worker_names():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("📋 Обновление имен работников...")
    
    for user_id, new_name in WORKERS_UPDATE.items():
        cursor.execute("SELECT name FROM workers WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result:
            old_name = result[0]
            cursor.execute("UPDATE workers SET name = ? WHERE user_id = ?", (new_name, user_id))
            print(f"   ✅ {old_name} → {new_name} (ID: {user_id})")
        else:
            print(f"   ❌ Работник {user_id} не найден в базе")
    
    conn.commit()
    
    print("\n📋 Финальный список:")
    cursor.execute("SELECT user_id, name, counter FROM workers")
    for uid, name, counter in cursor.fetchall():
        print(f"   {name} (ID: {uid}) - Счетчик: {counter}")
    
    conn.close()
    print("\n✅ Готово!")

if __name__ == "__main__":
    update_worker_names()
