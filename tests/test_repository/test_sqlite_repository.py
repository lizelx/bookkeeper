from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.category import Category
import pytest

repo = SQLiteRepository('test.db', Category)


def test_crud():
    """ add """
    obj = Category('Food', 2)
    obj2 = Category('Pizza', 1)
    obj3 = Category('Flowers', 3)
    pk = repo.add(obj)
    repo.add(obj2)
    repo.add(obj3)
    assert str(obj.name) == 'Food'
    assert obj.parent == 2

    """ get """
    obj_get: Category = repo.get(pk)
    assert str(obj.name) == str(obj_get.name)
    assert str(obj.parent) == str(obj_get.parent)
    assert str(obj.pk) == str(obj_get.pk)

    """ update """
    obj2 = Category('Meat', 2)
    obj2.pk = pk
    repo.update(obj2)
    obj_get: Category = repo.get(pk)
    obj_test: Category = Category('Meat', 2)
    obj_test.pk = pk
    assert str(obj_get.name) == str(obj_test.name)
    assert str(obj_get.parent) == str(obj_test.parent)
    assert str(obj_get.parent) == str(obj_test.parent)

    """ delete """
    repo.delete(pk)
    assert repo.get(pk) is None


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
