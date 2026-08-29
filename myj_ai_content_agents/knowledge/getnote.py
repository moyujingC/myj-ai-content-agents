"""Get笔记（biji.com）API 读取."""

from __future__ import annotations

from typing import Any

import requests

from . import KnowledgeSource


class GetNoteSource(KnowledgeSource):
    """Get笔记 API 适配器.

    个人开发者模式：使用 Client ID + API Key 直接调用接口，
    读取当前账号下的笔记内容，并支持知识库语义召回。
    """

    def __init__(
        self,
        api_key: str,
        client_id: str,
        base_url: str = "https://openapi.biji.com/open",
        topic_id: str | None = None,
    ) -> None:
        self.api_key = api_key
        self.client_id = client_id
        self.base_url = base_url.rstrip("/")
        self.topic_id = topic_id

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": self.api_key,
            "X-Client-ID": self.client_id,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """发起 API 请求."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Get笔记 API 请求失败: {exc}") from exc

    def list_notes(self, cursor: str | None = None, limit: int = 20) -> dict[str, Any]:
        """获取笔记列表."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/api/v1/resource/note/list", params=params)

    def list_topics(self, cursor: str | None = None, limit: int = 20) -> dict[str, Any]:
        """获取知识库（topic）列表."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._request("GET", "/api/v1/resource/topic/list", params=params)

    def recall(self, query: str, topic_id: str | None = None, top_k: int = 5, with_content: bool = True) -> dict[str, Any]:
        """知识库语义召回.

        通过向量/语义相似度，从指定知识库中召回与查询最相关的笔记片段。

        注意：该接口目前主要面向企业代授权模式。个人开发者模式调用可能返回 404，
        此时 query() 会自动回退到关键词筛选。
        """
        body: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
            "with_content": with_content,
        }
        if topic_id:
            body["topic_id"] = topic_id
        elif self.topic_id:
            body["topic_id"] = self.topic_id
        return self._request("POST", "/api/v1/resource/note/recall", json=body)

    def query(self, topic: str, max_notes: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """根据选题查询相关笔记.

        如果配置了 topic_id 且语义召回接口可用，优先使用语义召回；
        否则回退到拉取最近笔记并按关键词筛选。
        """
        effective_topic_id = kwargs.get("topic_id") or self.topic_id
        if effective_topic_id:
            try:
                return self._query_by_recall(topic, effective_topic_id, max_notes)
            except RuntimeError as exc:
                # 个人开发者模式可能不支持语义召回，回退到关键词筛选
                import re
                if "404" in str(exc):
                    print(f"[GetNote] 语义召回不可用（{exc}），回退到关键词筛选")
                else:
                    raise

        keywords = self._extract_keywords(topic)
        all_notes: list[dict[str, Any]] = []
        cursor: str | None = None
        fetched = 0
        max_fetch = max(100, max_notes * 3)  # 多取一些再筛选

        while fetched < max_fetch:
            result = self.list_notes(cursor=cursor, limit=50)
            data = result.get("data", {})
            notes = data.get("notes", [])
            if not notes:
                break

            for note in notes:
                all_notes.append(note)
                fetched += 1
                if fetched >= max_fetch:
                    break

            if not data.get("has_more"):
                break
            cursor = data.get("cursor")
            if not cursor:
                break

        # 按相关性筛选
        scored = []
        for note in all_notes:
            score = self._score(note, keywords)
            if score > 0:
                scored.append({"note": note, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        selected = scored[:max_notes]

        return [
            {
                "content": item["note"].get("content", ""),
                "title": item["note"].get("title", ""),
                "source": f"getnote://note/{item['note'].get('note_id', item['note'].get('id', ''))}",
                "section": "",
                "score": item["score"],
            }
            for item in selected
        ]

    def _query_by_recall(self, topic: str, topic_id: str, max_notes: int) -> list[dict[str, Any]]:
        """使用知识库语义召回答题."""
        result = self.recall(query=topic, topic_id=topic_id, top_k=max_notes)
        data = result.get("data", {})
        notes = data.get("notes", data.get("results", []))

        output: list[dict[str, Any]] = []
        for item in notes:
            note = item.get("note", item)
            output.append(
                {
                    "content": note.get("content", item.get("snippet", "")),
                    "title": note.get("title", ""),
                    "source": f"getnote://note/{note.get('note_id', note.get('id', ''))}",
                    "section": item.get("topic_name", ""),
                    "score": item.get("score", 0.0),
                }
            )
        return output

    def fetch_url(self, url: str) -> dict[str, Any]:
        """发送公众号文章链接给 Get笔记采集.

        TODO: 需要确认 Get笔记是否有文章采集接口。
        """
        raise NotImplementedError("Get笔记文章采集接口尚未实现")

    def _extract_keywords(self, topic: str) -> list[str]:
        """从选题中提取关键词."""
        import re
        words = re.findall(r"[a-zA-Z_]{3,}", topic)
        chars = re.findall(r"[一-龥]{2,}", topic)
        return list(set(words + chars))

    def _score(self, note: dict[str, Any], keywords: list[str]) -> int:
        """计算笔记与关键词的匹配分数."""
        text = f"{note.get('title', '')} {note.get('content', '')}".lower()
        return sum(1 for kw in keywords if kw.lower() in text)
