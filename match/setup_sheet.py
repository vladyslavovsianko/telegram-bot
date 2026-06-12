"""
Run once to create headers and dropdown validations in the Google Sheet.
Usage: py setup_sheet.py
"""
import os
import gspread
from dotenv import load_dotenv

load_dotenv()

CREDS_FILE     = os.getenv("GOOGLE_CREDENTIALS_FILE", "google_credentials.json")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

HEADERS = [
    "Дата",           # A
    "Группа (чат)",   # B
    "Имя клиента",    # C
    "Улица, дом",     # D
    "Город",          # E
    "Область/регион", # F
    "Индекс",         # G
    "Страна",         # H
    "Email",          # I
    "Телефон",        # J
    "Что купил",      # K
    "Дорожный кейс",  # L
    "Сертификат",     # M
    "Сумма USDT",     # N
    "Оплата",         # O
    "Ссылка оплаты",  # P
    "Заметки",        # Q
]

DROPDOWNS = {
    "L": ["Нет", "Чёрный", "Зелёный", "Синий", "Красный/Бордовый"],
    "M": ["Да", "Нет"],
    "O": ["Да", "Нет", "Ожидает"],
}

COL_WIDTHS = {
    "A": 120, "B": 140, "C": 160, "D": 220, "E": 130,
    "F": 140, "G": 80,  "H": 110, "I": 180, "J": 130,
    "K": 200, "L": 150, "M": 110, "N": 110, "O": 120,
    "P": 200, "Q": 220,
}

COL_IDX = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQ")}


def make_dropdown(sheet_id: int, col: str, values: list[str]) -> dict:
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1, "endRowIndex": 1000,
                "startColumnIndex": COL_IDX[col],
                "endColumnIndex": COL_IDX[col] + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values],
                },
                "showCustomUi": True,
                "strict": False,
            },
        }
    }


def main() -> None:
    gc = gspread.service_account(filename=CREDS_FILE)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.sheet1

    ws.update(values=[HEADERS], range_name="A1")

    ws.format("A1:Q1", {
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.13},
    })

    requests = []

    for col, width in COL_WIDTHS.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": ws.id, "dimension": "COLUMNS",
                    "startIndex": COL_IDX[col], "endIndex": COL_IDX[col] + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })

    for col, values in DROPDOWNS.items():
        requests.append(make_dropdown(ws.id, col, values))

    requests.append({
        "updateSheetProperties": {
            "properties": {"sheetId": ws.id, "gridProperties": {"frozenRowCount": 1}},
            "fields": "gridProperties.frozenRowCount",
        }
    })

    sh.batch_update({"requests": requests})
    print("Done! Columns: " + ", ".join(HEADERS))


if __name__ == "__main__":
    main()
