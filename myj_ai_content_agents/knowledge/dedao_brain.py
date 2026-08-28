"""得到大脑 API 读取."""

from __future__ import annotations

from typing import Any

from . import KnowledgeSource


class DedaoBrainSource(KnowledgeSource):
    """得到大脑知识库 API 适配器."""

    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def query(self, topic: str, **kwargs: Any) -> list[dict[str, Any]]:
        """查询得到大脑知识库."""
        # TODO: 等得到大脑 API 文档确认后实现
        # 占位实现：返回空列表，不阻塞主流程
        return []

    def fetch_url(self, url: str) -> dict[str, Any]:
        """发送公众号文章链接给得到大脑采集."""
        # TODO: 等 API 文档确认后实现
        raise NotImplementedError("得到大脑 API 尚未实现")
