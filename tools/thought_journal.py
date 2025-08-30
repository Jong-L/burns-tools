import sys
import os
import json
import time


from PySide6.QtWidgets import (QApplication, QButtonGroup, QWidget, QMessageBox, QDialog, 
                               QVBoxLayout,QHBoxLayout, QLabel, QGroupBox, QRadioButton, 
                               QDialogButtonBox, QPushButton,QFrame)
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtCore import Qt, Signal


from tools.thought_journal_design import Ui_Form  # pyright: ignore[reportImplicitRelativeImport]
from tools.log_editor import EditLogWindow3Col,EditLogWindow6Col    # pyright: ignore[reportImplicitRelativeImport]

from components.dlg_info_design import Ui_Dialog as Ui_DialogInfo
from components.dlg_confirm_design import Ui_Dialog as Ui_DialogConfirm


class CustomDelButton(QPushButton):
    """自定义删除按钮,点击时发出时间戳信息"""
    customClicked = Signal(float)
    def __init__(self, text,timestamp):
        super().__init__(text)
        self.timestamp = timestamp
        self.clicked.connect(self.on_clicked)
    def on_clicked(self):
        self.customClicked.emit(self.timestamp)
class LogEntryCard(QFrame):
    """日志条目卡片"""
    clicked=Signal(str,dict)
    def __init__(self, log):
        super().__init__()
        self.log=log
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.setMinimumSize(300, 120)
        self.setMaximumHeight(150)
        self.setCursor(Qt.PointingHandCursor)

        layout=QHBoxLayout(self)
        layout_text = QVBoxLayout()
        layout_text.setContentsMargins(10, 10, 10, 10)
        layout_text.setSpacing(0)
        # 时间
        timestamp = self.log.get("timestamp", 0)
        local_time = time.strftime("%Y-%m-%d", time.localtime(timestamp))
        time_label = QLabel(local_time)
        time_label.setFont(QFont("Microsoft YaHei", 9))
        time_label.setStyleSheet("color: #3498db;")
        layout_text.addWidget(time_label)
        # 模版类型
        template_type=self.log.get("type", "unknown")
        type_label = QLabel(f"📝 {template_type}")
        type_label.setFont(QFont("Microsoft YaHei", 9))
        type_label.setStyleSheet("color: #3498db;")
        layout_text.addWidget(type_label)

        #内容
        data=self.log.get("data", {})
        content=data.get("下意识思维", "")
        if len(content) > 100:
            content = content[:100] + "..."
        content_label = QLabel(content)
        content_label.setFont(QFont("Microsoft YaHei", 11))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #2c3e50;")
        layout_text.addWidget(content_label)

        layout.addLayout(layout_text)

        self.del_btn=CustomDelButton("删除", timestamp)
        self.del_btn.setFont(QFont("Microsoft YaHei", 9))
        self.del_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.del_btn)

        #设置伸缩
        layout_text.setStretchFactor(time_label, 1)
        layout_text.setStretchFactor(type_label, 1)
        layout_text.setStretchFactor(content_label, 3)
        layout.setStretchFactor(layout_text, 5)
        layout.setStretchFactor(self.del_btn, 1)

        #设置卡片样式
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #ecf0f1;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 1px solid #3498db;
                background-color: #f8f9fa;
            }
            QLabel {
                background-color: transparent;
                border: None;
            }
            QLabel:hover {
                border: None;
                background-color: transparent;
            }
            QPushButton {
                background-color: #e74c3c;
                border: None;
                border-radius: 8px;
                padding: 12px 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.log.get("type", "unknown"),self.log)
class TemplateSelectionDialog(QDialog):
    """模板选择对话框"""
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("选择日志模板")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout_text = QVBoxLayout(self)
        layout_text.setSpacing(20)
        
        # 标题
        title_label = QLabel("请选择日志模板类型")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_text.addWidget(title_label)
        
        # 模板选择组
        group_box = QGroupBox("模板类型")
        group_layout_text = QVBoxLayout(group_box)
        
        self.button_group: QButtonGroup = QButtonGroup()
        
        # 三列模板
        three_col_radio = QRadioButton("三列模板")
        three_col_radio.setFont(QFont("Microsoft YaHei", 11))
        three_col_radio.setCursor(Qt.PointingHandCursor)
        three_col_desc = QLabel("下意识思维 | 认知扭曲 | 理性回应")
        three_col_desc.setCursor(Qt.PointingHandCursor)
        three_col_desc.mousePressEvent=lambda event: three_col_radio.click()
        three_col_desc.setFont(QFont("Microsoft YaHei", 9))
        three_col_desc.setStyleSheet("color: #7f8c8d; margin-left: 20px;")
        group_layout_text.addWidget(three_col_radio)
        group_layout_text.addWidget(three_col_desc)
        
        # 六列模板
        six_col_radio = QRadioButton("六列模板")
        six_col_radio.setFont(QFont("Microsoft YaHei", 11))
        six_col_radio.setCursor(Qt.PointingHandCursor)
        six_col_desc = QLabel("情景 | 情绪 | 下意识思维 | 认知扭曲 | 理性回应 | 结果")
        six_col_desc.setCursor(Qt.PointingHandCursor)
        six_col_desc.mousePressEvent=lambda event: six_col_radio.click()
        six_col_desc.setFont(QFont("Microsoft YaHei", 9))
        six_col_desc.setStyleSheet("color: #7f8c8d; margin-left: 20px;")
        group_layout_text.addWidget(six_col_radio)
        group_layout_text.addWidget(six_col_desc)
        
        # 默认选择三列模板
        three_col_radio.setChecked(True)
        
        self.button_group.addButton(three_col_radio, 1)
        self.button_group.addButton(six_col_radio, 2)
        
        layout_text.addWidget(group_box)
        
        # 按钮
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox: QDialogButtonBox=QDialogButtonBox(buttons)
        ok_button=self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("确定")
        ok_button.setCursor(Qt.PointingHandCursor)
        cancel_button=self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("取消")
        cancel_button.setCursor(Qt.PointingHandCursor)
        # 添加按钮样式
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                
                background-color: #c0392b;
            }                         
        """)
        _=self.buttonBox.accepted.connect(self.accept)
        _=self.buttonBox.rejected.connect(self.reject)
        layout_text.addWidget(self.buttonBox)

    def get_selected_template(self):
        """获取选择的模板类型"""
        button_id = self.button_group.checkedId()
        if button_id == 1:
            return "three_column"
        elif button_id == 2:
            return "six_column"
        return "three_column"

class ThoughtJournalWindow(QWidget, Ui_Form):
    def __init__(self,main_window):
        """
        初始化思维日志窗口
        设置界面布局、数据存储和事件连接
        """
        super(ThoughtJournalWindow, self).__init__()
        #self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window=main_window
        # 初始化日志数据列表，存储字典类型数据，字典中键为字符串，值为字符串或字符串列表
        self.logs: list[dict[str, str|list[str]]]=[]#日志数据
        #当前操作的日志时间戳
        self.timestamp=0
        # 初始化编辑窗口为None
        self.edit_window: EditLogWindow3Col|None = None
        # 设置UI界面
        self.setupUi(Form=self)
        # 创建日志布局管理器
        self.logs_layout_text = QVBoxLayout()
        # 将布局应用到滚动区域的内容部件
        self.scrollAreaWidgetContents.setLayout(self.logs_layout_text)
        #滚动条样式
        self.scrollArea.setStyleSheet("""
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
        """
        )
        # 加载已保存的日志数据
        self.load_data()
        # 连接添加按钮的点击事件到add_log方法
        _=self.pushButtonAdd.clicked.connect(self.add_log)

    def load_data(self):
        """加载日志数据"""
        #文件不存在则创建
        if not os.path.exists('data/消极思维日志.json'):
            with open('data/消极思维日志.json', 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        #处理空文件
        if os.path.getsize('data/消极思维日志.json') <= 0:
            self.logs = []
            return
        try:
            with open('data/消极思维日志.json', 'r', encoding='utf-8') as f:
                self.logs = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载日志数据失败：{e}")
            self.logs = []
        else:
            self.update_log_card_list()

    def update_log_card_list(self):
        """更新日志卡片列表"""
        # 清空当前列表
        if self.logs_layout_text.count() > 0:#如果日志列表不为空
            for i in reversed(range(self.logs_layout_text.count())):
                widget = self.logs_layout_text.itemAt(i).widget()
                if widget is not None:
                    self.logs_layout_text.removeWidget(widget)
                    widget.deleteLater()
        # 添加新的日志卡片
        if self.logs and len(self.logs) > 0:
            for log in self.logs:
                card =LogEntryCard(log)
                card.clicked.connect(self.open_edit_window)
                card.del_btn.customClicked.connect(self.del_log)
                #self.logs_layout_text.insertWidget(self.logs_layout_text.count()-1, card) 
                self.logs_layout_text.addWidget(card)
        else:
            labelNoLogs=QLabel("还没有日志")
            labelNoLogs.setAlignment(Qt.AlignCenter)
            labelNoLogs.setStyleSheet("font-size: 16px; color: #999;")
            self.logs_layout_text.addWidget(labelNoLogs)

    def del_log(self,timestamp):
        """删除日志"""
        dlg=QDialog(self)
        ui=Ui_DialogConfirm()
        ui.setupUi(Dialog=dlg)
        ui.label_text.setText("确定要删除该日志吗？")
        ok_button=ui.buttonBox.button(QDialogButtonBox.Ok)
        ok_button.setText("确定")
        cancel_button=ui.buttonBox.button(QDialogButtonBox.Cancel)
        cancel_button.setText("取消")
        if dlg.exec() == QDialog.Accepted:
            for log in self.logs:
                if log.get("timestamp") == timestamp:
                    self.logs.remove(log)
                    break
            self.update_log_card_list()
            self.save_log_data()

    def open_edit_window(self,type,log=None):
        """打开编辑窗口"""
        if type == "three_column":
            self.edit_window=EditLogWindow3Col()
            if log is not None:#如果有传入日志数据,获取数据并设置到编辑窗口
                self.timestamp = log.get("timestamp")
                data=log.get("data")
                automatic_thought=data.get("下意识思维", "")
                rational_response=data.get("理性回应", "")
                distortions=data.get("认知扭曲", [])
                #设置文本编辑框内容
                self.edit_window.automatic_thought_edit.setPlainText(automatic_thought)
                self.edit_window.rational_response_edit.setPlainText(rational_response)
                #设置认知扭曲列表
                for distortion in distortions:
                    self.edit_window.add_distortion_item(distortion)
            _=self.edit_window.save_btn.clicked.connect(self.save_log_3col)
            _=self.edit_window.cancel_btn.clicked.connect(self.close_edit_window)
            _=self.edit_window.windowClosing.connect(self.close_edit_window)
            self.edit_window.show()
        elif type == "six_column":
            self.edit_window=EditLogWindow6Col()
            if log is not None:#如果有传入日志数据
                self.timestamp = log.get("timestamp")
                data=log.get("data")
                situation=data.get("情况", "")
                emotion=data.get("情绪", "")
                automatic_thought=data.get("下意识思维", "")
                rational_response=data.get("理性回应", "")
                result=data.get("结果", "")
                distortions=data.get("认知扭曲", [])
                #设置文本编辑框内容
                self.edit_window.situation_edit.setPlainText(situation)
                self.edit_window.emotion_edit.setPlainText(emotion)
                self.edit_window.automatic_thought_edit.setPlainText(automatic_thought)
                self.edit_window.rational_response_edit.setPlainText(rational_response)
                self.edit_window.result_edit.setPlainText(result)
                #设置认知扭曲列表
                for distortion in distortions:
                    self.edit_window.add_distortion_item(distortion)
            _=self.edit_window.save_btn.clicked.connect(self.save_log_6col)
            _=self.edit_window.cancel_btn.clicked.connect(self.close_edit_window)
            _= self.edit_window.windowClosing.connect(self.close_edit_window)
            self.edit_window.show()
        else:
            QMessageBox.warning(self, "提示", "未知的日志类型")

    def add_log(self):
        """添加日志"""
        # 选择模板对话框
        dialog = TemplateSelectionDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template = dialog.get_selected_template()
            # 编辑窗口
            self.open_edit_window(template)

    def save_log_data(self):
        """保存日志数据"""
        try:
            with open('data/消极思维日志.json', 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False,indent=4)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"保存日志数据失败：{e}")

    def save_log_3col(self):
        """编辑后保存三列日志"""
        if self.edit_window is not None:
            if self.timestamp!=0:
                for log in self.logs:
                    if log.get("timestamp")==self.timestamp:
                        self.logs.remove(log)
                        break
            timestamp=time.time()
            automatic_thought = self.edit_window.automatic_thought_edit.toPlainText()
            rational_response = self.edit_window.rational_response_edit.toPlainText()
            distortions = self.edit_window.distortions_list
            data={
                "下意识思维":automatic_thought,
                "认知扭曲":distortions,
                "理性回应":rational_response}
            temp_dict = {
                "type": "three_column",
                "timestamp":timestamp,
                "data": data
            }
            self.logs.append(temp_dict)
            with open('data/消极思维日志.json', 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False,indent=4)
            dlg=QDialog(self.edit_window)
            ui=Ui_DialogInfo()
            ui.setupUi(dlg)
            ui.label_text.setText("保存成功")
            ok_button=ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
            ok_button.setText("确定")
            dlg.exec()
            self.update_log_card_list()
        else:
            _=QMessageBox.warning(self, "错误", "未获取到窗口实例")
        #重置时间戳
        self.timestamp=0

    def save_log_6col(self):
        """编辑后保存六列日志"""
        if self.timestamp!=0:
            for log in self.logs:
                if log.get("timestamp")==self.timestamp:
                    self.logs.remove(log)
                    break
        if self.edit_window is not None:
            timestamp=time.time()
            situation = self.edit_window.situation_edit.toPlainText()
            emotion = self.edit_window.emotion_edit.toPlainText()
            automatic_thought = self.edit_window.automatic_thought_edit.toPlainText()
            distortions = self.edit_window.distortions_list
            rational_response = self.edit_window.rational_response_edit.toPlainText()
            result = self.edit_window.result_edit.toPlainText()
            data={
            "情景":situation,
            "情绪":emotion,
            "下意识思维":automatic_thought,
            "认知扭曲":distortions,
            "理性回应":rational_response,
            "结果":result
            }
            temp_dict = {
                "type": "six_column",
                "timestamp":timestamp,
                "data": data
            }
            self.logs.append(temp_dict)
            with open('data/消极思维日志.json', 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False, indent=4)
            dlg=QDialog(self.edit_window)
            ui=Ui_DialogInfo()
            ui.setupUi(dlg)
            ui.label_text.setText("保存成功")
            dlg.exec()
            self.update_log_card_list()
        else:
            _=QMessageBox.warning(self, "错误", "未获取到窗口实例")
        #重置时间戳
        self.timestamp=0

    def close_edit_window(self):
        """关闭编辑窗口"""
        if self.edit_window is not None:
            self.edit_window.close()
        #重置时间戳
        self.timestamp=0

    def closeEvent(self, event):
        # 通知主窗口清理
        if self.main_window and hasattr(self.main_window, 'close_tool'):
            self.main_window.close_tool("消极思维日志")

