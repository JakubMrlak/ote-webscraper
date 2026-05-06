import pandas as pd
import io
import logging
from datetime import date
import zoneinfo

logger = logging.getLogger(__name__)

TZ = zoneinfo.ZoneInfo("Europe/Prague")


def parse_xlsx(data: bytes, session: str, delivery_date: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parsuje XLSX soubor OTE IDA.
    Vrátí tuple: (intervals_df, summary_df)
    """
    df_raw = pd.read_excel(io.BytesIO(data), sheet_name=0, header=None)

    intervals_df = _parse_intervals(df_raw, session, delivery_date)
    summary_df = _parse_summary(df_raw, session, delivery_date)

    return intervals_df, summary_df


def _parse_intervals(df_raw: pd.DataFrame, session: str, delivery_date: date) -> pd.DataFrame:
    """Parsuje řádky s 15minutovými intervaly."""

    # Najdi řádek s hlavičkou (obsahuje "Perioda")
    header_row = df_raw[df_raw[0] == "Perioda"].index[0]

    # Data začínají dva řádky pod hlavičkou (jeden prázdný řádek mezi)
    data = df_raw.iloc[header_row + 2:].copy()
    data.columns = ["period", "interval", "price", "volume", "balance", "export", "import"]
    data = data.dropna(subset=["interval"])
    data = data.reset_index(drop=True)

    # Parsuj timestamps z intervalu např. "00:00-00:15"
    starts = []
    ends = []
    for _, row in data.iterrows():
        start_str, end_str = str(row["interval"]).split("-")
        start = _parse_timestamp(delivery_date, start_str)
        end = _parse_timestamp(delivery_date, end_str)

        # Půlnoc na konci dne = další den 00:00
        if end <= start:
            end = end + pd.Timedelta(days=1)

        starts.append(start)
        ends.append(end)

    result = pd.DataFrame({
        "delivery_date": delivery_date,
        "session": session,
        "interval_start": starts,
        "interval_end": ends,
        "price_eur_mwh": pd.to_numeric(data["price"].values, errors="coerce"),
        "volume_mwh": pd.to_numeric(data["volume"].values, errors="coerce"),
        "balance_mwh": pd.to_numeric(data["balance"].values, errors="coerce"),
        "export_mwh": pd.to_numeric(data["export"].values, errors="coerce"),
        "import_mwh": pd.to_numeric(data["import"].values, errors="coerce"),
    })

    # Validační příznak - standardní den má 96 intervalů
    expected = 96
    result["interval_count_valid"] = len(result) == expected
    if len(result) != expected:
        logger.warning(f"{session} {delivery_date}: očekáváno {expected} intervalů, nalezeno {len(result)}")

    return result


def _parse_summary(df_raw: pd.DataFrame, session: str, delivery_date: date) -> pd.DataFrame:
    """Parsuje souhrnné hodnoty BASE/PEAK/OFFPEAK."""

    rows = []
    labels = ["BASE LOAD", "PEAK LOAD", "OFFPEAK LOAD"]

    for label in labels:
        price_row = df_raw[df_raw[0] == label]
        if not price_row.empty:
            rows.append({
                "delivery_date": delivery_date,
                "session": session,
                "type": label,
                "price_eur_mwh": pd.to_numeric(price_row.iloc[0][1], errors="coerce"),
            })

    return pd.DataFrame(rows)


def _parse_timestamp(delivery_date: date, time_str: str) -> pd.Timestamp:
    """Převede datum a časový řetězec na timezone-aware Timestamp."""
    time_str = time_str.strip()
    hour, minute = int(time_str[:2]), int(time_str[3:5])

    # 24:00 = půlnoc = začátek dalšího dne
    if hour == 24:
        hour = 0
        ts = pd.Timestamp(delivery_date) + pd.Timedelta(days=1)
        ts = ts.replace(hour=hour, minute=minute)
    else:
        ts = pd.Timestamp(delivery_date).replace(hour=hour, minute=minute)

    try:
        return ts.tz_localize(TZ, nonexistent="shift_forward")
    except Exception:
        # Podzimní přechod - ambiguous timestamp, bereme první výskyt (letní čas)
        return ts.tz_localize(TZ, ambiguous=True, nonexistent="shift_forward")