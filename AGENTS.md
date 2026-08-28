# AGENTS.md — MYJ AI Content Agents

## 项目目标

建设一个基于多 Agent 协作的内容生产系统。核心流程以"内容单元"为中间产物，串联选题 Agent、内容生产 Agent（单 Agent 多 Skill）、多平台分发 Agent 集群与数据监控 Agent。项目开源，设计为可在 Claude Code 与 Codex 中协同开发和执行。

核心交付链路：

```
选题 → 内容访谈 → 内容单元组装 → 审阅打磨 → 人工审核 → 内容单元入库
```

## 核心约束

1. **单 Agent 多 Skill**：内容访谈、内容单元组装、审阅打磨必须在同一个 Agent 上下文内完成，避免上下文断裂。
2. **人工审核是强依赖**：任何内容单元在标记为 `approved` 之前，必须有具名人工审核人。
3. **内容单元是标准化中间产物**：不直接产出平台特定内容（如小红书笔记、公众号推文），而是产出可复用的内容单元。
4. **可替换性**：LLM、知识库、分发平台通过接口抽象，不得写死具体实现。
5. **运行时数据不提交 Git**：所有生成产物、数据库、日志写入 `.runtime/`，已配置在 `.gitignore` 中。
6. **Python 3.10+**：优先使用标准库，第三方依赖仅在必要时引入。

## 目录边界

- `myj_ai_content_agents/skills/`：内容访谈、内容单元组装、审阅打磨三个核心 Skill
- `myj_ai_content_agents/knowledge/`：知识库读取适配器（本地 Markdown、得到大脑 API 等）
- `myj_ai_content_agents/eval/`：唯一质量入口，所有审阅标准写成可执行检查
- `myj_ai_content_agents/state_machine.py`：显式状态机，记录内容单元任务状态流转
- `myj_ai_content_agents/store.py`：SQLite 持久化
- `myj_ai_content_agents/cli.py`：命令行入口
- `examples/`：示例配置、账号定义、Prompt 模板
- `tests/`：单元测试和集成测试

## 不可破坏的规则

1. 内容单元在 `approved` 之前必须有 `reviewer` 和 `review_decision == "approve"`
2. 审阅打磨不通过时，必须进入有界循环，最大轮数不得超过配置值（默认 3 轮）
3. 所有外部 API 调用必须可配置、可降级、可替换
4. 知识库路径通过配置文件传入，不得硬编码业务特定路径
5. 失败不可伪装成成功：Eval 不通过、LLM 调用失败、状态机异常都必须显式报错并记录

## 开发纪律

- 每个 Skill 都有明确的输入输出数据模型
- 每个状态转换都要记录 `trace`（from、to、reason、timestamp）
- 新增功能必须伴随测试
- 不要提交 `.env`、API Key、运行时数据库、生成产物
- 修改前阅读 `README.md` 和本文件

## 验证命令

```bash
# 代码风格与类型检查
ruff check myj_ai_content_agents tests
mypy myj_ai_content_agents

# 测试
python -m unittest discover -s tests -v

# Eval
python -m myj_ai_content_agents.eval.harness

# 演示
python -m myj_ai_content_agents.cli demo
```

## Definition of Done

- 相关测试通过
- Eval 检查通过或明确记录失败原因
- 新增 Skill 有输入输出示例
- CLI 命令可用
- 文档（README / AGENTS.md）同步更新
