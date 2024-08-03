# This Python file uses the following encoding: utf-8
import sys
from decimal import Decimal as Dec

from tkinter import filedialog

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

from PySide6.QtCore import Qt

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

        self.ui.pushButton.clicked.connect(self.new_row)
        self.ui.tableWidget.itemChanged.connect(self.update_values)

        self.currentfile = ''

    def new_row(self):
        self.ui.tableWidget.itemChanged.disconnect(self.update_values)

        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)

        for col in range(6):
            self.ui.tableWidget.setItem(row, col, QTableWidgetItem())
            self.ui.tableWidget.item(row, col).setText('0.00')

        self.ui.tableWidget.item(row, 0).setText('')

        area, volume = self.ui.tableWidget.item(row, 4), self.ui.tableWidget.item(row, 5)
        area.setFlags(area.flags() & ~Qt.ItemIsEditable)
        volume.setFlags(volume.flags() & ~Qt.ItemIsEditable)

        self.ui.tableWidget.itemChanged.connect(self.update_values)

    def update_values(self):
        self.ui.tableWidget.itemChanged.disconnect(self.update_values)

        self.calculate_area()
        self.calculate_volume()

        self.sum_area()
        self.sum_volume()

        self.ui.tableWidget.itemChanged.connect(self.update_values)

    def calculate_area(self):
        for row in range(self.ui.tableWidget.rowCount()):
            width, length = self.ui.tableWidget.item(row, 1), self.ui.tableWidget.item(row, 2)
            width, length = width.text(), length.text()
            width, length = width.replace(',', '.'), length.replace(',', '.')
            width, length = Dec(width), Dec(length)

            res = width * length
            res = self.out_format(res, rounding=1)

            self.ui.tableWidget.item(row, 4).setText(res)

            self.ui.actionOpen.triggered.connect(self.openfile)


    def sum_area(self):
        summ = Dec('0')
        sum_a = Dec('0')

        for row in range(self.ui.tableWidget.rowCount()):
            summ += Dec(self.ui.tableWidget.item(row, 4).text())
            letter = self.ui.tableWidget.item(row, 0).text()
            if letter and letter[0] in ('A', 'a', 'А', 'а'):
                sum_a += Dec(self.ui.tableWidget.item(row, 4).text())

        self.ui.area_dwelling.setText(str(sum_a))
        self.ui.area_economical.setText(str(summ - sum_a))
        self.ui.area_total.setText(str(summ))

    def calculate_volume(self):
        for row in range(self.ui.tableWidget.rowCount()):
            area, height = self.ui.tableWidget.item(row, 4), self.ui.tableWidget.item(row, 3)
            area, height = area.text(), height.text()
            area, height = area.replace(',', '.'), height.replace(',', '.')
            area, height = Dec(area), Dec(height)

            res = area * height
            res = self.out_format(res, rounding=0)

            self.ui.tableWidget.item(row, 5).setText(res)

    def sum_volume(self):
        summ = Dec('0')
        for row in range(self.ui.tableWidget.rowCount()):
            summ += Dec(self.ui.tableWidget.item(row, 5).text())
        self.ui.volume_total.setText(str(summ))

    def out_format(self, value, rounding=0):
        value = round(value, rounding)
        value = str(value)
        return value
    
    def openfile(self):
        self.currentfile = filedialog.askopenfilename()
        print(self.currentfile)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
