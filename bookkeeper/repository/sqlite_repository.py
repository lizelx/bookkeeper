"""
Модуль описывает репозиторий sqlite. Наследуется от класса абстрактного репозитория.
Репозиторий реализует хранение объектов, присваивая каждому объекту уникальный
идентификатор в атрибуте pk (primary key).
"""

import sqlite3
from typing import Any
from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T


def obj_make(cls: Any, fields: dict[Any, Any], values: str) -> Any:
    """
    Возвращает объект класса Expense, Category или Budget.
    """
    res = object.__new__(cls)
    if values is None:
        return None
    for attr, val in zip(fields.keys(), values):
        setattr(res, attr, val)
    setattr(res, 'pk', values[-1])
    return res


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, хранящий данные в базе данных.
    Реализует методы add(), get(), get_all(), update(),
    delete(), get_budget().
    """
    def __init__(self, db_file: str, cls: type) -> None:
        self.cls: type = cls
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            fileds_type = ' '.join([f"{field} TEXT," for field in self.fields])
            cur.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} ({fileds_type}'
                        f'pk INTEGER PRIMARY KEY)')

    def add(self, obj: T) -> T:
        """ Добавить объект в БД """
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj}'
                             f' with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        placeholder = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'INSERT INTO '
                        f'{self.table_name} ({names})'
                        f'VALUES({placeholder})', values)
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'SELECT * FROM {self.table_name} WHERE rowid = {pk}')
            res = obj_make(self.cls, self.fields, cur.fetchone())
        con.close()
        return res

    def get_all(self, where: dict[str, any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where is None:
                cur.execute(f'SELECT * FROM {self.table_name}')
            else:
                placeholder = " AND ".join(list(where.keys()))
                values = list(where.values())
                cur.execute(f"SELECT * FROM "
                            f"{self.table_name} "
                            f"WHERE {placeholder}", values)
            res = [obj_make(self.cls, self.fields, val) for val in cur.fetchall()]
        con.close()
        return res

    def update(self, obj: T) -> T:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
        if obj.pk == 0:
            raise ValueError(f'There is no object with {obj.pk} pk.')
        fields_str = ', '.join([f"{field}=?" for field in self.fields])
        self.cursor.execute(f"UPDATE {self.table_name} SET {fields_str} WHERE pk=?",
                            [getattr(obj, f) for f in self.fields] + [getattr(obj, 'pk')])
        self.conn.commit()
        return obj

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as con:
            if not self.check_pk(con.cursor(), pk):
                raise KeyError(f'No object with id={pk}.')
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE rowid = {pk}')
        con.close()

    def check_pk(self, cur: Any, pk: int) -> bool:
        """ Проверка на существование записей с существующим pk.
            Возвратит True если запись существует, и False если нет"""

        res = cur.execute(f'SELECT * FROM {self.table_name}'
                          f' WHERE rowid = {pk}').fetchone()
        return res is not None

    def get_budget(self) -> None:
        """ Рассчет бюджета за день. """

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            if len(cur.execute('SELECT * FROM expense').fetchall()) == 1:
                cur.execute('INSERT INTO '
                            'budget (period, amount, budget_all, budget_fix) VALUES'
                            '("День", 0, 1000, 1000)')
                cur.execute('INSERT INTO '
                            'budget (period, amount, budget_all, budget_fix) VALUES'
                            '("Неделя", 0, 7000, 7000)')
                cur.execute('INSERT INTO '
                            'budget (period, amount, budget_all, budget_fix) VALUES'
                            '("Месяц", 0, 30000, 30000)')
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) = DATE())'
                            ' WHERE period = "День"')
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) >= date(DATE(),'
                            ' "-7 days"))'
                            ' WHERE period = "Неделя"')
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) >= date(DATE(),'
                            ' "-30 days"))'
                            ' WHERE period = "Месяц"')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget.budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget WHERE budget.period = "День")'
                            ' WHERE budget.period = "День";')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget.budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget WHERE budget.period = "Неделя")'
                            ' WHERE budget.period = "Неделя";')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget.budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget WHERE budget.period = "Месяц")'
                            ' WHERE budget.period = "Месяц";')
            else:
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) = DATE())'
                            ' WHERE period = "День"')
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) >= date(DATE(),'
                            ' "-7 days"))'
                            ' WHERE period = "Неделя"')
                cur.execute('UPDATE budget SET amount = (select sum(amount)'
                            ' from expense where date(expense_date) >= date(DATE(),'
                            ' "-30 days"))'
                            ' WHERE period = "Месяц"')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget where budget.period = "День")'
                            ' where budget.period = "День";')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget WHERE budget.period = "Неделя")'
                            ' WHERE budget.period = "Неделя";')
                cur.execute('UPDATE budget SET budget_all ='
                            ' (select budget_all-(SELECT amount FROM expense'
                            ' ORDER BY pk DESC LIMIT 1)'
                            ' from budget WHERE budget.period = "Месяц")'
                            ' WHERE budget.period = "Месяц";')
