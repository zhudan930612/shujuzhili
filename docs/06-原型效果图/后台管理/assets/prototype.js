document.querySelectorAll(".drawer-label").forEach((label) => {
  label.addEventListener("click", () => {
    const frame = label.closest(".frame");
    const drawer = frame && frame.querySelector(".drawer");
    if (drawer) drawer.classList.toggle("open");
  });
});

document.querySelectorAll("[data-view-scope]").forEach((scope) => {
  const buttons = Array.from(scope.querySelectorAll("[data-view-button]")).filter(
    (button) => button.closest("[data-view-scope]") === scope,
  );
  const panels = Array.from(scope.querySelectorAll("[data-view-panel]")).filter(
    (panel) => panel.closest("[data-view-scope]") === scope,
  );

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.getAttribute("data-view-button");

      buttons.forEach((item) => item.classList.toggle("active", item === button));
      panels.forEach((panel) => {
        panel.classList.toggle("active", panel.getAttribute("data-view-panel") === target);
      });
    });
  });
});

const protoRegionTree = [
  {
    label: "全国",
  },
  {
    label: "广东省",
    children: [
      {
        label: "深圳市",
        children: [
          { label: "南山区", children: [{ label: "粤海街道" }, { label: "南山街道" }, { label: "请选择" }] },
          { label: "福田区", children: [{ label: "福田街道" }, { label: "华强北街道" }, { label: "请选择" }] },
        ],
      },
      {
        label: "广州市",
        children: [
          { label: "天河区", children: [{ label: "天园街道" }, { label: "冼村街道" }, { label: "请选择" }] },
          { label: "越秀区", children: [{ label: "北京街道" }, { label: "请选择" }] },
        ],
      },
    ],
  },
  {
    label: "上海市",
    children: [
      {
        label: "上海市",
        children: [
          { label: "黄浦区", children: [{ label: "南京东路街道" }, { label: "请选择" }] },
          { label: "青浦区", children: [{ label: "夏阳街道" }, { label: "赵巷镇" }, { label: "请选择" }] },
        ],
      },
    ],
  },
];

function findProtoCascaderNode(nodes, label) {
  return nodes.find((node) => node.label === label);
}

function getProtoCascaderTree(cascader) {
  if (cascader.dataset.allowNational === "false") {
    return protoRegionTree.filter((node) => node.label !== "全国");
  }
  return protoRegionTree;
}

function getProtoCascaderLevels(tree, selectedPath, maxDepth) {
  const levels = [tree];
  let nodes = tree;
  selectedPath.slice(0, maxDepth).forEach((label, index) => {
    const node = findProtoCascaderNode(nodes, label);
    if (node && node.children && index + 1 < maxDepth) {
      levels.push(node.children);
      nodes = node.children;
    }
  });
  return levels;
}

function renderProtoCascader(cascader, selectedPath) {
  cascader.dataset.protoCascaderPath = JSON.stringify(selectedPath);
  const panel = cascader.querySelector(".proto-cascader-panel");
  if (!panel) return;

  const maxDepth = Number(cascader.dataset.cascaderDepth || 4);
  const levels = getProtoCascaderLevels(getProtoCascaderTree(cascader), selectedPath, maxDepth);
  panel.innerHTML = "";

  levels.forEach((nodes, levelIndex) => {
    const column = document.createElement("div");
    column.className = "proto-cascader-col";

    nodes.forEach((node) => {
      const option = document.createElement("button");
      option.className = "proto-cascader-option";
      option.type = "button";
      option.textContent = node.label;
      option.dataset.level = String(levelIndex);
      option.dataset.label = node.label;

      if (selectedPath[levelIndex] === node.label) {
        option.classList.add("active");
      }

      if (node.children && levelIndex + 1 < maxDepth) {
        const arrow = document.createElement("span");
        arrow.textContent = "›";
        option.appendChild(arrow);
      }

      column.appendChild(option);
    });

    panel.appendChild(column);
  });
}

function getProtoCascaderValue(cascader) {
  const text = cascader.querySelector(".proto-cascader-value");
  if (!text) return [];
  const value = text.textContent.trim();
  if (!value || value === "行政区域" || value === "适用地区" || value === "请选择") return [];
  return value.split("/").map((item) => item.trim()).filter(Boolean);
}

function setProtoCascaderValue(cascader, selectedPath) {
  const text = cascader.querySelector(".proto-cascader-value");
  if (!text) return;
  if (selectedPath.length === 0) {
    text.textContent = cascader.dataset.placeholder || "请选择";
    return;
  }
  text.textContent = selectedPath.join(" / ");
}

document.querySelectorAll("[data-proto-cascader]").forEach((cascader) => {
  const control = cascader.querySelector(".proto-cascader-control");
  const panel = cascader.querySelector(".proto-cascader-panel");
  if (!control || !panel) return;

  renderProtoCascader(cascader, getProtoCascaderValue(cascader));

  control.addEventListener("click", (event) => {
    event.stopPropagation();
    document.querySelectorAll(".proto-cascader.open").forEach((item) => {
      if (item !== cascader) item.classList.remove("open");
    });
    renderProtoCascader(cascader, getProtoCascaderValue(cascader));
    cascader.classList.toggle("open");
  });

  panel.addEventListener("click", (event) => {
    event.stopPropagation();
    const option = event.target.closest(".proto-cascader-option");
    if (!option) return;

    const maxDepth = Number(cascader.dataset.cascaderDepth || 4);
    const level = Number(option.dataset.level || 0);
    const label = option.dataset.label || "";
    const currentPath = JSON.parse(cascader.dataset.protoCascaderPath || "[]");
    const selectedPath = currentPath.slice(0, level);
    if (label !== "请选择") selectedPath[level] = label;

    const levels = getProtoCascaderLevels(getProtoCascaderTree(cascader), selectedPath, maxDepth);
    const node = findProtoCascaderNode(levels[level] || [], label);
    const hasNextLevel = node && node.children && level + 1 < maxDepth && label !== "全国";
    const requiredDepth = Number(cascader.dataset.requireDepth || 0);

    if (hasNextLevel) {
      renderProtoCascader(cascader, selectedPath);
      return;
    }

    const isLeaf = !node || !node.children;
    if (!isLeaf && requiredDepth > 0 && selectedPath.length < requiredDepth) {
      showProtoToast("行政区域必须选择到街镇层级", "warning");
      renderProtoCascader(cascader, selectedPath);
      return;
    }

    setProtoCascaderValue(cascader, selectedPath);
    cascader.classList.remove("open");
    renderProtoCascader(cascader, selectedPath);
  });
});

document.querySelectorAll(".date-range-picker").forEach((picker) => {
  const display = picker.querySelector(".date-range-control");
  const panel = picker.querySelector(".date-range-panel");
  const start = picker.querySelector('[data-role="start"]');
  const end = picker.querySelector('[data-role="end"]');
  const cancel = picker.querySelector('[data-action="cancel"]');
  const apply = picker.querySelector('[data-action="apply"]');

  const showNativePicker = (input) => {
    if (!input) return;
    input.focus();
    if (typeof input.showPicker === "function") {
      setTimeout(() => input.showPicker(), 0);
    }
  };

  const formatRange = () => {
    if (!start.value || !end.value) return "请选择日期范围";
    return `${start.value} 至 ${end.value}`;
  };

  const openPicker = () => {
    picker.classList.add("open");
    picker.dataset.step = "start";
    showNativePicker(start);
  };

  display.addEventListener("click", (event) => {
    event.stopPropagation();
    openPicker();
  });

  start.addEventListener("change", () => {
    picker.dataset.step = "end";
    showNativePicker(end);
  });

  panel.addEventListener("click", (event) => {
    event.stopPropagation();
  });

  cancel.addEventListener("click", () => {
    picker.classList.remove("open");
  });

  apply.addEventListener("click", () => {
    display.value = formatRange();
    picker.classList.remove("open");
  });
});

document.addEventListener("click", () => {
  document.querySelectorAll(".proto-cascader.open").forEach((cascader) => {
    cascader.classList.remove("open");
  });
  document.querySelectorAll(".date-range-picker.open").forEach((picker) => {
    picker.classList.remove("open");
  });
});

let protoToastTimer = null;

function ensureProtoToastStack() {
  let stack = document.querySelector('[data-proto-toast-runtime="1"]');
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "proto-toast-stack";
    stack.dataset.protoToastRuntime = "1";
    document.body.appendChild(stack);
  }
  return stack;
}

function showProtoToast(message, type = "info") {
  const stack = ensureProtoToastStack();
  stack.innerHTML = "";

  const toast = document.createElement("div");
  toast.className = "proto-toast";
  toast.dataset.type = type;

  const text = document.createElement("span");
  text.className = "proto-toast-text";
  text.textContent = message;

  toast.appendChild(text);
  stack.appendChild(toast);

  window.requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  if (protoToastTimer) {
    window.clearTimeout(protoToastTimer);
  }

  protoToastTimer = window.setTimeout(() => {
    toast.classList.remove("show");
    window.setTimeout(() => {
      if (toast.parentNode === stack) {
        stack.removeChild(toast);
      }
    }, 200);
  }, 2600);
}

function initProtoPagination(root) {
  const scope = root || document;
  scope.querySelectorAll(".proto-pagination").forEach((pagination) => {
    const pageSize =
      pagination.querySelector(".proto-page-size-select") ||
      pagination.querySelector(".proto-page-size");
    const pageInput =
      pagination.querySelector(".proto-page-jump-input") ||
      pagination.querySelector(".proto-page-input");
    if (pageSize && !pageSize.hasAttribute("aria-label")) {
      pageSize.setAttribute("aria-label", "每页条数");
    }
    if (pageInput && !pageInput.hasAttribute("aria-label")) {
      pageInput.setAttribute("aria-label", "跳转页码");
    }
  });
}

function initProtoRowActions(root) {
  const scope = root || document;
  scope.querySelectorAll(".proto-row-actions").forEach((group) => {
    const actions = Array.from(group.querySelectorAll(".proto-action"));
    actions.forEach((action, index) => {
      action.dataset.actionOrder = String(index + 1);
    });
  });
}

window.initProtoPagination = initProtoPagination;
window.initProtoRowActions = initProtoRowActions;
window.showProtoToast = showProtoToast;
