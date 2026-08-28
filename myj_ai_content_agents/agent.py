"""核心 Agent 调度."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from myj_ai_content_agents.config import get_config
from myj_ai_content_agents.knowledge.dedao_brain import DedaoBrainSource
from myj_ai_content_agents.knowledge.local_markdown import LocalMarkdownSource
from myj_ai_content_agents.models import AccountConfig, ContentType, ContentUnit, Topic
from myj_ai_content_agents.skills.assembly import ContentAssemblySkill
from myj_ai_content_agents.skills.interview import ContentInterviewSkill
from myj_ai_content_agents.skills.review import ContentReviewSkill
from myj_ai_content_agents.state_machine import ContentUnitStateMachine
from myj_ai_content_agents.store import ContentStore


class ContentUnitAgent:
    """内容生产 Agent：单 Agent 多 Skill."""

    def __init__(self, store: ContentStore | None = None) -> None:
        self.config = get_config()
        self.store = store or ContentStore(self.config.runtime_dir / "myj_ai_content_agents.db")
        self._setup_knowledge_sources()

    def _setup_knowledge_sources(self) -> None:
        """初始化知识库来源."""
        sources = []
        if self.config.knowledge_paths:
            sources.append(LocalMarkdownSource(self.config.knowledge_paths))
        if self.config.dedao_api_key and self.config.dedao_base_url:
            sources.append(DedaoBrainSource(self.config.dedao_api_key, self.config.dedao_base_url))
        self.interview_skill = ContentInterviewSkill(sources)

    def create_unit(
        self,
        topic: Topic,
        account: AccountConfig,
        content_type: ContentType | None = None,
    ) -> ContentUnit:
        """创建新的内容单元任务."""
        unit_id = f"cu-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        unit = ContentUnit(
            id=unit_id,
            topic_id=topic.id,
            account_id=account.id,
            content_type=content_type or account.default_content_type,
            max_rounds=self.config.max_review_rounds,
        )
        self.store.save_topic(topic)
        self.store.save_unit(unit)
        return unit

    def run(
        self,
        unit: ContentUnit,
        account: AccountConfig,
        stop_at: str | None = None,
    ) -> ContentUnit:
        """运行内容生产工作流."""
        machine = ContentUnitStateMachine(unit)

        if unit.status == "created":
            material = self.interview_skill.run(unit)
            # 重新加载以获取最新状态
            unit = self.store.get_unit(unit.id) or unit
            machine = ContentUnitStateMachine(unit)
            machine.move("interviewing", f"Skill {self.interview_skill.name} 完成")

        if stop_at == "interviewing":
            self.store.save_unit(unit)
            return unit

        if unit.status == "interviewing":
            assembly = ContentAssemblySkill(account)
            # TODO: 传递 material
            unit = assembly.run(unit, material={})
            machine = ContentUnitStateMachine(unit)
            machine.move("assembling", f"Skill {assembly.name} 完成")

        if stop_at == "assembling":
            self.store.save_unit(unit)
            return unit

        if unit.status == "assembling":
            review = ContentReviewSkill(account)
            unit = review.run(unit)
            machine = ContentUnitStateMachine(unit)
            machine.move("reviewing", f"Skill {review.name} 完成")

        self.store.save_unit(unit)
        return unit
