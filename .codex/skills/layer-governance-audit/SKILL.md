---
name: layer-governance-audit
description: 用于审查当前仓库已有治理资产是否写乱层、放错位置或职责串位，尤其适合“检查当前规则是不是写乱层了”“审查 AGENTS、skills、scripts、hooks、rules 放得对不对”“看看哪些治理内容放错位置了”“给我当前仓库的分层整改建议”“检查运行时规则、hooks 和 rules 是否配置在合适的位置”这类场景。
---

# Layer Governance Audit

## 概述

用于主动审查当前仓库已有治理资产的分层治理现状。

`data-governance-layer-triage` 的职责是给新经验找归宿；`layer-governance-audit` 的职责是检查现有治理资产的归宿是否合理。

这个技能只审、不改，不负责新经验首次落点，不审过程文档，也不审业务主定义本身。

## 适用场景

- “检查当前规则是不是写乱层了”
- “审查 AGENTS、skills、scripts、hooks 放得对不对”
- “看看哪些治理内容放错位置了”
- “给我当前仓库的分层整改建议”
- “AGENTS 里是不是塞了不该放的内容”
- “这些技能是不是写错层了”
- “哪些 README 其实承担了错误职责”
- “哪些提醒其实该做成脚本或 hook”
- “settings 里的 hook、permissions 和 rules 是否合理”
- “运行时规则是不是和文档规则打架了”
- “检查 `.codex/rules/` 里的规则放得对不对”
- “看看哪些 command rules 应该进项目级 rules”
- “用户级 rules 会不会覆盖当前仓库的治理意图”

## 不适用场景

- “这条新经验要不要沉淀”
- “这条规则首次该写到哪里”
- “这次会话总结出来的教训该放哪”
- “某条业务规则是否合理”
- “过程文档和正式 PRD 是否冲突”
- “稳定业务规则是否该拆回主定义”

上述场景应改用 `data-governance-layer-triage` 或其他业务/文档工作流。

## 审计对象

- 顶层默认层：`AGENTS.md`，必要时 `CLAUDE.md`
- 路径作用域规则：高价值目录 `README.md`
- skill 层：`.codex/skills/*/SKILL.md`
- 执行层：`06-工具脚本/README.md` 与相关 `.py` 脚本
- hook 层：`.codex/settings.local.json` 中的 `hooks`
- rules 层：项目级 `.codex/rules/*.rules`
- runtime config 层：`.codex/settings.json`、`.codex/settings.local.json` 中的 `permissions` 等运行时规则

明确排除：

- `03-工作台/*`
- `00-项目总览/`
- `01-产品架构/`
- `02-PRD文档/`
- `90-归档记录/`

原因：本技能只审协作治理资产、项目级 rules 和运行时治理配置，不审过程内容，也不审业务主定义本身。

## 审计顺序

按以下顺序执行：

1. 先读取 `AGENTS.md`，确认顶层默认层是否承载了不该放在这里的内容。
2. 再读取 `CLAUDE.md`，确认它是否仍然只是引用或兜底，而不是形成独立规则集。
3. 读取高价值路径作用域规则；当前仓库默认先看：
   - `04-原型效果图/后台管理/README.md`
   - `04-原型效果图/后台管理/assets/README.md`
   - `06-工具脚本/README.md`
4. 读取现有 `.codex/skills` 下技能，检查哪些本应上移、下沉或拆分。
5. 读取 `06-工具脚本/README.md`，必要时再读相关 `.py` 脚本。
6. 先读取项目级 `.codex/rules/*.rules`；当前仓库相关 rules 默认应沉淀在这里，并优先在该目录下审计。
7. 再查看用户级 `~/.codex/rules/*.rules` 是否存在；用户级 rules 不作为主审计对象，只用于提示是否可能覆盖项目级意图、是否存在重复 prefix_rule、以及是否把本应项目私有的规则错误放在用户层。
8. 读取 `.codex/settings.json`，确认 runtime config 是否与当前治理分层一致。
9. 读取 `.codex/settings.local.json`，查看当前 hooks、permissions 和本地覆写是否合理。
10. 汇总分层判断、写法问题和迁移建议。

不要默认运行 `python 06-工具脚本/run_checks.py --scope ...`。只有用户明确提到检查结果、结构告警或希望结合 Sensor 时，才按需参考脚本结果；且脚本结果只能作为辅助输入，不能代替分层判断。

## 审计规则

按以下维度判断：

1. 顶层默认层是否合理。
检查 `AGENTS.md` / `CLAUDE.md` 是否混入局部规则、多步流程、实现细节、专题检查；是否遗漏了已经应该上移的通用约束。

2. 路径作用域层是否合理。
检查只对局部目录生效的规则是否被错误放到了全局；检查目录 `README.md` 是否承担了错误职责、重复顶层规则，或错误承担 workflow 职责。

3. skill 层是否合理。
检查 `.codex/skills` 中的技能是否真的是多步流程、专题检查或分支判断；检查哪些技能经验已经反复复用，应上移到 `AGENTS.md`；检查技能正文是否承担了目录规则、脚本说明或运行时规则职责。

4. 执行层是否合理。
检查哪些真实执行动作仍只是提醒；检查哪些内容应升级为脚本、CLI、MCP 或 checker，而不是继续停留在文档里。

5. hook 层是否合理。
检查哪些零例外动作仍没进入 `hooks`；检查现有 `hooks` 是否承担了不该承担的事，或与文档规则冲突。

6. rules 层是否合理。
检查项目相关命令控制是否优先写在项目级 `.codex/rules/`；检查是否把本应仓库私有的规则错误放到用户级；检查项目级与用户级是否存在重复、冲突或覆盖；检查 `.rules` 是否承担了不该承担的职责，例如本应进 `hooks`、`AGENTS.md`、`skill` 或 `settings*.json permissions` 的内容；检查是否存在过宽 prefix、规则漂移或职责串位。

7. runtime config 层是否合理。
检查 `.codex/settings*.json` 中的 `permissions`、技能调用许可、运行时配置是否与当前治理分层一致；检查是否和 `rules` / `hooks` 职责重叠，或存在配置漂移。

8. 写法是否合理。
检查重复、空话、过时、职责混杂、出口不清、文档或配置承担过重等问题。

## 输出格式

必须使用以下格式输出：

`【审计范围】`
简要说明本轮读了哪些层和哪些关键文件，并说明是否读取了项目级 `.codex/rules/` 以及是否发现用户级 `~/.codex/rules/`。

`【错层项清单】`
逐条列出：
- 审计对象
- 当前所在层
- 建议目标层
- 建议目标文件
- 迁移原因

`【治理升级候选】`
分别列出：
- 哪些应上移到 `AGENTS.md`
- 哪些应下沉到目录 `README.md`
- 哪些应升级为 `skill`
- 哪些应升级为 `hook`
- 哪些应升级为 `script/checker`
- 哪些应迁入项目级 `.codex/rules/`
- 哪些用户级 rules 仅提示冲突/覆盖风险
- 哪些应迁入或收紧到 `.codex/settings*.json` 的 runtime config

`【写法问题清单】`
列出不是错层、但需要收紧写法、配置方式或职责边界的问题。

`【本轮建议动作】`
只给 3 到 5 条本轮最值得做的动作，按优先级排序。

## 红线

- 不要把目录结构是否“好看”当作审计目标；只看是否放错层
- 不要默认运行 `run_checks.py`；只有用户明确要求结合 Sensor 时才按需参考
- 不要把单条经验细化成模板写作；那是 `data-governance-layer-triage` 的职责
- 不要把过程文档和业务主定义纳入本技能审计范围
- 不要把用户级 `~/.codex/rules/` 当成当前仓库相关 rules 的默认主承载位；项目相关 rules 默认应优先进入 `.codex/rules/`
- 不要把审计 skill 变成修改器；它只给建议，不直接改文件
