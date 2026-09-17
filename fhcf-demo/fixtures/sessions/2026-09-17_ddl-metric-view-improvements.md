# Session: DDL & Metric View Improvements

**Date:** 2026-09-17  
**Notebook:** `src/seed_all_data` (ID `2824221228946135`)  
**Schema:** `hls_fde.dev_matthew_giglia_healthcare_finance`

---

## Problem

The seed notebook's 8 tables and 3 metric views had several quality gaps discovered during a data review:

1. **No PK/FK constraints** — tables lacked informational integrity metadata for query optimizers and documentation.
2. **No liquid clustering** — no clustering on any table despite clear filter patterns (lob, year_month, state).
3. **`gold_utilization_monthly` missing `member_months`** — per-1K utilization rates (IP admits/1K, ED visits/1K) were impossible without joining to `gold_financial_monthly`.
4. **`gold_financial_monthly` only seeds `plan_type = 'PPO'`** — the dimension exists in DDL but is single-valued. Noted as known limitation; not changed to preserve planted narrative values.
5. **`mv_vbc_performance` uses `SUM(actual_value)` for all measures** — semantically wrong for non-additive measures (Readmission Rate, Quality Score, TCOC PMPM). Summing rates across ACOs produces nonsense.
6. **No `format`, `display_name`, or `synonyms` on any metric view** — hurts dashboard rendering and Genie/AI discovery.
7. **`mv_quality` doesn't expose star cutpoints or derived star rating** — hard to assess STARS risk without cutpoint context.
8. **No utilization metric view** — per-1K rates are a core healthcare finance lens with no governed path.
9. **No budget variance metric view** — actual vs target MLR comparison (Beat 1 narrative) has no governed path.
10. **No member risk/population health metric view** — risk stratification and care gap analysis unavailable.

## Root Causes

- Initial seed was focused on narrative correctness and data generation, not schema best practices or metric view completeness.
- Metric views were minimal (dimensions + raw aggregates) without semantic metadata or cross-table joins.
- Utilization table designed for raw counts only, missing the denominator needed for rate calculations.

## Changes Made

### Table DDL (8 cells updated)

| Table | Changes |
| --- | --- |
| `dim_aco_contract` | Added `CONSTRAINT pk_dim_aco_contract PRIMARY KEY (aco_id)` |
| `dim_budget` | Added `CONSTRAINT pk_dim_budget PRIMARY KEY (lob, year_month)` |
| `dim_member` | Added PK on `member_id`, FK to `dim_aco_contract(aco_id)`, `CLUSTER BY (lob, state)` |
| `dim_provider_network` | Added PK on `provider_id`, FK to `dim_aco_contract(aco_id)` |
| `gold_financial_monthly` | Added `CLUSTER BY (lob, year_month)` |
| `gold_quality_measures` | Added `CLUSTER BY (lob, year_month)` |
| `gold_utilization_monthly` | Added `member_months BIGINT` column, `CLUSTER BY (lob, year_month)` |
| `fact_vbc_performance` | Added FK to `dim_aco_contract(aco_id)`, `CLUSTER BY (aco_id, quarter)` |

### Seed Data (1 cell updated)

| Cell | Change |
| --- | --- |
| Seed — gold_utilization_monthly | Added `member_months` using same hash-based formula as `gold_financial_monthly` to ensure consistency across both tables |

### Existing Metric Views (3 cells updated)

| Metric View | Changes |
| --- | --- |
| `mv_financial` | Added `display_name`, `synonyms`, `format` (currency/percentage/date) on all 4 dimensions and 8 measures |
| `mv_quality` | Added `estimated_star_rating` derived dimension (CASE on cutpoints), `star_4_cutpoint` and `distance_to_4_star` measures, full semantic metadata on all columns |
| `mv_vbc_performance` | Joined `dim_aco_contract` with `rely: at_most_one_match: true`; added `aco_name`, `contract_type`, `region` dimensions; replaced generic `SUM(actual_value)` with properly typed filtered measures: `shared_savings_ytd` (SUM), `tcoc_pmpm` (AVG), `quality_score` (AVG), `readmission_rate` (AVG), `ed_rate_per_1k` (AVG), `pharmacy_pmpm` (AVG); retained `actual_value`/`target_value`/`variance` for grouped-by-measure queries |

### New Metric Views (3 cells added)

| Metric View | Source | Key Measures |
| --- | --- | --- |
| `mv_utilization` | `gold_utilization_monthly` | `ip_per_1k`, `ed_per_1k`, `readmission_rate`, `avoidable_ed_rate`, `avoidable_ip_rate`, `op_visits`, `rx_fills` |
| `mv_budget_variance` | SQL join of `gold_financial_monthly` + `dim_budget` (pre-aggregated to LOB/month grain) | `actual_mlr`, `target_mlr`, `mlr_variance`, `premium_variance`, `paid_claims_variance`, `budget_attainment` |
| `mv_member_risk` | `dim_member` | `member_count`, `avg_risk_score`, `high_risk_count`, `high_risk_pct`, `avg_open_gaps`, `members_with_gaps`, `gap_rate`; derived `risk_tier` dimension |

### Other

- Updated markdown header cell to reflect 6 metric views (was 3).
- Set `schema` widget to `dev_matthew_giglia_healthcare_finance` for execution.

## Decisions

1. **Did NOT diversify `plan_type`** from all-PPO — changing it risks breaking the carefully planted narrative values (Medicaid MLR > 1.0, Commercial MLR < 0.90, AHP shared savings > $2M). Noted as known limitation.
2. **Used SQL source (not YAML join) for `mv_budget_variance`** — budget is at (lob, year_month) grain while financial is at (lob, state, plan_type, year_month). A YAML join would fan-out budget rows across 10 states, inflating SUM aggregates. Pre-aggregating in SQL avoids this.
3. **Used `rely: at_most_one_match: true` on VBC → ACO join** — `aco_id` is PK of `dim_aco_contract`, so the assertion is safe and enables aggregation pushdown.
4. **Used `AVG()` for non-additive VBC measures** — rates and scores should not be summed across ACOs. `FILTER (WHERE measure_name = '...')` isolates each measure; `AVG` is the correct aggregation for rates when grouped above the (aco_id, measure_name, quarter) grain.

## Execution Status

- **All code edits applied successfully** (8 DDL updates, 1 seed update, 3 metric view updates, 3 new cells, 1 header update).
- **Notebook NOT yet executed** — automated run was blocked by safety review (CREATE OR REPLACE TABLE is destructive). User needs to **Run All** manually to recreate tables with improved DDL, reseed data, and create metric views.

## Files Modified

| File | Type | Changes |
| --- | --- | --- |
| `src/seed_all_data` | Notebook | 12 cells updated, 3 cells added (26 total cells, was 23) |

## Known Limitations / Follow-ups

- `plan_type` is single-valued ('PPO') across `gold_financial_monthly` — diversify if narrative can be recalibrated.
- Metric views use `${catalog}.${schema}` variable references — must match widget values at execution time.
- `mv_budget_variance` drops the `state` dimension (budget has no state-level allocation). Consider state-proportional allocation if needed.
- No window measures (trailing 3-month MLR, cumulative YTD spend) — could be added as a follow-up enhancement.
