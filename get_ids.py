from telethon import TelegramClient
import asyncio

# --- ТВОИ ДАННЫЕ ---
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии (создаст файл get_ids_session.session)
session_name = 'get_ids_session'

client = TelegramClient(session_name, api_id, api_hash)

SEARCH = [
    # Миша М
    "#133", "#134", "#138", "#141", "#149",
    "Toy49", "Toy50", "Toy61", "Toy63", "Toy64", "Toy68", "Toy78", "Toy79",
    # Виталий
    "#113", "#131", "#139", "#146",
    "Toy55", "Toy59", "Toy60", "Toy73",
    # Миша К
    "#101", "#103", "#117", "#125", "#142", "#144", "#147",
    "Toy56", "Toy75", "Toy76", "Старі",
    # Влад
    "#137", "#140", "#145", "#148",
    "Toy21", "Toy44", "Toy46", "Toy67", "Toy74",
    # Олег
    "#58", "#132", "#143",
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