import base64
import json
import logging
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_SYSTEM_PROMPT = """\
Ты ассистент который извлекает структурированные данные из переписки менеджера с клиентом.
Отвечай строго в формате JSON. Если информация не найдена — ставь null.

Особые правила разбора адреса:
- Адрес часто пишется блоком, каждое поле на отдельной строке. Например:
    Иванов
    Иван
    Прага
    Pocernicka 332
    +420123456789
    email@gmail.com
  В таком случае: первые строки — фамилия и имя клиента, далее — город, улица, телефон, email.
- Имя и фамилия могут быть на отдельных строках — объедини их в client_name через пробел.
- Улица и номер дома — одна строка (street), город — отдельно (city). Не смешивай их.
- Не путай имя клиента с названием города или улицей.
- Email всегда содержит @. Телефон — только цифры и + в начале. Не путай одно с другим.
- Сохраняй email точно как написан в тексте, включая все символы до и после @.
- Сохраняй телефон точно, включая + если есть.
"""

_EXTRACT_PROMPT = """\
Проанализируй переписку ниже и извлеки следующие данные:

1. client_name — полное имя клиента (не менеджера). Фамилия и имя могут быть на отдельных строках — объедини.
2. street — улица, дом, квартира (без города)
3. city — только город (не улица, не имя)
4. region — область, регион, округ (если есть)
5. postal_code — почтовый индекс
6. country — страна
7. email — email клиента (содержит @, копируй точно как написано)
8. phone — телефон клиента (сохраняй + если есть, с кодом страны)
9. what_bought — что именно купил клиент (часы + модель если известна)
10. travel_case — дорожный кейс: "Нет" или цвет ("Чёрный" / "Зелёный" / "Синий" / "Красный/Бордовый")
11. certificate — нужен ли сертификат: "Да" или "Нет"
12. amount_usdt — финальная сумма оплаты в USDT (только число)
13. payment_confirmed — подтверждена ли оплата менеджером: "Да", "Нет" или "Ожидает"
14. notes — важные заметки: сроки, пожелания по доставке, комментарии клиента

Переписка:
{chat_text}

Верни JSON с этими ключами. Если что-то не найдено — null.
"""

_PAYMENT_PROMPT = """\
Посмотри на это изображение. Это скриншот из мессенджера, криптокошелька или блокчейн-эксплорера.
Определи:
1. Это подтверждение транзакции/оплаты? (true/false)
2. Сумма транзакции (только число, или null если не видно)
3. Валюта (USDT, USD, EUR и т.д., или null)

Верни JSON: {"is_payment": true/false, "amount": число или null, "currency": "..." или null}
"""


def extract_order_data(chat_text: str) -> dict:
    """
    Sends chat text to GPT-4o and extracts structured order data.
    Returns a dict with order fields.
    """
    prompt = _EXTRACT_PROMPT.format(chat_text=chat_text)

    response = _client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    logger.info("Extracted order data: %s", result)
    return result


def analyze_payment_screenshot(image_bytes: bytes) -> dict:
    """
    Sends a payment screenshot to GPT-4o Vision.
    Returns {"is_payment": bool, "amount": float|None, "currency": str|None}
    """
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = _client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Ты анализируешь скриншоты транзакций. Отвечай строго в JSON."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64}",
                            "detail": "high",
                        },
                    },
                    {"type": "text", "text": _PAYMENT_PROMPT},
                ],
            },
        ],
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    logger.info("Payment screenshot analysis: %s", result)
    return result
