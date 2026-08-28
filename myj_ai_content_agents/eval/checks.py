"""Eval 质量检查."""

from __future__ import annotations

from myj_ai_content_agents.models import ContentUnit


def check_title_length(unit: ContentUnit) -> tuple[bool, str]:
    if len(unit.title) < 5:
        return False, f"标题过短: {len(unit.title)} 字"
    if len(unit.title) > 100:
        return False, f"标题过长: {len(unit.title)} 字"
    return True, "标题长度正常"


def check_summary_length(unit: ContentUnit) -> tuple[bool, str]:
    if len(unit.summary) < 30:
        return False, f"摘要过短: {len(unit.summary)} 字"
    return True, "摘要长度正常"


def check_body_length(unit: ContentUnit) -> tuple[bool, str]:
    if len(unit.body) < 100:
        return False, f"正文过短: {len(unit.body)} 字"
    return True, "正文长度正常"


def check_tags(unit: ContentUnit) -> tuple[bool, str]:
    if not unit.tags:
        return False, "标签为空"
    if len(unit.tags) > 7:
        return False, f"标签过多: {len(unit.tags)} 个"
    return True, "标签正常"


def check_sources(unit: ContentUnit) -> tuple[bool, str]:
    if not unit.sources:
        return False, "缺少来源标注"
    return True, "来源标注存在"


DEFAULT_CHECKS = [
    check_title_length,
    check_summary_length,
    check_body_length,
    check_tags,
    check_sources,
]
