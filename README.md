# MYJ AI Content Agents

基于多 Agent 协作的内容生产系统。核心流程以"内容单元"为中间产物，串联选题、内容访谈、内容单元组装、审阅打磨、人工审核、多平台分发与数据回流。

> 本项目是墨予镜 AI 服务工作室（ai-service-studio）的 Agent 基础设施，目标是可开源、可迁移、可证明企业级交付能力。

设计目标：
- **单 Agent 多 Skill**：内容生产相关环节共享上下文
- **人工必须参与审核**：不追求全自动，追求可控的高质量输出
- **内容单元作为中间产物**：标题、摘要、正文、标签、适用场景，可被多平台分发复用
- **可替换**：LLM、知识库、分发平台均可替换
- **适合在 Codex 中执行**：代码结构清晰，有明确状态机和 Eval 入口

## 核心工作流

```
选题（人工输入或外部 Agent）
    ↓
内容访谈 Skill（读取本地 Markdown 知识库 / 得到大脑 API）
    ↓
内容单元组装 Skill（调用 Kimi K3）
    ↓
审阅打磨 Skill（结构 / 表达 / 读者适配）
    ↓
人工审核（标题、摘要、金句）
    ↓
内容单元入库
```

## 快速开始

```bash
# 安装
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 KIMI_API_KEY 等

# 运行最小闭环
python -m myj_ai_content_agents.cli run \
  --topic "为什么企业 AI 项目总是在 POC 后死掉" \
  --account enterprise-ai \
  --content-type deep-dive
```

## 内容单元格式

```json
{
  "id": "cu-20260829-001",
  "title": "...",
  "summary": "...",
  "body": "...",
  "tags": ["..."],
  "usage": {
    "platforms": ["公众号", "知乎"],
    "audience": "30-200 人成长型公司创始人/CEO",
    "content_type": "deep-dive"
  },
  "sources": [...],
  "status": "approved",
  "reviewer": "human-name",
  "created_at": "...",
  "updated_at": "..."
}
```

## 项目结构

```
myj_ai_content_agents/     # 核心包
  __init__.py
  config.py             # 配置加载
  models.py             # 数据模型
  knowledge/            # 知识库读取
    __init__.py
    local_markdown.py
    dedao_brain.py      # 得到大脑 API（可选）
  skills/               # Skill 实现
    __init__.py
    interview.py        # 内容访谈
    assembly.py         # 内容单元组装
    review.py           # 审阅打磨
  agent.py              # 核心 Agent 调度
  state_machine.py      # 显式状态机
  eval/                 # 质量评估
    __init__.py
    harness.py
    checks.py
  store.py              # SQLite 持久化
  cli.py                # 命令行入口

examples/               # 示例配置和 Prompt
tests/                  # 测试
.env.example
pyproject.toml
LICENSE
README.md
AGENTS.md               # Codex 执行指引
```

## 账号配置

在 `examples/accounts/` 下配置不同账号的定位和风格：

- `enterprise-ai.yaml`：企业 AI 落地业务账号（个人 IP 号）
- `healing-ai.yaml`：疗愈师 AI 课账号（获客内容号）

## 在 Codex 中执行

1. 在 Codex 中打开本项目
2. 阅读 `AGENTS.md` 了解项目约束
3. 运行 `python -m myj_ai_content_agents.cli demo` 查看演示
4. 通过 `python -m unittest discover -s tests` 运行测试

## 设计原则

1. **业务逻辑自研，基础设施复用**：核心工作流、内容单元格式、审阅标准自己写；LLM API、数据库、文件读取用成熟库
2. **显式状态机**：每个内容单元任务的状态变化可追踪、可回放
3. **Eval 作为质量入口**：所有审阅标准写成可执行的检查
4. **人工审核不可绕过**：只有具名审核人 approve 后才能标记为完成
5. **运行时数据不提交 Git**：SQLite 数据库和生成产物写入 `.runtime/`

## License

MIT
