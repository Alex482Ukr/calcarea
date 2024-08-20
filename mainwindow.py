# This Python file uses the following encoding: utf-8
import sys
from traceback import format_exception_only, format_exception
from decimal import Decimal as Dec
from keyboard import add_hotkey
from pyperclip import copy
from openpyxl import Workbook

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
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

        try:
            add_hotkey('tab', self.tab_add_row)
        except ImportError as e:
            print('''"Press Tab to add new line" cannot be implemented:''')
            print(' keyboard:', *format_exception_only(e))

        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSaveAs.triggered.connect(self.save_as_file)
        self.ui.actionExport.triggered.connect(self.export_xlsx)

        self.current_file = None

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
    def open_file(self):
        path = QFileDialog.getOpenFileName(parent=self, 
                                           caption="Відкрити", 
                                           dir='save.csv', 
                                           filter="Comma separated values (*.csv);;Всі файли (*.*)",
                                           )[0]
        if path:
            self.current_file = path
            self.setWindowTitle(self.current_file)
            self.table.load_file(path)
        
    @Slot()
    def save_file(self):
        if self.current_file:
            self.table.write_file(self.current_file)
            return 'Success'
        else:
            return self.save_as_file()

    @Slot()
    def save_as_file(self):
        path = QFileDialog.getSaveFileName(parent=self, 
                                           caption="Зберегти як", 
                                           dir='save.csv', 
                                           filter="Comma separated values (*.csv);;Всі файли (*.*)",
                                           )[0]
        if path:
            self.current_file = path
            self.setWindowTitle(self.current_file)
            self.table.write_file(path)
            return 'Success'
        
    @Slot()
    def export_xlsx(self):
        if self.ask_save() == "Ignore":
            return

        default_path = self.current_file.split('.')[0] + '.xlsx' if self.current_file else "export.xlsx"
        path = QFileDialog.getSaveFileName(parent=self, 
                                           caption="Експортувати як",
                                           dir=default_path,
                                           filter="Таблиця Excel (*.xlsx);;Всі файли (*.*)",
                                           )[0]
        if path:
            self.table.write_xlsx(path)

    def tab_add_row(self):
        if self.table.rows and self.table.is_only_selected_item(self.table[-1][-1]):
            self.add_row()
    
    def closeEvent(self, event):
        if self.ask_save() == 'Accept':
            event.accept
        else:
            event.ignore()
    
    def ask_save(self):
        while True:
            if self.current_file or self.table.rows:
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Збереження")
                dlg.setText("Зберегти зміни?")
                dlg.setStandardButtons(QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)
                dlg.setIcon(QMessageBox.Question)
                button = dlg.exec()

                if button == QMessageBox.Save:
                    if self.save_file():
                        return "Accept"
                elif button == QMessageBox.No:
                    return "Accept"
                else:
                    return "Ignore"
            else:
                return "Accept"
                
        


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
            if item[0] < self.rows:
                self[item[0]][item[1]].setSelected(True)

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

    def load_file(self, path):
        with open(path, 'rt', encoding='utf-8') as f:
            rows = tuple(row.split(',') for row in f.read().split('\n'))
            self.rows = len(rows)
            if rows:
                for row in range(len(rows)):
                    for col in range(len(rows[0])):
                        self[row, col] = rows[row][col]


    def write_file(self, path):
        with open(path, 'wt', encoding='utf-8') as f:
            f.write('\n'.join(','.join(str(self[row, col]) for col in range(4)) for row in range(len(self))))
    
    def write_xlsx(self, path):
        wb = Workbook()
        ws = wb.active
        for row in self:
            ws.append(tuple(map(lambda item: item.text(), row)))
        wb.save(path)



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


def excepthook(cls, exception, tb):
    exc_type = cls.__name__
    exc = ''.join(format_exception_only(exception))
    exc_full = ''.join(format_exception(exception))
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(exc_type)
    msg.setText("Сталася помилка")
    msg.setInformativeText(exc)
    msg.setDetailedText(exc_full)
    msg.addButton('OK', QMessageBox.YesRole)
    copy_button = msg.addButton('Copy', QMessageBox.ActionRole)
    copy_button.clicked.connect(lambda: copy(exc_full))
    msg.exec()

if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
