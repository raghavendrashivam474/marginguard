"""MarginGuard domain value objects.

Value objects are immutable, compared by value, and have no identity of their own.
They must not import any infrastructure framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class Money:
    """Immutable monetary value combining an amount and a currency.

    Rules:
    - Amount must be a Decimal, never a float.
    - Currency must be a 3-letter ISO 4217 code.
    - Arithmetic between two Money values requires matching currencies.
    - Comparison between different currencies raises TypeError.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError(
                f"Money amount must be a Decimal, got {type(self.amount).__name__}. "
                "Use Decimal('42.00'), not float."
            )
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError(f"Currency must be a 3-letter ISO 4217 code, got {self.currency!r}")
        if self.currency != self.currency.upper():
            raise ValueError(f"Currency must be uppercase, got {self.currency!r}")

    @classmethod
    def from_str(cls, amount: str, currency: str) -> Money:
        """Construct from a string amount to avoid float imprecision."""
        try:
            return cls(amount=Decimal(amount), currency=currency)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid monetary amount: {amount!r}") from exc

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(
                f"Cannot add {self.currency} and {other.currency}. "
                "Convert to a common currency first."
            )
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(
                f"Cannot subtract {other.currency} from {self.currency}. "
                "Convert to a common currency first."
            )
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(f"Cannot compare {self.currency} and {other.currency}.")
        return self.amount < other.amount

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(f"Cannot compare {self.currency} and {other.currency}.")
        return self.amount <= other.amount

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(f"Cannot compare {self.currency} and {other.currency}.")
        return self.amount > other.amount

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise TypeError(f"Cannot compare {self.currency} and {other.currency}.")
        return self.amount >= other.amount

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    def is_positive(self) -> bool:
        return self.amount > Decimal("0")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0")
