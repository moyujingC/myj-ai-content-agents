# CLAUDE.md — MYJ AI Content Agents

> 本文件面向 Claude Code 和 Codex，定义项目协作规则。更详细的项目目标、约束和目录边界见 [AGENTS.md](AGENTS.md)。

## 项目一句话

基于多 Agent 协作的内容生产系统，以"内容单元"为中间产物，串联选题、内容访谈、内容单元组装、审阅打磨、人工审核、多平台分发与数据回流。

## 与 Codex / Claude Code 协作的规则

### 1. 先读 AGENTS.md

每次进入本项目或开始新任务前，先确认 [AGENTS.md](AGENTS.md) 中的以下条目是否变化：

- 项目目标
- 核心约束（单 Agent 多 Skill、人工审核、内容单元格式、可替换性）
- 目录边界
- 不可破坏的规则
- 验证命令

### 2. 任务粒度：小步快跑

每个变更只解决一个明确问题。典型任务大小：

- ✅ 接入 Kimi K3 API 生成内容单元正文
- ✅ 实现得到大脑知识库查询
- ✅ 增加一个 Eval 检查项
- ❌ 一次性重写整个 Agent 调度 + 所有 Skill

### 3. 必须伴随测试

新增功能必须有测试覆盖。可接受的形式：

- 单元测试（`tests/test_*.py`）
- Eval 检查（`myj_ai_content_agents/eval/checks.py`）
- CLI 命令可用性验证

### 4. 不要破坏状态机

内容单元状态机是核心。修改前确认：

- 状态流转是否符合 `state_machine.py` 中的 `VALID_TRANSITIONS`
- 是否记录了 `trace`
- 人工审核是否是强依赖

### 5. 外部依赖必须可替换

接入任何外部 API（Kimi、得到大脑、公众号 API）时，必须通过接口抽象，不得直接耦合到业务代码中。

### 6. 运行时数据不提交 Git

数据库、日志、生成产物、`.env` 都写入 `.runtime/` 或不提交。提交前检查 `git status`。

### 7. 文档同步

修改以下任何一项时，同步更新文档：

- 新增 Skill → 更新 `AGENTS.md` 目录边界 + `README.md` 项目结构
- 新增 CLI 命令 → 更新 `README.md` 快速开始
- 修改内容单元格式 → 更新 `README.md` 和 `AGENTS.md`

## 常用命令

```bash
# 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 运行测试
python3 -m unittest discover -s tests -v

# 运行演示
python3 -m myj_ai_content_agents.cli demo

# 从选题运行工作流
python3 -m myj_ai_content_agents.cli run \
  --topic "为什么企业 AI 项目总是在 POC 后死掉" \
  --account enterprise-ai \
  --content-type deep-dive

# 人工审核
python3 -m myj_ai_content_agents.cli review CU-XXXXXX \
  --reviewer your-name \
  --decision approve \
  --note "质量合格，可以发布"

# Eval
python3 -m myj_ai_content_agents.cli eval CU-XXXXXX
```

## 下一步优先级

1. 接入 Kimi K3 API，让 `assembly.py` 真正生成标题、摘要、正文
2. 接入得到大脑 API，让 `dedao_brain.py` 能查询知识库
3. 完善 `review.py` 的审阅逻辑
4. 实现分发 Agent 的占位/手动导出
5. 增加更多 Eval 检查项

## 参考

- [AGENTS.md](AGENTS.md)：项目目标、约束、目录边界、不可破坏的规则
- [README.md](README.md)：项目介绍、快速开始、项目结构
- [pyproject.toml](pyproject.toml)：包配置和依赖
