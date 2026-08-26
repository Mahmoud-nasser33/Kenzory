/* Kenzory shared UI helpers — cards, toasts, saved places, icons. */

const SAVED_KEY = "kenzory:saved";

const CATEGORY_TONES = {
  "Historical Sites": "cat-historical",
  "Hidden Gems": "cat-hidden",
  "Architecture": "cat-architecture",
  "Traditional Crafts": "cat-crafts",
  "Food & Culture": "cat-food",
  "Stories & Legends": "cat-stories",
  "Religious Heritage": "cat-religious",
  "Natural Heritage": "cat-natural",
};

/* ---------- icons ---------- */

function refreshIcons() {
  if (window.lucide) {
    try {
      lucide.createIcons();
    } catch (e) {
      /* ignore */
    }
  }
}

/* ---------- escaping ---------- */

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ---------- saved places ---------- */

function getSaved() {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || "[]");
  } catch (e) {
    return [];
  }
}

function setSaved(ids) {
  localStorage.setItem(SAVED_KEY, JSON.stringify(ids));
  window.dispatchEvent(new CustomEvent("kenzory:saved-changed"));
}

function updateSavedDot() {
  const dots = document.querySelectorAll(".js-saved-dot");
  const n = getSaved().length;
  dots.forEach((d) => {
    d.style.display = n ? "" : "none";
  });
}

function isSaved(id) {
  return getSaved().includes(id);
}

function toggleSaved(id, name) {
  const saved = getSaved();
  const idx = saved.indexOf(id);
  const nowSaved = idx === -1;
  if (nowSaved) {
    saved.push(id);
    setSaved(saved);
    showToast("Saved to your collection", name, { action: "View saved", href: "/saved" });
  } else {
    saved.splice(idx, 1);
    setSaved(saved);
    showToast("Removed from your collection", name);
  }
  return nowSaved;
}

function saveButton(id, name, { light = false } = {}) {
  const saved = isSaved(id);
  const lightClass = light ? " save-btn-light" : "";
  return `<button type="button" class="save-btn${saved ? " saved" : ""}${lightClass}" data-save-id="${esc(id)}" data-save-name="${esc(name)}" aria-label="${saved ? "Remove from saved" : "Save this place"}">
    <i data-lucide="${saved ? "bookmark" : "bookmark-plus"}" class="icon-sm"></i>
    ${saved ? "Saved" : "Save"}
  </button>`;
}

function syncSaveButtons(root) {
  (root || document).querySelectorAll("[data-save-id]").forEach((btn) => {
    const id = btn.dataset.saveId;
    const saved = isSaved(id);
    btn.classList.toggle("saved", saved);
    btn.innerHTML = `<i data-lucide="${saved ? "bookmark" : "bookmark-plus"}" class="icon-sm"></i>${saved ? "Saved" : "Save"}`;
    btn.setAttribute("aria-label", saved ? "Remove from saved" : "Save this place");
  });
  refreshIcons();
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-save-id]");
  if (!btn) return;
  e.preventDefault();
  e.stopPropagation();
  const id = btn.dataset.saveId;
  const name = btn.dataset.saveName || "";
  toggleSaved(id, name);
  syncSaveButtons();
});

/* ---------- toasts ---------- */

function toastRoot() {
  let root = document.querySelector(".toast-root");
  if (!root) {
    root = document.createElement("div");
    root.className = "toast-root";
    document.body.appendChild(root);
  }
  return root;
}

function showToast(title, msg, opts = {}) {
  const toast = document.createElement("div");
  toast.className = "toast";
  const action = opts.action
    ? `<a class="toast-action" href="${esc(opts.href || "#")}">${esc(opts.action)}</a>`
    : "";
  toast.innerHTML = `
    <i data-lucide="${opts.icon || (opts.action ? "bookmark" : "check-circle")}" class="icon"></i>
    <div class="toast-body"><b>${esc(title)}</b>${msg ? `<span>${esc(msg)}</span>` : ""}</div>
    ${action}
    <button type="button" class="toast-close" aria-label="Dismiss"><i data-lucide="x" class="icon-sm"></i></button>`;
  toastRoot().appendChild(toast);
  refreshIcons();

  const kill = () => {
    toast.classList.add("hide");
    setTimeout(() => toast.remove(), 300);
  };
  toast.querySelector(".toast-close").addEventListener("click", kill);
  setTimeout(kill, opts.ttl || 4200);
}

/* ---------- card builders ---------- */

function categoryBadge(cat) {
  const tone = CATEGORY_TONES[cat] || "cat-hidden";
  return `<span class="badge category-badge ${esc(tone)}">${esc(cat)}</span>`;
}

function stars(rating) {
  const full = Math.round(rating);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

function fmtNum(n) {
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, "") + "k";
  return String(n);
}

function placeCard(p) {
  return `
  <article class="place-card surface-card">
    <div class="place-card-media">
      <a href="/place/${esc(p.id)}"><img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy" width="640" height="400"></a>
      <span class="media-top-left">${categoryBadge(p.category)}</span>
      <span class="media-top-right">${saveButton(p.id, p.name)}</span>
      <span class="media-bottom-left"><i data-lucide="map-pin" class="icon-sm"></i> ${esc(p.city)}, ${esc(p.governorate)}</span>
    </div>
    <div class="place-card-body">
      <h3 class="place-card-title"><a href="/place/${esc(p.id)}">${esc(p.name)}</a></h3>
      <p class="place-card-ar">${esc(p.nameAr)}</p>
      <p class="place-card-summary">${esc(p.summary)}</p>
      <div class="place-card-meta">
        <span class="rating"><span class="stars">${stars(p.rating)}</span><span class="rating-value">${p.rating.toFixed(1)}</span></span>
        <span><i data-lucide="bookmark" class="icon-sm"></i> ${fmtNum(p.saves)}</span>
        <span><i data-lucide="camera" class="icon-sm"></i> ${p.photos}</span>
        ${p.verified ? '<span class="badge verified-badge"><i data-lucide="shield-check" class="icon-sm"></i> Verified</span>' : ""}
      </div>
    </div>
  </article>`;
}

function placeRow(p) {
  return `
  <article class="place-card place-row surface-card">
    <div class="place-card-media">
      <a href="/place/${esc(p.id)}"><img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy" width="640" height="400"></a>
    </div>
    <div class="place-card-body">
      <div class="place-row-head">
        <h3 class="place-card-title"><a href="/place/${esc(p.id)}">${esc(p.name)}</a></h3>
        <span>${saveButton(p.id, p.name)}</span>
      </div>
      <p class="place-card-ar">${esc(p.nameAr)}</p>
      <div class="row-badges">${categoryBadge(p.category)}${p.verified ? '<span class="badge verified-badge"><i data-lucide="shield-check" class="icon-sm"></i> Verified</span>' : ""}</div>
      <p class="place-card-summary">${esc(p.summary)}</p>
      <div class="place-card-meta">
        <span class="rating"><span class="stars">${stars(p.rating)}</span><span class="rating-value">${p.rating.toFixed(1)}</span><span class="rating-count">(${p.ratingCount})</span></span>
        <span><i data-lucide="bookmark" class="icon-sm"></i> ${fmtNum(p.saves)} saves</span>
        <span><i data-lucide="camera" class="icon-sm"></i> ${p.photos} photos</span>
        <span><i data-lucide="map-pin" class="icon-sm"></i> ${esc(p.city)}, ${esc(p.governorate)}</span>
      </div>
    </div>
  </article>`;
}

function storyCard(s) {
  return `
  <article class="story-card">
    <a class="story-card-media" href="/stories/${esc(s.id)}"><img src="${esc(s.image)}" alt="${esc(s.title)}" loading="lazy"></a>
    <div class="story-card-body">
      <div class="row-badges">${categoryBadge(s.category)}${s.governorate ? `<span class="badge category-badge cat-natural">${esc(s.governorate)}</span>` : ""}</div>
      <h3 class="story-card-title"><a href="/stories/${esc(s.id)}">${esc(s.title)}</a></h3>
      <p class="story-card-excerpt">${esc(s.excerpt)}</p>
      <div class="story-card-meta">
        <span class="byline"><span class="byline-avatar">${esc(s.author.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase())}</span>${esc(s.author)}</span>
        <span>· ${s.readMinutes} min read</span>
        <span>· ${esc(s.date)}</span>
      </div>
    </div>
  </article>`;
}

function skeletonCard() {
  return `
  <div class="skeleton-card">
    <div class="skeleton skeleton-media"></div>
    <div class="skeleton skeleton-line"></div>
    <div class="skeleton skeleton-line short"></div>
  </div>`;
}

function emptyState({ icon = "compass", title, body, action, href, label }) {
  return `
  <div class="empty-state">
    <div class="empty-icon"><i data-lucide="${icon}" class="icon-lg"></i></div>
    <h3>${esc(title)}</h3>
    <p>${esc(body)}</p>
    ${action ? `<a class="btn btn-accent" href="${esc(href)}">${esc(label)}</a>` : ""}
  </div>`;
}

/* ---------- boot ---------- */

document.addEventListener("DOMContentLoaded", () => {
  syncSaveButtons();
  updateSavedDot();
  refreshIcons();
  window.addEventListener("kenzory:saved-changed", updateSavedDot);

  /* newsletter demo */
  window.__kenzoryNewsletter = () =>
    showToast("You're on the list", "Field notes from the community, twice a month.", { icon: "mail" });

  /* mobile drawer */
  const drawer = document.getElementById("drawer");
  const burger = document.getElementById("burger");
  if (drawer && burger) {
    burger.addEventListener("click", () => drawer.classList.add("open"));
    drawer.querySelector(".drawer-backdrop").addEventListener("click", () => drawer.classList.remove("open"));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") drawer.classList.remove("open");
    });
  }

  /* user menu dropdown */
  const userBtn = document.getElementById("user-menu-btn");
  const userMenu = document.getElementById("user-dropdown");
  if (userBtn && userMenu) {
    const menu = userBtn.closest(".user-menu");
    userBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = menu.classList.toggle("open");
      userBtn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (e) => {
      if (!menu.contains(e.target)) {
        menu.classList.remove("open");
        userBtn.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        menu.classList.remove("open");
        userBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* notification bell dropdown */
  const notifBell = document.getElementById("notif-bell-btn");
  const notifDropdown = document.getElementById("notif-dropdown");
  const notifList = document.getElementById("notif-dropdown-list");
  if (notifBell && notifDropdown) {
    const notifMenu = notifBell.closest(".notif-menu");
    notifBell.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = notifMenu.classList.toggle("open");
      notifBell.setAttribute("aria-expanded", String(open));
      if (open && notifList && !notifList.dataset.loaded) {
        loadNotifDropdown();
      }
    });
    document.addEventListener("click", (e) => {
      if (!notifMenu.contains(e.target)) {
        notifMenu.classList.remove("open");
        notifBell.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        notifMenu.classList.remove("open");
        notifBell.setAttribute("aria-expanded", "false");
      }
    });
    loadNotifBadge();
  }

  function loadNotifBadge() {
    fetch("/notifications/unread-count")
      .then((r) => r.json())
      .then((d) => {
        const badge = document.querySelector(".js-notif-badge");
        if (!badge) return;
        if (d.count > 0) {
          badge.textContent = d.count > 99 ? "99+" : String(d.count);
          badge.style.display = "";
        } else {
          badge.style.display = "none";
        }
      })
      .catch(() => {});
  }

  function loadNotifDropdown() {
    fetch("/notifications/recent")
      .then((r) => r.json())
      .then((d) => {
        if (!notifList) return;
        notifList.dataset.loaded = "1";
        if (!d.notifications || d.notifications.length === 0) {
          notifList.innerHTML = '<div class="notif-dropdown-empty">No notifications yet</div>';
          return;
        }
        notifList.innerHTML = d.notifications.map((n) => {
          const iconMap = {
            submission_approved: "check-circle-2",
            submission_rejected: "x-circle",
            review_received: "star",
            endorsement_received: "thumbs-up",
            badge_earned: "award",
          };
          const icon = iconMap[n.type] || "bell";
          const unread = n.is_read ? "" : " unread";
          const dot = n.is_read ? "" : '<span class="notif-dropdown-dot"></span>';
          return `<a href="${esc(n.link)}" class="notif-dropdown-item${unread}">
            <span class="notif-dropdown-icon"><i data-lucide="${icon}" class="icon-sm"></i></span>
            <span class="notif-dropdown-body"><b>${esc(n.title)}</b><p>${esc(n.message)}</p></span>
            ${dot}
          </a>`;
        }).join("");
        refreshIcons();
      })
      .catch(() => {
        if (notifList) notifList.innerHTML = '<div class="notif-dropdown-empty">Couldn\'t load notifications</div>';
      });
  }
});
