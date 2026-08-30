import json, re, datetime
from pathlib import Path
ROOT=Path(__file__).parent
def load(n): return json.load(open(ROOT/"data"/f"{n}.json", encoding="utf-8"))
events=load("events"); upcoming=load("upcoming"); partners=load("partners"); clients=load("clients"); stats=load("stats")
TODAY=datetime.date.today()  # real build date drives auto-hide of past upcoming
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---------- EVENTS (On Record) ----------
def render_events():
    evs=sorted(events, key=lambda e:(-e["year"], 0 if e["category"]=="event" else 1))
    out=[]; last_year=None
    for e in evs:
        if e["year"]!=last_year:
            out.append(f'\n        <!-- {e["year"]} -->'); last_year=e["year"]
        cat=e["category"]; n=len(e["photos"])
        dl=("EVENT" if cat=="event" else "EXHIB")+f' · {e["year"]}'
        catlabel="Event" if cat=="event" else "Exhibition"
        extra="".join(f'<span class="tag">{esc(t)}</span>' for t in e.get("extraTags",[]))
        photos=",".join(e["photos"])
        out.append(f'''        <div class="event-row" data-category="{cat}" data-year="{e["year"]}">
          <div class="event-trigger" tabindex="0" role="button" aria-expanded="false">
            <div class="er-time"><span class="dateline">{dl}</span>{esc(e["shortLabel"])}</div>
            <div class="er-main">
              <div class="er-name">{esc(e["name"])}</div>
              <div class="er-meta"><span class="tag cat-badge">{catlabel}</span><span class="tag">{n} photos</span>{extra}</div>
            </div>
            <div class="expand-toggle"><span class="expand-hint">View photos</span><span class="expand-icon"></span></div>
          </div>
          <div class="photo-panel">
            <div class="photo-panel-inner">
              <div class="photo-count-bar">
                <span class="photo-count-label"><em>{n}</em> photographs — {esc(e["caption"])}</span>
                <button class="collapse-btn"><svg viewBox="0 0 12 12"><line x1="2" y1="10" x2="10" y2="2"/><line x1="10" y1="10" x2="2" y2="2"/></svg>Collapse</button>
              </div>
              <div class="photo-grid" data-folder="{e["folder"]}" data-photos="{photos}"></div>
            </div>
          </div>
        </div>''')
    return "\n"+"\n\n".join(out)+"\n\n      "

# ---------- UPCOMING ----------
def render_upcoming():
    up=[u for u in upcoming if datetime.date.fromisoformat(u.get("endDate",u["startDate"]))>=TODAY]
    up=sorted(up, key=lambda u:u["startDate"])
    out=[]
    for u in up:
        tags="".join(f'<span class="tag">{esc(t)}</span>' for t in u.get("extraTags",[]))+'<span class="tag">Booking now</span>'
        out.append(f'''        <div class="slot slot-upcoming">
          <div class="slot-time"><span class="dateline accent">{esc(u["dateLabel"])}</span>{u["year"]}</div>
          <div class="slot-main">
            <div class="slot-name">{esc(u["name"])}</div>
            <div class="slot-meta">{tags}</div>
          </div>
        </div>''')
    return "\n"+"\n".join(out)+"\n      "

# ---------- PARTNERS ----------
def partner_item(p):
    mark=""
    if p.get("svg"): mark="\n          "+p["svg"]
    elif p.get("logo"): mark=f'\n          <img class="partner-logo" src="{p["logo"]}" alt="{esc(p["name"])}">'
    return f'''        <div class="partner-item">{mark}
          <div class="partner-detail">
            <div class="partner-name-main">{esc(p["name"])}</div>
            <div class="partner-name-sub">{esc(p["sub"])}</div>
          </div>
        </div>
        <span class="p-sep"></span>'''
def render_partners():
    one="\n".join(partner_item(p) for p in partners)
    return "\n\n        <!-- \u2500\u2500 set 1 \u2500\u2500 -->\n"+one+"\n\n        <!-- \u2500\u2500 set 2 (duplicate for seamless loop) \u2500\u2500 -->\n"+one+"\n\n      "

# ---------- CLIENTS ----------
def client_item(c):
    logo=f'<img class="partner-logo" src="{c["logo"]}" alt="{esc(c["name"])}"> ' if c.get("logo") else ""
    return f'''        <div class="partner-item">
          <div class="partner-detail">{logo}<div class="partner-name-main">{esc(c["name"])}</div><div class="partner-name-sub">{esc(c["sub"])}</div></div>
        </div>
        <span class="p-sep"></span>'''
def render_clients():
    one="\n".join(client_item(c) for c in clients)
    return "\n\n        <!-- set 1 -->\n"+one+"\n\n        <!-- set 2 — duplicate for seamless loop -->\n"+one+"\n\n      "

# ---------- STATS ----------
def render_stats():
    out=[]
    for s in stats:
        if s.get("isWord"):
            num=f'<div class="stat-num is-word">{esc(s["value"])}</div>'
        else:
            num=f'<div class="stat-num">{esc(s["value"])}<span class="unit">{esc(s["unit"])}</span></div>'
        out.append(f'<div class="stat">{num}<div class="stat-label">{esc(s["label"])}</div></div>')
    return "\n        "+"\n        ".join(out)

html=open(ROOT/"index.html", encoding="utf-8").read()
regions=[
 ("EVENTS", r'(<div class="programme" id="eeList">)([\s\S]*?)(</div><!-- /eeList -->)', render_events()),
 ("UPCOMING", r'(<section id="upcoming">[\s\S]*?<div class="programme">)([\s\S]*?)(</div>\s*</div>\s*</section>)', render_upcoming()),
 ("PARTNERS", r'(<section class="partners" id="partners">[\s\S]*?<div class="partners-track">)([\s\S]*?)(</div>\s*</div>\s*</section>)', render_partners()),
 ("CLIENTS", r'(<div class="clients">[\s\S]*?<div class="partners-track">)([\s\S]*?)(\n      </div>\n    </div>\n  </div>)', render_clients()),
 ("STATS", r'(<div class="stats-grid">)([\s\S]*?)(\n      </div>\n    </div>\n  </div>)', render_stats()),
]
def norm(s): return re.sub(r'\s+',' ', re.sub(r'>\s+<','><', s)).strip()
built=html
print("=== PARITY CHECK (per region) ===")
for name,pat,new in regions:
    m=re.search(pat, built)
    if not m:
        print(f"{name}: ✗ ANCHOR NOT FOUND"); continue
    cur_inner=m.group(2)
    if norm(cur_inner)==norm(new):
        print(f"{name}: ✓ identical (normalized)")
    else:
        print(f"{name}: ⚠ differs — inspect")
        a=norm(cur_inner); b=norm(new)
        for i in range(min(len(a),len(b))):
            if a[i]!=b[i]:
                print("   first diff @",i); print("   CURRENT:",a[max(0,i-40):i+60]); print("   BUILT  :",b[max(0,i-40):i+60]); break
        else:
            print("   length diff cur",len(a),"built",len(b))
    built=built[:m.start()]+m.group(1)+new+m.group(3)+built[m.end():]
open(ROOT/"index.html","w",encoding="utf-8").write(built)
print("Wrote index.html (in place)")
