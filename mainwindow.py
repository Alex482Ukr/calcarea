# This Python file uses the following encoding: utf-8
import sys
from decimal import Decimal as Dec

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtGui import QIcon
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
        self.table.rows += 1
        print(self.ui.tableWidget.item(0, 0))
        self.table.custom_area(0, True)
        

class Table:
    def __init__(self, widget) -> None:
        self.__table = widget
        self.__table.itemChanged.connect(self.update)
    
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
    
    def update(self):
        self.__table.itemChanged.disconnect(self.update)



        self.__table.itemChanged.connect(self.update)

    def custom_area(self, row, flag):
        if flag:
            for col in (1, 2):
                self.__table.item(row, col).editable = False
            self.__table.item(row, 4).editable = True
        else:
            for col in (1, 2):
                self.__table.item(row, col).editable = True
            for col in (4, 5):
                self.__table.item(row, col).editable = False
        
    def fill_row(self, row):
        self.__table.setItem(row, 0, Item(str))
        self[row, 0] = 'A'
        

        for col in range(1, self.cols):
            item = Item()
            self.__table.setItem(row, col, item)
            self[row, col] = '0.00'
            item.edited.connect(lambda: print('asoi'))
        self.custom_area(row, False)

    def __getitem__(self, indx):
        return self.__table.item(*indx).text()

    def __setitem__(self, indx, value):
        self.__table.item(*indx).setText(value)

class Item(QTableWidgetItem):
    def __init__(self, value_type, rounding=None, raw=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_type = value_type
        self.rounding = rounding
        self.raw = raw   

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
            if self.value_type in (int, float, Dec) and self.rounding:
                text = round(text, self.rounding)
        
        super().setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
