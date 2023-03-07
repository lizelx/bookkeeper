from dataclasses import dataclass
from datetime import datetime
from inspect import get_annotations


@dataclass
class Test:
    name: str
    pk: int = 0

class SQLiteRepository:
    def __init__(self, db_file:str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str = True)
        self.fields.pop('pk')

