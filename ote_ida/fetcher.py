import requests
from datetime import date
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.ote-cr.cz/pubweb/attachments/431"


def build_url(session: str, delivery_date: date) -> str:
    """Sestaví URL pro stažení XLSX souboru."""
    year = delivery_date.year
    month = f"{delivery_date.month:02d}"
    day = f"{delivery_date.day:02d}"
    filename = f"{session}_{day}_{month}_{year}_CZ.xlsx"
    return f"{BASE_URL}/{year}/month{month}/day{day}/{filename}"


def download_xlsx(session: str, delivery_date: date) -> bytes | None:
    """Stáhne XLSX soubor pro danou session a datum. Vrátí bytes nebo None."""
    url = build_url(session, delivery_date)
    logger.info(f"Stahuji: {url}")

    try:
        response = requests.get(url, timeout=30)

        if response.status_code == 404:
            logger.warning(f"Aukce nenalezena (404): {session} {delivery_date}")
            return None

        response.raise_for_status()
        return response.content

    except requests.exceptions.Timeout:
        logger.error(f"Timeout: {session} {delivery_date}")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Chyba stahování {session} {delivery_date}: {e}")
        return None