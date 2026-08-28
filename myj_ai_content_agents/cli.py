"""命令行入口."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from myj_ai_content_agents.agent import ContentUnitAgent
from myj_ai_content_agents.config import get_config
from myj_ai_content_agents.eval import evaluate
from myj_ai_content_agents.llm import KimiClient
from myj_ai_content_agents.models import ContentType, Topic
from myj_ai_content_agents.state_machine import ContentUnitStateMachine
from myj_ai_content_agents.store import ContentStore


def _create_agent() -> ContentUnitAgent:
    """创建带 LLM 的 Agent."""
    return ContentUnitAgent(llm=KimiClient())


def cmd_demo(args: argparse.Namespace) -> int:
    """运行演示."""
    config = get_config()
    config.ensure_runtime_dir()

    agent = _create_agent()
    account = config.load_account(args.account or config.default_account)
    topic = Topic(
        id="demo-topic-001",
        title_direction="为什么企业 AI 项目总是在 POC 后死掉",
        user_pain="企业 AI 项目 POC 跑通后无法上线",
        competitor_coverage="多数文章泛泛而谈 AI 落地难",
        source="人工输入",
        priority=5,
        suggested_content_type=ContentType.DEEP_DIVE,
    )

    unit = agent.create_unit(topic, account)
    print(f"创建内容单元: {unit.id}")

    unit = agent.run(unit, account, stop_at=args.stop_at)
    print(f"当前状态: {unit.status}")
    print(json.dumps(unit.model_dump(), ensure_ascii=False, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """运行完整工作流."""
    config = get_config()
    config.ensure_runtime_dir()

    agent = _create_agent()
    account = config.load_account(args.account)
    topic = Topic(
        id=f"topic-{args.topic_hash or 'manual'}",
        title_direction=args.topic,
        user_pain=args.pain or "",
        competitor_coverage="",
        source="cli",
        priority=args.priority,
        suggested_content_type=ContentType(args.content_type),
    )

    unit = agent.create_unit(topic, account, ContentType(args.content_type))
    print(f"创建内容单元: {unit.id}")
    unit = agent.run(unit, account, stop_at=args.stop_at)
    print(f"当前状态: {unit.status}")
    print(json.dumps(unit.model_dump(), ensure_ascii=False, indent=2))
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    """人工审核内容单元."""
    config = get_config()
    store = ContentStore(config.runtime_dir / "myj_ai_content_agents.db")
    unit = store.get_unit(args.unit_id)
    if not unit:
        print(f"内容单元不存在: {args.unit_id}")
        return 1

    machine = ContentUnitStateMachine(unit)
    if args.decision == "approve":
        machine.approve(args.reviewer, args.note)
    else:
        machine.request_rework(args.reviewer, args.note)

    store.save_unit(unit)
    print(f"审核完成: {unit.status}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    """对内容单元执行 Eval."""
    config = get_config()
    store = ContentStore(config.runtime_dir / "myj_ai_content_agents.db")
    unit = store.get_unit(args.unit_id)
    if not unit:
        print(f"内容单元不存在: {args.unit_id}")
        return 1

    result = evaluate(unit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Content Unit Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    demo_cmd = sub.add_parser("demo", help="运行演示")
    demo_cmd.add_argument("--account", default=None)
    demo_cmd.add_argument("--stop-at", default=None, choices=["interviewing", "assembling", "reviewing"])

    run_cmd = sub.add_parser("run", help="从选题运行工作流")
    run_cmd.add_argument("--topic", required=True)
    run_cmd.add_argument("--pain", default="")
    run_cmd.add_argument("--account", required=True)
    run_cmd.add_argument("--content-type", default="deep-dive", choices=["deep-dive", "opinion", "case-flash"])
    run_cmd.add_argument("--priority", type=int, default=3)
    run_cmd.add_argument("--topic-hash", default="manual")
    run_cmd.add_argument("--stop-at", default=None, choices=["interviewing", "assembling", "reviewing"])

    review_cmd = sub.add_parser("review", help="人工审核内容单元")
    review_cmd.add_argument("unit_id")
    review_cmd.add_argument("--reviewer", required=True)
    review_cmd.add_argument("--decision", required=True, choices=["approve", "reject"])
    review_cmd.add_argument("--note", required=True)

    eval_cmd = sub.add_parser("eval", help="执行 Eval 检查")
    eval_cmd.add_argument("unit_id")

    args = parser.parse_args()

    if args.command == "demo":
        return cmd_demo(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "review":
        return cmd_review(args)
    if args.command == "eval":
        return cmd_eval(args)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
