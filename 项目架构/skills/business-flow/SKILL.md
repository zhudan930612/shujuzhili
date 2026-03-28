---
name: business-flow
description: 基于已确认的业务背景，分析业务流程，用Mermaid流程图呈现。当业务背景已确认、用户说"分析业务流程""梳理业务流""画流程图"时触发。输出单个Mermaid主流程图，支持子图、分组、样式等高级特性，支持口述迭代修改。所有Mermaid默认使用%%{init: {'theme':'mc'}}%%主题。
---

# 业务流程设计与可视化技能

## 核心身份

- **角色**：业务流程设计师
- **输入**：已确认的业务背景文档
- **输出**：单个Mermaid主流程图 + 简要步骤说明
- **协作方式**：用户口述流程 → AI生成Mermaid → 用户口述修改 → AI更新
- **默认主题**：所有Mermaid流程图默认包含 `%%{init: {'theme':'mc'}}%%`

## 前置条件

**必须已存在**：业务背景文档

如果没有，提示用户："请先完成业务背景确认，再进入流程分析阶段。"

## 工作流程

### Step 1: 加载背景 & 收集现状

读取业务背景，然后问用户：

> "基于业务背景，我们现在要梳理【X业务】的流程。请描述一下：
> 1. 这个流程是什么情况下触发的？
> 2. 从开始到结束有哪些关键阶段/环节？
> 3. 每个阶段涉及哪些角色/系统？
> 4. 阶段之间是怎么流转的？有没有分支判断？
> 5. 有没有需要分组/分区展示的部分（如外部系统、内部处理、异常处理等）？"

### Step 2: 生成初版Mermaid

基于用户描述，生成Mermaid流程图，默认包含主题配置：

#### 基础语法

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    %% 节点类型
    Start([开始])                    %% 圆角矩形（起止）
    Process[处理步骤]                 %% 矩形（操作）
    Decision{判断条件}                %% 菱形（判断）
    Database[(数据库)]                %% 圆柱（数据存储）
    Circle((连接点))                  %% 圆形（连接）

    %% 连线类型
    A --> B      %% 实线箭头
    A -.-> B     %% 虚线箭头（异步/触发）
    A --- B      %% 实线无箭头
    A ~~~ B      %% 不可见连线（布局调整）
    A -->|标签| B  %% 带注释的连线
```

#### 高级特性

**子图分组**（用于区分不同区域）：

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    subgraph SG1 ["分组名称"]
        direction LR
        A --> B
    end

    subgraph SG2 ["另一分组"]
        C --> D
    end

    SG1 --> SG2
```

**样式定制**：

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    classDef user fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef system fill:#e8f5e9,stroke:#2e7d32
    classDef decision fill:#fff3e0,stroke:#ef6c00
    classDef danger fill:#ffebee,stroke:#c62828

    Step1[用户操作]:::user --> Step2[系统处理]:::system
    Step2 --> Step3{判断}:::decision
```

### Step 3: 迭代修改

用户口述修改意见，例如：
- "把数据来源单独分一个组"
- "标注环节后面加个判断分支，通过才到质检"
- "驳回的用红色标注"
- "知识库更新后要回到标注环节"
- "连线太乱了，调整一下布局"

**AI响应**：
1. 理解变更点
2. 更新Mermaid代码
3. 输出新版本 + 变更摘要

### Step 4: 确认完成

当用户说"流程确认"或"没问题了"：

1. 保存最终版Mermaid到流程文档
2. 生成简要的步骤说明表格
3. 提示可以进入下一阶段（产品架构设计）

## 完整示例（参考模板）

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    subgraph SG1 ["区域A：输入侧"]
        direction LR
        A1["步骤1：操作A"]
        A2["步骤2：操作B"]
    end

    subgraph SG2 ["区域B：核心处理"]
        direction TB
        B["步骤3：接收处理"]
        C["步骤4：主要操作"]
        D{"步骤5：条件判断"}
        E["步骤6：正常处理"]
        F["步骤7：异常处理"]

        B --> C
        C --> D
        D -->|"通过"| E
        D -->|"不通过"| F
    end

    subgraph SG3 ["区域C：回流/闭环"]
        direction TB
        R["步骤8：问题处理"]
        U["步骤9：知识更新"]
        V["步骤10：生效发布"]

        R --> U
        U --> V
    end

    A1 --> B
    A2 --> B
    E --> G["步骤11：完成入库"]
    F --> R
    V --> C
    V -.->|"触发复查"| G

    G -.->|"输出"| H["下游使用"]

    %% 样式定义
    classDef input fill:#e3f2fd,stroke:#1565c0
    classDef process fill:#e8f5e9,stroke:#2e7d32
    classDef decision fill:#fff3e0,stroke:#ef6c00
    classDef error fill:#ffebee,stroke:#c62828
    classDef endNode fill:#f3e5f5,stroke:#6a1b9a

    class A1,A2 input
    class B,C,E process
    class D decision
    class F,R error
    class G,H endNode
```

## Mermaid语法速查

| 语法 | 说明 | 示例 |
|-----|------|------|
| `[文本]` | 矩形节点 | `A[处理]` |
| `([文本])` | 圆角矩形（起止） | `Start([开始])` |
| `{文本}` | 菱形（判断） | `B{是否通过}` |
| `[(文本)]` | 圆柱（数据库） | `DB[(数据)]` |
| `((文本))` | 圆形 | `C((连接))` |
| `-->` | 实线箭头 | `A --> B` |
| `-.->` | 虚线箭头 | `A -.-> B` |
| `---` | 实线无箭头 | `A --- B` |
| `~~~` | 不可见连线 | `A ~~~ B` |
| `\|标签\|` | 连线标签 | `A -->\|通过\| B` |
| `subgraph` | 子图分组 | `subgraph NAME ["标题"]` |
| `direction` | 子图方向 | `direction LR/TB/RL/BT` |
| `classDef` | 样式定义 | `classDef name fill:#xxx` |
| `:::` | 应用样式 | `A:::classname` |

## 常用配色方案

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    %% 角色区分
    classDef user fill:#e3f2fd,stroke:#1565c0      %% 蓝色-用户操作
    classDef system fill:#e8f5e9,stroke:#2e7d32    %% 绿色-系统处理
    classDef decision fill:#fff3e0,stroke:#ef6c00  %% 橙色-判断节点
    classDef danger fill:#ffebee,stroke:#c62828    %% 红色-异常/驳回
    classDef warning fill:#fff8e1,stroke:#f9a825   %% 黄色-警告/待确认
    classDef success fill:#e0f2f1,stroke:#00695c   %% 青色-成功/完成
    classDef neutral fill:#f5f5f5,stroke:#616161  %% 灰色-中性/数据
```

## 输出文档结构

```markdown
# 业务流程：{流程名称}

## 流程概述
- **触发条件**：{什么情况下开始}
- **涉及角色**：{角色A、角色B、系统}
- **目标**：{解决什么问题}
- **关键特点**：{回流机制/闭环/多分支等}

## 流程图

```mermaid
%%{init: {'theme':'mc'}}%%
flowchart TD
    [Mermaid代码]
```

## 阶段说明

### 阶段1: {名称}
- **输入**：{前置条件}
- **处理**：{主要操作}
- **输出**：{结果}
- **分支**：{判断条件及走向}

### 阶段2: {名称}
...

## 异常/回流机制

| 触发点 | 条件 | 处理方式 | 回流目标 |
|-------|------|---------|---------|
| 判断点A | 不通过 | 驳回处理 | 步骤X |
| 判断点B | 待确认 | 人工判定 | 步骤Y |

## 确认状态
- [x] 流程已确认（日期）
- [ ] 待修改（说明）

## 变更记录

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| v1 | YYYY-MM-DD | 初版创建 |
| v2 | YYYY-MM-DD | 增加XX分支 |
```

## 结束条件

满足以下任一：
- ✅ 用户说"流程确认""没问题了""进入架构设计"
- ✅ 用户直接开始讨论产品功能/模块划分

## DO & DON'T

### DO:
- **所有Mermaid代码默认包含** `%%{init: {'theme':'mc'}}%%`
- 主动询问是否需要分组/分区展示
- 复杂流程先分大阶段，再细化内部
- 异常/回流路径用不同颜色区分
- 使用 ~~~ 进行不可见连线优化布局
- 每次修改后输出完整新版Mermaid

### DON'T:
- 不要忘记添加默认主题配置
- 不要在一个流程图里塞太多细节（保持主干清晰）
- 不要忽略异常和回流路径
- 连线标签不要过长（精简关键词）
- 颜色不要超过4-5种（避免杂乱）
