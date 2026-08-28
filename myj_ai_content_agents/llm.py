"""LLM 调用封装."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from openai import OpenAI

from .config import get_config


class LLMClient(ABC):
    """LLM 客户端抽象."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """调用 LLM 进行对话."""
        raise NotImplementedError

    def chat_json(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """调用 LLM 并返回 JSON."""
        response_format = {"type": "json_object"}
        text = self.chat(messages, model, temperature, max_tokens, response_format)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM 返回不是合法 JSON: {text[:200]}") from exc


class KimiClient(LLMClient):
    """Kimi API 客户端."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        config = get_config()
        self.api_key = api_key or config.kimi_api_key
        self.base_url = base_url or config.kimi_base_url
        self.default_model = model or config.kimi_model
        if not self.api_key:
            raise ValueError("未配置 KIMI_API_KEY")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: dict[str, str] | None = None,
    ) -> str:
        model = model or self.default_model
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        # kimi-k3 目前只支持 temperature=1
        if model != "kimi-k3":
            kwargs["temperature"] = temperature
        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            return content or ""
        except Exception as exc:
            raise RuntimeError(f"Kimi API 调用失败: {exc}") from exc


def get_llm_client() -> LLMClient:
    """获取默认 LLM 客户端."""
    return KimiClient()
