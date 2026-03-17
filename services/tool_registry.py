from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import QWidget

from tools.anti_procrastination_table import AntiProcrastinationTableWindow
from tools.but_rebuttal_tool import ButRebuttalToolWindow
from tools.daily_activity_plan import DailyActivityPlanWindow
from tools.thought_count import ThoughtCounterWindow
from tools.thought_journal import ThoughtJournalWindow


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    default_name: str
    default_description: str
    factory: Callable[[object], QWidget]


@dataclass(frozen=True)
class ToolConfig:
    tool_id: str
    name: str
    description: str
    factory: Callable[[object], QWidget]


TOOL_DEFINITIONS = [
    ToolDefinition(
        tool_id="thought_journal",
        default_name="\u6d88\u6781\u601d\u7ef4\u65e5\u5fd7",
        default_description="\u8bb0\u5f55\u6d88\u6781\u601d\u7ef4\uff0c\u5e76\u5206\u6790\u5176\u4e2d\u7684\u8ba4\u77e5\u626d\u66f2\u5e76\u7406\u6027\u56de\u5e94",
        factory=lambda main_window: ThoughtJournalWindow(main_window=main_window, storage=main_window.storage),
    ),
    ToolDefinition(
        tool_id="thought_counter",
        default_name="\u6d88\u6781\u601d\u7ef4\u8ba1\u6570\u5668",
        default_description="\u8bb0\u5f55\u5e76\u4fdd\u5b58\u6bcf\u5929\u6d88\u6781\u601d\u7ef4\u53d1\u751f\u7684\u6b21\u6570",
        factory=lambda main_window: ThoughtCounterWindow(main_window=main_window, storage=main_window.storage),
    ),
    ToolDefinition(
        tool_id="daily_activity_plan",
        default_name="\u6bcf\u65e5\u6d3b\u52a8\u8ba1\u5212\u8868",
        default_description="\u5236\u5b9a\u4e00\u5929\u7684\u6d3b\u52a8\u8ba1\u5212\u5e76\u8bb0\u5f55\u5b9e\u9645\u6d3b\u52a8\u53ca\u6ee1\u610f\u5ea6\u8bc4\u5206",
        factory=lambda main_window: DailyActivityPlanWindow(main_window=main_window, storage=main_window.storage),
    ),
    ToolDefinition(
        tool_id="anti_procrastination_table",
        default_name="\u53cd\u62d6\u5ef6\u75c7\u8868",
        default_description="\u628a\u4efb\u52a1\u62c6\u6210\u5c0f\u6b65\u9aa4\uff0c\u6bd4\u8f83\u9884\u671f\u96be\u5ea6\u4e0e\u5b9e\u9645\u4f53\u9a8c\uff0c\u51cf\u8f7b\u62d6\u5ef6\u5e26\u6765\u7684\u754f\u96be\u611f",
        factory=lambda main_window: AntiProcrastinationTableWindow(main_window=main_window, storage=main_window.storage),
    ),
    ToolDefinition(
        tool_id="but_rebuttal_tool",
        default_name="\u53cd\u9a73\u201c\u4f46\u662f\u201d\u6cd5",
        default_description="\u7528\u66f4\u5b9e\u9645\u7406\u6027\u7684\u8bba\u70b9\u53cd\u9a73\u201c\u4f46\u662f\u201d\uff0c\u8ba9\u81ea\u5df1\u6ca1\u6709\u501f\u53e3\u7ee7\u7eed\u9003\u907f\u4efb\u52a1",
        factory=lambda main_window: ButRebuttalToolWindow(main_window=main_window, storage=main_window.storage),
    ),
]

TOOLS_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "tools.json"
TOOL_MAP = {tool.tool_id: tool for tool in TOOL_DEFINITIONS}
DEFAULT_NAME_MAP = {tool.default_name: tool.tool_id for tool in TOOL_DEFINITIONS}


def load_tool_definitions(config_path: Path | None = None) -> list[ToolConfig]:
    overrides = _load_tool_overrides(config_path or TOOLS_JSON_PATH)
    return [
        ToolConfig(
            tool_id=tool.tool_id,
            name=overrides.get(tool.tool_id, {}).get("name", tool.default_name),
            description=overrides.get(tool.tool_id, {}).get("description", tool.default_description),
            factory=tool.factory,
        )
        for tool in TOOL_DEFINITIONS
    ]


def _load_tool_overrides(config_path: Path) -> dict[str, dict[str, str]]:
    if not config_path.exists():
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}

    tools = payload.get("tools", [])
    if not isinstance(tools, list):
        return {}

    overrides: dict[str, dict[str, str]] = {}
    for item in tools:
        if not isinstance(item, dict):
            continue

        tool_id = str(item.get("id", "")).strip()
        if not tool_id:
            legacy_name = str(item.get("name", "")).strip()
            tool_id = DEFAULT_NAME_MAP.get(legacy_name, "")

        if not tool_id or tool_id not in TOOL_MAP:
            continue

        overrides[tool_id] = {
            "name": str(item.get("name", "")).strip() or TOOL_MAP[tool_id].default_name,
            "description": str(item.get("description", "")).strip() or TOOL_MAP[tool_id].default_description,
        }
    return overrides
