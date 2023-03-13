"""
Модель бюджета.
"""

from dataclasses import dataclass


@dataclass
class Budget:
    period: str = ''
    amount: float = 0.0
    budget_all: float = 0.0
    budget_fix: float = 0.0
    pk: int = 0


