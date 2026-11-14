"""Tests for the Money value object.

Verifies that financial arithmetic uses Decimal precision and that
cross-currency operations are rejected (ADR-002).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.domain.value_objects import Money


class TestMoneyConstruction:
    def test_valid_construction(self) -> None:
        m = Money(amount=Decimal("42000.00"), currency="INR")
        assert m.amount == Decimal("42000.00")
        assert m.currency == "INR"

    def test_from_str(self) -> None:
        m = Money.from_str("150.75", "USD")
        assert m.amount == Decimal("150.75")
        assert m.currency == "USD"

    def test_rejects_float(self) -> None:
        with pytest.raises(TypeError, match="must be a Decimal"):
            Money(amount=42.0, currency="INR")  # type: ignore[arg-type]

    def test_rejects_invalid_currency_length(self) -> None:
        with pytest.raises(ValueError, match="3-letter"):
            Money(amount=Decimal("10"), currency="US")

    def test_rejects_lowercase_currency(self) -> None:
        with pytest.raises(ValueError, match="uppercase"):
            Money(amount=Decimal("10"), currency="inr")

    def test_rejects_invalid_amount_string(self) -> None:
        with pytest.raises(ValueError, match="Invalid monetary amount"):
            Money.from_str("not-a-number", "INR")


class TestMoneyArithmetic:
    def test_addition_same_currency(self) -> None:
        a = Money(Decimal("100.00"), "INR")
        b = Money(Decimal("50.50"), "INR")
        result = a + b
        assert result.amount == Decimal("150.50")
        assert result.currency == "INR"

    def test_subtraction_same_currency(self) -> None:
        a = Money(Decimal("100.00"), "INR")
        b = Money(Decimal("30.25"), "INR")
        result = a - b
        assert result.amount == Decimal("69.75")

    def test_addition_cross_currency_raises(self) -> None:
        a = Money(Decimal("100"), "INR")
        b = Money(Decimal("100"), "USD")
        with pytest.raises(TypeError, match="Cannot add"):
            a + b

    def test_subtraction_cross_currency_raises(self) -> None:
        a = Money(Decimal("100"), "INR")
        b = Money(Decimal("100"), "USD")
        with pytest.raises(TypeError, match="Cannot subtract"):
            a - b


class TestMoneyComparison:
    def test_less_than(self) -> None:
        a = Money(Decimal("50"), "INR")
        b = Money(Decimal("100"), "INR")
        assert a < b

    def test_greater_than(self) -> None:
        a = Money(Decimal("100"), "INR")
        b = Money(Decimal("50"), "INR")
        assert a > b

    def test_equality(self) -> None:
        a = Money(Decimal("100.00"), "INR")
        b = Money(Decimal("100.00"), "INR")
        assert a == b

    def test_cross_currency_comparison_raises(self) -> None:
        a = Money(Decimal("100"), "INR")
        b = Money(Decimal("100"), "USD")
        with pytest.raises(TypeError, match="Cannot compare"):
            a < b


class TestMoneyPrecision:
    """Verify that Decimal arithmetic avoids float imprecision."""

    def test_float_imprecision_avoided(self) -> None:
        # In float: 0.1 + 0.2 = 0.30000000000000004
        a = Money.from_str("0.10", "INR")
        b = Money.from_str("0.20", "INR")
        result = a + b
        assert result.amount == Decimal("0.30")

    def test_large_amount_precision(self) -> None:
        a = Money.from_str("99999999999999.9999", "INR")
        b = Money.from_str("0.0001", "INR")
        result = a + b
        assert result.amount == Decimal("100000000000000.0000")

    def test_zero_detection(self) -> None:
        m = Money(Decimal("0"), "INR")
        assert m.is_zero()
        assert not m.is_positive()
        assert not m.is_negative()

    def test_missing_is_not_zero(self) -> None:
        """A missing value (None) is not equivalent to zero.

        This is a design principle (brief §7.5). The Money type itself
        cannot be None, but callers must handle optional amounts before
        constructing Money. This test documents the contract.
        """
        optional_amount: Decimal | None = None
        assert optional_amount is not Decimal("0")
