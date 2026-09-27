"""
Megapress — prune past upcoming events.
Removes any entry in data/upcoming.json whose end date (or start date, if no end)
is before today. Run daily by .github/workflows/prune-upcoming.yml; the commit it
makes triggers the site rebuild, so past 'Coming up' items drop off the site AND
out of the admin automatically.
"""
import json, datetime
from pathlib import Path

ROOT = Path(__file__).parent
p = ROOT / "data" / "upcoming.json"
today = datetime.date.today()

data = json.load(open(p, encoding="utf-8"))

def keep(u):
    end = u.get("endDate") or u.get("startDate")
    try:
        return datetime.date.fromisoformat(end) >= today
    except Exception:
        return True   # keep anything without a valid date, to be safe

kept = [u for u in data if keep(u)]
removed = len(data) - len(kept)
if removed:
    json.dump(kept, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Pruned {removed} past upcoming event(s).")
else:
    print("No past upcoming events to prune.")
