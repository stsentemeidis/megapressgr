"""
Megapress — Web Image Builder
Run from inside the megapressgr folder:
    python create_thumbs.py

For every photo in Events/, Exhibitions/, Pavilions/ and B2B/ it builds TWO
web derivatives (originals are never modified):

  thumbs/<...>       max 800px, CLEAN (no watermark)  -> used for the grid
  watermarked/<...>  max 1920px, WATERMARKED          -> used for the lightbox

The watermark is the megapress wordmark in the top-right corner: horizontal on
landscape photos, vertical on portrait photos. EXIF orientation is baked in so
the mark always lands correctly, and copyright metadata is embedded in both.

Safe to re-run: existing derivatives are skipped, so adding new photos only
processes the new files.

Requires Pillow:  pip install Pillow
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

PHOTO_DIRS = ["Events", "Exhibitions", "Pavilions", "B2B"]
THUMB_MAX  = 800      # grid thumbnail, clean
THUMB_Q    = 72
FULL_MAX   = 1920     # lightbox image, watermarked
FULL_Q     = 82
EXTENSIONS = {".jpg", ".jpeg", ".png"}

ORANGE = (255, 90, 31)
WHITE  = (242, 241, 238)

# Copyright metadata + watermark
ARTIST    = "Spyridon Makridis / Megapress"
COPYRIGHT = "(C) 2026 Megapress Photo Agency. All rights reserved. megapressagency01@gmail.com"
DESC      = "Megapress - Conference & Exhibition Photography, Thessaloniki"

root        = Path(__file__).parent
thumbs_root = root / "thumbs"
full_root   = root / "watermarked"
FONT_PATH   = root / "assets" / "DejaVuSans-Bold.ttf"   # bundled; swap for Space Grotesk if desired


def make_exif():
    e = Image.Exif()
    e[0x013B] = ARTIST      # Artist
    e[0x8298] = COPYRIGHT   # Copyright
    e[0x010E] = DESC        # ImageDescription
    e[0x0112] = 1           # Orientation = normal (already baked)
    return e


def _wordmark(scale):
    f = ImageFont.truetype(str(FONT_PATH), scale)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = probe.textbbox((0, 0), "megapress", font=f)
    Wt, Ht = bb[2] - bb[0], bb[3] - bb[1]
    w1 = probe.textbbox((0, 0), "mega", font=f); w1 = w1[2] - w1[0]
    pad = int(scale * 0.6)
    lay = Image.new("RGBA", (Wt + pad * 2, Ht + pad * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    sh = max(1, int(scale * 0.05))
    d.text((pad + sh, pad + sh), "megapress", font=f, fill=(0, 0, 0, 120))
    d.text((pad, pad), "mega", font=f, fill=ORANGE + (255,))
    d.text((pad + w1, pad), "press", font=f, fill=WHITE + (255,))
    return lay.crop(lay.getbbox())


def watermark(im):
    W, H = im.size
    scale = int(max(W, H) * 0.028)
    wm = _wordmark(scale)
    if H > W:                       # portrait -> vertical, reading upward
        wm = wm.rotate(90, expand=True)
    m = int(W * 0.022)
    base = im.convert("RGBA")
    base.alpha_composite(wm, (W - wm.width - m, m))   # top-right
    return base.convert("RGB")


processed = skipped = 0

for source_dir in PHOTO_DIRS:
    src_base = root / source_dir
    if not src_base.exists():
        continue
    for img_path in sorted(src_base.rglob("*")):
        if img_path.suffix.lower() not in EXTENSIONS:
            continue
        rel       = img_path.relative_to(root)
        thumb_dst = thumbs_root / rel
        full_dst  = full_root / rel
        if thumb_dst.exists() and full_dst.exists():
            skipped += 1
            continue
        thumb_dst.parent.mkdir(parents=True, exist_ok=True)
        full_dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with Image.open(img_path) as im:
                im = ImageOps.exif_transpose(im).convert("RGB")   # bake orientation upright
                exif = make_exif()
                # clean grid thumbnail
                if not thumb_dst.exists():
                    t = im.copy(); t.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
                    t.save(thumb_dst, "JPEG", quality=THUMB_Q, optimize=True, exif=exif)
                # watermarked full copy
                if not full_dst.exists():
                    fll = im.copy(); fll.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
                    watermark(fll).save(full_dst, "JPEG", quality=FULL_Q, optimize=True, exif=exif)
            print(f"  OK  {rel}")
            processed += 1
        except Exception as e:
            print(f"  x   {rel}  ({e})")

print(f"\nDone - {processed} photos processed, {skipped} already built.")
print(f"Clean thumbnails: {thumbs_root}")
print(f"Watermarked copies: {full_root}")
