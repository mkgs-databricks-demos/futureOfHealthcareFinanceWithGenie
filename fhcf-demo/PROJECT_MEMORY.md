# PROJECT_MEMORY -- fhcf-demo

## Project Overview

**Name:** Future of Healthcare Finance with Genie (fhcf-demo)  
**Purpose:** Databricks HLS Quarterly Webinar demo (September 17, 2026) showing Genie Agent over healthcare finance data  
**Repo:** https://github.com/mkgs-databricks-demos/futureOfHealthcareFinanceWithGenie.git  
**Branch:** mg-genie-ddl-metrics-genie-space  
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
  src/
    seed_all_data.py          # 26-cell notebook (Python default, SQL cells via %sql)
  fixtures/
    sessions/
      INDEX.md
      2026-09-17_initial-bundle-setup.md
      2026-09-17_ddl-metric-view-improvements.md
      2026-09-17_genie-space-and-catalog-migration.md
      2026-09-17_genie-space-testing-and-instruction-tuning.md
```

## Variables

| Variable | Default | Usage |
| --- | --- | --- |
| catalog | hls_fde | UC catalog for all tables/views. Dev override: hls_fde_dev |
| schema | healthcare_finance | UC schema (dev mode prefixes with dev_<user>_) |
| warehouse_id | lookup: demo-warehouse | SQL warehouse for Genie space |

## Resources

### Schema

- **healthcare_finance** -- UC schema resource. Referenced by job params via ${resources.schemas.healthcare_finance.*}

### Job

- **seed_data** -- "[FHCF] Seed Healthcare Finance Data"
  - Single task: runs src/seed_all_data.py
  - Passes catalog and schema as base_parameters from schema resource refs
  - Dev job ID: 749445244992722

### Genie Space

- **healthcare_finance_intelligence** -- "Healthcare Finance Intelligence"
  - Inline serialized_space in YAML (no separate JSON file)
  - Table identifiers use ${resources.schemas.healthcare_finance.*} refs — resolve per-target at deploy time
  - warehouse_id: ${var.warehouse_id} (demo-warehouse)
  - 14 data sources (8 tables + 6 metric views), 7 sample questions, 1 consolidated instruction
  - Dev space ID: 01f1b284db9618cc902e5cf68a43153c
  - Deployment ordering: seed job must run BEFORE Genie space deploy (API validates table existence)

## Data Model

### Tables (8)

| Table | Rows | Description |
| --- | --- | --- |
| dim_aco_contract | 5 | ACO/CIN reference data. ACO-001 = AHP (Dr. Sarah Chen). |
| dim_budget | 48 | Monthly budget targets by LOB (4 LOBs x 12 months). |
| dim_member | 50,000 | Member demographics and risk profiles. |
| dim_provider_network | 200 | Provider-level network data by ACO. |
| gold_financial_monthly | 480 | Monthly financial aggregates by LOB/state/plan_type (4x10x1x12). |
| gold_quality_measures | 288 | HEDIS quality measures by LOB/month (6 measures x 4 LOBs x 12 months). |
| gold_utilization_monthly | 480 | Monthly utilization by LOB/state (4x10x12). |
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

- **Medicaid MLR ~106%**, MA ~100.3%, Commercial ~87%, Individual ~83%
- FL, TX, CA: 2x avoidable ED rate (14% vs 7% elsewhere)
- BCS at 72% (4-star cutpoint 74%), HbA1c at 58% (cutpoint 60%)
- AHP (ACO-001): Shared Savings $2.1M YTD vs $1.8M target; TCOC PMPM up +3% QoQ; Pharmacy PMPM +8% QoQ from GLP-1
- Validation queries in notebook cell 23

## Demo Beats (all tested 2026-09-17, 7/7 passing)

| Beat | Prompt | Status | Metric Views Used |
| --- | --- | --- | --- |
| 1a | Morning briefing — flag off-track items | PASS | mv_budget_variance, mv_quality, mv_utilization |
| 1b | HEDIS measures below 4-star cutpoints | PASS | mv_quality (distance_to_4_star, estimated_star_rating) |
| 2a | Top 10 highest-risk members | PASS | dim_member |
| 2b | High-risk members in high avoidable ED states | PASS | dim_member, mv_utilization |
| 3a | Calendar (MCP connector) | SKIP | External — not testable via API |
| 3b | AHP value-based care overview | PASS | mv_vbc_performance |
| 3c | TCOC drill-down — is it pharmacy? | PASS | mv_vbc_performance |
| 3d | Dr. Chen meeting brief | PASS | mv_vbc_performance, mv_quality |

## Genie Agent (DEPLOYED)

- **Name:** Healthcare Finance Intelligence
- **Dev Space ID:** 01f1b284db9618cc902e5cf68a43153c
- **Data Sources:** 14 (6 metric views + 8 tables)
- **Instructions:** Consolidated from L300-C: glossary, 12 behavioral rules, MEASURE() syntax examples for all 6 views, condition domains
- **Sample Questions:** 7 (aligned with demo beats)
- **Key rules:** Always query metric views for KPIs (6 views); mv_budget_variance for budget variance (not manual join); mv_vbc_performance includes ACO name via join; mv_quality has distance_to_4_star; mv_utilization for per-1K rates; mv_member_risk for risk tiers
- **API constraints:** content (array of strings) not instruction; max 1 text_instruction; all collections sorted alphabetically
- **Instruction tuning:** Rule 9 must be directive ("SYNTHESIZE a structured meeting brief") not passive ("note that...") — Genie agents decline narrative generation unless explicitly directed

## Conventions

- Notebook uses USE CATALOG/SCHEMA + bare table names (not fully qualified in every statement)
- Metric view source fields use ${catalog}.${schema}.table (widget substitution for stored metadata)
- Job params reference ${resources.schemas.healthcare_finance.*} (never raw ${var.schema})
- Notebook stored as .py (Python default language) with %sql magic for SQL cells
- Session summaries in fixtures/sessions/ with INDEX.md

## Key IDs (dev target)

| Resource | ID |
| --- | --- |
| Seed Job | 749445244992722 |
| Latest Seed Run | 686881950106253 |
| Genie Space | 01f1b284db9618cc902e5cf68a43153c |
| Genie Space YAML | 2824221228946159 |
| Notebook (seed_all_data) | 2824221228946135 |
| databricks.yml | 2824221228946048 |
| Schema YAML | 2824221228946136 |
| Job YAML | 2824221228946137 |
