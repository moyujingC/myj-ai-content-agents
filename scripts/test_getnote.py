#!/usr/bin/env python3
"""测试 Get笔记（biji.com）API 接入."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from myj_ai_content_agents.knowledge.getnote import GetNoteSource


def main() -> None:
    from myj_ai_content_agents.config import get_config

    config = get_config()
    if not config.getnote_api_key or not config.getnote_client_id:
        print("错误：未配置 GETNOTE_API_KEY 和 GETNOTE_CLIENT_ID")
        print("请在 .env 文件中配置：")
        print("  GETNOTE_API_KEY=gk_live_xxx")
        print("  GETNOTE_CLIENT_ID=cli_xxx")
        return

    source = GetNoteSource(
        api_key=config.getnote_api_key,
        client_id=config.getnote_client_id,
        base_url=config.getnote_base_url,
        topic_id=config.getnote_topic_id or None,
    )

    print("=" * 50)
    print("测试 1：获取笔记列表")
    print("=" * 50)
    try:
        result = source.list_notes(limit=5)
        print(f"响应: {result}")
    except Exception as exc:
        print(f"失败: {exc}")

    print("\n" + "=" * 50)
    print("测试 2：获取知识库列表")
    print("=" * 50)
    try:
        result = source.list_topics(limit=5)
        print(f"响应: {result}")
    except Exception as exc:
        print(f"失败: {exc}")

    print("\n" + "=" * 50)
    print("测试 3：按选题查询相关笔记")
    print("=" * 50)
    try:
        notes = source.query("企业 AI 落地", max_notes=3)
        for note in notes:
            print(f"- 标题: {note.get('title', '')[:50]}")
            print(f"  来源: {note.get('source', '')}")
            print(f"  内容预览: {note.get('content', '')[:200]}...")
            print()
    except Exception as exc:
        print(f"失败: {exc}")

    print("\n" + "=" * 50)
    print("测试 4：知识库语义召回")
    print("=" * 50)
    if source.topic_id:
        try:
            result = source.recall("企业 AI 项目 POC 失败的原因", top_k=3)
            print(f"响应: {result}")
        except Exception as exc:
            print(f"失败: {exc}")
    else:
        print("跳过：未配置 GETNOTE_TOPIC_ID")


if __name__ == "__main__":
    main()
