"""
Модель бюджета.
"""

from dataclasses import dataclass


@dataclass
class Budget:
    """
    Модель бюджета.
    Period - "День"/"Неделя/""Месяц"
    amount - сумма расходов в периоде.
    budget_all - остаток средств.(Фиксированная сумма на период - сумма расходов)
    budget_fix - фиксированная сумма на период.
    """
    period: str = ''
    amount: float = 0.0
    budget_all: float = 0.0
    budget_fix: float = 0.0
    pk: int = 0
