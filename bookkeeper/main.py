from PySide6.QtWidgets import QApplication
from bookkeeper.models.category import Category
from bookkeeper.utils import read_tree
from bookkeeper.view.expense_view import MainWindow
from bookkeeper.presenter.expense_presenter import ExpensePresenter
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SQLiteRepository
import sys

DB_NAME = 'test2.db'


if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = MainWindow()
    model = None  # TODO: здесь должна быть модель

    cat_repo = SQLiteRepository[Category](DB_NAME, Category)
    exp_repo = SQLiteRepository[Expense](DB_NAME, Expense)
    bud_repo = SQLiteRepository[Budget](DB_NAME, Budget)


    cats = '''
    1.продукты
        2.мясо
            3.сырое мясо
            4.мясные продукты
        5.сладости
    6.книги
    7.одежда
    '''.splitlines()

    Category.create_from_tree(read_tree(cats), cat_repo)

    #window = ExpensePresenter(model, view, cat_repo, exp_repo)  # TODO: передать три репозитория
    window = ExpensePresenter(model, view, cat_repo, exp_repo, bud_repo)
    window.show()
    app.exec_()