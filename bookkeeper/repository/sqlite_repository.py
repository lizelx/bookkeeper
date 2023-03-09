import sqlite3
from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T
from typing import Any
from dataclasses import dataclass
from datetime import datetime
from inspect import get_annotations





class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.cls: type = cls
        self.db_file = db_file
        self.table_name = cls.__name__.lower()

        self.fields = get_annotations(cls, eval_str=True)
        names = ', '.join(self.fields.keys())
        self.fields.pop('pk')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} ({names})')
            print(self.fields)
            #con.close()


    def add(self, obj: T) -> int:
        """ Добавить объект в БД """

        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(
                f'INSERT INTO {self.table_name} ({names}) VALUES ({p})', values
            )
            con.commit()
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk

    def convert_object_datetime(self, final: list | tuple) -> tuple:
        obj = self.cls(*final)
        converted_temp = tuple()
        for i in range(len(final)):
            try:
                converted_temp += (list(obj.__annotations__.values())[i](final[i]),)
            except TypeError:
                if type(final[i]) == "<class 'datetime.datetime>'":
                    converted_temp += (list(obj.__annotations__.values(
                    ))[i].strptime(final[i], '%Y-%m-%d %H:%M:%S'),)
                elif final[i] is None:
                    converted_temp += (final[i],)
                else:
                    converted_temp += (type(final[i])(final[i]),)
        return converted_temp

    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute(f'SELECT * FROM {self.table_name} WHERE pk = {pk}')
            final = res.fetchone()
        con.close()
        if final is None:
            return None
        return self.cls(*self.convert_object_datetime(final))

    def get_all(self, where: dict[str, any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            res = cur.execute(f'SELECT * FROM {self.table_name}')
            if where is None:
                return [self.cls(*self.convert_object_datetime(temp))
                        for temp in res.fetchall()]
            objs = []
            for temp in res.fetchall():
                obj = self.cls(*self.convert_object_datetime(temp))
                if all([getattr(obj, attr) == value for attr, value in where.items()]):
                    objs.append(obj)
        con.close()
        return objs

    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """


        pass

    def delete(self, pk: int) -> None:
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as con:
            if not self.check_pk(con.cursor(), pk):
                raise KeyError(f'No object with id={pk}.')
            cur = con.cursor()
            cur.execute(f'DELETE FROM {self.table_name} WHERE id = {pk}') \
        con.close()


def check_pk(self, cur: Any, pk: int) -> bool:
    """ Проверка на существование записей с существующим pk.
        Возвратит True если запись существует, и False если нет"""

    query = f'SELECT * FROM {self.table_name} WHERE id = {pk}'
    res = cur.execute(query).fetchone()
    return res is not None

#         if not self.is_pk_in_db(con.cursor(), obj.pk):
#             raise ValueError(f'trying to add object id={obj.pk} in DB.')