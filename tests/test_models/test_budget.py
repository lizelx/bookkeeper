import pytest
from datetime import datetime

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget


@pytest.fixture
def repo():
    return MemoryRepository()


def test_create_with_full_args_list():
    b = Budget(period="День", amount=100, budget_all=400,
                budget_fix=500, pk=1)
    assert b.period == "День" and type(b.period) == str
    assert b.amount == 100
    assert b.budget_all == 400
    assert b.budget_fix == 500
    assert b.pk == 1


def test_create_brief():
    b = Budget("Вторник", 50, 600, 700, 2)
    assert b.period == "Вторник"
    assert b.amount == 50
    assert b.budget_all == 600
    assert b.budget_fix == 700
    assert b.pk == 2


def test_can_add_to_repo(repo):
    b = Budget("Вторник", 1, 7)
    pk = repo.add(b)
    assert b.pk == pk


