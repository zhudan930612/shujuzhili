;(function () {
  var TOP_NAV_ITEMS = [
    { key: "home", label: "⌂ 首页" },
    { key: "project", label: "▣ 项目管理" },
    { key: "inspection", label: "◎ 巡查管理" },
    { key: "annotation", label: "▧ 标注质检" },
    { key: "user", label: "♙ 用户中心" },
    { key: "knowledge", label: "◫ 知识库管理" },
    { key: "system", label: "⚙ 系统管理" },
  ];

  var SIDE_PRESETS = {
    project: [
      { key: "project", label: "▣ 项目管理" },
      { key: "inspection", label: "◎ 巡查记录管理" },
      { key: "knowledge", label: "◫ 知识库管理" },
    ],
    inspection: [
      { key: "inspection", label: "◎ 巡查记录管理" },
      { key: "project", label: "▣ 项目管理" },
      { key: "knowledge", label: "◫ 知识库管理" },
    ],
    annotation: [
      { key: "annotation-task", label: "▧ 标注任务" },
      { key: "annotation-qc", label: "▤ 质检任务" },
      { key: "quality-pool", label: "▣ 高质量数据池" },
      { key: "annotation-category", label: "◫ 标注要素类别库" },
    ],
    user: [
      { key: "inspection-org", label: "▤ 巡检单位库" },
      { key: "inspector", label: "♙ 巡查人员库" },
      { key: "insurer", label: "▣ 保险机构库" },
      { key: "contractor", label: "▣ 施工单位库" },
    ],
    knowledge: [
      { key: "hazard", label: "▣ 隐患库管理" },
      { key: "law", label: "▤ 法规库管理" },
      { key: "inspection", label: "◎ 巡查记录管理" },
    ],
    system: [
      { key: "dictionary", label: "▤ 字典管理" },
      { key: "user", label: "◧ 用户管理" },
      { key: "role", label: "◎ 角色权限" },
      { key: "log", label: "◫ 操作日志" },
    ],
    overview: [
      { key: "overview", label: "▣ 后台原型总览" },
      { key: "project", label: "▤ 项目管理" },
      { key: "inspection", label: "◎ 巡查管理" },
      { key: "annotation", label: "▧ 标注质检" },
      { key: "user", label: "♙ 用户中心" },
      { key: "knowledge", label: "◫ 知识库管理" },
    ],
  };

  function renderTopbar(activeKey) {
    var navHtml = TOP_NAV_ITEMS.map(function (item) {
      var activeClass = item.key === activeKey ? " active" : "";
      return '<div class="nav-item' + activeClass + '">' + item.label + "</div>";
    }).join("");

    return (
      '<div class="brand-box">' +
      '<div class="brand-text">小型工程全域全量<br />安全监管平台</div>' +
      '<div class="terminal-text">运<br />营<br />端</div>' +
      "</div>" +
      '<nav class="nav">' +
      navHtml +
      "</nav>" +
      '<div class="user-box">' +
      '<div class="avatar"></div>' +
      '<div class="user-name">超级管理员</div>' +
      '<button class="user-dropdown-toggle" type="button" aria-label="展开用户菜单">▾</button>' +
      "</div>"
    );
  }

  function renderSidebar(presetKey, activeKey) {
    var preset = SIDE_PRESETS[presetKey] || SIDE_PRESETS.project;
    return preset
      .map(function (item) {
        var activeClass = item.key === activeKey ? " active" : "";
        return '<div class="menu-item' + activeClass + '">' + item.label + "</div>";
      })
      .join("");
  }

  function initFrameLayout(frame) {
    if (!frame || frame.dataset.layoutReady === "1") return;

    var moduleKey = frame.dataset.layoutModule || "project";
    var topActive = frame.dataset.layoutTopActive || moduleKey;
    var sidePreset = frame.dataset.layoutSidePreset || moduleKey;
    var sideActive = frame.dataset.layoutSideActive || moduleKey;

    var topbar = frame.querySelector(".topbar");
    if (topbar) {
      topbar.innerHTML = renderTopbar(topActive);
    }

    var sidebar = frame.querySelector(".sidebar");
    if (sidebar) {
      sidebar.innerHTML = renderSidebar(sidePreset, sideActive);
    }

    frame.dataset.layoutReady = "1";
  }

  function initAllLayouts() {
    var frames = document.querySelectorAll("[data-layout-module]");
    Array.prototype.forEach.call(frames, initFrameLayout);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAllLayouts);
  } else {
    initAllLayouts();
  }

  window.initPrototypeLayout = initFrameLayout;
  window.initAllPrototypeLayouts = initAllLayouts;
})();
