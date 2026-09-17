# PROJECT_MEMORY -- fhcf-demo

## Project Overview

**Name:** Future of Healthcare Finance with Genie (fhcf-demo)  
**Purpose:** Databricks HLS Quarterly Webinar demo (September 17, 2026) showing Genie Agent over healthcare finance data  
**Repo:** https://github.com/mkgs-databricks-demos/futureOfHealthcareFinanceWithGenie.git  
**Branch:** mg-init  
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
  src/
    seed_all_data.py          # 23-cell notebook (Python default, SQL cells via %sql)
  fixtures/
    sessions/
      INDEX.md
      2026-09-17_initial-bundle-setup.md
```

## Variables

| Variable | Default | Usage |
| --- | --- | --- |
| catalog | hls_fde | UC catalog for all tables/views |
| schema | healthcare_finance | UC schema (dev mode prefixes with dev_<user>_) |

## Resources

### Schema

- **healthcare_finance** -- UC schema resource. Referenced by job params via ${resources.schemas.healthcare_finance.*}

### Job

- **seed_data** -- "[FHCF] Seed Healthcare Finance Data"
  - Single task: runs src/seed_all_data.py
  - Passes catalog and schema as base_parameters from schema resource refs
  - Dev job ID: 749445244992722

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

### Metric Views (3)

| View | Source Table | Key Measures |
| --- | --- | --- |
| mv_financial | gold_financial_monthly | mlr, paid_pmpm, premium_pmpm, avoidable_spend_ratio |
| mv_quality | gold_quality_measures | current_rate, gap_count, eligible_count, gap_closure_rate |
| mv_vbc_performance | fact_vbc_performance | actual_value, target_value, variance, trend_vs_prior_quarter |

Metric view YAML uses version: 1.1. Source fields use ${catalog}.${schema}.table_name for full qualification.

## Planted Narrative (must hold after seeding)

- **Medicaid MLR ~106%**, MA ~100.3%, Commercial ~87%, Individual ~83%
- FL, TX, CA: 2x avoidable ED rate (14% vs 7% elsewhere)
- BCS at 72% (4-star cutpoint 74%), HbA1c at 58% (cutpoint 60%)
- AHP (ACO-001): Shared Savings $2.1M YTD vs $1.8M target; TCOC PMPM up +3% QoQ; Pharmacy PMPM +8% QoQ from GLP-1
- Validation queries in notebook cell 23

## Demo Beats

1. **CFO morning briefing** -- MLR by LOB, avoidable spend
2. **Persona rotation** -- Actuary, quality officer, care manager perspectives
3. **AHP meeting prep** -- Dr. Sarah Chen (ACO-001), shared savings, TCOC, pharmacy
4. **Reveal** -- Platform capabilities

## Genie Agent (TODO)

- **Name:** Healthcare Finance Intelligence
- **Mode:** Agent Mode
- **Tables:** All 11 (3 metric views + 8 tables) in hls_fde.healthcare_finance
- **Instructions:** Full text from L300-C design doc (glossary + behavioral rules + MEASURE() syntax)
- **Key rules:** Always query metric views for KPIs; normalize per PMPM; morning briefing = MLR + avoidable spend; AHP/Dr. Sarah Chen = fact_vbc_performance WHERE aco_id = 'ACO-001'

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
| Failed Run (metric view error) | 669021950781837 |
| Notebook (seed_all_data) | 2824221228946135 |
| databricks.yml | 2824221228946048 |
| Schema YAML | 2824221228946136 |
| Job YAML | 2824221228946137 |
