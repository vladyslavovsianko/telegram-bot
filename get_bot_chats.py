import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

async def main():
    print("=" * 70)
    print("  BOT CHATS CHECK")
    print("=" * 70)
    
    me = await bot.get_me()
    print(f"\nBot: @{me.username} (ID: {me.id})\n")
    
    from bot_full import EMPLOYEES_CONFIG, TARGET_CHANNEL_ID, VIP_GROUP_ID, TARGET_CHAT_ID
    
    # Собираем ВСЕ уникальные chat_id
    all_ids = set()
    
    if TARGET_CHANNEL_ID: all_ids.add(TARGET_CHANNEL_ID)
    if VIP_GROUP_ID: all_ids.add(VIP_GROUP_ID)
    if TARGET_CHAT_ID: all_ids.add(TARGET_CHAT_ID)
    
    for worker_id, worker_data in EMPLOYEES_CONFIG.items():
        for client_tag, client_info in worker_data.get("clients", {}).items():
            gid = client_info.get("group_chat_id")
            if gid: all_ids.add(gid)
    
    all_ids.discard(0)
    
    groups = []
    supergroups = []
    channels = []
    errors = []
    
    for chat_id in sorted(all_ids):
        try:
            chat = await bot.get_chat(chat_id)
            title = chat.title or "N/A"
            ctype = chat.type
            
            # Проверяем права бота
            try:
                member = await bot.get_chat_member(chat_id, me.id)
                role = member.status
            except:
                role = "?"
            
            info = {"id": chat_id, "title": title, "type": ctype, "role": role}
            
            if ctype == "supergroup":
                supergroups.append(info)
            elif ctype == "group":
                groups.append(info)
            elif ctype == "channel":
                channels.append(info)
        except Exception as e:
            errors.append({"id": chat_id, "error": str(e)})
    
    if supergroups:
        print(f"SUPERGROUPS ({len(supergroups)}) - links t.me/c/ WORK")
        print("-" * 70)
        for c in supergroups:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()
    
    if groups:
        print(f"GROUPS ({len(groups)}) - NEED TO CONVERT to supergroup!")
        print("-" * 70)
        for c in groups:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()
    
    if channels:
        print(f"CHANNELS ({len(channels)})")
        print("-" * 70)
        for c in channels:
            print(f"  {c['id']:<20} {c['title']:<30} bot={c['role']}")
        print()
    
    if errors:
        print(f"ERRORS ({len(errors)}) - bot NOT in these chats!")
        print("-" * 70)
        for c in errors:
            print(f"  {c['id']:<20} {c['error']}")
        print()
    
    total = len(supergroups) + len(groups) + len(channels)
    print("=" * 70)
    print(f"Total accessible: {total}")
    print(f"  Supergroups: {len(supergroups)} (links work)")
    print(f"  Groups:      {len(groups)} (convert these!)")
    print(f"  Channels:    {len(channels)}")
    print(f"  Errors:      {len(errors)}")
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
