from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.local_store import LocalStore
from tools.dlg_calendar import CalendarDialog


@dataclass
class ButRebuttalEntry:
    excuse_text: str = ""
    rebuttal_text: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ButRebuttalEntry":
        return cls(
            excuse_text=str(data.get("excuse_text", "")).strip(),
            rebuttal_text=str(data.get("rebuttal_text", "")).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "excuse_text": self.excuse_text,
            "rebuttal_text": self.rebuttal_text,
        }


class ButRebuttalRow(QFrame):
    content_changed = Signal()

    def __init__(self, index: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.index = index
        self.setObjectName("rowCard")
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 14, 18, 14)
        outer_layout.setSpacing(8)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(18)

        left_title = QLabel("“但是”列")
        left_title.setObjectName("columnLabel")
        title_layout.addWidget(left_title)

        title_layout.addStretch()

        right_title = QLabel("“反驳‘但是’”列")
        right_title.setObjectName("columnLabel")
        title_layout.addWidget(right_title)
        outer_layout.addLayout(title_layout)

        self.incoming_arrow = QLabel("↙")
        self.incoming_arrow.setObjectName("incomingArrow")
        self.incoming_arrow.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.incoming_arrow.hide()
        outer_layout.addWidget(self.incoming_arrow)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        self.left_edit = QTextEdit()
        self.left_edit.setObjectName("leftEdit")
        self.left_edit.setPlaceholderText("把脑中冒出的“但是……”借口写在这里")
        self.left_edit.setFixedHeight(110)
        self.left_edit.textChanged.connect(self.content_changed.emit)
        content_layout.addWidget(self.left_edit, 5)

        self.bridge_arrow = QLabel("→")
        self.bridge_arrow.setObjectName("bridgeArrow")
        self.bridge_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bridge_arrow.hide()
        content_layout.addWidget(self.bridge_arrow, 1)

        self.right_edit = QTextEdit()
        self.right_edit.setObjectName("rightEdit")
        self.right_edit.setPlaceholderText("用更实际、更理性的论点反驳这个“但是”")
        self.right_edit.setFixedHeight(110)
        self.right_edit.textChanged.connect(self.content_changed.emit)
        content_layout.addWidget(self.right_edit, 5)

        outer_layout.addLayout(content_layout)

    def set_entry(self, entry: ButRebuttalEntry) -> None:
        self.left_edit.blockSignals(True)
        self.right_edit.blockSignals(True)
        self.left_edit.setPlainText(entry.excuse_text)
        self.right_edit.setPlainText(entry.rebuttal_text)
        self.left_edit.blockSignals(False)
        self.right_edit.blockSignals(False)

    def has_left_text(self) -> bool:
        return bool(self.left_edit.toPlainText().strip())

    def has_right_text(self) -> bool:
        return bool(self.right_edit.toPlainText().strip())

    def has_any_text(self) -> bool:
        return self.has_left_text() or self.has_right_text()

    def set_left_enabled(self, enabled: bool) -> None:
        self.left_edit.setEnabled(enabled)
        self.left_edit.setVisible(enabled or self.has_left_text())

    def set_right_enabled(self, enabled: bool) -> None:
        self.right_edit.setEnabled(enabled)
        self.right_edit.setVisible(enabled or self.has_right_text())

    def set_incoming_visible(self, visible: bool) -> None:
        self.incoming_arrow.setVisible(visible)

    def set_bridge_visible(self, visible: bool) -> None:
        self.bridge_arrow.setVisible(visible)

    def to_entry(self) -> ButRebuttalEntry:
        return ButRebuttalEntry(
            excuse_text=self.left_edit.toPlainText().strip(),
            rebuttal_text=self.right_edit.toPlainText().strip(),
        )


class ButRebuttalToolWindow(QWidget):
    def __init__(self, main_window: Any | None = None, storage: LocalStore | None = None) -> None:
        super().__init__()
        self.main_window = main_window
        self.storage = storage or LocalStore()
        self.current_date_str: Optional[str] = None
        self.rows: list[ButRebuttalRow] = []
        self._is_loading = False

        self.setWindowTitle("反驳“但是”法")
        self.resize(1100, 780)
        self.setObjectName("butRebuttalWindow")

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

        eyebrow = QLabel("Table 5-6")
        eyebrow.setObjectName("heroEyebrow")
        hero_layout.addWidget(eyebrow)

        title = QLabel("反驳“但是”法")
        title.setObjectName("heroTitle")
        hero_layout.addWidget(title)

        intro = QLabel("当脑中冒出“我应该去做，但是……”时，不要和它含糊拉扯，而是逐条写下更理性、更实际的反驳。")
        intro.setObjectName("heroIntro")
        intro.setWordWrap(True)
        hero_layout.addWidget(intro)

        hint = QLabel("填写方式是链式推进的：左边写完，箭头出现并解锁右边；右边写完，再解锁下一轮左边。")
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

        self.progress_label = QLabel("开始拆掉第一个“但是”吧。")
        self.progress_label.setObjectName("toolbarHint")
        self.progress_label.setWordWrap(True)
        toolbar_layout.addWidget(self.progress_label)

        toolbar_layout.addStretch()

        self.save_button = QPushButton("保存")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(lambda: self._save_current_day(show_message=True))
        toolbar_layout.addWidget(self.save_button)
        main_layout.addWidget(toolbar_card)

        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(18, 16, 18, 16)
        summary_layout.setSpacing(6)

        summary_title = QLabel("填写提醒")
        summary_title.setObjectName("sectionTitle")
        summary_layout.addWidget(summary_title)

        self.summary_label = QLabel("每次只反驳一个“但是”，不要急着一次说服自己所有事情。")
        self.summary_label.setObjectName("summaryInsight")
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        main_layout.addWidget(summary_card)

        scroll_card = QFrame()
        scroll_card.setObjectName("tableCard")
        scroll_layout = QVBoxLayout(scroll_card)
        scroll_layout.setContentsMargins(14, 14, 14, 14)
        scroll_layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setObjectName("chainScrollArea")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("chainContent")
        self.rows_layout = QVBoxLayout(self.scroll_content)
        self.rows_layout.setContentsMargins(4, 4, 4, 4)
        self.rows_layout.setSpacing(12)
        self.rows_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        scroll_layout.addWidget(self.scroll_area)
        main_layout.addWidget(scroll_card)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget#butRebuttalWindow {
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
            }
            QFrame#toolbarCard, QFrame#summaryCard, QFrame#tableCard, QWidget#chainContent {
                background-color: rgba(255, 255, 255, 0.86);
                border: 1px solid #d8e6d4;
                border-radius: 18px;
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
            QLabel#summaryInsight {
                color: #4d6452;
                font-size: 12px;
                background-color: #f5faf3;
                border: 1px solid #dde9d9;
                border-radius: 12px;
                padding: 10px 12px;
            }
            QDateEdit#dateEdit {
                min-width: 140px;
                padding: 8px 12px;
                border-radius: 12px;
                border: 1px solid #b7d0b2;
                background-color: #f7fbf5;
                color: #274030;
            }
            QPushButton#calendarButton, QPushButton#primaryButton {
                min-height: 40px;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#calendarButton {
                background-color: #edf5ea;
                color: #44614b;
                border: 1px solid #c7d9c1;
            }
            QPushButton#calendarButton:hover {
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
            QFrame#rowCard {
                background-color: rgba(252, 253, 249, 0.96);
                border: 1px solid #d4e3d0;
                border-radius: 16px;
            }
            QLabel#columnLabel {
                color: #56705d;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#incomingArrow, QLabel#bridgeArrow {
                color: #57a369;
                font-size: 28px;
                font-weight: 700;
            }
            QTextEdit#leftEdit, QTextEdit#rightEdit {
                background-color: #ffffff;
                border: 1px solid #c9d9c5;
                border-radius: 14px;
                padding: 10px 12px;
                color: #2e4533;
                font-size: 13px;
            }
            QTextEdit#leftEdit:disabled, QTextEdit#rightEdit:disabled {
                background-color: #edf2ea;
                color: #9aa79b;
                border: 1px dashed #d2ddd0;
            }
            QScrollArea#chainScrollArea {
                background: transparent;
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
            entries_data = self.storage.get_but_rebuttal_entries(self.current_date_str)
        except Exception as exc:
            QMessageBox.warning(self, "提示", f"加载反驳“但是”法失败：{exc}")
            entries_data = []

        entries = [ButRebuttalEntry.from_dict(item) for item in entries_data]
        if not entries:
            entries = [ButRebuttalEntry()]

        self._is_loading = True
        self._clear_rows()
        for entry in entries:
            self._append_row(entry)
        self._ensure_trailing_blank_row()
        self._sync_rows()
        self._is_loading = False

    def _clear_rows(self) -> None:
        while self.rows:
            row = self.rows.pop()
            row.setParent(None)
            row.deleteLater()

    def _append_row(self, entry: Optional[ButRebuttalEntry] = None) -> None:
        row_widget = ButRebuttalRow(len(self.rows), self.scroll_content)
        row_widget.content_changed.connect(self._on_row_content_changed)
        if entry is not None:
            row_widget.set_entry(entry)
        self.rows.append(row_widget)
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row_widget)

    def _ensure_trailing_blank_row(self) -> None:
        if not self.rows:
            self._append_row(ButRebuttalEntry())
            return
        if self.rows[-1].has_any_text():
            self._append_row(ButRebuttalEntry())

    def _sync_rows(self) -> None:
        for index, row in enumerate(self.rows):
            previous_right_ready = index == 0 or self.rows[index - 1].has_right_text()
            left_enabled = previous_right_ready
            right_enabled = left_enabled and row.has_left_text()

            row.set_incoming_visible(index > 0 and self.rows[index - 1].has_right_text())
            row.set_bridge_visible(row.has_left_text())
            row.set_left_enabled(left_enabled)
            row.set_right_enabled(right_enabled)

        completed_rebuttals = sum(1 for row in self.rows if row.has_right_text())
        self.progress_label.setText(f"今天已经完成了 {completed_rebuttals} 轮反驳。")
        self.summary_label.setText(self._build_summary_text(completed_rebuttals))

    def _build_summary_text(self, completed_rebuttals: int) -> str:
        if completed_rebuttals == 0:
            return "先把第一个“但是”写下来，再用一个更务实的观点去回应它。"
        if completed_rebuttals < 3:
            return "你已经在把借口具体化了。继续写下去，很多模糊逃避会在文字里自己变弱。"
        return "你已经完成了几轮反驳。现在更重要的不是继续想，而是抓住其中一个反驳，马上开始行动。"

    def _on_row_content_changed(self) -> None:
        if self._is_loading:
            return
        self._ensure_trailing_blank_row()
        self._sync_rows()

    def _collect_entries(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for row in self.rows:
            entry = row.to_entry()
            if entry.excuse_text or entry.rebuttal_text:
                entries.append(entry.to_dict())
        return entries

    def _save_current_day(self, show_message: bool) -> bool:
        if self.current_date_str is None:
            return False
        try:
            entries = self._collect_entries()
            self.storage.save_but_rebuttal_entries(self.current_date_str, entries)
        except Exception as exc:
            QMessageBox.critical(self, "错误", f"保存反驳“但是”法失败：{exc}")
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

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._save_current_day(show_message=False)
        if self.main_window and hasattr(self.main_window, "close_tool"):
            self.main_window.close_tool("but_rebuttal_tool")
        super().closeEvent(event)
