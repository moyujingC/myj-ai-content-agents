"""本地 Markdown 知识库读取."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import KnowledgeSource


class LocalMarkdownSource(KnowledgeSource):
    """读取本地 Markdown 文件作为知识库."""

    def __init__(self, paths: list[Path]) -> None:
        self.paths = paths

    def query(self, topic: str, max_files: int = 10, max_chars: int = 50000, **kwargs: Any) -> list[dict[str, Any]]:
        """根据关键词在 Markdown 文件中搜索相关片段."""
        keywords = self._extract_keywords(topic)
        results: list[dict[str, Any]] = []
        total_chars = 0

        for path in self.paths:
            if not path.exists():
                continue
            files = sorted(path.rglob("*.md")) if path.is_dir() else [path]
            for file in files:
                if len(results) >= max_files:
                    break
                try:
                    text = file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                score = self._score(text, keywords)
                if score > 0:
                    snippet = self._extract_snippet(text, keywords, 2000)
                    item = {
                        "source": str(file),
                        "score": score,
                        "snippet": snippet,
                        "section": self._extract_title(text),
                    }
                    results.append(item)
                    total_chars += len(snippet)
                    if total_chars >= max_chars:
                        break

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_files]

    def _extract_keywords(self, topic: str) -> list[str]:
        """从选题中提取关键词."""
        # 简单实现：取长度 > 2 的中文字符串和英文单词
        words = re.findall(r"[a-zA-Z_]{3,}", topic)
        chars = re.findall(r"[一-龥]{2,}", topic)
        return list(set(words + chars))

    def _score(self, text: str, keywords: list[str]) -> int:
        """计算文本与关键词的匹配分数."""
        return sum(1 for kw in keywords if kw.lower() in text.lower())

    def _extract_snippet(self, text: str, keywords: list[str], max_length: int) -> str:
        """提取包含关键词的片段."""
        if len(text) <= max_length:
            return text
        for kw in keywords:
            idx = text.lower().find(kw.lower())
            if idx >= 0:
                start = max(0, idx - max_length // 4)
                end = min(len(text), start + max_length)
                return text[start:end]
        return text[:max_length]

    def _extract_title(self, text: str) -> str:
        """提取 Markdown 标题."""
        for line in text.splitlines()[:10]:
            if line.startswith("# "):
                return line[2:].strip()
        return ""
