from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from services.local_store import LocalStore


class LocalStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_migrates_legacy_json_files(self) -> None:
        self._write_json(
            "消极思维日志.json",
            [
                {
                    "type": "three_column",
                    "timestamp": 10.0,
                    "data": {
                        "下意识思维": "未回应日志",
                        "认知扭曲": [["非此即彼", ""]],
                        "理性回应": "",
                    },
                },
                {
                    "type": "six_column",
                    "timestamp": 20.0,
                    "data": {
                        "情况": "考试",
                        "情绪": "焦虑",
                        "下意识思维": "我会失败",
                        "认知扭曲": [["妄下结论 - 先知错误", ""]],
                        "理性回应": "我还可以准备",
                        "结果": "开始复习",
                    },
                },
            ],
        )
        self._write_json("消极思维计数.json", {"2026-03-16": 2, "2026-03-17": 4})
        self._write_json(
            "每日活动计划表.json",
            {
                "2026-03-17": [
                    {
                        "time_slot": "上午 8-9",
                        "plan": "学习",
                        "actual": "学习",
                        "mastery_score": 4,
                        "pleasure_score": 3,
                    }
                ]
            },
        )

        store = LocalStore(self.data_dir)

        self.assertTrue((self.data_dir / "burns_tools.db").exists())
        self.assertEqual(store.get_thought_counts()["2026-03-17"], 4)
        self.assertEqual(store.get_daily_plan("2026-03-17")[0]["plan"], "学习")

        logs = store.get_journal_logs()
        self.assertEqual([log["timestamp"] for log in logs], [10.0, 20.0])
        self.assertEqual(logs[0]["data"]["认知扭曲"][0][0], "非此即彼")
        self.assertEqual(logs[1]["data"]["情况"], "考试")

    def test_supports_crud_after_migration(self) -> None:
        store = LocalStore(self.data_dir)

        store.upsert_journal_log(
            log_type="three_column",
            timestamp=30.0,
            data={
                "下意识思维": "我做不到",
                "认知扭曲": [["乱贴标签", "把自己定义死了"]],
                "理性回应": "",
            },
        )
        store.upsert_journal_log(
            log_type="three_column",
            timestamp=30.0,
            data={
                "下意识思维": "我做不到",
                "认知扭曲": [["乱贴标签", "把自己定义死了"]],
                "理性回应": "我可以先做一点",
            },
        )
        store.save_thought_count("2026-03-17", 7)
        store.save_daily_plan(
            "2026-03-17",
            [
                {
                    "time_slot": "上午 8-9",
                    "plan": "写作",
                    "actual": "写作",
                    "mastery_score": 5,
                    "pleasure_score": 4,
                }
            ],
        )

        logs = store.get_journal_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["data"]["理性回应"], "我可以先做一点")
        self.assertEqual(store.get_thought_counts()["2026-03-17"], 7)
        self.assertEqual(store.get_daily_plan("2026-03-17")[0]["actual"], "写作")

        store.delete_journal_log(30.0)
        self.assertEqual(store.get_journal_logs(), [])

    def test_supports_anti_procrastination_entries(self) -> None:
        store = LocalStore(self.data_dir)

        store.save_anti_procrastination_entries(
            "2026-03-17",
            [
                {
                    "activity": "列大纲",
                    "predicted_difficulty": 80,
                    "predicted_satisfaction": 20,
                    "actual_difficulty": 25,
                    "actual_satisfaction": 70,
                },
                {
                    "activity": "写草稿",
                    "predicted_difficulty": 90,
                    "predicted_satisfaction": 15,
                    "actual_difficulty": 40,
                    "actual_satisfaction": 85,
                },
            ],
        )

        entries = store.get_anti_procrastination_entries("2026-03-17")
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["activity"], "列大纲")
        self.assertEqual(entries[1]["actual_satisfaction"], 85)

    def test_supports_but_rebuttal_entries(self) -> None:
        store = LocalStore(self.data_dir)

        store.save_but_rebuttal_entries(
            "2026-03-17",
            [
                {
                    "excuse_text": "我应该开始做了，但是我现在没心情。",
                    "rebuttal_text": "只要开始五分钟，情绪常常会慢慢跟上。",
                },
                {
                    "excuse_text": "但是这件事太难了。",
                    "rebuttal_text": "我可以先只做最小的一步，不需要一次完成。",
                },
            ],
        )

        entries = store.get_but_rebuttal_entries("2026-03-17")
        self.assertEqual(len(entries), 2)
        self.assertTrue(entries[0]["excuse_text"].startswith("我应该"))
        self.assertIn("最小的一步", entries[1]["rebuttal_text"])

    def _write_json(self, filename: str, payload: object) -> None:
        path = self.data_dir / filename
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    unittest.main()
