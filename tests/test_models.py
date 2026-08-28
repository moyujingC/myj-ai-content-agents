"""模型测试."""

import unittest

from myj_ai_content_agents.models import AccountConfig, AccountTone, ContentType


class TestModels(unittest.TestCase):
    def test_account_config_load(self) -> None:
        data = {
            "id": "test",
            "name": "测试账号",
            "tone": "personal-ip",
            "target_audience": "测试用户",
            "content_logic": "测试逻辑",
            "platforms": ["公众号"],
            "default_content_type": "deep-dive",
        }
        account = AccountConfig(**data)
        self.assertEqual(account.tone, AccountTone.PERSONAL_IP)
        self.assertEqual(account.default_content_type, ContentType.DEEP_DIVE)


if __name__ == "__main__":
    unittest.main()
