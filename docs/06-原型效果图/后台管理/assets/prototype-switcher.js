;(function () {
  var STATE_BAR_HIDDEN_CLASS = "prototype-state-hidden";
  var shortcutReady = false;

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function toArray(nodeList) {
    return Array.prototype.slice.call(nodeList || []);
  }

  function initPrototypeSwitch(root) {
    if (!root || root.dataset.prototypeSwitchReady === "1") return;

    if (!root.style.touchAction) root.style.touchAction = "none";
    if (!root.style.userSelect) root.style.userSelect = "none";
    if (!root.style.cursor) root.style.cursor = "move";

    var buttonSelector = root.dataset.prototypeButtonSelector || "[data-prototype-button]";
    var panelSelector = root.dataset.prototypePanelSelector || "[data-prototype-panel]";
    var scopeSelector = root.dataset.prototypePanelScope || "";
    var scope = scopeSelector ? document.querySelector(scopeSelector) : document;
    if (!scope) scope = document;

    var buttons = toArray(root.querySelectorAll(buttonSelector));
    var panels = toArray(scope.querySelectorAll(panelSelector));
    if (!buttons.length || !panels.length) return;

    function applyState(target) {
      panels.forEach(function (panel) {
        panel.classList.toggle("active", panel.dataset.prototypePanel === target);
      });
      buttons.forEach(function (button) {
        button.classList.toggle("active", button.dataset.prototypeButton === target);
      });
    }

    var firstActiveButton = buttons.find(function (button) {
      return button.classList.contains("active");
    });
    var firstActivePanel = panels.find(function (panel) {
      return panel.classList.contains("active");
    });
    var initialState =
      root.dataset.prototypeDefault ||
      (firstActiveButton && firstActiveButton.dataset.prototypeButton) ||
      (firstActivePanel && firstActivePanel.dataset.prototypePanel) ||
      panels[0].dataset.prototypePanel;

    if (initialState) applyState(initialState);

    var closeBtn = document.createElement("button");
    closeBtn.textContent = "×";
    closeBtn.className = "proto-state-close";
    closeBtn.title = "隐藏状态栏";
    closeBtn.addEventListener("click", function () {
      root.classList.add(STATE_BAR_HIDDEN_CLASS);
    });
    root.appendChild(closeBtn);

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        applyState(button.dataset.prototypeButton);
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    });

    if (root.dataset.prototypeDraggable === "false") {
      root.dataset.prototypeSwitchReady = "1";
      return;
    }

    var dragging = false;
    var pointerId = null;
    var offsetX = 0;
    var offsetY = 0;

    root.addEventListener("pointerdown", function (event) {
      if (event.button !== 0) return;
      if (event.target.closest("button, a, input, select, textarea, label")) return;

      var rect = root.getBoundingClientRect();
      dragging = true;
      pointerId = event.pointerId;
      offsetX = event.clientX - rect.left;
      offsetY = event.clientY - rect.top;

      root.style.left = rect.left + "px";
      root.style.top = rect.top + "px";
      root.style.right = "auto";
      root.style.bottom = "auto";
      root.setPointerCapture(pointerId);
    });

    root.addEventListener("pointermove", function (event) {
      if (!dragging || event.pointerId !== pointerId) return;

      var rect = root.getBoundingClientRect();
      var maxLeft = Math.max(window.innerWidth - rect.width, 0);
      var maxTop = Math.max(window.innerHeight - rect.height, 0);
      var nextLeft = clamp(event.clientX - offsetX, 0, maxLeft);
      var nextTop = clamp(event.clientY - offsetY, 0, maxTop);

      root.style.left = nextLeft + "px";
      root.style.top = nextTop + "px";
    });

    function stopDragging(event) {
      if (!dragging || event.pointerId !== pointerId) return;
      dragging = false;
      if (root.hasPointerCapture(pointerId)) {
        root.releasePointerCapture(pointerId);
      }
      pointerId = null;
    }

    root.addEventListener("pointerup", stopDragging);
    root.addEventListener("pointercancel", stopDragging);

    root.dataset.prototypeSwitchReady = "1";
  }

  function toggleAllPrototypeSwitches() {
    var switches = toArray(document.querySelectorAll("[data-prototype-switch]"));
    if (!switches.length) return;

    var shouldShow = switches.some(function (root) {
      return root.classList.contains(STATE_BAR_HIDDEN_CLASS);
    });

    switches.forEach(function (root) {
      root.classList.toggle(STATE_BAR_HIDDEN_CLASS, !shouldShow);
    });
  }

  function initPrototypeSwitchShortcut() {
    if (shortcutReady) return;
    shortcutReady = true;

    document.addEventListener("keydown", function (event) {
      if (event.key !== "F8") return;
      event.preventDefault();
      toggleAllPrototypeSwitches();
    });
  }

  function initAllPrototypeSwitches() {
    toArray(document.querySelectorAll("[data-prototype-switch]")).forEach(initPrototypeSwitch);
    initPrototypeSwitchShortcut();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAllPrototypeSwitches);
  } else {
    initAllPrototypeSwitches();
  }

  window.initPrototypeSwitch = initPrototypeSwitch;
  window.initAllPrototypeSwitches = initAllPrototypeSwitches;
  window.toggleAllPrototypeSwitches = toggleAllPrototypeSwitches;
})();
