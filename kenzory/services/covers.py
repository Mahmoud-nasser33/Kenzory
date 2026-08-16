"""Generated SVG cover images.

Records without a photograph get a tasteful generated cover (Arabic + English
name on a category-toned background). Covers are generated once and written to
``static/img/covers/<slug>.svg``.
"""

import os

from xml.sax.saxutils import escape as _xml_escape

from flask import current_app

from kenzory.services.security import slugify

_COVER_COLORS = {
    "Historical Sites": {"bg": "#3b3f4a", "bg2": "#262a33", "fg": "#e8e3d6", "accent": "#c8a24a"},
    "Hidden Gems": {"bg": "#2f3d34", "bg2": "#1f2a24", "fg": "#e8e3d6", "accent": "#c8a24a"},
    "Architecture": {"bg": "#4a3b2f", "bg2": "#332821", "fg": "#ede7da", "accent": "#c8a24a"},
    "Traditional Crafts": {"bg": "#7a4433", "bg2": "#552e21", "fg": "#f2ead9", "accent": "#e6c784"},
    "Food & Culture": {"bg": "#6b4a2b", "bg2": "#4a3018", "fg": "#f2ead9", "accent": "#e6c784"},
    "Stories & Legends": {"bg": "#4a2f3d", "bg2": "#331f2b", "fg": "#e8e3d6", "accent": "#c8a24a"},
    "Religious Heritage": {"bg": "#4f3d2a", "bg2": "#362a1c", "fg": "#efe9dc", "accent": "#d9b45b"},
    "Natural Heritage": {"bg": "#2f4a45", "bg2": "#1e332f", "fg": "#e8e3d6", "accent": "#c8a24a"},
}

_DEFAULT = _COVER_COLORS["Hidden Gems"]


def _svg(category, name_ar, name_en, city):
    c = _COVER_COLORS.get(category, _DEFAULT)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c['bg']}"/>
      <stop offset="1" stop-color="{c['bg2']}"/>
    </linearGradient>
    <pattern id="p" width="80" height="80" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <path d="M0 40h80M40 0v80" stroke="{c['accent']}" stroke-opacity="0.10" stroke-width="1" fill="none"/>
    </pattern>
  </defs>
  <rect width="1200" height="800" fill="url(#g)"/>
  <rect width="1200" height="800" fill="url(#p)"/>
  <path d="M0 640 Q300 540 600 640 T1200 640 V800 H0 Z" fill="#000" opacity="0.18"/>
  <rect x="40" y="40" width="1120" height="720" fill="none" stroke="{c['accent']}" stroke-opacity="0.5" stroke-width="2"/>
  <text x="600" y="430" text-anchor="middle" font-family="'Alegreya','Amiri',Georgia,serif" font-size="92" fill="{c['fg']}">{_xml_escape(name_ar)}</text>
  <text x="600" y="520" text-anchor="middle" font-family="Georgia,serif" font-size="38" fill="{c['fg']}" opacity="0.85">{_xml_escape(name_en)}</text>
  <circle cx="600" cy="575" r="26" fill="none" stroke="{c['accent']}" stroke-width="2"/>
  <line x1="585" y1="575" x2="615" y2="575" stroke="{c['accent']}" stroke-width="2"/>
  <line x1="600" y1="560" x2="600" y2="590" stroke="{c['accent']}" stroke-width="2"/>
  <text x="600" y="650" text-anchor="middle" font-family="Georgia,serif" font-size="26" letter-spacing="4" fill="{c['fg']}" opacity="0.7">{_xml_escape(category.upper())}</text>
  <text x="600" y="700" text-anchor="middle" font-family="Georgia,serif" font-size="22" fill="{c['fg']}" opacity="0.5">{_xml_escape(city)}</text>
</svg>"""


def ensure_cover(slug, category, name_ar, name_en, city):
    """Write a cover SVG for the given record if one does not already exist."""
    slug = slugify(slug) or "place"
    folder = current_app.config["COVER_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{slug}.svg")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_svg(category, name_ar or "", name_en, city))
    return f"img/covers/{slug}.svg"


def cover_rel_path(slug):
    return f"img/covers/{slugify(slug) or 'place'}.svg"
