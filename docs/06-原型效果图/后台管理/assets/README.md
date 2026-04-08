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

### 巡查管理状态键示例
- `巡查管理-上传巡查记录页.html`：
  - `empty` / `uploaded` / `save-confirm`
- `巡查管理-巡查记录详情页.html`：
  - `detail` / `batch` / `delete-confirm` / `delete-blocked`

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

## Proto 组件接入契约（新增）
本节为“先建设组件、后替换页面”阶段的统一约定。

### 组件清单
- `proto-filter-bar`：统一筛选条容器。
- `date-range-picker`：统一日期范围选择器。
- `proto-list-shell`：列表页骨架（含标题区、工具区、表格区）。
- `proto-pagination`：统一分页（默认右下对齐）。
- `proto-row-actions`：统一操作列（动作顺序与分隔规范）。
- `prototype-state-bar`：统一浮窗状态栏样式。
- `proto-state-bar`：浮窗状态栏兼容类名，仅用于存量页面过渡。
- `proto-tag / proto-status`：统一业务标签与胶囊状态组件。
- `proto-table-status`：统一表格内紧凑状态组件。
- `proto-toast`：统一轻提示组件（顶部居中、单条、自动消失）。
- `proto-detail-card / proto-detail-grid / proto-detail-label / proto-detail-value`：统一基础详情展示卡片。
- `proto-image-upload / proto-image-grid / proto-image-card`：统一上传图片、缩略图和删除按钮表现层。
- `proto-modal-form`：统一弹窗表单模板（含遮罩、居中、footer 右下按钮）。
- `proto-input / proto-select / proto-textarea / proto-radio-group / proto-checkbox-group`：统一表单控件。
- `proto-field-row / proto-field-label`：统一表单行布局与标签宽度。

### 接入结构（最小示例）
```html
<section class="proto-list-shell">
  <div class="proto-list-head">
    <h3 class="proto-list-title">项目列表</h3>
    <div class="proto-list-tools"></div>
  </div>
  <div class="proto-table-wrap">...</div>
  <div class="proto-pagination">...</div>
</section>
```

```html
<div class="prototype-state-bar" data-prototype-switch>
  <button class="active" data-prototype-button="list">列表态</button>
  <button data-prototype-button="create">新增弹窗</button>
</div>
```

```html
<section class="proto-modal-form-stage">
  <div class="proto-modal-form">
    <div class="proto-modal-head">...</div>
    <div class="proto-modal-body">
      <div class="proto-modal-grid">...</div>
    </div>
    <div class="proto-modal-foot">...</div>
  </div>
</section>
```

```html
<script src="./assets/prototype.js"></script>
<script>
  showProtoToast("保存成功", "success");
</script>
```

```html
<div class="badge-row">
  <span class="proto-tag">小型工程</span>
  <span class="proto-status" data-variant="success">已巡查</span>
  <span class="proto-status" data-variant="muted">未巡查</span>
</div>
```

```html
<td><span class="proto-table-status" data-variant="success">启用</span></td>
<td><span class="proto-table-status" data-variant="muted">停用</span></td>
<td><span class="proto-table-status" data-variant="error">错误</span></td>
```

```html
<section class="proto-detail-card">
  <h3 class="proto-detail-card-title">基础信息</h3>
  <div class="proto-detail-card-body">
    <div class="proto-detail-grid">
      <div class="proto-detail-label">隐患编码</div>
      <div class="proto-detail-value">JZ-FALL-EDGE-0001</div>
      <div class="proto-detail-label">行业域</div>
      <div class="proto-detail-value">建筑施工</div>
      <div class="proto-detail-label">隐患名称</div>
      <div class="proto-detail-value">防护栏杆高度不足</div>
      <div class="proto-detail-label">整改措施</div>
      <div class="proto-detail-value">加高栏杆至1.2m以上，确保横杆符合要求</div>
    </div>
  </div>
</section>
```

```html
<div class="proto-image-upload">
  <div class="proto-image-upload-dropzone">
    <div class="proto-image-upload-icon">＋</div>
    <div class="proto-image-upload-text">点击上传 / 拖拽上传</div>
    <div class="proto-image-upload-note">支持 jpg / png，单张不得超过 5MB</div>
  </div>
</div>

<div class="proto-image-grid">
  <div class="proto-image-card"><span class="proto-image-card-delete">×</span>图1缩略</div>
  <div class="proto-image-card"><span class="proto-image-card-delete">×</span>图2缩略</div>
  <div class="proto-image-card upload">＋ 点击上传</div>
</div>
```

### 图片组件边界
- 本次图片组件只负责表现层，不负责上传、删除、确认保存等业务流程。
- 删除图片能力当前仅表示“删除按钮样式”，不包含删除确认弹窗。
- 批量管理、上传后不可追加、保存限制等规则仍由业务页面单独表达。

### 可选 JS 初始化
- `initProtoPagination(root?)`
- `initProtoRowActions(root?)`
- `showProtoToast(message, type?)`
- 说明：仅在页面使用 `proto-*` 类名时生效，不会改动旧页面现状。

```html
<script src="./assets/prototype.js"></script>
<script>
  initProtoPagination();
  initProtoRowActions();
</script>
```

### 禁止项
- 禁止在页面内再写“分页右下对齐补丁脚本”。
- 浮窗状态栏基础视觉样式统一由 `prototype.css` 提供。
- 禁止在页面内联重复定义浮窗状态栏样式（统一使用 `prototype-state-bar`，`proto-state-bar` 仅保留兼容）。
- 页面只允许通过数据属性控制浮窗行为，不允许覆盖基础视觉样式。
- 禁止为操作列追加不一致的分隔规则（统一使用 `proto-row-actions`）。
- 禁止在新页面继续混用零散表单类名（`input/select/textarea` 等应优先使用 `proto-*` 表单控件类）。

### 表单控件最小示例
```html
<div class="proto-field-row">
  <div class="proto-field-label">法规名称 *</div>
  <input class="proto-input" type="text" placeholder="请输入法规名称" />

  <div class="proto-field-label">法规类型 *</div>
  <select class="proto-select">
    <option>国家标准</option>
    <option selected>行业标准</option>
  </select>

  <div class="proto-field-label">状态 *</div>
  <div class="proto-radio-group">
    <label class="proto-radio"><input type="radio" name="status" checked /> 启用</label>
    <label class="proto-radio"><input type="radio" name="status" /> 停用</label>
  </div>

  <div class="proto-field-label">适用范围</div>
  <div class="proto-checkbox-group">
    <label class="proto-checkbox"><input type="checkbox" checked /> 建筑施工</label>
    <label class="proto-checkbox"><input type="checkbox" /> 危险化学品</label>
  </div>
</div>
```
