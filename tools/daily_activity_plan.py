from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCalendarWidget,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QHeaderView

from services.local_store import LocalStore
from tools.dlg_calendar import CalendarDialog


@dataclass
class ActivityEntry:
    """单个时间段的活动数据"""

    time_slot: str
    plan: str = ""
    actual: str = ""
    mastery_score: Optional[int] = None
    pleasure_score: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivityEntry":
        return cls(
            time_slot=data.get("time_slot", ""),
            plan=data.get("plan", ""),
            actual=data.get("actual", ""),
            mastery_score=cls._safe_int(data.get("mastery_score")),
            pleasure_score=cls._safe_int(data.get("pleasure_score")),
        )

    @staticmethod
    def _safe_int(value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            num = int(value)
        except (TypeError, ValueError):
            return None
        if 0 <= num <= 5:
            return num
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_slot": self.time_slot,
            "plan": self.plan,
            "actual": self.actual,
            "mastery_score": self.mastery_score,
            "pleasure_score": self.pleasure_score,
        }


class DailyActivityPlanWindow(QWidget):
    """每日活动计划表工具窗口"""
    TIME_SLOTS: List[str] = [
        "上午 8-9",
        "上午 9-10",
        "上午 10-11",
        "上午 11-12",
        "下午 12-1",
        "下午 1-2",
        "下午 2-3",
        "下午 3-4",
        "下午 4-5",
        "下午 5-6",
        "下午 6-7",
        "晚上 7-8",
        "晚上 8-9",
        "晚上 9-12",
    ]

    def __init__(self, main_window: Any | None = None, storage: LocalStore | None = None) -> None:
        super().__init__()
        self.main_window = main_window
        self.storage = storage or LocalStore()
        self.setWindowTitle("每日活动计划表")
        self.resize(960, 640)
        self.setObjectName("dailyPlanWindow")

        self.current_date_str: Optional[str] = None
        self._setup_ui()
        self._apply_styles()
        self._load_day(self.date_edit.date())

    # --------------------------- UI 构建 --------------------------- #
    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 18, 22, 18)
        main_layout.setSpacing(14)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(20, 14, 20, 14)
        hero_layout.setSpacing(14)

        title_block = QVBoxLayout()
        title_block.setSpacing(2)

        hero_eyebrow = QLabel("Gentle Daily Reflection")
        hero_eyebrow.setObjectName("heroEyebrow")
        title_block.addWidget(hero_eyebrow)

        hero_title = QLabel("每日活动计划表")
        hero_title.setObjectName("heroTitle")
        title_block.addWidget(hero_title)
        hero_layout.addLayout(title_block)

        hero_subtitle = QLabel("早晨轻轻安排今天，晚上温和回看行动、掌控感与愉悦感。")
        hero_subtitle.setObjectName("heroSubtitle")
        hero_subtitle.setWordWrap(True)
        hero_layout.addWidget(hero_subtitle)
        hero_layout.setStretch(0, 2)
        hero_layout.setStretch(1, 3)

        main_layout.addWidget(hero_card)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("toolbarCard")
        toolbar_layout = QHBoxLayout()
        toolbar_card.setLayout(toolbar_layout)
        toolbar_layout.setContentsMargins(18, 12, 18, 12)
        toolbar_layout.setSpacing(12)

        date_label = QLabel("选择日期：")
        date_label.setObjectName("fieldLabel")
        date_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        toolbar_layout.addWidget(date_label)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setObjectName("dateEdit")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.calendar_widget = QCalendarWidget(self)
        self.calendar_widget.setObjectName("dateCalendar")
        self.date_edit.setCalendarWidget(self.calendar_widget)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        toolbar_layout.addWidget(self.date_edit)

        self.calendar_button = QPushButton("日历")
        self.calendar_button.setObjectName("calendarButton")
        self.calendar_button.setCursor(Qt.PointingHandCursor)
        self.calendar_button.clicked.connect(self._open_calendar_dialog)
        toolbar_layout.addWidget(self.calendar_button)

        toolbar_hint = QLabel("计划尽量写得具体而温和，评分只用来观察，不用追求完美。")
        toolbar_hint.setObjectName("toolbarHint")
        toolbar_hint.setWordWrap(True)
        toolbar_layout.addWidget(toolbar_hint)

        toolbar_layout.addStretch()

        self.reset_button = QPushButton("清空当日内容")
        self.reset_button.setObjectName("secondaryButton")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.clicked.connect(self._reset_current_day)
        toolbar_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("保存当前日")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(lambda: self._save_current_day(show_message=True))
        toolbar_layout.addWidget(self.save_button)

        main_layout.addWidget(toolbar_card)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(18, 18, 18, 16)
        table_layout.setSpacing(14)

        section_layout = QHBoxLayout()
        section_layout.setSpacing(10)

        section_title = QLabel("今日节律")
        section_title.setObjectName("sectionTitle")
        section_layout.addWidget(section_title)

        section_note = QLabel("计划列写“想做什么”，实际列写“真正做了什么”")
        section_note.setObjectName("sectionNote")
        section_layout.addWidget(section_note)
        section_layout.addStretch()

        table_layout.addLayout(section_layout)

        # 表格
        self.table = QTableWidget(len(self.TIME_SLOTS), 5, self)
        self.table.setObjectName("planTable")
        self.table.setHorizontalHeaderLabels(
            ["时间段", "计划活动", "实际活动", "掌控型分数 (M)", "休闲活动分数 (P)"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setShowGrid(True)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(52)
        table_layout.addWidget(self.table)

        # 说明标签
        info_label = QLabel(
            "提示：每天早晨填写左侧列为计划活动，晚上回顾实际活动并为掌控型/休闲活动打分（0-5分，数字越大表示满意度越高）。"
        )
        info_label.setObjectName("infoLabel")
        info_label.setWordWrap(True)
        table_layout.addWidget(info_label)

        main_layout.addWidget(table_card)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#dailyPlanWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #eef4ee,
                    stop: 0.45 #f6f5ef,
                    stop: 1 #e6efe7
                );
                color: #24362a;
                font-family: "Microsoft YaHei";
            }
            QFrame#heroCard {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5ca86d,
                    stop: 1 #3f8f57
                );
                border-radius: 18px;
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            QLabel#heroEyebrow {
                color: rgba(245, 255, 245, 0.78);
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QLabel#heroTitle {
                color: white;
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#heroSubtitle {
                color: rgba(245, 255, 245, 0.92);
                font-size: 12px;
                line-height: 1.5;
            }
            QFrame#toolbarCard, QFrame#tableCard {
                background-color: rgba(255, 255, 255, 0.84);
                border: 1px solid #d8e6d4;
                border-radius: 18px;
            }
            QLabel#fieldLabel {
                color: #42634a;
                font-size: 13px;
                font-weight: 600;
            }
            QDateEdit#dateEdit {
                min-width: 140px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #b7d0b2;
                background-color: #f7fbf5;
                color: #274030;
                selection-background-color: #6cab75;
            }
            QDateEdit#dateEdit::drop-down {
                border: none;
                width: 24px;
            }
            QCalendarWidget#dateCalendar {
                background-color: #f8fbf5;
                border: 1px solid #c6d8c1;
                border-radius: 14px;
            }
            QCalendarWidget#dateCalendar QWidget {
                alternate-background-color: #edf5ea;
            }
            QCalendarWidget QToolButton {
                color: #31523a;
                font-weight: 600;
                background: transparent;
                padding: 6px;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #28412f;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                color: #28412f;
                border: 1px solid #c7d8c2;
                border-radius: 8px;
                padding: 2px 6px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #2d4232;
                selection-background-color: #67ab72;
                selection-color: white;
                background-color: #fcfdfb;
            }
            QPushButton#primaryButton, QPushButton#secondaryButton, QPushButton#calendarButton {
                padding: 9px 18px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 600;
                border: none;
            }
            QPushButton#primaryButton {
                background-color: #4f9c61;
                color: white;
            }
            QPushButton#primaryButton:hover {
                background-color: #458c56;
            }
            QPushButton#primaryButton:pressed {
                background-color: #3a7648;
            }
            QPushButton#secondaryButton {
                background-color: #eef5ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
            }
            QPushButton#secondaryButton:hover {
                background-color: #e5efe0;
            }
            QPushButton#calendarButton {
                background-color: #edf4ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
                padding-left: 14px;
                padding-right: 14px;
            }
            QPushButton#calendarButton:hover {
                background-color: #e2eedf;
            }
            QLabel#toolbarHint {
                color: #758878;
                font-size: 12px;
            }
            QLabel#sectionTitle {
                color: #32543b;
                font-size: 17px;
                font-weight: 700;
            }
            QLabel#sectionNote {
                color: #748777;
                font-size: 12px;
            }
            QTableWidget#planTable {
                border: 1px solid #c7d8c2;
                border-radius: 14px;
                background-color: rgba(252, 252, 249, 0.96);
                alternate-background-color: #f2f6ef;
                gridline-color: #cfe0ca;
                color: #28412f;
                selection-background-color: rgba(102, 163, 112, 0.22);
                selection-color: #1f3024;
                outline: 0;
            }
            QTableWidget#planTable::item {
                padding: 12px 10px;
                border: none;
            }
            QTableWidget#planTable::item:selected {
                border: 1px solid rgba(90, 145, 100, 0.28);
            }
            QHeaderView::section {
                background-color: #4caf5a;
                color: white;
                font-size: 13px;
                font-weight: 700;
                padding: 12px 10px;
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 0.18);
                border-bottom: 1px solid #41964d;
            }
            QTableCornerButton::section {
                background-color: #4caf5a;
                border: none;
                border-bottom: 1px solid #41964d;
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
            QLabel#infoLabel {
                color: #657b68;
                font-size: 12px;
                padding: 4px 2px 0 2px;
            }
            """
        )

    # -------------------------- 数据处理 --------------------------- #
    def _load_day(self, date: QDate) -> None:
        self.current_date_str = date.toString("yyyy-MM-dd")
        try:
            entries_data = self.storage.get_daily_plan(self.current_date_str)
        except Exception as exc:
            QMessageBox.warning(self, "提示", f"加载活动计划数据失败：{exc}")
            entries_data = []
        if not entries_data:
            entries = [ActivityEntry(time_slot=slot) for slot in self.TIME_SLOTS]
        else:
            entries = []
            for slot in self.TIME_SLOTS:
                matched = next(
                    (ActivityEntry.from_dict(item) for item in entries_data if item.get("time_slot") == slot),
                    None,
                )
                entries.append(matched if matched is not None else ActivityEntry(time_slot=slot))
        self._populate_table(entries)

    def _populate_table(self, entries: List[ActivityEntry]) -> None:
        self.table.blockSignals(True)
        for row, entry in enumerate(entries):
            time_item = QTableWidgetItem(entry.time_slot)
            time_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, time_item)

            plan_item = QTableWidgetItem(entry.plan)
            self.table.setItem(row, 1, plan_item)

            actual_item = QTableWidgetItem(entry.actual)
            self.table.setItem(row, 2, actual_item)

            mastery_item = QTableWidgetItem("" if entry.mastery_score is None else str(entry.mastery_score))
            mastery_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, mastery_item)

            pleasure_item = QTableWidgetItem("" if entry.pleasure_score is None else str(entry.pleasure_score))
            pleasure_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, pleasure_item)
        self.table.blockSignals(False)

    def _collect_entries(self) -> List[dict[str, Any]]:
        if self.current_date_str is None:
            return []

        collected: List[dict[str, Any]] = []
        for row, slot in enumerate(self.TIME_SLOTS):
            plan = self._get_item_text(row, 1)
            actual = self._get_item_text(row, 2)
            mastery_score = self._validate_score(row, 3, "掌控型分数")
            pleasure_score = self._validate_score(row, 4, "休闲活动分数")
            collected.append(
                ActivityEntry(
                    time_slot=slot,
                    plan=plan,
                    actual=actual,
                    mastery_score=mastery_score,
                    pleasure_score=pleasure_score,
                ).to_dict()
            )
        return collected

    def _get_item_text(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return item.text().strip() if item is not None else ""

    def _validate_score(self, row: int, column: int, label: str) -> Optional[int]:
        text = self._get_item_text(row, column)
        if text == "":
            return None
        if text.isdigit():
            value = int(text)
            if 0 <= value <= 5:
                return value
        raise ValueError(f"{self.TIME_SLOTS[row]} 的{label}必须是0到5之间的整数或留空。")

    def _save_current_day(self, show_message: bool) -> bool:
        if self.current_date_str is None:
            return False
        try:
            entries = self._collect_entries()
        except ValueError as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return False

        try:
            self.storage.save_daily_plan(self.current_date_str, entries)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "错误", f"保存数据失败：{exc}")
            return False

        if show_message:
            QMessageBox.information(self, "提示", "保存成功")
        return True

    # -------------------------- 事件处理 --------------------------- #
    def _on_date_changed(self, new_date: QDate) -> None:
        if self.current_date_str is not None:
            previous_date = QDate.fromString(self.current_date_str, "yyyy-MM-dd")
            if not self._save_current_day(show_message=False):
                # 恢复日期选择
                self.date_edit.blockSignals(True)
                self.date_edit.setDate(previous_date)
                self.date_edit.blockSignals(False)
                return
        self._load_day(new_date)

    def _open_calendar_dialog(self) -> None:
        dialog = CalendarDialog()
        dialog.calendarWidget.setSelectedDate(self.date_edit.date())
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.date_edit.setDate(dialog.calendarWidget.selectedDate())

    def _reset_current_day(self) -> None:
        entries = [ActivityEntry(time_slot=slot) for slot in self.TIME_SLOTS]
        self._populate_table(entries)

    # -------------------------- Qt 生命周期 ----------------------- #
    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_day(show_message=False)
        if self.main_window and hasattr(self.main_window, "close_tool"):
            self.main_window.close_tool("daily_activity_plan")
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = DailyActivityPlanWindow()
    window.show()
    sys.exit(app.exec())

