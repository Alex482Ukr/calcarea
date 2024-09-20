# This Python file uses the following encoding: utf-8
import sys
from traceback import format_exception_only, format_exception
from decimal import Decimal as Dec
from keyboard import add_hotkey
from pyperclip import copy
from openpyxl import Workbook

from typing import Iterable, Any, Iterator

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PySide6.QtGui import QIcon, QColor, QBrush, QCloseEvent
from PySide6.QtCore import Qt, Signal, Slot, QObject

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setting up window title and icon
        self.setWindowTitle('Calculator')
        icon = QIcon()
        icon.addFile('icons/icon.png')
        self.setWindowIcon(icon)

        # Setting up table
        self.table = Table(self.ui.tableWidget)
        self.table.area_sum_changed.connect(self.display_area_sum)
        self.ui.button_add_row.clicked.connect(self.add_row)
        self.ui.button_remove_row.clicked.connect(self.table.remove_current_row)
        self.ui.button_insert_row.clicked.connect(self.table.insert_after_current_row)

        # Implementing "Press Tab to add new line"
        try:
            add_hotkey('tab', self.tab_add_row)
        except ImportError as e:    # You must be root to use this library on linux.
            print('''"Press Tab to add new line" cannot be implemented:''')
            print(' keyboard:', *format_exception_only(e))

        # Setting up actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSaveAs.triggered.connect(self.save_as_file)
        self.ui.actionExport.triggered.connect(self.export_xlsx)

        # Current file you are working on, must be a path (full or relative)
        self.current_file = None

    @Slot(tuple)
    def display_area_sum(self, tpl: tuple[Dec, Dec, Dec]) -> None:
        '''Displays area sums in textboxes'''

        area_total, area_dw = tpl
        area_ec = area_total - area_dw

        self.ui.area_dwelling.setText(str(area_dw))
        self.ui.area_total.setText(str(area_total))
        self.ui.area_economical.setText(str(area_ec))

    @Slot()    
    def add_row(self) -> None:
        '''Adds a new row in table widget'''
        self.table.rows += 1
    
    @Slot()
    def open_file(self) -> None:
        '''Ask filename to open file'''

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
    def save_file(self) -> None:
        '''Ask filename to save in that file'''

        if self.current_file:
            self.table.write_file(self.current_file)
            return 'Success'
        else:
            return self.save_as_file()

    @Slot()
    def save_as_file(self) -> None:
        '''Ask filename to save as a file'''

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
    def export_xlsx(self) -> None:
        '''Ask filename to export as a .xlsx document'''
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

    def tab_add_row(self) -> None:
        '''Adds a new line in a table if Tab is pressed on the last item'''

        if self.table.rows and self.table.is_only_selected_item(self.table[-1][-1]):
            self.add_row()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        '''Trigger saving dialog before closing program'''

        if self.ask_save() == 'Accept':
            event.accept()
        else:
            event.ignore()
    
    def ask_save(self) -> str:
        '''Saving dialog'''

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


class Table(QObject):
    '''An interface to operate QTableWidgets'''

    area_sum_changed = Signal(tuple)    # Signal emitted when area sums are changed

    def __init__(self, widget: QTableWidget) -> None:
        super().__init__()
        self.__table = widget
        self.__table.itemChanged.connect(self.update)
        self.__table.itemSelectionChanged.connect(self.highlight_row)
    
    def __getitem__(self, indx: int | tuple[int, int] | Item) -> tuple[Item] | str | tuple[int, int]:
        '''Return row by given index
        or return item text by given tuple of item coordinates
        or return tuple of item coordinates of given item object'''

        if isinstance(indx, tuple):
            return self.__table.item(*indx).text()
        if isinstance(indx, Item):
            item = self.__table.indexFromItem(indx)
            return item.row(), item.column()
        return tuple(row for row in self)[indx]

    def __setitem__(self, indx: Iterable[int, int], value: Any) -> None:
        '''Setting text of item with given coordinates'''
        self.__table.item(*indx).setText(value)
    
    def __len__(self) -> int:
        '''Returns amount of rows in the table'''
        return self.rows
    
    def __iter__(self) -> Iterator[Item]:
        '''Returns iterator of Item objects in the table'''
        return iter(tuple(tuple(self.__table.item(row, col) for col in range(self.cols)) for row in range(self.rows)))
    
    @property
    def rows(self) -> int:
        '''Amount of table rows getter'''
        return self.__table.rowCount()
    @rows.setter
    def rows(self, num: int) -> None:
        '''Setting amount of rows in the table
        by removing or adding new rows'''

        filled_rows = self.rows
        self.__table.setRowCount(num)
        for row in range(filled_rows, self.rows):
            self.fill_row(row)
    
    @property
    def cols(self) -> int:
        '''Amount of table columns getter'''
        return self.__table.columnCount()
    
    def fill_row(self, row: int) -> None:
        '''Filling row with items with default values'''

        # Temporary disconnecting table updates 
        # to prevent huge amount of errors while filling row
        self.__table.itemChanged.disconnect(self.update)

        self.__table.setItem(row, 0, Item(str, 'A'))    # Filling "Letter" column

        for col in range(1, 4): # Filling "Width", "Length" and "Height" columns with rounding to hundredths
            self.__table.setItem(row, col, Item(Dec, rounding=2))
        
        self.__table.setItem(row, 4, Item(Dec, rounding=1)) # Filling "Area" column with rounding to tenths
        self.__table.setItem(row, 5, Item(Dec, rounding=0)) # Filling "Volume" column with rounding to whole numbers

        for col in (4, 5):  # Setting "Area" and "Volume" columns to not editable
            self[row][col].editable = False

        # Turns table updates back ON
        self.__table.itemChanged.connect(self.update)

    @Slot()
    def remove_current_row(self) -> None:
        '''Deleting highlited row'''

        items = list(map(lambda item: self[item], self.__table.selectedItems()))
        for row in map(lambda item: item[0], items):
            self.__table.removeRow(row)

        if items:   # Brings highlight back on it's place
            item = items[0]
            if item[0] < self.rows:
                self[item[0]][item[1]].setSelected(True)

    @Slot()
    def insert_after_current_row(self) -> None:
        '''Inserts an empty row after the highlighted one'''

        rows = list(map(lambda item: self[item][0], self.__table.selectedItems()))
        if rows:
            self.__table.insertRow(rows[0]+1)
            self.fill_row(rows[0]+1)
            self.update(self[rows[0]+1][-1])

    @Slot()
    def highlight_row(self) -> None:
        '''Highlighting all rows that have a selected item'''

        self.unhighlight_all()

        for row in map(lambda item: self[item][0], self.__table.selectedItems()):
            for col in range(self.cols):
                self[row][col].setBackground(QColor(255, 255, 204))
    
    def unhighlight_all(self) -> None:
        '''Unhighliting all rows in the table'''

        for row in self:
            for item in row:
                item.setBackground(QBrush())

    @Slot(Item)
    def update(self, item: Item) -> None:   # Takes a link to the changed item
        '''The main table update loop'''

        try:
            # Temporary disconnecting table updates to prevent recursion
            self.__table.itemChanged.disconnect(self.update)

            self.count_area()
            self.count_volume()
            self.composite_area()
            self.sum_area()

        finally: # Always turns table updates back ON
            self.__table.itemChanged.connect(self.update)

    def count_area(self) -> None:
        '''Updates values in "Area" column'''

        for row in range(self.rows):
            self[row, 4] = self[row, 1] * self[row, 2]
    
    def count_volume(self) -> None:
        '''Updates values in "Volume" column'''

        for row in range(self.rows):
            self[row, 5] = self[row, 3] * self[row, 4]

    def sum_area(self) -> None:
        '''Updates area sum'''

        sum_ = Dec('0')     # Total area
        sum_a = Dec('0')    # Dwelling area

        for row in range(len(self)):
            if not self[row, 0][0].startswith('+'):
                sum_ += self[row, 4]

            # Adding item value in dwelling area sum if it's row has first character 'A' in the "Letter" column
            if self[row, 0][0] in ('A', 'a', 'А', 'а'):
                sum_a += self[row, 4]

        # Emits the signal with tuple of counted sums as an argument
        self.area_sum_changed.emit((sum_, sum_a))

    def composite_area(self) -> None:
        '''If row has first character '+' in "Letter" column it will add it's area value to previous row value'''

        # Starting iteration of table rows in reverse,
        # so it can sum area values by chain to the top row, that has no '+'
        for row in range(self.rows-1, -1, -1):
            if self[row, 0].startswith('+'):
                if row == 0:
                    self[row, 0] = self[row, 0].replace('+', '')    # Deleting '+' from "Letter" value if it has no rows above
                else:
                    for col in (4, 5):
                        self[row-1, col] = self[row-1][col].value + self[row][col].value
                        self[row][col].setBackground(QColor(255, 240, 200))     # Highlighting row that is added
                        self[row-1][col].setBackground(QColor(220, 255, 220))   # Highlighting row to which is added with different color

    def is_only_selected_item(self, item: Item) -> bool:
        '''Returns True if given item is the only selected item'''
        return self.__table.selectedItems() == [item]

    def load_file(self, path: str) -> None:
        '''Loading table from the file'''

        with open(path, 'rt', encoding='utf-8') as f:
            rows = tuple(row.split(',') for row in f.read().split('\n'))
            self.rows = len(rows)
            if rows:
                for row in range(len(rows)):
                    for col in range(len(rows[0])):
                        self[row, col] = rows[row][col]


    def write_file(self, path: str) -> None:
        '''Writing the table in file'''

        with open(path, 'wt', encoding='utf-8') as f:
            f.write('\n'.join(','.join(str(self[row, col]) for col in range(4)) for row in range(len(self))))
    
    def write_xlsx(self, path: str) -> None:
        '''Exporting table to .xlsx (currently not used)'''

        wb = Workbook()
        ws = wb.active
        for row in self:
            ws.append(tuple(map(lambda item: item.text(), row)))
        wb.save(path)



def excepthook(cls: type, exception: Exception, traceback):
    '''Catches errors and showing them in dialog box'''
    
    exc_type = cls.__name__                         # Type of the exception (e. g. "ZeroDivisionError")
    exc = ''.join(format_exception_only(exception)) # Exception type with message (e. g. "ZeroDivisionError: division by zero")
    exc_full = ''.join(format_exception(exception)) # Whole traceback with exception type and message
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(exc_type)
    msg.setText("Сталася помилка")
    msg.setInformativeText(exc)
    msg.setDetailedText(exc_full)
    
    msg.addButton('OK', QMessageBox.YesRole)
    
    copy_button = msg.addButton('Копіювати', QMessageBox.ActionRole)
    copy_button.clicked.connect(lambda: copy(exc_full)) # Copying to clipboard
    
    terminate_program_button = msg.addButton('Зупинити', QMessageBox.ActionRole)
    terminate_program_button.clicked.connect(lambda: sys.exit(1)) # Terminating program
    
    msg.exec()

if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
