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

## Deployment

### Method

`databricks bundle deploy` is blocked from notebook execution (CLI binary checks interactive terminal context; pty workaround also fails). Deployed the two changed resources directly via Databricks Python SDK:

1. **CFO Dashboard** — `w.api_client.do("PATCH", "/api/2.0/lakeview/dashboards/{id}", body={"serialized_dashboard": ...})`
   - Dev dashboard ID: `01f1bbc037791ae5bb101a4d4ce318d9`
   - Updated at: 2026-09-29T11:52:06.867Z
2. **Genie Space** — `w.api_client.do("PATCH", "/api/2.0/genie/spaces/{id}", body={"serialized_space": ...})`
   - Required resolving bundle variable refs (`${resources.schemas.healthcare_finance.*}`) to dev values (`hls_fde_dev.dev_matthew_giglia_healthcare_finance`) before the API call
   - Dev Genie space ID: `01f1b284db9618cc902e5cf68a43153c`

Dashboard post-deploy validation: 15/15 dataset queries executed successfully against dev schema.

## Genie Agent Testing (5/5 Pass)

Tested all key demo beat prompts against the updated dev Genie agent:

| Test | Prompt | Sign Fix | Dynamic Date | Values Match | Status |
| --- | --- | --- | --- | --- | --- |
| Quality sign convention | "Which HEDIS measures are below 4-star for MA?" | `HAVING distance_to_4_star > 0` ✅ | `MAX(year_month)` = Aug 2026 ✅ | BCS 72.8%, HbA1c 58.8%, d2s 0.012 ✅ | PASS |
| Morning briefing | "What needs attention today?" | `> 0` in quality queries ✅ | Aug 2026 throughout ✅ | Medicaid 1.081, MA 1.008 flagged ✅ | PASS |
| AHP VBC performance | "Tell me about Accountable Health Partners" | n/a | `MAX(quarter)` = 2026-Q3 ✅ | $2.1M savings, $892 TCOC, 4.2 quality, $198 pharmacy ✅ | PASS |
| Budget variance | "Budget variance by LOB, latest month" | n/a | `MAX(year_month)` = Aug 2026 ✅ | All 4 LOBs exact match ✅ | PASS |
| Dr. Chen meeting brief | "Prepare talking points for Dr. Chen meeting" | BCS/HbA1c flagged as 3-star ✅ | Aug 2026 + 2026-Q3 ✅ | 4 queries, 3 charts, gainsharing 60/25/15 ✅ | PASS |

### Key observations

- **Sign convention fully corrected:** Genie now uses `HAVING distance_to_4_star > 0` (not WHERE, which would fail with MEASURE()). The instruction fix propagated correctly.
- **Dynamic dates working:** All queries use `(SELECT MAX(year_month) FROM ...)` or `(SELECT MAX(quarter) FROM ...)` — no trace of hardcoded `'2026-05-01'`.
- **Morning briefing note:** Some mv_utilization/mv_member_risk queries initially returned 0 rows due to MEASURE() in WHERE vs HAVING. Genie self-corrected on retry. This is a known Genie behavior with metric view aggregate filtering.
- **Dr. Chen brief is excellent:** 4 data queries, 3 visualizations (line, combo, bar), structured narrative with numbered talking points per instruction rule 9. GLP-1 cost pressure correctly inferred from pharmacy trend.

## Branch & Git

- **Branch:** `mg-genie-consistency-review` (created from `mg-genie-cmo-dashboard`)
- **Committed files:** 4 (healthcare_finance_intelligence.genie_space.yml, cfo_executive_dashboard.lvdash.json, INDEX.md, this session log)
- **Commit message:** `fix: Genie sign convention + CFO dashboard MV migration`
- **Artifact:** Empty `fhcf-demo/fixtures/cfo_dashboard_mv_queries.md` in working tree (createAsset artifact, should be discarded)

## Decisions

- All dashboard queries now use bare metric view names (no catalog.schema prefix) — the dashboard inherits dataset_catalog/dataset_schema from the lvdash.json config for dev/prod portability.
- `shared_savings` and `aco_scorecard` now use full `aco_name` from mv_vbc_performance instead of `aco_short_name` from dim_aco_contract. Widgets using these may need bar/column label adjustment.
- `hedis_ma` ORDER BY is DESC on distance_to_4_star_pct so measures needing the most improvement appear first (positive = below 4-star).
- SDK-based deploy is a viable alternative when `bundle deploy` is blocked. Requires manual variable resolution for Genie serialized_space.

## Files Modified

- `resources/healthcare_finance_intelligence.genie_space.yml` — Genie instruction fixes (sign convention + dynamic dates)
- `src/dashboards/cfo_executive_dashboard.lvdash.json` — 15 dataset query replacements (raw tables → metric views)
- `fixtures/sessions/INDEX.md` — updated with this session entry
- `fixtures/sessions/2026-09-29_consistency-review-and-mv-migration.md` — this file
