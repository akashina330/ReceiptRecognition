# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'time.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Total Time")
        Form.resize(493, 151)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(0, 0, 491, 150))
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPointSize(48)
        self.label.setFont(font)
        self.label.setText("")
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Затрачено на обработку"))
