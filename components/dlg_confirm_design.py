# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dlg_confirm_design.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)
from components import comp_icons_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 267)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 36)
        self.label_icon = QLabel(Dialog)
        self.label_icon.setObjectName(u"label_icon")
        font = QFont()
        font.setPointSize(8)
        self.label_icon.setFont(font)
        self.label_icon.setFrameShape(QFrame.Shape.NoFrame)
        self.label_icon.setPixmap(QPixmap(u":/icons/\u8be2\u95ee.png"))
        self.label_icon.setScaledContents(False)
        self.label_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_icon.setWordWrap(False)
        self.label_icon.setMargin(0)
        self.label_icon.setIndent(-1)
        self.label_icon.setOpenExternalLinks(False)

        self.horizontalLayout.addWidget(self.label_icon)

        self.label_text = QLabel(Dialog)
        self.label_text.setObjectName(u"label_text")
        font1 = QFont()
        font1.setPointSize(14)
        self.label_text.setFont(font1)

        self.horizontalLayout.addWidget(self.label_text)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStyleSheet(u"QDialogButtonBox QPushButton   {\n"
"	color: rgb(255, 255, 255);\n"
"    background-color: rgb(3, 147, 250); /* \u5929\u7a7a\u84dd\u80cc\u666f */\n"
"    border: 1px solid rgb(69, 139, 208); /* \u8fb9\u6846\u989c\u8272\u548c\u5bbd\u5ea6 */\n"
"    border-radius: 15px; /* \u5706\u89d2\u534a\u5f84 */\n"
"    padding: 20px 45px; /* \u5185\u8fb9\u8ddd\uff0c\u53ef\u4ee5\u6839\u636e\u9700\u8981\u8c03\u6574 */\n"
"    margin-bottom: 10px; /* \u5916\u8fb9\u8ddd\uff0c\u53ef\u9009\uff0c\u6839\u636e\u5b9e\u9645\u60c5\u51b5\u8c03\u6574 */\n"
"}\n"
"\n"
"/* \u9f20\u6807\u60ac\u505c\u65f6\u7684\u6837\u5f0f */\n"
"QDialogButtonBox QPushButton:hover {\n"
"    background-color: rgb(0, 103, 154); /* \u60ac\u505c\u65f6\u6539\u53d8\u80cc\u666f\u8272 */\n"
"}")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_icon.setText("")
        self.label_text.setText(QCoreApplication.translate("Dialog", u"\u63d0\u793a\u4fe1\u606f", None))
    # retranslateUi

