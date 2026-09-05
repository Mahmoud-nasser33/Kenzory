/* Trail detail page — draws the ordered stops as a route on a Leaflet map. */

(function () {
  const el = document.getElementById("trail-map");
  if (!el || !window.L || !window.TRAIL_STOPS) return;

  const points = window.TRAIL_STOPS.filter(
    (s) => typeof s.latitude === "number" && typeof s.longitude === "number"
  );
  if (!points.length) return;

  const map = L.map(el, {
    scrollWheelZoom: false,
    attributionControl: false,
    zoomControl: true,
  }).setView([points[0].latitude, points[0].longitude], 12);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 18 }).addTo(map);

  const latlngs = points.map((s) => [s.latitude, s.longitude]);
  L.polyline(latlngs, { color: "#b06a4a", weight: 3, opacity: 0.85 }).addTo(map);

  points.forEach((s, i) => {
    const icon = L.divIcon({
      className: "map-marker-wrap",
      html: `<div class="map-marker trail-map-marker"><span>${i + 1}</span></div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    });
    L.marker([s.latitude, s.longitude], { icon })
      .addTo(map)
      .bindPopup(`<div class="map-popup"><strong>${esc(s.name)}</strong></div>`);
  });

  if (latlngs.length > 1) {
    map.fitBounds(L.latLngBounds(latlngs).pad(0.4));
  }
  refreshIcons();
})();