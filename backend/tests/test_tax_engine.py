import pytest
from modules.tax_engine.tax_computation import compute_tax


def _income_txn(amount):
    return {"amount": amount, "direction": "credit", "category": "taxable_income"}


def _expense_txn(amount):
    return {"amount": amount, "direction": "debit", "category": "deductible_expense"}


class TestScenario1:
    """Gross Income = ₦2,400,000/year"""

    def setup_method(self):
        txns = [_income_txn(2_400_000)]
        self.result = compute_tax(txns, "test-user", 2024)

    def test_gross_income(self):
        assert self.result["gross_income"] == 2_400_000

    def test_cra_fixed(self):
        assert self.result["cra_fixed"] == 200_000

    def test_cra_percentage(self):
        assert self.result["cra_percentage"] == 480_000

    def test_total_cra(self):
        assert self.result["total_cra"] == 680_000

    def test_pension_relief(self):
        assert self.result["pension_relief"] == 192_000

    def test_nhf_relief(self):
        assert self.result["nhf_relief"] == 60_000

    def test_nhis_relief(self):
        assert self.result["nhis_relief"] == 120_000

    def test_taxable_income(self):
        assert self.result["taxable_income"] == 1_348_000

    def test_tax_liability(self):
        assert self.result["tax_liability"] == pytest.approx(176_120, abs=1)

    def test_effective_rate(self):
        assert self.result["effective_rate"] == pytest.approx(7.338, abs=0.01)


class TestScenario2:
    """Gross Income = ₦600,000/year"""

    def setup_method(self):
        txns = [_income_txn(600_000)]
        self.result = compute_tax(txns, "test-user", 2024)

    def test_total_cra(self):
        assert self.result["total_cra"] == 320_000

    def test_pension_relief(self):
        assert self.result["pension_relief"] == 48_000

    def test_nhf_relief(self):
        assert self.result["nhf_relief"] == 15_000

    def test_nhis_relief(self):
        assert self.result["nhis_relief"] == 30_000

    def test_taxable_income(self):
        assert self.result["taxable_income"] == 187_000

    def test_tax_liability(self):
        assert self.result["tax_liability"] == pytest.approx(13_090, abs=1)

    def test_minimum_tax_not_applied(self):
        minimum_tax = 0.01 * 600_000
        assert self.result["tax_liability"] >= minimum_tax
        assert self.result["tax_liability"] == pytest.approx(13_090, abs=1)


class TestScenario3:
    """Gross Income = ₦10,000,000/year (top band)"""

    def setup_method(self):
        txns = [_income_txn(10_000_000)]
        self.result = compute_tax(txns, "test-user", 2024)

    def test_band_breakdown_count(self):
        assert len(self.result["band_breakdown"]) == 6

    def test_tax_liability_positive(self):
        assert self.result["tax_liability"] > 0

    def test_effective_rate_above_20(self):
        assert self.result["effective_rate"] > 20

    def test_top_band_applied(self):
        last_band = self.result["band_breakdown"][-1]
        assert last_band["rate"] == 0.24
        assert last_band["taxable_amount"] > 0
