# Design System — AuraNode Reasoning Dashboard

`docs/design.md` — visual identity and component spec for the frontend. Read this before touching `frontend/src/`. Every color, type, and spacing decision below is derived from the design plan in §1 — don't introduce new ones ad hoc; extend this doc first if a new pattern is genuinely needed.

---

## 1. Design Thesis

AuraNode's whole value proposition is **making machine reasoning inspectable** — a graph fact traced back to its source text, a traversal path you can actually see. The UI should look like an instrument built for that job, not a chat-app skin with a graph bolted on.

**Direction: Technical Schematic / Lab Notebook Neobrutalism.**
Think: an electronics engineer's wiring diagram crossed with a physical index-card system — graph-paper ground, thick ink rules, flat hard-edged colour blocks, offset "stamped" shadows instead of blur, and a monospace data voice for anything that's a literal system value (chunk IDs, node types, relation labels). Nodes in the visualization and node-like elements in the UI (citation chips, entity chips) share the same visual grammar — a "card" is a card whether it's on the canvas or in the chat panel. That consistency **is** the signature.

Explicitly rejected: purple/violet gradients, soft glassmorphism, blurred drop-shadows, rounded pill-everything, warm-cream-plus-terracotta ("AI generated" tell), centered-hero-with-gradient-blob layouts. Nothing in this system uses `blur()`, gradients, or `border-radius` above 8px.

---

## 2. Colour System

Flat colour only. Every shadow is a **hard offset**, never blurred. Contrast is checked against WCAG AA at minimum for all text/background pairs.

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#EEEEE6` | App background — a cool bone-white, not warm cream. Reads as graph paper, not "AI beige." |
| `--paper-line` | `#D8D8CC` | Faint grid/rule lines on the paper background (the "graph paper" texture) |
| `--ink` | `#14161A` | Primary text, borders, default stroke on nearly everything. Near-black, slightly blue-shifted (not pure #000 — softer on paper). |
| `--ink-soft` | `#54585F` | Secondary text, captions, timestamps |
| `--signal` | `#2447FF` | Primary accent — cobalt "signal blue." Used for primary actions, the active traversal path, focus states. Deliberately electric, not pastel. |
| `--current` | `#FFC629` | Secondary accent — amber "current." Used sparingly: highlighted/selected node, loading pulses, the one animated element on screen. |
| `--edge-live` | `#00A876` | Tertiary accent — "circuit green." Used only for live/success states (query succeeded, connection healthy) and default (non-traversed) graph edges. |
| `--alert` | `#E13B2E` | Error/destructive state only. Not used decoratively. |
| `--card` | `#FFFFFF` | Card/panel surface, sits on `--paper` with a hard border + offset shadow |

**Shadow convention (the "stamped" effect):** every raised element uses a solid offset shadow, no blur:
```css
box-shadow: 4px 4px 0 var(--ink);
```
Interactive elements shift toward their shadow on press (`translate(2px, 2px)` + shadow reduces to `2px 2px 0`) — this is the primary tactile feedback mechanism instead of opacity/scale fades.

**Contrast checks (must hold):**
- `--ink` on `--paper`: ~15.5:1 ✅
- `--paper` on `--signal`: ~7.8:1 ✅ (white/paper text on cobalt buttons)
- `--ink` on `--current`: ~11.2:1 ✅ (amber is used with dark text, never light text)
- `--paper` on `--edge-live`: ~3.9:1 — large text/icon only, not body copy

---

## 3. Typography

Three roles, deliberately not the "geometric sans + generic serif" default pairing.

| Role | Typeface | Usage |
|---|---|---|
| **Display** | **Space Grotesk**, weights 500/700 | Page headers, panel titles, the empty-state headline. Slightly mechanical, wide apertures — reads as "instrument," not "startup landing page." |
| **Body** | **IBM Plex Sans**, weights 400/500 | Chat messages, all prose, UI labels. Chosen because Plex has a technical/engineering pedigree (IBM's own design-systems typeface) that matches the schematic direction without being a default like Inter. |
| **Data / Mono** | **IBM Plex Mono**, weights 400/500 | Chunk IDs, entity IDs, relation labels (`ACQUIRED`, `chunk_0472`), citation chips, the schema.json before/after count, API status text. Anything that is a literal system value gets set in mono — this is a functional signal, not decoration: it tells the user "this is data, not prose." |

**Type scale (base 16px):**
```
--text-display-lg: 2.5rem / 1.1   (Space Grotesk 700) — page/app title
--text-display-sm: 1.5rem / 1.2   (Space Grotesk 700) — panel headers ("Reasoning Trace", "Ask AuraNode")
--text-body:        1rem  / 1.5   (Plex Sans 400)      — chat/prose
--text-body-sm:      0.875rem / 1.4 (Plex Sans 400)     — captions, meta
--text-mono:         0.8125rem / 1.4 (Plex Mono 500)    — IDs, labels, data chips
```
Letter-spacing: Space Grotesk headers get `+0.01em`; Plex Mono data chips get `+0.02em` and are set in uppercase for relation/type labels specifically (`ACQUIRED`, not `Acquired`) — this mirrors how the canonical schema itself is stored (`schema.json` uses upper-snake-case), so the UI's typography literally reflects the data model. That's a deliberate, subject-grounded choice, not a style flourish.

---

## 4. Layout

**Grid:** 12-column, `--paper-line` grid visible faintly across the whole app background (a literal graph-paper texture, ~24px cells, 1px lines at low opacity) — this is the one persistent "wallpaper" motif and it's directly about the subject (a graph tool, on graph paper).

**Primary screen — split-panel dashboard**, no gradient hero, no marketing-style landing above the tool:
```
┌────────────────────────────────────────────────────────────────┐
│  AURANODE            [●live schema: 12 types]     [status: ok]  │  ← header bar, ink bg, paper text
├─────────────────────────────┬────────────────────────────────────┤
│  ASK AURANODE                │  REASONING TRACE                  │
│  ┌─────────────────────────┐ │  ┌──────────────────────────────┐ │
│  │ chat history             │ │  │                                │ │
│  │  [user bubble]            │ │  │     graph-paper canvas        │ │
│  │  [answer card + citations]│ │  │     nodes = stamped chips      │ │
│  │                           │ │  │     traversal path = signal    │ │
│  │                           │ │  │     blue thick edges           │ │
│  └─────────────────────────┘ │  │     other edges = thin ink      │ │
│  ┌─────────────────────────┐ │  └──────────────────────────────┘ │
│  │ [ input________ ] [Ask]  │ │  ⌄ expand: schema legend           │
│  └─────────────────────────┘ │                                    │
└─────────────────────────────┴────────────────────────────────────┘
```
- Left panel: `--paper` background, chat is the "notebook page."
- Right panel: same `--paper-line` grid but denser (graph canvas needs the grid as a spatial reference, like real graph paper) — this is the one place motion lives (see §6).
- No rounded full-bleed hero section, no centered gradient blob, no "trusted by" logo row — this is a working tool's dashboard, not a SaaS landing page skin.

**Cards / panels:** `--card` background, `2px solid var(--ink)` border, `4px 4px 0 var(--ink)` shadow, `border-radius: 4px` (just enough to soften the stamp, not full brutalist zero-radius — keeps it "aesthetic" per brief rather than harsh).

---

## 5. Signature Element

**The node chip.** One visual unit — a small rectangular card with a thick ink border, a mono-set label, and a coloured left-edge stripe indicating entity type — is reused identically in three places: (1) as an actual node in the force-graph canvas, (2) as a citation chip under a chat answer, (3) as an entry in the schema legend. The user learns the shape once and then recognizes it everywhere the system is referencing a piece of its own knowledge graph. This is the one idea the whole interface is "remembered by," and it directly encodes the product's actual architecture (graph nodes and citations are, underneath, the same kind of object — a piece of grounded evidence) rather than being decoration layered on top.

```
┌───┬─────────────────────┐
│ █ │ MICROSOFT            │   ← left stripe = entity-type colour
│ █ │ ORGANIZATION          │   (mono, uppercase, --ink-soft)
└───┴─────────────────────┘
     2px ink border, 3px 3px 0 hard shadow (smaller than panel-level cards —
     chips are one shadow-step lighter than panels, establishing hierarchy)
```

---

## 6. Motion

Restraint, per the brief. Three deliberate moments only:

1. **Query submit → answer arrival:** the right-panel graph canvas doesn't fade in — nodes "snap" into position one traversal-hop at a time (staggered ~120ms per hop), so the *build order* of the graph visually narrates the retrieval process (chunk match → hop 1 → hop 2). This is the orchestrated "page-load sequence" moment the brief calls for, and it's directly explanatory rather than ambient.
2. **Press feedback:** the stamped-shadow shift described in §2 (translate + shadow shrink) on every button/chip press. No opacity fades anywhere in the system — everything is a hard state change, consistent with the flat/brutalist material logic.
3. **Loading state:** a single `--current` amber pulse on the query input's border while waiting on `/api/query` — not a spinner, not a skeleton shimmer.

Everything else is static. `prefers-reduced-motion` disables #1's stagger (nodes appear at once) and #3's pulse (becomes a static amber border) — motion is never load-bearing for understanding the result.

---

## 7. Component Notes

- **Buttons:** rectangular, `border-radius: 4px`, `2px solid --ink`, filled `--signal` with `--paper` text for primary ("Ask"), outlined `--card`/`--ink` for secondary. No ghost/text-only buttons for primary actions — every actionable element has a visible border, consistent with the "instrument panel" logic (nothing is invisible until hovered).
- **Chat bubbles:** user messages — right-aligned, `--ink` fill, `--paper` text, no tail/pointer (a bubble tail is exactly the kind of default flourish this system avoids). Answer cards — left-aligned, `--card` fill, `--ink` border, citation chips (the signature element, §5) docked along the bottom edge of the card.
- **Empty state (first load):** headline in Space Grotesk explaining the loaded demo corpus in plain terms ("This graph currently knows about AI industry acquisitions — ask it something"), not a generic "start chatting" placeholder — per the frontend-design guidance on writing, this treats emptiness as direction, not mood.
- **Errors:** `--alert` red, left-stripe on the chip pattern reused for error cards, plain-language explanation of what failed and what to do ("Couldn't reach the graph database — try again in a moment"), never a raw stack trace in the user-facing surface.
- **Focus states:** every interactive element gets a visible `3px solid var(--signal)` outline offset by 2px on `:focus-visible` — never suppressed. This matters doubly here since keyboard/screen-reader users need a non-mouse way to inspect the same reasoning trace.

---

## 8. CSS Variables (drop into `frontend/src/index.css`)

```css
:root {
  /* colour */
  --paper: #EEEEE6;
  --paper-line: #D8D8CC;
  --ink: #14161A;
  --ink-soft: #54585F;
  --signal: #2447FF;
  --current: #FFC629;
  --edge-live: #00A876;
  --alert: #E13B2E;
  --card: #FFFFFF;

  /* type */
  --font-display: "Space Grotesk", sans-serif;
  --font-body: "IBM Plex Sans", sans-serif;
  --font-mono: "IBM Plex Mono", monospace;

  --text-display-lg: 700 2.5rem/1.1 var(--font-display);
  --text-display-sm: 700 1.5rem/1.2 var(--font-display);
  --text-body: 400 1rem/1.5 var(--font-body);
  --text-body-sm: 400 0.875rem/1.4 var(--font-body);
  --text-mono: 500 0.8125rem/1.4 var(--font-mono);

  /* shadow / shape */
  --shadow-panel: 4px 4px 0 var(--ink);
  --shadow-chip: 3px 3px 0 var(--ink);
  --shadow-press: 2px 2px 0 var(--ink);
  --radius: 4px;
  --border: 2px solid var(--ink);
}
```

---

## 9. Do / Don't Against Generic AI-Design Defaults

| Don't | Do instead |
|---|---|
| Purple/violet gradient background or buttons | Flat `--signal` cobalt, no gradients anywhere |
| Warm cream + terracotta palette | Cool bone-white paper + cobalt/amber/green |
| Blurred drop shadows / glassmorphism | Hard offset shadows only, 0 blur |
| Centered hero with big number + gradient blob | Straight into the working split-panel dashboard |
| Full-pill rounded corners everywhere | 4px radius cap, sharp rectangular chips/buttons |
| Same typeface for headers and data | Three distinct roles — Space Grotesk / Plex Sans / Plex Mono |
| Numbered 01/02/03 markers as decoration | No numbering unless content is a real sequence (it isn't, here) |
| Spinner/skeleton loading everywhere | One amber pulse on the active input only |
