/* Trail form — searchable place picker that builds an ordered route.
   Selected places are numbered in the order they were added; the hidden
   #place_ids input carries numeric place ids in that order for the server. */

(function () {
  const root = document.querySelector(".trail-picker");
  const input = document.getElementById("place_ids");
  if (!root || !input) return;

  const places = window.PLACES_FOR_TRAIL || [];
  const selectedIds = (root.dataset.selected || "[]").replace(/&quot;/g, '"');
  let selected = [];
  try {
    const raw = JSON.parse(selectedIds);
    selected = raw.map((id) => places.find((p) => String(p.dbId) === String(id))).filter(Boolean);
  } catch (e) {
    selected = [];
  }

  const filterInput = root.querySelector(".trail-picker-filter");
  const availableList = root.querySelector(".trail-picker-list");
  const stopsEl = root.querySelector(".trail-picker-stops");
  const countEl = root.querySelector(".trail-picker-count");

  function selectedIdsSet() {
    return new Set(selected.map((p) => p.dbId));
  }

  function renderAvailable() {
    const q = (filterInput.value || "").trim().toLowerCase();
    const inRoute = selectedIdsSet();
    const visible = places.filter(
      (p) =>
        !inRoute.has(p.dbId) &&
        (!q ||
          p.name.toLowerCase().includes(q) ||
          p.governorate.toLowerCase().includes(q) ||
          (p.summary || "").toLowerCase().includes(q))
    );
    if (!visible.length) {
      availableList.innerHTML =
        '<div class="trail-picker-empty">' +
        (q ? "No places match your search." : "All places are on your route.") +
        "</div>";
      return;
    }
    availableList.innerHTML = visible
      .map(
        (p) => `
      <button type="button" class="trail-picker-item" data-id="${p.dbId}">
        <img src="${esc(p.image)}" alt="" loading="lazy">
        <span class="trail-picker-item-name">
          <b>${esc(p.name)}</b>
          <small>${esc(p.governorate)}</small>
        </span>
        <i data-lucide="plus" class="icon-sm"></i>
      </button>`
      )
      .join("");
    refreshIcons();
    availableList.querySelectorAll(".trail-picker-item").forEach((btn) => {
      btn.addEventListener("click", () => addStop(Number(btn.dataset.id)));
    });
  }

  function renderStops() {
    countEl.textContent = `${selected.length} stop${selected.length !== 1 ? "s" : ""}`;
    if (!selected.length) {
      stopsEl.innerHTML =
        '<div class="trail-picker-empty">Pick places above — they appear here in order.</div>';
    } else {
      stopsEl.innerHTML = selected
        .map(
          (p, i) => `
      <div class="trail-picker-stop" data-id="${p.dbId}">
        <span class="trail-stop-num">${i + 1}</span>
        <img src="${esc(p.image)}" alt="" loading="lazy">
        <span class="trail-picker-stop-name"><b>${esc(p.name)}</b><small>${esc(p.governorate)}</small></span>
        <span class="trail-picker-stop-actions">
          <button type="button" class="icon-btn" data-action="up" title="Move up" ${i === 0 ? "disabled" : ""}><i data-lucide="chevron-up" class="icon-sm"></i></button>
          <button type="button" class="icon-btn" data-action="down" title="Move down" ${i === selected.length - 1 ? "disabled" : ""}><i data-lucide="chevron-down" class="icon-sm"></i></button>
          <button type="button" class="icon-btn" data-action="remove" title="Remove"><i data-lucide="x" class="icon-sm"></i></button>
        </span>
      </div>`
        )
        .join("");
      refreshIcons();
    }
    syncInput();
  }

  function syncInput() {
    input.value = selected.map((p) => p.dbId).join(",");
  }

  function addStop(id) {
    const place = places.find((p) => p.dbId === id);
    if (!place || selected.some((p) => p.dbId === id)) return;
    selected.push(place);
    renderStops();
    renderAvailable();
  }

  function removeStop(id) {
    selected = selected.filter((p) => p.dbId !== id);
    renderStops();
    renderAvailable();
  }

  function move(index, delta) {
    const target = index + delta;
    if (target < 0 || target >= selected.length) return;
    const [item] = selected.splice(index, 1);
    selected.splice(target, 0, item);
    renderStops();
  }

  stopsEl.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const id = Number(btn.closest("[data-id]").dataset.id);
    const idx = selected.findIndex((p) => p.dbId === id);
    if (btn.dataset.action === "up") move(idx, -1);
    else if (btn.dataset.action === "down") move(idx, 1);
    else if (btn.dataset.action === "remove") removeStop(id);
  });

  filterInput.addEventListener("input", renderAvailable);

  renderStops();
  renderAvailable();
})();