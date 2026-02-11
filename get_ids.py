from telethon import TelegramClient
import asyncio

# --- ТВОИ ДАННЫЕ ---
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии (создаст файл get_ids_session.session)
session_name = 'get_ids_session'

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    print("🔄 Подключаюсь к Telegram...")
    # Запускаем клиент
    await client.start()
    
    print("\n📜 СПИСОК ВСЕХ ЧАТОВ И ЛЮДЕЙ:")
    print("=" * 40)
    
    # Проходимся по всем диалогам
    async for dialog in client.iter_dialogs():
        print(f"Название: {dialog.name}")
        print(f"ID: {dialog.id}")
        print("-" * 40)

    print("\n✅ Готово! Скопируй нужные цифры (ID) и вставь в настройки бота.")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())