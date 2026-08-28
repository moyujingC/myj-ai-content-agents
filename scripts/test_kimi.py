#!/usr/bin/env python3
"""测试 Kimi API Key 是否可用，并验证是否支持 kimi-k3 模型."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def test_kimi_api() -> None:
    """测试 Kimi API."""
    api_key = os.getenv("KIMI_API_KEY")
    base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    model = os.getenv("KIMI_MODEL", "kimi-k3")

    if not api_key:
        print("错误：未设置 KIMI_API_KEY")
        return

    try:
        from openai import OpenAI
    except ImportError:
        print("需要安装 openai 包: pip install openai")
        return

    client = OpenAI(api_key=api_key, base_url=base_url)

    # 1. 列出可用模型
    print("=" * 50)
    print("1. 测试模型列表")
    print("=" * 50)
    try:
        models = client.models.list()
        available_models = [m.id for m in models.data]
        print(f"可用模型: {available_models}")
        if model in available_models:
            print(f"✅ 目标模型 {model} 可用")
        else:
            print(f"⚠️ 目标模型 {model} 不在列表中，但可能仍可调用")
    except Exception as exc:
        print(f"❌ 获取模型列表失败: {exc}")

    # 2. 简单对话测试
    print("\n" + "=" * 50)
    print("2. 测试简单对话")
    print("=" * 50)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的内容生产助手。"},
                {"role": "user", "content": "请用一句话解释什么是 POC（概念验证）。"},
            ],
            max_tokens=500,
        )
        print(f"模型: {response.model}")
        print(f"回复: {response.choices[0].message.content}")
        print(f"✅ API Key 可用，模型 {model} 可调用")
    except Exception as exc:
        print(f"❌ 对话测试失败: {exc}")


if __name__ == "__main__":
    test_kimi_api()
