"""
Модуль, обращающийся к БД и к главному окну.
"""
from bookkeeper.models.expense import Expense


class ExpensePresenter:
    """
    Позволяет обновлять отображение данных, при добавлении записи в БД.
    """
    def __init__(self, model, view, cat_repo, exp_repo, bud_repo):
        self.model = model
        self.view = view
        self.exp_repo = exp_repo

        self.exp_data = None
        self.cat_data = cat_repo.get_all()
        self.view.on_expense_add_button_clicked(self.handle_expense_add_button_clicked)
        self.view.on_expense_delete_button_clicked(self.handle_expense_delete_button_clicked)
        self.view.on_category_edit_button_clicked(self.handle_category_edit_button_clicked)
        self.bud_repo = bud_repo
        self.bud_data = bud_repo.get_all()

    def update_expense_data(self) -> None:
        """
        Попытка переименования номера категории в ее название.
        Не работает.
        """
        self.exp_data = self.exp_repo.get_all()
        for exp in self.exp_data:
            for cat in self.cat_data:
                if cat.pk == exp.category:
                    exp.category = cat.name
                    break
        self.view.set_expense_table(self.exp_data)

    def update_budget_data(self) -> None:
        """
        Обновление таблицы бюджета. Работает после добавления записи о расходе в БД.
        """
        self.bud_data = self.bud_repo.get_all()
        self.view.set_budget_table(self.bud_data)

    def show(self) -> None:
        """
        Показ окна и обновление таблиц расходов и бюджета.
        """
        self.view.show()
        self.update_expense_data()
        self.update_budget_data()
        self.view.set_category_dropdown(self.cat_data)

    def handle_expense_add_button_clicked(self) -> None:
        """
        Обработчик нажатия на кнопку Добавить.
        """
        cat_pk = self.view.get_selected_cat()
        amount = self.view.get_amount()
        comment = self.view.get_comment()
        exp = Expense(int(amount), cat_pk, comment=comment)
        self.exp_repo.add(exp)
        self.update_expense_data()
        self.bud_repo.get_budget()
        self.update_budget_data()

    def handle_expense_delete_button_clicked(self) -> None:
        """
        Обработчик нажатия на кнопку Удалить.
        """
        selected = self.view.get_selected_expenses()
        if selected:
            for exp in selected:
                self.exp_repo.delete(exp)
            self.update_expense_data()

    def handle_category_edit_button_clicked(self) -> None:
        """
        Обработчик нажатия на кнопку Изменить.
        """
        self.view.show_cats_dialog(self.cat_data)
