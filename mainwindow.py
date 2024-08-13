# This Python file uses the following encoding: utf-8
import sys
from decimal import Decimal as Dec
from keyboard import add_hotkey

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtGui import QIcon, QColor, QBrush
from PySide6.QtCore import Qt, Signal, Slot, QObject

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Calculator')
        icon = QIcon()
        icon.addFile('icons/icon.png')
        self.setWindowIcon(icon)

        self.table = Table(self.ui.tableWidget)
        self.table.area_sum_changed.connect(self.display_area_sum)
        self.ui.button_add_row.clicked.connect(self.add_row)
        self.ui.button_remove_row.clicked.connect(self.table.remove_current_row)
        self.ui.button_insert_row.clicked.connect(self.table.insert_after_current_row)

        add_hotkey('tab', self.tab_add_row)

    @Slot(tuple)
    def display_area_sum(self, tpl):
        area_total, area_dw = tpl
        area_ec = area_total - area_dw

        self.ui.area_dwelling.setText(str(area_dw))
        self.ui.area_total.setText(str(area_total))
        self.ui.area_economical.setText(str(area_ec))

    @Slot()    
    def add_row(self):
        self.table.rows += 1

    def tab_add_row(self):
        if self.table.rows and self.table.is_only_selected_item(self.table[-1][-1]):
            self.add_row()


class Table(QObject):
    area_sum_changed = Signal(tuple)

    def __init__(self, widget) -> None:
        super().__init__()
        self.__table = widget
        self.__table.itemChanged.connect(self.update)
        self.__table.itemSelectionChanged.connect(self.highlight_row)
    
    def __getitem__(self, indx):
        if isinstance(indx, tuple):
            return self.__table.item(*indx).text()
        if isinstance(indx, Item):
            item = self.__table.indexFromItem(indx)
            return item.row(), item.column()
        return tuple(row for row in self)[indx]

    def __setitem__(self, indx, value):
        self.__table.item(*indx).setText(value)
    
    def __len__(self):
        return self.rows
    
    def __iter__(self):
        return iter(tuple(tuple(self.__table.item(row, col) for col in range(self.cols)) for row in range(self.rows)))
    
    @property
    def rows(self):
        return self.__table.rowCount()
    @rows.setter
    def rows(self, num):
        filled_rows = self.rows
        self.__table.setRowCount(num)
        for row in range(filled_rows, self.rows):
            self.fill_row(row)
    
    @property
    def cols(self):
        return self.__table.columnCount()
    
    def fill_row(self, row):
        self.__table.itemChanged.disconnect(self.update)

        self.__table.setItem(row, 0, Item(str, 'A'))

        for col in range(1, 4):
            self.__table.setItem(row, col, Item(Dec, rounding=2))
        
        self.__table.setItem(row, 4, Item(Dec, rounding=1))
        self.__table.setItem(row, 5, Item(Dec, rounding=0))

        for col in (4, 5):
            self[row][col].editable = False

        self.__table.itemChanged.connect(self.update)

    @Slot()
    def remove_current_row(self):
        items = list(map(lambda item: self[item], self.__table.selectedItems()))
        for row in map(lambda item: item[0], items):
            self.__table.removeRow(row)

        if items:
            item = items[0]
            if item[0] > 0:
                self[item[0]-1][item[1]].setSelected(True)

    @Slot()
    def insert_after_current_row(self):
        rows = list(map(lambda item: self[item][0], self.__table.selectedItems()))
        if rows:
            self.__table.insertRow(rows[0]+1)
            self.fill_row(rows[0]+1)
            self.update(self[rows[0]+1][-1])

    @Slot()
    def highlight_row(self):
        self.unhighlight_all()

        for row in map(lambda item: self[item][0], self.__table.selectedItems()):
            for col in range(self.cols):
                self[row][col].setBackground(QColor(255, 255, 204))
    
    def unhighlight_all(self):
        for row in self:
            for item in row:
                item.setBackground(QBrush())

    @Slot(QTableWidgetItem)
    def update(self, item):
        try:
            self.__table.itemChanged.disconnect(self.update)

            self.count_area()
            self.count_volume()
            self.composite_area()
            self.sum_area()

        finally:
            self.__table.itemChanged.connect(self.update)

    def count_area(self):
        for row in range(self.rows):
            self[row, 4] = self[row, 1] * self[row, 2]
    
    def count_volume(self):
        for row in range(self.rows):
            self[row, 5] = self[row, 3] * self[row, 4]

    def sum_area(self):
        sum_ = Dec('0')
        sum_a = Dec('0')

        for row in range(len(self)):
            if not self[row, 0][0].startswith('+'):
                sum_ += self[row, 4]
            if self[row, 0][0] in ('A', 'a', 'А', 'а'):
                sum_a += self[row, 4]

        self.area_sum_changed.emit((sum_, sum_a))

    def composite_area(self):
        for row in range(self.rows-1, -1, -1):
            if self[row, 0].startswith('+'):
                if row == 0:
                    self[row, 0] = self[row, 0].replace('+', '')
                else:
                    for col in (4, 5):
                        self[row-1, col] = self[row-1][col].value + self[row][col].value
                        self[row][col].setBackground(QColor(255, 240, 200))
                        self[row-1][col].setBackground(QColor(220, 255, 220))

    def is_only_selected_item(self, item):
        return self.__table.selectedItems() == [item]


class Item(QTableWidgetItem):
    def __init__(self, value_type, value=None, rounding=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_type = value_type
        self.rounding = rounding
        self.value = value

        if not value:
            value = value_type()
        self.default = value

        self.setText(str(value))   

    def __str__(self):
        return str(self.text())

    def __add__(self, other):
        if self.value_type != other.value_type:
            raise TypeError(f'Items value types not matching: {self.value_type} and {other.value_type}')
        return self.text() + other.text()

    @property
    def editable(self):
        return Qt.ItemIsEditable in self.flags()
    @editable.setter
    def editable(self, flag):
        if flag:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
        else:
            self.setFlags(self.flags() & ~Qt.ItemIsEditable)
    
    def setText(self, text):
        text = self.verify_value(text)
        self.value = text

        if self.value_type in (int, float, Dec) and self.rounding is not None:
            text = self.round(text, self.rounding)

        super().setText(str(text))
    
    def set_raw_text(self, text):
        super().setText(str(text))
    
    def text(self):
        text = self.verify_value(super().text())

        if not text:
            self.setText(self.default)
            return self.default
        
        return text
    
    @staticmethod
    def round(num, rounding):
        num += Dec('0.000000001')
        return round(num, rounding)
    
    def verify_value(self, value):
        if not value:
            value = self.default
        else:
            value = str(value).replace(',', '.')
            value = str(value).replace('ё', "'")
            try:
                value = self.value_type(value)
            except:
                value = self.default

        self.set_raw_text(value)
        return value


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
