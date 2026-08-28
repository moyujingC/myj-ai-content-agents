"""内容访谈 Skill：把隐性知识变成结构化素材库."""

from __future__ import annotations

from myj_ai_content_agents.knowledge import KnowledgeSource
from myj_ai_content_agents.knowledge.local_markdown import LocalMarkdownSource
from myj_ai_content_agents.models import ContentUnit, Material, SourceItem
from myj_ai_content_agents.skills import InterviewSkill


class ContentInterviewSkill(InterviewSkill):
    """基于知识库的内容访谈 Skill."""

    name = "content_interview"

    def __init__(self, sources: list[KnowledgeSource] | None = None) -> None:
        self.sources = sources or [LocalMarkdownSource([])]

    def run(self, unit: ContentUnit, **kwargs: object) -> ContentUnit:
        """执行内容访谈，产出结构化素材库."""
        # 占位实现：从知识库查询相关素材，组装成 Material
        all_items: list[SourceItem] = []
        for source in self.sources:
            for item in source.query(unit.topic_id):
                all_items.append(SourceItem(
                    content=item.get("snippet", ""),
                    source=item.get("source", ""),
                    section=item.get("section", ""),
                ))

        # 简单分类：实际应由 LLM 或更精细规则完成
        material = Material(
            background=[it for it in all_items if "背景" in it.content[:100]],
            key_actions=[it for it in all_items if "做" in it.content[:100]],
            pitfalls=[it for it in all_items if "坑" in it.content[:100] or "失败" in it.content[:100]],
            data_results=[it for it in all_items if "%" in it.content or "倍" in it.content],
            core_insights=[it for it in all_items if "本质" in it.content or "核心" in it.content],
        )

        unit.move("interviewing", f"完成内容访谈，收集 {len(all_items)} 条素材")
        # 素材库通过 kwargs 传递，不直接存入 ContentUnit
        return unit
