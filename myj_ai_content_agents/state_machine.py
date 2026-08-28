"""内容单元任务状态机."""

from __future__ import annotations

from myj_ai_content_agents.models import ContentUnit


class ContentUnitStateMachine:
    """内容单元状态机.

    状态流转：
        created → interviewing → assembling → reviewing → approved
                              ↓            ↓
                           rework     failed
    """

    VALID_TRANSITIONS = {
        "created": {"interviewing", "failed"},
        "interviewing": {"assembling", "failed"},
        "assembling": {"reviewing", "failed"},
        "reviewing": {"approved", "rework", "failed"},
        "rework": {"reviewing", "failed"},
        "approved": set(),
        "failed": set(),
    }

    def __init__(self, unit: ContentUnit) -> None:
        self.unit = unit

    def can_move(self, target: str) -> bool:
        return target in self.VALID_TRANSITIONS.get(self.unit.status, set())

    def move(self, target: str, reason: str) -> None:
        if not self.can_move(target):
            raise ValueError(f"非法状态流转: {self.unit.status} → {target}")
        self.unit.move(target, reason)

    def approve(self, reviewer: str, note: str) -> None:
        if self.unit.status != "reviewing":
            raise ValueError(f"只有 reviewing 状态才能 approve，当前: {self.unit.status}")
        self.unit.reviewer = reviewer
        self.unit.review_decision = "approve"
        self.unit.review_note = note
        self.move("approved", f"审核人 {reviewer} 批准: {note}")

    def request_rework(self, reviewer: str, note: str) -> None:
        if self.unit.status != "reviewing":
            raise ValueError(f"只有 reviewing 状态才能请求返工，当前: {self.unit.status}")
        if self.unit.round_no >= self.unit.max_rounds:
            raise ValueError(f"已达到最大审阅轮数: {self.unit.max_rounds}")
        self.unit.reviewer = reviewer
        self.unit.review_decision = "reject"
        self.unit.review_note = note
        self.unit.round_no += 1
        self.move("rework", f"审核人 {reviewer} 打回: {note}")
