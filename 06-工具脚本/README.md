# 工具脚本

## 目录定位
当前目录用于存放仓库文档治理相关的本地辅助脚本。

脚本用于帮助 AI 自查与人工复核，不替代产品判断、PRD 评审或正式验收。
脚本目标是让 AI 快速发现结构性问题，并给出可执行修复建议。

## 主要内容
| 文件 | 用途 |
|------|------|
| [check_docs.py](check_docs.py) | 文档基础机械检查脚本 |
| [check_docs_tests.py](check_docs_tests.py) | `check_docs.py` 的单元测试 |

## 使用方式
在仓库根目录运行：

```powershell
python 06-工具脚本/check_docs.py
```

运行脚本测试：

```powershell
python 06-工具脚本/check_docs_tests.py
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

## 维护约定
- 脚本只读，不自动修改仓库文件。
- 新增检查项时，优先给出明确错误原因和修复建议。
- 新增检查项必须包含 `Why` 和 `Fix`，让 AI 能理解风险并执行修复。
- 涉及业务语义、产品取舍或页面规则的判断，不放进脚本硬编码。
- 脚本发现 `WARN` 时不阻断任务结束，但需要在任务收尾说明中交代原因。
