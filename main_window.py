import json
import sys
#将需要导入的模块的路径添加到sys.path中
sys.path.append("components")
sys.path.append("tools")

from PySide6.QtWidgets import (QMainWindow, QApplication)
from PySide6.QtCore import Qt

from main_window_design import Ui_MainWindow
from components.tool_card import ToolCard
from tools.thought_count import ThoughtCounterWindow
from tools.thought_journal import ThoughtJournalWindow
from tools.daily_activity_plan import DailyActivityPlanWindow

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tool_windows=set()#保存已经打开的工具窗口
        self.setupUi(self)
        self.setGeometry(280, 50, 1020, 760)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.daily_plan_window=None
        self.load_tools()

    # 加载工具
    def load_tools(self):
        """ 加载工具 """
        try:
            with open("data/tools.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            tools = data["tools"]
            for i,tool in enumerate(tools):
                tool_card = ToolCard(tool["name"], tool["description"])
                tool_card.clicked.connect(self.open_tool)
                tool_card.setCursor(Qt.PointingHandCursor)
                row = i // 4
                column = i % 4
                self.gridLayout.addWidget(tool_card, row, column)

        except FileNotFoundError:
            print("tools.json not found")

    # 打开工具窗口
    def open_tool(self,tool_name):
        print("Opening tool..."+tool_name)
        if tool_name =="消极思维日志":
            if tool_name not in self.tool_windows:
                self.tool_windows.add(tool_name)
                self.journal_window = ThoughtJournalWindow(main_window=self)
                #self.journal_window.destroyed.connect(lambda: self.close_tool(tool_name))#使用lambda表达式传递参数
                self.journal_window.show()
            else:
                #将窗口置于顶层
                self.journal_window.activateWindow()
        elif tool_name =="消极思维计数器":
            if tool_name not in self.tool_windows:
                self.tool_windows.add(tool_name)
                self.counter_window = ThoughtCounterWindow(main_window=self)
                self.counter_window.show()
            else:
                #将窗口置于顶层
                self.counter_window.activateWindow()
        elif tool_name =="每日活动计划表":
            if tool_name not in self.tool_windows:
                self.tool_windows.add(tool_name)
                self.daily_plan_window = DailyActivityPlanWindow(main_window=self)
                self.daily_plan_window.show()
            else:
                self.daily_plan_window.activateWindow()

    def close_tool(self,tool_name):
        self.tool_windows.discard(tool_name)
        print("Closed tool..."+tool_name)
        if tool_name=="消极思维日志":
            self.journal_window = None
        elif tool_name=="每日活动计划表":
            self.daily_plan_window = None
if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    app.exec()
