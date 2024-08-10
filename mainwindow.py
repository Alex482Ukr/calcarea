# This Python file uses the following encoding: utf-8
import sys
from decimal import Decimal as Dec
from tkinter import filedialog
import traceback
from pyperclip import copy

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QModelIndex

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

        my_icon = QIcon()
        my_icon.addFile('icons/icon.png')

        self.setWindowIcon(my_icon)

        self.ui.pushButton.clicked.connect(self.new_row)

        self.ui.actionOpen.triggered.connect(self.openfile)
        self.ui.actionSave.triggered.connect(self.savefile)
        self.ui.actionSaveAs.triggered.connect(self.saveasfile)

        self.ui.tableWidget.itemChanged.connect(self.update_values)
        self.ui.tableWidget.itemSelectionChanged.connect(self.unhighlight_all)
        self.ui.tableWidget.itemSelectionChanged.connect(self.highlight_row)

        self.currentfile = None

    @property
    def rows(self):
        return self.ui.tableWidget.rowCount()
    @property
    def cols(self):
        return self.ui.tableWidget.columnCount()

    def highlight_row(self):

        rows = map(QModelIndex.row, self.ui.tableWidget.selectedIndexes())
        for row in rows:
            for col in range(self.cols):
                item = self.ui.tableWidget.item(row, col)
                item.setBackground(QColor(255, 255, 204))

    def unhighlight_all(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.ui.tableWidget.item(row, col).setBackground(QColor(255, 255, 255))

    def new_row(self):
        self.ui.tableWidget.itemChanged.disconnect(self.update_values)

        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)

        for col in range(self.cols):
            self.ui.tableWidget.setItem(row, col, QTableWidgetItem())
            self.ui.tableWidget.item(row, col).setText('0.00')

        self.ui.tableWidget.item(row, 0).setText('A')

        area, volume = self.ui.tableWidget.item(row, 4), self.ui.tableWidget.item(row, 5)
        area.setFlags(area.flags() & ~Qt.ItemIsEditable)
        volume.setFlags(volume.flags() & ~Qt.ItemIsEditable)

        self.ui.tableWidget.itemChanged.connect(self.update_values)

    def update_values(self):
        self.ui.tableWidget.itemChanged.disconnect(self.update_values)
        try:
            self.verify_input()

            self.calculate_area()
            self.calculate_volume()

            self.sum_area()
            self.sum_volume()
        finally:
            self.ui.tableWidget.itemChanged.connect(self.update_values)

    def calculate_area(self):
        for row in range(self.rows):
            letter, width, length, area = self.getitems(row, 0, 1, 2, 4)

            if '!' in letter.text():
                res = area.text()
                res.replace(',', '.')
                res = Dec(res)
                res = self.out_format(res, rounding=1)
                width.setText(res)
                length.setText('1')
            else:
                width, length = width.text(), length.text()
                width, length = width.replace(',', '.'), length.replace(',', '.')
                width, length = Dec(width), Dec(length)
                res = width * length
                res = self.out_format(res, rounding=1)
            self.ui.tableWidget.item(row, 4).setText(res)


    def sum_area(self):
        summ = Dec('0')
        sum_a = Dec('0')

        for row in range(self.rows):
            summ += Dec(self.ui.tableWidget.item(row, 4).text())
            letter = self.ui.tableWidget.item(row, 0).text()
            if letter and letter[0] in ('A', 'a', 'А', 'а'):
                sum_a += Dec(self.ui.tableWidget.item(row, 4).text())

        self.ui.area_dwelling.setText(str(sum_a))
        self.ui.area_economical.setText(str(summ - sum_a))
        self.ui.area_total.setText(str(summ))

    def calculate_volume(self):
        for row in range(self.rows):
            area, height = self.ui.tableWidget.item(row, 4), self.ui.tableWidget.item(row, 3)
            area, height = area.text(), height.text()
            area, height = area.replace(',', '.'), height.replace(',', '.')
            area, height = Dec(area), Dec(height)

            res = area * height
            res = self.out_format(res, rounding=0)

            self.ui.tableWidget.item(row, 5).setText(res)

    def sum_volume(self):
        summ = Dec('0')
        for row in range(self.rows):
            summ += Dec(self.ui.tableWidget.item(row, 5).text())
        self.ui.volume_total.setText(str(summ))

    def out_format(self, value, rounding=0):
        value = str(value)
        if '.' in value and len(value.split('.')[1]) > rounding and value.rstrip('0').endswith('5'):
            value = value + '1'
        value = Dec(value)
        value = round(value, rounding)
        value = str(value)
        return value
    
    def openfile(self):
        with filedialog.askopenfile(
            defaultextension='.tsv', 
            filetypes=[('Comma Separated Values', '.csv'), ('All types', '.*')], 
            title='Відкрити', 
            initialfile='save.csv') as f:

            if f:
                self.currentfile = f.name

                table = [[value for value in row.split(',')] for row in f.read().split('\n')]

                self.clear_table()
                for _ in range(len(table)):
                    self.new_row()

                for row in range(self.ui.tableWidget.rowCount()):
                    for col in range(6):
                        self.ui.tableWidget.item(row, col).setText(table[row][col])

    def savefile(self):
        rows = [[self.ui.tableWidget.item(row, col).text() for col in range(self.cols)] for row in range(self.rows)]
        rows = '\n'.join([','.join(row) for row in rows])
        
        if self.currentfile:
            with open(self.currentfile, 'wt') as f:
                f.write(rows)
        else:
            self.saveasfile()

    def saveasfile(self):
        try:
            with filedialog.asksaveasfile(
                defaultextension='.csv', 
                filetypes=[('Comma Separated Values', '.csv'), ('All types', '.*')], 
                title='Зберегти як', 
                initialfile='save.csv') as f:

                if f:
                    self.currentfile = f.name

                    rows = [[self.ui.tableWidget.item(row, col).text() for col in range(self.cols)] for row in range(self.rows)]
                    rows = '\n'.join([','.join(row) for row in rows])

                    f.write(rows)
        except AttributeError:
            print('Save as file canceled')

    def clear_table(self):
        for _ in range(self.ui.tableWidget.rowCount()):
            self.ui.tableWidget.removeRow(0)

    def verify_input(self):
        for row in range(self.ui.tableWidget.rowCount()):
            letter = self.ui.tableWidget.item(row, 0).text()
            if not letter or ',' in letter:
                self.ui.tableWidget.item(row, 0).setText('A')
            elif 'ё' in letter:
                self.ui.tableWidget.item(row, 0).setText(letter.replace('ё', "'"))
            elif '!' in letter:
                self.composite_area(row)
            else:
                self.not_composite_area(row)

            for col in range(1, 6):
                value = self.ui.tableWidget.item(row, col).text()
                if not value:
                    value = '0.00'

                value = value.replace(',', '.')
                value = self.out_format(value, rounding=2)
                self.ui.tableWidget.item(row, col).setText(value)

    
    def getitems(self, row, *indxs):
        return tuple(self.ui.tableWidget.item(row, i) for i in indxs)
    
    def composite_area(self, row):
        width, length, area = self.getitems(row, 1, 2, 4)
        width.setFlags(width.flags() & ~Qt.ItemIsEditable)
        length.setFlags(length.flags() & ~Qt.ItemIsEditable)
        area.setFlags(area.flags() | Qt.ItemIsEditable)

    def not_composite_area(self, row):
        width, length, area = self.getitems(row, 1, 2, 4)
        width.setFlags(width.flags() | Qt.ItemIsEditable)
        length.setFlags(length.flags() | Qt.ItemIsEditable)
        area.setFlags(area.flags() & ~Qt.ItemIsEditable)
    
    def closeEvent(self, event):
        if self.currentfile:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Збереження")
            dlg.setText("Зберегти зміни?")
            dlg.setStandardButtons(QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)
            dlg.setIcon(QMessageBox.Question)
            button = dlg.exec()

            if button == QMessageBox.Save:
                self.savefile()
                event.accept()
            elif button == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
            

def excepthook(cls, exception, tb):
    exc_type = cls.__name__
    exc = ''.join(traceback.format_exception_only(exception))
    exc_full = ''.join(traceback.format_exception(exception))
    
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
    exit_code = app.exec()
    sys.exit(exit_code)
