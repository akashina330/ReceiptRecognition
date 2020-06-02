# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'recognition.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.showMaximized()
        MainWindow.resize(800, 900) #длина 900, было 600
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(500, 40, 280, 400)) #ocr
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(500, 470, 280, 400)) #qr
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(500, 20, 100, 20)) #ocr label
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 20, 50, 15)) #receipt label
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(500, 440, 150, 30)) # qr label
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 40, 450, 800)) #receipt window
        self.label_4.setText("")
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.n = QtWidgets.QPushButton(self.centralwidget)
        self.n.setGeometry(QtCore.QRect(395, 850, 75, 25)) # --->
        self.n.setObjectName("n")
        self.b = QtWidgets.QPushButton(self.centralwidget)
        self.b.setGeometry(QtCore.QRect(20, 850, 75, 25)) # <---
        self.b.setObjectName("b")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(100, 850, 50, 20)) #total_label
        self.label_5.setObjectName("label_5")
        self.total_sum = QtWidgets.QLabel(self.centralwidget)
        self.total_sum.setGeometry(QtCore.QRect(150, 850, 50, 20)) #total
        self.total_sum.setText("")
        self.total_sum.setObjectName("summ")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(160, 850, 250, 20)) #time_label
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        MainWindow.setCentralWidget(self.centralwidget)
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "OCR"))
        self.label_2.setText(_translate("MainWindow", "Receipt"))
        self.label_3.setText(_translate("MainWindow", "QR-code recognition"))
        self.n.setText(_translate("MainWindow", "------->"))
        self.b.setText(_translate("MainWindow", "<-------"))
        self.label_5.setText(_translate("MainWindow", "Total:"))
        self.label_6.setText(_translate("MainWindow", "TextLabel"))
        self.action.setText(_translate("MainWindow", "Choose a folder"))
