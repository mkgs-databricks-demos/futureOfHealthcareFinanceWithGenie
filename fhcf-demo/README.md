# The Future of Healthcare Finance with Genie

Declarative Automation Bundle for the **Databricks HLS Quarterly Webinar** (September 17, 2026). Demonstrates a Genie Agent over synthetic healthcare finance data — MLR trending, HEDIS quality measures, VBC performance, and avoidable spend analytics.

This repo contains everything needed to reproduce the demo end-to-end: the data bundle, the slide deck, the design documents, and the session logs that record how it was built.

---

## Table of Contents

1. [Repository Layout](#repository-layout)
2. [Prerequisites](#prerequisites)
3. [Quick Start — Deploy the Data Bundle](#quick-start--deploy-the-data-bundle)
4. [Quick Start — Run the Slide Deck](#quick-start--run-the-slide-deck)
5. [What Gets Created](#what-gets-created)
6. [The Demo: Talk Track and Beats](#the-demo-talk-track-and-beats)
7. [Planted Narrative](#planted-narrative)
8. [Ontology Layer — UC Pages and Knowledge Domain](#ontology-layer--uc-pages-and-knowledge-domain)
9. [Customizing for Your Own Demo](#customizing-for-your-own-demo)
10. [Design Documents](#design-documents)
11. [Session Logs](#session-logs)
12. [References](#references)

---

## Repository Layout

```
futureOfHealthcareFinanceWithGenie/
├── README.md                          # Repo-level overview (you are here if viewing from GitHub)
├── LICENSE
│
├── fhcf-demo/                         # ── Declarative Automation Bundle ──
│   ├── databricks.yml                 # Bundle config (variables: catalog, schema, warehouse)
│   ├── README.md                      # THIS FILE — full reproduction guide
│   ├── PROJECT_MEMORY.md              # Agent working memory (IDs, conventions, decisions)
│   ├── resources/
│   │   ├── healthcare_finance.schema.yml                   # UC schema resource
│   │   ├── seed_data.job.yml                               # Seed job definition
│   │   └── healthcare_finance_intelligence.genie_space.yml # Genie Agent resource (14 sources, 7 questions)
│   ├── src/
│   │   └── seed_all_data.py           # 26-cell notebook: widgets → DDL → seed data → metric views → validation
│   └── fixtures/
│       └── sessions/                  # Chronological build log (7 sessions)
│
├── webinar_slides/                    # ── Presentation Slide Deck ──
│   ├── app.py                         # Flask server (serves presenter.html as entry point)
│   ├── app.yaml                       # Databricks App manifest
│   ├── requirements.txt               # flask>=3.0
│   ├── presenter.html                 # Presenter console (keyboard nav, grid overview, fullscreen)
│   ├── slide-system.css               # Shared Databricks-brand styling
│   ├── slide_01_opening.html          # → slide_10_appendix.html (13 slides)
│   └── batch_01..04_*.md              # Slide-by-slide design notes and speaker notes
│
└── webinar_demo_docs/                 # ── Design Documents ──
    └── docs/
        ├── design/
        │   ├── L100_system_constitution.md        # System overview, data model, demo beats
        │   ├── L200-A_bundle1_data_foundation.md   # Table schemas, seed data design
        │   ├── L200-B_bundle2_aibi_experience.md   # Genie Agent and dashboard design
        │   ├── L200-C_glossary_pages.md             # 18 UC Page definitions (4 subdomains)
        │   ├── L300-A_table_schemas_and_data.md     # Column-level DDL specs
        │   ├── L300-B_metric_view_definitions.md    # Metric view YAML and SQL
        │   ├── L300-C_genie_agent_instructions.md   # Genie instruction set and rules
        │   └── L300-D_seed_data_sql.md              # INSERT statement templates
        └── diagrams/
            ├── 01_data_model.md                     # Mermaid ER diagram
            └── 02_bundle_deploy.md                  # Mermaid deployment sequence
```

---

## Prerequisites

| Requirement | Details |
| --- | --- |
| Databricks workspace | Any workspace with Unity Catalog enabled |
| Databricks CLI | v0.230+ (or use the workspace UI deployment panel) |
| Unity Catalog catalog | A catalog you can create schemas in (default: `hls_fde`) |
| SQL warehouse | A serverless SQL warehouse named `demo-warehouse` (or override the `warehouse_id` variable) |
| Permissions | `CREATE SCHEMA` on the target catalog; `USE CATALOG`; `CREATE TABLE` / `CREATE VIEW` |
| MCP connector (optional) | Google Calendar connector for Beat 3a (calendar integration) |

---

## Quick Start — Deploy the Data Bundle

### Step 1: Clone the repo

```bash
git clone https://github.com/mkgs-databricks-demos/futureOfHealthcareFinanceWithGenie.git
cd futureOfHealthcareFinanceWithGenie/fhcf-demo
```

Or, if working directly in the Databricks workspace, the repo is already at:  
`/Workspace/Users/<you>/futureOfHealthcareFinanceWithGenie/fhcf-demo/`

### Step 2: Configure variables

Edit `databricks.yml` or pass overrides at deploy time:

| Variable | Default | Override for your workspace |
| --- | --- | --- |
| `catalog` | `hls_fde` | Your UC catalog name |
| `schema` | `healthcare_finance` | Any schema name (dev mode auto-prefixes) |
| `warehouse_id` | lookup: `demo-warehouse` | Your SQL warehouse name or ID |

### Step 3: First deploy (creates schema + job)

```bash
databricks bundle deploy --target dev
```

Or use the **deployment rocket** icon in the workspace sidebar and click **Deploy**.

### Step 4: Seed the data

```bash
databricks bundle run seed_data --target dev
```

Or run `[FHCF] Seed Healthcare Finance Data` from the Jobs UI / Deployments panel. This creates all 8 tables and 6 metric views.

### Step 5: Redeploy (creates Genie space)

```bash
databricks bundle deploy --target dev
```

The Genie Agent API validates that tables exist before creating the space. This second deploy registers the Genie space now that the data layer is present.

### Step 6: Validate

Open `src/seed_all_data` and run the final validation cell (cell 23) to confirm all planted narrative values hold. Or open the Genie space and try the sample questions.

### Production deploy

For a clean production deployment:

```bash
databricks bundle deploy --target prod
databricks bundle run seed_data --target prod
databricks bundle deploy --target prod
```

---

## Quick Start — Run the Slide Deck

The slide deck is a standalone Flask app in `webinar_slides/`. It can be run as a **Databricks App** or locally.

### Option A: Databricks App

1. Navigate to **Apps** in the workspace sidebar
2. Create a new app pointing to the `webinar_slides/` directory
3. The app serves `presenter.html` at the root URL

### Option B: Local

```bash
cd webinar_slides
pip install -r requirements.txt
python app.py
# Open http://localhost:8000
```

### Presenter Controls

| Key | Action |
| --- | --- |
| `→` / `↓` / `Space` | Next slide |
| `←` / `↑` | Previous slide |
| `F` | Enter fullscreen (presentation mode) |
| `G` | Toggle grid overview |
| `Home` / `End` | First / last slide |
| `Escape` | Exit fullscreen |

### Slide Deck (13 slides)

| # | Title | Arc |
| --- | --- | --- |
| 1 | What I'm Seeing This Week | Opening — field credibility |
| 2 | These Aren't Cyclical — They're Structural | Industry trends (PWC data) |
| 3 | Sister Teams. Same Function. No Shared Context. | The silo problem |
| 4 | Underwriting: 15 Years Overdue | Regulatory arc |
| 4b | NAIC AI Guidelines | Regulatory arc |
| 4c | Rx Rebates: Same Data, Different Questions | Persona rotation |
| 5 | Risk Adjustment: CMS Changed the Game | SAS → Python transition |
| 6 | The Unified Data Vision | Architecture slide |
| 6b | Enterprise Context: Genie Ontology | Ontology explainer |
| 7 | Genie: Data-Smart AI Coworker | Transition to live demo |
| 8 | Genie One: Four Beats, One Story | Demo reference card (rehearsal only) |
| 9 | Customer Proof Points | HSS, Humana, Premier |
| 10 | Appendix: References & Footnotes | Sourced references |

Detailed speaker notes and design rationale are in the `batch_*.md` files alongside the HTML.

---

## What Gets Created

### Bundle Resources

| Resource | Name | Description |
| --- | --- | --- |
| UC Schema | `<catalog>.healthcare_finance` | All tables and views land here |
| Job | `[FHCF] Seed Healthcare Finance Data` | Runs `seed_all_data` notebook to create and populate all objects |
| Genie Space | Healthcare Finance Intelligence | 14 data sources, 7 sample questions, lean instructions backed by metric view semantic metadata |

### 8 Delta Tables

| Table | Rows | Description |
| --- | --- | --- |
| `dim_aco_contract` | 5 | ACO/CIN reference data (ACO-001 = AHP, Dr. Sarah Chen) |
| `dim_budget` | 48 | Monthly budget targets by LOB (4 LOBs x 12 months) |
| `dim_member` | 50,000 | Member demographics and risk profiles |
| `dim_provider_network` | 200 | Provider-level network data by ACO |
| `gold_financial_monthly` | 480 | Monthly financial aggregates by LOB/state/plan_type |
| `gold_quality_measures` | 288 | HEDIS quality measures by LOB/month |
| `gold_utilization_monthly` | 480 | Monthly utilization by LOB/state |
| `fact_vbc_performance` | 120 | Quarterly VBC performance by ACO/measure |

### 6 Metric Views

| View | Source | Key Measures |
| --- | --- | --- |
| `mv_financial` | gold_financial_monthly | MLR, paid PMPM, premium PMPM, avoidable share of spend |
| `mv_quality` | gold_quality_measures | Current rate, gap closure rate, distance to 4-star, estimated star rating |
| `mv_vbc_performance` | fact_vbc_performance JOIN dim_aco_contract | Shared savings YTD, TCOC PMPM, quality score, pharmacy PMPM |
| `mv_utilization` | gold_utilization_monthly | IP/ED per 1K, readmission rate, avoidable ED/IP rates |
| `mv_budget_variance` | gold_financial_monthly JOIN dim_budget | Actual vs target MLR, premium/claims variance, budget attainment |
| `mv_member_risk` | dim_member | Member count, avg risk score, high-risk count/pct, gap rate by risk tier |

All metric views carry full semantic metadata — `display_name`, `synonyms`, `format`, and detailed `comment` on every column, plus `COMMENT ON VIEW` with authoritative-source guidance. The Genie instruction is intentionally lean: it contains only behavioral routing rules, `MEASURE()` syntax examples, and synthesis directives. Domain definitions (MLR, PMPM, TCOC, HEDIS measure-to-domain mappings, AHP synonyms) live in the metric view metadata, not the instruction text.

---

## The Demo: Talk Track and Beats

The webinar follows a three-act structure:

### Act 1 — The Problem (Slides 1–4c)

Industry trends, silo pain, regulatory forcing functions (underwriting, NAIC AI, Rx rebates). Establishes credibility through field experience and empathetic framing.

### Act 2 — The Solution (Slides 5–7)

Risk adjustment modernization (SAS → Python), the unified data vision (governed data + ontology + Genie), and the transition to live demo.

### Act 3 — The Live Demo (4 Beats)

Switch from slides to the Genie Agent. Slide 8 is a rehearsal-only reference card.

| Beat | Prompt | What It Shows | Data Sources |
| --- | --- | --- | --- |
| **1a** | "Give me my morning briefing — what needs attention today across our financial performance, quality measures, and care management? Flag anything that's off track." | Genie as a scheduled morning intelligence agent. Flags Medicaid MLR > 100%, BCS and HbA1c below 4-star, high avoidable ED states. | mv_budget_variance, mv_quality, mv_utilization |
| **1b** | "Tell me more about the quality measures at risk. Which HEDIS measures are below 4-star cutpoints for our MA population?" | Drill-down into quality. Genie routes to the governed metric view, not raw tables. | mv_quality |
| **2a** | "Show me the top 10 highest-risk members with the most open care gaps." | Member-level detail with risk scores, care gap counts, and NBA recommendations. | dim_member |
| **2b** | "How many of those high-risk members are in states with high avoidable ED rates?" | Cross-referencing member data with utilization patterns (FL, TX, CA). | dim_member, mv_utilization |
| **3a** | *(Calendar integration — MCP connector)* | Shows Genie accessing external tools (Google Calendar) to find the upcoming meeting with Dr. Chen. | External |
| **3b** | "Tell me about Accountable Health Partners. What's their VBC performance?" | AHP shared savings $2.1M vs $1.8M target. Uses synonyms (AHP → ACO-001). | mv_vbc_performance |
| **3c** | "What's driving the TCOC increase at AHP? Is it pharmacy?" | Drill into pharmacy PMPM (+8% QoQ from GLP-1 drugs). | mv_vbc_performance |
| **3d** | "Prepare a brief for my meeting with Dr. Chen — key talking points." | Genie synthesizes a structured meeting brief with numbered talking points across shared savings, quality gaps, and pharmacy cost pressure. | mv_vbc_performance, mv_quality |

### Act 4 — The Close (Slides 9–10)

Customer proof points (HSS, Humana, Premier) and appendix with sourced references.

---

## Planted Narrative

The seed data encodes a deterministic narrative. Every value is intentional — designed to create a compelling story when the demo beats are executed in order. The validation cell (cell 23 in the seed notebook) asserts these hold:

| Signal | Expected Value | Why It Matters |
| --- | --- | --- |
| Medicaid MLR | \~106% | Triggers the "off track" flag in Beat 1a |
| MA MLR | \~100% | Borderline — interesting discussion point |
| Commercial MLR | \~87% | Healthy — shows contrast |
| Individual MLR | \~83% | Healthy — shows contrast |
| FL, TX, CA avoidable ED rate | 2x other states (14% vs 7%) | Drives the geographic pattern in Beat 2b |
| BCS (Breast Cancer Screening) | 72% (cutpoint 74%) | Below 4-star — flagged in Beat 1b |
| HbA1c (Diabetes Control) | 58% (cutpoint 60%) | Below 4-star — flagged in Beat 1b |
| AHP Shared Savings | $2.1M YTD vs $1.8M target | Positive story for Beat 3b |
| AHP TCOC PMPM | +3% QoQ | Cost pressure narrative for Beat 3c |
| AHP Pharmacy PMPM | +8% QoQ (GLP-1) | Root cause for Beat 3c |

---

## Ontology Layer — UC Pages and Knowledge Domain

Beyond the data and Genie Agent, the demo includes a full **semantic ontology layer** built on Unity Catalog Pages and a knowledge domain (`mkgs_hc_finance`). This was created post-deployment (see the [UC Pages & Domain Setup session](fixtures/sessions/2026-09-17_uc-pages-and-domain-setup.md)).

### 18 UC Glossary Pages

| Subdomain | Terms |
| --- | --- |
| Financial | Medical Loss Ratio (MLR), Per Member Per Month (PMPM), Avoidable Spend, Incurred But Not Reported (IBNR), Premium, Line of Business (LOB) |
| Quality | HEDIS, STARS Rating, Care Gap, Gap Closure Rate |
| VBC | Total Cost of Care (TCOC), Shared Savings, Attribution, Gainsharing, Clinically Integrated Network (CIN) |
| Organizational | Accountable Health Partners (AHP), UR Medicine, Excellus BlueCross BlueShield |

Each page has a definition, business use, data usage guidance, synonyms, and links to relevant tables and the Genie space. Pages are created as **drafts** and must be published from the Discover UI.

### Knowledge Domain

The `mkgs_hc_finance` domain registers all 15 data assets (8 tables + 6 metric views + 1 Genie space) alongside the 18 pages. This creates a single discoverable entry point for the entire healthcare finance ontology.

### Reproducing the Ontology

1. Navigate to the target knowledge domain in Discover
2. Provide the glossary design document (`webinar_demo_docs/docs/design/L200-C_glossary_pages.md`) to Genie Code and ask it to bulk-create pages
3. Register tables, metric views, and the Genie space in the domain
4. Update the domain description
5. Publish pages individually from the Discover UI

---

## Customizing for Your Own Demo

### Change the catalog and schema

Edit `databricks.yml` variables:

```yaml
variables:
  catalog:
    default: your_catalog
  schema:
    default: your_schema
  warehouse_id:
    lookup:
      warehouse: "your-warehouse-name"
```

All table references in the Genie space use `${resources.schemas.*}` interpolation, so they resolve automatically per target.

### Change the target workspace

Update the `workspace.host` under your target:

```yaml
targets:
  prod:
    mode: production
    workspace:
      host: https://your-workspace.cloud.databricks.com
```

### Modify the narrative

Edit the seed data in `src/seed_all_data.py`. The notebook is organized as:

* Cells 1–2: Widget parameters (catalog, schema)
* Cells 3–10: DDL (CREATE TABLE statements)
* Cells 11–18: Seed data (INSERT statements with the planted narrative values)
* Cells 19–22: Metric view creation (CREATE VIEW WITH METRICS)
* Cell 23: Validation queries that assert the planted narrative

Change the INSERT values to encode your own story, then update the validation cell to match.

### Modify the Genie Agent

Edit `resources/healthcare_finance_intelligence.genie_space.yml`. Key sections:

* `sample_questions` — The 7 prompts shown in the Genie space UI
* `text_instructions` — The consolidated instruction set (domain context, 12 behavioral rules, MEASURE() syntax)
* `data_sources.tables` — The 14 table identifiers (8 tables + 6 metric views)

### Modify the slides

Each slide is a self-contained HTML file in `webinar_slides/`. Edit directly — they use shared CSS from `slide-system.css` and Databricks brand conventions (DM Sans, Lava 600 `#FF3621`, Navy 800 `#1B3139`). Speaker notes and design rationale are in the corresponding `batch_*.md` files.

---

## Design Documents

The `webinar_demo_docs/docs/design/` directory contains the full design specification used to build this demo:

| Document | Level | Content |
| --- | --- | --- |
| `L100_system_constitution.md` | L100 | System overview, component inventory, data model, demo beats, deploy order |
| `L200-A_bundle1_data_foundation.md` | L200 | Table schemas, seed data design, bundle structure |
| `L200-B_bundle2_aibi_experience.md` | L200 | Genie Agent design, instruction set, benchmark prompts |
| `L200-C_glossary_pages.md` | L200 | 18 UC Page definitions across 4 subdomains |
| `L300-A_table_schemas_and_data.md` | L300 | Column-level DDL specifications |
| `L300-B_metric_view_definitions.md` | L300 | Metric view YAML and SQL definitions |
| `L300-C_genie_agent_instructions.md` | L300 | Complete Genie instruction set and behavioral rules |
| `L300-D_seed_data_sql.md` | L300 | INSERT statement templates with narrative values |

Diagrams (Mermaid format) are in `webinar_demo_docs/docs/diagrams/`.

---

## Session Logs

The `fixtures/sessions/` directory contains a chronological record of every build session (all from 2026-09-17). These document the decisions, problems, and solutions encountered while building the demo:

| Session | Summary |
| --- | --- |
| [Initial Bundle Setup](fixtures/sessions/2026-09-17_initial-bundle-setup.md) | Stood up the bundle: 8 tables, 3 metric views, seed job |
| [DDL & Metric View Improvements](fixtures/sessions/2026-09-17_ddl-metric-view-improvements.md) | Added PK/FK constraints, liquid clustering, 3 new metric views |
| [Genie Space & Catalog Migration](fixtures/sessions/2026-09-17_genie-space-and-catalog-migration.md) | Built Genie Agent, migrated dev catalog, two-phase deploy |
| [Genie Space Testing & Instruction Tuning](fixtures/sessions/2026-09-17_genie-space-testing-and-instruction-tuning.md) | Validated all 7 beats, fixed Beat 3d directive, 7/7 passing |
| [Metric View Metadata & Instruction Trim](fixtures/sessions/2026-09-17_metric-view-metadata-and-instruction-trim.md) | Migrated glossary into metric view metadata, trimmed instruction 25% |
| [Prod Deploy & Validation](fixtures/sessions/2026-09-17_prod-deploy-and-validation.md) | First production deployment, all beats confirmed on prod |
| [UC Pages & Domain Setup](fixtures/sessions/2026-09-17_uc-pages-and-domain-setup.md) | Created 18 UC Pages, registered assets in knowledge domain |

---

## References

* [Declarative Automation Bundles in the workspace](https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-bundles)
* [Declarative Automation Bundles configuration reference](https://docs.databricks.com/aws/en/dev-tools/bundles/reference)
* [Metric Views documentation](https://docs.databricks.com/en/sql/language-manual/sql-ref-metric-views.html)
* [Genie Spaces API](https://docs.databricks.com/en/genie/index.html)
* [Unity Catalog Pages](https://docs.databricks.com/en/discover/pages.html)
* Design docs: `webinar_demo_docs/docs/design/` (L100–L300 at repo root)
