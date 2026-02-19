import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

async def main():
    print("=" * 50)
    print("  BOT CHATS - ID всех чатов где есть бот")
    print("=" * 50)
    
    # Получаем инфо о боте
    me = await bot.get_me()
    print(f"\nБот: @{me.username} (ID: {me.id})")
    print("-" * 50)
    
    # Проверяем чаты из EMPLOYEES_CONFIG
    from bot_full import EMPLOYEES_CONFIG
    
    checked = set()
    print("\nЧаты из EMPLOYEES_CONFIG:\n")
    
    for worker_id, worker_data in EMPLOYEES_CONFIG.items():
        clients = worker_data.get("clients", {})
        for client_tag, client_info in clients.items():
            chat_id = client_info.get("group_chat_id")
            if chat_id and chat_id not in checked:
                checked.add(chat_id)
                try:
                    chat = await bot.get_chat(chat_id)
                    chat_type = chat.type
                    title = chat.title or "N/A"
                    is_super = "SUPERGROUP" if chat_type == "supergroup" else "GROUP"
                    invite = chat.invite_link or "нет"
                    print(f"  {is_super}: {title}")
                    print(f"    ID: {chat_id}")
                    print(f"    Тип: {chat_type}")
                    print(f"    Invite: {invite}")
                    
                    # Проверяем права бота
                    try:
                        member = await bot.get_chat_member(chat_id, me.id)
                        print(f"    Бот: {member.status}")
                    except:
                        print(f"    Бот: неизвестно")
                    print()
                except Exception as e:
                    print(f"  ERROR: chat_id={chat_id}")
                    print(f"    {e}\n")
    
    print("-" * 50)
    print(f"Всего уникальных чатов: {len(checked)}")
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
