#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сброса счетчиков анкет и обновления имени
"""
import sqlite3

DB_FILE = "bot_database.db"

def reset_counters():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Показываем текущее состояние
    print("📋 Текущие работники:")
    cursor.execute("SELECT user_id, name, counter FROM workers")
    workers = cursor.fetchall()
    for uid, name, counter in workers:
        print(f"   {name} (ID: {uid}) - Счетчик: {counter}")
    
    print("\n🔄 Сброс счетчиков...")
    
    # Сбрасываем все счетчики на 0
    cursor.execute("UPDATE workers SET counter = 0")
    
    # Меняем Михаил → Владислав
    cursor.execute("UPDATE workers SET name = 'Владислав' WHERE user_id = 645070075")
    
    conn.commit()
    
    print("\n✅ Счетчики сброшены!")
    print("\n📋 Новое состояние:")
    cursor.execute("SELECT user_id, name, counter FROM workers")
    workers = cursor.fetchall()
    for uid, name, counter in workers:
        first_letter = name[0].upper()
        next_id = f"{first_letter}{counter + 1}"
        print(f"   {name} (ID: {uid}) - Счетчик: {counter}, Следующий ID: {next_id}")
    
    conn.close()
    print("\n✅ Готово! Нумерация анкет начнется заново.")

if __name__ == "__main__":
    reset_counters()
