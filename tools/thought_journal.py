import sys
import time
from typing import Dict, Optional, Any


from PySide6.QtWidgets import (QApplication, QButtonGroup, QWidget, QMessageBox, QDialog, 
                               QVBoxLayout,QHBoxLayout, QLabel, QGroupBox, QRadioButton, 
                               QDialogButtonBox, QPushButton,QFrame)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

from services.local_store import LocalStore
from services.stylesheet_loader import load_stylesheet

from tools.thought_journal_design import Ui_Form  # pyright: ignore[reportImplicitRelativeImport]
from tools.log_editor import EditLogWindow3Col,EditLogWindow6Col    # pyright: ignore[reportImplicitRelativeImport]

from components.dlg_info_design import Ui_Dialog as Ui_DialogInfo
from components.dlg_confirm_design import Ui_Dialog as Ui_DialogConfirm


# 常量定义
class LogConstants:
    """日志相关常量"""
    RATIONAL_RESPONSE_KEY = "理性回应"
    AUTOMATIC_THOUGHT_KEY = "下意识思维"
    COGNITIVE_DISTORTION_KEY = "认知扭曲"
    SITUATION_KEY = "情况"
    EMOTION_KEY = "情绪"
    RESULT_KEY = "结果"
    
    THREE_COLUMN_TYPE = "three_column"
    SIX_COLUMN_TYPE = "six_column"

    # UI相关常量
    CONTENT_PREVIEW_LENGTH = 100
    CARD_MIN_WIDTH = 300
    CARD_MIN_HEIGHT = 120
    CARD_MAX_HEIGHT = 150


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
        self.setObjectName("logEntryCard")
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)
        self.setMinimumSize(LogConstants.CARD_MIN_WIDTH, LogConstants.CARD_MIN_HEIGHT)
        self.setMaximumHeight(LogConstants.CARD_MAX_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        
        layout=QHBoxLayout(self)
        layout_text = QVBoxLayout()
        layout_text.setContentsMargins(10, 10, 10, 10)
        layout_text.setSpacing(5)

        #顶部信息，包括时间、模版类型，是否进行回应
        layout_top_label=QHBoxLayout()
        layout_top_label.setSpacing(16)
        # 时间
        timestamp = self.log.get("timestamp", 0)
        local_time = time.strftime("%Y-%m-%d", time.localtime(timestamp))
        time_label = QLabel(local_time)
        time_label.setProperty("role", "meta")
        time_label.setFont(QFont("Microsoft YaHei", 9))
        layout_top_label.addWidget(time_label)
        # 模版类型
        template_type=self.log.get("type", "unknown")
        type_label = QLabel(f"📝 {template_type}")
        type_label.setProperty("role", "meta")
        type_label.setFont(QFont("Microsoft YaHei", 9))
        layout_top_label.addWidget(type_label)
        #是否进行回应
        data=self.log.get("data", {})
        responseed=data.get(LogConstants.RATIONAL_RESPONSE_KEY,"")
        if responseed=="":
            response_label=QLabel("未回应")
            response_label.setProperty("role", "status-pill")
            response_label.setFont(QFont("Microsoft YaHei", 9))
            layout_top_label.addWidget(response_label)


        #设置伸缩
        layout_top_label.addStretch()

        layout_text.addLayout(layout_top_label)
        #内容
        content=data.get(LogConstants.AUTOMATIC_THOUGHT_KEY, "")
        if len(content) > LogConstants.CONTENT_PREVIEW_LENGTH:
            content = content[:LogConstants.CONTENT_PREVIEW_LENGTH] + "..."
        content_label = QLabel(content)
        content_label.setProperty("role", "content")
        content_label.setFont(QFont("Microsoft YaHei", 11))
        content_label.setWordWrap(True)
        layout_text.addWidget(content_label)

        layout.addLayout(layout_text)

        self.del_btn=CustomDelButton("删除", timestamp)
        self.del_btn.setProperty("variant", "card-delete")
        self.del_btn.setFont(QFont("Microsoft YaHei", 9))
        self.del_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.del_btn)

        #设置伸缩
        layout_text.setStretchFactor(layout_top_label, 1)
        layout_text.setStretchFactor(content_label, 3)
        layout.setStretchFactor(layout_text, 5)
        layout.setStretchFactor(self.del_btn, 1)

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
        three_col_desc = QLabel(f"{LogConstants.AUTOMATIC_THOUGHT_KEY} | {LogConstants.COGNITIVE_DISTORTION_KEY} | {LogConstants.RATIONAL_RESPONSE_KEY}")
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
        six_col_desc = QLabel(f"{LogConstants.SITUATION_KEY} | {LogConstants.EMOTION_KEY} | {LogConstants.AUTOMATIC_THOUGHT_KEY} | {LogConstants.COGNITIVE_DISTORTION_KEY} | {LogConstants.RATIONAL_RESPONSE_KEY} | {LogConstants.RESULT_KEY}")
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
            return LogConstants.THREE_COLUMN_TYPE
        elif button_id == 2:
            return LogConstants.SIX_COLUMN_TYPE
        return LogConstants.THREE_COLUMN_TYPE

class ThoughtJournalWindow(QWidget, Ui_Form):
    def __init__(self, main_window, storage: LocalStore):
        """
        初始化思维日志窗口
        设置界面布局、数据存储和事件连接
        """
        super(ThoughtJournalWindow, self).__init__()
        #self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.main_window = main_window
        self.storage = storage
        # 初始化日志数据列表，存储字典类型数据，字典中键为字符串，值为字符串或字符串列表
        self.logs: list[dict[str, Any]] = []
        #当前操作的日志时间戳
        self.timestamp = 0.0
        # 初始化编辑窗口为None，同时只允许一个编辑窗口存在
        self.edit_window: EditLogWindow3Col|None = None
        # 设置UI界面
        self.setupUi(Form=self)
        self.setObjectName("thoughtJournalWindow")
        # 创建日志布局管理器
        self.logs_layout_text = QVBoxLayout()
        self.logs_layout_text.setContentsMargins(6, 6, 6, 6)
        self.logs_layout_text.setSpacing(12)
        # 将布局应用到滚动区域的内容部件
        self.scrollAreaWidgetContents.setLayout(self.logs_layout_text)
        self._apply_styles()
        #滚动条样式
        self._apply_styles()
        # 加载已保存的日志数据
        self.load_data()
        # 连接添加按钮的点击事件到add_log方法
        _=self.pushButtonAdd.clicked.connect(self.add_log)

    def _apply_styles(self) -> None:
        self.setStyleSheet(load_stylesheet("styles/thought_journal.qss"))


    def load_data(self):
        """加载日志数据"""
        try:
            self.logs = self.storage.get_journal_logs()
        except Exception as e:
            QMessageBox.warning(self, "提示", f"加载日志数据失败：{e}")
            self.logs = []
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
            labelNoLogs.setProperty("role", "empty-state")
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
            try:
                self.storage.delete_journal_log(timestamp)
            except Exception as e:
                QMessageBox.warning(self, "提示", f"删除日志失败：{e}")
                return
            self.load_data()

    def open_edit_window(self, type: str, log: Optional[Dict[str, Any]] = None) -> None:
        """打开编辑窗口"""
        if type == LogConstants.THREE_COLUMN_TYPE:
            self.edit_window=EditLogWindow3Col()
            if log is not None:#如果有传入日志数据,获取数据并设置到编辑窗口
                self.timestamp = log.get("timestamp")
                data=log.get("data")
                automatic_thought=data.get(LogConstants.AUTOMATIC_THOUGHT_KEY, "")
                rational_response=data.get(LogConstants.RATIONAL_RESPONSE_KEY, "")
                distortions=data.get(LogConstants.COGNITIVE_DISTORTION_KEY, [])
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
        elif type == LogConstants.SIX_COLUMN_TYPE:
            self.edit_window=EditLogWindow6Col()
            if log is not None:#如果有传入日志数据
                self.timestamp = log.get("timestamp")
                data=log.get("data")
                situation=data.get(LogConstants.SITUATION_KEY, "")
                emotion=data.get(LogConstants.EMOTION_KEY, "")
                automatic_thought=data.get(LogConstants.AUTOMATIC_THOUGHT_KEY, "")
                rational_response=data.get(LogConstants.RATIONAL_RESPONSE_KEY, "")
                result=data.get(LogConstants.RESULT_KEY, "")
                distortions=data.get(LogConstants.COGNITIVE_DISTORTION_KEY, [])
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

    def _save_log(self, log_type: str, data: Dict[str, Any]) -> None:
        timestamp = self.timestamp or time.time()
        try:
            self.storage.upsert_journal_log(log_type=log_type, timestamp=timestamp, data=data)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"保存日志失败：{e}")
            return

        self.timestamp = 0
        self.load_data()
        self._show_save_success_dialog()

    def _show_save_success_dialog(self) -> None:
        dlg = QDialog(self.edit_window)
        ui = Ui_DialogInfo()
        ui.setupUi(dlg)
        ui.label_text.setText("保存成功")
        ok_button = ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setText("确定")
        dlg.exec()
        
    def save_log_3col(self):
        """在编辑窗口编辑后保存日志"""
        automatic_thought = self.edit_window.automatic_thought_edit.toPlainText()
        rational_response = self.edit_window.rational_response_edit.toPlainText()
        distortions = self.edit_window.distortions_list
        data={
            LogConstants.AUTOMATIC_THOUGHT_KEY: automatic_thought,
            LogConstants.COGNITIVE_DISTORTION_KEY: distortions,
            LogConstants.RATIONAL_RESPONSE_KEY: rational_response
            }
        self._save_log(LogConstants.THREE_COLUMN_TYPE, data)

    def save_log_6col(self):
        """在编辑窗口编辑后保存六列日志"""
        situation = self.edit_window.situation_edit.toPlainText()
        emotion = self.edit_window.emotion_edit.toPlainText()
        automatic_thought = self.edit_window.automatic_thought_edit.toPlainText()
        distortions = self.edit_window.distortions_list
        rational_response = self.edit_window.rational_response_edit.toPlainText()
        result = self.edit_window.result_edit.toPlainText()
        data={
        LogConstants.SITUATION_KEY: situation,
        LogConstants.EMOTION_KEY: emotion,
        LogConstants.AUTOMATIC_THOUGHT_KEY: automatic_thought,
        LogConstants.COGNITIVE_DISTORTION_KEY: distortions,
        LogConstants.RATIONAL_RESPONSE_KEY: rational_response,
        LogConstants.RESULT_KEY: result
        }
        self._save_log(LogConstants.SIX_COLUMN_TYPE, data)

    def close_edit_window(self):
        """关闭编辑窗口"""
        if self.edit_window is not None:
            self.edit_window.close()
        #重置时间戳
        self.timestamp=0

    def closeEvent(self, event):
        # 通知主窗口清理
        if self.main_window and hasattr(self.main_window, 'close_tool'):
            self.main_window.close_tool("thought_journal")
        super().closeEvent(event)

