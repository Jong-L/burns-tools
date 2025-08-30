# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'thought_count_design.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
#将tools目录加入到sys.path中
import sys
sys.path.append('tools')
import tools.tool_icons_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(400, 559)
        Form.setStyleSheet(u"QcomboBox {\n"
"                background-color: #ffffff;\n"
"                border: 1px solid #bdc3c7;\n"
"                border-radius: 5px;\n"
"                padding: 5px;\n"
"            }")
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet(u"padding:-20px")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(4)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setStyleSheet(u"background-color: #ffffff;\n"
"border: 2px solid #ecf0f1;\n"
"border-radius: 15px;\n"
"padding: 20px;")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame.setLineWidth(1)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_5 = QPushButton(self.frame)
        self.pushButton_5.setObjectName(u"pushButton_5")
        font1 = QFont()
        font1.setPointSize(12)
        self.pushButton_5.setFont(font1)
        self.pushButton_5.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.pushButton_5.setStyleSheet(u"QPushButton:hover {\n"
"                background-color: rgb(206, 206, 206);\n"
"            }")
        icon = QIcon()
        icon.addFile(u":/icons/\u65e5\u5386.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_5.setIcon(icon)
        self.pushButton_5.setIconSize(QSize(20, 20))

        self.verticalLayout.addWidget(self.pushButton_5)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        font2 = QFont()
        font2.setFamilies([u"Microsoft YaHei UI"])
        font2.setPointSize(39)
        self.label_2.setFont(font2)
        self.label_2.setStyleSheet(u"color: rgb(0, 170, 255)")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_4 = QPushButton(self.frame)
        self.pushButton_4.setObjectName(u"pushButton_4")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy3)
        self.pushButton_4.setMinimumSize(QSize(30, 30))
        font3 = QFont()
        font3.setPointSize(11)
        self.pushButton_4.setFont(font3)
        self.pushButton_4.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_4.setStyleSheet(u"QPushButton {\n"
"                background-color: #e74c3c;\n"
"                color: white;\n"
"                border: none;\n"
"                border-radius: 30px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #c0392b;\n"
"            }\n"
"            QPushButton:pressed {\n"
"                background-color: #a93226;\n"
"            }")
        self.pushButton_4.setAutoDefault(False)

        self.horizontalLayout_2.addWidget(self.pushButton_4)

        self.pushButton_3 = QPushButton(self.frame)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy3.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy3)
        self.pushButton_3.setMinimumSize(QSize(30, 30))
        self.pushButton_3.setFont(font3)
        self.pushButton_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_3.setStyleSheet(u"QPushButton {\n"
"                background-color: #27ae60;\n"
"                color: white;\n"
"                border: none;\n"
"                border-radius: 30px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #229954;\n"
"            }\n"
"            QPushButton:pressed {\n"
"                background-color: #1e8449;\n"
"            }")

        self.horizontalLayout_2.addWidget(self.pushButton_3)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.verticalLayout_2.addWidget(self.frame)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(67)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(15, 36, 15, 25)
        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(0, 40))
        self.pushButton_2.setFont(font1)
        self.pushButton_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_2.setStyleSheet(u"QPushButton {\n"
"                background-color: rgb(255, 85, 0);\n"
"                color: white;\n"
"                border: none;\n"
"                border-radius: 8px;\n"
"                padding: 10px 20px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: rgb(255, 0, 0);\n"
"            }")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(0, 40))
        self.pushButton.setFont(font1)
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"                background-color: #9b59b6;\n"
"                color: white;\n"
"                border: none;\n"
"                border-radius: 8px;\n"
"                padding: 10px 20px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #8e44ad;\n"
"            }")

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u6d88\u6781\u601d\u7ef4\u8ba1\u6570\u5668", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u6d88\u6781\u601d\u7ef4\u8ba1\u6570\u5668", None))
        self.pushButton_5.setText(QCoreApplication.translate("Form", u"\u4eca\u5929", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"0", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"-", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"+", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"\u7edf\u8ba1", None))
    # retranslateUi

