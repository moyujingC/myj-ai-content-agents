"""数据模型定义."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """内容类型."""

    DEEP_DIVE = "deep-dive"      # 深度拆解型：5000-8000 字
    OPINION = "opinion"          # 观点输出型：800-1500 字
    CASE_FLASH = "case-flash"    # 案例快报型：300-500 字


class AccountTone(str, Enum):
    """账号定位."""

    PERSONAL_IP = "personal-ip"      # 个人 IP 号
    ACQUISITION = "acquisition"      # 获客内容号


class AccountConfig(BaseModel):
    """账号配置."""

    id: str
    name: str
    tone: AccountTone
    target_audience: str
    content_logic: str
    platforms: list[str]
    default_content_type: ContentType
    style_notes: str = ""


class Topic(BaseModel):
    """选题."""

    id: str
    title_direction: str
    user_pain: str
    competitor_coverage: str
    source: str
    priority: int = Field(default=3, ge=1, le=5)
    suggested_content_type: ContentType = ContentType.DEEP_DIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SourceItem(BaseModel):
    """素材来源标注."""

    content: str
    source: str
    section: str = ""


class Material(BaseModel):
    """结构化素材."""

    background: list[SourceItem] = Field(default_factory=list)
    key_actions: list[SourceItem] = Field(default_factory=list)
    pitfalls: list[SourceItem] = Field(default_factory=list)
    data_results: list[SourceItem] = Field(default_factory=list)
    core_insights: list[SourceItem] = Field(default_factory=list)


class ContentUnit(BaseModel):
    """内容单元."""

    id: str
    topic_id: str
    account_id: str
    content_type: ContentType
    title: str = ""
    summary: str = ""
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)
    sources: list[SourceItem] = Field(default_factory=list)
    status: str = "created"
    round_no: int = 0
    max_rounds: int = 3
    trace: list[dict[str, Any]] = Field(default_factory=list)
    reviewer: str | None = None
    review_decision: str | None = None
    review_note: str | None = None
    reviewed_at: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def move(self, target: str, reason: str) -> None:
        """记录状态流转."""
        self.trace.append({
            "from": self.status,
            "to": target,
            "reason": reason,
            "round": self.round_no,
            "at": datetime.now(timezone.utc).isoformat(),
        })
        self.status = target
        self.updated_at = datetime.now(timezone.utc).isoformat()
