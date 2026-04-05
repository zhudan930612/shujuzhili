# 后台管理通用组件原型资源

当前目录既是后台管理原型效果图的运行资源目录，也是后台管理原型的通用组件资源层。

## 当前职责
- `prototype.css` 负责后台原型的公共样式母版，例如顶部导航、侧栏、表格、表单、弹窗、抽屉、分页等。
- `prototype.js` 负责后台原型的公共交互母版，例如抽屉切换、视图切换、日期范围选择等。

## 使用原则
- 后台页面级 HTML 原型统一引用当前目录下的公共资源。
- 后台新增可复用的原型组件能力，优先沉淀到当前目录维护，而不是再单独扩散出一套并行的“通用组件”目录。
- Excel 模板、示例文件等原型配套附件不放在当前目录，统一归位到 [../模板文件/](../模板文件/)。
- App 端组件仍然独立维护在 [../../App/通用组件/](../../App/通用组件/)。

## 原型状态切换浮窗（公共组件）
- 公共脚本：`prototype-switcher.js`
- 作用：统一提供“状态切换 + 浮窗拖动”能力，避免每个页面重复写脚本。

### 页面接入方式
1. 在浮窗根节点添加 `data-prototype-switch`。
2. 按钮使用 `data-prototype-button="状态值"`。
3. 页面状态容器使用 `data-prototype-panel="状态值"`。
4. 页面底部引入：
   - `<script src="./assets/prototype.js"></script>`
   - `<script src="./assets/prototype-switcher.js"></script>`

### 可选配置
- `data-prototype-default="list"`：指定默认状态。
- `data-prototype-panel-scope="#page-id"`：指定状态面板查询范围（默认全页面）。
- `data-prototype-draggable="false"`：关闭拖拽能力。

## 原型布局组件（公共组件）
- 公共脚本：`prototype-layout.js`
- 作用：统一注入顶部导航和左侧菜单，避免每个页面重复维护相同结构。

### 页面接入方式
1. 给 `.frame` 添加布局配置属性：
   - `data-layout-module="project|inspection|knowledge|system|overview"`
   - `data-layout-top-active="..."`
   - `data-layout-side-preset="..."`
   - `data-layout-side-active="..."`
2. 在页面保留占位节点：
   - `<header class="topbar"></header>`
   - `<aside class="sidebar"></aside>`
3. 页面底部引入：
   - `<script src="./assets/prototype.js"></script>`
   - `<script src="./assets/prototype-layout.js"></script>`

### 预设说明
- 侧栏预设按模块集中维护在 `prototype-layout.js`：`project / inspection / knowledge / system / overview`。
- 页面仅传 key，不再重复写导航和菜单 DOM。