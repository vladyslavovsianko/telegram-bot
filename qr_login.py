from telethon import TelegramClient, errors
import qrcode
import asyncio
import os

# ТВОИ ДАННЫЕ
api_id = 33447442
api_hash = '8478a091230df0ecfabf552e97c55aa2'

# Имя сессии
session_name = 'manager_session'

# Чистим старую сессию, чтобы не мешала
if os.path.exists(f"{session_name}.session"):
    try:
        os.remove(f"{session_name}.session")
        print("🗑 Старый файл сессии удален.")
    except: pass

client = TelegramClient(session_name, api_id, api_hash)

async def main():
    print("\n🚀 ЗАПУСК ВХОДА ПО QR-КОДУ (С ПОДДЕРЖКОЙ 2FA)...")
    await client.connect()
    
    if not await client.is_user_authorized():
        qr_login = await client.qr_login()
        print("\n📸 ОТСКАНИРУЙ ЭТОТ КОД ЧЕРЕЗ ТЕЛЕФОН:")
        print(f"Ссылка (если QR кривой): {qr_login.url}")
        
        qr = qrcode.QRCode()
        qr.add_data(qr_login.url)
        qr.print_ascii(invert=True)
        
        print("\n⏳ Жду сканирования...")
        
        try:
            # Ждем подтверждения с телефона
            await qr_login.wait()
        except errors.SessionPasswordNeededError:
            # ЕСЛИ НУЖЕН ПАРОЛЬ — СКРИПТ ПОПАДЕТ СЮДА
            print("\n🔐 ТРЕБУЕТСЯ ОБЛАЧНЫЙ ПАРОЛЬ!")
            pwd = input("⌨️ Введите ваш пароль от Telegram: ")
            await client.sign_in(password=pwd)
        except Exception as e:
            # Обработка других ошибок (включая ту, что у тебя вылезла)
            if "password is required" in str(e) or "Two-steps" in str(e):
                print("\n🔐 ТРЕБУЕТСЯ ОБЛАЧНЫЙ ПАРОЛЬ!")
                pwd = input("⌨️ Введите ваш пароль от Telegram: ")
                await client.sign_in(password=pwd)
            else:
                print(f"\n❌ Ошибка: {e}")
                return

    # Проверка
    if await client.is_user_authorized():
        me = await client.get_me()
        print("\n" + "="*30)
        print(f"✅ УСПЕХ! Вход выполнен.")
        print(f"👤 Пользователь: {me.first_name}")
        print(f"🆔 Твой ID: {me.id}")
        print("="*30)
        print("Теперь запускай new.py!")
    else:
        print("❌ Не удалось авторизоваться.")
        
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())