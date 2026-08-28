"""审阅打磨 Skill：结构、表达、读者适配检查."""

from __future__ import annotations

from myj_ai_content_agents.models import AccountConfig, ContentUnit
from myj_ai_content_agents.skills import ReviewSkill


class ContentReviewSkill(ReviewSkill):
    """内容单元审阅 Skill."""

    name = "content_review"

    def __init__(self, account: AccountConfig) -> None:
        self.account = account

    def run(self, unit: ContentUnit, **kwargs: object) -> ContentUnit:
        """执行审阅打磨."""
        # TODO: 接入 Eval 检查和 LLM 审阅
        # 占位实现：只做基础检查
        issues: list[str] = []
        if len(unit.title) < 5:
            issues.append("标题过短")
        if len(unit.summary) < 20:
            issues.append("摘要过短")
        if len(unit.body) < 100:
            issues.append("正文过短")
        if len(unit.tags) > 7:
            issues.append("标签过多")

        if issues:
            unit.move("reviewing", f"审阅发现问题: {'; '.join(issues)}")
        else:
            unit.move("reviewing", "基础审阅通过，等待人工审核")
        return unit
