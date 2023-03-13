from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.category import Category
import pytest

repo = SQLiteRepository('test_db.db', Category)


def test_crud():
    """ add """
    obj = Category('Food', 2)
    food = repo.add(obj)
    print(food)
    assert str(obj.name) == 'Food'
    assert str(obj.parent) == '2'
    assert str(obj.pk) == '1'

    """ get """
    obj_get: Category = repo.get(obj.pk)
    assert str(obj.name) == str(obj_get.name)
    assert str(obj.parent) == str(obj_get.parent)
    assert str(obj.pk) == str(obj_get.pk)

    """ update """
    obj2 = Category('Meat', 2)
    obj2.pk = food
    repo.update(obj2)
    obj_get: Category = repo.get(food)
    obj_test: Category = Category('Meat', 2)
    obj_test.pk = food
    assert str(obj_get.name) == str(obj_test.name)
    assert str(obj_get.parent) == str(obj_test.parent)
    assert str(obj_get.parent) == str(obj_test.parent)

    """ delete """
    repo.delete(food)
    assert repo.get(food) is None


def test_cannot_add_with_pk():
    obj = Category('Fruit', 3)
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)

def test_cannot_add_without_pk():
    with pytest.raises(ValueError):
        repo.add(10)


def test_cannot_delete_not_exist():
    with pytest.raises(KeyError):
        repo.delete(5)


def test_cannot_update_without_pk():
    obj = Category('Lemon', 10)
    with pytest.raises(ValueError):
        repo.update(obj)
