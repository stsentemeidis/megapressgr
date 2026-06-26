# megapress — Project Brief

Context for continuing work on the megapress conference & exhibition photography website. The current build is a single self-contained `index.html` file (HTML/CSS/JS, no build step).

## Who this is for
A Thessaloniki-based photographer (Megapress) specializing in conference and exhibition coverage — HELEXPO trade fairs, festivals, and similar events — who also takes assignments outside Greece.

## Brand
- **Name / logo**: "megapress" wordmark, rebuilt as live CSS text (not an image) — "mega" in signature orange, "press" in off-white, "PHOTO AGENCY" tracked out above in small mono caps. This replaces the client's old low-res raster logo (orange/charcoal, italic, drop-shadow) with a clean, scalable version that keeps the same color identity.
- **Old site context**: the original megapress.gr was a general news/press agency (sports, politics, disasters, etc.). This rebuild deliberately repositions the brand as a **conference & exhibition specialist** — old generalist copy was fully dropped.

## Visual direction
- **Mood**: dark, dramatic, black-background, modern/minimal — explicitly requested by the client over bright/airy or bold/energetic alternatives.
- **Palette**: near-black (#0b0b0c) base, signature orange (#ff5a1f, pulled from the real logo) as the single accent, charcoal/steel grays for structure, warm off-white (#f2f1ee) for text. Earlier draft used an amber/blue "stage light" palette before the real logo was supplied — orange replaced amber once the logo was uploaded.
- **Type**: Space Grotesk (display/headlines), Inter (body), JetBrains Mono (labels, datelines, tags — gives a press-wire/credential feel).
- **Signature concept — "running order / press log"**: instead of a generic photo grid, work is displayed like a conference programme or news-wire log (dateline-style labels, event names, tags). This is a deliberate structural choice tying the layout to the subject (conferences run on schedules; press agencies run on wires), not decoration.
- **Hero motion**: originally generic light-beam sweeps; replaced with an **animated architectural blueprint of a convention center floor plan** (main stage, breakout rooms, exhibition hall with booth grid, dimension lines, north-arrow/scale mark, title block reading "MEGAPRESS — FLOOR PLAN"). Lines trace themselves in via SVG stroke-dasharray animation, loop continuously, plus a subtle scanning line. This is more specific to the subject than generic light beams — it's literally the photographer's working environment.

## Section-by-section state

**Header / nav**: Logo wordmark, nav links (Work, Approach, About, Contact), nav CTA "Book a date."

**Hero**: Headline "The story behind every stage." Hero CTA buttons: "View the work →" and **"Reach the desk →"** (changed from generic "Check availability" — ties into press/wire vocabulary already used elsewhere on the site; "the desk" = newsroom shorthand for the assignment desk). Hero height fixed to 92vh (capped at 880px) with vertically centered content — originally 100vh bottom-pinned content left an awkward empty gap on load.

**Clients marquee**: scrolling strip of real Thessaloniki/HELEXPO event names (TIF · HELEXPO, Artozyma, Agrotica, Philoxenia–Hotelia, Thessaloniki Film Festival, Documentary Festival, Book Fair) — originally had placeholder global conference names (Web Summit, CES, etc.), replaced once real local events were confirmed.

**"Covered" section** (id="work") — title changed from "From the wire" (ambiguous, didn't signal past tense) to **"Covered"**, which pairs cleanly against "Coming up." Lists 6 real, verified-past Thessaloniki events, **ordered most recent first**:
1. Thessaloniki International Book Fair — May 2026
2. Agrotica (31st, biennial) — Mar 2026
3. Thessaloniki Documentary Festival (28th) — Mar 2026
4. Artozyma (12th) — Feb–Mar 2026
5. Thessaloniki International Film Festival (66th) — Oct–Nov 2025 (2026 dates not yet announced at time of writing)
6. Thessaloniki International Fair / TIF (89th) — Sep 2025

Dates were verified via live web search, not assumed. Rule used: if the event's 2026 edition had already occurred as of the conversation date (June 20, 2026), use 2026; otherwise use the most recent completed edition (2025).

**Note on Photosynkyria**: client's original list included it, but research found it appears to have become the biennial "Thessaloniki Photobiennale" with no confirmable 2025/2026 edition — client chose to **omit it entirely** rather than guess at a date.

**"Coming up" section** (id="upcoming") — new section for confirmed-future events, styled distinctly (dashed borders, outlined "COVERAGE PENDING" placeholder thumbnails) so it doesn't imply photos already exist:
1. Thessaloniki International Fair — 90th edition / centenary year, **5–13 Sep 2026**, Japan as Honoured Country
2. Philoxenia – Hotelia — **13–15 Nov 2026**

**Layout note (Covered + Coming up)**: both were rebuilt from a spacious "row" layout (130px image, 28px padding, up to 30px name text) into a **compact dense ledger** — 64×44px thumbnails (hidden until hover), 14px row padding, 16px name text, name+tags on one inline line. This was a deliberate compactness pass per client request; a card-grid alternative was considered and rejected because it would abandon the schedule/wire-log brand concept.

**Stats row**: exactly 4 stats in one row, per client spec:
- 15 yrs — Behind the lens
- 500+ — Events covered
- 24hr — Standard turnaround
- **Global** — Availability (originally "WW", changed to the word "Global" with a smaller font-size override since a 6-letter word at the same size as "15"/"24" looked oversized/awkward)

**"Why work with a specialist" section** (id="approach") — title changed from "How it works" / "Built for the schedule, not around it" to **"Why work with a specialist"** (eyebrow: "The case for a specialist"). Purpose: this is a trust/differentiation section aimed at event organizers, making the case for hiring a conference specialist over a generalist photographer. Originally a 2-column layout (text list + large decorative empty visual panel); rebuilt as a **horizontal strip of 5 compact tiles** (A–E) since the decorative panel had no real content and felt empty:
- A — Run-of-show briefing
- B — Stage-light fluency
- C — Floor-level coverage
- D — Same-day delivery
- E — On location, anywhere (added later — see "Global reach" below)

**Testimonial**: generic placeholder quote, not yet replaced with a real client testimonial.

**CTA / Contact section** (id="contact"): "Let's cover your next stage." Contact line tweaked to read "...in Thessaloniki or further afield..." to subtly signal non-local availability.

**Footer**: wordmark, sitemap, services list, contact block (address/phone pulled from the old megapress.gr site via search — **flagged as possibly outdated, needs client verification**: Agias Sofias 22, 54622 Thessaloniki, +30 2310 235090). Footer tagline: "Thessaloniki — working worldwide."

## "Global reach" requirement
Client wants the site to subtly signal ability to work outside Greece, threaded through **multiple sections rather than one banner**. Current touchpoints:
1. Hero tag: "Based in Thessaloniki — working worldwide"
2. Stats row: "Global" / Availability
3. Approach tile E: "On location, anywhere — based in Thessaloniki, travelling across Greece and abroad"
4. CTA subtext: "...in Thessaloniki or further afield..."
5. Footer tagline: "Thessaloniki — working worldwide"

The "Covered" section itself stays 100% Thessaloniki events by design (real past work) — global signal lives in the other sections.

## Section spacing (recent pass)
Vertical gaps between these adjacent sections were tightened from the default 140px section padding to scoped, smaller values:
- Clients marquee → Covered: 140px → 64px
- Covered → Coming up: 120px → 96px
- Coming up → Stats row: 140px → 64px
- Stats row → testimonial (spans the "Why work with a specialist" section in between): 280px → 128px

## Known gaps / things flagged but not yet resolved
1. **All photos are placeholder gradients** (`.ph-1` through `.ph-5`, `.ph-upcoming`) — no real photography has been supplied yet.
2. **Footer contact details are unverified** — pulled from old site via search, could be stale.
3. **Email placeholder**: `info@megapress.gr` — not confirmed as a real/active address.
4. **Testimonial is generic placeholder text**, not a real client quote.
5. **Logo**: rebuilt as live CSS text matching the original's color scheme; a standalone SVG export (for business cards, social profiles, etc.) has not yet been created — offered but not requested.
6. Client uses **Claude Cowork** going forward; this brief exists because chat memory doesn't transfer between conversations/products — the canonical source of truth is the `index.html` file itself, not this document.

## File
Single file: `index.html`, self-contained (inline CSS, inline JS, Google Fonts import). No build tooling, no dependencies beyond the font import.
