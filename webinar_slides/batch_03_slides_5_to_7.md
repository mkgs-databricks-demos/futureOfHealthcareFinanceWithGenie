# Batch 3 — Slides 5, 6, 7: The Solution Arc
## Risk Adjustment → Unified Vision → Genie

---

## Slide 5 — Risk Adjustment: CMS Just Changed the Game
**File:** `slide_05_risk_adjustment.html`

### Visual
- Two-column: narrative left, SVG transition diagram right
- Green-themed (technology opportunity)
- Timeline row: CY26-27 (green "Now") → CY28 (red "Deadline")
- Green performance callout: "1M members × 1 HCC = 2 minutes"
- Program coverage chips: CMS-HCC V28, HHS-HCC, ESRD, Part D RxHCC
- Amber quote callout with the softened/empathetic talk track
- **SVG right:** "Old World" (SAS, gray, faded) → Python pill → "New World" (Databricks, green) with capability cards

### Speaker Notes
> "On July 31st, CMS and HHS released official Python code for risk adjustment calculations for the first time."
>
> "For CY26 and CY27, both SAS and Python will be published. Starting in CY28, CMS will stop publishing SAS entirely."
>
> "For years, finance and actuarial teams had a perfectly rational reason to stay on SAS — CMS required it for official submissions. That constraint shaped how entire departments were built. What's changed is that CMS itself has moved forward. With Python code now available for CY26 and CY27, and SAS being retired after CY28, the teams that start building on the new foundation today will have the smoothest transition — and they'll unlock capabilities like real-time prospective scoring and partial-year cohort analysis that were never practical in the old environment."
>
> "The Python code fits perfectly for Spark UDFs. We've seen 1 million members with one HCC processed in 2 minutes on a single-node cluster."

---

## Slide 6 — The Unified Data Vision
**File:** `slide_06_unified_vision.html`

### Visual
- Teal-themed (governance/platform)
- Three-layer SVG architecture diagram:
  - **Top:** 6 use-case bubbles (Employer Group, Trend Analytics, Risk Adjustment, VBC, Payment Integrity, HEDIS/Quality) — each in its team color
  - **Middle:** Genie AI Coworker Layer (green border)
  - **Bottom:** Governed Data Foundation (teal, Unity Catalog + Metric Views + Ontology)
- Dashed lines connecting bubbles → Genie → Foundation
- Bottom row: "Accurate" vs "Correct" comparison cards (red vs green)

### Speaker Notes
> "The real opportunity isn't solving any one of these problems in isolation. It's unifying data across clinical, actuarial, finance, programs — having one centralized and governed way of asking questions."
>
> "The alternative is a collection of disconnected AI use cases, each with its own data, definitions, and view of the business — the same fragmentation health plans have spent years trying to eliminate, only with an AI interface on top."
>
> "Here's a distinction that matters: an answer can be *accurate* — the right figure — but not *correct*, because it's missing the business context: which payer, which contract, which service line. The ontology is what makes the difference."

---

## Slide 7 — Genie Is Not a Dashboard. It's a Data-Smart AI Coworker.
**File:** `slide_07_genie_answer.html`

### Visual
- Two-column: narrative left, before/after SVG right
- Green-themed (the solution)
- Large story card with the Barry Thornton quote (green border, opening quotation mark)
- Dark "Let me show you what that looks like →" transition bar at bottom
- **SVG right:** Before (gray card with 6 mini dashboard wireframes, "2 hours every morning") → green arrow → After (green card with phone mockup showing Genie chat bubbles: "MLR alert", "3 contracts flagged", "Action: call Dr. Chen", "Ask follow-up" button → "10 minutes. On your phone.")

### Speaker Notes
> "Genie is not a dashboard. It's a data-smart AI coworker."
>
> "A dashboard shows you what the data says. Genie helps you act on it — grounded in your ontology, governed end to end, with a person deciding."
>
> "I knew a COO who spent two hours every morning in PowerBI dashboards with his coffee. I don't want him to spend two hours. I want him to wake up, look at his phone, and know what actually needs attention — and by the way, here's what you should do about it and who you should contact. That two hours is now ten minutes."
>
> "Let me show you what that looks like."
>
> [TRANSITION TO LIVE DEMO]

---

*Batch 3 of 4 · Slides 5–7 complete*
*Next: Batch 4 — Demo Flow + Customer Proof Points + Appendix*
