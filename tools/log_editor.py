import sys

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QRadioButton,
    QGroupBox, QScrollArea, QFrame, QButtonGroup,QCheckBox,QSizePolicy
)
from PySide6.QtCore import Qt, Signal,QSize


class DistortionSelectionDialog(QDialog):
    """ 选择认知扭曲类型对话框 """
    def __init__(self, distortions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择认知扭曲")
        self.setModal(True)# 设置为模态对话框，在对话框关闭前阻止其他窗口操作
        self.distortions = distortions
        self.selected_distortion = None
        self.radio_buttons = []
        self.button_group = QButtonGroup(self)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        #是否追加描述
        self.descEdit=QTextEdit()
        self.descEdit.setPlaceholderText("编辑描述")
        layout.addWidget(self.descEdit)

        # 标题
        title_label = QLabel("请选择一个认知扭曲类型：")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
                    QScrollArea{
        border: 0px solid;
        border-right-width: 1px;
        border-right-color: #dcdbdc;
        background-color: #f5f5f7;
        }
        QScrollBar:vertical {
        border: none;
        background: #f5f5f7;
        width: 10px;
        margin: 0px 0 0px 0;
        }
        QScrollBar::handle:vertical {
        background: Gainsboro;
        min-height: 20px;
        border-radius: 5px;
        border: none;
        }
        QScrollBar::add-line:vertical {
        border: 0px solid grey;
        background: #32CC99;
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
        border: 0px solid grey;
        background: #32CC99;
        height: 0px;
        subcontrol-position: top;
        subcontrol-origin: margin;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
        width: 0px;
        height: 0px;
        }

        """)
        
        group_box = QGroupBox()
        group_box.setStyleSheet("border: none;")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)
        group_layout.setContentsMargins(10, 10, 10, 10)

        # 创建单选按钮
        for i, (name, desc) in enumerate(distortions.items()):
            radio = QRadioButton(f"{name}")
            radio.setCursor(Qt.PointingHandCursor)
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 13px;
                    spacing: 8px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QRadioButton::indicator:unchecked {
                    image: url(none);
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    background-color: white;
                }
                QRadioButton::indicator:checked {
                    image: url(none);
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    background-color: #3498db;
                }
            """)
            self.button_group.addButton(radio, i)
            self.radio_buttons.append((name, radio))
            group_layout.addWidget(radio)
            
            # 描述文本
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("""
                color: #7f8c8d;
                font-size: 12px;
                margin-left: 24px;
                margin-bottom: 8px;
            """)
            desc_label.setWordWrap(True)
            desc_label.mousePressEvent=lambda event,r=radio: r.click()
            desc_label.setCursor(Qt.PointingHandCursor)
            group_layout.addWidget(desc_label)
            # 添加分隔线
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #ecf0f1;")
            group_layout.addWidget(line)

        group_box.setLayout(group_layout)
        scroll.setWidget(group_box)
        layout.addWidget(scroll)

        # 按钮区域
        buttons = QDialogButtonBox()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        
        self.ok_button.setObjectName("okButton")
        self.cancel_button.setObjectName("cancelButton")

        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        
        buttons.addButton(self.ok_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.setEnabled(False)  # 默认禁用确定按钮
        
        # 连接单选按钮信号
        self.button_group.buttonClicked.connect(self.on_radio_clicked)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
        # 应用样式
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                font-family: "Segoe UI", sans-serif;
            }
        """)
        
        self.ok_button.setStyleSheet("""
            QPushButton#okButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#okButton:hover {
                background-color: #2980b9;
            }
            QPushButton#okButton:disabled {
                background-color: #bdc3c7;
                color: #95a5a6;
            }
        """)
        
        self.cancel_button.setStyleSheet("""
            QPushButton#cancelButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#cancelButton:hover {
                background-color: #c0392b;
            }
        """)

    def on_radio_clicked(self, button):
        self.ok_button.setEnabled(True)

    def get_selected(self):
        checked_button = self.button_group.checkedButton()
        if checked_button:
            for name, radio in self.radio_buttons:
                if radio == checked_button:
                    return (name,self.descEdit.toPlainText())
        return None


class DistortionItemWidget(QWidget):
    """ 认知扭曲条目卡片 """
    def __init__(self, text, on_delete, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(text)
        label.setStyleSheet("font-size: 14px;")
        label.setWordWrap(True)
        label.setMinimumWidth(120)
        label.setMaximumWidth(120)
        layout.addWidget(label)

        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton{
                background-color: #e74c3c;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(on_delete)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

class EditLogWindow3Col(QWidget):
    """ 编辑日志窗口 """
    windowClosing = Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("编辑日志")
        self.resize(800, 550)
        self.distortions_list = []

        # 认知扭曲数据
        self.distortion_data = {
            "非此即彼": "用非黑即白的极端方式看待事物。如果表现不够完美，就会认为自己彻底失败。",
            "以偏概全": "基于单一事件推断出广泛结论，常使用“总是”、“从不”等绝对化语言。",
            "心理过滤": "专注于消极事件而忽略积极方面，只看到负面信息，好像戴上了一副有色眼镜。",
            "否定正面思考": "拒绝接受正面的经验，找理由告诉自己这些经验不算数。",
            "妄下结论 - 读心术": "未经证实就认为知道别人在想什么，通常假设他人对自己有负面看法。",
            "妄下结论 - 先知错误": "预测事情会变得很糟糕，并坚信这一预言为事实。",
            "放大和缩小": "夸大自己的错误或他人的成就，同时缩小自己的优点或他人的缺点。",
            "情绪化推理": "根据感觉来判断现实，“我这么感觉，所以它肯定是真的”。",
            "‘应该’句式": "常用“我应该…”、“我不应该…”来要求自己或他人，带来内疚感或愤怒。",
            "乱贴标签": "给自己或他人贴上固定、消极的标签，而不是描述具体的行为。",
            "罪责归己": "即使没有直接责任，也会将外界的消极事件归咎于自己。"
        }

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 第一行：标题
        title_label = QLabel("消极思维日志")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # 第二行：标签
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("下意识思维"))
        label_layout.addWidget(QLabel("认知扭曲"))
        label_layout.addWidget(QLabel("理性回应"))
        for i in range(label_layout.count()):
            widget = label_layout.itemAt(i).widget()
            widget.setObjectName("fieldLabel")
            widget.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(label_layout)

        # 第三行：输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)

        # 左侧：下意识思维输入框
        self.automatic_thought_edit = QTextEdit()
        self.automatic_thought_edit.setPlaceholderText("请输入你的下意识思维...")
        input_layout.addWidget(self.automatic_thought_edit)

        # 中间：认知扭曲列表和添加按钮
        distortion_layout = QVBoxLayout()
        distortion_layout.setContentsMargins(0, 0, 0, 0)
        distortion_layout.setSpacing(0)
        
        self.distortion_list_widget = QListWidget()
        self.distortion_list_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.distortion_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 180px;
                max-width: 180px;
            }
        """)
        distortion_layout.addWidget(self.distortion_list_widget)

        self.add_distortion_btn = QPushButton("+ 添加认知扭曲")
        self.add_distortion_btn.setObjectName("addDistortionBtn")
        self.add_distortion_btn.setCursor(Qt.PointingHandCursor)
        self.add_distortion_btn.clicked.connect(self.open_distortion_dialog)
        distortion_layout.addWidget(self.add_distortion_btn)

        input_layout.addLayout(distortion_layout)

        # 右侧：理性回应输入框
        self.rational_response_edit = QTextEdit()
        self.rational_response_edit.setPlaceholderText("请输入你的理性回应...")
        input_layout.addWidget(self.rational_response_edit)

        main_layout.addLayout(input_layout)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn: QPushButton = QPushButton("保存")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn: QPushButton = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI", sans-serif;
                background-color: #f9f9f9;
            }
            #titleLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            #fieldLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
            QPushButton#addDistortionBtn, QPushButton#saveBtn, QPushButton#cancelBtn {
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 6px;
            }
            #addDistortionBtn {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                border: none;
            }
            #addDistortionBtn:hover {
                background-color: #27ae60;
            }
            #saveBtn {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
            }
            #saveBtn:hover {
                background-color: #2980b9;
            }
            #cancelBtn {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                border: none;
            }
            #cancelBtn:hover {
                background-color: #c0392b;
            }
        """)

    def open_distortion_dialog(self):
        """
        打开认知扭曲选择对话框的方法
        当用户选择并确认后，将选中的添加到列表中（如果尚未存在）
        """
        # 创建失真选择对话框实例，传入失真数据和父窗口
        dialog = DistortionSelectionDialog(self.distortion_data, self)
        # 检查对话框是否被接受（用户点击了确认按钮）
        if dialog.exec() == QDialog.Accepted:
            # 获取用户选择
            selected = dialog.get_selected()
            # 检查是否有选择并且该选择不在当前的列表中
            if selected and selected not in self.distortions_list:
                # 如果选择有效且不存在于列表中，则添加
                self.add_distortion_item(selected)

    def add_distortion_item(self, distortion_item):
        """ 添加认知扭曲项到列表和QListWidget """
        # 将失真项添加到失真列表中
        self.distortions_list.append(distortion_item)
        # 创建一个新的列表项
        item = QListWidgetItem()
        # 检查项是否有描述信息
        if distortion_item[1]!="":
            text= f'<font color="#39b0ff"><b>{distortion_item[0]}</b></font> :  {distortion_item[1]}'
        else:
            text= f'<font color="#39b0ff"><b>{distortion_item[0]}</b></font>'

        widget = DistortionItemWidget(text, lambda: self.remove_distortion_item(item, distortion_item))
        item.setSizeHint(widget.sizeHint()+QSize(0, 50))
        self.distortion_list_widget.addItem(item)
        self.distortion_list_widget.setItemWidget(item, widget)

    def remove_distortion_item(self, item, distortion_item):
        self.distortions_list.remove(distortion_item)
        row = self.distortion_list_widget.row(item)
        self.distortion_list_widget.takeItem(row)

    def closeEvent(self, event):
        self.windowClosing.emit()
        super().closeEvent(event)

class EditLogWindow6Col(QWidget):
    """ 编辑日志窗口（6列） """ 
    windowClosing=Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("编辑日志")
        self.resize(1100, 600)
        self.distortions_list = []

        # 认知扭曲数据
        self.distortion_data = {
            "非此即彼": "用非黑即白的极端方式看待事物。如果表现不够完美，就会认为自己彻底失败。",
            "以偏概全": "基于单一事件推断出广泛结论，常使用“总是”、“从不”等绝对化语言。",
            "心理过滤": "专注于消极事件而忽略积极方面，只看到负面信息，好像戴上了一副有色眼镜。",
            "否定正面思考": "拒绝接受正面的经验，找理由告诉自己这些经验不算数。",
            "妄下结论 - 读心术": "未经证实就认为知道别人在想什么，通常假设他人对自己有负面看法。",
            "妄下结论 - 先知错误": "预测事情会变得很糟糕，并坚信这一预言为事实。",
            "放大和缩小": "夸大自己的错误或他人的成就，同时缩小自己的优点或他人的缺点。",
            "情绪化推理": "根据感觉来判断现实，“我这么感觉，所以它肯定是真的”。",
            "‘应该’句式": "常用“我应该…”、“我不应该…”来要求自己或他人，带来内疚感或愤怒。",
            "乱贴标签": "给自己或他人贴上固定、消极的标签，而不是描述具体的行为。",
            "罪责归己": "即使没有直接责任，也会将外界的消极事件归咎于自己。"
        }

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 第一行：标题
        title_label = QLabel("思维记录日志")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # 第二行：标签
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("情景"))
        label_layout.addWidget(QLabel("情绪"))
        label_layout.addWidget(QLabel("下意识思维"))
        label_layout.addWidget(QLabel("认知扭曲"))
        label_layout.addWidget(QLabel("理性回应"))
        label_layout.addWidget(QLabel("结果"))

        for i in range(label_layout.count()):
            widget = label_layout.itemAt(i).widget()
            widget.setObjectName("fieldLabel")
            widget.setAlignment(Qt.AlignCenter)

        main_layout.addLayout(label_layout)

        # 第三行：输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)

        # 左侧：情景输入框
        self.situation_edit = QTextEdit()
        self.situation_edit.setPlaceholderText("请描述当前情景...")
        input_layout.addWidget(self.situation_edit)

        # 中间：情绪输入框
        self.emotion_edit = QTextEdit()
        self.emotion_edit.setPlaceholderText("请描述你的情绪...")
        input_layout.addWidget(self.emotion_edit)

        # 中间：下意识思维输入框
        self.automatic_thought_edit = QTextEdit()
        self.automatic_thought_edit.setPlaceholderText("请输入你的下意识思维...")
        input_layout.addWidget(self.automatic_thought_edit)

        # 中间：认知扭曲列表和添加按钮
        distortion_layout = QVBoxLayout()
        distortion_layout.setSpacing(8)

        self.distortion_list_widget = QListWidget()
        self.distortion_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-width: 180px;
                max-width: 180px;
            }
        """)
        distortion_layout.addWidget(self.distortion_list_widget)

        self.add_distortion_btn = QPushButton("+ 添加认知扭曲")
        self.add_distortion_btn.setObjectName("addDistortionBtn")
        self.add_distortion_btn.setCursor(Qt.PointingHandCursor)
        self.add_distortion_btn.clicked.connect(self.open_distortion_dialog)
        distortion_layout.addWidget(self.add_distortion_btn)

        input_layout.addLayout(distortion_layout)

        # 右侧：理性回应输入框
        self.rational_response_edit = QTextEdit()
        self.rational_response_edit.setPlaceholderText("请输入你的理性回应...")
        input_layout.addWidget(self.rational_response_edit)

        # 右侧：结果输入框
        self.result_edit = QTextEdit()
        self.result_edit.setPlaceholderText("请描述结果...")
        input_layout.addWidget(self.result_edit)

        main_layout.addLayout(input_layout)

        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: "Segoe UI", sans-serif;
            }

            QLabel#fieldLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 14px;
            }

            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }

            QTextEdit:focus {
                border: 1px solid #3498db;
            }

            QPushButton#addDistortionBtn {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#addDistortionBtn:hover {
                background-color: #27ae60;
            }

            QPushButton#saveBtn {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#saveBtn:hover {
                background-color: #2980b9;
            }

            QPushButton#cancelBtn {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }

            QPushButton#cancelBtn:hover {
                background-color: #c0392b;
            }
        """)

    def open_distortion_dialog(self):
        dialog = DistortionSelectionDialog(self.distortion_data, self)
        if dialog.exec() == QDialog.Accepted:
            distortion = dialog.get_selected()
            if distortion and distortion not in self.distortions_list:
                self.add_distortion_item(distortion)

    def add_distortion_item(self, distortion_item):
        """ 添加一个认知扭曲项 """ 
        item = QListWidgetItem()
        if distortion_item[1]!="":
            text= f'<font color="#39b0ff"><b>{distortion_item[0]}</b></font> :  {distortion_item[1]}'
        else:
            text= f'<font color="#39b0ff"><b>{distortion_item[0]}</b></font>'
        item_widget = DistortionItemWidget(text, lambda: self.distortion_list_widget.takeItem(self.distortion_list_widget.row(item)))
        item.setSizeHint(item_widget.sizeHint()+QSize(0, 50))
        self.distortions_list.append(distortion_item)
        self.distortion_list_widget.addItem(item)
        self.distortion_list_widget.setItemWidget(item, item_widget)

    def closeEvent(self, event):
        self.windowClosing.emit()
        super().closeEvent(event)

# 示例调用入口（可选）
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = EditLogWindow3Col()
    window.show()
    sys.exit(app.exec())