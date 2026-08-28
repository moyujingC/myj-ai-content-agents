"""内容生产 Skill 抽象."""

from __future__ import annotations

from abc import ABC, abstractmethod

from myj_ai_content_agents.models import ContentUnit


class Skill(ABC):
    """Skill 基类."""

    name: str = ""

    @abstractmethod
    def run(self, unit: ContentUnit, **kwargs: object) -> ContentUnit:
        raise NotImplementedError


class InterviewSkill(Skill):
    """内容访谈 Skill."""

    name = "interview"


class AssemblySkill(Skill):
    """内容单元组装 Skill."""

    name = "assembly"


class ReviewSkill(Skill):
    """审阅打磨 Skill."""

    name = "review"
