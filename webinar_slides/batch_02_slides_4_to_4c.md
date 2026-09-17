# Batch 2 — Slides 4, 4b, 4c: The Regulatory Forcing Function Arc
## Underwriting → NAIC AI → Rx Rebates

---

## Slide 4 — Underwriting: 15 Years Overdue
**File:** `slide_04_underwriting.html`

### Visual
- Two-column layout: narrative left, SVG timeline right
- Red quote callout with your personal story (italic)
- Pain list with red ✕ bullets
- Green opportunity callout at bottom
- Timeline SVG: 2006 → 2010 → 2015 → 2020 → **2026 NOW** (pulsing red dot) → green arrow to "Databricks + AI"

### Speaker Notes
> "Underwriting has been ripe for disruption for at least the last 15 years. I used a rating and underwriting platform 20 years ago as a young analyst out of college — and I'm now on-site with one of the largest health plans in the country, and their entire block renewal process — thousands of groups, millions in margin — depends on one person and one spreadsheet."
>
> "The right solution isn't to create a new front end to a manual process. The right solution is to understand the process back to first principles and automate that."
>
> "No one even knows how long it takes to do a quote. There's no consistency across any of these processes."
>
> "What I find is that the people doing this work are incredibly sophisticated. One underwriter I observed considers the risk of losing the medical business, the broker relationship dynamics, the competitive threat — and then balances the entire block against a margin target. That's portfolio optimization. She's doing it in Excel. The judgment is world-class; the tool is 15 years behind the work."

**Tone:** Empathetic. The people are sophisticated; the infrastructure hasn't caught up.

---

## Slide 4b — NAIC AI Guidelines
**File:** `slide_04b_naic_ai.html`

### Visual
- 6-row table: dark header, alternating row stripes
- Green "chip" badges for Databricks products (Unity Catalog, MLflow, AI Gateway, etc.)
- Red callout at bottom with the "human in the loop" key insight

### Speaker Notes
> "Here's why this matters right now. The NAIC Model Bulletin was adopted in December 2023, and states are actively adopting it. If you're using AI anywhere in underwriting, rating, pricing, claims, or fraud detection — and you should be — you need a written AI Systems Program."
>
> "The good news is that Databricks natively handles about 80% of these requirements through platform capabilities you're already using or can turn on."
>
> "The key insight for this audience: the NAIC bulletin explicitly says that a 'human in the loop' is not, by itself, a safe harbor. The human review must be meaningful, appropriately informed, and capable of detecting or correcting an erroneous or discriminatory output. That's exactly how Genie is designed — it shows its work, traces to source, and presents the evidence so the human making the call is genuinely informed."
>
> "And here's the part that should concern anyone still running underwriting in Excel: the bulletin covers vendor-supplied AI too. If your underwriting process uses any predictive model — even one from a third party — you're accountable for explaining and validating those decisions. Excel doesn't give you lineage. It doesn't give you audit trails. Databricks does."

---

## Slide 4c — Rx Rebates: Same Data, Different Questions, One Agent
**File:** `slide_04c_rx_rebates.html`

### Visual
- Amber-themed (regulatory transparency)
- Stat pill in top-right: "6 Teams in one rebate lifecycle"
- 6-row persona table: Sales/AE, Underwriter, Contract Mgr, Operations, Finance, Compliance
- Each persona has a unique color, their role, and an italic example question
- Amber callout at bottom: "Same Genie Agent. Same governed Metric Views. Same data."

### Speaker Notes
> "Let me make this concrete. In an Rx Rebate program, there are 5 to 6 teams involved — from the account executive who sold the rebate guarantee, to the underwriter who priced it, to the contract manager negotiating with pharma, to operations implementing the formulary, to finance tracking the accruals, to compliance making sure the passthrough meets the new transparency rules."
>
> "Today, every one of these teams has their own spreadsheet, their own extract, their own version of the numbers. The account exec doesn't know what the contract manager negotiated. The underwriter doesn't know what finance is accruing. And when the regulator asks 'show me the audit trail from manufacturer payment to member passthrough' — nobody can produce it without weeks of manual reconciliation."
>
> "Now imagine one governed Genie Agent backed by certified Metric Views over the same unified data. Same data. Same definitions. Same truth. Different questions — answered in seconds, not weeks."

**Tone:** This is the "aha" slide. The audience sees their own org chart in this table.

---

## Slide Sequence — The Regulatory Crescendo

| Slide | Theme | Forcing Function |
|-------|-------|-----------------|
| **4** — Underwriting | The industry problem | 15 years of Excel-based processes that don't scale |
| **4b** — NAIC AI | Regulatory: AI governance | If you're using AI in insurance, you're accountable |
| **4c** — Rx Rebates | Regulatory: Transparency | Bipartisan pressure on PBM reporting — can't manage in spreadsheets |

Each slide raises the stakes. By the time you get to Slide 5 (Risk Adjustment / CMS Python), the audience understands that the regulatory environment is closing in from multiple directions simultaneously.

---

*Batch 2 of 4 · Slides 4–4c complete*
*Next: Batch 3 — Slides 5–7 (Risk Adjustment → Unified Vision → Genie)*
