"""
Megapress — Copyright Metadata Stamper (lossless)
Run from inside the megapressgr folder:
    python embed_metadata.py

Writes IPTC/EXIF copyright fields (Artist, Copyright, Description) into every
original photo in Events/, Exhibitions/, Pavilions/ and B2B/ WITHOUT re-encoding
the image (no quality loss). Safe to re-run — it simply overwrites the fields.
This is provenance only: it proves authorship, it does not stop downloads.

Requires piexif:  pip install piexif
"""

from pathlib import Path
import glob
import piexif

PHOTO_DIRS = ["Events", "Exhibitions", "Pavilions", "B2B"]
EXTS = ("*.jpg", "*.jpeg", "*.JPG", "*.JPEG")

ARTIST    = "Spyridon Makridis / Megapress"
COPYRIGHT = "(C) 2026 Megapress Photo Agency. All rights reserved. megapressagency01@gmail.com"
DESC      = "Megapress - Conference & Exhibition Photography, Thessaloniki"

root = Path(__file__).parent

files = []
for d in PHOTO_DIRS:
    for ext in EXTS:
        files += glob.glob(str(root / d / "**" / ext), recursive=True)
files = sorted(set(files))

ok = err = 0
for f in files:
    try:
        try:
            exif = piexif.load(f)
        except Exception:
            exif = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        exif["0th"][piexif.ImageIFD.Artist]           = ARTIST.encode("ascii", "ignore")
        exif["0th"][piexif.ImageIFD.Copyright]        = COPYRIGHT.encode("ascii", "ignore")
        exif["0th"][piexif.ImageIFD.ImageDescription] = DESC.encode("ascii", "ignore")
        exif["0th"][piexif.ImageIFD.XPAuthor]         = ARTIST.encode("utf-16le")
        piexif.insert(piexif.dump(exif), f)   # lossless, in place
        ok += 1
    except Exception as e:
        err += 1
        print(f"  x  {Path(f).name}  ({e})")

print(f"\nDone — copyright embedded in {ok} photos, {err} errors.")
