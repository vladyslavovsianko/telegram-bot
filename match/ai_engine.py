import base64
import json
import logging
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI
from serpapi import GoogleSearch

load_dotenv()

logger = logging.getLogger(__name__)

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

_VISUAL_COMPARE_SYSTEM = (
    "Ты строгий эксперт по швейцарским часам. "
    "Тебе показывают два изображения для визуального сравнения. "
    "Если в запросе есть особые инструкции клиента — они имеют наивысший приоритет: "
    "если все обнаруженные различия явно разрешены или объяснены этими инструкциями, "
    "статус обязан быть 'Match', а не 'Partial'. "
    "'Partial' используй только при наличии сомнений, НЕ покрытых инструкциями клиента. "
    "Отвечай строго в формате JSON."
)


# ── Google Lens ───────────────────────────────────────────────────────────────

def _upload_to_temp_host(image_bytes: bytes) -> str:
    """
    Uploads image bytes to 0x0.st and returns the public URL.
    Returns empty string on any failure.
    """
    try:
        resp = requests.post(
            "https://0x0.st",
            files={"file": ("collage.jpg", image_bytes, "image/jpeg")},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception:
        logger.warning("Temp image upload failed", exc_info=True)
    return ""


def get_lens_hint(image_bytes: bytes) -> str:
    """
    Uploads the collage to a temporary host, queries SerpApi Google Lens,
    and returns the title of the top visual match.
    Returns an empty string if anything fails or no results found.
    """
    if not _SERPAPI_KEY:
        logger.warning("SERPAPI_KEY not set — skipping Google Lens")
        return ""

    image_url = _upload_to_temp_host(image_bytes)
    if not image_url:
        return ""

    try:
        results = GoogleSearch(
            {"engine": "google_lens", "url": image_url, "api_key": _SERPAPI_KEY}
        ).get_dict()

        visual_matches = results.get("visual_matches", [])
        if visual_matches:
            top3 = [m.get("title", "") for m in visual_matches[:3]]
            hint = visual_matches[0].get("title", "")
            logger.info("Google Lens топ-3: %s", " | ".join(top3))
            return hint
    except Exception:
        logger.warning("Google Lens search failed", exc_info=True)

    return ""


# ── Matching ──────────────────────────────────────────────────────────────────

def visual_compare(
    telegram_b64: str,
    airtable_bytes: bytes,
    lens_hint: str = "",
    brand: str = "",
    details: str = "",
    notes: str = "",
) -> dict:
    """
    Visually compares a Telegram watch photo with a client's reference photo
    from Airtable using GPT-4o Vision.

    Returns a dict with keys:
        - status: 'Match' | 'Partial' | 'No Match'
        - reason: short explanation in Russian
    """
    airtable_b64 = base64.b64encode(airtable_bytes).decode("utf-8")

    hint_line = (
        f"Google Lens подсказывает, что на фото из канала, скорее всего, {lens_hint}. "
        if lens_hint else ""
    )

    client_info_parts = []
    if brand:
        client_info_parts.append(f"Бренд: {brand}")
    if details:
        client_info_parts.append(f"Детали: {details}")
    client_info = (
        "Информация о запросе клиента:\n" + "\n".join(f"  • {p}" for p in client_info_parts) + "\n"
        if client_info_parts else ""
    )

    notes_block = (
        f"⚠️ ОСОБЫЕ ИНСТРУКЦИИ КЛИЕНТА (соблюдай строго при сравнении):\n{notes}\n"
        if notes else ""
    )

    prompt = (
        "Перед тобой два изображения. "
        "Первое — фото лота из Telegram-канала. "
        "Второе — фото желаемых часов от клиента.\n"
        f"{hint_line}"
        f"{client_info}"
        f"{notes_block}"
        "Визуально сравни эти часы:\n"
        "1. Совпадает ли бренд и конкретная модель?\n"
        "2. Совпадает ли цвет циферблата, безель, тип меток?\n"
        "3. Совпадает ли материал и тип браслета/ремешка?\n"
        "4. Если в особых инструкциях клиента что-то разрешено или запрещено — это имеет приоритет над обычными критериями.\n\n"
        "Верни JSON с ключами: "
        "'score' (целое число от 0 до 100 — визуальное сходство в процентах), "
        "'status' ('Match' если score >= 70, 'Partial' если 50–69, 'No Match' если < 50) и "
        "'reason' (краткое объяснение на русском языке)."
    )

    response = _client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _VISUAL_COMPARE_SYSTEM},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{telegram_b64}",
                            "detail": "high",
                        },
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{airtable_b64}",
                            "detail": "high",
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
    )

    result = json.loads(response.choices[0].message.content)
    logger.info(
        "visual_compare result → status: %s | reason: %s",
        result.get("status"), result.get("reason"),
    )
    return result
