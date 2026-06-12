import logging
import os
from datetime import datetime

import gspread
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_CREDS_FILE     = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")
_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")


def _get_sheet():
    gc = gspread.service_account(filename=_CREDS_FILE)
    return gc.open_by_key(_SPREADSHEET_ID).sheet1


def append_order(data: dict) -> None:
    """
    Appends one row to the Google Sheet.
    data keys: group, client_name, street, city, region, postal_code, country,
               email, phone, what_bought, travel_case, certificate,
               amount_usdt, payment_confirmed, payment_link, notes
    """
    ws = _get_sheet()
    row = [
        datetime.now().strftime("%d.%m.%Y %H:%M"),  # A  Дата
        data.get("group", ""),                        # B  Группа
        data.get("client_name", ""),                  # C  Имя клиента
        data.get("street", ""),                       # D  Улица, дом
        data.get("city", ""),                         # E  Город
        data.get("region", ""),                       # F  Область/регион
        data.get("postal_code", ""),                  # G  Индекс
        data.get("country", ""),                      # H  Страна
        data.get("email", ""),                        # I  Email
        data.get("phone", ""),                        # J  Телефон
        data.get("what_bought", ""),                  # K  Что купил
        data.get("travel_case", "Нет"),               # L  Дорожный кейс
        data.get("certificate", "Нет"),               # M  Сертификат
        data.get("amount_usdt", ""),                  # N  Сумма USDT
        data.get("payment_confirmed", "Ожидает"),     # O  Оплата
        data.get("payment_link", ""),                 # P  Ссылка оплаты
        data.get("notes", ""),                        # Q  Заметки
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")
    logger.info("Row appended: %s", data.get("client_name"))
