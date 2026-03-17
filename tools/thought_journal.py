import sys
import os
import json
import time
from typing import Dict, List, Optional, Any, Union


from PySide6.QtWidgets import (QApplication, QButtonGroup, QWidget, QMessageBox, QDialog, 
                               QVBoxLayout,QHBoxLayout, QLabel, QGroupBox, QRadioButton, 
                               QDialogButtonBox, QPushButton,QFrame)
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtCore import Qt, Signal


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
    
    LOG_FILE_PATH = 'data/消极思维日志.json'
    
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
        time_label.setFont(QFont("Microsoft YaHei", 9))
        time_label.setStyleSheet("color: #3498db;")
        layout_top_label.addWidget(time_label)
        # 模版类型
        template_type=self.log.get("type", "unknown")
        type_label = QLabel(f"📝 {template_type}")
        type_label.setFont(QFont("Microsoft YaHei", 9))
        type_label.setStyleSheet("color: #3498db;")
        layout_top_label.addWidget(type_label)
        #是否进行回应
        data=self.log.get("data", {})
        responseed=data.get(LogConstants.RATIONAL_RESPONSE_KEY,"")
        if responseed=="":
            response_label=QLabel("未回应")
            response_label.setFont(QFont("Microsoft YaHei", 9))
            response_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #ff6b6b;
                    border-radius: 12px;
                    padding: 3px 10px;
                    border: 1px solid #ff5252;
                }
            """)
            layout_top_label.addWidget(response_label)


        #设置伸缩
        layout_top_label.addStretch()

        layout_text.addLayout(layout_top_label)
        #内容
        content=data.get(LogConstants.AUTOMATIC_THOUGHT_KEY, "")
        if len(content) > LogConstants.CONTENT_PREVIEW_LENGTH:
            content = content[:LogConstants.CONTENT_PREVIEW_LENGTH] + "..."
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
        layout_text.setStretchFactor(layout_top_label, 1)
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
        # 初始化编辑窗口为None，同时只允许一个编辑窗口存在
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
        if not os.path.exists(LogConstants.LOG_FILE_PATH):
            with open(LogConstants.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        #处理空文件
        if os.path.getsize(LogConstants.LOG_FILE_PATH) <= 0:
            self.logs = []
            return
        try:
            with open(LogConstants.LOG_FILE_PATH, 'r', encoding='utf-8') as f:
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

    def save_log_data(self):
        """点击删除后将日志数据写入文件"""
        try:
            with open(LogConstants.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, ensure_ascii=False,indent=4)
        except Exception as e:
            QMessageBox.warning(self, "提示", f"保存日志数据失败：{e}")

    def insert_log_in_order(self, log: Dict[str, Any]) -> None:
        """
        按规则插入日志：未回应日志排在已回应日志前面，每组内部按时间升序排列
        
        Args:
            log: 要插入的日志字典，包含timestamp和data字段
        """
        if not self._is_valid_log(log):
            return
            
        # 分离已回应和未回应的日志
        unresponded_logs, responded_logs = self._separate_logs_by_response_status()
        
        # 根据新日志的回应状态插入到对应列表
        if self._has_rational_response(log):
            self._insert_log_sorted(responded_logs, log)
        else:
            self._insert_log_sorted(unresponded_logs, log)
        
        # 合并两部分日志
        self.logs = unresponded_logs + responded_logs
    
    def _is_valid_log(self, log: Dict[str, Any]) -> bool:
        """验证日志格式是否正确"""
        if not isinstance(log, dict):
            return False
        if "timestamp" not in log or "data" not in log:
            return False
        if not isinstance(log.get("data"), dict):
            return False
        return True
    
    def _has_rational_response(self, log: Dict[str, Any]) -> bool:
        """检查日志是否有理性回应"""
        rational_response = log.get("data", {}).get(LogConstants.RATIONAL_RESPONSE_KEY, "")
        return bool(rational_response and rational_response.strip())
    
    def _separate_logs_by_response_status(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """将日志列表分离为已回应和未回应两部分"""
        unresponded_logs = []
        responded_logs = []
        
        for log in self.logs:
            if self._has_rational_response(log):
                responded_logs.append(log)
            else:
                unresponded_logs.append(log)
        
        return unresponded_logs, responded_logs
    
    def _insert_log_sorted(self, log_list: List[Dict[str, Any]], new_log: Dict[str, Any]) -> None:
        """
        将新日志按时间戳升序插入到指定列表中
        
        Args:
            log_list: 目标日志列表
            new_log: 要插入的新日志
        """
        new_timestamp = new_log.get("timestamp", 0)
        
        # 使用二分查找优化插入位置
        insert_position = self._find_insert_position(log_list, new_timestamp)
        log_list.insert(insert_position, new_log)
    
    def _find_insert_position(self, log_list: List[Dict[str, Any]], timestamp: float) -> int:
        """
        使用二分查找找到插入位置，保持时间戳升序
        
        Args:
            log_list: 日志列表
            timestamp: 要插入的时间戳
            
        Returns:
            插入位置的索引
        """
        if not log_list:
            return 0
            
        left, right = 0, len(log_list)
        
        while left < right:
            mid = (left + right) // 2
            mid_timestamp = log_list[mid].get("timestamp", 0)
            
            if timestamp < mid_timestamp:
                right = mid
            else:
                left = mid + 1
        
        return left
        
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
    
        if self.timestamp!=0:#如果打开的是创建过的日志
            # 使用列表推导式找到匹配的日志
            matching_logs = [log for log in self.logs if log.get("timestamp") == self.timestamp]
            if matching_logs:
                matching_log = matching_logs[0]
                pre_response = matching_log.get("data").get(LogConstants.RATIONAL_RESPONSE_KEY, "")

            matching_log["data"]=data

            #如果回应状态改变，需要将日志插入到改变后状态对应的列表中并保持时间升序
            if pre_response!=rational_response:
                #删除原日志
                self.logs.remove(matching_log)
                #插入新日志
                self.insert_log_in_order(matching_log)
        
        else:#新日志
            timestamp=time.time()
            temp_dict = {
                "type": LogConstants.THREE_COLUMN_TYPE,
                "timestamp":timestamp,
                "data": data
            }
            self.insert_log_in_order(temp_dict)

        with open(LogConstants.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False,indent=4)
        dlg=QDialog(self.edit_window)
        ui=Ui_DialogInfo()
        ui.setupUi(dlg)
        ui.label_text.setText("保存成功")
        ok_button=ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("确定")
        dlg.exec()
        #更新日志卡片列表
        self.update_log_card_list()

        #重置时间戳
        self.timestamp=0

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

        if self.timestamp!=0:#如果打开的是创建过的日志
            # 使用列表推导式找到匹配的日志
            matching_logs = [log for log in self.logs if log.get("timestamp") == self.timestamp]
            if matching_logs:
                matching_log = matching_logs[0]
                pre_response = matching_log.get("data").get(LogConstants.RATIONAL_RESPONSE_KEY, "")

            matching_log["data"]=data

            #如果回应状态改变，需要将日志插入到改变后状态对应的列表中并保持时间升序
            if pre_response!=rational_response:
                #删除原日志
                self.logs.remove(matching_log)
                #插入新日志
                self.insert_log_in_order(matching_log)

        else:#新日志
            timestamp=time.time()
            temp_dict = {
                "type": LogConstants.SIX_COLUMN_TYPE,
                "timestamp":timestamp,
                "data": data
            }
            self.insert_log_in_order(temp_dict)
        
        #保存日志到文件
        with open(LogConstants.LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=4)
        dlg=QDialog(self.edit_window)
        ui=Ui_DialogInfo()
        ui.setupUi(dlg)
        ui.label_text.setText("保存成功")
        dlg.exec()
        self.update_log_card_list()
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

