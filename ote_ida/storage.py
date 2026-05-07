import pandas as pd
from pathlib import Path
from datetime import date
import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output/ote_ida_aukce")
SUMMARY_DIR = Path("output/ote_ida_souhrn")


def save_intervals(df: pd.DataFrame, delivery_date: date) -> Path:
    """Uloží intervalová data do parquet souboru."""
    path = _build_path(OUTPUT_DIR, delivery_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info(f"Uloženo: {path}")
    return path


def save_summary(df: pd.DataFrame, delivery_date: date) -> Path:
    """Uloží souhrnná data do parquet souboru."""
    path = _build_path(SUMMARY_DIR, delivery_date)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info(f"Uloženo souhrn: {path}")
    return path


def _build_path(base_dir: Path, delivery_date: date) -> Path:
    """Sestaví cestu ve formátu year=/month=/day=/part000.parquet"""
    return (
        base_dir
        / f"year={delivery_date.year}"
        / f"month={delivery_date.month:02d}"
        / f"day={delivery_date.day:02d}"
        / "part000.parquet"
    )