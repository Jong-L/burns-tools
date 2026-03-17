from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, List, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
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

    DATA_FILE = os.path.join("data", "每日活动计划表.json")
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

    def __init__(self, main_window: Any | None = None) -> None:
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("每日活动计划表")
        self.resize(960, 640)

        self.current_date_str: Optional[str] = None
        self.plan_data: dict[str, List[dict[str, Any]]] = {}
        self._setup_ui()
        self._ensure_storage_file()
        self._load_storage()
        self._load_day(self.date_edit.date())

    # --------------------------- UI 构建 --------------------------- #
    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)

        date_label = QLabel("选择日期：")
        date_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        toolbar_layout.addWidget(date_label)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.dateChanged.connect(self._on_date_changed)
        toolbar_layout.addWidget(self.date_edit)

        toolbar_layout.addStretch()

        self.reset_button = QPushButton("清空当日内容")
        self.reset_button.clicked.connect(self._reset_current_day)
        toolbar_layout.addWidget(self.reset_button)

        self.save_button = QPushButton("保存当前日")
        self.save_button.clicked.connect(lambda: self._save_current_day(show_message=True))
        toolbar_layout.addWidget(self.save_button)

        main_layout.addLayout(toolbar_layout)

        # 表格
        self.table = QTableWidget(len(self.TIME_SLOTS), 5, self)
        self.table.setHorizontalHeaderLabels(
            ["时间段", "计划活动", "实际活动", "掌控型分数 (M)", "休闲活动分数 (P)"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)

        # 说明标签
        info_label = QLabel(
            "提示：每天早晨填写左侧列为计划活动，晚上回顾实际活动并为掌控型/休闲活动打分（0-5分，数字越大表示满意度越高）。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555555; font-size: 12px;")
        main_layout.addWidget(info_label)

    # -------------------------- 数据处理 --------------------------- #
    def _ensure_storage_file(self) -> None:
        os.makedirs(os.path.dirname(self.DATA_FILE), exist_ok=True)
        if not os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def _load_storage(self) -> None:
        if os.path.getsize(self.DATA_FILE) == 0:
            self.plan_data = {}
            return
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.plan_data = data
            else:
                self.plan_data = {}
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.warning(self, "提示", f"加载活动计划数据失败：{exc}")
            self.plan_data = {}

    def _load_day(self, date: QDate) -> None:
        self.current_date_str = date.toString("yyyy-MM-dd")
        entries_data = self.plan_data.get(self.current_date_str, [])
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

        self.plan_data[self.current_date_str] = entries
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.plan_data, f, ensure_ascii=False, indent=4)
        except OSError as exc:
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

    def _reset_current_day(self) -> None:
        entries = [ActivityEntry(time_slot=slot) for slot in self.TIME_SLOTS]
        self._populate_table(entries)

    # -------------------------- Qt 生命周期 ----------------------- #
    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_day(show_message=False)
        if self.main_window and hasattr(self.main_window, "close_tool"):
            self.main_window.close_tool("每日活动计划表")
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = DailyActivityPlanWindow()
    window.show()
    sys.exit(app.exec())

