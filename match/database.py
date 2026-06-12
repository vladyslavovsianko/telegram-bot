import logging
import os

import requests
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()

logger = logging.getLogger(__name__)

_AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
_AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
_TABLE_NAME = "Client Requests"


def _download_image(url: str) -> bytes | None:
    """Downloads an image from a URL and returns raw bytes, or None on failure."""
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        logger.warning("Failed to download image: %s", url, exc_info=True)
    return None


def get_active_requests() -> list[dict]:
    """
    Fetches all records from the 'Client Requests' table
    where Status == 'Active'.

    Returns a list of dicts with keys:
        - client_id   (field: Client ID)
        - budget      (field: Budget)
        - brand       (field: Brand)
        - details     (field: Watch Details)
        - source      (field: Source)
        - notes       (field: Notes)
        - photo_bytes (bytes of the first attachment in field: Photo, or None)
    """
    api = Api(_AIRTABLE_API_KEY)
    table = api.table(_AIRTABLE_BASE_ID, _TABLE_NAME)

    records = table.all(formula="Status = 'Active'")

    result: list[dict] = []
    for record in records:
        fields = record.get("fields", {})

        photo_bytes: bytes | None = None
        attachments = fields.get("Photo", [])
        if attachments and isinstance(attachments, list):
            url = attachments[0].get("url", "")
            if url:
                photo_bytes = _download_image(url)
                if photo_bytes:
                    logger.info("Downloaded photo for client %s", fields.get("Client ID", "?"))
                else:
                    logger.warning("Could not download photo for client %s", fields.get("Client ID", "?"))

        result.append(
            {
                "client_id": fields.get("Client ID", ""),
                "budget":    fields.get("Budget", ""),
                "brand":     fields.get("Brand", ""),
                "details":   fields.get("Watch Details", ""),
                "source":    fields.get("Source", ""),
                "notes":     fields.get("Notes", ""),
                "photo_bytes": photo_bytes,
            }
        )

    return result
