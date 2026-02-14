#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для изменения имени работника в базе данных
"""
import sqlite3

DB_FILE = "bot_database.db"

def update_worker_name(user_id, new_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Проверяем текущее имя
    cursor.execute("SELECT name, counter FROM workers WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Работник с ID {user_id} не найден в базе!")
        conn.close()
        return
    
    old_name, counter = result
    print(f"📋 Текущее имя: {old_name}")
    print(f"📋 Счетчик: {counter}")
    
    # Обновляем имя
    cursor.execute("UPDATE workers SET name = ? WHERE user_id = ?", (new_name, user_id))
    conn.commit()
    
    print(f"\n✅ Имя изменено: {old_name} → {new_name}")
    
    first_letter = new_name[0].upper()
    next_id = f"{first_letter}{counter + 1}"
    print(f"📌 Следующий ID анкеты будет: {next_id}")
    
    conn.close()

if __name__ == "__main__":
    # ID: 645070075, новое имя: Владислав
    update_worker_name(645070075, "Владислав")
