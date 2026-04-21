# DESIGN.md — 小型工程安全监管平台·后台管理端

> 视觉系统文档 for AI Agent。生成或修改后台管理原型时，请先阅读本文件，确保输出符合已确认的蓝白政务后台风格。

---

## 1. Visual Theme & Atmosphere

### 设计哲学
- **政务企业后台风**：稳重、专业、可信赖，强调信息层级清晰与操作效率。
- **蓝白主基调**：以品牌蓝为视觉锚点，白色面板承载内容，浅灰蓝作为画布背景，形成干净通透的整体氛围。
- **数据驱动**：页面以表格、筛选、表单为核心，信息密度适中，优先保证可读性与操作明确性。
- **规整克制**：拒绝营销感、海报感、过度装饰。圆角统一偏小，阴影轻量，过渡色简洁。

### 情绪关键词
`专业` · `清晰` · `稳重` · `高效` · `可信赖`

### 密度与留白
- 内容区卡片内部 padding: `22px 28px`
- 组件级间距: `10px ~ 18px`
- 卡片间间距: `14px`
- 表格行高: 紧凑但不拥挤，`th` `14px 12px` / `td` `12px`

---

## 2. Color Palette & Roles

| Token | Hex | Role |
|-------|-----|------|
| `--bg` | `#eef3f8` | 全局画布背景、底层表面 |
| `--panel` | `#ffffff` | 卡片、面板、弹窗、菜单背景 |
| `--line` | `#dde6f0` | 主分割线、卡片边框、表格外边框 |
| `--line-soft` | `#edf2f7` | 表格内细分割线、柔和分隔 |
| `--text` | `#223549` | 主标题、正文、核心文字 |
| `--muted` | `#748395` | 辅助文字、占位符、次要信息 |
| `--brand` | `#2f84e7` | 品牌主色：Primary 按钮、链接、激活态、强调条 |
| `--brand-deep` | `#194887` | 顶部导航渐变中间色 |
| `--brand-deeper` | `#123d79` | 顶部导航渐变起始色 |
| `--brand-light` | `#e8f2ff` | Tab 背景、轻量强调背景 |
| `--table-head` | `#dbe7f6` | 表格表头背景 |
| `--success` | `#20a36b` | 成功状态、通过、启用 |
| `--warning` | `#f3a73d` | 警告状态、待处理 |
| `--danger` | `#ef6a6a` | 错误状态、删除、危险操作 |
| `--disabled` | `#98a6b7` | 禁用文字、停用状态 |
| `--shadow` | `0 10px 22px rgba(18,51,95,0.06)` | 标准卡片阴影 |
| `--drawer-shadow` | `0 22px 46px rgba(17,46,86,0.22)` | 抽屉/侧板阴影 |

### 状态色板（Status & Tag）

| 语义 | 背景 | 边框 | 文字 | 圆点 |
|------|------|------|------|------|
| Success | `#f2fbf5` | `#bfe9cf` | `#138f52` | `#24ad67` |
| Warning | `#fff9ef` | `#f5dfbd` | `#b06f16` | `#e0a13a` |
| Error | `#fff4f3` | `#f3c9c5` | `#bf4b43` | `#e16056` |
| Muted | `#f5f7fa` | `#dce3ec` | `#7a8898` | `#9eaab7` |
| Info/Tag | `#f7fbff` | `#cfe0f6` | `#2c5cab` | — |

### 渐变使用场景
- **顶部导航栏**: `linear-gradient(90deg, #123d79 0%, #194887 44%, #235293 100%)`
- **全局页面背景**: `linear-gradient(180deg, #f5f8fc 0%, #eef3f8 100%)`
- **Tab 激活态背景**: `linear-gradient(180deg, #e7f2ff 0%, #d9ebff 100%)`

---

## 3. Typography Rules

### 字体栈
```
"Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif
```

### 字号层级表

| 层级 | Token | 字号 | 字重 | 行高 | 字间距 | 用途 |
|------|-------|------|------|------|--------|------|
| 页面大标题 | `--fs-title-lg` | `20px` | `700` | `1.25` | `0.3px` | 页面主标题 |
| 模块标题 | `--fs-title-md` | `18px` | `700` | `1.3` | — | 弹窗标题、卡片标题 |
| 小模块标题 | `--fs-title-sm` | `16px` | `700` | `1.3` | — | 列表标题、详情区块标题 |
| 正文/导航 | `--fs-body` / `--fs-nav` | `14px` | `400~600` | `1.5` | — | 正文、导航、按钮、表单标签 |
| 辅助说明 | `--fs-helper` | `13px` | `400` | `1.6~1.7` | — | 占位符、提示文案、面包屑 |
| 最小字 | `--fs-caption` | `12px` | `400~700` | `1.4` | — | 表格紧凑状态、标签、角标 |

### 字重定义
| Token | 值 | 用途 |
|-------|-----|------|
| `--fw-regular` | `400` | 正文、描述 |
| `--fw-medium` | `500` | 次要标签、次要按钮 |
| `--fw-semibold` | `600` | 导航、按钮、操作链接 |
| `--fw-bold` | `700` | 标题、表头、强调数字 |

### 标题装饰规范
- 卡片/列表标题左侧必须有 **4px 宽、18px 高、圆角 999px** 的蓝色竖条 (`--brand`)
- 标题与装饰条间距: `12px ~ 18px`

---

## 4. Component Stylings

### 4.1 按钮 (Button)

| 类型 | 高度 | Padding | 背景 | 边框 | 文字色 | 用途 |
|------|------|---------|------|------|--------|------|
| Primary | `32px` | `0 20px` | `--brand` (#2f84e7) | transparent | `#fff` | 主要操作：保存、查询、新增 |
| Ghost | `32px` | `0 20px` | `#fff` | `#d7dfe9` | `#5d6d82` | 次要操作：取消、重置、导出 |
| Danger | `32px` | `0 20px` | `#fff3f3` | `#f1caca` | `#d35f5f` | 危险操作：删除 |

- 按钮文字统一 `14px`，字重 `600`
- 按钮间水平间距: `10px ~ 14px`

### 4.2 输入框 / 下拉框 / 文本域

| 属性 | 值 |
|------|-----|
| 高度 | `32px` (标准) / `36px` (弹窗内) |
| 边框 | `1px solid #d7dfe9` |
| 背景 | `#fff` |
| 文字色 | `#42566b` / `#35475d` |
| 占位符 | `#95a5b8` |
| Focus 态 | 边框 `#2e7de0` + `box-shadow: 0 0 0 2px rgba(46,125,224,0.12)` |
| Padding | `0 12px` (input/select) / `8px 12px` (textarea) |
| 圆角 | `0` (直角) |

- 下拉框右侧有自定义三角箭头（CSS 绘制，非系统默认）
- 禁用态: 背景 `#f7f9fc`，文字 `#90a0b3`

### 4.3 表格 (Table)

| 属性 | 值 |
|------|-----|
| 表头背景 | `#dbe7f6` |
| 表头文字 | `#22344b`，字重 `700` |
| 表头 Padding | `14px 12px` |
| 单元格 Padding | `12px` |
| 单元格文字 | `#405164`，行高 `1.5` |
| 行分割线 | `1px solid #edf2f7` (soft) |
| 斑马纹 | 偶数行 `#fafcff` |
| 最小宽度 | `1280px` (列表页) |

### 4.4 卡片 / 面板

| 属性 | 值 |
|------|-----|
| 背景 | `#fff` |
| 阴影 | `0 10px 22px rgba(18,51,95,0.06)` |
| 边框 | 无（或 `1px solid #e6edf5` 用于 info-card） |
| Padding | `18px 0 16px` (列表骨架) / `22px 28px` (内容面板) |

### 4.5 标签 / 状态胶囊 (Tag / Status)

- 形状: 圆角 `999px`（全圆角胶囊）
- 高度: `min-height: 34px`
- Padding: `0 16px`
- 标签不带圆点，状态带左侧 `10px` 圆点
- 四种语义变体: success / warning / error / muted

### 4.6 表格内紧凑状态 (Table Status)

- 无背景、无边框、无胶囊
- 仅文字 + 左侧 `10px` 圆点
- 颜色跟随语义变体
- 用途: 列表页、导入结果表、字典管理表（保持列表密度）

### 4.7 弹窗 (Modal)

| 属性 | 标准 | Large |
|------|------|-------|
| 宽度 | `680px` | `860px` |
| 背景 | `#fff` | `#fff` |
| 阴影 | `0 24px 54px rgba(23,49,85,0.18)` | 同左 |
| 头部 | 标题左 + 关闭右，底部 `1px solid #edf2f7`，padding `16px 18px` | 同左 |
| 表单区 | 双列网格 `140px 1fr`，gap `18px 18px` | 同左 |
| 底部 | 按钮右对齐，`1px solid #edf2f7` 上边框 | 同左 |

### 4.8 顶部导航栏 (Topbar)

- 高度: `64px`
- 背景: `linear-gradient(90deg, #123d79 0%, #194887 44%, #235293 100%)`
- 左侧品牌区: 宽 `220px`，白字，品牌名 `18px bold`，竖排"运营端" `14px bold`
- 中部导航: 白字 `14px semibold`，active 态背景 `rgba(255,255,255,0.08)`
- 右侧用户区: 头像(36px 圆) + 用户名 + 下拉三角

### 4.9 侧边菜单 (Sidebar)

- 宽度: `208px`
- 背景: `#fff`
- 右边框: `1px solid #dee6ef`
- 菜单项: 高 `40px`，padding `0 18px`，`14px semibold`，颜色 `#44566c`
- Active 态: 背景 `--brand` (#2f84e7)，白字，底部内阴影 `inset 0 -1px 0 rgba(255,255,255,0.15)`

### 4.10 面包屑 (Breadcrumb)

- Padding: `6px 12px 8px`
- 颜色: `#4d5d70`
- 字号: `14px`
- 分隔符: `〉`

### 4.11 页签 (Tab)

- 高度: `32px`
- Padding: `0 28px`
- 背景: `linear-gradient(180deg, #e7f2ff 0%, #d9ebff 100%)`
- 文字: `--brand` (#2f84e7)，`14px semibold`
- Active 指示: 底部居中 `20px × 3px` 圆角条，`--brand` 色

### 4.12 轻提示 (Toast)

- 位置: 顶部居中 (`top: 70px`)
- 最小宽度: `280px`，最大 `680px`
- Padding: `12px 18px`
- 圆角: `8px`
- 背景: `#fff`，阴影 `0 6px 20px rgba(16,33,58,0.12)`
- 左侧 `20px` 圆角图标，四种语义色
- 自动消失，单条展示

### 4.13 抽屉 (Drawer)

- 宽度: `420px`
- 背景: `rgba(255,255,255,0.92)` + `backdrop-filter: blur(12px)`
- 阴影: `--drawer-shadow`
- 滑入动画: `transform 220ms ease`
- 头部: padding `18px 20px 14px`，底部边框 `1px solid #e7edf5`

### 4.14 页面底部操作栏 (Page Actions)

- 位置: 固定在工作区右下角 (`fixed; left: 236px; right: 12px; bottom: 0`)
- Padding: `14px 28px 16px`
- 上边框: `1px solid #e5edf6`
- 背景: `#fff`
- 阴影: `0 -8px 20px rgba(19,47,86,0.06)`
- 按钮右对齐，间距 `12px`
- **注意**: 内容区需使用 `.content-panel.has-page-actions` 预留底部空间，避免遮挡

### 4.15 操作列 (Row Actions)

- 横向排列，无间隙
- 按钮间以 `1px #d6e1ef` 竖线分隔
- 文字: `--brand` (#2f84e7)，`semibold`
- 危险操作: `#d75555`
- 首个按钮无左 padding

### 4.16 图片上传区

- 外容器: `1px dashed #c8d7e8` 边框，背景 `#fbfdff`，padding `18px`
- 拖拽区: `min-height: 180px`，居中排列
- 上传图标: `46px` 圆角方框，`1px dashed #c8d9ed` 边框
- 主文案: `14px semibold`，`#5f738c`
- 次文案: `13px`，`#7f8fa4`

### 4.17 缩略图网格

- 网格: `repeat(5, 1fr)`，gap `14px`
- 比例: `4:3`
- 边框: `1px solid #d9e2ec`
- 背景: `linear-gradient(135deg, #eff5fb 0%, #e5edf7 100%)`
- 删除按钮: 右上角 `20px` 圆形，背景 `rgba(239,106,106,0.94)`，白字
- 继续上传卡片: 虚线边框，`#f8fbff` 背景，`--brand` 色文字

---

## 5. Layout Principles

### 画布规格
- **标准桌面后台画布**: `1920px × 1080px`
- 页面根元素 `.frame`: 固定宽高，overflow hidden
- 实际开发时，外层可自适应，但原型图严格按此尺寸

### 全局布局结构
```
┌─────────────────────────────────────────┐  ← .topbar (64px)
│ 品牌区 (220px) │ 导航 (flex) │ 用户区 (220px) │
├──────────┬──────────────────────────────┤
│          │  .crumb (面包屑)              │
│ .sidebar │──────────────────────────────│  ← .workspace
│ (208px)  │  .surface.tabbar (页签)       │
│          │──────────────────────────────│
│          │  .content-panel (内容卡片)    │
│          │  ├─ 筛选区 / 列表骨架        │
│          │  ├─ 表格                     │
│          │  └─ 分页                     │
└──────────┴──────────────────────────────┘
```

### 间距体系

| Token | 值 | 用途 |
|-------|-----|------|
| xs | `6px ~ 8px` | 图标与文字间距、紧凑内边距 |
| sm | `10px ~ 12px` | 组件内部间隙、按钮间距 |
| md | `14px ~ 16px` | 卡片间距、表单行间距 |
| lg | `18px ~ 22px` | 卡片内边距、区块间距 |
| xl | `24px ~ 28px` | 大模块间距、内容面板 padding |

### 网格系统
- 详情页键值对: `grid-template-columns: 140px 1fr`
- 详情卡片双列: `grid-template-columns: repeat(2, minmax(0, 1fr))`
- 缩略图网格: `grid-template-columns: repeat(5, 1fr)`
- 弹窗表单: `grid-template-columns: 140px 1fr`

### 白色空间哲学
- 工作区背景与白色内容卡片形成**自然的层次对比**，无需重阴影即可区分层级。
- 信息区块之间以**浅灰蓝分割线** (`--line-soft`) 或**边框**分隔，避免过度依赖空白。
- 顶部导航与侧边菜单的深色/白色对比，自然框定工作区域。

---

## 6. Depth & Elevation

### 阴影层级

| 层级 | 阴影值 | 用途 |
|------|--------|------|
| Surface (L1) | `0 10px 22px rgba(18,51,95,0.06)` | 标准卡片、列表骨架、内容面板 |
| Modal (L2) | `0 24px 54px rgba(23,49,85,0.18)` | 弹窗、模态框 |
| Drawer (L3) | `0 22px 46px rgba(17,46,86,0.22)` | 右侧抽屉、侧滑面板 |
| Frame (L0) | `0 26px 56px rgba(16,44,82,0.12)` | 整个原型画框（仅效果图用） |
| Dropdown (L1.5) | `0 16px 36px rgba(16,44,82,0.14)` | 下拉面板、级联选择器、日期面板 |
| Toast (L2) | `0 6px 20px rgba(16,33,58,0.12)` | 轻提示 |
| Page Actions (L1) | `0 -8px 20px rgba(19,47,86,0.06)` | 底部固定操作栏（上阴影） |

### 表面层级 (Z-Index)

| 元素 | Z-Index |
|------|---------|
| 原型状态切换浮窗 | `9999` |
| Toast | `10020` |
| Topbar / Sidebar | 无（布局层） |
| 下拉面板 / 日期面板 | `40~60` |
| 弹窗遮罩 + 弹窗 | 布局层（相对定位） |
| Drawer | `25` |
| Page Actions (fixed) | `30` |

### 边框与圆角策略
- **全局默认圆角**: `0`（直角）——输入框、下拉框、卡片、表格均为直角，体现政务系统的严肃感。
- **胶囊圆角**: `999px` ——仅用于 Tag、Status、状态切换按钮、头像。
- **小圆角**: `8px` ——Toast、缩略图、上传区图标。
- **中等圆角**: `10px~14px` ——预览容器、组件展示盒（仅限内部预览使用，非业务界面）。

---

## 7. Do's and Don'ts

### Do
- ✅ 所有后台管理页面必须基于 **1920×1080** 画布。
- ✅ 优先复用已有公共组件（`proto-list-shell`、`proto-filter-bar`、`proto-modal-form` 等）。
- ✅ 表格、筛选器、按钮、分页等组件保持**业务系统风格**，规整稳定。
- ✅ 真实界面内容与功能说明必须分层；说明内容优先用抽屉、浮窗、侧边说明板承载。
- ✅ 配色、间距、控件风格延续本文件定义，保证同一项目风格统一。
- ✅ 列表导出必须复用完整的"导出选项 + 导出按钮"组合，不得只取一部分。
- ✅ 阻断态、空态、编辑受限态的按钮位置仍需服从共享布局规则。
- ✅ 当用户提供参考图片时，**严格复刻**，禁止擅自"优化"或"推断"。

### Don't
- ❌ 禁止做营销页、站点页、海报页式设计。
- ❌ 禁止把说明文案直接塞进界面主体。
- ❌ 禁止在已有公共组件能覆盖时，新增页面私有平行实现。
- ❌ 禁止使用纯黑色 (`#000`) 作为背景或文字色。
- ❌ 禁止在表格内使用胶囊背景的状态标签（应使用 `proto-table-status` 紧凑样式）。
- ❌ 禁止随意增大圆角或添加过多装饰性阴影。
- ❌ 禁止在原型效果图中使用真实业务敏感数据。
- ❌ 禁止将弹窗按钮塞回标题区、图片区或局部区块。

---

## 8. Responsive Behavior

> 本项目原型以 **桌面端 1920×1080 固定画布** 为主。以下为设计约束，非完整响应式方案。

### 断点策略
- **主要目标**: 1920px 桌面全屏
- **最小支持**: 1366px（内容区横向滚动）
- **表格**: 设置 `min-width: 1280px`，超出时横向滚动

### 触控目标
- 按钮/菜单项最小高度: `32px`（桌面鼠标操作标准）
- 操作链接/文字按钮: 保持 `14px` 以上，确保可点击区域

### 折叠策略
- 侧边栏: 固定 `208px`，不折叠
- 导航项: 超出时横向滚动或收纳入"更多"
- 筛选区: 自动换行 (`flex-wrap: wrap`)
- 表格列: 固定重要列，次要列允许横向滚动

---

## 9. Agent Prompt Guide

### 快速色值参考

```
主色:    #2f84e7  (按钮、链接、激活态)
深蓝:    #123d79  (导航渐变起始)
背景:    #eef3f8  (画布)
面板:    #ffffff  (卡片)
文字:    #223549  (主文字)
辅助:    #748395  (次要文字)
边框:    #dde6f0  (分割线)
表头:    #dbe7f6  (表格表头)
成功:    #20a36b
警告:    #f3a73d
危险:    #ef6a6a
禁用:    #98a6b7
```

### 可直接使用的 Prompt 模板

**模板 A：生成列表页**
> 基于 DESIGN.md 风格，生成一个 `[模块名]` 列表页原型。使用 `proto-list-shell` 骨架，包含：面包屑、页签、筛选条（搜索 + 下拉 + 日期范围 + 查询/重置）、列表标题与工具区（新增 + 批量导入 + 导出）、表格（含操作列）、分页。画布 1920×1080，蓝白政务后台风格。

**模板 B：生成表单/详情页**
> 基于 DESIGN.md 风格，生成一个 `[模块名]` 详情/编辑页原型。使用 `proto-detail-card` 展示键值对信息，表单区使用 `proto-field-row` 双列布局，底部固定 `page-actions`（取消 + 保存）。画布 1920×1080，蓝白政务后台风格。

**模板 C：生成弹窗**
> 基于 DESIGN.md 风格，生成一个 `[操作名]` 弹窗。使用 `proto-modal-form` 标准尺寸（680px），包含弹窗头部（标题 + 关闭）、表单区（双列网格 140px/1fr）、底部按钮（取消 + 保存，右对齐）。蓝白政务后台风格。

**模板 D：生成字典管理页**
> 基于 DESIGN.md 风格，生成一个 `[字典名]` 字典管理页原型。包含：面包屑、页签、表格（编码 + 名称 + 状态 + 操作列）、分页。状态列使用 `proto-table-status`。画布 1920×1080，蓝白政务后台风格。

### 组件映射速查

| 页面元素 | 组件名 | 来源 |
|---------|--------|------|
| 列表页骨架 | `proto-list-shell` | prototype.css |
| 筛选条 | `proto-filter-bar` | prototype.css |
| 日期范围选择 | `date-range-picker` | prototype.css |
| 列表标题区 | `proto-list-head` + `proto-list-title` + `proto-list-tools` | prototype.css |
| 表格 | `proto-table-wrap` + `table` | prototype.css |
| 分页 | `proto-pagination` | prototype.css |
| 操作列 | `proto-row-actions` + `proto-action` | prototype.css |
| 页面底部操作栏 | `page-actions` | prototype.css |
| 详情卡片 | `proto-detail-card` + `proto-detail-grid` | prototype.css |
| 弹窗表单 | `proto-modal-form` | prototype.css |
| 图片上传 | `proto-image-upload` | prototype.css |
| 缩略图网格 | `proto-image-grid` + `proto-image-card` | prototype.css |
| 状态胶囊 | `proto-status` | prototype.css |
| 表格状态 | `proto-table-status` | prototype.css |
| 轻提示 | `proto-toast` | prototype.css |
| 表单控件 | `proto-input` / `proto-select` / `proto-textarea` | prototype.css |
| 表单行 | `proto-field-row` + `proto-field-label` | prototype.css |
| 单选/多选 | `proto-radio-group` / `proto-checkbox-group` | prototype.css |
| 面包屑 | `.crumb` | prototype.css |
| 页签 | `.tabbar` + `.tab` / `.tab-chip` | prototype.css |

---

## 附录：文件位置

| 文件 | 路径 |
|------|------|
| 本设计文档 | `04-原型效果图/后台管理/DESIGN-admin.md` |
| 公共样式 | `04-原型效果图/后台管理/assets/prototype.css` |
| 公共脚本 | `04-原型效果图/后台管理/assets/prototype.js` |
| 布局脚本 | `04-原型效果图/后台管理/assets/prototype-layout.js` |
| 组件预览页 | `04-原型效果图/后台管理/后台管理-组件预览.html` |
| 组件说明 | `04-原型效果图/后台管理/assets/README.md` |
| 页面规范 | `04-原型效果图/后台管理/README.md` |
