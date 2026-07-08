# This Python file uses the following encoding: utf-8
import sys
from traceback import format_exception_only, format_exception
from decimal import Decimal as Dec
from json import dump, load
from os.path import exists

from typing import Any, Iterator, Iterable, SupportsIndex
from types import FunctionType

from keyboard import add_hotkey
from pyperclip import copy
# from openpyxl import Workbook # not used

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QWidget, QTextBrowser, QPushButton, QLabel, QCheckBox, QHBoxLayout, QSizePolicy, QLineEdit
from PySide6.QtGui import QIcon, QColor, QBrush, QCloseEvent, QFont
from PySide6.QtCore import Qt, Signal, Slot, QObject, QRect, QCoreApplication, QSize

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Setting up window title and icon
        self.setWindowTitle('Table Calculator')
        icon = QIcon()
        icon.addFile('icons/icon.png')
        self.setWindowIcon(icon)

        # Setting up table
        self.table = Table(self.ui.tableWidget, dw_checkbox=self.ui.checkBox)
        self.table.area_sum_changed.connect(self.connect_area_widgets((self.ui.area_total, self.ui.area_dwelling, self.ui.area_economical)))
        self.ui.button_add_row.clicked.connect(self.table.add_row)
        self.ui.button_remove_row.clicked.connect(self.table.remove_current_row)
        self.ui.button_insert_row.clicked.connect(self.table.insert_after_current_row)
        self.ui.checkBox.checkStateChanged.connect(self.table.dw_change)

        # Setting up actions
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)
        self.ui.actionSaveAs.triggered.connect(self.save_as_file)
        # self.ui.actionExport.triggered.connect(self.export_xlsx)  # not used

        # Implementing 'Tab' to add new row
        try:
            add_hotkey('tab', self.tab_add_row)
        except ImportError as e:    # You must be root to use this library on linux.
            print('''"Press Tab to add new line" cannot be implemented:''')
            print(' keyboard:', *format_exception_only(e))
        
        self.ui.button_add_floor.clicked.connect(self.add_floor)
        self.ui.button_remove_floor.clicked.connect(self.remove_floor)
        # self.ui.button_insert_floor.clicked.connect(self.insert_floor)    # Deprecated

        # Current file you are working on, must be a path (full or relative)
        self.current_file: str = None

        # List of floors: 
        # list(tuple(Table, checkBox, button_add_row, button_insert_row, button_remove_row, 
        #               label_S, label_Sdw, label_Sec, area_total, area_dwelling, area_economical), ...)
        self.floors: list[Floor] = []
        self.ui.tabWidget_floors.removeTab(0)   # Removing first demo tab (Floor n)

        # "Open with" implementation
        if len(sys.argv) > 1:
            file = sys.argv[1]
            if exists(file):
                self.open_file(path=file)

        # Editable floor names
        self.ui.tabWidget_floors.tabBarDoubleClicked.connect(self._on_tab_bar_double_clicked)

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
    def open_file(self, path: str = None) -> None:
        '''Load tables from file'''

        if not path:
            path = QFileDialog.getOpenFileName(parent=self, 
                                            caption="Відкрити", 
                                            dir='', 
                                            filter="CalcArea JSON / JavaScript Object Notation (*.cajs *.json);;Comma Separated Values (*.csv);;Всі файли (*.*)",
                                            )[0]
        if path:
            self.table.unhighlight_dw()
            self.table.dw_rows = []
            self.table.unhighlight_composite()
            if path.endswith('.csv'):   # For old save format support
                self.current_file = None
                self.setWindowTitle("Table Calculator")
                with open(path, 'rt', encoding='utf-8') as f:
                    rows = tuple(row.split(',') for row in f.read().split('\n'))
                    self.table.rows = len(rows)
                    if rows:
                        for row in range(len(rows)):
                            for col in range(len(rows[0])):
                                self.table[row, col] = rows[row][col]
                self.save_as_file()     # Resave with new format

            elif path.endswith('.json'):   # For old save format support
                self.current_file = None
                self.setWindowTitle("Table Calculator")
                with open(path, 'rt', encoding='utf-8') as f:
                    table, *tables = load(f)
                    self.table.load_json(table)

                    for i in range(len(self.floors)):
                        self.remove_floor()
                    self.floors = []

                    for i in range(len(tables)):
                        self.add_floor()
                        self.floors[i].table_obj.load_json(tables[i])
                self.sum_floors((0, 0))
                self.save_as_file()     # Resave with new format
            else:
                self.current_file = path
                self.setWindowTitle(self.current_file)
                self.table.highlight_row()

                with open(path, 'rt', encoding='utf-8') as f:
                    table, *tables = load(f)
                    self.table.load(table)
                
                for i in range(len(self.floors)):   # Remove all existing floors
                    self.remove_floor()
                self.floors = []
                
                for i in range(len(tables)):
                    self.add_floor(name=tables[i]["name"])
                    self.floors[i].table_obj.load(tables[i])
                self.sum_floors((0, 0))
        
    @Slot()
    def save_file(self) -> str:
        '''Save tables in the current file'''

        if self.current_file:
            with open(self.current_file, 'wt', encoding='utf-8') as f:
                tables = [{"name": "MAIN", "table": self.table.get_matrix(), "dw_rows": self.save_dw(self.table)}]

                self.sync_floor_list()

                tables = tables + [{"name": floor.tab_n.objectName(), "table": floor.table_obj.get_matrix(), "dw_rows": self.save_dw(floor.table_obj)} for floor in self.floors]
                dump(tuple(tables), f)
            return 'Success'
        else:
            return self.save_as_file()
    
    def sync_floor_list(self) -> None:
        '''Match current tab order with self.floors'''
        self.floors = sorted(self.floors, key=lambda obj: self.ui.tabWidget_floors.indexOf(obj.tab_n))

    @staticmethod
    def save_dw(table: Table) -> tuple[int]:
        '''Get indices of rows, marked as "dwelling"'''
        return tuple(table[item][0] for item in table.dw_rows)

    @Slot()
    def save_as_file(self) -> str:
        '''Save tables as a file'''

        path = QFileDialog.getSaveFileName(parent=self, 
                                           caption="Зберегти як", 
                                           dir='save.cajs', 
                                           filter="CalcArea JSON (*.cajs);;Всі файли (*.*)",
                                           )[0]
        if path:
            self.current_file = path
            self.setWindowTitle(self.current_file)
            self.save_file()
            return 'Success'
        
    # @Slot()
    # def export_xlsx(self) -> None:
    #     '''Ask filename to export as a .xlsx document'''
    #     if self.ask_save() == "Ignore":
    #         return

    #     default_path = self.current_file.split('.')[0] + '.xlsx' if self.current_file else "export.xlsx"
    #     path = QFileDialog.getSaveFileName(parent=self, 
    #                                        caption="Експортувати як",
    #                                        dir=default_path,
    #                                        filter="Таблиця Excel (*.xlsx);;Всі файли (*.*)",
    #                                        )[0]
    #     if path:
    #         self.table.write_xlsx(path)

    @Slot()
    def add_floor(self, name=None) -> None:
        '''Adding new floor'''
        i = len(self.floors)
        floor = self.create_floor(i)
        if name:
            floor.tab_n.setObjectName(name)
            self.ui.tabWidget_floors.setTabText(i, name)
        self.floors.append(floor)
    
    @Slot()
    def remove_floor(self) -> None:
        '''Deleting current floor'''
        i = self.ui.tabWidget_floors.currentIndex()
        if i != -1:
            self.ui.tabWidget_floors.removeTab(i)
            del self.floors[i]
            # self.enumerate_floors()   # Deprecated
    
    # @Slot()                               Deprecated
    # def insert_floor(self) -> None:
    #     '''Inserting new floor after current'''
    #     i = self.ui.tabWidget_floors.currentIndex()+1
    #     self.floors.insert(i, self.create_floor(i))
    #     self.enumerate_floors()

    # def enumerate_floors(self) -> None:   Deprecated
    #     '''Reset numberation of floors'''
    #     for i in range(len(self.floors)):
    #         self.ui.tabWidget_floors.setTabText(i, f"Поверх {i+1}")
    
    @Slot(tuple)
    def sum_floors(self, areas: tuple[Dec, Dec]) -> None:
        '''Displaying area sum for all floors'''
        sum_total, sum_dwelling, sum_economical = [Dec('0')]*3

        for floor in self.floors:
            total_widget, dwelling_widget, economical_widget = floor.area_total_n, floor.area_dwelling_n, floor.area_economical_n
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
                self.ui.button_add_row.click()  # Calls self.add_row().
                # Could've just write self.add_row() 
                # but it somehow triggers updates frantically if running without a debug breakpoint.
    
    def current_item(self) -> QTableWidgetItem | None:
        '''Returns first currently selected item'''
        table = self.current_table()
        if table:
            items = table.selectedItems
            return items[0] if items else None
    
    def current_table(self) -> Table | None:
        '''Returns current table'''
        tab1 = self.ui.tabWidget.currentIndex()
        tab2 = self.ui.tabWidget_floors.currentIndex()
        if tab1 == 0:
            return self.table
        elif self.floors:
            return self.floors[tab2].table_obj
    
    def create_floor(self, indx: int, name: str = 'xxx') -> Floor:
        '''Creates new floor'''
        floor = Floor(name)
        self.ui.tabWidget_floors.insertTab(indx, floor.tab_n, QIcon(), name)
        
        floor.table_obj.area_sum_changed.connect(self.connect_area_widgets((floor.area_total_n, floor.area_dwelling_n, floor.area_economical_n)))
        floor.table_obj.area_sum_changed.connect(self.sum_floors)

        return floor
    
    @Slot(int)
    def _on_tab_bar_double_clicked(self, index: int) -> None:
        '''Rename a floor by double-clicking'''
        if index < 0:
            return  # Ensure a valid tab was clicked

        editor = QLineEdit(self.ui.tabWidget_floors.tabBar())
        editor.setText(self.ui.tabWidget_floors.tabText(index))
        editor.setGeometry(self.ui.tabWidget_floors.tabBar().tabRect(index))
        editor.setFrame(False) 
        editor.setFocus()
        editor.selectAll()
        editor.show()

        @Slot()
        def finish_editing() -> None:
            '''Apply changes'''
            new_text = editor.text().strip()
            
            if new_text:
                self.ui.tabWidget_floors.setTabText(index, new_text)
                self.ui.tabWidget_floors.widget(index).setObjectName(new_text)
            
            editor.deleteLater()

        editor.editingFinished.connect(finish_editing)
    
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
    def __init__(self, value_type: type, value: str | Dec = None, rounding: SupportsIndex = None, *args, **kwargs) -> None:
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
    def round(num: Dec, rounding: SupportsIndex) -> Dec:
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

    def __init__(self, widget: QTableWidget, dw_checkbox: QCheckBox) -> None:
        super().__init__()
        self.__table = widget
        self.__table.itemChanged.connect(self.update)
        self.__table.itemSelectionChanged.connect(self.highlight_row)
        self.__table.itemSelectionChanged.connect(self.dw_checkbox_change_state)
        
        self.dw_checkbox = dw_checkbox  # Dwelling area toggle widget
        self.dw_rows: list[int] = list()    # Indices of rows marked as "Dwelling area"
        self.hrows: tuple[tuple[Item]] = tuple()    # Highlighted rows
        self.comp_rows: list[Item] = list()

        self.letter_default: str = 'A'
    
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
    
    @Slot()
    def dw_checkbox_change_state(self) -> None:
        '''Update state of the checkbox based on selected items'''
        try:
            self.dw_checkbox.blockSignals(True)

            self.dw_checkbox.setTristate(False) # Disable middle position
            if not self.hrows:  # If no rows are highlighted disable checkbox
                self.dw_checkbox.setChecked(False)
                self.dw_checkbox.setEnabled(False)
            else:
                self.dw_checkbox.setEnabled(True)
                self.dw_checkbox.setChecked(False)
                dw = False  # found a row with dwelling area 
                ec = False  # found a row with economical area
                for row in self.hrows:
                    if row[0] in self.dw_rows:
                        dw = True
                    else:
                        ec = True
                    if dw and ec:
                        self.dw_checkbox.setCheckState(Qt.CheckState(1))    # If both are present set checkbox to middle position
                        break
                else:
                    self.dw_checkbox.setChecked(dw)
        finally:
            self.dw_checkbox.blockSignals(False)

    @Slot()
    def dw_change(self) -> None:
        '''Change dwelling state of highlighted rows'''
        self.dw_checkbox.setTristate(False) # Disable third state
        state = self.dw_checkbox.checkState().value # Get checkbox state
        if state == 0:  # If turned off
            for row in self.hrows:
                self.dw_rows.remove(row[0])
        else:
            for row in self.hrows:
                if row[0] not in self.dw_rows:
                    self.dw_rows.append(row[0])
                
        self.highlight_row()

        try:
            self.__table.blockSignals(True)
            self.sum_area()
        finally:
            self.__table.blockSignals(False)

    def fill_row(self, row: int) -> None:
        '''Filling row with items with default values'''

        # Temporary suppress table updates 
        # to prevent huge amount of errors while filling row
        self.__table.blockSignals(True)

        self.__table.setItem(row, 0, Item(str, self.letter_default))    # Filling "Letter" column

        for col in range(1, 4): # Filling "Width", "Length" and "Height" columns with rounding to hundredths
            self.__table.setItem(row, col, Item(Dec, rounding=2))
        
        area_item = Item(Dec, rounding=1)
        area_font = area_item.font()
        area_font.setBold(True)
        area_item.setFont(area_font)
        self.__table.setItem(row, 4, area_item) # Filling "Area" column with rounding to tenths
        self.__table.setItem(row, 5, Item(Dec, rounding=0)) # Filling "Volume" column with rounding to whole numbers

        for col in (4, 5):   # Setting "Area" and "Volume" columns to not editable
            self[row][col].editable = False

        # Turns table updates back ON
        self.__table.blockSignals(False)

    @Slot()
    def remove_current_row(self) -> None:
        '''Deleting selected rows'''
        self.comp_rows = list()
        items = list(map(lambda row: self[row[0]], self.hrows))
        for row in map(lambda item: item[0], items[::-1]):
            items_obj = self[row]
            if items_obj[0] in self.dw_rows:
                self.dw_rows.remove(items_obj[0])
            
            self.__table.removeRow(row)

        # if items:
        #     item = items[0]
        #     if item[0] < self.rows:
        #         self[item[0]][item[1]].setSelected(True)

        self.update()

    @Slot()
    def insert_after_current_row(self) -> None:
        '''Inserts an empty row after the selected one or insert at the top if no selected rows'''
        rows = list(map(lambda item: self[item][0], self.__table.selectedItems()))  #           
        if rows:
            self.__table.insertRow(rows[0]+1)
            self.fill_row(rows[0]+1)
            self.update(self[rows[0]+1][-1])
        else:
            self.__table.insertRow(0)
            self.fill_row(0)
            self.update(self[0][-1])

    @Slot()
    def highlight_row(self) -> None:
        '''Highlighting all rows that have a selected item'''
        self.__table.blockSignals(True)
        self.unhighlight()

        rows_i = set(map(lambda item: self[item][0], self.__table.selectedItems())) # Get indices of rows to highlight
        self.hrows = tuple(self[row] for row in rows_i)  # Get tuples of items to highlight
        for row in self.hrows:
            for item in row:
                item.setBackground(QColor(255, 255, 204))
                item.setForeground(QColor(0, 0, 0))
        self.highlight_composite()
        self.highlight_dw()
        self.__table.blockSignals(False)
    
    def unhighlight(self) -> None:
        '''Unhighliting all selected rows'''
        for row in self.hrows:
            for item in row:
                try:
                    item.setBackground(QBrush())
                    item.setForeground(QBrush())
                except RuntimeError:
                    pass
        self.hrows = tuple()

    def unhighlight_all(self) -> None:
        '''Unhighliting all rows in the table'''
        for row in range(self.rows):
            for col in range(self.cols):
                self[row][col].setBackground(QBrush())
                self[row][col].setForeground(QBrush())
        self.hrows = tuple()
    
    def highlight_dw(self) -> None:
        '''Highlight all rows marked "dwelling"'''
        for item in self.dw_rows:
            item.setBackground(QColor(114, 92, 52))
            item.setForeground(QColor(0, 0, 0))
    
    def unhighlight_dw(self) -> None:
        '''Unhighlight all rows marked "dwelling"'''
        for item in self.dw_rows:
            item.setBackground(QBrush())
            item.setForeground(QBrush())

    @Slot(QTableWidgetItem)
    def update(self, item: Item = None) -> None:   # Takes a link to the changed item
        '''The main table update loop'''
        if item:
            row, col = self[item]
            print(f"Update triggered by [{row}][{col}]")
        else:
            print("Update triggered by no item")
        try:
            # Temporary disconnecting table updates to prevent recursion
            self.__table.blockSignals(True)

            self.count_area()
            self.count_volume()
            self.composite_area()
            self.sum_area()

        finally:    # Always turns table updates back ON
            self.__table.blockSignals(False)

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
            
            
            if self[row][0] in self.dw_rows:
                sum_a += self[row, 4]

        # Emits the signal with tuple of counted sums as an argument
        self.area_sum_changed.emit((sum_, sum_a))

    def composite_area(self) -> None:
        '''If row has first character '+' in "Letter" column it will add it's area value to previous row value'''
        if self.rows and self[0, 0].startswith(('+', '-')):
            self[0, 0] = self[0, 0].lstrip('+-')    # Deleting '+' and '-' from "Letter" value if it has no rows above
            self.count_area()
            self.count_volume()
            self.composite_area()
            return

        # Starting iteration of table rows in reverse,
        # so it can sum area values by chain to the top row, that has no '+'
        for row in range(self.rows-1, -1, -1):
            if self[row, 0].startswith(('+', '-')):
                for col in (4, self.cols-1):
                    self[row-1, col] = self[row-1][col].value + self[row][col].value
            self.highlight_composite()

    def highlight_composite(self) -> None:
        '''Highlight items associated with composite area calculation'''
        self.unhighlight_composite()
        for row in range(self.rows-1, -1, -1):
            if self[row, 0].startswith('+'):
                for col in (4, 5):
                    self[row][col].setBackground(QColor(255, 240, 200))     # Highlighting row that is added
                    self[row][col].setForeground(QColor(0, 0, 0))
                    self[row-1][col].setBackground(QColor(220, 255, 220))   # Highlighting row to which is added with different color
                    self[row-1][col].setForeground(QColor(0, 0, 0))

                    for r in (row, row-1):
                            item = self[r][col]
                            if item not in self.comp_rows:
                                self.comp_rows.append(item)

            elif self[row, 0].startswith('-'):
                for col in (4, 5):
                    self[row][col].setBackground(QColor(255, 200, 200))     # Highlighting row that is subtracted with another color
                    self[row][col].setForeground(QColor(0, 0, 0))
                    self[row-1][col].setBackground(QColor(220, 255, 220))   # Highlighting row to which is added with different color
                    self[row-1][col].setForeground(QColor(0, 0, 0))

                    for r in (row, row-1):
                            item = self[r][col]
                            if item not in self.comp_rows:
                                self.comp_rows.append(item)

    def unhighlight_composite(self) -> None:
        '''Unhighlight items previously highlighted as composite area'''
        for item in self.comp_rows:
            try:
                if any((item in row for row in self.hrows)):
                    item.setBackground(QColor(255, 255, 204))
                    item.setForeground(QColor(0, 0, 0))
                else:
                    item.setBackground(QBrush())
                    item.setForeground(QBrush())
            except RuntimeError:    # Occurs when stumbling upon a reference to already deleted Item object
                pass
        self.comp_rows = []

    def load_json(self, matrix: Iterable[Iterable]) -> None:    # For legacy .json support
        '''Loading table from matrix (.json file type)'''
        try:
            self.__table.itemChanged.disconnect(self.update)    # The only found way it doesn't cause update on each item
            self.rows = len(matrix)
            if matrix:
                for row in range(len(matrix)):
                    for col in range(len(matrix[0])):
                        self[row, col] = matrix[row][col]
        finally:
            self.__table.itemChanged.connect(self.update)
            self.update()
    
    def load(self, table: dict) -> None:
        '''Loading table from dictionary'''
        try:
            self.__table.itemChanged.disconnect(self.update)    # The only found way it doesn't cause update on each item

            matrix = table["table"]
            self.rows = len(matrix)
            if matrix:
                for row in range(len(matrix)):
                    for col in range(len(matrix[0])):
                        self[row, col] = matrix[row][col]
            self.dw_rows = list(self[row_i][0] for row_i in table["dw_rows"])
            self.dw_checkbox_change_state()
            self.highlight_dw()
        finally:
            self.__table.itemChanged.connect(self.update)
            self.update()

    def get_matrix(self) -> tuple[tuple]:
        '''Get matrix of table items'''
        try:
            # Temporary disconnecting table updates to prevent recursion
            self.__table.blockSignals(True)
            res = tuple(tuple(str(self[row, col]) for col in range(self.cols))[:-2] for row in range(self.rows))
        finally:
            self.__table.blockSignals(False)
        return res
    
    # def write_xlsx(self, path: str) -> None:
    #     '''Exporting table to .xlsx (currently not used)'''

    #     wb = Workbook()
    #     ws = wb.active
    #     for row in self:
    #         ws.append(tuple(map(lambda item: item.text(), row)))
    #     wb.save(path)


class Floor:
    def __init__(self, name: str) -> None:
        self.setupUi()
        self.retranslateUi()

        self.table_obj = Table(self.tableWidget_n, self.checkBox_n)
        self.table_obj.letter_default = '0'

        self.button_add_row_n.clicked.connect(self.table_obj.add_row)
        self.button_insert_row_n.clicked.connect(self.table_obj.insert_after_current_row)
        self.button_remove_row_n.clicked.connect(self.table_obj.remove_current_row)
        self.checkBox_n.checkStateChanged.connect(self.table_obj.dw_change)

        self.tab_n.setObjectName(name)

    def setupUi(self) -> None:
        '''Set up floor widgets'''
        font1 = QFont()
        font1.setPointSize(12)

        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)

        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)

        self.tab_n = QWidget()
        self.tab_n.setObjectName(u"tab_n")
        self.horizontalLayout = QHBoxLayout(self.tab_n)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tableWidget_n = QTableWidget(self.tab_n)
        if (self.tableWidget_n.columnCount() < 6):
            self.tableWidget_n.setColumnCount(6)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(3, __qtablewidgetitem9)
        font3 = QFont()
        font3.setBold(True)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setFont(font3)
        self.tableWidget_n.setHorizontalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(5, __qtablewidgetitem11)
        self.tableWidget_n.setObjectName(u"tableWidget_n")
        self.tableWidget_n.horizontalHeader().setDefaultSectionSize(70)

        self.horizontalLayout.addWidget(self.tableWidget_n)

        self.container_n = QWidget(self.tab_n)
        self.container_n.setObjectName(u"container_n")
        sizePolicy1.setHeightForWidth(self.container_n.sizePolicy().hasHeightForWidth())
        self.container_n.setSizePolicy(sizePolicy1)
        self.container_n.setMinimumSize(QSize(201, 0))
        self.area_dwelling_n = QTextBrowser(self.container_n)
        self.area_dwelling_n.setObjectName(u"area_dwelling_n")
        self.area_dwelling_n.setGeometry(QRect(110, 110, 91, 31))
        self.area_total_n = QTextBrowser(self.container_n)
        self.area_total_n.setObjectName(u"area_total_n")
        self.area_total_n.setGeometry(QRect(110, 170, 91, 31))
        self.button_add_row_n = QPushButton(self.container_n)
        self.button_add_row_n.setObjectName(u"button_add_row_n")
        self.button_add_row_n.setGeometry(QRect(0, 0, 201, 25))
        self.label_Sdw_n = QLabel(self.container_n)
        self.label_Sdw_n.setObjectName(u"label_Sdw_n")
        self.label_Sdw_n.setGeometry(QRect(0, 110, 101, 31))
        self.label_Sdw_n.setFont(font1)
        self.label_Sdw_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_remove_row_n = QPushButton(self.container_n)
        self.button_remove_row_n.setObjectName(u"button_remove_row_n")
        self.button_remove_row_n.setGeometry(QRect(100, 30, 101, 25))
        self.area_economical_n = QTextBrowser(self.container_n)
        self.area_economical_n.setObjectName(u"area_economical_n")
        self.area_economical_n.setGeometry(QRect(110, 140, 91, 31))
        self.label_S_n = QLabel(self.container_n)
        self.label_S_n.setObjectName(u"label_S_n")
        self.label_S_n.setGeometry(QRect(0, 170, 101, 31))
        self.label_S_n.setFont(font2)
        self.label_S_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_Sec_n = QLabel(self.container_n)
        self.label_Sec_n.setObjectName(u"label_Sec_n")
        self.label_Sec_n.setGeometry(QRect(0, 140, 101, 31))
        self.label_Sec_n.setFont(font1)
        self.label_Sec_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkBox_n = QCheckBox(self.container_n)
        self.checkBox_n.setObjectName(u"checkBox_n")
        self.checkBox_n.setEnabled(False)
        self.checkBox_n.setGeometry(QRect(0, 70, 84, 24))
        self.checkBox_n.setCheckable(True)
        self.checkBox_n.setChecked(False)
        self.checkBox_n.setAutoRepeat(False)
        self.checkBox_n.setAutoExclusive(False)
        self.checkBox_n.setTristate(True)
        self.button_insert_row_n = QPushButton(self.container_n)
        self.button_insert_row_n.setObjectName(u"button_insert_row_n")
        self.button_insert_row_n.setGeometry(QRect(0, 30, 101, 25))

        self.horizontalLayout.addWidget(self.container_n)

        self.tableWidget_n.show()
        self.container_n.show()

    def retranslateUi(self) -> None:
        '''Set up text on widgets'''
        ___qtablewidgetitem6 = self.tableWidget_n.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\u041d\u043e\u043c\u0435\u0440", None))
        ___qtablewidgetitem7 = self.tableWidget_n.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0438\u0440\u0438\u043d\u0430", None))
        ___qtablewidgetitem8 = self.tableWidget_n.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0432\u0436\u0438\u043d\u0430", None))
        ___qtablewidgetitem9 = self.tableWidget_n.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0441\u043e\u0442\u0430", None))
        ___qtablewidgetitem10 = self.tableWidget_n.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0449\u0430", None))
        ___qtablewidgetitem11 = self.tableWidget_n.horizontalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431'\u0454\u043c", None))
        self.area_dwelling_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Sans Serif';\">0</span></p></body></html>", None))
        self.area_total_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Sans Serif';\">0</span></p></body></html>", None))
        self.button_add_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0434\u0430\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.button_insert_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.label_Sdw_n.setText(QCoreApplication.translate("MainWindow", u"S\u0436\u0438\u0442\u043b\u043e\u0432\u0430", None))
        self.button_remove_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0440\u044f\u0434\u043a\u0438", None))
        self.area_economical_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Sans Serif';\">0</span></p></body></html>", None))
        self.label_S_n.setText(QCoreApplication.translate("MainWindow", u"S\u0437\u0430\u0433\u0430\u043b\u044c\u043d\u0430", None))
        self.label_Sec_n.setText(QCoreApplication.translate("MainWindow", u"S\u043f\u0456\u0434\u0441\u043e\u0431\u043d\u0430", None))
        self.checkBox_n.setText(QCoreApplication.translate("MainWindow", u"\u0416\u0438\u0442\u043b\u043e\u0432\u0430", None))

def excepthook(cls: type, exception: Exception, traceback) -> None:
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