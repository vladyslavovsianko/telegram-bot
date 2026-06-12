import asyncio
import base64
import logging
import os
import re
import sqlite3
from io import BytesIO
from typing import Callable, Coroutine, Any

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import load_dotenv
from PIL import Image

from ai_engine import visual_compare, get_lens_hint
from database import get_active_requests
from extractor import extract_order_data, analyze_payment_screenshot
from sheets import append_order

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


_NOISY_LOGGERS = {
    "aiogram", "aiohttp", "httpx", "httpcore",
    "openai._base_client", "urllib3", "asyncio",
}


class TelegramLogHandler(logging.Handler):
    """Forwards all bot/AI log records to REPORT_CHAT_ID via Telegram."""

    ICONS = {
        logging.DEBUG:    "🔍",
        logging.INFO:     "ℹ️",
        logging.WARNING:  "⚠️",
        logging.ERROR:    "🔴",
        logging.CRITICAL: "🆘",
    }

    def __init__(self, bot: Bot, chat_id: int) -> None:
        super().__init__(level=logging.ERROR)
        self._bot = bot
        self._chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        # Пропускаем шум от сторонних библиотек
        top_logger = record.name.split(".")[0]
        if top_logger in _NOISY_LOGGERS:
            return
        try:
            icon = self.ICONS.get(record.levelno, "ℹ️")
            text = f"{icon} *{record.levelname}* | `{record.name}`\n{record.getMessage()}"
            if record.exc_info:
                import traceback
                tb = traceback.format_exception(*record.exc_info)
                excerpt = "".join(tb)[-800:]
                text += f"\n```\n{excerpt}\n```"
            asyncio.get_event_loop().create_task(
                self._bot.send_message(self._chat_id, text, parse_mode="Markdown")
            )
        except Exception:
            pass

# ── Config ────────────────────────────────────────────────────────────────────
_CHANNEL_ID     = int(os.getenv("CHANNEL_ID", "0"))
_REPORT_CHAT_ID = int(os.getenv("REPORT_CHAT_ID", "0"))
_CALC_GROUP_ID  = int(os.getenv("CALC_GROUP_ID", "0"))
_MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN", "")
_MAIN_DB_PATH   = os.getenv("MAIN_DB_PATH", "")

# Второй Bot-объект с токеном основного бота — только для send_message в чаты клиентов
_main_bot: Bot | None = Bot(token=_MAIN_BOT_TOKEN) if _MAIN_BOT_TOKEN else None


def _get_client_chat_id(client_tag: str) -> int | None:
    """Ищет group_chat_id клиента по client_tag в SQLite основного бота."""
    if not _MAIN_DB_PATH or not client_tag:
        return None
    try:
        conn = sqlite3.connect(_MAIN_DB_PATH, timeout=5)
        row = conn.execute(
            "SELECT group_chat_id FROM clients WHERE client_tag = ? AND is_active = 1 LIMIT 1",
            (client_tag,)
        ).fetchone()
        conn.close()
        return row[0] if row and row[0] else None
    except Exception as exc:
        logger.warning("SQLite lookup failed for '%s': %s", client_tag, exc)
        return None

# Telegram user_id менеджеров → имя (формат в .env: "id:имя,id:имя")
_MANAGERS: dict[int, str] = {}
for _entry in os.getenv("MANAGERS", "").split(","):
    _entry = _entry.strip()
    if ":" in _entry:
        _mid, _mname = _entry.split(":", 1)
        if _mid.strip().lstrip("-").isdigit():
            _MANAGERS[int(_mid.strip())] = _mname.strip()
    elif _entry.lstrip("-").isdigit():
        _MANAGERS[int(_entry)] = "Менеджер"

# Группы где разрешена команда /save
_SAVE_GROUP_IDS: set[int] = {
    int(g.strip())
    for g in os.getenv("SAVE_GROUP_IDS", "").split(",")
    if g.strip().lstrip("-").isdigit()
}

# Буфер сообщений группы: все сообщения с момента запуска бота
_group_buffer: dict[int, dict] = {}   # {chat_id: {"messages": [...], "photos": [bytes]}}
_GROUP_BUFFER_SIZE = 500              # хватит на ~неделю активной переписки

# Фразы менеджера означающие подтверждение оплаты
_PAYMENT_PHRASES = re.compile(
    r"(оплат[аеу]?\s*(получен|пришл|подтвер|есть|прошл)|"
    r"деньги\s*(пришл|получен|есть)|"
    r"пришл[аои]?\s*(оплат|деньг)|"
    r"оплачен[оа]?|"
    r"средства\s*(получен|пришл|зачислен)|"
    r"транзакци[яю]\s*(прошл|подтвер|получен)|"
    r"всё\s*оплачен|"
    r"подтверждаю\s*(получение|оплат))",
    re.IGNORECASE,
)

# Буфер для /save: накапливаем сообщения и фото по chat_id
_save_buffer: dict[int, dict] = {}  # {chat_id: {"messages": [...], "photos": [bytes]}}
_save_tasks:  dict[int, asyncio.Task] = {}
_auto_tasks:  dict[int, asyncio.Task] = {}  # авто-сохранение после подтверждения оплаты

# Группа для калькулятора — бот следит за словом "расчет" + числом.
_CALC_GROUP_ID = int(os.getenv("CALC_GROUP_ID", "0"))

ALBUM_WAIT_SEC = 1.5
MAX_ALBUM_PHOTOS = 3

# ── Кэш заявок клиентов (загружается один раз при старте) ────────────────────
_requests_cache: list[dict] = []

# ── Album collector state ─────────────────────────────────────────────────────
# Ключ: "{chat_id}_{mgid}" — чтобы альбомы из разных чатов не пересекались.
_album_buffer: dict[str, list[bytes]] = {}
_album_tasks:  dict[str, asyncio.Task] = {}
_album_meta:   dict[str, dict] = {}   # origin_msg, sender (Callable), post_link

# ─────────────────────────────────────────────────────────────────────────────

SendFn = Callable[..., Coroutine[Any, Any, None]]


def _escape_md(text: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+=|{}.!\\-])", r"\\\1", text)


def _post_link(message: Message) -> str:
    """Generates a t.me link to the original channel post."""
    if message.chat.username:
        return f"https://t\\.me/{message.chat.username}/{message.message_id}"
    cid = str(message.chat.id).lstrip("-").removeprefix("100")
    return f"https://t\\.me/c/{cid}/{message.message_id}"


def _build_match_message(
    req: dict,
    reason: str,
    post_link: str = "",
    score: int | None = None,
) -> str:
    lines = ["🚨 *Найдено визуальное совпадение\\!*", ""]
    if post_link:
        lines.append(f"📎 [Открыть пост в канале]({post_link})")
        lines.append("")
    lines.append(f"👤 Клиент: `{_escape_md(str(req.get('client_id', '?')))}`")
    if req.get("brand"):
        lines.append(f"⌚ Бренд: {_escape_md(req['brand'])}")
    if req.get("details"):
        lines.append(f"📋 Запрос: {_escape_md(req['details'])}")
    if req.get("budget"):
        lines.append(f"💰 Бюджет: {_escape_md(str(req['budget']))}")
    if req.get("notes"):
        lines.append(f"📝 Заметки: {_escape_md(req['notes'])}")
    lines.append("")
    if score is not None:
        lines.append(f"📊 Сходство: *{score}%*")
    lines.append(f"🤖 {_escape_md(reason)}")
    return "\n".join(lines)


# ── Collage builder ───────────────────────────────────────────────────────────

def build_collage(images_bytes: list[bytes]) -> bytes:
    if len(images_bytes) == 1:
        return images_bytes[0]

    pil_images = [Image.open(BytesIO(b)).convert("RGB") for b in images_bytes]
    target_h = min(img.height for img in pil_images)

    resized: list[Image.Image] = []
    for img in pil_images:
        ratio = target_h / img.height
        new_w = max(1, int(img.width * ratio))
        resized.append(img.resize((new_w, target_h), Image.LANCZOS))

    total_w = sum(img.width for img in resized)
    collage = Image.new("RGB", (total_w, target_h))
    x = 0
    for img in resized:
        collage.paste(img, (x, 0))
        x += img.width

    out = BytesIO()
    collage.save(out, format="JPEG", quality=90)
    return out.getvalue()


# ── Processing pipeline ───────────────────────────────────────────────────────

async def _run_pipeline(
    photos: list[bytes],
    bot: Bot,
    send: SendFn,           # async send(text, md=False) — абстракция над reply/send_message
    post_link: str = "",    # ссылка на пост в канале (пусто для личных сообщений)
    channel_mode: bool = False,
) -> None:
    is_album = len(photos) > 1
    collage_bytes = await asyncio.to_thread(build_collage, photos)
    b64_image = base64.b64encode(collage_bytes).decode("utf-8")

    prefix = f"🖼 Коллаж из {len(photos)} фото\\. " if is_album else ""
    if not channel_mode:
        await send(f"{prefix}🔎 Анализирую часы…", md=bool(prefix))

    # Step 1 — Google Lens (некритичный шаг, даёт подсказку для GPT)
    lens_hint = ""
    try:
        lens_hint = await asyncio.to_thread(get_lens_hint, collage_bytes)
        if lens_hint:
            logger.info("Lens hint: %s", lens_hint)
    except Exception:
        logger.warning("Google Lens failed — continuing without hint", exc_info=True)

    # Step 2 — Берём заявки из кэша (загружены при старте)
    active_requests = _requests_cache
    if not active_requests:
        logger.warning("Кэш заявок пуст — пропускаем сравнение")
        if not channel_mode:
            await send("⚠️ База клиентов не загружена. Перезапусти бота.")
        return

    # Step 3 — Визуальное сравнение с каждой заявкой
    matched_any = False
    for req in active_requests:
        client_id = req.get("client_id", "?")
        photo_bytes: bytes | None = req.get("photo_bytes")

        if not photo_bytes:
            logger.info("Client %s has no photo — skipping visual compare", client_id)
            continue

        try:
            result = await asyncio.to_thread(
                visual_compare, b64_image, photo_bytes, lens_hint,
                req.get("brand", ""), req.get("details", ""), req.get("notes", ""),
            )
            status = result.get("status", "No Match")
            reason = result.get("reason", "")
            score  = result.get("score")
            logger.info("Client %s → %s (%s%%): %s", client_id, status, score, reason)
        except Exception as exc:
            logger.exception("visual_compare error for client %s", client_id)
            continue

        if status == "Match":
            matched_any = True
            text = _build_match_message(req, reason, post_link, score)
            # Всегда шлём в report chat
            await send(text, md=True)
            # Если задан основной бот и есть group_chat_id — шлём и в чат клиента
            if _main_bot and channel_mode:
                client_tag = str(req.get("client_id", ""))
                group_chat_id = _get_client_chat_id(client_tag)
                if group_chat_id:
                    try:
                        await _main_bot.send_message(
                            group_chat_id,
                            text,
                            parse_mode="MarkdownV2",
                            disable_web_page_preview=True,
                        )
                        logger.info("Match sent to group_chat_id=%s for client '%s'", group_chat_id, client_tag)
                    except Exception as exc:
                        logger.warning("Failed to send match to group chat %s: %s", group_chat_id, exc)
                else:
                    logger.info("No group_chat_id found for client '%s' — skipped group send", client_tag)

    if not matched_any and not channel_mode:
        # В канальном режиме молчим при отсутствии совпадений — не спамим
        await send("✅ Анализ завершён. Совпадений с активными заявками не найдено.")


# ── Album collector helpers ───────────────────────────────────────────────────

async def _flush_album(key: str, bot: Bot) -> None:
    await asyncio.sleep(ALBUM_WAIT_SEC)

    photos   = _album_buffer.pop(key, [])
    meta     = _album_meta.pop(key, {})
    _album_tasks.pop(key, None)

    if not photos:
        return

    logger.info("Flushing album %s: %d photo(s)", key, len(photos))
    await _run_pipeline(
        photos, bot,
        send=meta["send"],
        post_link=meta.get("post_link", ""),
        channel_mode=meta.get("channel_mode", False),
    )


async def _queue(
    message: Message,
    bot: Bot,
    photo_bytes: bytes,
    send: SendFn,
    post_link: str = "",
    channel_mode: bool = False,
) -> None:
    """Adds a photo to the album buffer or triggers immediate processing."""
    mgid = message.media_group_id
    if mgid:
        key = f"{message.chat.id}_{mgid}"
        if key not in _album_buffer:
            _album_buffer[key] = []
            _album_meta[key] = {"send": send, "post_link": post_link, "channel_mode": channel_mode}
        if len(_album_buffer[key]) < MAX_ALBUM_PHOTOS:
            _album_buffer[key].append(photo_bytes)
            logger.debug("Buffered %d photo(s) for %s", len(_album_buffer[key]), key)
        if key not in _album_tasks:
            _album_tasks[key] = asyncio.create_task(_flush_album(key, bot))
    else:
        await _run_pipeline([photo_bytes], bot, send=send, post_link=post_link, channel_mode=channel_mode)


# ── Handlers ──────────────────────────────────────────────────────────────────

async def handle_photo(message: Message, bot: Bot) -> None:
    """Личные сообщения и пересылки боту."""
    buf = BytesIO()
    await bot.download(message.photo[-1], destination=buf)

    async def send(text: str, md: bool = False) -> None:
        await message.reply(text, parse_mode="MarkdownV2" if md else None)

    await _queue(message, bot, buf.getvalue(), send)


async def handle_channel_photo(message: Message, bot: Bot) -> None:
    """Посты из отслеживаемого канала."""
    # Фильтр по конкретному каналу (если задан)
    if _CHANNEL_ID and message.chat.id != _CHANNEL_ID:
        return

    if not _REPORT_CHAT_ID:
        logger.warning("REPORT_CHAT_ID не задан — пост из канала проигнорирован")
        return

    buf = BytesIO()
    await bot.download(message.photo[-1], destination=buf)

    link = _post_link(message)

    async def send(text: str, md: bool = False) -> None:
        await bot.send_message(
            _REPORT_CHAT_ID, text,
            parse_mode="MarkdownV2" if md else None,
            disable_web_page_preview=True,
        )

    await _queue(message, bot, buf.getvalue(), send, post_link=link, channel_mode=True)


# ── Calculator ────────────────────────────────────────────────────────────────

_CALC_RE = re.compile(r"расчет", re.IGNORECASE)
_NUM_RE  = re.compile(r"[\d\s.,]+")   # ищем числа (с пробелами/запятыми/точками)


def _parse_amount(text: str) -> float | None:
    """Extracts the first number from a message text."""
    for match in _NUM_RE.finditer(text):
        raw = match.group().replace(" ", "").replace(",", ".")
        try:
            value = float(raw)
            if value > 0:
                return value
        except ValueError:
            continue
    return None


def _fmt(value: float) -> str:
    """Formats a number with thousand separators, no trailing zeros."""
    if value == int(value):
        return f"{int(value):,}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ")


async def handle_calc(message: Message) -> None:
    """Handles calculator trigger in the calc group."""
    if _CALC_GROUP_ID and message.chat.id != _CALC_GROUP_ID:
        return

    text = message.text or message.caption or ""

    # Фильтр: только сообщения с цифрой (быстро отсекаем лишнее)
    if not any(ch.isdigit() for ch in text):
        return

    # Фильтр: должно быть слово "расчет"
    if not _CALC_RE.search(text):
        return

    amount = _parse_amount(text)
    if amount is None:
        return

    x = amount * 15
    y = x * 1.15

    reply = (
        f"🧮 <b>Расчёт для {_fmt(amount)}:</b>\n\n"
        f"<code>{_fmt(amount)} × 15 = {_fmt(x)}</code>\n"
        f"<code>{_fmt(x)} × 1.15 = {_fmt(y)}</code>\n\n"
        f"✅ Итого: <b>{_fmt(y)}</b>"
    )
    await message.reply(reply, parse_mode="HTML")
    logger.info("Calc: %.2f → x=%.2f → y=%.2f", amount, x, y)


# ── /save handler ─────────────────────────────────────────────────────────────

_SAVE_WINDOW_SEC = 3  # секунды ожидания после /save (минимум)
_MAX_MESSAGES    = 150


async def _report(bot: Bot, text: str, parse_mode: str = "HTML") -> None:
    """Sends message to REPORT_CHAT_ID (not to the group)."""
    if _REPORT_CHAT_ID:
        try:
            await bot.send_message(_REPORT_CHAT_ID, text, parse_mode=parse_mode)
        except Exception:
            logger.exception("Failed to send report message")


async def _process_save(chat_id: int, group_name: str, manager_name: str, bot: Bot) -> None:
    """Collects buffered messages, runs GPT extraction, writes to Google Sheets."""
    await asyncio.sleep(2)

    buf = _save_buffer.pop(chat_id, {})
    _save_tasks.pop(chat_id, None)
    _auto_tasks.pop(chat_id, None)

    # Берём весь накопленный буфер группы
    live = _group_buffer.get(chat_id, {"messages": [], "photos": []})
    seen_msgs = set(buf.get("messages", []))
    all_messages = buf.get("messages", []) + [m for m in live["messages"] if m not in seen_msgs]
    seen_photos  = set(id(p) for p in buf.get("photos", []))
    all_photos   = buf.get("photos", []) + [p for p in live["photos"] if id(p) not in seen_photos]

    messages: list[str]  = all_messages[-_MAX_MESSAGES:]
    photos:   list[bytes] = all_photos[-20:]

    if not messages and not photos:
        logger.warning("_process_save: buffer empty for chat %s", chat_id)
        return

    logger.info("Processing save: %d messages, %d photos", len(messages), len(photos))

    chat_text = "\n".join(messages)

    # Анализ скринов оплаты
    payment_confirmed = "Ожидает"
    amount_usdt = None

    for photo_bytes in photos:
        try:
            result = await asyncio.to_thread(analyze_payment_screenshot, photo_bytes)
            if result.get("is_payment"):
                payment_confirmed = "Да"
                if result.get("amount"):
                    amount_usdt = result["amount"]
                logger.info("Payment photo confirmed: %s %s", amount_usdt, result.get("currency"))
                break
        except Exception:
            logger.exception("Payment screenshot analysis failed")

    # Извлечение данных из текста
    try:
        data = await asyncio.to_thread(extract_order_data, chat_text)
    except Exception as exc:
        logger.exception("Order extraction failed")
        await _report(bot, f"⚠️ Ошибка при анализе переписки: {exc}")
        return

    if data.get("payment_confirmed") == "Да":
        payment_confirmed = "Да"
    if data.get("amount_usdt") and not amount_usdt:
        amount_usdt = data["amount_usdt"]

    row = {
        "group":             group_name,
        "client_name":       data.get("client_name") or "",
        "street":            data.get("street") or "",
        "city":              data.get("city") or "",
        "region":            data.get("region") or "",
        "postal_code":       data.get("postal_code") or "",
        "country":           data.get("country") or "",
        "email":             data.get("email") or "",
        "phone":             data.get("phone") or "",
        "what_bought":       data.get("what_bought") or "",
        "travel_case":       data.get("travel_case") or "Нет",
        "certificate":       data.get("certificate") or "Нет",
        "amount_usdt":       amount_usdt or data.get("amount_usdt") or "",
        "payment_confirmed": payment_confirmed,
        "payment_link":      "",
        "notes":             data.get("notes") or "",
    }

    try:
        await asyncio.to_thread(append_order, row)
    except Exception as exc:
        logger.exception("Google Sheets write failed")
        await _report(bot, f"⚠️ Ошибка записи в таблицу: {exc}")
        return

    lines = [
        "✅ <b>Сохранено в таблицу!</b>",
        f"👨‍💼 Менеджер: {manager_name} | 💬 {group_name}",
        "",
        f"👤 Клиент: {row['client_name'] or '—'}",
        f"📦 Купил: {row['what_bought'] or '—'}",
        f"🧳 Кейс: {row['travel_case']}",
        f"📜 Сертификат: {row['certificate']}",
        f"💰 Сумма: {row['amount_usdt'] or '—'} USDT",
        f"✅ Оплата: {row['payment_confirmed']}",
        f"🏠 {row['street'] or '—'}, {row['city'] or '—'}, {row['country'] or '—'}",
    ]
    await _report(bot, "\n".join(lines))


async def handle_save(message: Message, bot: Bot) -> None:
    """Handles /save command — starts collecting chat history."""
    chat_id    = message.chat.id
    group_name = message.chat.title or str(chat_id)

    # Только разрешённые группы
    if _SAVE_GROUP_IDS and chat_id not in _SAVE_GROUP_IDS:
        return

    # Только менеджеры
    if _MANAGERS and message.from_user.id not in _MANAGERS:
        await message.reply("⛔ У вас нет доступа к этой команде.")
        return

    manager_name = _MANAGERS.get(message.from_user.id, "Менеджер")

    # Копируем уже накопленный буфер + оставляем место для новых сообщений
    existing = _group_buffer.get(chat_id, {"messages": [], "photos": []})
    _save_buffer[chat_id] = {
        "messages": list(existing["messages"]),
        "photos":   list(existing["photos"]),
    }

    msg_count   = len(_save_buffer[chat_id]["messages"])
    photo_count = len(_save_buffer[chat_id]["photos"])
    logger.info("/save triggered by %s: %d msgs, %d photos — waiting %ds", manager_name, msg_count, photo_count, _SAVE_WINDOW_SEC)
    await _report(bot, f"📋 /save запущен — {msg_count} сообщений, {photo_count} фото. Жду {_SAVE_WINDOW_SEC}с...")

    if chat_id in _save_tasks:
        _save_tasks[chat_id].cancel()
    _save_tasks[chat_id] = asyncio.create_task(
        _delayed_save(chat_id, group_name, manager_name, bot)
    )


async def _delayed_save(chat_id: int, group_name: str, manager_name: str, bot: Bot) -> None:
    await asyncio.sleep(_SAVE_WINDOW_SEC)
    await _process_save(chat_id, group_name, manager_name, bot)


async def _buffer_message(chat_id: int, sender: str, text: str) -> None:
    """Adds a text line to the group rolling buffer."""
    if chat_id not in _group_buffer:
        _group_buffer[chat_id] = {"messages": [], "photos": []}
    buf = _group_buffer[chat_id]
    buf["messages"].append(f"{sender}: {text}")
    if len(buf["messages"]) > _GROUP_BUFFER_SIZE:
        buf["messages"] = buf["messages"][-_GROUP_BUFFER_SIZE:]


async def handle_group_message(message: Message, bot: Bot) -> None:
    """Unified handler for all text messages — buffers, runs calc, detects payment."""
    chat_id = message.chat.id
    text    = message.text or message.caption or ""

    if not text:
        return

    sender = (message.from_user.username or message.from_user.full_name or "?") if message.from_user else "?"

    # ── 1. Буферизация (только для save-групп) ────────────────────────────────
    if not _SAVE_GROUP_IDS or chat_id in _SAVE_GROUP_IDS:
        await _buffer_message(chat_id, sender, text)

        # Авто-сохранение при подтверждении оплаты менеджером
        is_manager = message.from_user and message.from_user.id in _MANAGERS
        if is_manager and _PAYMENT_PHRASES.search(text):
            manager_name = _MANAGERS.get(message.from_user.id, "Менеджер")
            group_name   = message.chat.title or str(chat_id)
            logger.info("Payment confirmation from %s in %s", manager_name, group_name)
            await _report(
                bot,
                f"💰 <b>Оплата зафиксирована!</b>\n"
                f"👨‍💼 {manager_name} | 💬 {group_name}\n\n"
                f"Когда клиент даст адрес — напиши <code>/save</code> в группе.",
            )

    # ── 2. Калькулятор ────────────────────────────────────────────────────────
    if _CALC_GROUP_ID and chat_id != _CALC_GROUP_ID:
        return
    if not any(ch.isdigit() for ch in text):
        return
    if not _CALC_RE.search(text):
        return

    amount = _parse_amount(text)
    if amount is None:
        return

    x = amount * 15
    y = x * 1.15

    reply = (
        f"🧮 <b>Расчёт для {_fmt(amount)}:</b>\n\n"
        f"<code>{_fmt(amount)} × 15 = {_fmt(x)}</code>\n"
        f"<code>{_fmt(x)} × 1.15 = {_fmt(y)}</code>\n\n"
        f"✅ Итого: <b>{_fmt(y)}</b>"
    )
    await message.reply(reply, parse_mode="HTML")
    logger.info("Calc: %.2f → x=%.2f → y=%.2f", amount, x, y)


async def handle_group_photo(message: Message, bot: Bot) -> None:
    """Handles photos — buffers for save-groups, processes for watch matching."""
    chat_id = message.chat.id

    # ── Буферизация для save-группы ───────────────────────────────────────────
    if not _SAVE_GROUP_IDS or chat_id in _SAVE_GROUP_IDS:
        buf = BytesIO()
        await bot.download(message.photo[-1], destination=buf)
        photo_bytes = buf.getvalue()

        if chat_id not in _group_buffer:
            _group_buffer[chat_id] = {"messages": [], "photos": []}
        _group_buffer[chat_id]["photos"].append(photo_bytes)
        if len(_group_buffer[chat_id]["photos"]) > 20:
            _group_buffer[chat_id]["photos"] = _group_buffer[chat_id]["photos"][-20:]

        sender  = (message.from_user.username or message.from_user.full_name or "?") if message.from_user else "?"
        caption = message.caption or ""
        if caption:
            await _buffer_message(chat_id, sender, f"[фото] {caption}")

        # Если фото от менеджера — проверяем не скрин ли это оплаты
        is_manager = message.from_user and message.from_user.id in _MANAGERS
        if is_manager and chat_id not in _auto_tasks:
            try:
                result = await asyncio.to_thread(analyze_payment_screenshot, photo_bytes)
                if result.get("is_payment"):
                    manager_name = _MANAGERS.get(message.from_user.id, "Менеджер")
                    group_name   = message.chat.title or str(chat_id)
                    amount       = result.get("amount", "?")
                    currency     = result.get("currency", "USDT")
                    logger.info("Payment photo detected from %s: %s %s", manager_name, amount, currency)
                    await _report(
                        bot,
                        f"💰 <b>Вижу скрин оплаты!</b>\n"
                        f"👨‍💼 {manager_name} | 💬 {group_name}\n"
                        f"💵 Сумма: {amount} {currency}\n\n"
                        f"Когда клиент даст адрес — напиши <code>/save</code> в группе.",
                    )
            except Exception:
                logger.exception("Payment photo check failed")
        return

    # ── Мэтчинг часов (личные сообщения боту) ────────────────────────────────
    await handle_photo(message, bot)


# ── Periodic cache refresh ────────────────────────────────────────────────────

_CACHE_REFRESH_SEC = 30 * 60  # каждые 30 минут


async def _refresh_cache_loop(bot: Bot) -> None:
    """Periodically reloads the client requests cache from Airtable."""
    global _requests_cache
    while True:
        await asyncio.sleep(_CACHE_REFRESH_SEC)
        logger.info("Обновляю кэш клиентов из Airtable…")
        try:
            fresh = await asyncio.to_thread(get_active_requests)
            _requests_cache = fresh
            with_photo = sum(1 for r in fresh if r.get("photo_bytes"))
            logger.info(
                "Кэш обновлён: %d клиентов, у %d есть фото",
                len(fresh), with_photo,
            )
        except Exception:
            logger.exception("Не удалось обновить кэш клиентов")


# ── Daily auto-save ───────────────────────────────────────────────────────────

# Индекс последнего сохранённого сообщения по chat_id (чтобы не дублировать)
_last_saved_idx: dict[int, int] = {}


async def _daily_auto_save(bot: Bot) -> None:
    """Runs every 24h: saves only NEW messages since last save."""
    while True:
        await asyncio.sleep(24 * 60 * 60)

        if not _SAVE_GROUP_IDS:
            continue

        logger.info("Daily auto-save starting for %d groups", len(_SAVE_GROUP_IDS))
        saved_count = 0

        for chat_id in list(_SAVE_GROUP_IDS):
            buf = _group_buffer.get(chat_id)
            if not buf or not buf.get("messages"):
                continue

            all_msgs   = buf["messages"]
            last_idx   = _last_saved_idx.get(chat_id, 0)
            new_msgs   = all_msgs[last_idx:]   # только новые с прошлого сохранения

            if not new_msgs:
                logger.info("Daily save: no new messages for chat %s", chat_id)
                continue

            try:
                group_name = str(chat_id)
                _save_buffer[chat_id] = {
                    "messages": new_msgs,
                    "photos":   list(buf.get("photos", [])),
                }
                await _process_save(chat_id, group_name, "Авто (ежедневно)", bot)
                # Запоминаем до какого индекса сохранили
                _last_saved_idx[chat_id] = len(all_msgs)
                saved_count += 1
                logger.info("Daily save done for chat %s (%d new msgs)", chat_id, len(new_msgs))
            except Exception:
                logger.exception("Daily auto-save failed for chat %s", chat_id)

        await _report(bot, f"🕛 Ежедневное сохранение: обработано групп — {saved_count}.")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    global _requests_cache

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set in .env")

    bot = Bot(token=token)
    dp  = Dispatcher()

    if _REPORT_CHAT_ID:
        tg_handler = TelegramLogHandler(bot, _REPORT_CHAT_ID)
        logging.getLogger().addHandler(tg_handler)

    # Загружаем базу клиентов один раз при старте
    logger.info("Загружаю базу клиентов из Airtable…")
    try:
        _requests_cache = await asyncio.to_thread(get_active_requests)
        with_photo = sum(1 for r in _requests_cache if r.get("photo_bytes"))
        logger.info(
            "База загружена: %d клиентов, у %d есть фото",
            len(_requests_cache), with_photo,
        )
    except Exception:
        logger.exception("Не удалось загрузить базу клиентов — бот запущен без кэша")

    dp.message.register(handle_group_message, F.text | F.caption)
    dp.message.register(handle_group_photo, F.photo)

    # Периодическое обновление кэша клиентов
    asyncio.create_task(_refresh_cache_loop(bot))
    dp.message.register(handle_photo, F.photo)
    dp.channel_post.register(handle_channel_photo, F.photo)

    logger.info(
        "Бот запущен (channel_id=%s, report_chat=%s)",
        _CHANNEL_ID or "any", _REPORT_CHAT_ID or "not set",
    )
    if _REPORT_CHAT_ID:
        await bot.send_message(
            _REPORT_CHAT_ID,
            f"🟢 Бот запущен\n"
            f"📋 Загружено клиентов: {len(_requests_cache)}\n"
            f"🖼 С фото: {sum(1 for r in _requests_cache if r.get('photo_bytes'))}",
        )
    await dp.start_polling(bot, allowed_updates=["message", "channel_post"], drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
