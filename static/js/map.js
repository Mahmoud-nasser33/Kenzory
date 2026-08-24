/* Map page — Leaflet interactive map with category filtering, lightweight
   grid clustering, distance-from-you and graceful offline behaviour.

   Clustering is implemented here (no external plugin): at low zooms nearby
   markers merge into numbered bubbles that zoom in when clicked. When the
   browser shares a location, popups and the side panel show distances. */

(function () {
  const PLACES = window.PLACES_JSON || [];
  const el = document.getElementById("map");
  const chipsRow = document.getElementById("map-category-chips");
  const legendEl = document.getElementById("map-legend");
  const nearestEl = document.getElementById("map-nearest");
  const locateBtn = document.getElementById("locate-btn");
  const bannerEl = document.getElementById("map-offline-banner");
  if (!el || !window.L) return;

  /* Zoom at or above which every record gets its own marker. */
  const UNCLUSTERED_ZOOM = 11;
  /* Cluster bubble size in pixels used to build grid cells. */
  const CLUSTER_PX = 64;

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
  const tiles = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  /* ------------------------------------------------------------------
     Offline handling: after a few tile failures, tell the user while the
     pins/popups keep working (all data is embedded in the page).
  ------------------------------------------------------------------ */
  let tileErrors = 0;
  let offlineShown = false;
  tiles.on("tileerror", () => {
    tileErrors += 1;
    if (tileErrors >= 3 && !offlineShown && bannerEl) {
      offlineShown = true;
      bannerEl.hidden = false;
      refreshIcons();
    }
  });
  if (bannerEl) {
    bannerEl.addEventListener("click", (e) => {
      if (e.target.closest("[data-dismiss]")) bannerEl.hidden = true;
    });
    window.addEventListener("online", () => {
      offlineShown = false;
      tileErrors = 0;
      bannerEl.hidden = true;
      tiles.redraw();
    });
  }

  /* ------------------------------------------------------------------
     Distance from you
  ------------------------------------------------------------------ */
  let userPos = null; // {lat, lng, accuracy}

  function distanceKm(from, to) {
    const R = 6371;
    const dLat = ((to.lat - from.lat) * Math.PI) / 180;
    const dLng = ((to.lng - from.lng) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((from.lat * Math.PI) / 180) *
        Math.cos((to.lat * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  function formatKm(km) {
    if (km < 1) return `${Math.round(km * 1000)} m`;
    if (km < 100) return `${km.toFixed(1)} km`;
    return `${Math.round(km)} km`;
  }

  function popupHtml(p) {
    const distance =
      userPos && p.lat && p.lng
        ? `<p class="map-popup-distance"><i data-lucide="navigation" class="icon-sm"></i> ${esc(formatKm(distanceKm(userPos, p)))} from you</p>`
        : "";
    return `
      <div class="map-popup">
        <h4>${esc(p.name)}</h4>
        <p>${esc(p.city)}, ${esc(p.governorate)}</p>
        ${distance}
        <a href="/place/${esc(p.id)}">View record →</a>
      </div>`;
  }

  function makeMarker(p) {
    const color = CAT_COLORS[p.category] || "#666";
    const icon = L.divIcon({
      className: "map-dot",
      html: `<span class="map-dot-inner" style="background:${color}"></span>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
      popupAnchor: [0, -12],
    });
    const marker = L.marker([p.lat, p.lng], { icon });
    marker.bindPopup(popupHtml(p));
    marker.on("popupopen", () => refreshIcons());
    return marker;
  }

  /* ------------------------------------------------------------------
     Lightweight grid clustering
  ------------------------------------------------------------------ */
  const clusterLayer = L.layerGroup({ pane: "markerPane" }).addTo(map);
  let userLayer = null;

  function clusterIcon(count) {
    return L.divIcon({
      className: "map-cluster",
      html: `<span>${count}</span>`,
      iconSize: [42, 42],
      iconAnchor: [21, 21],
    });
  }

  function clusterListHtml(members) {
    const rows = members
      .slice(0, 8)
      .map(
        (m) =>
          `<li><a href="/place/${esc(m.id)}">${esc(m.name)}</a><small>${esc(m.city)}</small></li>`
      )
      .join("");
    const more = members.length > 8 ? `<li class="more">+${members.length - 8} more…</li>` : "";
    return `<div class="map-popup map-cluster-list"><h4>${members.length} records here</h4><ul>${rows}${more}</ul></div>`;
  }

  function renderClusters(places) {
    clusterLayer.clearLayers();
    if (!places.length) return;

    if (map.getZoom() >= UNCLUSTERED_ZOOM || places.length <= 10) {
      places.forEach((p) => clusterLayer.addLayer(makeMarker(p)));
      return;
    }

    const zoom = map.getZoom();
    const cells = new Map();
    places.forEach((p) => {
      const pt = map.project([p.lat, p.lng], zoom);
      const key = `${Math.floor(pt.x / CLUSTER_PX)}:${Math.floor(pt.y / CLUSTER_PX)}`;
      (cells.get(key) || cells.set(key, []).get(key)).push(p);
    });

    cells.forEach((members) => {
      if (members.length === 1) {
        clusterLayer.addLayer(makeMarker(members[0]));
        return;
      }
      const lat = members.reduce((s, m) => s + m.lat, 0) / members.length;
      const lng = members.reduce((s, m) => s + m.lng, 0) / members.length;
      const cluster = L.marker([lat, lng], { icon: clusterIcon(members.length) });
      cluster.on("click", () => {
        const bounds = L.latLngBounds(members.map((m) => [m.lat, m.lng]));
        if (
          map.getZoom() >= map.getMaxZoom() - 1 &&
          bounds.getNorthEast().distanceTo(bounds.getSouthWest()) < 5
        ) {
          cluster.bindPopup(clusterListHtml(members)).openPopup();
        } else {
          map.fitBounds(bounds.pad(0.25), { maxZoom: UNCLUSTERED_ZOOM });
        }
      });
      clusterLayer.addLayer(cluster);
    });
  }

  /* ------------------------------------------------------------------
     Category chips + legend (unchanged behaviour, new renderer)
  ------------------------------------------------------------------ */
  const layers = {};
  PLACES.forEach((p) => {
    (layers[p.category] = layers[p.category] || []).push(p);
  });

  const cats = Object.keys(layers);
  const allActive = new Set(cats);
  let activeCategories = cats.slice();

  function setVisible(categories) {
    activeCategories = categories;
    renderClusters(PLACES.filter((p) => categories.includes(p.category)));
    if (legendEl) {
      legendEl.innerHTML =
        `<div style="font-weight:700;font-size:0.8rem;margin-bottom:8px;">Legend</div>` +
        categories
          .map((c) => `<div style="display:flex;align-items:center;gap:8px;padding:2px 0;"><span style="width:11px;height:11px;border-radius:50%;background:${CAT_COLORS[c]};display:inline-block;"></span>${esc(c)}</div>`)
          .join("");
    }
    refreshIcons();
  }

  chipsRow.innerHTML =
    `<button type="button" class="chip active" data-all="1">All <span class="count">${PLACES.length}</span></button>` +
    cats
      .map(
        (c) =>
          `<button type="button" class="chip active" data-cat="${esc(c)}">${esc(c)} <span class="count">${layers[c].length}</span></button>`
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

  /* ------------------------------------------------------------------
     Nearest records panel + locate control
  ------------------------------------------------------------------ */
  function updateNearestPanel() {
    if (!nearestEl) return;
    if (!userPos) {
      nearestEl.hidden = true;
      return;
    }
    const withDistance = PLACES.filter((p) => p.lat && p.lng).map((p) => ({
      p,
      km: distanceKm(userPos, p),
    }));
    withDistance.sort((a, b) => a.km - b.km);
    const top = withDistance.slice(0, 5);
    nearestEl.hidden = false;
    nearestEl.innerHTML =
      `<div class="map-nearest-head">Nearest records</div>` +
      top
        .map(
          ({ p, km }) =>
            `<a class="map-nearest-row" href="/place/${esc(p.id)}">` +
            `<span class="map-nearest-dot" style="background:${CAT_COLORS[p.category] || "#666"}"></span>` +
            `<span class="map-nearest-name">${esc(p.name)}</span>` +
            `<b>${esc(formatKm(km))}</b></a>`
        )
        .join("");
    refreshIcons();
  }

  function setUserPosition(latlng, accuracy) {
    userPos = { lat: latlng.lat, lng: latlng.lng, accuracy: accuracy || 0 };
    if (userLayer) map.removeLayer(userLayer);
    userLayer = L.layerGroup();
    const dot = L.circleMarker([userPos.lat, userPos.lng], {
      radius: 7,
      color: "#fff",
      weight: 2,
      fillColor: "#e05d38",
      fillOpacity: 1,
    });
    userLayer.addLayer(dot);
    if (userPos.accuracy) {
      userLayer.addLayer(
        L.circle([userPos.lat, userPos.lng], {
          radius: Math.min(userPos.accuracy, 5000),
          color: "#e05d38",
          weight: 1,
          fillColor: "#e05d38",
          fillOpacity: 0.08,
        })
      );
    }
    dot.bindPopup("<div class='map-popup'><h4>You are here</h4></div>");
    userLayer.addTo(map);
    renderClusters(PLACES.filter((p) => activeCategories.includes(p.category)));
    updateNearestPanel();
  }

  if (locateBtn && "geolocation" in navigator) {
    locateBtn.addEventListener("click", () => {
      locateBtn.classList.add("locating");
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          locateBtn.classList.remove("locating");
          setUserPosition(pos.coords.latitude, pos.coords.accuracy);
          map.setView([userPos.lat, userPos.lng], Math.max(map.getZoom(), 9));
        },
        () => {
          locateBtn.classList.remove("locating");
          showToast(
            "Location unavailable",
            "We couldn't get your location. Check your browser permissions.",
            { icon: "alert-circle" }
          );
        },
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
      );
    });
  } else if (locateBtn) {
    locateBtn.hidden = true;
  }

  map.on("zoomend", () => {
    renderClusters(PLACES.filter((p) => activeCategories.includes(p.category)));
  });

  setVisible(cats);
})();
