"""配置加载."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from .models import AccountConfig


class Config:
    """运行时配置."""

    def __init__(self) -> None:
        self.runtime_dir = Path(os.getenv("CUA_RUNTIME_DIR", ".runtime"))
        self.default_account = os.getenv("CUA_DEFAULT_ACCOUNT", "enterprise-ai")
        self.max_review_rounds = int(os.getenv("CUA_MAX_REVIEW_ROUNDS", "3"))

        self.kimi_api_key = os.getenv("KIMI_API_KEY", "")
        self.kimi_base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
        self.kimi_model = os.getenv("KIMI_MODEL", "kimi-k3")

        # Get笔记（biji.com）个人开发者配置
        self.getnote_api_key = os.getenv("GETNOTE_API_KEY", "")
        self.getnote_client_id = os.getenv("GETNOTE_CLIENT_ID", "")
        self.getnote_base_url = os.getenv("GETNOTE_BASE_URL", "https://openapi.biji.com/open")

        # Get笔记企业代授权配置（可选）
        self.getnote_grant_id = os.getenv("GETNOTE_GRANT_ID", "")

        raw_paths = os.getenv("CUA_KNOWLEDGE_PATHS", "")
        self.knowledge_paths = [Path(p.strip()) for p in raw_paths.split(",") if p.strip()]

    def ensure_runtime_dir(self) -> None:
        """确保运行时目录存在."""
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def load_account(self, account_id: str) -> AccountConfig:
        """加载账号配置."""
        path = Path("examples/accounts") / f"{account_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"账号配置不存在: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return AccountConfig(**data)


_config: Config | None = None


def get_config() -> Config:
    """获取全局配置."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """重置配置（测试用）."""
    global _config
    _config = None
