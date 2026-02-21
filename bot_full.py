import asyncio
import logging
import uuid
import os
import io
import json
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
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "-1003745353210"))

# ГРУППА ДЛЯ АВТО-ПОСТИНГА VIP
VIP_GROUP_ID = int(os.getenv("VIP_GROUP_ID", "0"))

# ЧАТ ПО УМОЛЧАНИЮ
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))

# ⏱ ЗАДЕРЖКА ПУБЛИКАЦИИ В КАНАЛ (СЕКУНДЫ)
CHANNEL_POST_DELAY = int(os.getenv("CHANNEL_POST_DELAY", "120"))

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# ⚠️ НАСТРОЙКИ КЛИЕНТОВ
EMPLOYEES_CONFIG = {
    12313213131321: { 
        "clients": {
            "#Test": {"group_chat_id": -5069461222},
            "#1": {"group_chat_id": -5069461222},
            "#2": {"group_chat_id": -5069461222},
            "#3": {"group_chat_id": -5069461222},
            "#4": {"group_chat_id": -5069461222},
            "#5": {"group_chat_id": -5069461222},
            "#6": {"group_chat_id": -5069461222},
            "#7": {"group_chat_id": -5069461222},
            "#8": {"group_chat_id": -5069461222},
            "#9": {"group_chat_id": -5069461222},
            "#10": {"group_chat_id": -5069461222},
            "#11": {"group_chat_id": -5069461222},
            "#12": {"group_chat_id": -5069461222},
            "#13": {"group_chat_id": -5069461222},
            "#14": {"group_chat_id": -5069461222},
            "#15": {"group_chat_id": -5069461222},
            "#16": {"group_chat_id": -5069461222},
            "#17": {"group_chat_id": -5069461222},
            "#18": {"group_chat_id": -5069461222},
            "#19": {"group_chat_id": -5069461222},
            "#20": {"group_chat_id": -5069461222}
        } 
    },
    610220736: { 
        "clients": { 
            "#1": {"group_chat_id": -5182586637},
            "#2": {"group_chat_id": -5105834721},
            "#3": {"group_chat_id": -5029226279},
            "#4": {"group_chat_id": -5069461222},
            "#5": {"group_chat_id": -5069461222},
            "#6": {"group_chat_id": -5069461222},
            "#7": {"group_chat_id": -5069461222},
            "#8": {"group_chat_id": -5069461222},
            "#9": {"group_chat_id": -5069461222},
            "#10": {"group_chat_id": -5069461222},
            "#11": {"group_chat_id": -5069461222},
            "#12": {"group_chat_id": -5069461222},
            "#13": {"group_chat_id": -5069461222},
            "#14": {"group_chat_id": -5069461222},
            "#15": {"group_chat_id": -5069461222},
            "#16": {"group_chat_id": -5069461222},
            "#17": {"group_chat_id": -5069461222},
            "#18": {"group_chat_id": -5069461222},
            "#19": {"group_chat_id": -5069461222},
            "#20": {"group_chat_id": -5069461222},
            "#136": {"group_chat_id": -5295466035}
        } 
    },
    645070075: {  # Vladyslav
        "clients": {
            "#50": {"group_chat_id": -5290089216},
            "#51": {"group_chat_id": -5273767727},
            "#69": {"group_chat_id": -5191676311},
            "#96": {"group_chat_id": -5238109092},
            "#101": {"group_chat_id": -5291170403},
            "#104": {"group_chat_id": -5237170604},
            "#116": {"group_chat_id": -5174599310},
            "#117": {"group_chat_id": -5105853553},
            "#125": {"group_chat_id": -5156346053},
            "Toy9": {"group_chat_id": -5296775849},
            "Toy17": {"group_chat_id": -4995762095},
            "Toy23": {"group_chat_id": -5142004346},
            "Toy40": {"group_chat_id": -5229699686}
        } 
    },
    625971673: {  # Виталий
        "clients": {
            "#79": {"group_chat_id": -5148667064},
            "#85": {"group_chat_id": -5016013600},
            "#87": {"group_chat_id": -5171048824},
            "#93": {"group_chat_id": -5006054596},
            "#97": {"group_chat_id": -5148348191},
            "#99": {"group_chat_id": -5033105513},
            "#107": {"group_chat_id": -5180230828},
            "#111": {"group_chat_id": -5176219649},
            "#120": {"group_chat_id": -5275969573},
            "#124": {"group_chat_id": -5121925059},
            "#136": {"group_chat_id": -5075946318},
            "Toy14": {"group_chat_id": -5126299598},
            "Toy20": {"group_chat_id": -5250147547},
            "Toy26": {"group_chat_id": -5256884020},
            "Toy27": {"group_chat_id": -5251521211},
            "Toy29": {"group_chat_id": -4999840936},
            "Toy30": {"group_chat_id": -5268553476},
            "Toy31": {"group_chat_id": -5239027986},
            "Toy34": {"group_chat_id": -5278523032},
            "Toy36": {"group_chat_id": -5251959514},
            "Toy38": {"group_chat_id": -5200145003},
            "Toy47": {"group_chat_id": -5249359726}
        }
    },
    5442618444: {  # Миша K
        "clients": {
            "#74": {"group_chat_id": -5155293679},
            "#75": {"group_chat_id": -5289378718},
            "#76": {"group_chat_id": -5289378718},
            "#78": {"group_chat_id": -5069461222},
            "#91": {"group_chat_id": -5094267136},
            "#94": {"group_chat_id": -5217474814},
            "#98": {"group_chat_id": -4968185056},
            "#100": {"group_chat_id": -5135458325},
            "#110": {"group_chat_id": -5157805999},
            "#115": {"group_chat_id": -5127025704},
            "#118": {"group_chat_id": -5188694886},
            "#119": {"group_chat_id": -5170362817},
            "#122": {"group_chat_id": -5256550803},
            "#123": {"group_chat_id": -5273847484},
            "#127": {"group_chat_id": -5113224392}, 
            "Toy8": {"group_chat_id": -5143325351},
            "Toy16": {"group_chat_id": -5171972901},
            "Toy21": {"group_chat_id": -5291979002},
            "Toy25": {"group_chat_id": -5141761162},
            "Toy32": {"group_chat_id": -5207210520},
            "Toy41": {"group_chat_id": -5163315891},
            "Toy44": {"group_chat_id": -5086915437},
            "Toy45": {"group_chat_id": -5150643117},
            "Toy46": {"group_chat_id": -5173644458}
        }
    },
    419890021: {  # Олег
        "clients": {
            "Lex1": {"group_chat_id": -5104534927},
            "Lex2": {"group_chat_id": -5257148446},
            "Lex3": {"group_chat_id": -5100666271},
            "Lex4": {"group_chat_id": -5287711922},
            "Lex5": {"group_chat_id": -5104534927},
            "Lex6": {"group_chat_id": -5112242325},
            "Lex7": {"group_chat_id": -5279607641},
            "Lex10": {"group_chat_id": -5204094110},
            "Lex11": {"group_chat_id": -5083040356},
            "Lex12": {"group_chat_id": -5251934001},
            "Lex18": {"group_chat_id": -5226630032},
            "Lex19": {"group_chat_id": -5254977860},
            "Lex28": {"group_chat_id": -5269767297},
            "Lex33": {"group_chat_id": -5121071814},
            "Lex35": {"group_chat_id": -5290079522},
            "Lex37": {"group_chat_id": -4999921873},
            "Lex39": {"group_chat_id": -5251934001},
            "Lex43": {"group_chat_id": -5132901747},
            "Lex48": {"group_chat_id": -5259988260},
            "#103": {"group_chat_id": -5233036184},
            "#108": {"group_chat_id": -5026852971},
            "#112": {"group_chat_id": -5162450800}
        }
    },
    6776561610: {  # Misha M (2)
        "clients": {
            "#23": {"group_chat_id": -5104162767},
            "#51": {"group_chat_id": -5001283164},
            "#54": {"group_chat_id": -5213680626},
            "#58": {"group_chat_id": -5227727762},
            "#61": {"group_chat_id": -5293857124},
            "#67": {"group_chat_id": -5142489904},
            "#68": {"group_chat_id": -5116629011},
            "#71": {"group_chat_id": -5187405414},
            "#82": {"group_chat_id": -5041021255},
            "#88": {"group_chat_id": -5126814623},
            "#89": {"group_chat_id": -5234126541},
            "#91": {"group_chat_id": -5094267136},
            "#95": {"group_chat_id": -5204603957},
            "#102": {"group_chat_id": -5141670241},
            "#105": {"group_chat_id": -5280848104},
            "#106": {"group_chat_id": -5086400568},
            "#114": {"group_chat_id": -4882418624},
            "#117": {"group_chat_id": -5105853553},
            "#121": {"group_chat_id": -5221766017},
            "#126": {"group_chat_id": -4758469868},
            "#128": {"group_chat_id": -5250840602},
            "#204": {"group_chat_id": -4993033356},
            "Lex37": {"group_chat_id": -4999921873},
            "Toy42": {"group_chat_id": -5299629678}
        }
    }
}

DB_FILE = 'bot_database.db'
LOTS_CACHE_FILE = 'lots_cache.json'
LOTS_CACHE = {}
INVITE_LINK_CACHE = {}  # chat_id -> invite_link (кэш инвайт-ссылок)

def save_lots_cache():
    """Сохраняет LOTS_CACHE в JSON файл"""
    try:
        with open(LOTS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(LOTS_CACHE, f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ошибка сохранения LOTS_CACHE: {e}")

def load_lots_cache():
    """Загружает LOTS_CACHE из JSON файла"""
    global LOTS_CACHE
    try:
        if os.path.exists(LOTS_CACHE_FILE):
            with open(LOTS_CACHE_FILE, 'r', encoding='utf-8') as f:
                LOTS_CACHE = json.load(f)
            logging.info(f"Загружено {len(LOTS_CACHE)} лотов из кэша")
    except Exception as e:
        logging.error(f"Ошибка загрузки LOTS_CACHE: {e}")
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
            manager_comment TEXT, table_num TEXT, price TEXT, 
            chrono_price TEXT, negotiation TEXT, year TEXT, diameter TEXT, 
            wrist TEXT, kit TEXT, condition TEXT, material TEXT, rating TEXT, status TEXT DEFAULT 'Available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # Миграции: добавляем новые колонки если их нет
    for col in ["material TEXT", "manager_comment TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {col}")
        except:
            pass  # колонка уже существует
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
        6776561610: "MM",     # Misha M (2)
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
                worker_id, worker_name, anketa_id, client_tag, manager_comment, 
                table_num, price, chrono_price, negotiation, year, diameter, wrist, kit, 
                condition, material, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            user_id, worker_name, anketa_id, data.get('client'), data.get('manager_comment'),
            data.get('table'), data.get('price'),
            data.get('chrono_price'), data.get('negotiation'), data.get('year'),
            data.get('diameter'), data.get('wrist'), data.get('kit'),
            data.get('condition'), data.get('material'), data.get('rating')
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
    entering_material = State()
    entering_manager_comment = State() 
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

async def make_chat_link(chat_id, msg_id=None):
    """Генерирует ссылку на групповой чат Telegram (Android + iOS)"""
    if not chat_id:
        return None
    cid = str(chat_id)
    # Супергруппа (ID начинается с -100) → t.me/c/ ссылки работают
    if cid.startswith("-100"):
        clean = cid[4:]
        if msg_id:
            return f"tg://privatepost?channel={clean}&post={msg_id}"
        return f"https://t.me/c/{clean}"
    # Обычная группа → нужен invite link
    try:
        if chat_id in INVITE_LINK_CACHE:
            return INVITE_LINK_CACHE[chat_id]
        link = await bot.export_chat_invite_link(chat_id)
        INVITE_LINK_CACHE[chat_id] = link
        logging.info(f"🔗 Invite link для {chat_id}: {link}")
        return link
    except Exception as e:
        logging.warning(f"⚠️ Не удалось создать invite link для {chat_id}: {e}")
        # Фоллбэк — t.me/c/ (может не работать для обычных групп)
        clean = cid.lstrip("-")
        if msg_id:
            return f"tg://privatepost?channel={clean}&post={msg_id}"
        return f"https://t.me/c/{clean}"

def format_client_table(tag, table):
    """Форматирует клиент-стол, скрывая стол если пропущен"""
    if table and str(table) != '—':
        return f"{tag}-{table}"
    return str(tag)

def build_anketa_fields(data, chrono_label="Chrono", include_manager=False, include_rating=True, bold_rating=False):
    """Построение полей анкеты — пропускает поля со значением '—'"""
    lines = []
    if include_manager:
        v = data.get('manager_comment', '—')
        if v and v != '—':
            lines.append(f"💬 Manager: {v}")
    for label, val, prefix, suffix in [
        ("💶 Price", data.get('price'), "€", ""),
        (f"📉 {chrono_label}", data.get('chrono_price'), "€", ""),
        ("💰 Discount", data.get('negotiation'), "", ""),
        ("📅 Year", data.get('year'), "", ""),
        ("📏 Diam", data.get('diameter'), "", " mm"),
        ("🖐 Wrist", data.get('wrist'), "", " cm"),
        ("📦 Set", data.get('kit'), "", ""),
        ("⚙️ Cond", data.get('condition'), "", ""),
        ("🪨 Material", data.get('material', '—'), "", ""),
    ]:
        if val and str(val) != '—':
            lines.append(f"{label}: {prefix}{val}{suffix}")
    if include_rating:
        v = data.get('rating', '—')
        if v and v != '—':
            if bold_rating:
                lines.append(f"\n👀 <b>Rating:</b> {v}")
            else:
                lines.append(f"\n👀 Rating: {v}")
    return '\n'.join(lines)

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
    
    # Добавляем кнопку для множественного выбора + канал
    clients_list.append("📢 Канал")
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
    
    if message.text == "📢 Канал":
        logging.info("▶ Режим отправки только в канал")
        await state.update_data(client="📢 Channel", channel_only=True)
        return await check_edit_or_next(message, state, show_media_menu)
    
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
    # Убираем предыдущую reply-клавиатуру
    rm_msg = await message.answer("⌨️", reply_markup=ReplyKeyboardRemove())
    await rm_msg.delete()
    calc_msg = await message.answer(f"{title}\n\n💡 <i>Введите число с клавиатуры</i>", reply_markup=get_calc_control_buttons(show_skip=allow_skip), parse_mode="HTML")
    await state.update_data(calc_title=title, calc_allow_skip=allow_skip, calc_msg_id=calc_msg.message_id)

# Обработчик кнопок управления калькулятором
@dp.callback_query(F.data.startswith("calc_"), StateFilter(Form.entering_table, Form.entering_price, Form.entering_chrono_price, Form.manual_year, Form.manual_diameter, Form.manual_wrist))
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
            if curr_state == Form.entering_table: await show_media_menu(callback.message)
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
        
        if curr_state == Form.entering_table:
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
@dp.message(StateFilter(Form.entering_table, Form.entering_price, Form.entering_chrono_price, Form.manual_year, Form.manual_diameter, Form.manual_wrist))
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
    
    if curr_state == Form.entering_table:
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
    kb = make_kb(["✅ Да", "❌ Нет"], rows=2, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id)
    await fsm.set_state(Form.choosing_negotiation); await bot.send_message(message.chat.id, "6️⃣ <b>Скидка:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_negotiation)
async def process_negotiation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await start_calculator(message, state, Form.entering_chrono_price, "5️⃣ <b>Цена CHRONO24:</b>", allow_skip=True)
    val = message.text
    if message.text == "⏩ Пропустить": val = "—"
    elif message.text == "✅ Да": val = "Yes"
    elif message.text == "❌ Нет": val = "No"
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
    kb = make_kb(["🆕 Новые", "💎 Отличное", "👌 Хорошее", "📦 Удовлетворительное", "💀 Плохое"], rows=2, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_condition); await bot.send_message(message.chat.id, "1️⃣1️⃣ <b>Состояние:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_condition)
async def process_condition(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_kit_menu(message)
    val = message.text
    if message.text == "⏩ Пропустить": val = "—"
    elif message.text == "🆕 Новые": val = "New"
    elif message.text == "💎 Отличное": val = "Excellent"
    elif message.text == "👌 Хорошее": val = "Good"
    elif message.text == "📦 Удовлетворительное": val = "satisfactory"
    elif message.text == "💀 Плохое": val = "Poor"
    await state.update_data(condition=val); await check_edit_or_next(message, state, ask_material)

async def ask_material(message):
    kb = make_kb([], rows=1, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.entering_material); await bot.send_message(message.chat.id, "🪨 <b>Материал (Material):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.entering_material)
async def process_material(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        data = await state.get_data()
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await show_condition_menu(message)
    val = "—" if message.text == "⏩ Пропустить" else message.text
    await state.update_data(material=val); await check_edit_or_next(message, state, ask_manager_comment)

async def ask_manager_comment(message):
    kb = make_kb([], rows=1, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.entering_manager_comment); await bot.send_message(message.chat.id, "💬 <b>Комментарий менеджера (Manager comment):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.entering_manager_comment)
async def process_manager_comment(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        data = await state.get_data()
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await ask_material(message)
    val = "—" if message.text == "⏩ Пропустить" else message.text
    await state.update_data(manager_comment=val); await check_edit_or_next(message, state, show_worker_rating_menu)

async def show_worker_rating_menu(message):
    kb = make_kb(["✅ Рекомендую", "👌 Нормально", "❌ Не рекомендую"], rows=3, back=True, skip=True)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.choosing_worker_rating); await bot.send_message(message.chat.id, "1️⃣2️⃣ <b>Твоя оценка (для менеджера):</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Form.choosing_worker_rating)
async def process_rating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "🔙 Назад":
        if data.get("editing_mode"):
            return await show_final_review(message, state)
        return await ask_manager_comment(message)
    val = message.text
    if message.text == "⏩ Пропустить": val = "—"
    elif message.text == "✅ Рекомендую": val = "✅ Recommended"
    elif message.text == "👌 Нормально": val = "👌 OK"
    elif message.text == "❌ Не рекомендую": val = "❌ Not recommended"
    await state.update_data(rating=val); await show_final_review(message, state)

# ==========================================
# 8. ПРОВЕРКА И ОТПРАВКА
# ==========================================

async def show_final_review(message: types.Message, state: FSMContext):
    await state.update_data(editing_mode=False)
    fsm = dp.fsm.get_context(bot, message.chat.id, message.chat.id); await fsm.set_state(Form.final_review); data = await state.get_data()
    ct = format_client_table(data.get('client'), data.get('table'))
    fields = build_anketa_fields(data, chrono_label="Chrono", include_manager=True, include_rating=True, bold_rating=True)
    text = f"📋 <b>ПРОВЕРКА (Вид для клиента):</b>\n\n👤 Client: {ct}\n{fields}"
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить", callback_data="open_edit_menu")
    if data.get('channel_only'):
        builder.button(text="📢 ОТПРАВИТЬ В КАНАЛ", callback_data="send_final")
        builder.adjust(1)
    else:
        builder.button(text="📢 В КАНАЛ И ГРУППУ", callback_data="send_final")
        builder.button(text="💬 ТОЛЬКО В ГРУППУ", callback_data="send_group_only")
        builder.adjust(1, 2)
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
    b.button(text="⚙️ Cond", callback_data="edit_cond"); b.button(text="🪨 Material", callback_data="edit_material")
    b.button(text="💬 Manager", callback_data="edit_mgrcomment"); b.button(text="👀 Rating", callback_data="edit_rating")
    b.button(text="🔙 Назад", callback_data="back_to_review")
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
    elif field == "material": await ask_material(c.message)
    elif field == "mgrcomment": await ask_manager_comment(c.message)
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

async def broadcast_to_channels_chat_only(media_files, text, specific_chat_id, lot_id=""):
    """Отправляет пост только в конкретный чат (без канала)"""
    channel_buttons = get_channel_status_kb(lot_id)
    chat_msg_id = None
    chat_text_msg_id = None
    
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
                chat_text_msg_id = text_msg.message_id
            else:
                # Одно медиа: подпись с кнопками
                msg = None
                if media_files[0]['type'] == 'photo': msg = await bot.send_photo(target, media_files[0]['id'], caption=text, reply_markup=channel_buttons, parse_mode="HTML")
                else: msg = await bot.send_video(target, media_files[0]['id'], caption=text, reply_markup=channel_buttons, parse_mode="HTML")
                chat_msg_id = msg.message_id
        except Exception as e:
            print(f"❌ Ошибка чата {target}: {e}")
            
    return None, chat_msg_id, chat_text_msg_id

async def broadcast_to_channels(media_files, text, lot_id, specific_chat_id, skip_channel=False):
    """Отправляет пост в Канал (отложенно) и В КОНКРЕТНЫЙ ЧАТ (сразу)"""
    channel_buttons = get_channel_status_kb(lot_id)
    chat_msg_id = None
    chat_text_msg_id = None
    
    # 1. ОТЛОЖЕННАЯ ОТПРАВКА В ОБЩИЙ КАНАЛ
    if TARGET_CHANNEL_ID != 0 and not skip_channel:
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
            # Сохраняем ID ПОСЛЕДНЕГО сообщения (где caption)
            msg_id = msgs[-1].message_id
            logging.info(f"📤 Отправлен альбом в канал: {len(msgs)} фото, последнее ID={msg_id}")
        else:
            # Одно медиа: подпись БЕЗ кнопок
            if media_files[0]['type'] == 'photo': 
                msg = await bot.send_photo(chat_id, media_files[0]['id'], caption=text, parse_mode="HTML")
            else: 
                msg = await bot.send_video(chat_id, media_files[0]['id'], caption=text, parse_mode="HTML")
            msg_id = msg.message_id
            logging.info(f"📤 Отправлено одно фото в канал: ID={msg_id}")
        
        # Обновляем кэш
        if lot_id in LOTS_CACHE:
            LOTS_CACHE[lot_id]['channel_msg_id'] = msg_id
            LOTS_CACHE[lot_id]['channel_text_msg_id'] = None  # Больше нет отдельного текста
            save_lots_cache()
            logging.info(f"💾 Сохранен channel_msg_id={msg_id} для lot_id={lot_id}")
            
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
        chat_link = await make_chat_link(actual_chat_id, chat_msg_id)
    
        # Пересоздаем кнопки
        mgr_kb = InlineKeyboardBuilder()
        
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

@dp.callback_query(F.data.in_({"send_final", "send_group_only"}))
async def send_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data(); user_id = callback.from_user.id
    anketa_id = db_get_next_id(user_id); worker_name = db_check_worker(user_id); client_tag = data.get('client')
    
    # Проверяем режим: только группа (без канала)
    group_only = callback.data == "send_group_only"
    
    # Проверяем режим множественного выбора
    multi_clients = data.get('multi_clients', [])
    is_multi = len(multi_clients) > 0
    
    # Проверяем, выбран ли клиент другого работника
    client_owner_id = data.get('client_owner_id', user_id)  # Используем ID владельца клиента
    
    # Проверяем режим "только канал"
    channel_only = data.get('channel_only', False)
    
    if channel_only:
        await send_to_channel_only(callback, state, user_id, worker_name, anketa_id, data)
    elif is_multi:
        # Множественная отправка
        await send_to_multiple_clients(callback, state, user_id, worker_name, anketa_id, data, multi_clients, client_owner_id, skip_channel=group_only)
    else:
        # Обычная отправка одному клиенту
        await send_to_single_client(callback, state, user_id, worker_name, anketa_id, data, client_tag, client_owner_id, skip_channel=group_only)

async def send_to_channel_only(callback, state, user_id, worker_name, anketa_id, data):
    """Отправка анкеты только в канал (без клиентского чата)"""
    start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔄 Новые часы")]], resize_keyboard=True)
    
    pub_fields = build_anketa_fields(data, chrono_label="Market Price (Chrono24)", include_manager=False, include_rating=True, bold_rating=False)
    public_text = f"🟢 <b>Status: Available</b>\n\n👤 <b>{worker_name}</b>\n📢 Channel\n🆔 <b>ID: {anketa_id}</b>\n{pub_fields}"
    
    mgr_fields = build_anketa_fields(data, chrono_label="Chrono", include_manager=True, include_rating=True, bold_rating=True)
    manager_body = f"🆔 <b>ID: {anketa_id}</b>\n👤 <b>От:</b> {worker_name}\n📢 <b>Только канал</b>\n{mgr_fields}"
    manager_text_final = f"🟢 <b>Status: Available</b>\n\n{manager_body}"
    
    db_save_full_order(user_id, worker_name, anketa_id, data)
    lot_id = str(uuid.uuid4())[:8]
    
    # Отправляем ТОЛЬКО в канал (без чата клиента)
    channel_buttons = get_channel_status_kb(lot_id)
    if TARGET_CHANNEL_ID != 0:
        asyncio.create_task(delayed_channel_post(TARGET_CHANNEL_ID, data.get("media_files"), public_text, channel_buttons, lot_id))
    
    # Кнопки для работника
    worker_msg = await callback.message.answer(f"✅ <b>Отправлено в канал!</b>\n🆔 <b>ID: {anketa_id}</b>", reply_markup=start_kb, parse_mode="HTML")
    
    # Отправляем менеджерам
    manager_msgs_info = []
    try:
        media_files = data.get("media_files", [])
        for mgr_id in MANAGER_IDS:
            try:
                media_group = []
                for item in media_files:
                    if item['type'] == 'photo': media_group.append(InputMediaPhoto(media=item['id'], parse_mode="HTML"))
                    elif item['type'] == 'video': media_group.append(InputMediaVideo(media=item['id'], parse_mode="HTML"))
                
                mgr_kb = InlineKeyboardBuilder()
                mgr_kb.button(text="📹 Запросить видео", callback_data=f"req_video_{lot_id}")
                mgr_kb.button(text="✅ БЕРУТ", callback_data=f"client_buy_{lot_id}")
                mgr_kb.button(text="❌ Отказ", callback_data=f"reject_{lot_id}")
                mgr_kb.button(text="💬 Коммент", callback_data=f"feedback_start_{lot_id}")
                mgr_kb.button(text="🟢", callback_data=f"lot_status_available_{lot_id}")
                mgr_kb.button(text="🟡", callback_data=f"lot_status_reserved_{lot_id}")
                mgr_kb.button(text="🔴", callback_data=f"lot_status_sold_{lot_id}")
                mgr_kb.adjust(1, 1, 1, 1, 3)
                
                if len(media_group) > 1:
                    await bot.send_media_group(mgr_id, media=media_group)
                    mgr_msg = await bot.send_message(mgr_id, manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    msg_id = mgr_msg.message_id
                else:
                    if media_files[0]['type'] == 'photo': mgr_msg = await bot.send_photo(mgr_id, media_files[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    else: mgr_msg = await bot.send_video(mgr_id, media_files[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    msg_id = mgr_msg.message_id
                manager_msgs_info.append({'chat_id': mgr_id, 'msg_id': msg_id})
            except Exception as e: logging.error(f"Не удалось отправить менеджеру {mgr_id}: {e}")
    except Exception as e: await callback.message.answer(f"❌ Ошибка отправки: {e}")
    
    LOTS_CACHE[lot_id] = {
        "media_files": data.get("media_files"),
        "clean_text": public_text.replace("🟢 <b>Status: Available</b>\n\n", ""),
        "manager_body": manager_body,
        "user_id": user_id,
        "target_client_id": None,
        "client_tag": "📢 Channel",
        "worker_msg_id": worker_msg.message_id,
        "worker_name": worker_name,
        "channel_msg_id": None,
        "channel_text_msg_id": None,
        "chat_msg_id": None,
        "chat_text_msg_id": None,
        "manager_msgs": manager_msgs_info
    }
    save_lots_cache()
    logging.info(f"💾 Сохранен lot_id={lot_id} (только канал)")
    
    await state.clear()

async def send_to_multiple_clients(callback, state, user_id, worker_name, anketa_id, data, multi_clients, client_owner_id, skip_channel=False):
    """Отправка анкеты нескольким клиентам"""
    start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔄 Новые часы")]], resize_keyboard=True)
    
    # Формируем список клиентов для отображения
    clients_display = ", ".join(multi_clients)
    
    await callback.message.answer(f"✅ <b>Отправляю анкету {len(multi_clients)} клиентам...</b>\n🆔 <b>ID: {anketa_id}</b>", reply_markup=start_kb, parse_mode="HTML")

    # Создаем общий lot_id для всех клиентов (для статуса в канале)
    main_lot_id = str(uuid.uuid4())[:8]
    first_client_tag = multi_clients[0]
    target_client_id = get_client_id(client_owner_id, first_client_tag)
    
    ct = format_client_table(first_client_tag, data.get('table'))
    pub_fields = build_anketa_fields(data, chrono_label="Market Price (Chrono24)", include_manager=False, include_rating=True, bold_rating=False)
    clean_text = f"👤 <b>{worker_name}</b>\nClient {ct}\n🆔 <b>ID: {anketa_id}</b>\n{pub_fields}\n\n📞 <a href=\"tg://user?id=8548264779\">Contact Manager</a>"
    
    # Отправляем в каждый чат клиента        
    first_chat_msg_id = None
    first_chat_text_msg_id = None
    all_chat_messages = []
    is_first = True
    
    for client_tag in multi_clients:
        # Получаем групповой чат для каждого клиента
        actual_chat_id = get_client_group_chat(client_owner_id, client_tag)
        
        ct_loop = format_client_table(client_tag, data.get('table'))
        public_text = f"🟢 <b>Status: Available</b>\n\n👤 <b>{worker_name}</b>\nClient {ct_loop}\n🆔 <b>ID: {anketa_id}</b>\n{pub_fields}\n\n📞 <a href=\"tg://user?id=8548264779\">Contact Manager</a>"
        
        try:
            # Используем main_lot_id только для ПЕРВОГО клиента (для канала), остальным отправляем только в чат
            if is_first:
                _, chat_msg_id, chat_text_msg_id = await broadcast_to_channels(data.get("media_files"), public_text, main_lot_id, actual_chat_id, skip_channel=skip_channel)
                first_chat_msg_id = chat_msg_id
                first_chat_text_msg_id = chat_text_msg_id
                is_first = False
            else:
                # Для остальных клиентов только в чат, без канала, НО с правильным lot_id
                _, chat_msg_id, chat_text_msg_id = await broadcast_to_channels_chat_only(data.get("media_files"), public_text, actual_chat_id, main_lot_id)
            # Сохраняем все chat messages для обновления статуса
            all_chat_messages.append({"chat_id": actual_chat_id, "msg_id": chat_msg_id, "text_msg_id": chat_text_msg_id})
            logging.info(f"✅ Отправлено {client_tag}")
        except Exception as e:
            logging.error(f"❌ Ошибка отправки {client_tag}: {e}")
    
    # Ссылки на чаты для работника
    await callback.message.answer(f"📍 Анкета отправлена в {len(multi_clients)} чатов.", parse_mode="HTML")

    # Отправляем менеджеру сводку
    mgr_fields = build_anketa_fields(data, chrono_label="Chrono", include_manager=True, include_rating=True, bold_rating=True)
    manager_body = f"🆔 <b>ID: {anketa_id}</b>\n👤 <b>От:</b> {worker_name}\n🏷 <b>Клиенты:</b> {clients_display}\n{mgr_fields}"
    manager_text_final = f"🟢 <b>Status: Available</b>\n\n{manager_body}\n\n📤 <b>Отправлено {len(multi_clients)} клиентам</b>"
    
    # Генерируем ссылку на первый групповой чат
    actual_chat_id = get_client_group_chat(client_owner_id, first_client_tag)
    chat_link = await make_chat_link(actual_chat_id, first_chat_msg_id)
    
    # Создаем кнопки для менеджера
    mgr_kb = InlineKeyboardBuilder()
    
    mgr_kb.button(text="📹 Запросить видео", callback_data=f"req_video_{main_lot_id}")
    mgr_kb.button(text="✅ БЕРУТ", callback_data=f"client_buy_{main_lot_id}")
    mgr_kb.button(text="❌ Отказ", callback_data=f"reject_{main_lot_id}")
    mgr_kb.button(text="💬 Коммент", callback_data=f"feedback_start_{main_lot_id}")
    
    mgr_kb.row(
        InlineKeyboardButton(text="🟡 Rsrv", callback_data=f"set_status_reserved_{main_lot_id}"),
        InlineKeyboardButton(text="🟢 Avail", callback_data=f"set_status_available_{main_lot_id}"),
        InlineKeyboardButton(text="🔴 Sold", callback_data=f"set_status_sold_{main_lot_id}")
    )
    
    # Отправляем менеджерам
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
                    if mf[0]['type'] == 'photo': 
                        msg = await bot.send_photo(mgr_id, mf[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    else: 
                        msg = await bot.send_video(mgr_id, mf[0]['id'], caption=manager_text_final, reply_markup=mgr_kb.as_markup(), parse_mode="HTML")
                    msg_id = msg.message_id
                
                if msg_id:
                    manager_msgs_info.append({'chat_id': mgr_id, 'msg_id': msg_id})
            except Exception as e: 
                print(f"Не удалось отправить менеджеру {mgr_id}: {e}")
    except Exception as e: 
        await callback.message.answer(f"❌ Ошибка отправки: {e}")
    
    # Сохраняем в кэш
    LOTS_CACHE[main_lot_id] = {
        "media_files": data.get("media_files"),
        "clean_text": clean_text,
        "manager_body": manager_body,
        "user_id": user_id,
        "target_client_id": target_client_id,
        "client_tag": first_client_tag,
        "worker_msg_id": None,
        "worker_name": worker_name,
        "channel_msg_id": None,
        "channel_text_msg_id": None,
        "chat_msg_id": first_chat_msg_id,
        "chat_text_msg_id": first_chat_text_msg_id,
        "all_chat_messages": all_chat_messages,
        "manager_msgs": manager_msgs_info
    }
    save_lots_cache()
    logging.info(f"💾 Сохранен lot_id={main_lot_id} для множественной отправки ({len(all_chat_messages)} чатов)")
    
    db_save_full_order(user_id, worker_name, anketa_id, data)
    
    # Предлагаем повторить отправку тем же клиентам (только для 2+ клиентов)
    if len(multi_clients) >= 2:
        await state.clear()
        await state.update_data(repeat_clients=multi_clients, repeat_owner_id=client_owner_id)
        repeat_kb = InlineKeyboardBuilder()
        repeat_kb.button(text="🔁 Новая анкета тем же клиентам", callback_data="repeat_same_clients")
        for i, cl in enumerate(multi_clients):
            repeat_kb.button(text=f"❌ {cl}", callback_data=f"repeat_remove_{i}")
        repeat_kb.adjust(1)
        await callback.message.answer(
            f"📋 <b>Клиенты:</b> {', '.join(multi_clients)}\n\nОтправить новую анкету тем же клиентам?",
            reply_markup=repeat_kb.as_markup(), parse_mode="HTML"
        )
    else:
        await state.clear()

@dp.callback_query(F.data == "repeat_same_clients")
async def repeat_same_clients(callback: types.CallbackQuery, state: FSMContext):
    """Начать новую анкету для тех же клиентов"""
    data = await state.get_data()
    clients = data.get('repeat_clients', [])
    owner_id = data.get('repeat_owner_id')
    if not clients or len(clients) < 1:
        await callback.answer("⚠️ Нет клиентов для повтора", show_alert=True)
        return
    await callback.message.delete()
    await state.clear()
    await state.update_data(
        media_files=[], editing_mode=False,
        multi_clients=clients, client=", ".join(clients),
        multi_mode=False, client_owner_id=owner_id
    )
    fsm = dp.fsm.get_context(bot, callback.message.chat.id, callback.message.chat.id)
    await fsm.set_state(Form.uploading_media)
    await callback.message.answer(
        f"📸 <b>Загрузи фото/видео для новой анкеты</b>\n👥 Клиенты: {', '.join(clients)}",
        reply_markup=make_kb([], rows=1, back=True, done_text="✅ Все файлы загружены", skip=False),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("repeat_remove_"))
async def repeat_remove_client(callback: types.CallbackQuery, state: FSMContext):
    """Удалить клиента из списка повторной отправки"""
    data = await state.get_data()
    clients = list(data.get('repeat_clients', []))
    owner_id = data.get('repeat_owner_id')
    idx = int(callback.data.split("_")[-1])
    if idx < 0 or idx >= len(clients):
        await callback.answer("⚠️ Ошибка", show_alert=True)
        return
    removed = clients.pop(idx)
    await state.update_data(repeat_clients=clients)
    if len(clients) == 0:
        await callback.message.delete()
        await callback.answer(f"❌ Все клиенты удалены")
        await state.clear()
        return
    # Обновляем кнопки
    repeat_kb = InlineKeyboardBuilder()
    if len(clients) >= 1:
        repeat_kb.button(text="🔁 Новая анкета тем же клиентам", callback_data="repeat_same_clients")
    for i, cl in enumerate(clients):
        repeat_kb.button(text=f"❌ {cl}", callback_data=f"repeat_remove_{i}")
    repeat_kb.adjust(1)
    await callback.message.edit_text(
        f"📋 <b>Клиенты:</b> {', '.join(clients)}\n\nОтправить новую анкету тем же клиентам?",
        reply_markup=repeat_kb.as_markup(), parse_mode="HTML"
    )
    await callback.answer(f"❌ {removed} удален")

async def send_to_single_client(callback, state, user_id, worker_name, anketa_id, data, client_tag, client_owner_id, skip_channel=False):
    """Отправка анкеты одному клиенту"""
    target_client_id = get_client_id(client_owner_id, client_tag)
    
    client_link_text = client_tag
    if target_client_id and isinstance(target_client_id, int):
        client_link_text = f'<a href="tg://user?id={target_client_id}">{client_tag}</a>'

    ct_mgr = format_client_table(client_link_text, data.get('table'))
    mgr_fields = build_anketa_fields(data, chrono_label="Chrono", include_manager=True, include_rating=True, bold_rating=True)
    manager_body = f"🆔 <b>ID: {anketa_id}</b>\n👤 <b>От:</b> {worker_name}\n🏷 <b>Клиент:</b> {ct_mgr}\n{mgr_fields}"
    manager_text_final = f"🟢 <b>Status: Available</b>\n\n{manager_body}"

    ct = format_client_table(client_tag, data.get('table'))
    pub_fields = build_anketa_fields(data, chrono_label="Market Price (Chrono24)", include_manager=False, include_rating=True, bold_rating=False)
    public_text = f"🟢 <b>Status: Available</b>\n\n👤 <b>{worker_name}</b>\nClient {ct}\n🆔 <b>ID: {anketa_id}</b>\n{pub_fields}\n\n📞 <a href=\"tg://user?id=8548264779\">Contact Manager</a>"
    clean_text = f"👤 <b>{worker_name}</b>\nClient {ct}\n🆔 <b>ID: {anketa_id}</b>\n{pub_fields}\n\n📞 <a href=\"tg://user?id=8548264779\">Contact Manager</a>"

    db_save_full_order(user_id, worker_name, anketa_id, data)
    lot_id = str(uuid.uuid4())[:8]
    
    # Получаем групповой чат для этого клиента (используем владельца клиента)
    actual_chat_id = get_client_group_chat(client_owner_id, client_tag)
    
    _, chat_msg_id, chat_text_msg_id = await broadcast_to_channels(data.get("media_files"), public_text, lot_id, actual_chat_id, skip_channel=skip_channel)

    # ГЕНЕРАЦИЯ ССЫЛКИ НА ЧАТ
    chat_link = await make_chat_link(actual_chat_id, chat_msg_id)

    # Кнопки для работника
    start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔄 Новые часы")]], resize_keyboard=True)
    worker_msg = await callback.message.answer(f"✅ <b>Отправлено!</b>\n🆔 <b>ID: {anketa_id}</b>", reply_markup=start_kb, parse_mode="HTML")
    

    # СБОРКА КНОПОК ДЛЯ МЕНЕДЖЕРА
    mgr_kb = InlineKeyboardBuilder()
    
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
    save_lots_cache()
    logging.info(f"💾 Сохранен lot_id={lot_id} в LOTS_CACHE")

    await state.clear()

# --- СМЕНА СТАТУСА ---
@dp.callback_query(F.data.startswith("set_status_"))
@dp.callback_query(F.data.startswith("ch_status_"))
async def change_status_unified(callback: types.CallbackQuery):
    is_admin = callback.from_user.id in MANAGER_IDS or callback.from_user.id in STATUS_MODERATORS
    if not is_admin: return await callback.answer("⛔️ Только менеджер может менять статус.", show_alert=True)

    parts = callback.data.split("_")
    new_status = parts[2]; lot_id = parts[3]
    
    logging.info(f"🔍 Смена статуса: callback_data={callback.data}, lot_id={lot_id}")
    logging.info(f"🔍 LOTS_CACHE keys: {list(LOTS_CACHE.keys())}")
    
    lot_data = LOTS_CACHE.get(lot_id)
    if not lot_data: 
        logging.error(f"❌ Лот {lot_id} не найден в кэше!")
        return await callback.answer("Лот устарел", show_alert=True)
    
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

    # Обновляем КАНАЛ (витрину)
    chan_msg_id = lot_data.get('channel_msg_id')
    
    logging.info(f"🔍 Попытка обновить канал: TARGET_CHANNEL_ID={TARGET_CHANNEL_ID}, chan_msg_id={chan_msg_id}")
    
    if TARGET_CHANNEL_ID != 0 and chan_msg_id:
        try:
            # Редактируем caption последнего фото в альбоме (где находится текст)
            logging.info(f"🔄 Редактируем сообщение {chan_msg_id} в канале {TARGET_CHANNEL_ID}")
            await bot.edit_message_caption(
                chat_id=TARGET_CHANNEL_ID, 
                message_id=chan_msg_id, 
                caption=final_public_text, 
                parse_mode="HTML"
            )
            logging.info(f"✅ Статус обновлен в канале")
        except Exception as e:
            logging.error(f"❌ Ошибка обновления канала: {e}")
    else:
        logging.warning(f"⚠️ Пропуск обновления канала: TARGET_CHANNEL_ID={TARGET_CHANNEL_ID}, chan_msg_id={chan_msg_id}")

    # Обновляем ГРУППОВЫЕ ЧАТЫ (поддержка нескольких клиентов)
    all_chat_messages = lot_data.get('all_chat_messages', [])
    
    if all_chat_messages:
        # Мульти-клиент: обновляем все чаты
        for chat_info in all_chat_messages:
            target_chat = chat_info.get('chat_id')
            chat_text_msg_id = chat_info.get('text_msg_id')
            chat_msg_id = chat_info.get('msg_id')
            
            if target_chat and isinstance(target_chat, int) and target_chat < 0:
                try:
                    if chat_text_msg_id:
                        await bot.edit_message_text(
                            chat_id=target_chat, 
                            message_id=chat_text_msg_id, 
                            text=final_public_text, 
                            reply_markup=get_channel_status_kb(lot_id), 
                            parse_mode="HTML"
                        )
                    elif chat_msg_id:
                        await bot.edit_message_caption(
                            chat_id=target_chat, 
                            message_id=chat_msg_id, 
                            caption=final_public_text, 
                            reply_markup=get_channel_status_kb(lot_id), 
                            parse_mode="HTML"
                        )
                    logging.info(f"✅ Статус обновлен в чате {target_chat}")
                except Exception as e:
                    logging.error(f"❌ Ошибка обновления чата {target_chat}: {e}")
    else:
        # Одиночный клиент: старая логика
        worker_id = lot_data.get('user_id')
        client_tag = lot_data.get('client_tag')
        target_chat = get_client_group_chat(worker_id, client_tag) if worker_id and client_tag else lot_data['target_client_id']
        chat_text_msg_id = lot_data.get('chat_text_msg_id')
        chat_msg_id = lot_data.get('chat_msg_id')
        
        if target_chat and isinstance(target_chat, int) and target_chat < 0:
            try:
                if chat_text_msg_id:
                    await bot.edit_message_text(
                        chat_id=target_chat, 
                        message_id=chat_text_msg_id, 
                        text=final_public_text, 
                        reply_markup=get_channel_status_kb(lot_id), 
                        parse_mode="HTML"
                    )
                elif chat_msg_id:
                    await bot.edit_message_caption(
                        chat_id=target_chat, 
                        message_id=chat_msg_id, 
                        caption=final_public_text, 
                        reply_markup=get_channel_status_kb(lot_id), 
                        parse_mode="HTML"
                    )
                logging.info(f"✅ Статус обновлен в чате {target_chat}")
            except Exception as e:
                logging.error(f"❌ Ошибка обновления чата: {e}")

    # Пересоздаем клавиатуру менеджера с актуальными кнопками
    target_client_id = lot_data.get('target_client_id')
    client_tag = lot_data.get('client_tag', 'Клиент')
    worker_id = lot_data.get('user_id')
    
    # Получаем ссылку на пост в группе
    chat_msg_id = lot_data.get('chat_msg_id')
    actual_chat_id = get_client_group_chat(worker_id, client_tag) if worker_id and client_tag else target_client_id
    chat_link = await make_chat_link(actual_chat_id, chat_msg_id)
    
    mgr_kb = InlineKeyboardBuilder()
    
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
        
        await c.message.answer("✅ Улетело клиенту!")
        
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
        
        mkb = InlineKeyboardBuilder()
        mkb.button(text=f"🚀 В чат клиента ({ld.get('client_tag', '')})", callback_data=f"fwd_vid_{lid}")
        mkb.adjust(1)
        
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
    lid = c.data.split("_")[2]; ld = LOTS_CACHE.get(lid)
    if not ld: return await c.answer("Лот устарел", show_alert=True)
    
    worker_id = ld.get('user_id')
    client_tag = ld.get('client_tag')
    actual_chat_id = get_client_group_chat(worker_id, client_tag) if worker_id and client_tag else None
    
    if not actual_chat_id: return await c.answer("Чат не найден", show_alert=True)
    
    await c.answer("⏳...")
    # Извлекаем ID анкеты из clean_text
    clean_text = ld.get('clean_text', '')
    anketa_line = ""
    for line in clean_text.split('\n'):
        if '🆔' in line:
            anketa_line = line
            break
    video_caption = f"📹 {anketa_line}" if anketa_line else "📹"
    try:
        await bot.send_video(actual_chat_id, c.message.video.file_id, caption=video_caption, parse_mode="HTML")
        await c.message.answer(f"✅ Видео отправлено в чат {client_tag}!")
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
    load_lots_cache()  # Загрузка кэша лотов после перезапуска
    logging.info("Bot started (v104: Persistent LOTS_CACHE)")
    await user_client.start(); await dp.start_polling(bot)

if __name__ == "__main__": asyncio.run(main())