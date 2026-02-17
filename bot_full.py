import asyncio
import logging
import uuid
import os
import io
import sqlite3
from contextlib import suppress
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto, InputMediaVideo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from telethon import TelegramClient
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# ==========================================
# 1. НАСТРОЙКИ
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")

# 👑 ГЛАВНЫЕ МЕНЕДЖЕРЫ
MANAGER_IDS = [int(x) for x in os.getenv("MANAGER_IDS", "").split(",") if x]

# 👮‍♂️ МОДЕРАТОРЫ
STATUS_MODERATORS = [int(x) for x in os.getenv("STATUS_MODERATORS", "").split(",") if x]

# КАНАЛЫ (Витрина)
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

# ГРУППА ДЛЯ АВТО-ПОСТИНГА VIP
VIP_GROUP_ID = int(os.getenv("VIP_GROUP_ID", "0"))

# ЧАТ ПО УМОЛЧАНИЮ
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

# ⏱ ЗАДЕРЖКА ПУБЛИКАЦИИ В КАНАЛ (СЕКУНДЫ)
CHANNEL_POST_DELAY = int(os.getenv("CHANNEL_POST_DELAY", "10"))

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# ⚠️ НАСТРОЙКИ КЛИЕНТОВ
EMPLOYEES_CONFIG = {
    12313213131321: { 
        "clients": {
            "#Test": {"client_id": 12312213131321, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#4": {"client_id": 0, "group_chat_id": -5069461222},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222}
        } 
    },
    610220736: { 
        "clients": { 
            "#VIP_Chat": {"client_id": 610220736, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#4": {"client_id": 0, "group_chat_id": -5069461222},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222},
            "#136": {"client_id": 0, "group_chat_id": -5295466035}
        } 
    },
    645070075: { 
        "clients": { 
            "#Moscow": {"client_id": 7948650630, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#136": {"client_id": 0, "group_chat_id": -5295466035},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222}
        } 
    },
    625971673: {  # Виталий
        "clients": {
            "#Moscow": {"client_id": 7948650630, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#4": {"client_id": 0, "group_chat_id": -5069461222},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222}
        }
    },
    5442618444: {  # Миша
        "clients": {
            "#Moscow": {"client_id": 7948650630, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#4": {"client_id": 0, "group_chat_id": -5069461222},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222}
        }
    },
    419890021: {  # Олег
        "clients": {
            "#Moscow": {"client_id": 7948650630, "group_chat_id": -5069461222},
            "#1": {"client_id": 0, "group_chat_id": -5069461222},
            "#2": {"client_id": 0, "group_chat_id": -5069461222},
            "#3": {"client_id": 0, "group_chat_id": -5069461222},
            "#4": {"client_id": 0, "group_chat_id": -5069461222},
            "#5": {"client_id": 0, "group_chat_id": -5069461222},
            "#6": {"client_id": 0, "group_chat_id": -5069461222},
            "#7": {"client_id": 0, "group_chat_id": -5069461222},
            "#8": {"client_id": 0, "group_chat_id": -5069461222},
            "#9": {"client_id": 0, "group_chat_id": -5069461222},
            "#10": {"client_id": 0, "group_chat_id": -5069461222},
            "#11": {"client_id": 0, "group_chat_id": -5069461222},
            "#12": {"client_id": 0, "group_chat_id": -5069461222},
            "#13": {"client_id": 0, "group_chat_id": -5069461222},
            "#14": {"client_id": 0, "group_chat_id": -5069461222},
            "#15": {"client_id": 0, "group_chat_id": -5069461222},
            "#16": {"client_id": 0, "group_chat_id": -5069461222},
            "#17": {"client_id": 0, "group_chat_id": -5069461222},
            "#18": {"client_id": 0, "group_chat_id": -5069461222},
            "#19": {"client_id": 0, "group_chat_id": -5069461222},
            "#20": {"client_id": 0, "group_chat_id": -5069461222}
        }
    }
}

DB_FILE = 'bot_database.db'
LOTS_CACHE = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
user_client = TelegramClient('manager_session', API_ID, API_HASH)

# ==========================================
# 2. БАЗА ДАННЫХ
# ==========================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS workers (
            user_id INTEGER PRIMARY KEY, name TEXT, counter INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER, worker_name TEXT, anketa_id TEXT, client_tag TEXT, 
            seller_name TEXT, seller_number TEXT, table_num TEXT, price TEXT, 
            chrono_price TEXT, negotiation TEXT, year TEXT, diameter TEXT, 
            wrist TEXT, kit TEXT, condition TEXT, rating TEXT, status TEXT DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def db_check_worker(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM workers WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result: return result[0]
    return None

def db_get_next_id(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, counter FROM workers WHERE user_id = ?", (user_id,))
    data = cursor.fetchone()
    if not data: conn.close(); return "UNK0" 
    name, current_counter = data
    
    # Уникальные префиксы для каждого работника
    PREFIX_MAP = {
        610220736: "MM",      # Misha M
        5442618444: "MK",     # Misha K
        645070075: "VL",      # Vladyslav
        625971673: "VIT",     # Vitalij
        419890021: "O",       # Oleh
    }
    
    prefix = PREFIX_MAP.get(user_id, name[0].upper() if name else "X")
    new_counter = current_counter + 1
    cursor.execute("UPDATE workers SET counter = ? WHERE user_id = ?", (new_counter, user_id))
    conn.commit()
    conn.close()
    return f"{prefix}{new_counter}"

def db_save_full_order(user_id, worker_name, anketa_id, data):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO orders (
                worker_id, worker_name, anketa_id, client_tag, seller_name, seller_number, 
                table_num, price, chrono_price, negotiation, year, diameter, wrist, kit, 
                condition, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            user_id, worker_name, anketa_id, data.get('client'), data.get('seller_name'),
            data.get('seller_number'), data.get('table'), data.get('price'),
            data.get('chrono_price'), data.get('negotiation'), data.get('year'),
            data.get('diameter'), data.get('wrist'), data.get('kit'),
            data.get('condition'), data.get('rating')
        ))
        conn.commit()
        conn.close()
        logging.info(f"✅ Анкета {anketa_id} сохранена в базу данных")
    except Exception as e:
        logging.error(f"❌ Ошибка сохранения анкеты {anketa_id} в базу: {e}")
        if 'conn' in locals():
            conn.close()

def db_update_status(anketa_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE orders SET status = ? WHERE anketa_id = ?", (new_status, anketa_id))
        conn.commit()
    except: pass
    conn.close()

# ==========================================
# 3. ЭТАПЫ (STATES)
# ==========================================

class Form(StatesGroup):
    choosing_client = State()
    choosing_other_worker = State()  # Выбор другого работника
    choosing_other_worker_client = State()  # Выбор клиента другого работника
    uploading_media = State()
    entering_table = State()
    entering_price = State()
    entering_chrono_price = State()
    manual_year = State()
    manual_diameter = State()
    manual_wrist = State()
    choosing_negotiation = State()
    choosing_year = State()
    choosing_diameter = State()
    choosing_wrist = State()
    choosing_kit = State()
    choosing_condition = State()
    entering_seller_name = State()   
    entering_seller_number = State() 
    choosing_worker_rating = State()
    entering_custom_rating = State()
    final_review = State()

class ManagerState(StatesGroup):
    waiting_for_feedback = State()
    choosing_employee_to_write = State()
    writing_to_employee = State()

class EmployeeState(StatesGroup):
    uploading_requested_video = State()

# ==========================================
# 4. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def get_user_clients(user_id):
    """Возвращает словарь клиентов сотрудника"""
    config = EMPLOYEES_CONFIG.get(user_id)
    if config: return config['clients']
    return {}

def get_client_id(user_id, client_tag):
    """Получить ID клиента по тегу"""
    clients = get_user_clients(user_id)
    client_data = clients.get(client_tag)
    if isinstance(client_data, dict):
        return client_data.get("client_id")
    return client_data  # Обратная совместимость со старым форматом

def get_client_group_chat(user_id, client_tag):
    """Получить ID группового чата для клиента"""
    clients = get_user_clients(user_id)
    client_data = clients.get(client_tag)
    if isinstance(client_data, dict):
        group_chat = client_data.get("group_chat_id")
        return group_chat if group_chat is not None else TARGET_CHAT_ID
    # Если старый формат или нет данных
    return TARGET_CHAT_ID

def make_kb(buttons, rows=2, back=True, manual_text=None, skip=True, done_text=None):
    kb = []
    row = []
    for btn in buttons:
        row.append(KeyboardButton(text=btn))
        if len(row) == rows: kb.append(row); row = []
    if row: kb.append(row)
    controls = []
    if back: controls.append(KeyboardButton(text="🔙 Назад"))
    if manual_text: controls.append(KeyboardButton(text=manual_text))
    if skip: controls.append(KeyboardButton(text="⏩ Пропустить")) 
    if done_text: controls.append(KeyboardButton(text=done_text))
    if controls: kb.append(controls)
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, is_persistent=True)

def get_calc_control_buttons(show_skip=True):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="calc_back")
    if show_skip:
        builder.button(text="⏩ Пропустить", callback_data="calc_skip")
    builder.adjust(2 if show_skip else 1)
    return builder.as_markup()

def get_channel_status_kb(lot_id):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🟡 Reserved", callback_data=f"ch_status_reserved_{lot_id}"),
        InlineKeyboardButton(text="🟢 Available", callback_data=f"ch_status_available_{lot_id}"),
        InlineKeyboardButton(text="🔴 Sold", callback_data=f"ch_status_sold_{lot_id}")
    )
    return builder.as_markup()

# ==========================================
# 5. ЛОГИКА БОТА
# ==========================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    worker_name = db_check_worker(user_id)
    is_authorized = worker_name or (user_id in MANAGER_IDS) or (user_id in STATUS_MODERATORS)
    if not is_authorized: return await message.answer(f"⛔️ Нет доступа (ID: {user_id})")
    if not worker_name and user_id in MANAGER_IDS: worker_name = "Менеджер"
    await message.answer(f"👋 Привет, <b>{worker_name}</b>!", parse_mode="HTML")
    await restart_logic(message, state, real_user_id=user_id)

async def restart_logic(message: types.Message, state: FSMContext, real_user_id=None):
    await state.clear()
    await state.update_data(media_files=[], editing_mode=False)
    uid = real_user_id if real_user_id else message.from_user.id
    if uid in MANAGER_IDS: await show_manager_main_menu(message)
    else: await show_client_menu(message, user_id=uid)

async def show_manager_main_menu(message: types.Message):
    kb = [[KeyboardButton(text="👥 Сотрудники")], [KeyboardButton(text="#Test")]]
    await message.answer("👨‍💼 <b>Панель менеджера:</b>", reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True), parse_mode="HTML")

# --- ЛОГИКА АНКЕТЫ ---
async def show_client_menu(message: types.Message, user_id=None):
    if not user_id: user_id = message.from_user.id
    clients_dict = get_user_clients(user_id)
    clients_list = list(clients_dict.keys())
    if not clients_list:
        if user_id in MANAGER_IDS: pass
        else: await message.answer("⚠️ Нет клиентов."); return
    
    # Добавляем кнопку для множественного выбора
    kb = make_kb(clients_list, rows=3, back=False, skip=False, done_text="📋 Несколько клиентов") 
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(Form.choosing_client)
    await message.answer("1️⃣ <b>Выбери клиента:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_client)
async def process_client(message: types.Message, state: FSMContext):
    logging.info(f"🔍 process_client вызван: текст='{message.text}'")
    
    if message.text == "📋 Несколько клиентов":
        logging.info("▶ Переход в режим множественного выбора")
        return await start_multi_client_selection(message, state)
    
    data = await state.get_data()
    logging.info(f"🔍 State data: multi_mode={data.get('multi_mode')}, selected={data.get('selected_clients', [])}")
    
    # Проверяем режим множественного выбора
    if data.get('multi_mode'):
        # Убираем галочку если есть
        client = message.text.replace("✅ ", "")
        selected = data.get('selected_clients', [])
        
        if message.text.startswith("✅ ") and not message.text.startswith("✅ Готово"):
            # Убираем из выбранных
            if client in selected:
                selected.remove(client)
            await state.update_data(selected_clients=selected)
            return await show_multi_client_menu(message, state)
        elif message.text == "🔙 Назад":
            # Отменяем множественный выбор
            await state.update_data(multi_mode=False, selected_clients=[])
            return await show_client_menu(message, user_id=message.from_user.id)
        elif message.text.startswith("✅ Готово"):
            # Завершаем выбор
            if not selected:
                return await message.answer("⚠️ Выберите хотя бы одного клиента!")
            logging.info(f"✅ Выбрано {len(selected)} клиентов: {selected}")
            await state.update_data(multi_clients=selected, client=", ".join(selected), multi_mode=False)
            return await show_media_menu(message)
        else:
            # Добавляем в выбранные
            if client not in selected:
                selected.append(client)
            await state.update_data(selected_clients=selected)
            return await show_multi_client_menu(message, state)
    
    # Обычный режим - один клиент
    if message.text == "#Test" and message.from_user.id in MANAGER_IDS: 
        await state.update_data(client="#Test")
    else: 
        await state.update_data(client=message.text)
    await check_edit_or_next(message, state, show_media_menu)

async def start_multi_client_selection(message: types.Message, state: FSMContext):
    """Начинаем выбор нескольких клиентов"""
    await state.update_data(selected_clients=[], multi_mode=True)
    await show_multi_client_menu(message, state)

async def show_multi_client_menu(message: types.Message, state: FSMContext):
    """Показываем меню выбора с отметками"""
    user_id = message.from_user.id
    data = await state.get_data()
    selected = data.get('selected_clients', [])
    
    clients_dict = get_user_clients(user_id)
    clients_list = []
    
    # Добавляем галочки к выбранным клиентам
    for client in clients_dict.keys():
        if client in selected:
            clients_list.append(f"✅ {client}")
        else:
            clients_list.append(client)
    
    selected_count = len(selected)
    kb = make_kb(clients_list, rows=3, back=True, skip=False, done_text=f"✅ Готово ({selected_count})" if selected_count > 0 else None)
    await message.answer(f"📋 <b>Выбери клиентов ({selected_count} выбрано):</b>", reply_markup=kb, parse_mode="HTML")

async def show_other_workers_menu(message: types.Message, state: FSMContext):
    """Показывает список других работников"""
    current_user_id = message.from_user.id
    
    # Получаем список всех работников кроме текущего
    workers_list = []
    for worker_id, config in EMPLOYEES_CONFIG.items():
        if worker_id != current_user_id and config.get('clients'):
            worker_name = db_check_worker(worker_id)
            if worker_name:
                workers_list.append(f"👤 {worker_name}")
    
    if not workers_list:
        await message.answer("⚠️ Нет других работников")
        return await show_client_menu(message, user_id=current_user_id)
    
    kb = make_kb(workers_list, rows=2, back=True, skip=False)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(Form.choosing_other_worker)
    await message.answer("👥 <b>Выбери работника:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_other_worker)
async def process_other_worker(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await show_client_menu(message, user_id=message.from_user.id)
    
    # Убираем "👤 " из имени
    worker_name = message.text.replace("👤 ", "")
    
    # Находим ID работника по имени
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM workers WHERE name = ?", (worker_name,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        await message.answer("⚠️ Работник не найден")
        return await show_other_workers_menu(message, state)
    
    worker_id = result[0]
    
    # Получаем клиентов этого работника
    clients_dict = get_user_clients(worker_id)
    clients_list = list(clients_dict.keys())
    
    if not clients_list:
        await message.answer("⚠️ У этого работника нет клиентов")
        return await show_other_workers_menu(message, state)
    
    # Сохраняем ID работника в state
    await state.update_data(other_worker_id=worker_id, other_worker_name=worker_name)
    
    kb = make_kb(clients_list, rows=3, back=True, skip=False)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(Form.choosing_other_worker_client)
    await message.answer(f"👤 <b>Клиенты работника {worker_name}:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_other_worker_client)
async def process_other_worker_client(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        return await show_other_workers_menu(message, state)
    
    data = await state.get_data()
    other_worker_id = data.get('other_worker_id')
    
    # Сохраняем выбранного клиента и ID работника-владельца клиента
    await state.update_data(
        client=message.text,
        client_owner_id=other_worker_id  # Запоминаем чей это клиент
    )
    await check_edit_or_next(message, state, show_media_menu)

async def show_media_menu(message):
    chat_id = message.chat.id
    kb = make_kb([], rows=1, back=True, done_text="✅ Все файлы загружены", skip=False)
    fsm = dp.fsm.get_context(bot, chat_id, chat_id)
    await fsm.set_state(Form.uploading_media)
    await bot.send_message(chat_id, "📸 <b>Скинь фото и видео:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.uploading_media, F.photo | F.video)
async def receive_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_files = data.get("media_files", [])
    if message.photo: media_files.append({'type': 'photo', 'id': message.photo[-1].file_id})
    elif message.video: media_files.append({'type': 'video', 'id': message.video.file_id})
    await state.update_data(media_files=media_files)

@dp.message(Form.uploading_media, F.text == "✅ Все файлы загружены")
async def finish_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("media_files"): return await message.answer("⛔️ Загрузи хотя бы 1 фото.")
    await check_edit_or_next(message, state, lambda m: start_calculator(m, state, Form.entering_table, "3️⃣ <b>Введи номер СТОЛА:</b>", allow_skip=True))

@dp.message(Form.uploading_media, F.text == "🔙 Назад")
async def back_to_client(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("editing_mode"):
        return await show_final_review(message, state)
    await show_client_menu(message)

# --- КАЛЬКУЛЯТОР ---
async def start_calculator(message: types.Message, state: FSMContext, target_state, title, allow_skip=True):
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(target_state)
    calc_msg = await message.answer(f"{title}\n\n💡 <i>Введите число с клавиатуры</i>", reply_markup=get_calc_control_buttons(show_skip=allow_skip), parse_mode="HTML")
    await state.update_data(calc_title=title, calc_allow_skip=allow_skip, calc_msg_id=calc_msg.message_id)

# Обработчик кнопок управления калькулятором
@dp.callback_query(F.data.startswith("calc_"), StateFilter(Form.entering_seller_number, Form.entering_table, Form.entering_price, Form.entering_chrono_price, Form.manual_year, Form.manual_diameter, Form.manual_wrist))
async def process_calc_buttons(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.replace("calc_", "")
    data = await state.get_data()
    calc_msg_id = data.get("calc_msg_id")
    entered_value = data.get("entered_value", "")

    if action == "back":
        # Удаляем сообщение калькулятора
        if calc_msg_id:
            try:
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=calc_msg_id)
            except:
                pass
        
        curr_state = await state.get_state()
        editing_mode = data.get("editing_mode", False)
        
        # Если в режиме редактирования - вернуться к просмотру анкеты
        if editing_mode:
            await show_final_review(callback.message, state)
        else:
            # Обычный режим - назад к предыдущему шагу
            if curr_state == Form.entering_seller_number: await show_condition_menu(callback.message)
            elif curr_state == Form.entering_table: await show_media_menu(callback.message)
            elif curr_state == Form.entering_price: await start_calculator(callback.message, state, Form.entering_table, "3️⃣ <b>Введи номер СТОЛА:</b>", allow_skip=True)
            elif curr_state == Form.entering_chrono_price: await start_calculator(callback.message, state, Form.entering_price, "4️⃣ <b>Введи ЦЕНУ (EUR):</b>", allow_skip=True)
            elif curr_state == Form.manual_year: await show_year_menu(callback.message)
            elif curr_state == Form.manual_diameter: await show_diameter_menu(callback.message)
            elif curr_state == Form.manual_wrist: await show_wrist_menu(callback.message)
        await callback.answer()
        return

    if action == "skip":
        # Удаляем сообщение калькулятора
        if calc_msg_id:
            try:
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=calc_msg_id)
            except:
                pass
        
        final_val = "—"
        curr_state = await state.get_state()
        
        if curr_state == Form.entering_seller_number:
            await state.update_data(seller_number=final_val); await check_edit_or_next(callback.message, state, show_worker_rating_menu)
        elif curr_state == Form.entering_table:
            await state.update_data(table=final_val); await check_edit_or_next(callback.message, state, lambda m: start_calculator(m, state, Form.entering_price, "4️⃣ <b>Введи ЦЕНУ (EUR):</b>", allow_skip=False))
        elif curr_state == Form.entering_price:
            await state.update_data(price=final_val); await check_edit_or_next(callback.message, state, lambda m: start_calculator(m, state, Form.entering_chrono_price, "5️⃣ <b>Цена CHRONO24:</b>", allow_skip=False))
        elif curr_state == Form.entering_chrono_price:
            await state.update_data(chrono_price=final_val); await check_edit_or_next(callback.message, state, show_negotiation_menu)
        elif curr_state == Form.manual_year:
            await state.update_data(year=final_val); await check_edit_or_next(callback.message, state, show_diameter_menu)
        elif curr_state == Form.manual_diameter:
            await state.update_data(diameter=final_val); await check_edit_or_next(callback.message, state, show_wrist_menu)
        elif curr_state == Form.manual_wrist:
            await state.update_data(wrist=final_val); await check_edit_or_next(callback.message, state, show_kit_menu)
        await callback.answer()
        return
    
    await callback.answer()

# Обработчик текстового ввода чисел
@dp.message(StateFilter(Form.entering_seller_number, Form.entering_table, Form.entering_price, Form.entering_chrono_price, Form.manual_year, Form.manual_diameter, Form.manual_wrist))
async def process_text_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    calc_msg_id = data.get("calc_msg_id")
    
    # Удаляем сообщение калькулятора
    if calc_msg_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=calc_msg_id)
        except:
            pass
    
    # Автоматически подтверждаем введенное значение
    final_val = message.text if message.text else "0"
    curr_state = await state.get_state()
    
    if curr_state == Form.entering_seller_number:
        await state.update_data(seller_number=final_val)
        await check_edit_or_next(message, state, show_worker_rating_menu)
    elif curr_state == Form.entering_table:
        await state.update_data(table=final_val)
        await check_edit_or_next(message, state, lambda m: start_calculator(m, state, Form.entering_price, "4️⃣ <b>Введи ЦЕНУ (EUR):</b>", allow_skip=True))
    elif curr_state == Form.entering_price:
        await state.update_data(price=final_val)
        await check_edit_or_next(message, state, lambda m: start_calculator(m, state, Form.entering_chrono_price, "5️⃣ <b>Цена CHRONO24:</b>", allow_skip=True))
    elif curr_state == Form.entering_chrono_price:
        await state.update_data(chrono_price=final_val)
        await check_edit_or_next(message, state, show_negotiation_menu)
    elif curr_state == Form.manual_year:
        await state.update_data(year=final_val)
        await check_edit_or_next(message, state, show_diameter_menu)
    elif curr_state == Form.manual_diameter:
        await state.update_data(diameter=final_val)
        await check_edit_or_next(message, state, show_wrist_menu)
    elif curr_state == Form.manual_wrist:
        await state.update_data(wrist=final_val)
        await check_edit_or_next(message, state, show_kit_menu)

async def show_negotiation_menu(message):
    kb = make_kb(["⛔️ Без торга", "🤝 Есть потенциал"], rows=2, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(Form.choosing_negotiation); await bot.send_message(message.chat.id, "6️⃣ <b>Торг:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_negotiation)
async def process_negotiation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await start_calculator(message, state, Form.entering_chrono_price, "5️⃣ <b>Цена CHRONO24:</b>", allow_skip=True)
    val = message.text
    if message.text == "⏩ Пропустить": val = "—"
    elif message.text == "⛔️ Без торга": val = "Fixed price"
    elif message.text == "🤝 Есть потенциал": val = "Negotiable"
    await state.update_data(negotiation=val); await check_edit_or_next(message, state, show_year_menu)

async def show_year_menu(message):
    kb = make_kb(["60s", "70s", "80s", "90s", "00s", "10s", "20s"], rows=4, back=True, manual_text="✍️ Вручную", skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_year); await bot.send_message(message.chat.id, "7️⃣ <b>Год выпуска:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_year)
async def process_year(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_negotiation_menu(message)
    if message.text == "✍️ Вручную": return await start_calculator(message, state, Form.manual_year, "7️⃣ <b>Введите год:</b>", allow_skip=True)
    val = "—" if message.text == "⏩ Пропустить" else message.text; await state.update_data(year=val); await check_edit_or_next(message, state, show_diameter_menu)

async def show_diameter_menu(message):
    kb = make_kb([str(x) for x in range(26, 49)], rows=6, back=True, manual_text="✍️ Вручную", skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_diameter); await bot.send_message(message.chat.id, "8️⃣ <b>Диаметр (мм):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_diameter)
async def process_diameter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_year_menu(message)
    if message.text == "✍️ Вручную": return await start_calculator(message, state, Form.manual_diameter, "8️⃣ <b>Введите диаметр:</b>", allow_skip=True)
    val = "—" if message.text == "⏩ Пропустить" else message.text; await state.update_data(diameter=val); await check_edit_or_next(message, state, show_wrist_menu)

async def show_wrist_menu(message):
    wrists = []; val = 15.0
    while val <= 25.0: wrists.append(str(val).replace(".0", "")); val += 0.5
    kb = make_kb(wrists, rows=5, back=True, manual_text="✍️ Вручную", skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_wrist); await bot.send_message(message.chat.id, "9️⃣ <b>Размер запястья (см):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_wrist)
async def process_wrist(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_diameter_menu(message)
    if message.text == "✍️ Вручную": return await start_calculator(message, state, Form.manual_wrist, "9️⃣ <b>Введите размер запястья:</b>", allow_skip=True)
    val = "—" if message.text == "⏩ Пропустить" else message.text; await state.update_data(wrist=val); await check_edit_or_next(message, state, show_kit_menu)

async def show_kit_menu(message):
    kb = make_kb(["📦 Фул сет", "🎁 Только коробка", "📄 Только доки", "⌚️ Только часы"], rows=2, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_kit); await bot.send_message(message.chat.id, "🔟 <b>Комплект:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_kit)
async def process_kit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_wrist_menu(message)
    val = "—" if message.text == "⏩ Пропустить" else ("Full set" if "Фул" in message.text else ("Box only" if "коробка" in message.text else ("Papers only" if "доки" in message.text else ("Watch only" if "часы" in message.text else message.text))))
    await state.update_data(kit=val); await check_edit_or_next(message, state, show_condition_menu)

async def show_condition_menu(message):
    kb = make_kb(["✨ Новые в пленках", "💎 Отличное", "👌 Хорошее", "🤏 Носились, без критических", "🧹 Под полировку", "💀 Плохое"], rows=2, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_condition); await bot.send_message(message.chat.id, "1️⃣1️⃣ <b>Состояние:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_condition)
async def process_condition(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_kit_menu(message)
    val = "—" if message.text == "⏩ Пропустить" else ("New / Unworn" if "Новые" in message.text else ("Excellent" if "Отличное" in message.text else ("Good" if "Хорошее" in message.text else ("Worn (no major damage)" if "Носились" in message.text else ("Needs polishing" if "полировку" in message.text else ("Poor" if "Плохое" in message.text else message.text))))))
    await state.update_data(condition=val, seller_name="—"); await check_edit_or_next(message, state, lambda m: start_calculator(m, state, Form.entering_seller_number, "📱 <b>Введи НОМЕР продавца:</b>", allow_skip=True))

async def ask_seller_name(message):
    kb = make_kb([], rows=1, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.entering_seller_name); await bot.send_message(message.chat.id, "✍️ <b>Введи ИМЯ продавца:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.entering_seller_name)
async def process_seller_name(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад": return await show_condition_menu(message)
    val = "—" if message.text == "⏩ Пропустить" else message.text
    await state.update_data(seller_name=val); await check_edit_or_next(message, state, lambda m: start_calculator(m, state, Form.entering_seller_number, "📱 <b>Введи НОМЕР продавца:</b>", allow_skip=True))

async def show_worker_rating_menu(message):
    kb = make_kb(["🔥 Сильный вариант, рекомендую", "👍 Можно брать", "⚠️ Есть нюансы", "🤔 Под вопросом", "❌ Не рекомендую"], rows=1, back=True, skip=True, manual_text="💬 Свой комментарий")
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_worker_rating); await bot.send_message(message.chat.id, "1️⃣2️⃣ <b>Твоя оценка (для менеджера):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_worker_rating)
async def process_rating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await start_calculator(message, state, Form.entering_seller_number, "📱 <b>Введи НОМЕР продавца:</b>", allow_skip=True)
    if message.text == "💬 Свой комментарий": await state.set_state(Form.entering_custom_rating); await message.answer("✍️ <b>Напиши комментарий:</b>", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML"); return
    val = "—" if message.text == "⏩ Пропустить" else ("🔥 Highly recommended" if "Сильный" in message.text else ("👍 Good option" if "Можно" in message.text else ("⚠️ Has nuances" if "нюансы" in message.text else ("🤔 Questionable" if "вопросом" in message.text else ("❌ Not recommended" if "Не" in message.text else message.text)))))
    await state.update_data(rating=val); await show_final_review(message, state)

@dp.message(Form.entering_custom_rating)
async def process_custom_rating_text(message: types.Message, state: FSMContext):
    await state.update_data(rating=f"💬 {message.text}"); await show_final_review(message, state)

# ==========================================
# 8. ПРОВЕРКА И ОТПРАВКА
# ==========================================

async def show_final_review(message: types.Message, state: FSMContext):
    await state.update_data(editing_mode=False)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.final_review); data = await state.get_data()
    text = (f"📋 <b>ПРОВЕРКА (Вид для клиента):</b>\n\n👤 Client: {data.get('client')}\nS{data.get('table')}\n📱 Seller: {data.get('seller_number')}\n💶 Price: €{data.get('price')}\n📉 Chrono: €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 <b>Rating:</b> {data.get('rating')}")
    builder = InlineKeyboardBuilder(); builder.button(text="✏️ Изменить", callback_data="open_edit_menu"); builder.button(text="✅ ОТПРАВИТЬ МЕНЕДЖЕРУ", callback_data="send_final"); builder.adjust(1)
    msg = await message.answer("Загружаю анкету...", reply_markup=ReplyKeyboardRemove()); await msg.delete()
    media_files = data.get("media_files", [])
    if len(media_files) > 0:
        media_group = []
        for item in media_files:
            if item['type'] == 'photo': media_group.append(InputMediaPhoto(media=item['id'], parse_mode="HTML"))
            elif item['type'] == 'video': media_group.append(InputMediaVideo(media=item['id'], parse_mode="HTML"))
        media_group[0].caption = text; media_group[0].parse_mode = "HTML"
        if len(media_group) > 1: 
            # Отправляем медиагруппу с полным текстом
            await message.answer_media_group(media=media_group)
            # Добавляем минимальное сообщение только с кнопками
            await message.answer("⬇️", reply_markup=builder.as_markup())
        else:
            # Одно медиа - кнопки прикрепляются к нему
            if media_files[0]['type'] == 'photo': await message.answer_photo(photo=media_files[0]['id'], caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")
            else: await message.answer_video(video=media_files[0]['id'], caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "open_edit_menu")
async def show_edit_menu(c: types.CallbackQuery):
    b = InlineKeyboardBuilder()
    b.button(text="👤 Client", callback_data="edit_client"); b.button(text="📸 Media", callback_data="edit_media")
    b.button(text="🔢 Table", callback_data="edit_table"); b.button(text="💶 Price", callback_data="edit_price")
    b.button(text="📉 Chrono", callback_data="edit_chrono"); b.button(text="🗣 Nego", callback_data="edit_nego")
    b.button(text="📅 Year", callback_data="edit_year"); b.button(text="📏 Diam", callback_data="edit_diam")
    b.button(text="🖐 Wrist", callback_data="edit_wrist"); b.button(text="📦 Set", callback_data="edit_kit")
    b.button(text="⚙️ Cond", callback_data="edit_cond"); b.button(text="👨‍💼 Seller", callback_data="edit_seller")
    b.button(text="👀 Rating", callback_data="edit_rating"); b.button(text="🔙 Назад", callback_data="back_to_review")
    b.adjust(2, 2, 2, 2, 2, 2, 2, 2, 1); await c.message.edit_reply_markup(reply_markup=b.as_markup())

@dp.callback_query(F.data == "back_to_review")
async def back_to_rev(c: types.CallbackQuery, state: FSMContext):
    await c.answer()
    await c.message.delete()
    await show_final_review(c.message, state)

@dp.callback_query(F.data.startswith("edit_"))
async def process_edit_click(c: types.CallbackQuery, state: FSMContext):
    field = c.data.split("_")[1]; await state.update_data(editing_mode=True); await c.message.delete(); uid = c.from_user.id
    if field == "client": await show_client_menu(c.message, user_id=uid)
    elif field == "media": await state.update_data(media_files=[]); await show_media_menu(c.message)
    elif field == "table": await start_calculator(c.message, state, Form.entering_table, "3️⃣ <b>Введи номер СТОЛА:</b>", allow_skip=True)
    elif field == "price": await start_calculator(c.message, state, Form.entering_price, "4️⃣ <b>Введи ЦЕНУ (EUR):</b>", allow_skip=True)
    elif field == "chrono": await start_calculator(c.message, state, Form.entering_chrono_price, "5️⃣ <b>Цена CHRONO24:</b>", allow_skip=True)
    elif field == "nego": await show_negotiation_menu(c.message)
    elif field == "year": await show_year_menu(c.message)
    elif field == "diam": await show_diameter_menu(c.message)
    elif field == "wrist": await show_wrist_menu(c.message)
    elif field == "kit": await show_kit_menu(c.message)
    elif field == "cond": await show_condition_menu(c.message)
    elif field == "seller": await ask_seller_name(c.message)
    elif field == "rating": await show_worker_rating_menu(c.message)
    await c.answer()

async def check_edit_or_next(message, state, next_func):
    data = await state.get_data()
    if data.get("editing_mode"): await show_final_review(message, state)
    else:
        if callable(next_func): 
            if next_func.__code__.co_argcount == 1: await next_func(message)
            else: await next_func(message)
        else: await next_func(message)

# ==========================================
# ОТПРАВКА И ПОСТИНГ
# ==========================================

async def broadcast_to_channels(media_files, text, lot_id, specific_chat_id):
    """Отправляет пост в Канал (отложенно) и В КОНКРЕТНЫЙ ЧАТ (сразу)"""
    channel_buttons = get_channel_status_kb(lot_id)
    chat_msg_id = None
    chat_text_msg_id = None
    
    # 1. ОТЛОЖЕННАЯ ОТПРАВКА В ОБЩИЙ КАНАЛ
    if TARGET_CHANNEL_ID != 0:
        asyncio.create_task(delayed_channel_post(TARGET_CHANNEL_ID, media_files, text, channel_buttons, lot_id))

    # 2. МГНОВЕННАЯ ОТПРАВКА В ЦЕЛЕВОЙ ЧАТ
    # specific_chat_id теперь уже содержит правильный ID группового чата
    target = specific_chat_id if specific_chat_id else TARGET_CHAT_ID
    
    if target and target != 0:
        try:
            # Создаем свежую медиагруппу для чата
            chat_media_group = []
            for item in media_files:
                if item['type'] == 'photo': chat_media_group.append(InputMediaPhoto(media=item['id'], parse_mode="HTML"))
                elif item['type'] == 'video': chat_media_group.append(InputMediaVideo(media=item['id'], parse_mode="HTML"))
            
            if len(chat_media_group) > 1:
                # Медиагруппа: отправляем фото/видео, затем отдельное текстовое сообщение с кнопками
                msgs = await bot.send_media_group(target, media=chat_media_group)
                text_msg = await bot.send_message(target, text, reply_markup=channel_buttons, parse_mode="HTML")
                chat_msg_id = msgs[0].message_id
                chat_text_msg_id = text_msg.message_id  # ID текстового сообщения для обновления
            else:
                # Одно медиа: подпись с кнопками
                msg = None
                if media_files[0]['type'] == 'photo': msg = await bot.send_photo(target, media_files[0]['id'], caption=text, reply_markup=channel_buttons, parse_mode="HTML")
                else: msg = await bot.send_video(target, media_files[0]['id'], caption=text, reply_markup=channel_buttons, parse_mode="HTML")
                chat_msg_id = msg.message_id
        except Exception as e:
            print(f"❌ Ошибка чата {target}: {e}")
            
    return None, chat_msg_id, chat_text_msg_id

async def delayed_channel_post(chat_id, media_files, text, buttons, lot_id):
    # ТАЙМЕР (СЕКУНДЫ)
    await asyncio.sleep(CHANNEL_POST_DELAY) 
    
    try:
        # Создаем свежую медиагруппу для канала
        channel_media_group = []
        for i, item in enumerate(media_files):
            if item['type'] == 'photo': 
                # Добавляем caption только к последнему фото в альбоме
                caption = text if i == len(media_files) - 1 else None
                channel_media_group.append(InputMediaPhoto(media=item['id'], caption=caption, parse_mode="HTML"))
            elif item['type'] == 'video': 
                caption = text if i == len(media_files) - 1 else None
                channel_media_group.append(InputMediaVideo(media=item['id'], caption=caption, parse_mode="HTML"))
        
        msg_id = None
        text_msg_id = None
        if len(channel_media_group) > 1:
            # Медиагруппа: отправляем с caption на последнем медиа (БЕЗ кнопок)
            msgs = await bot.send_media_group(chat_id, media=channel_media_group)
            msg_id = msgs[0].message_id
        else:
            # Одно медиа: подпись БЕЗ кнопок
            if media_files[0]['type'] == 'photo': 
                msg = await bot.send_photo(chat_id, media_files[0]['id'], caption=text, parse_mode="HTML")
            else: 
                msg = await bot.send_video(chat_id, media_files[0]['id'], caption=text, parse_mode="HTML")
            msg_id = msg.message_id
        
        # Обновляем кэш
        if lot_id in LOTS_CACHE:
            LOTS_CACHE[lot_id]['channel_msg_id'] = msg_id
            LOTS_CACHE[lot_id]['channel_text_msg_id'] = None  # Больше нет отдельного текста
            
            # Обновляем кнопки менеджера с ссылкой на канал
            await update_manager_buttons_with_channel_link(lot_id, msg_id)
            
    except Exception as e:
        print(f"❌ Ошибка отложенного поста: {e}")

async def update_manager_buttons_with_channel_link(lot_id, channel_msg_id):
    """Обновляет кнопки менеджера после публикации в канале"""
    try:
        lot_data = LOTS_CACHE.get(lot_id)
        if not lot_data:
            return
        
        # Создаем ссылку на канал
        clean_channel_id = str(TARGET_CHANNEL_ID).replace("-100", "")
        channel_link = f"https://t.me/c/{clean_channel_id}/{channel_msg_id}"
        
        # Получаем данные для пересоздания кнопок
        target_client_id = lot_data.get('target_client_id')
        client_tag = lot_data.get('client_tag')
        chat_msg_id = lot_data.get('chat_msg_id')
        user_id = lot_data.get('user_id')
        
        # Ссылка на групповой чат
        actual_chat_id = get_client_group_chat(user_id, client_tag) if user_id and client_tag else None
        chat_link = None
        if actual_chat_id and chat_msg_id:
            clean_id = str(actual_chat_id).replace("-100", "").replace("-", "")
            chat_link = f"https://t.me/c/{clean_id}/{chat_msg_id}"
        
        # Пересоздаем кнопки
        mgr_kb = InlineKeyboardBuilder()
        if target_client_id: 
            mgr_kb.button(text=f"🚀 Клиенту ({client_tag})", callback_data=f"sendto_client_{lot_id}")
        else: 
            mgr_kb.button(text="⚠️ Нет контакта", callback_data=f"clean_text_{lot_id}")
        
        if chat_link: 
            mgr_kb.button(text="💬 Пост в группе", url=chat_link)
        
        # Кнопка на канал (теперь с ссылкой!)
        mgr_kb.button(text="📢 Пост в канале", url=channel_link)
        
        if target_client_id and isinstance(target_client_id, int):
            mgr_kb.button(text="👤 Чат с клиентом", url=f"tg://user?id={target_client_id}")
        
        mgr_kb.button(text="📹 Запросить видео", callback_data=f"req_video_{lot_id}")
        mgr_kb.button(text="✅ БЕРУТ", callback_data=f"client_buy_{lot_id}")
        mgr_kb.button(text="❌ Отказ", callback_data=f"reject_{lot_id}")
        mgr_kb.button(text="💬 Коммент", callback_data=f"feedback_start_{lot_id}")
        
        mgr_kb.row(
            InlineKeyboardButton(text="🟡 Rsrv", callback_data=f"set_status_reserved_{lot_id}"),
            InlineKeyboardButton(text="🟢 Avail", callback_data=f"set_status_available_{lot_id}"),
            InlineKeyboardButton(text="🔴 Sold", callback_data=f"set_status_sold_{lot_id}")
        )
        
        # Обновляем кнопки у всех менеджеров
        manager_msgs = lot_data.get('manager_msgs', [])
        for mgr_info in manager_msgs:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=mgr_info['chat_id'],
                    message_id=mgr_info['msg_id'],
                    reply_markup=mgr_kb.as_markup()
                )
            except Exception as e:
                print(f"❌ Не удалось обновить кнопки для менеджера {mgr_info['chat_id']}: {e}")
    
    except Exception as e:
        print(f"❌ Ошибка обновления кнопок менеджера: {e}")

@dp.callback_query(F.data == "send_final")
async def send_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data(); user_id = callback.from_user.id
    anketa_id = db_get_next_id(user_id); worker_name = db_check_worker(user_id); client_tag = data.get('client')
    
    # Проверяем режим множественного выбора
    multi_clients = data.get('multi_clients', [])
    is_multi = len(multi_clients) > 0
    
    # Проверяем, выбран ли клиент другого работника
    client_owner_id = data.get('client_owner_id', user_id)  # Используем ID владельца клиента
    
    if is_multi:
        # Множественная отправка
        await send_to_multiple_clients(callback, state, user_id, worker_name, anketa_id, data, multi_clients, client_owner_id)
    else:
        # Обычная отправка одному клиенту
        await send_to_single_client(callback, state, user_id, worker_name, anketa_id, data, client_tag, client_owner_id)

async def send_to_multiple_clients(callback, state, user_id, worker_name, anketa_id, data, multi_clients, client_owner_id):
    """Отправка анкеты нескольким клиентам"""
    start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔄 Новые часы")]], resize_keyboard=True)
    
    # Формируем список клиентов для отображения
    clients_display = ", ".join(multi_clients)
    
    await callback.message.answer(f"✅ <b>Отправляю анкету {len(multi_clients)} клиентам...</b>\n🆔 <b>ID: {anketa_id}</b>", reply_markup=start_kb, parse_mode="HTML")
    
    # Отправляем в каждый чат клиента
    for client_tag in multi_clients:
        # Получаем групповой чат для каждого клиента
        actual_chat_id = get_client_group_chat(client_owner_id, client_tag)
        
        public_text = (f"🟢 <b>Status: Available</b>\n\n👤 <b>{worker_name}</b>\nClient {client_tag}\n🆔 <b>ID: {anketa_id}</b>\nS{data.get('table')}\n💶 Price: €{data.get('price')}\n📉 Market Price (Chrono24): €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 Rating: {data.get('rating')}")
        
        try:
            await broadcast_to_channels(data.get("media_files"), public_text, f"{anketa_id}_{client_tag}", actual_chat_id)
            logging.info(f"✅ Отправлено {client_tag}")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки {client_tag}: {e}")
    
    # Отправляем менеджеру сводку
    manager_body = (f"🆔 <b>ID: {anketa_id}</b>\n👤 <b>От:</b> {worker_name}\n🏷 <b>Клиенты:</b> {clients_display}\nS{data.get('table')}\n📱 Seller: {data.get('seller_number')}\n💶 Price: €{data.get('price')}\n📉 Chrono: €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 <b>Rating:</b> {data.get('rating')}")
    manager_text_final = f"🟢 <b>Status: Available</b>\n\n{manager_body}\n\n📤 <b>Отправлено {len(multi_clients)} клиентам</b>"
    
    # Отправляем менеджерам
    try:
        mf = data.get("media_files"); mg = []
        for i in mf:
            if i['type'] == 'photo': mg.append(InputMediaPhoto(media=i['id'], parse_mode="HTML"))
            elif i['type'] == 'video': mg.append(InputMediaVideo(media=i['id'], parse_mode="HTML"))
        mg[0].caption = manager_text_final; mg[0].parse_mode = "HTML"
        
        for mgr_id in MANAGER_IDS:
            try:
                if len(mg) > 1:
                    await bot.send_media_group(mgr_id, media=mg)
                else:
                    if mf[0]['type'] == 'photo': 
                        await bot.send_photo(mgr_id, mf[0]['id'], caption=manager_text_final, parse_mode="HTML")
                    else: 
                        await bot.send_video(mgr_id, mf[0]['id'], caption=manager_text_final, parse_mode="HTML")
            except Exception as e: 
                print(f"Не удалось отправить менеджеру {mgr_id}: {e}")
    except Exception as e: 
        await callback.message.answer(f"❌ Ошибка отправки: {e}")
    
    db_save_full_order(user_id, worker_name, anketa_id, data)
    await state.clear()

async def send_to_single_client(callback, state, user_id, worker_name, anketa_id, data, client_tag, client_owner_id):
    """Отправка анкеты одному клиенту"""
    target_client_id = get_client_id(client_owner_id, client_tag)
    
    client_link_text = client_tag
    if target_client_id and isinstance(target_client_id, int):
        client_link_text = f'<a href="tg://user?id={target_client_id}">{client_tag}</a>'

    manager_body = (f"🆔 <b>ID: {anketa_id}</b>\n👤 <b>От:</b> {worker_name}\n🏷 <b>Клиент:</b> {client_link_text}\nS{data.get('table')}\n📱 Seller: {data.get('seller_number')}\n💶 Price: €{data.get('price')}\n📉 Chrono: €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 <b>Rating:</b> {data.get('rating')}")
    manager_text_final = f"🟢 <b>Status: Available</b>\n\n{manager_body}"

    public_text = (f"🟢 <b>Status: Available</b>\n\n👤 <b>{worker_name}</b>\nClient {client_tag}\n🆔 <b>ID: {anketa_id}</b>\nS{data.get('table')}\n💶 Price: €{data.get('price')}\n📉 Market Price (Chrono24): €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 Rating: {data.get('rating')}")
    clean_text = (f"👤 <b>{worker_name}</b>\nClient {client_tag}\n🆔 <b>ID: {anketa_id}</b>\nS{data.get('table')}\n💶 Price: €{data.get('price')}\n📉 Market Price (Chrono24): €{data.get('chrono_price')}\n🗣 Nego: {data.get('negotiation')}\n📅 Year: {data.get('year')}\n📏 Diam: {data.get('diameter')} mm\n🖐 Wrist: {data.get('wrist')} cm\n📦 Set: {data.get('kit')}\n⚙️ Cond: {data.get('condition')}\n\n👀 Rating: {data.get('rating')}")

    db_save_full_order(user_id, worker_name, anketa_id, data)
    lot_id = str(uuid.uuid4())[:8]
    
    start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔄 Новые часы")]], resize_keyboard=True)
    worker_msg = await callback.message.answer(f"✅ <b>Отправлено!</b>\n🆔 <b>ID: {anketa_id}</b>", reply_markup=start_kb, parse_mode="HTML")

    # Получаем групповой чат для этого клиента (используем владельца клиента)
    actual_chat_id = get_client_group_chat(client_owner_id, client_tag)
    
    _, chat_msg_id, chat_text_msg_id = await broadcast_to_channels(data.get("media_files"), public_text, lot_id, actual_chat_id)

    # ГЕНЕРАЦИЯ ССЫЛКИ НА ПОСТ В ГРУППЕ
    chat_link = None
    if actual_chat_id and chat_msg_id:
        clean_id = str(actual_chat_id).replace("-100", "").replace("-", "")
        chat_link = f"https://t.me/c/{clean_id}/{chat_msg_id}"

    # СБОРКА КНОПОК ДЛЯ МЕНЕДЖЕРА
    mgr_kb = InlineKeyboardBuilder()
    if target_client_id: 
        mgr_kb.button(text=f"🚀 Клиенту ({client_tag})", callback_data=f"sendto_client_{lot_id}")
    else: 
        mgr_kb.button(text="⚠️ Нет контакта", callback_data=f"clean_text_{lot_id}")
    
    # КНОПКА НА ПОСТ В ГРУППЕ
    if chat_link: 
        mgr_kb.button(text="💬 Пост в группе", url=chat_link)
    
    # КНОПКА НА КАНАЛ (будет обновлена после отправки поста)
    if TARGET_CHANNEL_ID != 0:
        mgr_kb.button(text="📢 Пост в канале ⏳", callback_data=f"wait_channel_{lot_id}")
    
    # КНОПКА НА ЧАТ С КЛИЕНТОМ
    if target_client_id and isinstance(target_client_id, int):
        mgr_kb.button(text="👤 Чат с клиентом", url=f"tg://user?id={target_client_id}")

    mgr_kb.button(text="📹 Запросить видео", callback_data=f"req_video_{lot_id}")
    mgr_kb.button(text="✅ БЕРУТ", callback_data=f"client_buy_{lot_id}")
    mgr_kb.button(text="❌ Отказ", callback_data=f"reject_{lot_id}")
    mgr_kb.button(text="💬 Коммент", callback_data=f"feedback_start_{lot_id}")
    
    mgr_kb.row(
        InlineKeyboardButton(text="🟡 Rsrv", callback_data=f"set_status_reserved_{lot_id}"),
        InlineKeyboardButton(text="🟢 Avail", callback_data=f"set_status_available_{lot_id}"),
        InlineKeyboardButton(text="🔴 Sold", callback_data=f"set_status_sold_{lot_id}")
    )
    
    # ОТПРАВКА МЕНЕДЖЕРАМ
    manager_msgs_info = []
    try:
        mf = data.get("media_files"); mg = []
        for i in mf:
            if i['type'] == 'photo': mg.append(InputMediaPhoto(media=i['id'], parse_mode="HTML"))
            elif i['type'] == 'video': mg.append(InputMediaVideo(media=i['id'], parse_mode="HTML"))
        mg[0].caption = manager_text_final; mg[0].parse_mode = "HTML"
        
        for mgr_id in MANAGER_IDS:
            try:
                msg_id = None
                if len(mg) > 1:
                    msgs = await bot.send_media_group(mgr_id, media=mg)
                    await bot.send_message(mgr_id, "Действия:", reply_markup=mgr_kb.as_markup())
                    msg_id = msgs[0].message_id
                else:
                    if mf[0]['type'] == 'photo': msg = await bot.send_photo(mgr_id, mf[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    else: msg = await bot.send_video(mgr_id, mf[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    msg_id = msg.message_id
                
                if msg_id:
                    manager_msgs_info.append({'chat_id': mgr_id, 'msg_id': msg_id})
            except Exception as e: print(f"Не удалось отправить менеджеру {mgr_id}: {e}")
            
    except Exception as e: await callback.message.answer(f"❌ Ошибка отправки: {e}")

    LOTS_CACHE[lot_id] = {
        "media_files": data.get("media_files"),
        "clean_text": clean_text,
        "manager_body": manager_body,
        "user_id": user_id,
        "target_client_id": target_client_id,
        "client_tag": client_tag,
        "worker_msg_id": worker_msg.message_id,
        "worker_name": worker_name,
        "channel_msg_id": None,
        "channel_text_msg_id": None,
        "chat_msg_id": chat_msg_id,
        "chat_text_msg_id": chat_text_msg_id,
        "manager_msgs": manager_msgs_info
    }

    await state.clear()

# --- СМЕНА СТАТУСА ---
@dp.callback_query(F.data.startswith("set_status_"))
@dp.callback_query(F.data.startswith("ch_status_"))
async def change_status_unified(callback: types.CallbackQuery):
    is_admin = callback.from_user.id in MANAGER_IDS or callback.from_user.id in STATUS_MODERATORS
    if not is_admin: return await callback.answer("⛔️ Только менеджер может менять статус.", show_alert=True)

    parts = callback.data.split("_")
    new_status = parts[2]; lot_id = parts[3]
    lot_data = LOTS_CACHE.get(lot_id)
    if not lot_data: return await callback.answer("Лот устарел", show_alert=True)
    
    if new_status == "reserved": header = "🟡 <b>Status: Reserved (Search Client)</b>"
    elif new_status == "sold": header = "🔴 <b>Status: SOLD</b>"
    else: header = "🟢 <b>Status: Available</b>"
    
    public_body = lot_data['clean_text']
    final_public_text = f"{header}\n\n{public_body}"

    manager_body = lot_data.get('manager_body', public_body)
    final_manager_text = f"{header}\n\n{manager_body}"
    
    try:
        anketa_id = public_body.split('\n')[0].replace("🆔 <b>ID: ", "").replace("</b>", "").strip()
        db_update_status(anketa_id, new_status)
    except: pass

    # Канал (витрина) - не обновляем статус, т.к. это может вызвать проблемы с альбомами
    # Статус виден только в групповом чате и у менеджеров

    # Обновляем чат/группу
    # Получаем групповой чат для клиента
    worker_id = lot_data.get('user_id')
    client_tag = lot_data.get('client_tag')
    target_chat = get_client_group_chat(worker_id, client_tag) if worker_id and client_tag else lot_data['target_client_id']
    chat_msg_id = lot_data.get('chat_msg_id')
    chat_text_msg_id = lot_data.get('chat_text_msg_id')
    
    if target_chat and isinstance(target_chat, int) and target_chat < 0:
        # Если есть отдельное текстовое сообщение (медиагруппа), обновляем его
        if chat_text_msg_id:
            try:
                await bot.edit_message_text(chat_id=target_chat, message_id=chat_text_msg_id, text=final_public_text, reply_markup=get_channel_status_kb(lot_id), parse_mode="HTML")
            except Exception as e:
                print(f"❌ Ошибка обновления текста чата: {e}")
        # Если нет отдельного текста, обновляем caption медиа
        elif chat_msg_id:
            try:
                await bot.edit_message_caption(chat_id=target_chat, message_id=chat_msg_id, caption=final_public_text, reply_markup=get_channel_status_kb(lot_id), parse_mode="HTML")
            except Exception as e:
                print(f"❌ Ошибка обновления caption чата: {e}")

    # Пересоздаем клавиатуру менеджера с актуальными кнопками
    target_client_id = lot_data.get('target_client_id')
    client_tag = lot_data.get('client_tag', 'Клиент')
    worker_id = lot_data.get('user_id')
    
    # Получаем ссылку на пост в группе
    chat_msg_id = lot_data.get('chat_msg_id')
    actual_chat_id = get_client_group_chat(worker_id, client_tag) if worker_id and client_tag else target_client_id
    chat_link = None
    if actual_chat_id and chat_msg_id:
        clean_id = str(actual_chat_id).replace("-100", "").replace("-", "")
        chat_link = f"https://t.me/c/{clean_id}/{chat_msg_id}"
    
    mgr_kb = InlineKeyboardBuilder()
    if target_client_id: 
        mgr_kb.button(text=f"🚀 Клиенту ({client_tag})", callback_data=f"sendto_client_{lot_id}")
    else: 
        mgr_kb.button(text="⚠️ Нет контакта", callback_data=f"clean_text_{lot_id}")
    
    if chat_link: mgr_kb.button(text="🔗 Пост в группе", url=chat_link)
    
    if target_client_id and isinstance(target_client_id, int):
        mgr_kb.button(text="💬 Чат с клиентом", url=f"tg://user?id={target_client_id}")

    mgr_kb.button(text="📹 Запросить видео", callback_data=f"req_video_{lot_id}")
    mgr_kb.button(text="✅ БЕРУТ", callback_data=f"client_buy_{lot_id}")
    mgr_kb.button(text="❌ Отказ", callback_data=f"reject_{lot_id}")
    mgr_kb.button(text="💬 Коммент", callback_data=f"feedback_start_{lot_id}")
    
    mgr_kb.row(
        InlineKeyboardButton(text="🟡 Rsrv", callback_data=f"set_status_reserved_{lot_id}"),
        InlineKeyboardButton(text="🟢 Avail", callback_data=f"set_status_available_{lot_id}"),
        InlineKeyboardButton(text="🔴 Sold", callback_data=f"set_status_sold_{lot_id}")
    )
    
    for mgr_info in lot_data.get('manager_msgs', []):
        try:
            await bot.edit_message_caption(chat_id=mgr_info['chat_id'], message_id=mgr_info['msg_id'], caption=final_manager_text, parse_mode="HTML", reply_markup=mgr_kb.as_markup())
        except Exception as e: 
            print(f"Update manager error: {e}")

    await callback.answer(f"Статус изменен на {new_status.upper()}")

# --- ХЕНДЛЕРЫ МЕНЕДЖЕРА ---
@dp.callback_query(F.data.startswith("sendto_client_"))
async def manager_send_to_client(c: types.CallbackQuery):
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid)
    if not ld: return await c.answer("Лот устарел", show_alert=True)
    t = ld.get('target_client_id')
    if not t: return await c.answer("Нет контакта", show_alert=True)
    await c.answer("⏳..."); f = []; 
    for i in ld['media_files']:
        ext = "mp4" if i['type'] == 'video' else "jpg"
        fi = await bot.get_file(i['id']); buf = io.BytesIO(); await bot.download_file(fi.file_path, buf); buf.seek(0); buf.name=f"f.{ext}"; f.append(buf)
    
    try:
        if f: await user_client.send_file(t, f, caption=ld['clean_text'], parse_mode='html')
        else: await user_client.send_message(t, ld['clean_text'], parse_mode='html')
        
        success_kb = InlineKeyboardBuilder()
        success_kb.button(text="💬 Открыть чат с клиентом", url=f"tg://user?id={t}")
        await c.message.answer("✅ Улетело клиенту!", reply_markup=success_kb.as_markup())
        
    except Exception as e:
        await c.message.answer(f"❌ Ошибка отправки: {e}")

@dp.callback_query(F.data.startswith("req_video_"))
async def req_video(c: types.CallbackQuery):
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid)
    if ld:
        kb = InlineKeyboardBuilder(); kb.button(text="📤 Отправить видео", callback_data=f"give_video_{lid}")
        await bot.send_message(ld['user_id'], "📹 <b>Запрос видео от менеджера!</b>", reply_markup=kb.as_markup(), parse_mode="HTML", reply_to_message_id=ld.get('worker_msg_id'))
        await c.answer("Запрос отправлен")

@dp.callback_query(F.data.startswith("give_video_"))
async def give_video_start(c: types.CallbackQuery, state: FSMContext): await state.update_data(vid_lid=c.data.split("_")[2]); await state.set_state(EmployeeState.uploading_requested_video); await c.message.answer("📹 Пришли видео:"); await c.answer()

@dp.message(EmployeeState.uploading_requested_video, F.video)
async def give_video_fin(m: types.Message, state: FSMContext):
    d = await state.get_data(); lid = d.get("vid_lid"); ld = LOTS_CACHE.get(lid)
    if ld:
        # Извлекаем только ID анкеты
        clean_text = ld.get('clean_text', '')
        anketa_id = clean_text.split('\n')[0] if clean_text else "ID не найден"
        caption_text = f"📹 <b>ВИДЕО!</b> {anketa_id}"
        
        mkb = InlineKeyboardBuilder(); mkb.button(text="🚀 Клиенту", callback_data=f"fwd_vid_{lid}"); mkb.adjust(1)
        
        # Отправляем видео каждому менеджеру как ответ на его анкету
        manager_msgs = ld.get('manager_msgs', [])
        for mgr_info in manager_msgs:
            try:
                mgr_id = mgr_info['chat_id']
                mgr_msg_id = mgr_info['msg_id']
                # Отправляем видео как ответ на сообщение с анкетой
                await bot.send_video(mgr_id, m.video.file_id, caption=caption_text, reply_markup=mkb.as_markup(), parse_mode="HTML", reply_to_message_id=mgr_msg_id)
            except Exception as e:
                print(f"❌ Ошибка отправки видео менеджеру {mgr_info.get('chat_id')}: {e}")
        
        await m.answer("✅ Отправлено")
    await state.clear()

@dp.callback_query(F.data.startswith("fwd_vid_"))
async def fwd_vid(c: types.CallbackQuery):
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid); t = ld.get('target_client_id')
    if not t: return await c.answer("No contact")
    await c.answer("⏳..."); f = await bot.get_file(c.message.video.file_id); buf = io.BytesIO(); await bot.download_file(f.file_path, buf); buf.seek(0); buf.name="v.mp4"
    
    try:
        await user_client.send_file(t, buf, caption="📹")
        success_kb = InlineKeyboardBuilder()
        success_kb.button(text="💬 Открыть чат с клиентом", url=f"tg://user?id={t}")
        await c.message.answer("✅ Видео у клиента!", reply_markup=success_kb.as_markup())
    except Exception as e:
        await c.message.answer(f"❌ Ошибка: {e}")

@dp.callback_query(F.data.startswith("client_buy_"))
async def buy(c: types.CallbackQuery):
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid)
    if ld: await bot.send_message(ld['user_id'], "✅💰 <b>БЕРУТ!</b>", parse_mode="HTML", reply_to_message_id=ld.get('worker_msg_id')); await c.answer("Ok")

@dp.callback_query(F.data.startswith("reject_"))
async def reject(c: types.CallbackQuery):
    lid = c.data.split("_")[1]; ld = LOTS_CACHE.get(lid)
    if ld: await bot.send_message(ld['user_id'], f"❌ <b>Отказ:</b>", parse_mode="HTML", reply_to_message_id=ld.get('worker_msg_id')); await c.message.answer("❌ Отказано")

@dp.callback_query(F.data.startswith("feedback_start_"))
async def feed_start(c: types.CallbackQuery, state: FSMContext):
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid)
    if ld: await state.update_data(feed_uid=ld['user_id'], feed_reply_id=ld.get('worker_msg_id')); await state.set_state(ManagerState.waiting_for_feedback); await c.message.answer(f"✍️ Коммент для <b>{ld.get('worker_name')}</b>:", parse_mode="HTML", reply_markup=make_kb([], back=True, skip=False)); await c.answer()

@dp.message(ManagerState.waiting_for_feedback)
async def feed_send(m: types.Message, state: FSMContext):
    if m.text == "🔙 Назад": await state.clear(); await show_manager_main_menu(m); return
    d = await state.get_data(); uid = d.get("feed_uid"); rid = d.get("feed_reply_id")
    if uid: await bot.send_message(uid, f"💬 <b>Менеджер:</b>\n{m.text}", parse_mode="HTML", reply_to_message_id=rid); await m.answer("✅")
    await state.clear(); await show_manager_main_menu(m)

# ЛОГИКА СОТРУДНИКОВ (МЕНЕДЖЕР)
@dp.message(F.text == "👥 Сотрудники")
async def m_team(m: types.Message, state: FSMContext):
    if m.from_user.id not in MANAGER_IDS: return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT name FROM workers"); rows = c.fetchall(); conn.close()
    kb = make_kb([r[0] for r in rows], rows=2, back=True, skip=False)
    await state.set_state(ManagerState.choosing_employee_to_write); await m.answer("👥 Кому?", reply_markup=kb)

@dp.message(ManagerState.choosing_employee_to_write)
async def m_pick(m: types.Message, state: FSMContext):
    if m.text == "🔙 Назад": await state.clear(); await show_manager_main_menu(m); return
    conn = sqlite3.connect(DB_FILE); c = conn.cursor(); c.execute("SELECT user_id, name FROM workers WHERE name = ?", (m.text,)); d = c.fetchone(); conn.close()
    if d: await state.update_data(wid=d[0], wname=d[1]); await state.set_state(ManagerState.writing_to_employee); await m.answer(f"✍️ Сообщение для <b>{d[1]}</b>:", reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
    else: await m.answer("⚠️ Сотрудник не найден.")

@dp.message(ManagerState.writing_to_employee)
async def m_send(m: types.Message, state: FSMContext):
    d = await state.get_data(); tid = d.get("wid")
    if tid: await bot.send_message(tid, f"🔔 <b>Менеджер:</b>\n{m.text}", parse_mode="HTML"); await m.answer(f"✅ Отправлено {d.get('wname')}")
    await state.clear(); await show_manager_main_menu(m)

@dp.message(F.text == "🔄 Новые часы", StateFilter('*'))
async def new_cycle(m: types.Message, state: FSMContext): await restart_logic(m, state)

async def main():
    init_db() # АВТО-ЗАПУСК СОЗДАНИЯ ТАБЛИЦ
    print("🚀 Бот запущен (Версия 103: Fixed Links & Buttons) ...")
    await user_client.start(); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())