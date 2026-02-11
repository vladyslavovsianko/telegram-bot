from telethon import TelegramClient
import asyncio

# Данные приложения
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии (совпадает с основным ботом)
session_name = 'manager_session'

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    print("🚀 НАЧИНАЕМ ВХОД...")
    print("Сейчас нужно ввести номер ДРУГОГО аккаунта (не забаненного).")
    
    # Запускаем авторизацию
    await client.start()
    
    # Получаем информацию о том, кто вошел
    me = await client.get_me()
    
    print("\n" + "="*40)
    print(f"✅ УСПЕШНЫЙ ВХОД!")
    print(f"👤 Имя: {me.first_name}")
    print(f"🆔 ТВОЙ НОВЫЙ ID: {me.id}  <-- СКОПИРУЙ ЭТИ ЦИФРЫ!")
    print("="*40 + "\n")
    print("Теперь закрой этот скрипт и вставь ID в файл new.py")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())