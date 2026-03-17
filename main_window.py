from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent, QShowEvent
from PySide6.QtWidgets import QMainWindow, QWidget

from components.tool_card import ToolCard
from main_window_design import Ui_MainWindow
from services.local_store import LocalStore
from services.tool_registry import TOOL_MAP, load_tool_definitions


class MainWindow(QMainWindow, Ui_MainWindow):
    CARD_MIN_WIDTH = 300
    CARD_HORIZONTAL_SPACING = 16

    def __init__(self):
        super(MainWindow, self).__init__()
        self.storage = LocalStore()
        self.tool_windows: dict[str, QWidget] = {}
        self.tool_cards: list[ToolCard] = []
        self.tool_configs = load_tool_definitions()
        self.current_columns = 0

        self.setupUi(self)
        self.setGeometry(280, 50, 1020, 760)
        self._apply_styles()
        self.load_tools()

    def _apply_styles(self) -> None:
        self.centralwidget.setObjectName("mainCentralWidget")
        self.scrollAreaWidgetContents.setObjectName("toolGridContainer")

        self.label.setText("\u4f2f\u6069\u65af\u60c5\u7eea\u5de5\u5177\u96c6")
        self.label_2.setText("\u9009\u62e9\u4e00\u4e2a\u5de5\u5177\uff0c\u5f00\u59cb\u4eca\u5929\u7684\u81ea\u52a9\u7ec3\u4e60")

        self.setStyleSheet(
            """
            QWidget#mainCentralWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #eef4ee,
                    stop: 0.45 #f6f5ef,
                    stop: 1 #e6efe7
                );
                font-family: "Microsoft YaHei";
                color: #24362a;
            }
            QLabel#label {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5ba76c,
                    stop: 1 #408f57
                );
                color: white;
                border-radius: 22px;
                padding: 18px 22px;
                font-size: 28px;
                font-weight: 700;
                margin: 6px 12px 0 12px;
            }
            QLabel#label_2 {
                color: #667c69;
                font-size: 13px;
                background-color: rgba(255, 255, 255, 0.7);
                border: 1px solid #dbe8d7;
                border-radius: 14px;
                padding: 10px 16px;
                margin: 0 24px 4px 24px;
            }
            QScrollArea#scrollArea {
                border: none;
                background: transparent;
            }
            QWidget#toolGridContainer {
                background-color: rgba(255, 255, 255, 0.72);
                border: 1px solid #d9e6d5;
                border-radius: 22px;
            }
            QScrollBar:vertical {
                width: 12px;
                border: none;
                background: transparent;
                margin: 8px 4px 8px 0;
            }
            QScrollBar::handle:vertical {
                min-height: 28px;
                border-radius: 6px;
                background: rgba(110, 156, 116, 0.6);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    def load_tools(self) -> None:
        """加载工具卡片。"""
        self.gridLayout.setHorizontalSpacing(self.CARD_HORIZONTAL_SPACING)
        self.gridLayout.setVerticalSpacing(self.CARD_HORIZONTAL_SPACING)

        for tool in self.tool_configs:
            tool_card = ToolCard(tool.tool_id, tool.name, tool.description)
            tool_card.clicked.connect(self.open_tool)
            tool_card.setCursor(Qt.PointingHandCursor)
            self.tool_cards.append(tool_card)

        self._relayout_tool_cards()

    def _relayout_tool_cards(self) -> None:
        columns = self._calculate_column_count()
        if columns == self.current_columns and self.gridLayout.count() == len(self.tool_cards):
            return

        self.current_columns = columns

        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self.scrollAreaWidgetContents)

        for index, tool_card in enumerate(self.tool_cards):
            row = index // columns
            column = index % columns
            self.gridLayout.addWidget(tool_card, row, column)

        for column in range(columns):
            self.gridLayout.setColumnStretch(column, 1)

    def _calculate_column_count(self) -> int:
        available_width = max(1, self.scrollArea.viewport().width())
        card_full_width = self.CARD_MIN_WIDTH + self.CARD_HORIZONTAL_SPACING
        columns = max(1, (available_width + self.CARD_HORIZONTAL_SPACING) // card_full_width)
        return min(columns, max(1, len(self.tool_cards)))

    def open_tool(self, tool_id: str) -> None:
        existing_window = self.tool_windows.get(tool_id)
        if existing_window is not None:
            existing_window.showNormal()
            existing_window.raise_()
            existing_window.activateWindow()
            return

        tool = TOOL_MAP.get(tool_id)
        if tool is None:
            return

        window = tool.factory(self)
        self.tool_windows[tool_id] = window
        window.destroyed.connect(lambda _=None, name=tool_id: self.close_tool(name))
        window.show()

    def close_tool(self, tool_id: str) -> None:
        self.tool_windows.pop(tool_id, None)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._relayout_tool_cards()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._relayout_tool_cards()
