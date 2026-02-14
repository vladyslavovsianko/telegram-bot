@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ====================================
echo 📥 Скачивание базы данных с сервера...
echo ====================================
echo.

"C:\Program Files\Git\usr\bin\scp.exe" root@46.225.119.58:/opt/telegram-bot/bot_database.db server_database.db

if %errorlevel% equ 0 (
    echo.
    echo ✅ База данных успешно скачана!
    echo 📁 Файл: server_database.db
    echo 📍 Путь: %~dp0server_database.db
    echo.
    echo Теперь откройте server_database.db в DBeaver
    echo.
) else (
    echo.
    echo ❌ Ошибка скачивания!
    echo.
    echo Попробуйте запустить вручную в Git Bash:
    echo scp root@46.225.119.58:/opt/telegram-bot/bot_database.db ./server_database.db
    echo.
)

pause
