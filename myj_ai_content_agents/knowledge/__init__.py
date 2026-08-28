"""知识库读取抽象."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class KnowledgeSource(ABC):
    """知识库来源抽象."""

    @abstractmethod
    def query(self, topic: str, **kwargs: Any) -> list[dict[str, Any]]:
        """根据选题查询相关素材."""
        raise NotImplementedError
