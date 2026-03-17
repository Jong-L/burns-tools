from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
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
    QHeaderView,
)

from services.local_store import LocalStore
from tools.dlg_calendar import CalendarDialog


@dataclass
class AntiProcrastinationEntry:
    activity: str = ""
    predicted_difficulty: Optional[int] = None
    predicted_satisfaction: Optional[int] = None
    actual_difficulty: Optional[int] = None
    actual_satisfaction: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AntiProcrastinationEntry":
        return cls(
            activity=str(data.get("activity", "")).strip(),
            predicted_difficulty=cls._safe_percent(data.get("predicted_difficulty")),
            predicted_satisfaction=cls._safe_percent(data.get("predicted_satisfaction")),
            actual_difficulty=cls._safe_percent(data.get("actual_difficulty")),
            actual_satisfaction=cls._safe_percent(data.get("actual_satisfaction")),
        )

    @staticmethod
    def _safe_percent(value: Any) -> Optional[int]:
        if value in (None, ""):
            return None
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if 0 <= number <= 100 else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "activity": self.activity,
            "predicted_difficulty": self.predicted_difficulty,
            "predicted_satisfaction": self.predicted_satisfaction,
            "actual_difficulty": self.actual_difficulty,
            "actual_satisfaction": self.actual_satisfaction,
        }


class AntiProcrastinationTableWindow(QWidget):
    COLUMN_LABELS = [
        "日期",
        "活动\n（请将每项任务分解成几个小步骤）",
        "预计难度\n（0-100%）",
        "预计的\n满足程度\n（0-100%）",
        "实际难度\n（0-100%）",
        "实际的\n满足程度\n（0-100%）",
    ]

    def __init__(self, main_window: Any | None = None, storage: LocalStore | None = None) -> None:
        super().__init__()
        self.main_window = main_window
        self.storage = storage or LocalStore()
        self.current_date_str: Optional[str] = None
        self.setWindowTitle("反拖延症表")
        self.resize(1080, 760)
        self.setObjectName("antiProcrastinationWindow")

        self._setup_ui()
        self._apply_styles()
        self._load_day(self.date_edit.date())

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(22, 18, 22, 18)
        main_layout.setSpacing(14)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(22, 16, 22, 16)
        hero_layout.setSpacing(6)

        eyebrow = QLabel("Table 5-3")
        eyebrow.setObjectName("heroEyebrow")
        hero_layout.addWidget(eyebrow)

        title = QLabel("反拖延症表")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)

        intro = QLabel(
            "把一个让你迟迟不想开始的任务拆成几个小步骤。开始前先写下你预计的难度和满足程度，完成后再记录真实体验。"
        )
        intro.setObjectName("heroIntro")
        intro.setWordWrap(True)
        hero_layout.addWidget(intro)

        hint = QLabel("很多任务并没有想象中那么难，而完成后的满足感常常比预期更高。")
        hint.setObjectName("heroHint")
        hint.setWordWrap(True)
        hero_layout.addWidget(hint)

        main_layout.addWidget(hero_card)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("toolbarCard")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(18, 12, 18, 12)
        toolbar_layout.setSpacing(12)

        date_label = QLabel("记录日期：")
        date_label.setObjectName("fieldLabel")
        toolbar_layout.addWidget(date_label)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setObjectName("dateEdit")
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self._on_date_changed)
        toolbar_layout.addWidget(self.date_edit)

        self.calendar_button = QPushButton("日历")
        self.calendar_button.setObjectName("calendarButton")
        self.calendar_button.clicked.connect(self._open_calendar_dialog)
        toolbar_layout.addWidget(self.calendar_button)

        toolbar_hint = QLabel("建议每次只填一个任务，并把它拆成足够小、足够具体的步骤。")
        toolbar_hint.setObjectName("toolbarHint")
        toolbar_hint.setWordWrap(True)
        toolbar_layout.addWidget(toolbar_hint)

        toolbar_layout.addStretch()

        self.add_row_button = QPushButton("添加步骤")
        self.add_row_button.setObjectName("secondaryButton")
        self.add_row_button.clicked.connect(self._add_row)
        toolbar_layout.addWidget(self.add_row_button)

        self.delete_row_button = QPushButton("删除选中")
        self.delete_row_button.setObjectName("secondaryButton")
        self.delete_row_button.clicked.connect(self._delete_selected_row)
        toolbar_layout.addWidget(self.delete_row_button)

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(lambda: self._save_current_day(show_message=True))
        toolbar_layout.addWidget(self.save_button)

        main_layout.addWidget(toolbar_card)

        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 16, 18, 16)
        summary_layout.setSpacing(10)

        summary_title = QLabel("预期与实际摘要")
        summary_title.setObjectName("sectionTitle")
        summary_layout.addWidget(summary_title)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.predicted_difficulty_metric = self._create_metric_card("平均预计难度", "0%")
        self.actual_difficulty_metric = self._create_metric_card("平均实际难度", "0%")
        self.predicted_satisfaction_metric = self._create_metric_card("平均预计满足", "0%")
        self.actual_satisfaction_metric = self._create_metric_card("平均实际满足", "0%")

        metrics_layout.addWidget(self.predicted_difficulty_metric)
        metrics_layout.addWidget(self.actual_difficulty_metric)
        metrics_layout.addWidget(self.predicted_satisfaction_metric)
        metrics_layout.addWidget(self.actual_satisfaction_metric)

        summary_layout.addLayout(metrics_layout)

        self.summary_insight_label = QLabel("开始记录后，这里会自动告诉你：任务是否真的像想象中那样困难。")
        self.summary_insight_label.setObjectName("summaryInsight")
        self.summary_insight_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_insight_label)

        main_layout.addWidget(summary_card)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(18, 18, 18, 16)
        table_layout.setSpacing(12)

        section_title = QLabel("任务拆解与预期校正")
        section_title.setObjectName("sectionTitle")
        table_layout.addWidget(section_title)

        self.table = QTableWidget(0, len(self.COLUMN_LABELS), self)
        self.table.setObjectName("antiTable")
        self.table.setHorizontalHeaderLabels(self.COLUMN_LABELS)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.itemChanged.connect(self._refresh_summary)
        table_layout.addWidget(self.table)

        footnote = QLabel("百分比字段可留空，或填写 0 到 100 的整数。")
        footnote.setObjectName("infoLabel")
        table_layout.addWidget(footnote)

        main_layout.addWidget(table_card)

    def _create_metric_card(self, title: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("metricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("metricTitle")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        layout.addWidget(value_label)
        card.value_label = value_label  # type: ignore[attr-defined]
        return card

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#antiProcrastinationWindow {
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
                    stop: 0 #5ba76c,
                    stop: 1 #408f57
                );
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 18px;
            }
            QLabel#heroEyebrow {
                color: rgba(245, 255, 245, 0.78);
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QLabel#heroTitle {
                color: white;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#heroIntro, QLabel#heroHint {
                color: rgba(246, 255, 246, 0.92);
                font-size: 12px;
                line-height: 1.5;
            }
            QFrame#toolbarCard, QFrame#tableCard, QFrame#summaryCard {
                background-color: rgba(255, 255, 255, 0.86);
                border: 1px solid #d8e6d4;
                border-radius: 18px;
            }
            QFrame#metricCard {
                background-color: #f7fbf5;
                border: 1px solid #dbe8d7;
                border-radius: 14px;
            }
            QLabel#fieldLabel {
                color: #42634a;
                font-size: 13px;
                font-weight: 600;
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
            QLabel#metricTitle {
                color: #708271;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#metricValue {
                color: #4f9c61;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#summaryInsight {
                color: #4d6452;
                font-size: 12px;
                background-color: #f5faf3;
                border: 1px solid #dde9d9;
                border-radius: 12px;
                padding: 10px 12px;
            }
            QLabel#infoLabel {
                color: #657b68;
                font-size: 12px;
            }
            QDateEdit#dateEdit {
                min-width: 140px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #b7d0b2;
                background-color: #f7fbf5;
                color: #274030;
            }
            QPushButton#calendarButton, QPushButton#secondaryButton, QPushButton#primaryButton {
                min-height: 40px;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#calendarButton, QPushButton#secondaryButton {
                background-color: #edf5ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
            }
            QPushButton#calendarButton:hover, QPushButton#secondaryButton:hover {
                background-color: #e5efe0;
            }
            QPushButton#primaryButton {
                background-color: #4f9c61;
                color: white;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background-color: #458c56;
            }
            QTableWidget#antiTable {
                border: 1px solid #c7d8c2;
                border-radius: 14px;
                background-color: rgba(252, 252, 249, 0.96);
                alternate-background-color: #f2f6ef;
                gridline-color: #cfe0ca;
                color: #28412f;
                selection-background-color: rgba(102, 163, 112, 0.22);
                selection-color: #1f3024;
            }
            QTableWidget#antiTable::item {
                padding: 12px 10px;
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
            """
        )

    def _load_day(self, date: QDate) -> None:
        self.current_date_str = date.toString("yyyy-MM-dd")
        try:
            entries_data = self.storage.get_anti_procrastination_entries(self.current_date_str)
        except Exception as exc:
            QMessageBox.warning(self, "提示", f"加载反拖延症表失败：{exc}")
            entries_data = []
        entries = [AntiProcrastinationEntry.from_dict(item) for item in entries_data]
        if not entries:
            entries = [AntiProcrastinationEntry()]
        self._populate_table(entries)
        self._refresh_summary()

    def _populate_table(self, entries: list[AntiProcrastinationEntry]) -> None:
        self.table.blockSignals(True)
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self._set_text_item(row, 0, self.current_date_str or "", editable=False, centered=True)
            self._set_text_item(row, 1, entry.activity)
            self._set_text_item(row, 2, self._format_percent(entry.predicted_difficulty), centered=True)
            self._set_text_item(row, 3, self._format_percent(entry.predicted_satisfaction), centered=True)
            self._set_text_item(row, 4, self._format_percent(entry.actual_difficulty), centered=True)
            self._set_text_item(row, 5, self._format_percent(entry.actual_satisfaction), centered=True)
        self.table.blockSignals(False)

    def _refresh_summary(self) -> None:
        try:
            entries = self._collect_entries()
        except ValueError:
            return

        predicted_difficulties = [entry["predicted_difficulty"] for entry in entries if entry["predicted_difficulty"] is not None]
        actual_difficulties = [entry["actual_difficulty"] for entry in entries if entry["actual_difficulty"] is not None]
        predicted_satisfactions = [entry["predicted_satisfaction"] for entry in entries if entry["predicted_satisfaction"] is not None]
        actual_satisfactions = [entry["actual_satisfaction"] for entry in entries if entry["actual_satisfaction"] is not None]

        predicted_diff_avg = self._average(predicted_difficulties)
        actual_diff_avg = self._average(actual_difficulties)
        predicted_sat_avg = self._average(predicted_satisfactions)
        actual_sat_avg = self._average(actual_satisfactions)

        self.predicted_difficulty_metric.value_label.setText(self._format_metric(predicted_diff_avg))  # type: ignore[attr-defined]
        self.actual_difficulty_metric.value_label.setText(self._format_metric(actual_diff_avg))  # type: ignore[attr-defined]
        self.predicted_satisfaction_metric.value_label.setText(self._format_metric(predicted_sat_avg))  # type: ignore[attr-defined]
        self.actual_satisfaction_metric.value_label.setText(self._format_metric(actual_sat_avg))  # type: ignore[attr-defined]

        self.summary_insight_label.setText(
            self._build_summary_insight(
                predicted_diff_avg=predicted_diff_avg,
                actual_diff_avg=actual_diff_avg,
                predicted_sat_avg=predicted_sat_avg,
                actual_sat_avg=actual_sat_avg,
                entry_count=len(entries),
            )
        )

    @staticmethod
    def _average(values: list[int]) -> Optional[float]:
        if not values:
            return None
        return sum(values) / len(values)

    @staticmethod
    def _format_metric(value: Optional[float]) -> str:
        if value is None:
            return "--"
        return f"{round(value):.0f}%"

    def _build_summary_insight(
        self,
        predicted_diff_avg: Optional[float],
        actual_diff_avg: Optional[float],
        predicted_sat_avg: Optional[float],
        actual_sat_avg: Optional[float],
        entry_count: int,
    ) -> str:
        if entry_count == 0:
            return "开始记录后，这里会自动告诉你：任务是否真的像想象中那样困难。"

        messages: list[str] = [f"今天共记录了 {entry_count} 个步骤。"]

        if predicted_diff_avg is not None and actual_diff_avg is not None:
            diff_gap = actual_diff_avg - predicted_diff_avg
            if diff_gap <= -10:
                messages.append("整体来看，实际难度明显低于预期，你可能把任务想得比真实体验更难。")
            elif diff_gap >= 10:
                messages.append("整体来看，实际难度高于预期，下一次可以把步骤拆得更小一些。")
            else:
                messages.append("整体来看，实际难度和预期接近，你对任务的判断已经比较稳定。")

        if predicted_sat_avg is not None and actual_sat_avg is not None:
            sat_gap = actual_sat_avg - predicted_sat_avg
            if sat_gap >= 10:
                messages.append("完成后的满足感高于预期，行动本身很可能比拖延更让你轻松。")
            elif sat_gap <= -10:
                messages.append("完成后的满足感低于预期，也许需要调整任务形式或奖励方式。")
            else:
                messages.append("完成后的满足感和预期接近，可以继续保持这种节奏。")

        return " ".join(messages)

    def _set_text_item(self, row: int, column: int, text: str, editable: bool = True, centered: bool = False) -> None:
        item = QTableWidgetItem(text)
        if not editable:
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        if centered:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, column, item)

    def _format_percent(self, value: Optional[int]) -> str:
        return "" if value is None else str(value)

    def _collect_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for row in range(self.table.rowCount()):
            activity = self._get_item_text(row, 1)
            predicted_difficulty = self._validate_percent(row, 2, "预计难度")
            predicted_satisfaction = self._validate_percent(row, 3, "预计满足程度")
            actual_difficulty = self._validate_percent(row, 4, "实际难度")
            actual_satisfaction = self._validate_percent(row, 5, "实际满足程度")
            if not activity and all(
                value is None
                for value in (
                    predicted_difficulty,
                    predicted_satisfaction,
                    actual_difficulty,
                    actual_satisfaction,
                )
            ):
                continue
            entries.append(
                AntiProcrastinationEntry(
                    activity=activity,
                    predicted_difficulty=predicted_difficulty,
                    predicted_satisfaction=predicted_satisfaction,
                    actual_difficulty=actual_difficulty,
                    actual_satisfaction=actual_satisfaction,
                ).to_dict()
            )
        return entries

    def _get_item_text(self, row: int, column: int) -> str:
        item = self.table.item(row, column)
        return item.text().strip() if item is not None else ""

    def _validate_percent(self, row: int, column: int, label: str) -> Optional[int]:
        text = self._get_item_text(row, column)
        if text == "":
            return None
        if text.isdigit():
            value = int(text)
            if 0 <= value <= 100:
                return value
        raise ValueError(f"第 {row + 1} 行的{label}必须是 0 到 100 的整数或留空。")

    def _save_current_day(self, show_message: bool) -> bool:
        if self.current_date_str is None:
            return False
        try:
            entries = self._collect_entries()
            self.storage.save_anti_procrastination_entries(self.current_date_str, entries)
        except ValueError as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return False
        except Exception as exc:
            QMessageBox.critical(self, "错误", f"保存反拖延症表失败：{exc}")
            return False

        if show_message:
            QMessageBox.information(self, "提示", "保存成功")
        return True

    def _on_date_changed(self, new_date: QDate) -> None:
        if self.current_date_str is not None:
            previous_date = QDate.fromString(self.current_date_str, "yyyy-MM-dd")
            if not self._save_current_day(show_message=False):
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

    def _add_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._set_text_item(row, 0, self.current_date_str or "", editable=False, centered=True)
        for column in range(1, self.table.columnCount()):
            self._set_text_item(row, column, "", centered=column >= 2)
        self._refresh_summary()

    def _delete_selected_row(self) -> None:
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选中一行。")
            return
        self.table.removeRow(current_row)
        if self.table.rowCount() == 0:
            self._add_row()
            return
        self._refresh_summary()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_day(show_message=False)
        if self.main_window and hasattr(self.main_window, "close_tool"):
            self.main_window.close_tool("anti_procrastination_table")
        super().closeEvent(event)
