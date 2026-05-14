---
name: layer-governance-audit
description: Use when the current repository needs an explicit governance-layer audit to find which rules, workflows, scripts, and documents are sitting in the wrong layer and what should be moved, promoted, or split.
---

# Layer Governance Audit

## 概述

用于主动审查当前仓库的分层治理现状。

这个技能处理的是“当前仓库整体状态”，不是单条经验分诊。它与 `data-governance-layer-triage` 使用同一套判断规则，只是输入粒度更大。

## 必读规则

先读取 `../_shared/layer-governance-rules.md`，并严格按其中 6 条规则审计。

如果共享规则文件与本技能正文出现冲突，以共享规则文件为准。

## 审计目标

识别当前仓库中：

- 哪些内容本应进入顶层默认层，当前仓库默认即 `AGENTS.md`，却还停留在 skill 或过程文档里
- 哪些内容本应进入 path-scoped rules，却污染了全局
- 哪些内容本应进入 `skill`，却仍停留在长 Markdown 里
- 哪些内容本应进入 `hook`，却仍只是提醒
- 哪些内容本应进入 `script/CLI/MCP/checker`，却仍写成口头说明
- 哪些专题经验已反复出现，应从 `skill` 上移到顶层默认层
- 哪些稳定业务主定义错误地滞留在 `03-工作台`

## 审计顺序

按以下顺序执行：

1. 读取共享规则文件。
2. 先读取 `AGENTS.md`；只有需要确认兜底入口时再读取 `CLAUDE.md`。
3. 读取高价值 path-scoped rules；当前仓库默认先看：
   - `03-工作台/README.md`
   - `04-原型效果图/后台管理/README.md`
   - `04-原型效果图/后台管理/assets/README.md`
   - `06-工具脚本/README.md`
4. 读取流程型文档：
   - `03-工作台/任务执行协议.md`
   - `03-工作台/任务完成检查.md`
   - `03-工作台/错误治理清单.md`
5. 读取现有 repo-local skills。
6. 读取 `.claude/settings.local.json`，查看当前 hooks 现状。
7. 运行 `python 06-工具脚本/run_checks.py --scope all`。
8. 汇总“脚本已发现的问题”和“脚本查不到但明显错层的问题”。

## 输出格式

必须使用以下格式输出：

`【仓库映射】`
简要说明当前仓库各层默认落点是否清晰。

`【错层项清单】`
逐条列出：
- 审计对象
- 当前所在层
- 建议目标层
- 迁移原因

`【治理升级候选】`
分别列出：
- 哪些应升级为 `skill`
- 哪些应升级为 `hook`
- 哪些应升级为 `script/checker`
- 哪些应上移到顶层默认层

`【本轮建议动作】`
只给 3 到 5 条本轮最值得做的动作，按优先级排序。

## 当前仓库默认落点

- 顶层默认层：当前仓库默认优先 `AGENTS.md`，必要时才考虑 `CLAUDE.md`
- path-scoped rules：各目录 `README.md`
- skill：全局技能文件夹，例如 `~/.agents/skills/<skill-name>/SKILL.md`
- hook 候选：`.claude/settings.local.json`
- 执行层：`06-工具脚本/*.py`
- 过程暂存层：`03-工作台/*.md`
- 正式主定义层：`00-项目总览/`、`01-产品架构/`、`02-PRD文档/`、`90-归档记录/`

## 红线

- 不要把目录结构是否“好看”当作审计目标；只看是否放错层
- 不要把 `run_checks.py` 的结果原样复述成审计报告；必须补充分层判断
- 不要把单条经验细化成模板写作；那是 `data-governance-layer-triage` 的职责
- 不要把稳定业务主定义误审成协作规则层问题；必要时明确要求拆回正式主定义层
