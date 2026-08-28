#!/usr/bin/env python3
"""测试 assembly prompt 和 LLM 输出."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from myj_ai_content_agents.config import get_config
from myj_ai_content_agents.llm import KimiClient
from myj_ai_content_agents.models import AccountConfig, ContentType, ContentUnit, Material
from myj_ai_content_agents.skills.assembly import ContentAssemblySkill


def main() -> None:
    config = get_config()
    account = config.load_account("enterprise-ai")
    unit = ContentUnit(
        id="cu-test-001",
        topic_id="demo-topic-001",
        account_id="enterprise-ai",
        content_type=ContentType.OPINION,  # 先用短文本测试
    )
    material = Material()

    skill = ContentAssemblySkill(account, llm=KimiClient())
    prompt = skill._build_prompt(unit, material)

    print("=" * 50)
    print("PROMPT:")
    print("=" * 50)
    print(prompt[:2000])
    print("\n" + "=" * 50)
    print("LLM RAW RESPONSE:")
    print("=" * 50)

    llm = KimiClient()
    messages = [
        {"role": "system", "content": "你是一位专业的内容生产专家，擅长把结构化素材转化为高质量、可发布的内容单元。"},
        {"role": "user", "content": prompt},
    ]
    response = llm.chat(messages, max_tokens=2500)
    print(response)


if __name__ == "__main__":
    main()
