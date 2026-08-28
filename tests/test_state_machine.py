"""状态机测试."""

import unittest

from myj_ai_content_agents.models import ContentType, ContentUnit
from myj_ai_content_agents.state_machine import ContentUnitStateMachine


class TestStateMachine(unittest.TestCase):
    def setUp(self) -> None:
        self.unit = ContentUnit(
            id="cu-test-001",
            topic_id="topic-001",
            account_id="enterprise-ai",
            content_type=ContentType.DEEP_DIVE,
            max_rounds=2,
        )

    def test_normal_flow(self) -> None:
        machine = ContentUnitStateMachine(self.unit)
        machine.move("interviewing", "开始访谈")
        machine.move("assembling", "完成访谈")
        machine.move("reviewing", "完成组装")
        machine.approve("reviewer-a", "质量合格")
        self.assertEqual(self.unit.status, "approved")
        self.assertEqual(self.unit.reviewer, "reviewer-a")

    def test_rework_within_limit(self) -> None:
        machine = ContentUnitStateMachine(self.unit)
        machine.move("interviewing", "开始访谈")
        machine.move("assembling", "完成访谈")
        machine.move("reviewing", "进入审阅")
        machine.request_rework("reviewer-a", "需要修改")
        self.assertEqual(self.unit.status, "rework")
        self.assertEqual(self.unit.round_no, 1)

    def test_rework_exceeds_limit(self) -> None:
        self.unit.max_rounds = 1
        machine = ContentUnitStateMachine(self.unit)
        machine.move("interviewing", "开始访谈")
        machine.move("assembling", "完成访谈")
        machine.move("reviewing", "进入审阅")
        machine.request_rework("reviewer-a", "需要修改")
        machine.move("reviewing", "再次进入审阅")
        with self.assertRaises(ValueError):
            machine.request_rework("reviewer-a", "还需要修改")

    def test_invalid_transition(self) -> None:
        machine = ContentUnitStateMachine(self.unit)
        with self.assertRaises(ValueError):
            machine.move("approved", "非法跳转")


if __name__ == "__main__":
    unittest.main()
