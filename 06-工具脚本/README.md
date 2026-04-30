# 工具脚本

## 目录定位
当前目录用于存放仓库文档治理相关的本地辅助脚本。

脚本用于帮助 AI 自查与人工复核，不替代产品判断、PRD 评审或正式验收。
脚本目标是让 AI 快速发现结构性问题，并给出可执行修复建议。

## Guide / Sensor 边界
- Guide 是行动前引导，包括 [../AGENTS.md](../AGENTS.md)、目录 README、任务执行协议、PRD、业务上下文。
- Sensor 是行动后反馈，包括 [check_docs.py](check_docs.py)、[check_docs_tests.py](check_docs_tests.py)、任务完成检查、AI 自查与人工复核。
- [check_docs.py](check_docs.py) 属于计算性 Sensor，只检查明确结构问题。
- [check_prototypes.py](check_prototypes.py) 属于原型类 Sensor，检查后台原型的共享组件复用和共享脚本接入。
- 业务评审属于推理性 Sensor，不放入脚本硬编码。
- 工具脚本只做结构性背压，不替代人工确认点。
- 脚本通过只代表结构闭环基本成立，不代表业务结论、评审质量或方案取舍已经正确。
- 页面需求里的权限说明只负责页面表现，不负责角色映射主定义；角色到页面/操作/数据范围权限统一以 `02-PRD文档/后台管理/系统管理.md` 为准。

## 主要内容
| 文件 | 用途 |
|------|------|
| [check_docs.py](check_docs.py) | 文档基础机械检查脚本 |
| [check_docs_tests.py](check_docs_tests.py) | `check_docs.py` 的单元测试 |
| [check_prototypes.py](check_prototypes.py) | 后台原型共享组件与共享脚本检查脚本 |
| [check_prototypes_tests.py](check_prototypes_tests.py) | `check_prototypes.py` 的单元测试 |

## 使用方式
在仓库根目录运行：

```powershell
python 06-工具脚本/check_docs.py
```

运行脚本测试：

```powershell
python 06-工具脚本/check_docs_tests.py
python 06-工具脚本/check_prototypes.py
python 06-工具脚本/check_prototypes_tests.py
```

## 当前检查项
| 检查项 | 结果类型 |
|--------|----------|
| 必要 harness 文件是否存在 | ERROR |
| `AGENTS.md` 是否超过 120 行 | ERROR |
| 是否出现旧版 ASCII 草图命名 | ERROR |
| `AGENTS.md` 是否承载专题细则 | ERROR |
| Markdown 相对链接是否有效 | ERROR |
| `当前需求沟通文档.md` 是否超过 30000 bytes | WARN |
| 根目录是否存在非预期一级目录 | WARN |
| 一级目录 README 是否包含基础章节 | WARN |
| `AGENTS.md` 是否覆盖已有一级目录 | ERROR |
| 是否引用不存在的根 README | WARN |
| `任务完成检查.md` 是否引用检查脚本 | ERROR |
| `当前需求沟通文档.md` 是否维护拆回正式文档清单 | WARN |
| 拆回正式文档清单状态值是否合法 | WARN |
| `已拆回` 条目是否带主定义文档路径 | WARN |
| `已归档` 条目是否带归档记录路径 | WARN |
| `任务完成检查.md` 是否包含收尾闭环门 | WARN |
| `评审记录.md` 是否符合默认骨架 | WARN |
| `03-工作台/README.md` 是否体现协议驱动区 | WARN |
| 过程文档是否重复承载“权限矩阵式”主定义 | WARN |
| 后台模块 PRD 是否包含页面目录索引和统一页面骨架 | WARN |
| 正式 PRD 是否残留页面 ASCII 草图正文 | WARN |
| 确认类弹窗是否具备最小结构 | WARN |
| 页面级 PRD 是否出现开放口径、扩展字段、否定式冗余、暂缓区正式规则 | WARN |
| 同一页面内同一图片对象是否出现互斥规则模式 | WARN |
| 原型页是否接入 `prototype.css` | ERROR |
| 原型页是否接入 `prototype-layout.js` / `prototype-switcher.js` | WARN |
| 列表页是否复用 `proto-list-shell` | WARN |
| 页面底部操作是否复用 `page-actions + has-page-actions` | WARN |
| 多操作列是否复用 `proto-row-actions` | WARN |

## 维护约定
- 脚本只读，不自动修改仓库文件。
- `ERROR` 表示结构性阻断，任务结束前必须修复。
- `WARN` 表示上下文腐烂或潜在风险，可保留但必须说明。
- 脚本只处理结构性背压，不替代业务决策门。
- 新增检查项时，优先给出明确错误原因和修复建议。
- 新增检查项必须包含 `Why` 和 `Fix`，让 AI 能理解风险并执行修复。
- 新检查项优先从重复出现的 AI 漏改、断链、术语漂移、目录漂移中沉淀。
- 已经犯过且明确不该再次发生的错误，应优先判断是否要升级为模板或脚本检查，而不是只写进经验说明。
- 沟通落地检查只判断结构闭环、状态和链接痕迹，不判断业务拆回是否正确。
- 权限相关检查只提示“主定义漂移”风险，不判断业务角色建议是否合理，也不裁决具体权限点设计。
- 涉及业务语义、产品取舍或页面规则的判断，不放进脚本硬编码。
- 脚本发现 `WARN` 时不阻断任务结束，但需要在任务收尾说明中交代原因。
- `当前需求沟通文档.md` 过大 warning 的默认处理动作是拆回或归档，不是长期容忍。
