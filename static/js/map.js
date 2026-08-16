/* Map page — Leaflet interactive map with category filtering. Places render
   as simple dots; popups carry only text so the map stays fast and light. */

(function () {
  const PLACES = window.PLACES_JSON || [];
  const el = document.getElementById("map");
  const chipsRow = document.getElementById("map-category-chips");
  const legendEl = document.getElementById("map-legend");
  if (!el || !window.L) return;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  const CAT_COLORS = {
    "Historical Sites": "#3a5a7a",
    "Hidden Gems": "#5a7a4a",
    "Architecture": "#b06a4a",
    "Traditional Crafts": "#a04a3a",
    "Food & Culture": "#c99a3a",
    "Stories & Legends": "#7a5a8a",
    "Religious Heritage": "#9a7a3a",
    "Natural Heritage": "#3a8a7a",
  };

  const map = L.map("map", { scrollWheelZoom: true }).setView([26.7, 30.2], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  const layers = {};
  const markers = [];

  PLACES.forEach((p) => {
    const color = CAT_COLORS[p.category] || "#666";
    const icon = L.divIcon({
      className: "map-dot",
      html: `<span class="map-dot-inner" style="background:${color}"></span>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
      popupAnchor: [0, -12],
    });
    const marker = L.marker([p.lat, p.lng], { icon });
    marker.bindPopup(`
      <div class="map-popup">
        <h4>${esc(p.name)}</h4>
        <p>${esc(p.city)}, ${esc(p.governorate)}</p>
        <a href="/place/${esc(p.id)}">View record →</a>
      </div>`);
    markers.push({ marker, category: p.category, place: p });
    (layers[p.category] = layers[p.category] || L.layerGroup()).addLayer(marker);
  });

  Object.values(layers).forEach((g) => g.addTo(map));

  function setVisible(categories) {
    Object.entries(layers).forEach(([cat, group]) => {
      if (categories.includes(cat)) {
        map.addLayer(group);
      } else {
        map.removeLayer(group);
      }
    });
    if (legendEl) {
      legendEl.innerHTML =
        `<div style="font-weight:700;font-size:0.8rem;margin-bottom:8px;">Legend</div>` +
        categories
          .map((c) => `<div style="display:flex;align-items:center;gap:8px;padding:2px 0;"><span style="width:11px;height:11px;border-radius:50%;background:${CAT_COLORS[c]};display:inline-block;"></span>${esc(c)}</div>`)
          .join("");
    }
  }

  /* build chips */
  const cats = Object.keys(layers);
  const allActive = new Set(cats);
  chipsRow.innerHTML =
    `<button type="button" class="chip active" data-all="1">All <span class="count">${markers.length}</span></button>` +
    cats
      .map(
        (c) =>
          `<button type="button" class="chip active" data-cat="${esc(c)}">${esc(c)} <span class="count">${layers[c].getLayers().length}</span></button>`
      )
      .join("");

  chipsRow.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    if (chip.dataset.all) {
      allActive.clear();
      cats.forEach((c) => allActive.add(c));
      chipsRow.querySelectorAll(".chip").forEach((c) => c.classList.add("active"));
      setVisible(cats);
      return;
    }
    const cat = chip.dataset.cat;
    if (allActive.has(cat)) allActive.delete(cat);
    else allActive.add(cat);
    chip.classList.toggle("active", allActive.has(cat));
    setVisible(cats.filter((c) => allActive.has(c)));
  });

  setVisible(cats);
})();
