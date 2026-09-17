# Session: UC Pages & Domain Setup for Healthcare Finance Ontology

**Date:** 2026-09-17  
**Bundle:** fhcf-demo  
**Scope:** Created 18 UC Glossary Pages from design document, registered all schema assets and the Genie space in the `mkgs_hc_finance` knowledge domain, and configured the domain description.

---

## Context

With the production schema (`hls_fde.healthcare_finance`) deployed and the Genie Agent live (ID: `01f1b2a18cde1845b9937112d70fe765`), this session adds the **semantic ontology layer** — Unity Catalog Pages that define the business terms the Genie Agent uses to ground its answers. These pages live in the `mkgs_hc_finance` knowledge domain alongside the tables, metric views, and Genie space.

The source material was a pre-authored design document:

```
webinar_demo_docs/docs/design/L200-C_glossary_pages.md
```

This document defined 18 healthcare finance terms organized across four subdomains: Financial, Quality, VBC (Value-Based Care), and Organizational.

## What Are UC Pages?

Unity Catalog Pages are structured metadata objects that define business terms for a knowledge domain. Unlike table comments or column descriptions (which describe *data*), Pages describe *concepts* — the business logic, regulatory context, and organizational knowledge that make analytical answers *correct* (not just technically accurate).

Each Page has:

* **Name** — The canonical business term (e.g., "Medical Loss Ratio")
* **Description** — A one-line summary (≤160 chars), used for search and quick reference
* **Body** — Markdown content structured with `## Definition`, `## Business use`, and `## Data usage` sections
* **Synonyms** — Alternate names and abbreviations (e.g., MLR, PMPM, TCOC)
* **Related Assets** — Links to tables, metric views, and Genie spaces that are relevant to the term
* **Sources** — References to the design documents or materials the page was derived from

Pages are created in **draft** state and must be published individually from the Discover UI.

## Workflow: How the 18 Pages Were Created

### Step 1 — Source Document Review

The design document `L200-C_glossary_pages.md` was read and analyzed. It contained 18 terms organized into four domains:

| Domain | Terms | Count |
| --- | --- | --- |
| Financial | Medical Loss Ratio (MLR), Per Member Per Month (PMPM), Avoidable Spend, Incurred But Not Reported (IBNR), Premium, Line of Business (LOB) | 6 |
| Quality | HEDIS, STARS Rating, Care Gap, Gap Closure Rate | 4 |
| VBC | Total Cost of Care (TCOC), Shared Savings, Attribution, Gainsharing, Clinically Integrated Network (CIN) | 5 |
| Organizational | Accountable Health Partners (AHP), UR Medicine, Excellus BlueCross BlueShield | 3 |

Each term in the source document had a consistent structure: Definition, Business Context, Data Usage, and Related Terms.

### Step 2 — Schema Reference Update

The source document referenced the development schema (`home_matthew_giglia.webinar_demo`). Since the production schema was now live, **all table references were updated** to `hls_fde.healthcare_finance.*`. For example:

* `mv_financial` → `hls_fde.healthcare_finance.mv_financial`
* `gold_financial_monthly` → `hls_fde.healthcare_finance.gold_financial_monthly`
* `fact_vbc_performance` → `hls_fde.healthcare_finance.fact_vbc_performance`

### Step 3 — Genie Space Linking

The production Genie Agent ([Healthcare Finance Intelligence](https://fevm-hls-fde.cloud.databricks.com/genie/rooms/01f1b2a18cde1845b9937112d70fe765)) was identified via workspace search and added as a **related asset** on every page. This creates bidirectional discoverability: users browsing a glossary term can navigate directly to the conversational agent that queries the underlying data.

### Step 4 — Bulk Page Proposal

All 18 pages were submitted as a single batch proposal to the `mkgs_hc_finance` domain. The proposal system performed overlap detection and flagged 4 pages:

| Flagged Page | Alleged Overlap | Verdict |
| --- | --- | --- |
| Gap Closure Rate | Care Gap | **Soft overlap** — metric vs. concept. Gap Closure Rate is a performance KPI (percentage); Care Gap is a member status (missing a service). Distinct pages warranted. |
| Total Cost of Care | Line of Business | **False positive** — TCOC is a VBC financial metric; LOB is an insurance segmentation dimension. No meaningful overlap. |
| Attribution | Per Member Per Month | **False positive** — Attribution is a member-assignment methodology; PMPM is a normalization unit. Different concepts that both reference "members." |
| UR Medicine | Line of Business | **False positive** — UR Medicine is a specific organization; LOB is an insurance product type. Zero conceptual overlap. |

All 4 flags were reviewed and determined to be false positives (or acceptably soft overlaps). The decision was made to create all 18 pages.

### Step 5 — Bulk Page Creation

All 18 pages were created as **drafts** in a single batch operation. Zero failures.

**Full inventory of created pages:**

| # | Name | Synonyms | Related Assets |
| --- | --- | --- | --- |
| 1 | Medical Loss Ratio | MLR | mv_financial, gold_financial_monthly, Genie space |
| 2 | Per Member Per Month | PMPM | mv_financial, Genie space |
| 3 | Avoidable Spend | — | gold_financial_monthly, gold_utilization_monthly, Genie space |
| 4 | Incurred But Not Reported | IBNR | Genie space (no direct table — actuarial concept) |
| 5 | Premium | Premium Revenue | gold_financial_monthly, mv_financial, Genie space |
| 6 | Line of Business | LOB | mv_financial, gold_financial_monthly, Genie space |
| 7 | HEDIS | Healthcare Effectiveness Data and Information Set | gold_quality_measures, mv_quality, Genie space |
| 8 | STARS Rating | Star Rating, CMS Star Rating, Medicare Star Rating | gold_quality_measures, Genie space |
| 9 | Care Gap | Quality Gap, Open Gap | gold_quality_measures, dim_member, Genie space |
| 10 | Gap Closure Rate | — | mv_quality, Genie space |
| 11 | Total Cost of Care | TCOC | fact_vbc_performance, Genie space |
| 12 | Shared Savings | — | fact_vbc_performance, Genie space |
| 13 | Attribution | Member Attribution | dim_aco_contract, dim_provider_network, Genie space |
| 14 | Gainsharing | Gain Sharing | dim_aco_contract, Genie space |
| 15 | Clinically Integrated Network | CIN | dim_aco_contract, Genie space |
| 16 | Accountable Health Partners | AHP | dim_aco_contract, Genie space |
| 17 | UR Medicine | University of Rochester Medicine, URMC | dim_aco_contract, Genie space |
| 18 | Excellus BlueCross BlueShield | Excellus BCBS, Excellus | dim_aco_contract, Genie space |

## Domain Asset Registration

After creating the pages, all data assets from `hls_fde.healthcare_finance` and the Genie space were registered in the `mkgs_hc_finance` domain. The schema was queried via `information_schema.tables` to get the complete and typed inventory:

### Tables (8)

| Table | Type | Purpose |
| --- | --- | --- |
| dim_aco_contract | MANAGED | ACO/CIN reference data |
| dim_budget | MANAGED | Monthly budget targets by LOB |
| dim_member | MANAGED | Member demographics and risk profile |
| dim_provider_network | MANAGED | Provider-level network data by ACO |
| fact_vbc_performance | MANAGED | Quarterly VBC performance by ACO/measure |
| gold_financial_monthly | MANAGED | Monthly financial aggregates by LOB/state |
| gold_quality_measures | MANAGED | HEDIS quality measure performance |
| gold_utilization_monthly | MANAGED | Monthly utilization aggregates |

### Metric Views (6)

| Metric View | Purpose |
| --- | --- |
| mv_budget_variance | Budget vs. actual variance |
| mv_financial | Financial KPIs (MLR, PMPM) |
| mv_member_risk | Population health risk stratification |
| mv_quality | HEDIS quality measure KPIs |
| mv_utilization | Utilization rates (IP/ED per 1K) |
| mv_vbc_performance | VBC contract performance KPIs |

### Genie Space (1)

| Name | ID |
| --- | --- |
| Healthcare Finance Intelligence | `01f1b2a18cde1845b9937112d70fe765` |

All 15 assets were added via `addAssetToCurrentDomain` in a single parallel batch (15/15 successful).

## Domain Description

The `mkgs_hc_finance` domain description was updated to reflect the complete asset inventory:

* **Subtitle:** Healthcare finance analytics — MLR, quality measures, VBC performance, and population health
* **Description:** Structured overview of the 8 tables, 6 metric views, Genie Agent, and 18-term ontology with schema reference and query conventions

## Subdomain Creation (Blocked)

Subdomain creation was attempted for Financial, Quality, and Value-Based Care. This requires governed tags in the format `mkgs_hc_finance/<subdomain>` to exist at the account level before the API can create subdomains.

Required tags (not yet created):

* `mkgs_hc_finance/Financial`
* `mkgs_hc_finance/Quality`
* `mkgs_hc_finance/Value-Based Care`

These must be created by an account admin via the Unity Catalog governed tags UI or API before subdomains can be established.

## Architecture Summary

The complete `mkgs_hc_finance` domain now has three layers:

```
┌─────────────────────────────────────────────────────────┐
│                  mkgs_hc_finance Domain                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Ontology Layer (18 UC Pages — DRAFT)                   │
│  ├── Financial: MLR, PMPM, Avoidable Spend, IBNR,       │
│  │              Premium, LOB                            │
│  ├── Quality:   HEDIS, STARS, Care Gap, Gap Closure     │
│  ├── VBC:       TCOC, Shared Savings, Attribution,      │
│  │              Gainsharing, CIN                        │
│  └── Org:       AHP, UR Medicine, Excellus BCBS         │
│                                                         │
│  Semantic Layer (6 Metric Views)                        │
│  ├── mv_financial, mv_quality, mv_utilization           │
│  ├── mv_vbc_performance, mv_budget_variance             │
│  └── mv_member_risk                                     │
│                                                         │
│  Data Layer (8 Tables)                                  │
│  ├── gold_financial_monthly, gold_quality_measures       │
│  ├── gold_utilization_monthly, fact_vbc_performance      │
│  ├── dim_member, dim_aco_contract                       │
│  ├── dim_provider_network, dim_budget                   │
│  └── Schema: hls_fde.healthcare_finance                 │
│                                                         │
│  Conversational Layer (1 Genie Space)                   │
│  └── Healthcare Finance Intelligence                    │
│      (01f1b2a18cde1845b9937112d70fe765)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## How to Reproduce This for Another Domain

1. **Author a glossary document** — Use the `L200-C_glossary_pages.md` format: structured terms with Definition, Business Context, Data Usage, and Related Terms sections.
2. **Open the domain page** — Navigate to the target knowledge domain in Discover.
3. **Ask Genie Code to bulk-create pages** — Provide the document path and target domain. The agent extracts terms, proposes pages with overlap detection, and creates them as drafts.
4. **Register assets** — Add tables, metric views, and Genie spaces to the domain using `addAssetToCurrentDomain`.
5. **Update the domain description** — Reflect the complete asset inventory.
6. **Publish pages** — Review each draft in the Discover UI and publish when ready.

## Files Modified

| File | Change |
| --- | --- |
| `fixtures/sessions/2026-09-17_uc-pages-and-domain-setup.md` | This file |
| `fixtures/sessions/INDEX.md` | Added this session entry |

## Decisions

1. **All 18 terms created as separate pages** — Even the 4 flagged overlaps were determined to be false positives or acceptably soft. The ontology benefits from granular, individually discoverable definitions.
2. **Genie space linked on every page** — Creates maximum discoverability. A user browsing any term can immediately jump to the conversational agent.
3. **IBNR page has no related tables** — Incurred But Not Reported is an actuarial concept referenced in the talk track only; no direct data column exists in the demo schema. The page still provides critical business context for Genie answers.
4. **Subdomain creation deferred** — Requires account-level governed tag creation. The flat 18-page structure works well in the interim; subdomains are a refinement, not a blocker.
5. **Schema references use production catalog** — All pages reference `hls_fde.healthcare_finance.*`, not the dev catalog. This matches the deployed bundle target.
