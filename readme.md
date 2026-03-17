# Burns Tools

一个基于 `PySide6` 的桌面心理自助工具集，目前包含 3 个核心工具：

- 消极思维日志
- 消极思维计数器
- 每日活动计划表

项目整体是一个典型的单体桌面应用：`main.py` 负责启动，`main_window.py` 负责主窗口和工具分发，`components/` 提供复用 UI 组件，`tools/` 承载具体业务工具，`data/` 保存 JSON 数据。

## 快速理解

| 模块 | 作用 |
| :-- | :-- |
| `main.py` | 应用入口，创建 `QApplication`，启动主窗口 |
| `main_window.py` | 主界面控制器，读取工具配置、渲染卡片、打开工具窗口 |
| `components/` | 通用组件，如工具卡片、确认弹窗、提示弹窗 |
| `tools/` | 业务工具模块，如日志、计数器、活动计划 |
| `data/` | 本地 JSON 数据存储与辅助字典 |
| `tests/` | 实验脚本和功能验证脚本 |

## 系统架构图

```mermaid
flowchart TB
    A["main.py<br/>应用入口"] --> B["MainWindow<br/>主窗口控制器"]
    B --> C["data/tools.json<br/>工具清单"]
    B --> D["ToolCard<br/>工具卡片组件"]
    B --> E["ThoughtJournalWindow<br/>消极思维日志"]
    B --> F["ThoughtCounterWindow<br/>消极思维计数器"]
    B --> G["DailyActivityPlanWindow<br/>每日活动计划表"]

    E --> E1["tools/log_editor.py<br/>三列/六列日志编辑器"]
    E --> E2["components/dlg_info_design.py<br/>提示弹窗"]
    E --> E3["components/dlg_confirm_design.py<br/>确认弹窗"]
    E --> E4["data/消极思维日志.json"]

    F --> F1["tools/dlg_calendar.py<br/>日期选择器"]
    F --> F2["ThoughtCounterPlotWindow<br/>统计图窗口"]
    F --> F3["data/消极思维计数.json"]

    G --> G1["ActivityEntry<br/>活动数据模型"]
    G --> G2["data/每日活动计划表.json"]
```

## 目录分层图

```mermaid
flowchart LR
    subgraph App["应用层"]
        A1["main.py"]
        A2["main_window.py"]
    end

    subgraph UI["复用 UI 层"]
        U1["components/tool_card.py"]
        U2["components/dlg_info_design.py"]
        U3["components/dlg_confirm_design.py"]
        U4["main_window_design.py"]
    end

    subgraph Domain["工具业务层"]
        D1["tools/thought_journal.py"]
        D2["tools/log_editor.py"]
        D3["tools/thought_count.py"]
        D4["tools/dlg_calendar.py"]
        D5["tools/daily_activity_plan.py"]
    end

    subgraph Data["本地数据层"]
        DB1["data/tools.json"]
        DB2["data/消极思维日志.json"]
        DB3["data/消极思维计数.json"]
        DB4["data/每日活动计划表.json"]
        DB5["data/date_trans_dict.json"]
    end

    A1 --> A2
    A2 --> U1
    A2 --> U4
    A2 --> D1
    A2 --> D3
    A2 --> D5
    A2 --> DB1
    D1 --> D2
    D1 --> U2
    D1 --> U3
    D1 --> DB2
    D3 --> D4
    D3 --> DB3
    D4 --> DB5
    D5 --> DB4
```

## 核心类图

```mermaid
classDiagram
    class MainWindow {
        +tool_windows: set
        +load_tools()
        +open_tool(tool_name)
        +close_tool(tool_name)
    }

    class ToolCard {
        +tool_name: str
        +tool_description: str
        +clicked(str)
        +setup_ui()
    }

    class ThoughtJournalWindow {
        +logs: list
        +timestamp: float
        +load_data()
        +add_log()
        +open_edit_window(type, log)
        +save_log_3col()
        +save_log_6col()
        +del_log(timestamp)
    }

    class ThoughtCounterWindow {
        +count_data: dict
        +current_count: int
        +load_data()
        +increase_count()
        +decrease_count()
        +save_count()
        +show_statistics()
    }

    class ThoughtCounterPlotWindow {
        +update_plot(index)
        +_get_count_list(time_list)
        +_finalize_plot()
    }

    class DailyActivityPlanWindow {
        +plan_data: dict
        +current_date_str: str
        +_load_day(date)
        +_collect_entries()
        +_save_current_day(show_message)
        +_reset_current_day()
    }

    class ActivityEntry {
        +time_slot: str
        +plan: str
        +actual: str
        +mastery_score: int
        +pleasure_score: int
        +from_dict(data)
        +to_dict()
    }

    class EditLogWindow3Col {
        +distortions_list: list
        +open_distortion_dialog()
        +add_distortion_item(item)
    }

    class EditLogWindow6Col {
        +distortions_list: list
        +open_distortion_dialog()
        +add_distortion_item(item)
    }

    MainWindow --> ToolCard : 创建并监听点击
    MainWindow --> ThoughtJournalWindow : 打开
    MainWindow --> ThoughtCounterWindow : 打开
    MainWindow --> DailyActivityPlanWindow : 打开
    ThoughtJournalWindow --> EditLogWindow3Col : 使用
    ThoughtJournalWindow --> EditLogWindow6Col : 使用
    ThoughtCounterWindow --> ThoughtCounterPlotWindow : 打开
    DailyActivityPlanWindow --> ActivityEntry : 组装/转换
```

## 主流程时序图

### 1. 从主页打开工具

```mermaid
sequenceDiagram
    participant U as 用户
    participant C as ToolCard
    participant M as MainWindow
    participant T as ToolWindow

    U->>C: 点击工具卡片
    C->>M: clicked(tool_name)
    M->>M: open_tool(tool_name)
    alt 窗口未打开
        M->>T: 创建工具窗口实例
        M->>T: show()
    else 窗口已打开
        M->>T: activateWindow()
    end
```

### 2. 消极思维日志保存流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant J as ThoughtJournalWindow
    participant D as TemplateSelectionDialog
    participant E as EditLogWindow3Col/6Col
    participant F as JSON文件

    U->>J: 点击“添加日志”
    J->>D: 打开模板选择框
    U->>D: 选择三列或六列模板
    D-->>J: 返回模板类型
    J->>E: 打开编辑窗口
    U->>E: 输入内容并点击保存
    E-->>J: 触发保存信号
    J->>J: 组装日志数据并排序
    J->>F: 写入 data/消极思维日志.json
    J->>J: 刷新日志卡片列表
```

### 3. 消极思维计数器统计流程

```mermaid
sequenceDiagram
    participant U as 用户
    participant W as ThoughtCounterWindow
    participant F as data/消极思维计数.json
    participant P as ThoughtCounterPlotWindow

    W->>F: 启动时加载历史计数
    U->>W: 增减当天计数并保存
    W->>F: 写入 JSON
    U->>W: 点击“统计”
    W->>P: 创建统计图窗口
    P->>P: 计算近7/30/90/180/365天数据
    P->>U: 展示折线图
```

## 数据模型图

```mermaid
classDiagram
    class JournalLog {
        +type: str
        +timestamp: float
        +data: dict
    }

    class CountData {
        +date: yyyy-MM-dd
        +count: int
    }

    class ActivityEntry {
        +time_slot: str
        +plan: str
        +actual: str
        +mastery_score: 0..5
        +pleasure_score: 0..5
    }

    class DailyPlanData {
        +date: str
        +entries: ActivityEntry[]
    }

    JournalLog --> CountData : 并列存储
    DailyPlanData --> ActivityEntry : 包含多个
```

## 当前架构特点

- 优点：结构直观，入口清晰，适合小型桌面工具集快速迭代。
- 优点：每个工具基本独立，便于继续新增新的心理辅助小工具。
- 优点：数据采用本地 JSON，开发和调试成本低。
- 可改进点：业务逻辑、UI 逻辑、存储逻辑目前仍有一定耦合，后续可抽出 `service` 或 `repository` 层。
- 可改进点：工具打开逻辑现在依赖 `if/elif` 分发，后续可以改为注册表模式。
- 可改进点：`tests/` 目前更像实验脚本，尚未形成自动化测试体系。

## 新人阅读建议

推荐按下面顺序阅读代码：

1. `main.py`
2. `main_window.py`
3. `components/tool_card.py`
4. `tools/thought_journal.py`
5. `tools/thought_count.py`
6. `tools/daily_activity_plan.py`

这样可以先看清“应用如何启动”，再理解“主窗口如何分发工具”，最后再分别进入各个业务工具内部。
