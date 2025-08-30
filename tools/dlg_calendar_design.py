# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_calender_design.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCalendarWidget, QComboBox,
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(461, 376)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.pushButtonPreYear = QPushButton(Dialog)
        self.pushButtonPreYear.setObjectName(u"pushButtonPreYear")
        font = QFont()
        font.setPointSize(11)
        self.pushButtonPreYear.setFont(font)
        self.pushButtonPreYear.setStyleSheet(u"    QPushButton {\n"
"        background-color: transparent; /* \u900f\u660e\u80cc\u666f */\n"
"        border: none; /* \u65e0\u8fb9\u6846 */\n"
"        color: black; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272 */\n"
"    }\n"
"    QPushButton:hover {\n"
"        color: rgb(0, 170, 255); /* \u9f20\u6807\u60ac\u505c\u65f6\u5b57\u4f53\u989c\u8272\u53d8\u4e3a\u84dd\u8272 */\n"
"\n"
"    }")

        self.horizontalLayout.addWidget(self.pushButtonPreYear)

        self.pushButtonPreMonth = QPushButton(Dialog)
        self.pushButtonPreMonth.setObjectName(u"pushButtonPreMonth")
        self.pushButtonPreMonth.setFont(font)
        self.pushButtonPreMonth.setStyleSheet(u"    QPushButton {\n"
"        background-color: transparent; /* \u900f\u660e\u80cc\u666f */\n"
"        border: none; /* \u65e0\u8fb9\u6846 */\n"
"        color: black; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272 */\n"
"    }\n"
"    QPushButton:hover {\n"
"        color: rgb(0, 170, 255); /* \u9f20\u6807\u60ac\u505c\u65f6\u5b57\u4f53\u989c\u8272\u53d8\u4e3a\u84dd\u8272 */\n"
"\n"
"    }")

        self.horizontalLayout.addWidget(self.pushButtonPreMonth)

        self.comboBox = QComboBox(Dialog)
        self.comboBox.setObjectName(u"comboBox")
        font1 = QFont()
        font1.setPointSize(10)
        self.comboBox.setFont(font1)

        self.horizontalLayout.addWidget(self.comboBox)

        self.comboBox_2 = QComboBox(Dialog)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setFont(font1)

        self.horizontalLayout.addWidget(self.comboBox_2)

        self.pushButtonNextMonth = QPushButton(Dialog)
        self.pushButtonNextMonth.setObjectName(u"pushButtonNextMonth")
        self.pushButtonNextMonth.setFont(font)
        self.pushButtonNextMonth.setStyleSheet(u"    QPushButton {\n"
"        background-color: transparent; /* \u900f\u660e\u80cc\u666f */\n"
"        border: none; /* \u65e0\u8fb9\u6846 */\n"
"        color: black; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272 */\n"
"    }\n"
"    QPushButton:hover {\n"
"        color: rgb(0, 170, 255); /* \u9f20\u6807\u60ac\u505c\u65f6\u5b57\u4f53\u989c\u8272\u53d8\u4e3a\u84dd\u8272 */\n"
"\n"
"    }")

        self.horizontalLayout.addWidget(self.pushButtonNextMonth)

        self.pushButtonNextYear = QPushButton(Dialog)
        self.pushButtonNextYear.setObjectName(u"pushButtonNextYear")
        self.pushButtonNextYear.setFont(font)
        self.pushButtonNextYear.setStyleSheet(u"    QPushButton {\n"
"        background-color: transparent; /* \u900f\u660e\u80cc\u666f */\n"
"        border: none; /* \u65e0\u8fb9\u6846 */\n"
"        color: black; /* \u9ed8\u8ba4\u5b57\u4f53\u989c\u8272 */\n"
"    }\n"
"    QPushButton:hover {\n"
"        color: rgb(0, 170, 255); /* \u9f20\u6807\u60ac\u505c\u65f6\u5b57\u4f53\u989c\u8272\u53d8\u4e3a\u84dd\u8272 */\n"
"\n"
"    }")

        self.horizontalLayout.addWidget(self.pushButtonNextYear)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.horizontalLayout.setStretch(2, 1)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 3)
        self.horizontalLayout.setStretch(5, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.calendarWidget = QCalendarWidget(Dialog)
        self.calendarWidget.setObjectName(u"calendarWidget")
        font2 = QFont()
        self.calendarWidget.setFont(font2)
        self.calendarWidget.setStyleSheet(u"")
        self.calendarWidget.setMinimumDate(QDate(1900, 1, 31))
        self.calendarWidget.setMaximumDate(QDate(2101, 1, 28))
        self.calendarWidget.setGridVisible(True)
        self.calendarWidget.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        self.calendarWidget.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendarWidget.setNavigationBarVisible(False)
        self.calendarWidget.setDateEditEnabled(True)

        self.verticalLayout.addWidget(self.calendarWidget)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        font3 = QFont()
        font3.setPointSize(12)
        self.buttonBox.setFont(font3)
        self.buttonBox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.buttonBox.setStyleSheet(u"QDialogButtonBox QPushButton {\n"
"	color: rgb(255, 255, 255);\n"
"    background-color: rgb(3, 147, 250); /* \u5929\u7a7a\u84dd\u80cc\u666f */\n"
"    border: None;\n"
"    border-radius: 15px; /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 10px 20px; /* \u5185\u8fb9\u8ddd\uff0c\u53ef\u4ee5\u6839\u636e\u9700\u8981\u8c03\u6574 */\n"
"    margin-bottom: 10px; /* \u5916\u8fb9\u8ddd\uff0c\u53ef\u9009\uff0c\u6839\u636e\u5b9e\u9645\u60c5\u51b5\u8c03\u6574 */\n"
"}\n"
"\n"
"/* \u9f20\u6807\u60ac\u505c\u65f6\u7684\u6837\u5f0f */\n"
"QDialogButtonBox QPushButton:hover {\n"
"    background-color: rgb(0, 103, 154); /* \u60ac\u505c\u65f6\u6539\u53d8\u80cc\u666f\u8272 */\n"
"}\n"
"")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout.addWidget(self.buttonBox)

        self.labelHint = QLabel(Dialog)
        self.labelHint.setObjectName(u"labelHint")
        font4 = QFont()
        font4.setPointSize(9)
        self.labelHint.setFont(font4)
        self.labelHint.setStyleSheet(u"color:rgb(139, 139, 139)")
        self.labelHint.setMargin(0)

        self.verticalLayout.addWidget(self.labelHint)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.pushButtonPreYear.setText(QCoreApplication.translate("Dialog", u"<<", None))
        self.pushButtonPreMonth.setText(QCoreApplication.translate("Dialog", u"<", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("Dialog", u"\u4e00\u6708", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("Dialog", u"\u4e8c\u6708", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("Dialog", u"\u4e09\u6708", None))
        self.comboBox_2.setItemText(3, QCoreApplication.translate("Dialog", u"\u56db\u6708", None))
        self.comboBox_2.setItemText(4, QCoreApplication.translate("Dialog", u"\u4e94\u6708", None))
        self.comboBox_2.setItemText(5, QCoreApplication.translate("Dialog", u"\u516d\u6708", None))
        self.comboBox_2.setItemText(6, QCoreApplication.translate("Dialog", u"\u4e03\u6708", None))
        self.comboBox_2.setItemText(7, QCoreApplication.translate("Dialog", u"\u516b\u6708", None))
        self.comboBox_2.setItemText(8, QCoreApplication.translate("Dialog", u"\u4e5d\u6708", None))
        self.comboBox_2.setItemText(9, QCoreApplication.translate("Dialog", u"\u5341\u6708", None))
        self.comboBox_2.setItemText(10, QCoreApplication.translate("Dialog", u"\u5341\u4e00\u6708", None))
        self.comboBox_2.setItemText(11, QCoreApplication.translate("Dialog", u"\u5341\u4e8c\u6708", None))

        self.pushButtonNextMonth.setText(QCoreApplication.translate("Dialog", u">", None))
        self.pushButtonNextYear.setText(QCoreApplication.translate("Dialog", u">>", None))
        self.labelHint.setText(QCoreApplication.translate("Dialog", u"\u6309\u4e0b\u5b57\u6bcd\u6216\u6570\u5b57\u952e\uff0c\u7136\u540e\u914d\u5408\u65b9\u5411\u952e\u53ef\u4ee5\u7f16\u8f91\u9009\u62e9\u65e5\u671f", None))
    # retranslateUi

