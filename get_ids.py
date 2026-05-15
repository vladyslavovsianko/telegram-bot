import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from telethon import TelegramClient
import asyncio

# --- ТВОИ ДАННЫЕ ---
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии (создаст файл get_ids_session.session)
session_name = 'get_ids_session'

client = TelegramClient(session_name, api_id, api_hash)

SEARCH = [
    # Числовые
    "#46/47", "#58", "#70", "#102", "#103", "#112", "#114", "#124",
    "#127", "#131", "#133", "#136", "#139", "#140-2", "#142", "#144",
    "#148", "#150", "#152", "#154", "#155", "#156", "#157", "#159",
    "#160", "#161", "#162", "#163", "#164", "#165", "#166", "#167",
    "#168", "#169", "#170", "#1003",
    # Toy
    "Toy 8", "Toy 30", "Toy 32", "Toy 38", "Toy 44", "Toy 47",
    "Toy 49", "Toy 60", "Toy 64", "Toy 67", "Toy 73", "Toy 77",
    "Toy 78", "Toy 82", "Toy 85", "Toy 86", "Toy 87", "Toy 88",
    "Toy 90", "Toy 92", "Toy 93", "Toy 94", "Toy 95", "Toy 96",
    "Toy 97", "Toy 104", "Toy 105", "Toy 107", "Toy 110", "Toy 113",
    "Toy 116", "Toy 119", "Toy 120",
    # Lex
    "Lex 2", "Lex 6", "Lex 7", "Lex 19", "Lex 28", "Lex 51",
    "Lex 54", "Lex 69", "Lex 70", "Lex 72", "Lex 83", "Lex 89",
    "Lex 91", "Lex 92", "Lex 98", "Lex 99", "Lex 102", "Lex 103",
    "Lex 106", "Lex 108", "Lex 109", "Lex 111", "Lex 112", "Lex 113",
    "Lex 114", "Lex 115", "Lex 117", "Lex 118",
]

async def main():
    print("Connecting...")
    await client.start()
    print(f"\nSearch {len(SEARCH)} clients...\n")
    
    found = {}       # tag -> (id, name) — первое совпадение
    duplicates = {}  # tag -> [(id, name), ...] — все совпадения
    async for dialog in client.iter_dialogs(limit=None):
        name = dialog.name or ""
        for s in SEARCH:
            if s in name:
                if s not in found:
                    found[s] = (dialog.id, name)
                    print(f"MATCH [{s}] -> {name} | ID: {dialog.id}")
                else:
                    # Нашли второй (третий...) чат с тем же именем
                    if s not in duplicates:
                        duplicates[s] = [found[s]]
                    duplicates[s].append((dialog.id, name))
                    print(f"DUPLICATE [{s}] -> {name} | ID: {dialog.id}")

    if duplicates:
        print("\n!!! DUPLICATES — check manually which ID is correct !!!")
        for tag, matches in duplicates.items():
            print(f"  [{tag}]:")
            for mid, mname in matches:
                print(f"    ID: {mid}  name: {mname}")

    not_found = [s for s in SEARCH if s not in found]
    print(f"\nFound: {len(found)}")
    print(f"Not found ({len(not_found)}): {', '.join(not_found)}")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())