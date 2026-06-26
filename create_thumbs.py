"""
Megapress — Thumbnail Generator
Run once from inside the megapressgr folder:
    python create_thumbs.py

Creates a `thumbs/` mirror of Events/, Exhibitions/, Pavilions/, B2B/
with images resized to max 800px wide at 70% quality (~50-150 KB each).
Originals are untouched — the website uses thumbs for the grid
and originals for the full-screen lightbox.

Requires Pillow:  pip install Pillow
"""

from pathlib import Path
from PIL import Image

PHOTO_DIRS = ["Events", "Exhibitions", "Pavilions", "B2B"]
THUMB_MAX  = 800      # px — longest side
QUALITY    = 72       # JPEG quality (50–95)
EXTENSIONS = {".jpg", ".jpeg", ".png"}

root = Path(__file__).parent
thumbs_root = root / "thumbs"

processed = 0
skipped   = 0

for source_dir in PHOTO_DIRS:
    src_base = root / source_dir
    if not src_base.exists():
        continue
    for img_path in sorted(src_base.rglob("*")):
        if img_path.suffix.lower() not in EXTENSIONS:
            continue
        rel      = img_path.relative_to(root)
        dst_path = thumbs_root / rel
        if dst_path.exists():
            skipped += 1
            continue
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(img_path) as im:
                im = im.convert("RGB")
                im.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
                im.save(dst_path, "JPEG", quality=QUALITY, optimize=True)
            print(f"  ✓  {rel}")
            processed += 1
        except Exception as e:
            print(f"  ✗  {rel}  ({e})")

print(f"\nDone — {processed} thumbnails created, {skipped} already existed.")
print(f"Thumbs folder: {thumbs_root}")
