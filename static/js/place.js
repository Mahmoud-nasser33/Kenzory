/* Place detail page — mini map, share, gallery lightbox. */

(function () {
  /* share */
  const shareBtn = document.getElementById("share-btn");
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const data = { title: document.title, url: window.PLACE_URL || window.location.href };
      if (navigator.share) {
        try {
          await navigator.share(data);
          return;
        } catch (e) {
          /* user cancelled */
        }
      }
      try {
        await navigator.clipboard.writeText(data.url);
        showToast("Link copied", "Share this record with someone who needs to see it.", { icon: "link" });
      } catch (e) {
        showToast("Share this record", data.url, { icon: "link" });
      }
    });
  }

  /* mini map */
  const mini = document.getElementById("place-mini-map");
  if (mini && window.L && window.PLACE_MAP) {
    const map = L.map(mini, {
      scrollWheelZoom: false,
      dragging: true,
      attributionControl: false,
      zoomControl: false,
    }).setView([window.PLACE_MAP.lat, window.PLACE_MAP.lng], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 18 }).addTo(map);
    const icon = L.divIcon({
      className: "map-marker-wrap",
      html: `<div class="map-marker" style="background:#b06a4a"><i data-lucide="map-pin" class="icon-sm"></i></div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    });
    L.marker([window.PLACE_MAP.lat, window.PLACE_MAP.lng], { icon })
      .addTo(map)
      .bindPopup(`<div class="map-popup"><h4>${esc(window.PLACE_MAP.name)}</h4></div>`)
      .openPopup();
    refreshIcons();
  }

  /* gallery lightbox */
  document.querySelectorAll("[data-lightbox]").forEach((img) => {
    img.addEventListener("click", () => {
      const overlay = document.createElement("div");
      overlay.className = "lightbox";
      overlay.innerHTML = `<img src="${esc(img.src)}" alt="${esc(img.alt)}"><button type="button" class="lightbox-close" aria-label="Close"><i data-lucide="x" class="icon"></i></button>`;
      document.body.appendChild(overlay);
      refreshIcons();
      const close = () => overlay.remove();
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay || e.target.closest(".lightbox-close")) close();
      });
      document.addEventListener("keydown", function onKey(e) {
        if (e.key === "Escape") {
          close();
          document.removeEventListener("keydown", onKey);
        }
      });
    });
  });
})();
