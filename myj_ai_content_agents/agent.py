"""核心 Agent 调度."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from myj_ai_content_agents.config import get_config
from myj_ai_content_agents.knowledge.getnote import GetNoteSource
from myj_ai_content_agents.knowledge.local_markdown import LocalMarkdownSource
from myj_ai_content_agents.llm import LLMClient
from myj_ai_content_agents.models import AccountConfig, ContentType, ContentUnit, Topic
from myj_ai_content_agents.skills.assembly import ContentAssemblySkill
from myj_ai_content_agents.skills.interview import ContentInterviewSkill
from myj_ai_content_agents.skills.review import ContentReviewSkill
from myj_ai_content_agents.state_machine import ContentUnitStateMachine
from myj_ai_content_agents.store import ContentStore


class ContentUnitAgent:
    """内容生产 Agent：单 Agent 多 Skill."""

    def __init__(self, store: ContentStore | None = None, llm: LLMClient | None = None) -> None:
        self.config = get_config()
        self.store = store or ContentStore(self.config.runtime_dir / "myj_ai_content_agents.db")
        self.llm = llm
        self._setup_knowledge_sources()

    def _setup_knowledge_sources(self) -> None:
        """初始化知识库来源."""
        sources = []
        if self.config.knowledge_paths:
            sources.append(LocalMarkdownSource(self.config.knowledge_paths))
        if self.config.getnote_api_key and self.config.getnote_client_id:
            sources.append(
                GetNoteSource(
                    api_key=self.config.getnote_api_key,
                    client_id=self.config.getnote_client_id,
                    base_url=self.config.getnote_base_url,
                    topic_id=self.config.getnote_topic_id or None,
                )
            )
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
        material = None

        if unit.status == "created":
            material = self.interview_skill.interview(unit)
            unit = self.interview_skill.run(unit)
            self.store.save_unit(unit)

        if stop_at == "interviewing":
            return unit

        if unit.status == "interviewing":
            if material is None:
                material = self.interview_skill.interview(unit)
            assembly = ContentAssemblySkill(account, llm=self.llm)
            unit = assembly.run(unit, material=material)
            self.store.save_unit(unit)

        if stop_at == "assembling":
            return unit

        if unit.status == "assembling":
            review = ContentReviewSkill(account)
            unit = review.run(unit)
            self.store.save_unit(unit)

        return unit

    def approve(self, unit_id: str, reviewer: str, note: str) -> ContentUnit:
        """人工审核通过."""
        unit = self.store.get_unit(unit_id)
        if not unit:
            raise ValueError(f"内容单元不存在: {unit_id}")
        machine = ContentUnitStateMachine(unit)
        machine.approve(reviewer, note)
        self.store.save_unit(unit)
        return unit

    def request_rework(self, unit_id: str, reviewer: str, note: str) -> ContentUnit:
        """请求返工."""
        unit = self.store.get_unit(unit_id)
        if not unit:
            raise ValueError(f"内容单元不存在: {unit_id}")
        machine = ContentUnitStateMachine(unit)
        machine.request_rework(reviewer, note)
        self.store.save_unit(unit)
        return unit
