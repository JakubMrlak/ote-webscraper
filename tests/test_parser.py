from datetime import date
from pathlib import Path
import pandas as pd
import pytest
from ote_ida.parser import parse_xlsx

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(session: str, d: date) -> bytes:
    path = FIXTURES / f"{session}_{d}.xlsx"
    return path.read_bytes()


class TestStandardDay:
    def test_interval_count(self):
        data = load_fixture("IDA1", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA1", date(2026, 4, 30))
        assert len(intervals) == 96

    def test_columns_present(self):
        data = load_fixture("IDA1", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA1", date(2026, 4, 30))
        expected_cols = [
            "delivery_date", "session", "interval_start", "interval_end",
            "price_eur_mwh", "volume_mwh", "balance_mwh",
            "export_mwh", "import_mwh", "interval_count_valid"
        ]
        for col in expected_cols:
            assert col in intervals.columns

    def test_timestamps_are_timezone_aware(self):
        data = load_fixture("IDA1", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA1", date(2026, 4, 30))
        assert intervals["interval_start"].dt.tz is not None
        assert intervals["interval_end"].dt.tz is not None

    def test_interval_count_valid_is_true(self):
        data = load_fixture("IDA1", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA1", date(2026, 4, 30))
        assert intervals["interval_count_valid"].all()

    def test_summary_has_three_rows(self):
        data = load_fixture("IDA1", date(2026, 4, 30))
        _, summary = parse_xlsx(data, "IDA1", date(2026, 4, 30))
        assert len(summary) == 3
        assert set(summary["type"]) == {"BASE LOAD", "PEAK LOAD", "OFFPEAK LOAD"}


class TestIDA3:
    def test_interval_count(self):
        data = load_fixture("IDA3", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA3", date(2026, 4, 30))
        assert len(intervals) == 48

    def test_starts_at_noon(self):
        data = load_fixture("IDA3", date(2026, 4, 30))
        intervals, _ = parse_xlsx(data, "IDA3", date(2026, 4, 30))
        first = intervals["interval_start"].iloc[0]
        assert first.hour == 12
        assert first.minute == 0


class TestSpringDST:
    def test_interval_count(self):
        data = load_fixture("IDA2", date(2025, 3, 30))
        intervals, _ = parse_xlsx(data, "IDA2", date(2025, 3, 30))
        assert len(intervals) == 92

    def test_interval_count_valid_is_true(self):
        # 92 intervalů je správně pro jarní přechod - validace to ví
        data = load_fixture("IDA2", date(2025, 3, 30))
        intervals, _ = parse_xlsx(data, "IDA2", date(2025, 3, 30))
        assert intervals["interval_count_valid"].all()


class TestAutumnDST:
    def test_interval_count(self):
        data = load_fixture("IDA1", date(2025, 10, 26))
        intervals, _ = parse_xlsx(data, "IDA1", date(2025, 10, 26))
        assert len(intervals) == 100

    def test_interval_count_valid_is_true(self):
        data = load_fixture("IDA1", date(2025, 10, 26))
        intervals, _ = parse_xlsx(data, "IDA1", date(2025, 10, 26))
        assert intervals["interval_count_valid"].all()

    def test_no_duplicate_timestamps(self):
        data = load_fixture("IDA1", date(2025, 10, 26))
        intervals, _ = parse_xlsx(data, "IDA1", date(2025, 10, 26))
        assert intervals["interval_start"].nunique() == len(intervals)