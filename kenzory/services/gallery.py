"""Gallery helpers: captions and safe edits to published photo sets.

Galleries remain lists of static-relative paths; captions live in a parallel
JSON mapping of path -> caption so existing data keeps working unchanged.
"""

import os

from flask import current_app


MAX_CAPTION_LENGTH = 140


def pair_captions(paths, caption_values):
    """Zip saved image paths with their submitted caption strings."""
    values = [str(c or "").strip()[:MAX_CAPTION_LENGTH] for c in (caption_values or [])]
    return {
        path: values[index]
        for index, path in enumerate(paths)
        if index < len(values) and values[index]
    }


def clean_caption(value):
    return str(value or "").strip()[:MAX_CAPTION_LENGTH]


def is_upload(path):
    """True when a gallery path points into the user-uploads folder."""
    return bool(path) and path.startswith("uploads/")


def remove_upload_files(paths):
    """Delete uploaded files from disk; ignore missing/foreign paths."""
    folder = current_app.config["UPLOAD_FOLDER"]
    for rel in paths or []:
        if not is_upload(rel):
            continue
        try:
            os.remove(os.path.join(folder, os.path.basename(rel)))
        except OSError:
            pass


def apply_gallery_edits(place, keep_paths, new_captions_by_path=None):
    """Reconcile a place's gallery after an edit form submit.

    ``keep_paths`` is the ordered list of existing photos the editor kept,
    with their (possibly updated) captions in ``new_captions_by_path``.
    Photos dropped from the list are removed from disk when they were user
    uploads; curated seed photos are left untouched. Returns nothing — the
    place's columns are updated in place (caller commits).
    """
    keep_paths = [p for p in (keep_paths or []) if p in (place.gallery or [])]

    dropped = [p for p in (place.gallery or []) if p not in keep_paths]
    remove_upload_files(dropped)

    captions = {
        p: clean_caption((new_captions_by_path or {}).get(p))
        for p in keep_paths
    }
    captions = {p: c for p, c in captions.items() if c}

    place.gallery = keep_paths
    place.photo_captions = captions
    place.photos = len(keep_paths)
    if keep_paths and place.image not in keep_paths:
        place.image = keep_paths[0]
    if not keep_paths:
        # Cover falls back to the generated cover art; keep ``image`` as-is
        # because place_image() already falls back gracefully.
        pass


def append_uploads(place, new_paths, captions_by_path):
    """Add freshly uploaded paths (and captions) to a place's gallery."""
    if not new_paths:
        return
    gallery = list(place.gallery or [])
    gallery.extend(new_paths)
    place.gallery = gallery

    merged = dict(place.photo_captions or {})
    for path in new_paths:
        caption = clean_caption(captions_by_path.get(path))
        if caption:
            merged[path] = caption
    place.photo_captions = merged
    place.photos = len(gallery)
