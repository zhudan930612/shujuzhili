---
name: data-governance-layer-triage
description: Use when a completed task, discussion, new rule, repeated mistake, or newly learned workflow in this repository needs to be classified into the correct governance layer instead of being left in chat or placed by instinct.
---

# Data Governance Layer Triage

## 概述

用于在当前仓库每次完成一个任务、一次需求沟通轮次或一次重要对话后，对“这次学到的东西”做分层分诊。

这个技能只处理单条对象，不做全仓普查。

## 必读规则

先读取 `../_shared/layer-governance-rules.md`，并严格按其中 6 条规则判断。

如果共享规则文件与本技能正文出现冲突，以共享规则文件为准。

## 适用场景

- “这条规则该写到哪里”
- “这个坑该不该沉淀”
- “这条流程该进 skill 还是脚本”
- “这条经验是不是该上移到顶层默认层”
- “这条稳定规则为什么不能继续放在 `03-工作台`”

## 输入要求

要求用户至少提供以下信息中的 2 项；若缺失，先补问再分诊：

- 这次想沉淀的具体内容
- 它当前放在哪里
- 它为什么值得沉淀
- 它是否需要真实执行
- 它是否只在某目录或某类文件生效

## 分诊顺序

按以下顺序判断，不要跳步：

1. 先检查共享规则中的 6 条是否有明确命中项。
2. 命中后，给出当前仓库中的具体推荐位置。
3. 如果对象本质上是稳定业务主定义，再根据共享规则文件里的“当前仓库补充出口”改判为正式主定义层。
4. 如果 6 条都不命中，明确说明当前暂不沉淀，不要硬放到某层。
5. 如果对象当前在 `skill` 中，但已反复复用，评估是否应按规则 6 上移到顶层默认层；当前仓库默认优先上移到 `AGENTS.md`。

## 输出格式

必须使用以下格式输出：

`【分诊对象】`
一句话说明当前要分诊的对象。

`【命中规则】`
写明命中共享规则中的第几条；若未命中，明确写“未命中 1-6 条，当前暂不沉淀”。

`【推荐层级】`
写明推荐进入哪一层：`顶层默认层`、`path-scoped rules`、`skill`、`hook`、`script/CLI/MCP/checker`、`正式主定义层`、或“暂不沉淀”。

`【推荐位置】`
给出当前仓库中的具体落点或落点类型。

`【建议动作】`
给出下一步动作。只写当前需要做的最小动作。

`【上移提醒】`
如果适用，说明是否应从 `skill` 上移到顶层默认层；当前仓库默认优先上移到 `AGENTS.md`。如果不适用，明确写“当前不涉及上移”。

## 当前仓库默认落点

- 顶层默认层：当前仓库默认优先 `AGENTS.md`，必要时才考虑 `CLAUDE.md`
- path-scoped rules：各目录 `README.md`
- skill：全局技能文件夹，例如 `~/.agents/skills/<skill-name>/SKILL.md`
- hook 候选：`.claude/settings.local.json`
- 执行层：`06-工具脚本/*.py`
- 过程暂存层：`03-工作台/*.md`
- 正式主定义层：`00-项目总览/`、`01-产品架构/`、`02-PRD文档/`、`90-归档记录/`

## 红线

- 不要把只对局部目录生效的规则上移到顶层默认层
- 不要把需要真实执行的动作写成只靠记忆的说明
- 不要把稳定业务主定义继续留在 `03-工作台`
- 不要把“暂不沉淀”的对象硬塞进某个层级
