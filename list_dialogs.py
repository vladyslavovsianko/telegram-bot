import asyncio, sqlite3
from telethon import TelegramClient

DB_FILE = 'bot_database.db'

def get_setting(key):
    conn = sqlite3.connect(DB_FILE)
    r = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return r[0] if r else None

API_ID   = 33447442
API_HASH = get_setting("API_HASH") or input("Введи API_HASH: ").strip()

async def main():
    client = TelegramClient('bot_chats_session', API_ID, API_HASH)
    await client.start()
    dialogs = await client.get_dialogs(limit=500)
    print(f"{'ID':<22} {'Название'}")
    print("-" * 60)
    for d in dialogs:
        if d.is_group or d.is_channel:
            print(f"{d.id:<22} {d.name}")
    await client.disconnect()

asyncio.run(main())
