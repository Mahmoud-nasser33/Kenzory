/* Saved page — render saved places from localStorage. */

(function () {
  const PLACES = window.PLACES_JSON || [];
  const grid = document.getElementById("saved-grid");
  const count = document.getElementById("saved-count");
  const note = document.getElementById("saved-note");
  if (!grid) return;

  const byId = {};
  PLACES.forEach((p) => (byId[p.id] = p));

  function render() {
    const saved = getSaved().map((id) => byId[id]).filter(Boolean);
    count.textContent = saved.length + (saved.length === 1 ? " saved place" : " saved places");

    if (!saved.length) {
      note.style.display = "block";
      grid.style.display = "none";
    } else {
      note.style.display = "none";
      grid.style.display = "";
      grid.innerHTML = saved.map(placeCard).join("");
    }
    syncSaveButtons();
    refreshIcons();
  }

  window.addEventListener("kenzory:saved-changed", render);
  render();
})();
