# PROJECT_MEMORY -- fhcf-demo

## Project Overview

**Name:** Future of Healthcare Finance with Genie (fhcf-demo)  
**Purpose:** Databricks HLS Quarterly Webinar demo (September 17, 2026) showing Genie Agent over healthcare finance data  
**Repo:** https://github.com/mkgs-databricks-demos/futureOfHealthcareFinanceWithGenie.git  
**Branch:** mg-genie-consistency-review  
**Bundle root:** /Users/matthew.giglia@databricks.com/futureOfHealthcareFinanceWithGenie/fhcf-demo/  
**Design docs:** webinar_demo_docs/docs/design/ (L100-L300 at repo root)

---

## Targets

| Target | Mode | Workspace | Catalog | Schema (effective) |
| --- | --- | --- | --- | --- |
| dev (default) | development | fevm-hls-fde | hls_fde_dev | dev_matthew_giglia_healthcare_finance |
| prod | production | fevm-hls-fde | hls_fde | healthcare_finance |

## Bundle Structure

```
fhcf-demo/
  databricks.yml
  PROJECT_MEMORY.md
  README.md
  resources/
    healthcare_finance.schema.yml
    seed_data.job.yml
    healthcare_finance_intelligence.genie_space.yml
    cfo_executive_dashboard.dashboard.yml
    health_plan_cmo_performance.dashboard.yml
    demo_warehouse.sql_warehouse.yml
  src/
    seed_all_data.py          # 26-cell notebook (Python default, SQL cells via %sql)
    dashboards/
      cfo_executive_dashboard.lvdash.json
      health_plan_cmo_performance.lvdash.json
  fixtures/
    sessions/
      INDEX.md
      2026-09-17_initial-bundle-setup.md
      2026-09-17_ddl-metric-view-improvements.md
      2026-09-17_genie-space-and-catalog-migration.md
      2026-09-17_metric-view-metadata-and-instruction-trim.md
      2026-09-17_genie-space-testing-and-instruction-tuning.md
      2026-09-28_prod-data-restoration.md
      2026-09-28_cfo-executive-dashboard.md
      2026-09-29_cmo-dashboard-and-warehouse-resource.md
      2026-09-29_consistency-review-and-mv-migration.md
```

## Variables

| Variable | Default | Usage |
| --- | --- | --- |
| catalog | hls_fde | UC catalog for all tables/views. Dev override: hls_fde_dev |
| schema | healthcare_finance | UC schema (dev mode prefixes with dev_<user>_) |

> **Note:** `warehouse_id` was removed as a variable in session 2026-09-29. The warehouse is now a managed resource (`demo_warehouse`). All resource YAMLs reference `${resources.sql_warehouses.demo_warehouse.id}`.

## Resources

### Schema

- **healthcare_finance** -- UC schema resource. Referenced by job params via ${resources.schemas.healthcare_finance.*}

### Job

- **seed_data** -- "[FHCF] Seed Healthcare Finance Data"
  - Single task: runs src/seed_all_data.py
  - Passes catalog and schema as base_parameters from schema resource refs
  - Dev job ID: 749445244992722
  - Prod job ID: 824849230298800

### Genie Space

- **healthcare_finance_intelligence** -- "Healthcare Finance Intelligence"
  - Inline serialized_space in YAML (no separate JSON file)
  - Table identifiers use ${resources.schemas.healthcare_finance.*} refs — resolve per-target at deploy time
  - warehouse_id: ${resources.sql_warehouses.demo_warehouse.id}
  - 14 data sources (8 tables + 6 metric views), 7 sample questions, 1 consolidated instruction
  - Dev space ID: 01f1b284db9618cc902e5cf68a43153c
  - Deployment ordering: seed job must run BEFORE Genie space deploy (API validates table existence)

### SQL Warehouse

- **demo_warehouse** -- "[FHCF] Healthcare Finance Warehouse"
  - 2X-Small serverless PRO, auto-stop 10 min, 1 cluster
  - Referenced by dashboards and Genie space via ${resources.sql_warehouses.demo_warehouse.id}
  - Dev warehouse ID: 1be43d05d0d903f4

### Dashboards

- **cfo_executive_dashboard** -- "CFO Executive Dashboard — Healthcare Finance"
  - Serialized .lvdash.json in src/dashboards/ (49K chars)
  - 5 pages: Executive Summary, Financial Performance, Quality & Star Ratings, Utilization, VBC & ACO Performance
  - 15 SQL datasets, 24 widgets (4 counters, 6 bar charts, 5 line charts, 3 tables, 5 text headers, 1 grouped bar)
  - **All 15 datasets migrated to governed metric views with MEASURE() syntax** (session 2026-09-29). No raw gold_/dim_ queries remain.
  - hedis_ma sign convention aligned: distance_to_4_star positive = below 4-star (matches MV convention)
  - Queries use bare MV names — dataset_catalog/dataset_schema resolve per-target
  - warehouse_id: ${resources.sql_warehouses.demo_warehouse.id}, embed_credentials: false
  - Surfaces planted narrative: Medicaid MLR ~108%, BCS/HbA1c below 4-star, FL/TX/CA avoidable hotspots, AHP shared savings
  - Interactive copy: dashboard ID 01f1bb448f8015d28f7b267049954018
  - Branch: mg-genie-consistency-review (originally mg-genie-cfo-dashboard)

- **health_plan_cmo_performance** -- "Health Plan CMO Performance Dashboard"
  - Serialized .lvdash.json in src/dashboards/ (271K chars)
  - 12 pages: Executive Summary, Member Risk & Care Gaps, Quality & Stars, Financial Performance, Utilization, VBC Contract Performance, Member Attribution & Care Mgmt, Provider Network, Risk-Adjusted Financials, Medicaid VBC Business Case, Commercial VBC Business Case, Global Filters
  - 9 datasets sourced from metric views and tables (all via MEASURE())
  - All KPI widgets delegate to metric view MEASURE() — verified identical to Genie Agent output across all 6 domains
  - dataset_catalog/dataset_schema/warehouse_id: ${resources.*} refs
  - Interactive copy: dashboard ID 01f1bb4cabc019b3a02c18e9b8e2daf7
  - Dev dashboard ID: 01f1bbc0377d184aaab81612a310442a
  - Branch: mg-genie-cmo-dashboard

## Data Model

### Tables (8)

| Table | Rows | Description |
| --- | --- | --- |
| dim_aco_contract | 5 | ACO/CIN reference data. ACO-001 = AHP (Dr. Sarah Chen). |
| dim_budget | 60 | Monthly budget targets by LOB (4 LOBs x 15 months, Jun 2025–Aug 2026). |
| dim_member | 50,000 | Member demographics and risk profiles. |
| dim_provider_network | 200 | Provider-level network data by ACO. |
| gold_financial_monthly | 600 | Monthly financial aggregates by LOB/state/plan_type (4x10x1x15). |
| gold_quality_measures | 360 | HEDIS quality measures by LOB/month (6 measures x 4 LOBs x 15 months). |
| gold_utilization_monthly | 600 | Monthly utilization by LOB/state (4x10x15). |
| fact_vbc_performance | 120 | Quarterly VBC performance by ACO/measure (5x6x4). |

### Metric Views (6)

| View | Source | Key Measures |
| --- | --- | --- |
| mv_financial | gold_financial_monthly | mlr, paid_pmpm, premium_pmpm, avoidable_share_of_spend. Semantic metadata: display_name, synonyms, format on all columns. |
| mv_quality | gold_quality_measures | current_rate, gap_count, gap_closure_rate, star_4_cutpoint, distance_to_4_star. Derived: estimated_star_rating. |
| mv_vbc_performance | fact_vbc_performance JOIN dim_aco_contract | Typed measures: shared_savings_ytd (SUM), tcoc_pmpm (AVG), quality_score (AVG), readmission_rate (AVG), ed_rate_per_1k (AVG), pharmacy_pmpm (AVG). Dimensions: aco_name, contract_type, region. |
| mv_utilization | gold_utilization_monthly | ip_per_1k, ed_per_1k, readmission_rate, avoidable_ed_rate, avoidable_ip_rate, op_visits, rx_fills |
| mv_budget_variance | gold_financial_monthly JOIN dim_budget | actual_mlr, target_mlr, mlr_variance, premium_variance, paid_claims_variance, budget_attainment |
| mv_member_risk | dim_member | member_count, avg_risk_score, high_risk_count, high_risk_pct, avg_open_gaps, gap_rate. Derived: risk_tier. |

Metric view YAML uses version: 1.1. Source fields use ${catalog}.${schema}.table_name for full qualification.

## Planted Narrative (must hold after seeding)

- **Medicaid MLR ~108%**, MA ~100.8%, Commercial ~86.5%, Individual ~82%
- FL, TX, CA: 2x avoidable ED rate (35% vs 17% elsewhere)
- BCS at 72.8% (4-star cutpoint 74%), HbA1c at 58.8% (cutpoint 60%)
- AHP (ACO-001): Shared Savings $2.1M YTD vs $1.8M target; TCOC PMPM up +3% QoQ; Pharmacy PMPM +8% QoQ from GLP-1
- Validation queries in notebook cell 23

## Demo Beats (retested 2026-09-29, 5/5 key beats passing on dev after instruction fix)

| Beat | Prompt | Status | Metric Views Used | Notes |
| --- | --- | --- | --- | --- |
| 1a | Morning briefing — flag off-track items | PASS | mv_budget_variance, mv_quality, mv_utilization | Uses `> 0` for quality, `MAX(year_month)` throughout |
| 1b | HEDIS measures below 4-star cutpoints | PASS | mv_quality | `HAVING distance_to_4_star > 0`, Aug 2026 data |
| 2a | Top 10 highest-risk members | PASS (2026-09-17) | dim_member | Not retested 2026-09-29 (unaffected by changes) |
| 2b | High-risk members in high avoidable ED states | PASS (2026-09-17) | dim_member, mv_utilization | Not retested 2026-09-29 |
| 3a | Calendar (MCP connector) | SKIP | External | Not testable via API |
| 3b | AHP value-based care overview | PASS | mv_vbc_performance | $2.1M savings, $892 TCOC, 4.2 quality, $198 pharmacy |
| 3c | TCOC drill-down — is it pharmacy? | PASS (2026-09-17) | mv_vbc_performance | Not retested 2026-09-29 (AHP test covers same data) |
| 3d | Dr. Chen meeting brief | PASS | mv_vbc_performance, mv_quality | 4 queries, 3 charts, structured narrative, GLP-1 insight |
| - | Budget variance by LOB | PASS | mv_budget_variance | New test: `MAX(year_month)` = Aug 2026, all 4 LOBs exact match |

## Genie Agent (DEPLOYED)

- **Name:** Healthcare Finance Intelligence
- **Dev Space ID:** 01f1b284db9618cc902e5cf68a43153c
- **Data Sources:** 14 (6 metric views + 8 tables)
- **Instructions:** Consolidated from L300-C: domain context (gainsharing only), 12 behavioral rules, MEASURE() syntax examples for all 6 views. Glossary and condition-domain content migrated to metric view metadata.
- **Sample Questions:** 7 (aligned with demo beats)
- **Instruction fixes (session 2026-09-29):**
  - Rule 6 & 10: `distance_to_4_star < 0` → `> 0 (positive = below cutpoint, needs improvement)` — aligns with MV convention
  - All MEASURE() example queries: hardcoded `'2026-05-01'` → `(SELECT MAX(year_month) FROM ...)` — ensures latest data always used
  - Tested 5/5 demo beats passing after fix
- **Key rules:** Always query metric views for KPIs (6 views); mv_budget_variance for budget variance (not manual join); mv_vbc_performance includes ACO name via join (AHP synonyms on aco_name); mv_quality has distance_to_4_star + condition-domain mappings in comment; mv_utilization for per-1K rates (authoritative-source in COMMENT ON VIEW); mv_member_risk for risk tiers
- **API constraints:** content (array of strings) not instruction; max 1 text_instruction; all collections sorted alphabetically
- **Instruction tuning:** Rule 9 must be directive ("SYNTHESIZE a structured meeting brief") not passive ("note that...") — Genie agents decline narrative generation unless explicitly directed

## Conventions

- Notebook uses USE CATALOG/SCHEMA + bare table names (not fully qualified in every statement)
- Metric view source fields use ${catalog}.${schema}.table (widget substitution for stored metadata)
- All resource refs use ${resources.*} syntax (schemas, sql_warehouses) — never raw ${var.*} except in schema resource itself
- warehouse_id variable removed — warehouse lifecycle is bundle-managed
- Notebook stored as .py (Python default language) with %sql magic for SQL cells
- Session summaries in fixtures/sessions/ with INDEX.md

## Key IDs

### Dev target

| Resource | ID |
| --- | --- |
| Seed Job | 749445244992722 |
| Latest Seed Run | 849614388632475 |
| Latest Seed Run | 849614388632475 |
| Genie Space | 01f1b284db9618cc902e5cf68a43153c |
| Genie Space YAML | 2824221228946159 |
| SQL Warehouse | 1be43d05d0d903f4 |
| CMO Dashboard | 01f1bbc0377d184aaab81612a310442a |
| CFO Dashboard | 01f1bbc037791ae5bb101a4d4ce318d9 |
| Seed Run (2026-09-29) | 947527817242476 |
| Notebook (seed_all_data) | 2824221228946135 |
| databricks.yml | 2824221228946048 |
| Schema YAML | 2824221228946136 |
| Job YAML | 2824221228946137 |

### Prod target

| Resource | ID |
| --- | --- |
| Genie Space | 01f1b2a18cde1845b9937112d70fe765 |
| Seed Job | 824849230298800 |
| Latest Seed Run | 849614388632475 |
| Demo beats | 7/7 passing (validated 2026-09-17, data re-seeded 2026-09-28) |
