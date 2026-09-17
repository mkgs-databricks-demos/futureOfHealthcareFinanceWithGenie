# Healthcare Finance Webinar — Slide Deck
## The Future of Healthcare Finance with Genie
**September 17, 2026 · 9:00–10:40 AM PT · Virtual**
**Speaker:** Matt Giglia, Healthcare Field CTO, Databricks

---

## Slide 1 — What I'm Seeing This Week
**File:** `slide_01_opening.html`

### Visual
- Dark Databricks theme with gradient accent bar (red → amber → green)
- Abstract SVG data-flow lines on right side — flowing curves with glowing nodes
- Speaker card with avatar, name, and title

### Speaker Notes
> "I'm Matt Giglia, Healthcare FDE Lead at Databricks. Before this, I spent years as a principal data scientist at a health plan — so I've lived the challenges we're going to talk about."
>
> "I'm coming to you live from a week of on-site meetings with healthcare finance teams, and I want to share what I'm seeing right now — because it's directly relevant to every organization on this call."

**Tone:** Credibility through lived experience. Not reading from a playbook — telling the audience what you're seeing across healthcare finance teams *right now*, this week, from the field.

---

## Slide 2 — These Aren't Cyclical — They're Structural
**File:** `slide_02_industry_trends.html`

### Visual
- Four stat cards in a 2×2 grid, each with a colored left accent bar
- **9%** (red) — Medical cost increase
- **70%** (amber) — AI coding as top-3 cost driver
- **2×** (green) — GLP-1 utilization surge
- **+10%** (teal) — Behavioral health spike
- Empathetic quote callout at bottom

### Speaker Notes
> "Let me set the stage with what the industry is facing. These numbers from PWC's Health Behind the Numbers report tell the story."
>
> [Walk through each stat card]
>
> "These aren't cyclical — they're structural. The speed and complexity of change has outrun the systems finance teams rely on."
>
> "And I want to be clear about something: this isn't about any organization falling behind. Existing processes were rational given the constraints of the time. What's different now is the industry has reached an inflection point."

**Tone:** Empathetic framing. Acknowledge the constraint was real, position the shift as the industry moving forward, not a customer failure.

### Sources
- PWC "Health Behind the Numbers" 2026
- Industry analysis 2025–2026

---

## Slide 3 — Sister Teams. Same Function. No Shared Context.
**File:** `slide_03_disparate_systems.html`

### Visual
- Six team silos as dashed-border columns: Underwriting, Actuarial, Finance, Contracting, Operations, Clinical
- Each silo contains 3–4 sub-functions as cards
- Red ✕ marks between each silo showing disconnection
- CFO question bubble at bottom: *"What's our real exposure on this block?"* → "Nobody has the answer."
- Amber insight callout about metric reconciliation

### Speaker Notes
> "What I'm seeing across every health plan I visit is the same structural problem: teams that sit within the same financial or actuarial function — teams that are literally sister teams — operate on completely different data, different definitions, and different timelines."
>
> "The underwriting team has one view of a group's risk. The actuarial team has another. The account management team has a third. And when the CFO asks a question that crosses those boundaries — 'what's our real exposure on this block?' — nobody has the answer because the systems don't talk to each other."
>
> "At one organization, I found 5 or 6 separate underwriting workflows — small group, large group, level-funded, stop loss, ancillary — each with different data inputs, different regulatory requirements, different personas. All within the same department. No shared context. No common definitions."
>
> "The same metric gets defined differently depending on who's calculating it. One version lands in the CFO's monthly reporting package, another shows up in an ad hoc analytics request, and eventually someone has to reconcile them manually. That reconciliation is where the weeks go."

**Tone:** Organizational, not technical. The audience is 50% business decision-makers. "Sister teams that don't share context" resonates more than "claims grouper ETL." Frame as: the people are sophisticated; the infrastructure hasn't caught up.

---

## Design Language Reference

### Colors
| Token | Hex | Usage |
|-------|-----|-------|
| Databricks Red | `#FF3621` | Primary accent, CTAs, logo |
| Amber | `#FFAB00` | Secondary accent, warnings |
| Green | `#00A972` | Success, positive metrics |
| Teal | `#077A9D` | Tertiary accent |
| Rose | `#AB4057` | Operations accent |
| Sky | `#8BCAE7` | Clinical accent |
| Dark BG | `#1B1F24` | Slide background |
| Card BG | `rgba(255,255,255,0.04)` | Card surfaces |

### Typography
- **Font:** DM Sans (Google Fonts)
- **H1:** 36–52px, weight 700
- **Body:** 15–16px, weight 400–500
- **Eyebrow:** 13–14px, weight 500, letter-spacing 3px, uppercase

### Patterns
- Gradient accent bar: `linear-gradient(90deg, #FF3621, #FF6A4D 30%, #FFAB00 60%, #00A972)`
- Subtle grid background at 3% opacity
- Colored left-border accent on cards (4px)
- Dashed borders on silo diagrams
- Quote callouts with colored left border

---

*Batch 1 of 4 · Slides 1–3 complete*
*Next: Batch 2 — Slides 4–4c (Underwriting → NAIC AI → Rx Rebates)*

---

## Design Language Reference (Light Mode)

### Colors
| Token | Hex | Usage |
|-------|-----|-------|
| Databricks Red | `#FF3621` | Primary accent, CTAs, logo, alerts |
| Amber (dark) | `#D49200` | Secondary accent on light bg |
| Green (dark) | `#008A5E` | Success, positive metrics on light bg |
| Teal | `#077A9D` | Tertiary accent |
| Rose | `#AB4057` | Operations accent |
| Sky | `#4DA8C9` | Clinical accent |
| **Background** | `#FFFFFF` | Slide background |
| Card BG | `#F8F9FA` | Card surfaces |
| Card Border | `#E8EAED` | Card/silo borders |
| Body Text | `#1B1F24` | Headlines |
| Secondary Text | `#3C4043` | Body copy |
| Muted Text | `#5A6068` | Sub-items |
| Tertiary Text | `#8A9099` | Subtitles, roles |
| Faint Text | `#B0B5BB` | Sources, footer |

### Silo Tint Backgrounds
| Team | Fill | Border |
|------|------|--------|
| Underwriting | `#FFF5F4` | `#FF3621` |
| Actuarial | `#FFFBF0` | `#D49200` |
| Finance | `#F0FBF6` | `#008A5E` |
| Contracting | `#F0F8FB` | `#077A9D` |
| Operations | `#FDF4F6` | `#AB4057` |
| Clinical | `#F0F8FC` | `#4DA8C9` |

### Typography
- **Font:** DM Sans (Google Fonts)
- **H1:** 33–52px, weight 700, color `#1B1F24`
- **Body:** 14.5–16px, weight 400–500, color `#3C4043`
- **Eyebrow:** 13px, weight 500, letter-spacing 3px, uppercase

### Patterns
- Gradient accent bar: `linear-gradient(90deg, #FF3621, #FF6A4D 30%, #FFAB00 60%, #00A972)`
- Subtle dot grid at 4% opacity
- Colored left-border accent on cards (4px)
- Dashed borders on silo diagrams
- Quote callouts: tinted background + colored left border
