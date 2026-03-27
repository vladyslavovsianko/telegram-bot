from telethon import TelegramClient
import asyncio

# --- ТВОИ ДАННЫЕ ---
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии (создаст файл get_ids_session.session)
session_name = 'get_ids_session'

client = TelegramClient(session_name, api_id, api_hash)

SEARCH = [
    # Олег
    "#63", "#103", "#112",
    "Lex1", "Lex2", "Lex6", "Lex7", "Lex10", "Lex11",
    "Lex19", "Lex28", "Lex33", "Lex35", "Lex48",
    "Lex51", "Lex52", "Lex54", "Lex58", "Lex69", "Lex72",
]

async def main():
    print("Connecting...")
    await client.start()
    
    print("\n=== SEARCH for clients: " + ", ".join(SEARCH) + " ===\n")
    
    found = []
    all_chats = []
    async for dialog in client.iter_dialogs(limit=None):
        all_chats.append(dialog)
        name = dialog.name or ""
        for s in SEARCH:
            if s in name:
                found.append((s, name, dialog.id))
                print(f"MATCH [{s}] -> {name} | ID: {dialog.id}")
    
    if not found:
        print("\nNot found. Showing ALL group chats:\n")
        for d in all_chats:
            if d.is_group:
                print(f"  {d.name} | ID: {d.id}")
    
    print(f"\nTotal dialogs: {len(all_chats)}")
    print("Done!")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())