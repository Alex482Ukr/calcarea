# This Python file uses the following encoding: utf-8
import sys
from decimal import Decimal as Dec

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtGui import QIcon, QColor
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
        self.ui.pushButton.clicked.connect(self.add_row)

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

    @Slot()    
    def remove_row(self):
        self.table.rows -= 1


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
        return tuple(self.__table.item(indx, col) for col in range(self.cols))

    def __setitem__(self, indx, value):
        self.__table.item(*indx).setText(value)
    
    def __len__(self):
        return self.rows
    
    def __iter__(self):
        for row in range(self.rows):
            yield self[row]
    
    @property
    def rows(self):
        return self.__table.rowCount()
    @rows.setter
    def rows(self, num):
        self.__table.itemChanged.disconnect(self.update)

        filled_rows = self.rows
        self.__table.setRowCount(num)
        for row in range(filled_rows, self.rows):
            self.fill_row(row)
        
        self.__table.itemChanged.connect(self.update)
    
    @property
    def cols(self):
        return self.__table.columnCount()
    
    def fill_row(self, row):
        self.__table.setItem(row, 0, Item(str, 'A'))

        for col in range(1, 4):
            self.__table.setItem(row, col, Item(Dec, rounding=2))
        
        self.__table.setItem(row, 4, Item(Dec, rounding=1))
        self.__table.setItem(row, 5, Item(Dec, rounding=0))

        self.custom_area(row, False)

    @Slot()
    def highlight_row(self):
        self.unhighlight_all()

        for row in map(lambda item: self[item][0], self.__table.selectedItems()):
            for col in range(self.cols):
                self[row][col].setBackground(QColor(255, 255, 204))
    
    def unhighlight_all(self):
        for row in self:
            for item in row:
                item.setBackground(QColor(255, 255, 255))

    @Slot(QTableWidgetItem)
    def update(self, item):
        try:
            self.__table.itemChanged.disconnect(self.update)
            row, col = self[item]

            self.count_area(row)
            self.sum_area()
            self.count_volume(row)

        finally:
            self.__table.itemChanged.connect(self.update)

    def count_area(self, row):
        self[row, 4] = self[row, 1] * self[row, 2]
    
    def count_volume(self, row):
        self[row, 5] = self[row, 3] * self[row, 4]

    def sum_area(self):
        sum_ = Dec('0')
        sum_a = Dec('0')

        for row in range(len(self)):
            sum_ += self[row, 4]
            if self[row, 0][0] in ('A', 'a', 'А', 'а'):
                sum_a += self[row, 4]

        self.area_sum_changed.emit((sum_, sum_a))


    def custom_area(self, row, flag):
        if flag:
            for col in (1, 2):
                self[row][col].editable = False
            self[row][4].editable = True
        else:
            for col in (1, 2):
                self[row][col].editable = True
            for col in (4, 5):
                self[row][col].editable = False
                

class Item(QTableWidgetItem):
    def __init__(self, value_type, value=None, rounding=None, raw=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_type = value_type
        self.rounding = rounding
        self.raw = raw

        if not value:
            value = value_type()
        self.default = value
        self.setText(str(value))   

    @property
    def editable(self):
        return Qt.ItemIsEditable in self.flags()
    @editable.setter
    def editable(self, flag):
        if flag:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
        else:
            self.setFlags(self.flags() & ~Qt.ItemIsEditable)
    
    @property
    def raw(self):
        return self._raw
    @raw.setter
    def raw(self, value):
        self._raw = value
    
    def setText(self, text):
        if not self.raw:
            text = self.value_type(text)
            if self.value_type in (int, float, Dec) and self.rounding is not None:
                text = self.round(text, self.rounding)

        super().setText(str(text))
    
    def text(self):
        text = self.value_type(super().text())
        if not text and not self.raw:
            self.reset()
            return self.default
        return text
    
    def round(self, num, rounding):
        num += Dec('0.000000001')
        return round(num, rounding)
    
    def reset(self):
        self.setText(self.default)

    def __str__(self):
        return str(self.text())


    def __add__(self, other):
        if self.value_type != other.value_type:
            raise TypeError(f'Items value types not matching: {self.value_type} and {other.value_type}')
        return self.text() + other.text()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())