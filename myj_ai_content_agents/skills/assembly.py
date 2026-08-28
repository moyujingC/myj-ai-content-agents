"""内容单元组装 Skill：从素材库产出标准化内容单元."""

from __future__ import annotations

from myj_ai_content_agents.models import AccountConfig, ContentUnit, Material
from myj_ai_content_agents.skills import AssemblySkill


class ContentAssemblySkill(AssemblySkill):
    """基于素材库组装内容单元."""

    name = "content_assembly"

    def __init__(self, account: AccountConfig) -> None:
        self.account = account

    def run(self, unit: ContentUnit, material: Material, **kwargs: object) -> ContentUnit:
        """执行内容单元组装."""
        # TODO: 接入 Kimi K3 API，根据素材库、账号定位、内容类型生成标题、摘要、正文
        # 占位实现：生成框架性内容
        unit.title = f"【占位标题】{unit.topic_id}"
        unit.summary = "【占位摘要】待接入 Kimi K3 后生成。"
        unit.body = self._build_body_placeholder(material)
        unit.tags = ["AI", "企业落地", "POC"]
        unit.usage = {
            "platforms": self.account.platforms,
            "audience": self.account.target_audience,
            "content_type": unit.content_type.value,
        }
        unit.move("assembling", "完成内容单元组装（占位实现）")
        return unit

    def _build_body_placeholder(self, material: Material) -> str:
        lines = ["# 占位正文", ""]
        if material.background:
            lines.extend(["## 背景", ""])
            for it in material.background[:3]:
                lines.append(f"- {it.content[:200]}")
            lines.append("")
        if material.key_actions:
            lines.extend(["## 关键动作", ""])
            for it in material.key_actions[:3]:
                lines.append(f"- {it.content[:200]}")
            lines.append("")
        lines.append("## 待接入 LLM 生成完整正文")
        return "\n".join(lines)
