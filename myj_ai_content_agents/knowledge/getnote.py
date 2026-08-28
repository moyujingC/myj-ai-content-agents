"""Get笔记（biji.com）API 读取."""

from __future__ import annotations

from typing import Any

import requests

from . import KnowledgeSource


class GetNoteSource(KnowledgeSource):
    """Get笔记 API 适配器.

    个人开发者模式：使用 Client ID + API Key 直接调用接口，
    读取当前账号下的笔记内容。
    """

    def __init__(self, api_key: str, client_id: str, base_url: str = "https://openapi.biji.com/open") -> None:
        self.api_key = api_key
        self.client_id = client_id
        self.base_url = base_url.rstrip("/")

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

    def query(self, topic: str, max_notes: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        """根据选题关键词查询相关笔记.

        当前实现：拉取最近笔记，按标题和内容与选题关键词的相关性筛选。
        """
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
                "content": note.get("content", ""),
                "title": note.get("title", ""),
                "source": f"getnote://note/{note.get('note_id', note.get('id', ''))}",
                "section": "",
                "score": score,
            }
            for note, score in selected
        ]

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
