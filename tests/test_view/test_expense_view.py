from bookkeeper.view.expense_view import MainWindow
import pytest


@pytest.fixture
def test_input_expense(qtbot):
    widget = MainWindow()
    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.amount_line_edit, '123')
    qtbot.keyClicks(widget.comment_line_edit, 'хлеб')
    assert widget.amount_line_edit.text() == '123'
    assert widget.get_amount() == 123

    assert widget.comment_line_edit.text() == 'хлеб'
    assert widget.get_comment() == 'хлеб'



