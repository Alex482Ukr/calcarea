# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHeaderView, QLabel, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextBrowser, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(713, 500)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(713, 500))
        MainWindow.setMaximumSize(QSize(713, 500))
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSaveAs = QAction(MainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.actionExport = QAction(MainWindow)
        self.actionExport.setObjectName(u"actionExport")
        self.actionExport.setEnabled(False)
        self.actionExport.setVisible(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(9, 0, 701, 451))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tableWidget = QTableWidget(self.tab)
        if (self.tableWidget.columnCount() < 6):
            self.tableWidget.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(0, 0, 461, 411))
        self.tableWidget.horizontalHeader().setDefaultSectionSize(70)
        self.label_Sec = QLabel(self.tab)
        self.label_Sec.setObjectName(u"label_Sec")
        self.label_Sec.setGeometry(QRect(480, 100, 101, 31))
        font = QFont()
        font.setPointSize(12)
        self.label_Sec.setFont(font)
        self.label_Sec.setAlignment(Qt.AlignCenter)
        self.label_S = QLabel(self.tab)
        self.label_S.setObjectName(u"label_S")
        self.label_S.setGeometry(QRect(480, 130, 101, 31))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.label_S.setFont(font1)
        self.label_S.setAlignment(Qt.AlignCenter)
        self.button_add_row = QPushButton(self.tab)
        self.button_add_row.setObjectName(u"button_add_row")
        self.button_add_row.setGeometry(QRect(480, 0, 201, 25))
        self.area_total = QTextBrowser(self.tab)
        self.area_total.setObjectName(u"area_total")
        self.area_total.setGeometry(QRect(590, 130, 91, 31))
        self.button_insert_row = QPushButton(self.tab)
        self.button_insert_row.setObjectName(u"button_insert_row")
        self.button_insert_row.setGeometry(QRect(480, 30, 101, 25))
        self.area_economical = QTextBrowser(self.tab)
        self.area_economical.setObjectName(u"area_economical")
        self.area_economical.setGeometry(QRect(590, 100, 91, 31))
        self.area_dwelling = QTextBrowser(self.tab)
        self.area_dwelling.setObjectName(u"area_dwelling")
        self.area_dwelling.setGeometry(QRect(590, 70, 91, 31))
        self.label_Sdw = QLabel(self.tab)
        self.label_Sdw.setObjectName(u"label_Sdw")
        self.label_Sdw.setGeometry(QRect(480, 70, 101, 31))
        self.label_Sdw.setFont(font)
        self.label_Sdw.setAlignment(Qt.AlignCenter)
        self.button_remove_row = QPushButton(self.tab)
        self.button_remove_row.setObjectName(u"button_remove_row")
        self.button_remove_row.setGeometry(QRect(580, 30, 101, 25))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.label_Sec_floor = QLabel(self.tab_2)
        self.label_Sec_floor.setObjectName(u"label_Sec_floor")
        self.label_Sec_floor.setGeometry(QRect(240, 380, 101, 31))
        self.label_Sec_floor.setFont(font)
        self.label_Sec_floor.setAlignment(Qt.AlignCenter)
        self.label_S_floor = QLabel(self.tab_2)
        self.label_S_floor.setObjectName(u"label_S_floor")
        self.label_S_floor.setGeometry(QRect(480, 380, 101, 31))
        self.label_S_floor.setFont(font1)
        self.label_S_floor.setAlignment(Qt.AlignCenter)
        self.area_total_floor = QTextBrowser(self.tab_2)
        self.area_total_floor.setObjectName(u"area_total_floor")
        self.area_total_floor.setGeometry(QRect(590, 380, 91, 31))
        self.area_economical_floor = QTextBrowser(self.tab_2)
        self.area_economical_floor.setObjectName(u"area_economical_floor")
        self.area_economical_floor.setGeometry(QRect(350, 380, 91, 31))
        self.area_dwelling_floor = QTextBrowser(self.tab_2)
        self.area_dwelling_floor.setObjectName(u"area_dwelling_floor")
        self.area_dwelling_floor.setGeometry(QRect(120, 380, 91, 31))
        self.label_Sdw_floor = QLabel(self.tab_2)
        self.label_Sdw_floor.setObjectName(u"label_Sdw_floor")
        self.label_Sdw_floor.setGeometry(QRect(10, 380, 101, 31))
        self.label_Sdw_floor.setFont(font)
        self.label_Sdw_floor.setAlignment(Qt.AlignCenter)
        self.button_add_floor = QPushButton(self.tab_2)
        self.button_add_floor.setObjectName(u"button_add_floor")
        self.button_add_floor.setGeometry(QRect(10, 340, 141, 25))
        self.tabWidget_floors = QTabWidget(self.tab_2)
        self.tabWidget_floors.setObjectName(u"tabWidget_floors")
        self.tabWidget_floors.setGeometry(QRect(0, 0, 701, 321))
        self.tab_n = QWidget()
        self.tab_n.setObjectName(u"tab_n")
        self.button_remove_row_n = QPushButton(self.tab_n)
        self.button_remove_row_n.setObjectName(u"button_remove_row_n")
        self.button_remove_row_n.setGeometry(QRect(580, 30, 101, 25))
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
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_n.setHorizontalHeaderItem(5, __qtablewidgetitem11)
        self.tableWidget_n.setObjectName(u"tableWidget_n")
        self.tableWidget_n.setGeometry(QRect(0, 0, 461, 291))
        self.tableWidget_n.horizontalHeader().setDefaultSectionSize(70)
        self.area_economical_n = QTextBrowser(self.tab_n)
        self.area_economical_n.setObjectName(u"area_economical_n")
        self.area_economical_n.setGeometry(QRect(590, 100, 91, 31))
        self.button_add_row_n = QPushButton(self.tab_n)
        self.button_add_row_n.setObjectName(u"button_add_row_n")
        self.button_add_row_n.setGeometry(QRect(480, 0, 201, 25))
        self.area_total_n = QTextBrowser(self.tab_n)
        self.area_total_n.setObjectName(u"area_total_n")
        self.area_total_n.setGeometry(QRect(590, 130, 91, 31))
        self.button_insert_row_n = QPushButton(self.tab_n)
        self.button_insert_row_n.setObjectName(u"button_insert_row_n")
        self.button_insert_row_n.setGeometry(QRect(480, 30, 101, 25))
        self.label_Sdw_n = QLabel(self.tab_n)
        self.label_Sdw_n.setObjectName(u"label_Sdw_n")
        self.label_Sdw_n.setGeometry(QRect(480, 70, 101, 31))
        self.label_Sdw_n.setFont(font)
        self.label_Sdw_n.setAlignment(Qt.AlignCenter)
        self.area_dwelling_n = QTextBrowser(self.tab_n)
        self.area_dwelling_n.setObjectName(u"area_dwelling_n")
        self.area_dwelling_n.setGeometry(QRect(590, 70, 91, 31))
        self.label_S_n = QLabel(self.tab_n)
        self.label_S_n.setObjectName(u"label_S_n")
        self.label_S_n.setGeometry(QRect(480, 130, 101, 31))
        self.label_S_n.setFont(font1)
        self.label_S_n.setAlignment(Qt.AlignCenter)
        self.label_Sec_n = QLabel(self.tab_n)
        self.label_Sec_n.setObjectName(u"label_Sec_n")
        self.label_Sec_n.setGeometry(QRect(480, 100, 101, 31))
        self.label_Sec_n.setFont(font)
        self.label_Sec_n.setAlignment(Qt.AlignCenter)
        self.tabWidget_floors.addTab(self.tab_n, "")
        self.button_remove_floor = QPushButton(self.tab_2)
        self.button_remove_floor.setObjectName(u"button_remove_floor")
        self.button_remove_floor.setGeometry(QRect(310, 340, 141, 25))
        self.button_insert_floor = QPushButton(self.tab_2)
        self.button_insert_floor.setObjectName(u"button_insert_floor")
        self.button_insert_floor.setGeometry(QRect(160, 340, 141, 25))
        self.tabWidget.addTab(self.tab_2, "")
        self.area_economical_floor.raise_()
        self.area_total_floor.raise_()
        self.area_dwelling_floor.raise_()
        self.label_S_floor.raise_()
        self.label_Sdw_floor.raise_()
        self.label_Sec_floor.raise_()
        self.button_add_floor.raise_()
        self.tabWidget_floors.raise_()
        self.button_remove_floor.raise_()
        self.button_insert_floor.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 713, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionExport)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_floors.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0456\u0434\u043a\u0440\u0438\u0442\u0438", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveAs.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0431\u0435\u0440\u0435\u0433\u0442\u0438 \u044f\u043a", None))
        self.actionExport.setText(QCoreApplication.translate("MainWindow", u"\u0415\u043a\u0441\u043f\u043e\u0440\u0442\u0443\u0432\u0430\u0442\u0438 \u0432 Excel", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0443\u043a\u0432\u0430", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0438\u0440\u0438\u043d\u0430", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0432\u0436\u0438\u043d\u0430", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0441\u043e\u0442\u0430", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0449\u0430", None));
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431'\u0454\u043c", None));
        self.label_Sec.setText(QCoreApplication.translate("MainWindow", u"S\u0433\u043e\u0441\u043f", None))
        self.label_S.setText(QCoreApplication.translate("MainWindow", u"S\u0437\u0430\u0433\u0430\u043b\u044c\u043d\u0430", None))
        self.button_add_row.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0434\u0430\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.area_total.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.button_insert_row.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.area_economical.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.area_dwelling.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.label_Sdw.setText(QCoreApplication.translate("MainWindow", u"S\u0436\u0438\u0442\u043b\u043e\u0432\u0430", None))
        self.button_remove_row.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\u0414\u0456\u043b\u044f\u043d\u043a\u0430", None))
        self.label_Sec_floor.setText(QCoreApplication.translate("MainWindow", u"S\u0433\u043e\u0441\u043f", None))
        self.label_S_floor.setText(QCoreApplication.translate("MainWindow", u"S\u0437\u0430\u0433\u0430\u043b\u044c\u043d\u0430", None))
        self.area_total_floor.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.area_economical_floor.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.area_dwelling_floor.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.label_Sdw_floor.setText(QCoreApplication.translate("MainWindow", u"S\u0436\u0438\u0442\u043b\u043e\u0432\u0430", None))
        self.button_add_floor.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0434\u0430\u0442\u0438 \u043f\u043e\u0432\u0435\u0440\u0445", None))
        self.button_remove_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        ___qtablewidgetitem6 = self.tableWidget_n.horizontalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\u0411\u0443\u043a\u0432\u0430", None));
        ___qtablewidgetitem7 = self.tableWidget_n.horizontalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0438\u0440\u0438\u043d\u0430", None));
        ___qtablewidgetitem8 = self.tableWidget_n.horizontalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0432\u0436\u0438\u043d\u0430", None));
        ___qtablewidgetitem9 = self.tableWidget_n.horizontalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0441\u043e\u0442\u0430", None));
        ___qtablewidgetitem10 = self.tableWidget_n.horizontalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0449\u0430", None));
        ___qtablewidgetitem11 = self.tableWidget_n.horizontalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431'\u0454\u043c", None));
        self.area_economical_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.button_add_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0434\u0430\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.area_total_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.button_insert_row_n.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u0438 \u0440\u044f\u0434\u043e\u043a", None))
        self.label_Sdw_n.setText(QCoreApplication.translate("MainWindow", u"S\u0436\u0438\u0442\u043b\u043e\u0432\u0430", None))
        self.area_dwelling_n.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0</p></body></html>", None))
        self.label_S_n.setText(QCoreApplication.translate("MainWindow", u"S\u0437\u0430\u0433\u0430\u043b\u044c\u043d\u0430", None))
        self.label_Sec_n.setText(QCoreApplication.translate("MainWindow", u"S\u0433\u043e\u0441\u043f", None))
        self.tabWidget_floors.setTabText(self.tabWidget_floors.indexOf(self.tab_n), QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0432\u0435\u0440\u0445 n", None))
        self.button_remove_floor.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0438\u0434\u0430\u043b\u0438\u0442\u0438 \u043f\u043e\u0432\u0435\u0440\u0445", None))
        self.button_insert_floor.setText(QCoreApplication.translate("MainWindow", u"\u0412\u0441\u0442\u0430\u0432\u0438\u0442\u0438 \u043f\u043e\u0432\u0435\u0440\u0445", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\u0412\u043d\u0443\u0442\u0440\u0456\u0448\u043d\u044f \u043f\u043b\u043e\u0449\u0430", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b", None))
    # retranslateUi

