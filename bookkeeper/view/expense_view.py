from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget,\
    QGridLayout, QComboBox, QLineEdit, QPushButton
from PySide6 import QtCore, QtWidgets
from bookkeeper.view.categories_view import CategoryDialog


class TableModel(QtCore.QAbstractTableModel):
    """
    Отображение табличного виджета.
    """
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
        if len(self._data[0].__dataclass_fields__.keys()) == 6:
            fields_dict = dict.fromkeys(self._data[0].__dataclass_fields__.keys())
            fields_dict['amount'] = 'Сумма'
            fields_dict['category'] = 'Категория'
            fields_dict['expense_date'] = 'Дата'
            fields_dict['added_date'] = 'Добавлено в БД'
            fields_dict['comment'] = 'Комментарий'
            self.header_names = list(fields_dict.values())

        if len(self._data[0].__dataclass_fields__.keys()) == 5:
            fields_dict = dict.fromkeys(self._data[0].__dataclass_fields__.keys())
            fields_dict['period'] = 'Период'
            fields_dict['amount'] = 'Сумма'
            fields_dict['budget_all'] = 'Остаток'
            fields_dict['budget_fix'] = 'Бюджет'
            self.header_names = list(fields_dict.values())

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        Заголовки колонок.
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_names[section]
        return super().headerData(section, orientation, role)

    def data(self, index, role):
        """
        ...
        """
        if role == QtCore.Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            fields = list(self._data[index.row()].__dataclass_fields__.keys())
            return self._data[index.row()].__getattribute__(fields[index.column()])

    def rowCount(self, index) -> int:
        """
        Для подгона размеров таблицы.
        """
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index) -> int:
        """
        Для подгона размеров таблицы.
        """
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0].__dataclass_fields__)


class MainWindow(QtWidgets.QMainWindow):
    """
    Главное окно программы.
    """
    def __init__(self):
        super().__init__()

        self.item_model = None
        self.item_model_budget = None

        self.setWindowTitle("Программа для ведения бюджета")

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel('Последние расходы'))

        self.expenses_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.expenses_grid)

        self.layout.addWidget(QLabel('Бюджет'))
        self.budget_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.budget_grid)

        self.bottom_controls = QGridLayout()
        self.bottom_controls.addWidget(QLabel('Сумма'), 0, 0)
        self.amount_line_edit = QLineEdit()
        self.amount_line_edit.setPlaceholderText('Введите сумму покупки в рублях')

        self.bottom_controls.addWidget(self.amount_line_edit, 0, 1)
        self.bottom_controls.addWidget(QLabel('Категория'), 1, 0)

        self.category_dropdown = QComboBox()

        self.bottom_controls.addWidget(self.category_dropdown, 1, 1)

        self.category_edit_button = QPushButton('Редактировать')
        self.bottom_controls.addWidget(self.category_edit_button, 1, 2)
        self.category_edit_button.clicked.connect(self.show_cats_dialog)

        self.bottom_controls.addWidget(QLabel('Комментарий'), 2, 0)
        self.comment_line_edit = QLineEdit()
        self.comment_line_edit.setPlaceholderText('Например: Кофточка из Gloria Jeans')
        self.bottom_controls.addWidget(self.comment_line_edit, 2, 1)

        self.expense_add_button = QPushButton('Добавить')
        self.bottom_controls.addWidget(self.expense_add_button, 3, 1)

        self.expense_delete_button = QPushButton('Удалить')
        self.bottom_controls.addWidget(self.expense_delete_button, 2, 2)

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(self.bottom_controls)

        self.layout.addWidget(self.bottom_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def set_expense_table(self, data) -> None:
        """
        Настройка отображение размеров таблицы расходов.
        """
        if data:
            self.item_model = TableModel(data)
            self.expenses_grid.setModel(self.item_model)
            self.expenses_grid.resizeColumnsToContents()
            grid_width = sum([self.expenses_grid.columnWidth(x)
                              for x in range(0, self.item_model.columnCount(0) + 1)])
            self.setFixedSize(grid_width + 80, 600)

    def set_budget_table(self, data) -> None:
        """
        Настройка отображение размеров таблицы Бюджета.
        Ее размер зависит от размера таблицы Расходов.
        """
        if data:
            self.item_model = TableModel(data)
            self.budget_grid.setModel(self.item_model)

    def set_category_dropdown(self, data) -> None:
        """
        Выбор категории из выпадающего списка.
        """
        for cat in data:
            self.category_dropdown.addItem(cat.name, cat.pk)

    def on_expense_add_button_clicked(self, slot) -> None:
        """
        Сигнал при нажатии на кнопку Добавить.
        """
        self.expense_add_button.clicked.connect(slot)

    def get_comment(self) -> str:
        """
        Получение введенного комментария.
        """
        return str(self.comment_line_edit.text())

    def on_expense_delete_button_clicked(self, slot) -> None:
        """
        Сигнал при нажатии на кнопку удалить.
        """
        self.expense_delete_button.clicked.connect(slot)

    def get_amount(self) -> float:
        """
        Получение введенной суммы.
        """
        return float(self.amount_line_edit.text())

    def __get_selected_row_indices(self) -> list[int]:
        return list(set([qmi.row() for qmi in
                         self.expenses_grid.selectionModel().selection().indexes()]))

    def __get_selected_row_indices_budget(self) -> list[int]:
        return list(set([qmi.row() for qmi in
                         self.budget_grid.selectionModel().selection().indexes()]))

    def get_selected_expenses(self) -> list[int] | None:
        """
        Выбор расхода.
        """
        idx = self.__get_selected_row_indices()
        if not idx:
            return None
        return [self.item_model._data[i].pk for i in idx]

    def get_selected_budget(self) -> list[int] | None:
        """
        Выбор бюджета.
        """
        idx = self.__get_selected_row_indices_budget()
        if not idx:
            return None
        return [self.item_model._data[i].pk for i in idx]

    def get_selected_cat(self) -> int:
        """
        Выбор категории.
        """
        return self.category_dropdown.itemData(self.category_dropdown.currentIndex())

    def on_category_edit_button_clicked(self, slot) -> None:
        """
        Сигнал при нажатии на кнопку редактировать.
        """
        self.category_edit_button.clicked.connect(slot)

    def show_cats_dialog(self, data: list) -> None:
        """
        Диалоговое окно редактирования категорий.
        Не реализовано
        """
        if data:
            cat_dlg = CategoryDialog(data)
            cat_dlg.setWindowTitle('Редактирование категорий')
            cat_dlg.setGeometry(300, 100, 600, 300)
            cat_dlg.exec_()
