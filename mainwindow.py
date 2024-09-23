# This Python file uses the following encoding: utf-8
import sys
from traceback import format_exception_only, format_exception
from decimal import Decimal as Dec
from json import dump, load
from os.path import exists

from typing import Any, Iterator, Iterable
from types import FunctionType

from keyboard import add_hotkey
from pyperclip import copy
# from openpyxl import Workbook # not used

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QWidget, QTableWidget, QTextBrowser, QPushButton, QLabel
from PySide6.QtGui import QIcon, QColor, QBrush, QCloseEvent, QFont
from PySide6.QtCore import Qt, Signal, Slot, QObject, QRect, QCoreApplication

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
        self.table.area_sum_changed.connect(self.connect_area_widgets((self.ui.area_total, self.ui.area_dwelling, self.ui.area_economical)))
        self.ui.button_add_row.clicked.connect(self.table.add_row)
        self.ui.button_remove_row.clicked.connect(self.table.remove_current_row)
        self.ui.button_insert_row.clicked.connect(self.table.insert_after_current_row)

        # Setting up actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSaveAs.triggered.connect(self.save_as_file)
        self.ui.actionExport.triggered.connect(self.export_xlsx)  # not used

        # Implementing 'Tab' to add new row
        try:
            add_hotkey('tab', self.tab_add_row)
        except ImportError as e:    # You must be root to use this library on linux.
            print('''"Press Tab to add new line" cannot be implemented:''')
            print(' keyboard:', *format_exception_only(e))
        
        self.ui.button_add_floor.clicked.connect(self.add_floor)
        self.ui.button_remove_floor.clicked.connect(self.remove_floor)
        self.ui.button_insert_floor.clicked.connect(self.insert_floor)

        # Current file you are working on, must be a path (full or relative)
        self.current_file = None

        # List of floors: 
        # list(tuple(Table, button_add_row, button_insert_row, button_remove_row, label_S, label_Sdw, label_Sec, area_total, area_dwelling, area_economical), ...)
        self.floors = []
        self.ui.tabWidget_floors.removeTab(0)   # Removing first demo tab (Floor n)

        # Open with this program
        if len(sys.argv) > 1:
            file = sys.argv[1]
            if exists(file):
                self.open_file(path=file)

    def connect_area_widgets(self, txt_browsers: tuple[QTextBrowser, QTextBrowser, QTextBrowser]) -> FunctionType:
        '''Returns a Slot that displays given areas in connected text browsers'''
        total_widget, dwelling_widget, economical_widget = txt_browsers

        @Slot(tuple)
        def slot(areas: tuple[Dec, Dec]) -> None:
            '''Displays given areas in connected text browsers'''
            area_total, area_dw = areas
            area_ec = area_total - area_dw

            dwelling_widget.setText(str(area_dw))
            total_widget.setText(str(area_total))
            economical_widget.setText(str(area_ec))
        return slot
    
    @Slot()
    def open_file(self, path=None) -> None:
        '''Load tables from file'''

        if not path:
            path = QFileDialog.getOpenFileName(parent=self, 
                                            caption="Відкрити", 
                                            dir='save.json', 
                                            filter="JavaScript Object Notation (*.json);;Comma Separated Values (*.csv);;Всі файли (*.*)",
                                            )[0]
        if path:
            if path.endswith('.csv'):   # For old save format support
                with open(path, 'rt', encoding='utf-8') as f:
                    rows = tuple(row.split(',') for row in f.read().split('\n'))
                    self.table.rows = len(rows)
                    if rows:
                        for row in range(len(rows)):
                            for col in range(len(rows[0])):
                                self.table[row, col] = rows[row][col]
                self.save_as_file()     # Resave with new format
            else:
                self.current_file = path
                self.setWindowTitle(self.current_file)

                with open(path, 'rt', encoding='utf-8') as f:
                    table, *tables = load(f)
                    self.table.load(table)

                    for i in range(len(self.floors)):
                        self.remove_floor()
                    self.floors = []

                    for i in range(len(tables)):
                        self.add_floor()
                        self.floors[i][0].load(tables[i])
        
    @Slot()
    def save_file(self) -> str:
        '''Save tables in the current file'''

        if self.current_file:
            with open(self.current_file, 'wt', encoding='utf-8') as f:
                tables = [self.table.get_matrix()]
                tables = tables + [floor[0].get_matrix() for floor in self.floors]
                dump(tuple(tables), f)
            return 'Success'
        else:
            return self.save_as_file()

    @Slot()
    def save_as_file(self) -> str:
        '''Save tables as a file'''

        path = QFileDialog.getSaveFileName(parent=self, 
                                           caption="Зберегти як", 
                                           dir='save.json', 
                                           filter="JavaScript Object Notation (*.json);;Всі файли (*.*)",
                                           )[0]
        if path:
            self.current_file = path
            self.setWindowTitle(self.current_file)
            self.save_file()
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

    @Slot()
    def add_floor(self) -> None:
        '''Adding new floor'''
        i = len(self.floors)
        self.floors.append(self.create_floor(i))
    
    @Slot()
    def remove_floor(self):
        '''Deleting current floor'''
        i = self.ui.tabWidget_floors.currentIndex()
        if i != -1:
            self.ui.tabWidget_floors.removeTab(i)
            del self.floors[i]
            self.enumerate_floors()
    
    @Slot()
    def insert_floor(self):
        '''Inserting new floor after current'''
        i = self.ui.tabWidget_floors.currentIndex()+1
        self.floors.insert(i, self.create_floor(i))
        self.enumerate_floors()

    def enumerate_floors(self) -> None:
        '''Reset numberation of floors'''
        for i in range(len(self.floors)):
            self.ui.tabWidget_floors.setTabText(i, f"Поверх {i+1}")
    
    @Slot(tuple)
    def sum_floors(self, areas: tuple[Dec, Dec]):
        '''Displaying area sum for all floors'''
        sum_total, sum_dwelling, sum_economical = [Dec('0')]*3

        for floor in self.floors:
            total_widget, dwelling_widget, economical_widget = floor[-3:]
            sum_total += Dec(total_widget.toPlainText())
            sum_dwelling += Dec(dwelling_widget.toPlainText())
            sum_economical += Dec(economical_widget.toPlainText())
        self.ui.area_total_floor.setText(str(sum_total))
        
        self.ui.area_dwelling_floor.setText(str(sum_dwelling))
        self.ui.area_economical_floor.setText(str(sum_economical))

    def tab_add_row(self) -> None:
        '''Adds a new line in a table if Tab is pressed on the last item'''
        table = self.current_table()
        item = self.current_item()

        if table and item:
            if self.current_item() == table[-1][-1]:
                table.add_row()
    
    def current_item(self) -> QTableWidgetItem | None:
        '''Returns first currently selected item'''

        table = self.current_table()
        if table:
            items = table.selectedItems
            return items[0] if items else None
    
    def current_table(self) -> QTableWidget:
        '''Returns current table'''

        tab1 = self.ui.tabWidget.currentIndex()
        tab2 = self.ui.tabWidget_floors.currentIndex()
        if tab1 == 0:
            return self.table
        elif self.floors:
            return self.floors[tab2][0]
    
    def create_floor(self, indx: int) -> tuple[QTableWidget, QPushButton, QPushButton, QPushButton, QLabel, QLabel, QLabel, QTextBrowser, QTextBrowser, QTextBrowser]:
        '''Creates new floor'''

        self.ui.tabWidget_floors.insertTab(indx, QWidget(), QIcon(), f'Поверх {indx+1}')
        parent = self.ui.tabWidget_floors.widget(indx)
        floor = []

        font = QFont()
        font.setPointSize(12)
        font_bold = QFont()
        font_bold.setPointSize(12)
        font_bold.setBold(True)

        # tableWidget
        table = QTableWidget(parent)
        table.setColumnCount(6)
        for i in range(6):
            table.setHorizontalHeaderItem(i, QTableWidgetItem())
        table.setObjectName(f"tableWidget_{indx}")
        table.setGeometry(QRect(0, 0, 461, 291))
        table.horizontalHeader().setDefaultSectionSize(70)
        table.show()
        table_obj = Table(table)

        # button_add_row
        button_add_row = QPushButton(parent)
        button_add_row.setObjectName(f"button_add_row_{indx}")
        button_add_row.setGeometry(QRect(480, 0, 201, 25))
        floor.append(button_add_row)

        # button_insert_row
        button_insert_row = QPushButton(parent)
        button_insert_row.setObjectName(f"button_insert_row_{indx}")
        button_insert_row.setGeometry(QRect(480, 30, 101, 25))
        floor.append(button_insert_row)

        # button_remove_row
        button_remove_row = QPushButton(parent)
        button_remove_row.setObjectName(f"button_remove_row_{indx}")
        button_remove_row.setGeometry(QRect(580, 30, 101, 25))
        floor.append(button_remove_row)

        # label_S
        label_S = QLabel(parent)
        label_S.setObjectName(f"label_S_{indx}")
        label_S.setGeometry(QRect(480, 130, 101, 31))
        label_S.setFont(font_bold)
        label_S.setAlignment(Qt.AlignCenter)
        floor.append(label_S)

        # label_Sdw
        label_Sdw = QLabel(parent)
        label_Sdw.setObjectName(f"label_Sdw_{indx}")
        label_Sdw.setGeometry(QRect(480, 70, 101, 31))
        label_Sdw.setFont(font)
        label_Sdw.setAlignment(Qt.AlignCenter)
        floor.append(label_Sdw)

        # label_Sec
        label_Sec = QLabel(parent)
        label_Sec.setObjectName(f"label_Sec_{indx}")
        label_Sec.setGeometry(QRect(480, 100, 101, 31))
        label_Sec.setFont(font)
        label_Sec.setAlignment(Qt.AlignCenter)
        floor.append(label_Sec)

        # area_total
        area_total = QTextBrowser(parent)
        area_total.setObjectName(f"area_total_{indx}")
        area_total.setGeometry(QRect(590, 130, 91, 31))
        floor.append(area_total)

        # area_dwelling
        area_dwelling = QTextBrowser(parent)
        area_dwelling.setObjectName(f"area_dwelling_{indx}")
        area_dwelling.setGeometry(QRect(590, 70, 91, 31))
        floor.append(area_dwelling)

        # area_economical
        area_economical = QTextBrowser(parent)
        area_economical.setObjectName(f"area_economical_{indx}")
        area_economical.setGeometry(QRect(590, 100, 91, 31))
        floor.append(area_economical)


        # retranslateUi
        ___qtablewidgetitem = table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0443\u043a\u0432\u0430", None))
        ___qtablewidgetitem1 = table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0438\u0440\u0438\u043d\u0430", None))
        ___qtablewidgetitem2 = table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0432\u0436\u0438\u043d\u0430", None))
        ___qtablewidgetitem3 = table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0441\u043e\u0442\u0430", None))
        ___qtablewidgetitem4 = table.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0449\u0430", None))
        ___qtablewidgetitem5 = table.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431'\u0454\u043c", None))

        button_add_row.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0434\u0430\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        button_insert_row.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        button_remove_row.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))

        label_S.setText(QCoreApplication.translate("MainWindow", u"S\u0437\u0430\u0433\u0430\u043b\u044c\u043d\u0430", None))
        label_Sdw.setText(QCoreApplication.translate("MainWindow", u"S\u0436\u0438\u0442\u043b\u043e\u0432\u0430", None))
        label_Sec.setText(QCoreApplication.translate("MainWindow", u"S\u0433\u043e\u0441\u043f", None))

        area_total.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        area_dwelling.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        area_economical.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))


        table_obj.area_sum_changed.connect(self.connect_area_widgets((area_total, area_dwelling, area_economical)))
        table_obj.area_sum_changed.connect(self.sum_floors)
        button_add_row.clicked.connect(table_obj.add_row)
        button_insert_row.clicked.connect(table_obj.insert_after_current_row)
        button_remove_row.clicked.connect(table_obj.remove_current_row)

        for widget in floor:
            widget.show()

        floor.insert(0, table_obj)
        return tuple(floor)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        '''Trigger saving dialog before closing program'''

        if self.ask_save() == 'Accept':
            event.accept()
        else:
            event.ignore()
    
    def ask_save(self) -> str:
        '''Saving dialog'''

        while True:
            if self.current_file or len(self.floors) != 0 or self.table.rows:
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
    def __init__(self, value_type, value=None, rounding=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value_type = value_type
        self.rounding = rounding
        self.value = value

        if not value:
            value = value_type()
        self.default = value

        self.setText(str(value))   

    def __str__(self) -> str:
        '''Return text of the item'''
        return str(self.text())

    def __add__(self, other) -> str | Dec:
        '''Add values of two Items'''
        if self.value_type != other.value_type:
            raise TypeError(f'Items value types not matching: {self.value_type} and {other.value_type}')
        return self.text() + other.text()

    @property
    def editable(self) -> bool:
        return Qt.ItemIsEditable in self.flags()
    @editable.setter
    def editable(self, flag) -> None:
        if flag:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
        else:
            self.setFlags(self.flags() & ~Qt.ItemIsEditable)
    
    def setText(self, text: Any) -> None:
        '''Setting text of the item'''
        text = self.verify_value(text)
        self.value = text

        if self.value_type in (int, float, Dec) and self.rounding is not None:
            text = self.round(text, self.rounding)

        super().setText(str(text))
    
    def set_raw_text(self, text: Any) -> None:
        '''Setting text directly'''
        super().setText(str(text))
    
    def text(self) -> str | Dec:
        text = self.verify_value(super().text())
        if not text:
            self.setText(self.default)
            return self.default
        return text
    
    @staticmethod
    def round(num: Dec, rounding: int) -> Dec:
        '''Rounding to the given number of decimal places'''
        num *= Dec('1.000000001')   # 0.5 rounding to 1
        return round(num, rounding)
    
    def verify_value(self, value: Any) -> Any:
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
    
    def __getitem__(self, indx: int | Iterable[int] | Item) -> tuple[Item] | (str | Dec) | tuple[int, int]:
        '''Return row by given index
        or return item text by given tuple of item coordinates
        or return tuple of item coordinates of given item object'''

        if isinstance(indx, tuple):
            return self.__table.item(*indx).text()
        if isinstance(indx, Item):
            item = self.__table.indexFromItem(indx)
            return item.row(), item.column()
        return tuple(row for row in self)[indx]

    def __setitem__(self, indx: Iterable[int], value: Any) -> None:
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
    
    @property
    def selectedItems(self) -> list[Item]:
        '''List of selected items getter'''
        return self.__table.selectedItems()
    
    @Slot()    
    def add_row(self) -> None:
        '''Adding row to the table'''
        self.rows += 1

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

        for col in (4, 5):   # Setting "Area" and "Volume" columns to not editable
            self[row][col].editable = False

        # Turns table updates back ON
        self.__table.itemChanged.connect(self.update)

    @Slot()
    def remove_current_row(self) -> None:
        '''Deleting selected row'''

        items = list(map(lambda item: self[item], self.__table.selectedItems()))
        for row in map(lambda item: item[0], items):
            self.__table.removeRow(row)

        if items:
            item = items[0]
            if item[0] < self.rows:
                self[item[0]][item[1]].setSelected(True)

    @Slot()
    def insert_after_current_row(self) -> None:
        '''Inserts an empty row after the selected one'''
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

    @Slot(QTableWidgetItem)
    def update(self, item: Item) -> None:   # Takes a link to the changed item
        '''The main table update loop'''
        try:
            # Temporary disconnecting table updates to prevent recursion
            self.__table.itemChanged.disconnect(self.update)

            self.count_area()
            self.count_volume()
            self.composite_area()
            self.sum_area()

        finally:    # Always turns table updates back ON
            self.__table.itemChanged.connect(self.update)

    def count_area(self) -> None:
        '''Updates values in "Area" column'''

        for row in range(self.rows):
            self[row, 4] = self[row, 1] * self[row, 2]
            if self[row, 0].startswith('-'):    # Inverting area value if "Letter" column in row starts with '-'
                self[row, 4] *= -1
    
    def count_volume(self) -> None:
        '''Updates values in "Volume" column'''

        for row in range(self.rows):
            self[row, 5] = self[row, 3] * self[row, 4]

    def sum_area(self) -> None:
        '''Updates area sum'''

        sum_ = Dec('0')     # Total area
        sum_a = Dec('0')    # Dwelling area

        for row in range(len(self)):
            if self[row, 0][0].startswith(('+', '-')):  # If "Letter" starts with '+' or '-' not adding to the sum
                continue
            sum_ += self[row, 4]
            
            # Adding item value in dwelling area sum if it's row has character 'A' or 'Ж' in the "Letter" column
            if not set(self[row, 0]).isdisjoint(('A', 'a', 'А', 'а', 'Ж', 'ж')):
                sum_a += self[row, 4]

        # Emits the signal with tuple of counted sums as an argument
        self.area_sum_changed.emit((sum_, sum_a))

    def composite_area(self) -> None:
        '''If row has first character '+' in "Letter" column it will add it's area value to previous row value'''

        # Starting iteration of table rows in reverse,
        # so it can sum area values by chain to the top row, that has no '+'
        for row in range(self.rows-1, -1, -1):
            if self[row, 0].startswith(('+', '-')):
                if row == 0:
                    self[row, 0] = self[row, 0].lstrip('+-')    # Deleting '+' and '-' from "Letter" value if it has no rows above
                else:
                    for col in (4, 5):
                        self[row-1, col] = self[row-1][col].value + self[row][col].value
                        self[row][col].setBackground(QColor(255, 240, 200))     # Highlighting row that is added
                        self[row-1][col].setBackground(QColor(220, 255, 220))   # Highlighting row to which is added with different color
            if self[row, 0].startswith('-'):
                for col in (4, 5):
                    self[row][col].setBackground(QColor(255, 200, 200))     # Highlighting row that is subtracted with another color

    def load(self, matrix: Iterable[Iterable]) -> None:
        '''Loading table from matrix'''

        self.rows = len(matrix)
        if matrix:
            for row in range(len(matrix)):
                for col in range(len(matrix[0])):
                    self[row, col] = matrix[row][col]


    def get_matrix(self) -> tuple[tuple]:
        '''Get matrix of table items'''
        return tuple(tuple(str(self[row, col]) for col in range(self.cols))[:-2] for row in range(self.rows))
    
    # def write_xlsx(self, path: str) -> None:
    #     '''Exporting table to .xlsx (currently not used)'''

    #     wb = Workbook()
    #     ws = wb.active
    #     for row in self:
    #         ws.append(tuple(map(lambda item: item.text(), row)))
    #     wb.save(path)



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
