# L100 — Healthcare Finance Webinar Demo: System Constitution

## Overview

**Project:** Healthcare Finance Webinar Demo Data Product
**Schema:** `home_matthew_giglia.webinar_demo`
**Workspace:** FEVM (Azure)
**Purpose:** Purpose-built synthetic data product for the Sep 17, 2026 Healthcare Finance Webinar Genie One demo. Designed to support 4 demo beats with realistic health plan financial, quality, utilization, and value-based care data grounded in real-world AHP (Accountable Health Partners) / UR Medicine structure.
**Audience:** 340+ webinar registrants, ~50% business decision-makers (CFOs, VPs Finance, Actuaries)

---

## Component Inventory

### Bundle 1: Data Foundation (`webinar-demo-data`)
Deploys tables and metric views via DAB. This is the governed data layer.

| Component | Type | Count |
|---|---|---|
| Gold tables | Delta tables | 8 |
| Metric views | `CREATE VIEW WITH METRICS` | 3 |
| UC Glossary Pages | Business term definitions | 15+ |

### Bundle 2: AI/BI Experience (`webinar-demo-aibi`)
Deploys the Genie Agent and AI/BI Dashboard. Depends on Bundle 1.

| Component | Type | Count |
|---|---|---|
| Genie Agent | Genie Space (Agent Mode) | 1 |
| AI/BI Dashboard | Lakeview Dashboard | 1 |

### Deploy Order
```
Bundle 1 (webinar-demo-data) → Bundle 2 (webinar-demo-aibi)
```
Bundle 2 references tables and metric views created by Bundle 1. Always deploy data first.

---

## Data Model

### Layer 1: Core Financial (Beat 1 — CFO Morning Briefing)

| Table | Grain | Est. Rows | Key Columns |
|---|---|---|---|
| `gold_financial_monthly` | LOB × state × plan_type × year_month | ~2,400 | lob, state, plan_type, year_month, paid_amount, premium_amount, member_months, avoidable_paid_amount |
| `dim_budget` | LOB × year_month | ~48 | lob, year_month, target_mlr, target_pmpm, budget_premium |
| `dim_member` | member_id | ~50,000 | member_id, lob, state, age_band, gender, plan_type, risk_score, cost_percentile, open_gaps_count |

### Layer 2: Quality & Utilization (Beat 2 — Persona Rotation)

| Table | Grain | Est. Rows | Key Columns |
|---|---|---|---|
| `gold_quality_measures` | measure_id × LOB × year_month | ~288 | measure_id, measure_name, lob, year_month, current_rate, star_3_cutpoint, star_4_cutpoint, eligible_count, gap_count |
| `gold_utilization_monthly` | LOB × state × year_month | ~2,400 | lob, state, year_month, ip_admits, ed_visits, readmissions, avoidable_ed_visits, avoidable_ip_admits |

### Layer 3: VBC / ACO (Beat 3 — CFO Calendar + Meeting Prep)

| Table | Grain | Est. Rows | Key Columns |
|---|---|---|---|
| `fact_vbc_performance` | aco_id × measure × quarter | ~120 | aco_id, measure_name, quarter, actual_value, target_value, benchmark_value |
| `dim_aco_contract` | aco_id | 5 | aco_id, aco_name, parent_system, exec_medical_director, contract_type, payers, region, attributed_members, gainsharing_split |
| `dim_provider_network` | provider_id × aco_id | ~200 | provider_id, provider_name, specialty, aco_id, attributed_members, cost_efficiency_score |

---

## Metric Views

| Metric View | Source Table | Dimensions | Measures |
|---|---|---|---|
| `mv_financial` | `gold_financial_monthly` | lob, state, plan_type, year_month | `mlr` = SUM(paid_amount) / NULLIF(SUM(premium_amount), 0); `paid_pmpm` = SUM(paid_amount) / NULLIF(SUM(member_months), 0); `premium_pmpm` = SUM(premium_amount) / NULLIF(SUM(member_months), 0); `avoidable_share` = SUM(avoidable_paid_amount) / NULLIF(SUM(paid_amount), 0); `member_months` = SUM(member_months) |
| `mv_quality` | `gold_quality_measures` | measure_id, measure_name, lob, year_month | `current_rate` = AVG(current_rate); `gap_count` = SUM(gap_count); `eligible_count` = SUM(eligible_count); `gap_closure_rate` = 1 - (SUM(gap_count) / NULLIF(SUM(eligible_count), 0)) |
| `mv_vbc_performance` | `fact_vbc_performance` JOIN `dim_aco_contract` | aco_name, measure_name, quarter, region | `actual_value` = SUM(actual_value); `target_value` = SUM(target_value); `variance` = SUM(actual_value) - SUM(target_value) |

---

## Cross-Cutting Patterns

### Governance
- All tables in `home_matthew_giglia.webinar_demo` schema
- Metric views are the authoritative source for all KPIs — Genie Agent queries metric views, not raw tables
- Table and column comments are mandatory (Genie uses them for context)
- All data is synthetic — `COMMENT ON TABLE` must include "Synthetic demo data" disclaimer

### Data Narrative (Planted Story)
The synthetic data must tell a specific, pre-determined story for each demo beat:

| Beat | Narrative | Key Numbers |
|---|---|---|
| 1 | Medicaid is underwater, MA is borderline, Commercial is healthy | Medicaid MLR 106%, MA 100.3%, Commercial 87%, Individual 83% |
| 1 | Problem concentrated in 3 states | FL, TX, CA have 2× avoidable ED rate vs plan average |
| 1 | Budget variance | Medicaid $1.2M behind budget YTD, MA $0.3M behind |
| 2 | MA risk scores trending up but premium hasn't kept pace | Risk score +0.05 YoY, premium PMPM flat |
| 2 | Quality measures below 4-star | BCS at 72% (4-star cutpoint 74%), HbA1c at 58% (cutpoint 60%) |
| 2 | High-risk members with open gaps | Top 10 members have 8+ open gaps, NBA recommends outreach |
| 3 | AHP shared savings performing well | $2.1M YTD, quality score 4.2 stars |
| 3 | TCOC PMPM trending up | +3% QoQ driven by specialty pharmacy (GLP-1) |
| 3 | Conversation focus | GLP-1 utilization management + diabetes care gap closure |

### Naming Conventions
- Tables: `gold_*` for fact/aggregate, `dim_*` for dimensions, `fact_*` for transactional
- Metric views: `mv_*`
- All lowercase with underscores
- Date columns: `year_month` (DATE type, first of month)
- Quarter columns: `quarter` (STRING, format "2026-Q1")

### AHP Realism Rules
- Use real entity name: "Accountable Health Partners (AHP)"
- Use real payer names: Excellus BCBS, MVP Health Care
- Use real hospital names: Strong Memorial, Highland, F.F. Thompson, Noyes Memorial
- Use real quality measures: HbA1c, Diabetic Eye Exam, BP Control, BCS, CCS
- Use real gainsharing split: 60% PCP / 25% Specialist / 15% Hospital
- Use FICTIONAL person: Dr. Sarah Chen, Executive Medical Director
- Use FICTIONAL financial numbers for all dollar amounts

---

## Genie Agent Design

### Agent Name
**Healthcare Finance Intelligence**

### Agent Mode
Enabled (Agent Mode, not classic Genie Space)

### Tables Attached
All 8 tables + 3 metric views (11 total)

### Instructions
See L200-B for full instruction set. Key principles:
- Always query metric views for KPIs, not raw tables
- Normalize cross-LOB comparisons per member-month (PMPM)
- "How is X trending" → monthly time series using year_month
- Never expose member PII (no full_name even if available)
- Include budget variance when discussing financial performance
- For VBC questions, always identify the ACO and its executive medical director

### Glossary Pages
See L200-C for full glossary. Minimum 15 terms covering:
- Financial: MLR, PMPM, IBNR, Avoidable Spend, Premium, Paid Claims
- Quality: HEDIS, STARS, Care Gap, Gap Closure Rate, Star Cutpoint
- VBC: Shared Savings, TCOC, Attribution, Gainsharing, Clinically Integrated Network
- Organizational: AHP, UR Medicine, Excellus BCBS

---

## Design Document Index

| Doc | Title | Scope |
|---|---|---|
| **L100** | System Constitution (this document) | Overall architecture, data model, cross-cutting patterns |
| **L200-A** | Bundle 1: Data Foundation | Table DDL, synthetic data generation, metric view YAML |
| **L200-B** | Bundle 2: AI/BI Experience | Genie Agent config, instructions, AI/BI Dashboard |
| **L200-C** | UC Glossary Pages | Business term definitions for Genie ontology |
| **L300-A** | Table Schemas & Synthetic Data SQL | Complete DDL + INSERT statements with planted narrative |
| **L300-B** | Metric View YAML Definitions | Full CREATE VIEW WITH METRICS syntax |
| **L300-C** | Genie Agent Instructions & Benchmark Prompts | Full instruction text + test prompts for each demo beat |

> See [docs/diagrams/01_data_model.md] for entity-relationship diagram
> See [docs/diagrams/02_bundle_deploy.md] for deployment sequence
