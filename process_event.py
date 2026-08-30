"""
Megapress — portal event processor (runs in GitHub Actions).

Reads new original photos from R2 under _incoming/<folder>/, produces the clean
thumbnail and the watermarked full-size copy back to R2 (thumbs/ and watermarked/),
then discards the original from _incoming/. Finally it adds the event to
data/events.json. build_site.py regenerates index.html afterwards.

Environment (provided by the workflow):
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
  EVENT_JSON  — JSON string describing the event, e.g.:
    {
      "id": "my-event-2026",
      "category": "event",            # "event" | "exhibition"
      "year": 2026,
      "name": "My Event — Subtitle",
      "shortLabel": "My Event",       # optional; derived from name if omitted
      "caption": "My Event 2026",     # optional; derived from name+year if omitted
      "extraTags": ["40+ Speakers"],  # optional
      "folder": "Events/My Event 2026",
      "photos": ["A.JPG","B.JPG"]     # filenames already uploaded to _incoming/<folder>/
    }

Requires: Pillow, boto3
"""
import os, io, json
from pathlib import Path
import boto3
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).parent
THUMB_MAX, THUMB_Q = 800, 72
FULL_MAX,  FULL_Q  = 1920, 82
ORANGE, WHITE = (255, 90, 31), (242, 241, 238)
FONT = str(ROOT / "assets" / "DejaVuSans-Bold.ttf")
ARTIST    = "Spyridon Makridis / Megapress"
COPYRIGHT = "(C) 2026 Megapress Photo Agency. All rights reserved. info@megapressevents.com"
DESC      = "Megapress - Conference & Exhibition Photography, Thessaloniki"

def _env(k):
    return os.environ[k].strip()  # strip stray spaces/newlines from pasted secrets

BUCKET = _env("R2_BUCKET")
s3 = boto3.client(
    "s3",
    endpoint_url=f'https://{_env("R2_ACCOUNT_ID")}.r2.cloudflarestorage.com',
    aws_access_key_id=_env("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=_env("R2_SECRET_ACCESS_KEY"),
    region_name="auto",
)

def make_exif():
    e = Image.Exif()
    e[0x013B] = ARTIST; e[0x8298] = COPYRIGHT; e[0x010E] = DESC; e[0x0112] = 1
    return e

def _wordmark(scale):
    f = ImageFont.truetype(FONT, scale)
    pr = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = pr.textbbox((0, 0), "megapress", font=f); Wt, Ht = bb[2] - bb[0], bb[3] - bb[1]
    w1 = pr.textbbox((0, 0), "mega", font=f); w1 = w1[2] - w1[0]
    pad = int(scale * 0.6)
    lay = Image.new("RGBA", (Wt + pad * 2, Ht + pad * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay); sh = max(1, int(scale * 0.05))
    d.text((pad + sh, pad + sh), "megapress", font=f, fill=(0, 0, 0, 120))
    d.text((pad, pad), "mega", font=f, fill=ORANGE + (255,))
    d.text((pad + w1, pad), "press", font=f, fill=WHITE + (255,))
    return lay.crop(lay.getbbox())

def watermark(im):
    W, H = im.size
    scale = int(max(W, H) * 0.028)
    wm = _wordmark(scale)
    if H > W:
        wm = wm.rotate(90, expand=True)
    m = int(W * 0.022)
    b = im.convert("RGBA"); b.alpha_composite(wm, (W - wm.width - m, m))
    return b.convert("RGB")

def put_jpeg(img, key, q):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=q, optimize=True, exif=make_exif())
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue(), ContentType="image/jpeg")

def process_photos(folder, incoming):
    """Download each original from _incoming/, write thumb + watermarked to R2, discard original."""
    processed = []
    for fn in incoming:
        src_key = f"_incoming/{folder}/{fn}"
        obj = s3.get_object(Bucket=BUCKET, Key=src_key)
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(obj["Body"].read()))).convert("RGB")
        t = im.copy(); t.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
        put_jpeg(t, f"thumbs/{folder}/{fn}", THUMB_Q)
        fll = im.copy(); fll.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
        put_jpeg(watermark(fll), f"watermarked/{folder}/{fn}", FULL_Q)
        s3.delete_object(Bucket=BUCKET, Key=src_key)   # discard the original
        processed.append(fn)
        print(f"  processed {fn}")
    return processed

def main():
    ev = json.loads(os.environ["EVENT_JSON"])

    # ---- Gallery mode (Pavilions / B2B): append photos to an existing gallery ----
    gallery = ev.get("gallery")
    if gallery:
        gp = ROOT / "data" / "galleries.json"
        gal = json.load(open(gp, encoding="utf-8"))
        folder = ev.get("folder") or gal[gallery]["folder"]
        processed = process_photos(folder, ev["photos"])
        existing = gal[gallery]["photos"]
        gal[gallery]["photos"] = existing + [p for p in processed if p not in existing]
        json.dump(gal, open(gp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"Added {len(processed)} photos to gallery '{gallery}'.")
        return

    # ---- Event mode ----
    folder = ev["folder"]
    processed = process_photos(folder, ev["photos"])
    name = ev["name"]; year = ev["year"]
    entry = {
        "id": ev["id"],
        "category": ev["category"],
        "year": year,
        "shortLabel": ev.get("shortLabel") or name.split("—")[0].split("-")[0].strip(),
        "name": name,
        "caption": ev.get("caption") or f"{name} {year}",
        "extraTags": ev.get("extraTags", []),
        "folder": folder,
        "photos": processed,
    }
    dp = ROOT / "data" / "events.json"
    events = json.load(open(dp, encoding="utf-8"))
    events = [e for e in events if e.get("id") != entry["id"]]   # replace if same id
    events.insert(0, entry)
    json.dump(events, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Added event '{name}' with {len(processed)} photos.")

if __name__ == "__main__":
    main()
