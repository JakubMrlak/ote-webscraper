import logging
from datetime import date, timedelta
from ote_ida.fetcher import download_xlsx
from ote_ida.parser import parse_xlsx
from ote_ida.storage import save_intervals, save_summary

logger = logging.getLogger(__name__)

SESSIONS = ["IDA1", "IDA2", "IDA3"]


def fetch_auction(session: str, delivery_date: date) -> bool:
    """
    Stáhne, parsuje a uloží jednu aukci.
    Vrátí True pokud úspěšně, False pokud ne.
    """
    logger.info(f"Zpracovávám: {session} {delivery_date}")

    data = download_xlsx(session, delivery_date)
    if data is None:
        logger.warning(f"Přeskakuji {session} {delivery_date} - data nedostupná")
        return False

    try:
        intervals, summary = parse_xlsx(data, session, delivery_date)
    except Exception as e:
        logger.error(f"Chyba parsování {session} {delivery_date}: {e}")
        return False

    save_intervals(intervals, delivery_date, session)
    save_summary(summary, delivery_date, session)
    return True


def fetch_range(
    date_from: date,
    date_to: date,
    sessions: list[str] = SESSIONS,
) -> None:
    """
    Stáhne aukce pro rozsah datumů a seznam sessions.
    Chyby loguje a pokračuje dál.
    """
    current = date_from
    while current <= date_to:
        for session in sessions:
            fetch_auction(session, current)
        current += timedelta(days=1)