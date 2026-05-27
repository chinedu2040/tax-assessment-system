import io
import pytest
import pandas as pd

from modules.ingestion.document_parser import parse_csv, parse_excel
from modules.ingestion.normaliser import normalise, _parse_date, _clean_amount


class TestCSVParser:
    def _make_csv(self, df: pd.DataFrame) -> bytes:
        buf = io.BytesIO()
        df.to_csv(buf, index=False)
        return buf.getvalue()

    def test_gtbank_style(self):
        df = pd.DataFrame({
            "Date": ["14/01/2024", "15/01/2024"],
            "Narration": ["UPWORK PAYMENT INV 2341", "ATM WITHDRAWAL LAGOS"],
            "Debit": [None, 5000],
            "Credit": [150000, None],
            "Balance": [500000, 495000],
        })
        records = parse_csv(self._make_csv(df))
        assert len(records) == 2
        assert records[0]["direction"] == "credit"
        assert records[1]["direction"] == "debit"

    def test_kuda_style(self):
        df = pd.DataFrame({
            "Transaction Date": ["2024-01-20", "2024-01-21"],
            "Description": ["MTN DATA SUBSCRIPTION", "FIVERR WITHDRAWAL"],
            "Amount": [-3000, 50000],
        })
        records = parse_csv(self._make_csv(df))
        assert len(records) == 2
        assert records[0]["direction"] == "debit"
        assert records[1]["direction"] == "credit"

    def test_removes_zero_amount(self):
        df = pd.DataFrame({
            "Date": ["14/01/2024"],
            "Narration": ["ZERO TXN"],
            "Amount": [0],
        })
        records = parse_csv(self._make_csv(df))
        assert len(records) == 0

    def test_deduplication(self):
        df = pd.DataFrame({
            "Date": ["14/01/2024", "14/01/2024"],
            "Narration": ["UPWORK PAYMENT", "UPWORK PAYMENT"],
            "Amount": [100000, 100000],
        })
        records = parse_csv(self._make_csv(df))
        assert len(records) == 1


class TestNormaliser:
    def test_date_dd_mm_yyyy(self):
        assert _parse_date("14/01/2024") == "2024-01-14"

    def test_date_yyyy_mm_dd(self):
        assert _parse_date("2024-01-14") == "2024-01-14"

    def test_date_14_jan_2024(self):
        assert _parse_date("14 Jan 2024") == "2024-01-14"

    def test_date_dd_mon_yy(self):
        assert _parse_date("14-Jan-24") == "2024-01-14"

    def test_amount_removes_naira_symbol(self):
        assert _clean_amount("₦150,000.00") == 150000.0

    def test_amount_removes_ngn(self):
        assert _clean_amount("NGN 50000") == 50000.0

    def test_amount_removes_commas(self):
        assert _clean_amount("1,200,000.50") == 1200000.5

    def test_signed_amount_direction(self):
        records = normalise([
            {"date": "2024-01-14", "description": "CREDIT ENTRY", "_signed_amount": 100000}
        ], "csv")
        assert records[0]["direction"] == "credit"

        records = normalise([
            {"date": "2024-01-14", "description": "DEBIT ENTRY", "_signed_amount": -50000}
        ], "csv")
        assert records[0]["direction"] == "debit"

    def test_amount_always_positive(self):
        records = normalise([
            {"date": "2024-01-14", "description": "DEBIT ENTRY", "_signed_amount": -50000}
        ], "csv")
        assert records[0]["amount"] > 0
