"""内容单元组装 Skill：从素材库产出标准化内容单元."""

from __future__ import annotations

import json
from typing import Any

from myj_ai_content_agents.llm import LLMClient
from myj_ai_content_agents.models import AccountConfig, ContentType, ContentUnit, Material, SourceItem
from myj_ai_content_agents.skills import AssemblySkill


class ContentAssemblySkill(AssemblySkill):
    """基于素材库组装内容单元."""

    name = "content_assembly"

    def __init__(self, account: AccountConfig, llm: LLMClient | None = None) -> None:
        self.account = account
        self.llm = llm

    def run(self, unit: ContentUnit, material: Material, **kwargs: object) -> ContentUnit:
        """执行内容单元组装."""
        llm = self.llm or kwargs.get("llm")
        if not isinstance(llm, LLMClient):
            raise ValueError("ContentAssemblySkill 需要传入 LLMClient")

        prompt = self._build_prompt(unit, material)
        messages = [
            {"role": "system", "content": "你是一位专业的内容生产专家，擅长把结构化素材转化为高质量、可发布的内容单元。"},
            {"role": "user", "content": prompt},
        ]

        try:
            result = llm.chat_json(messages, temperature=0.7, max_tokens=self._max_tokens(unit.content_type))
        except Exception as exc:
            unit.move("failed", f"LLM 调用失败: {exc}")
            return unit

        unit.title = str(result.get("title", "")).strip()
        unit.summary = str(result.get("summary", "")).strip()
        unit.body = str(result.get("body", "")).strip()
        unit.tags = [str(t).strip() for t in result.get("tags", []) if str(t).strip()]
        unit.usage = {
            "platforms": self.account.platforms,
            "audience": self.account.target_audience,
            "content_type": unit.content_type.value,
        }
        unit.sources = self._collect_sources(material)

        if not unit.title or not unit.summary or not unit.body:
            unit.move("failed", "LLM 返回的内容单元缺少必要字段")
            return unit

        unit.move("assembling", "完成内容单元组装")
        return unit

    def _max_tokens(self, content_type: ContentType) -> int:
        """根据内容类型选择最大 token 数."""
        return {
            ContentType.DEEP_DIVE: 12000,
            ContentType.OPINION: 6000,
            ContentType.CASE_FLASH: 2000,
        }.get(content_type, 6000)

    def _build_prompt(self, unit: ContentUnit, material: Material) -> str:
        """构建组装 Prompt."""
        structure = self._content_structure(unit.content_type)
        material_text = self._material_to_text(material)

        output_format = (
            "## 输出格式\n"
            "请直接输出以下 JSON 对象，不要包含代码块标记、不要包含 JSON 之外的任何解释：\n\n"
            '{"title": "文章标题，一句话概括核心观点，有冲突感", "summary": "3-5句话摘要，说明内容价值", "body": "完整正文，使用 Markdown 格式", "tags": ["标签1", "标签2", "标签3"]}\n\n'
            "要求：\n"
            "1. 标题必须有冲突感或信息密度，能吸引人点击\n"
            "2. 摘要直接说明读者能获得什么价值\n"
            "3. 正文先堆信息密度，再统一语气\n"
            "4. 每个新概念必须用人话解释，英文缩写尽量少用\n"
            "5. 案例必须自洽，经得起推敲\n"
            "6. 引用保守，不能追溯来源的数据用模糊表述\n"
            "7. 结尾尽量给出可执行的清单/框架/问题集"
        )

        return f"""请根据以下素材，为一篇{self._content_type_name(unit.content_type)}生成标准化的内容单元。

## 选题
{unit.topic_id}

## 账号定位
- 账号名称：{self.account.name}
- 目标读者：{self.account.target_audience}
- 内容风格：{self.account.content_logic}
- 风格备注：{self.account.style_notes}

## 内容结构要求
{structure}

## 素材库
{material_text}

{output_format}
"""

    def _content_structure(self, content_type: ContentType) -> str:
        """根据内容类型返回结构要求."""
        structures = {
            ContentType.DEEP_DIVE: """深度拆解型（5000-8000 字）
结构：问题定义 → 案例拆解 → 底层逻辑 → 可复制方法
- 开头直接抛出核心问题
- 中间用 2-3 个具体案例支撑
- 每个案例后提炼底层逻辑
- 结尾给出可执行的方法或清单""",
            ContentType.OPINION: """观点输出型（800-1500 字）
结构：一个反常识观点 → 3 个论据 → 1 个行动建议
- 开头给出一个有冲突感的观点
- 用 3 个论据支撑，每个论据配一个案例或数据
- 结尾给读者一个具体可做的行动建议""",
            ContentType.CASE_FLASH: """案例快报型（300-500 字）
结构：谁做了什么 → 结果如何 → 为什么值得关注
- 一句话说明主体和动作
- 给出关键结果数据
- 点明这个案例对目标读者的启发""",
        }
        return structures.get(content_type, structures[ContentType.DEEP_DIVE])

    def _content_type_name(self, content_type: ContentType) -> str:
        names = {
            ContentType.DEEP_DIVE: "深度拆解型文章",
            ContentType.OPINION: "观点输出型文章",
            ContentType.CASE_FLASH: "案例快报型内容",
        }
        return names.get(content_type, "文章")

    def _material_to_text(self, material: Material) -> str:
        """把素材库转换为文本."""
        sections = []
        if material.background:
            sections.append("### 背景信息\n" + self._items_to_text(material.background))
        if material.key_actions:
            sections.append("### 关键动作\n" + self._items_to_text(material.key_actions))
        if material.pitfalls:
            sections.append("### 踩坑记录\n" + self._items_to_text(material.pitfalls))
        if material.data_results:
            sections.append("### 数据结果\n" + self._items_to_text(material.data_results))
        if material.core_insights:
            sections.append("### 核心认知\n" + self._items_to_text(material.core_insights))
        return "\n\n".join(sections) or "（暂无结构化素材，请基于选题自由发挥）"

    def _items_to_text(self, items: list[SourceItem]) -> str:
        lines = []
        for it in items:
            lines.append(f"- {it.content}")
            if it.source:
                lines.append(f"  来源：{it.source}")
        return "\n".join(lines)

    def _collect_sources(self, material: Material) -> list[SourceItem]:
        """收集所有素材来源."""
        sources: list[SourceItem] = []
        for field in (material.background, material.key_actions, material.pitfalls, material.data_results, material.core_insights):
            sources.extend(field)
        return sources
