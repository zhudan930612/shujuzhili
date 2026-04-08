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
