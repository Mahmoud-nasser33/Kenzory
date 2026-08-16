"""Secure image handling for user uploads.

- Accepts only jpg/png/webp by extension AND by Pillow inspection.
- Rejects files larger than the configured per-file limit.
- Never trusts the client filename: files are saved under a random UUID name.
- Re-encodes large images down to a reasonable width to keep pages fast.
"""

import os
import secrets

from flask import current_app
from PIL import Image, UnidentifiedImageError

MAX_DIMENSION = 1600
OUTPUT_QUALITY = 85


def _ensure_folder():
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    return folder


def save_upload(file_storage):
    """Validate and save one uploaded image.

    Returns the relative URL path (e.g. ``uploads/abc123.jpg``) or raises
    ValueError with a user-facing message.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file selected.")

    original_name = file_storage.filename or ""
    ext = os.path.splitext(original_name)[1].lower()
    allowed = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
    if ext not in allowed:
        raise ValueError(
            "Unsupported file type. Please upload a JPG, PNG or WebP image."
        )

    data = file_storage.read()
    if len(data) > current_app.config["MAX_IMAGE_SIZE"]:
        raise ValueError(
            "This image is larger than 5 MB. Please upload a smaller photo."
        )

    try:
        with Image.open(file_storage.stream) as im:
            im.verify()
    except UnidentifiedImageError:
        raise ValueError("The uploaded file is not a valid image.")

    # Reopen after verify() and normalize orientation / size.
    file_storage.stream.seek(0)
    image = Image.open(file_storage.stream)
    image = _normalize_image(image)

    safe_ext = _safe_extension(image.format or ext.lstrip("."))
    filename = f"{secrets.token_hex(12)}.{safe_ext}"
    rel_path = f"uploads/{filename}"

    folder = _ensure_folder()
    image.save(os.path.join(folder, filename), quality=OUTPUT_QUALITY, optimize=True)
    return rel_path


def _normalize_image(image):
    # Rotate according to EXIF orientation and cap dimensions.
    try:
        image = ImageOps_exif_transpose(image)
    except Exception:
        pass
    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    if image.mode in ("P", "LA"):
        image = image.convert("RGBA")
    elif image.mode != "RGB" and image.mode != "RGBA":
        image = image.convert("RGB")
    return image


def ImageOps_exif_transpose(image):
    from PIL import ImageOps

    return ImageOps.exif_transpose(image)


def _safe_extension(fmt):
    mapping = {
        "JPEG": "jpg",
        "JPG": "jpg",
        "PNG": "png",
        "WEBP": "webp",
    }
    return mapping.get((fmt or "").upper(), "jpg")
