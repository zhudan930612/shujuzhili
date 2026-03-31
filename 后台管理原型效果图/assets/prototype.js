document.querySelectorAll(".drawer-label").forEach((label) => {
  label.addEventListener("click", () => {
    const frame = label.closest(".frame");
    const drawer = frame && frame.querySelector(".drawer");
    if (drawer) drawer.classList.toggle("open");
  });
});

document.querySelectorAll("[data-view-scope]").forEach((scope) => {
  const buttons = scope.querySelectorAll("[data-view-button]");
  const panels = scope.querySelectorAll("[data-view-panel]");

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