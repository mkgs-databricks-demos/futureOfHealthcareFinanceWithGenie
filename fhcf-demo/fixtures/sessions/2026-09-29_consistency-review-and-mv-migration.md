# 2026-09-29 — Consistency Review & CFO Dashboard MV Migration

## Summary

Performed a full cross-surface consistency review of both dashboards and the dev Genie agent. Then migrated all 15 CFO Executive Dashboard datasets from raw gold_/dim_ table queries to governed metric views with MEASURE() syntax.

## Problems Found

### 1. `distance_to_4_star` sign convention (Critical)

- **Root cause:** `mv_quality` defines `distance_to_4_star = AVG(star_4_cutpoint) - AVG(current_rate)` — positive = below 4-star. The CFO dashboard computed `current_rate - star_4_cutpoint` — negative = below 4-star. The Genie instruction rule 6 said "Flag distance_to_4_star < 0" which was inverted for the MV convention.
- **Fix:** Patched Genie instruction rule 6 to say `> 0`. Patched rule 10 similarly. Updated MEASURE() example queries throughout. Aligned CFO `hedis_ma` dataset to MV convention with `ORDER BY distance_to_4_star_pct DESC` (worst-first).

### 2. Genie hardcoded May 2026 for quality (Moderate)

- **Root cause:** Instruction example queries used `year_month = '2026-05-01'` literally. Genie followed examples instead of using MAX(year_month). Data goes through August 2026.
- **Fix:** Updated all MEASURE() example queries to use dynamic `(SELECT MAX(year_month) FROM ...)` subqueries.

### 3. Format differences (Minor)

- Budget attainment: CFO showed percentage (100.7%), MV returns ratio (1.006606). Fixed by wrapping in `ROUND(... * 100, 1)`.
- Avoidable rates: same pattern. All MV queries now multiply by 100 and round for dashboard display.

## Changes Made

### healthcare_finance_intelligence.genie_space.yml

6 patches applied:
- Rule 6: `distance_to_4_star < 0` → `distance_to_4_star > 0`
- Rule 10: `distance_to_4_star < 0` → `distance_to_4_star > 0`
- 4 MEASURE() example queries: hardcoded `'2026-05-01'` → `(SELECT MAX(year_month) FROM mv_quality/mv_financial/mv_utilization/mv_budget_variance)`

### cfo_executive_dashboard.lvdash.json

All 15 datasets migrated from raw table queries to governed metric views:

| Dataset | Old Source | New Source | Key Change |
| --- | --- | --- | --- |
| avoidable_spend_state | gold_financial_monthly (manual calc) | mv_financial MEASURE(avoidable_share_of_spend) | Governed measure replaces SUM/SUM ratio |
| avoidable_ed_state | gold_utilization_monthly (manual calc) | mv_utilization MEASURE(avoidable_ed_rate) | Governed measure |
| mlr_by_lob | gold_financial_monthly (SUM/SUM) | mv_financial MEASURE(mlr) | Governed measure |
| mlr_trend | gold_financial_monthly | mv_financial MEASURE(mlr) | GROUP BY ALL |
| paid_pmpm_trend | gold_financial_monthly (SUM/SUM) | mv_financial MEASURE(paid_pmpm) | Governed measure |
| exec_counters | gold_financial_monthly | mv_financial (4 measures) | Single governed source |
| budget_variance | gold_financial_monthly JOIN dim_budget | mv_budget_variance (6 measures) | Eliminates manual join |
| ed_per_1k | gold_utilization_monthly (manual calc) | mv_utilization MEASURE(ed_per_1k) | Governed measure |
| hedis_ma | gold_quality_measures (manual calc) | mv_quality (5 measures + 2 dims) | Sign convention aligned |
| bcs_hba1c_trend | gold_quality_measures | mv_quality MEASURE(current_rate) | GROUP BY ALL |
| shared_savings | fact_vbc_performance JOIN dim_aco_contract (UNION) | mv_vbc_performance (actual/target) | aco_name replaces short_name |
| readmission_trend | gold_utilization_monthly (manual calc) | mv_utilization MEASURE(readmission_rate) | Governed measure |
| aco_scorecard | fact_vbc_performance JOIN dim_aco_contract (PIVOT) | mv_vbc_performance (5 typed measures) | Eliminates CASE pivot |
| ip_per_1k | gold_utilization_monthly (manual calc) | mv_utilization MEASURE(ip_per_1k) | Governed measure |
| ahp_trends | fact_vbc_performance (raw filter) | mv_vbc_performance MEASURE(actual_value) | GROUP BY ALL |

### Reference file created

- `/Users/matthew.giglia@databricks.com/cfo_dashboard_mv_queries.md` (workspace file ID 3410933705378442) — all 15 validated replacement queries.

## Validation

- 15/15 metric view queries execute successfully
- Key narrative values confirmed:
  - Medicaid MLR: 1.0811
  - BCS distance_to_4_star: +1.2% (positive = below 4-star, correctly aligned)
  - AHP shared savings: $2,100,000
  - FL/TX/CA avoidable ED: ~35%
- Dev and prod schemas have identical data (600/360/120 rows through August 2026)

## Decisions

- All dashboard queries now use bare metric view names (no catalog.schema prefix) — the dashboard inherits dataset_catalog/dataset_schema from the lvdash.json config for dev/prod portability.
- `shared_savings` and `aco_scorecard` now use full `aco_name` from mv_vbc_performance instead of `aco_short_name` from dim_aco_contract. Widgets using these may need bar/column label adjustment.
- `hedis_ma` ORDER BY is DESC on distance_to_4_star_pct so measures needing the most improvement appear first (positive = below 4-star).

## Files Modified

- `resources/healthcare_finance_intelligence.genie_space.yml` — Genie instruction fixes
- `src/dashboards/cfo_executive_dashboard.lvdash.json` — 15 dataset query replacements

## Next Steps

- Bundle deploy to dev and verify dashboard renders correctly
- Verify shared_savings bar chart label display with full ACO names
- Consider applying same MV migration to CMO dashboard (already uses MV as direct sources, but may need query refinement)
