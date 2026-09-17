# L300-B — Metric View YAML Definitions

## Overview
Full `CREATE VIEW WITH METRICS` SQL for all 3 metric views. These are the governed KPI layer that the Genie Agent queries.

## Important: Metric View Constraints
- **No JOINs** inside metric view definitions (Spark limitation: `METRIC_VIEW_JOIN_NOT_SUPPORTED`)
- Use `MEASURE()` function to query measures
- Use `GROUP BY ALL` for aggregation
- Dimensions are the columns Genie can filter/group by
- Measures are the calculated KPIs

---

## mv_financial

```sql
CREATE OR REPLACE VIEW `home_matthew_giglia`.`webinar_demo`.`mv_financial`
WITH METRICS
LANGUAGE YAML
AS $$
source: home_matthew_giglia.webinar_demo.gold_financial_monthly

dimensions:
  - name: lob
    expr: lob
    description: "Line of business: Commercial, MA (Medicare Advantage), Medicaid, Individual"
  - name: state
    expr: state
    description: "US state abbreviation"
  - name: plan_type
    expr: plan_type
    description: "Plan type: PPO, HMO, EPO, POS"
  - name: year_month
    expr: year_month
    description: "First day of the month. Use for time series trending."

measures:
  - name: paid_amount
    expr: "SUM(paid_amount)"
    description: "Total paid medical claims"
  - name: premium_amount
    expr: "SUM(premium_amount)"
    description: "Total earned premium revenue"
  - name: member_months
    expr: "SUM(member_months)"
    description: "Total member-months"
  - name: mlr
    expr: "SUM(paid_amount) / NULLIF(SUM(premium_amount), 0)"
    description: "Medical Loss Ratio = paid claims / earned premium. Values above 1.0 mean claims exceed premium. Lower is better for the payer."
  - name: paid_pmpm
    expr: "SUM(paid_amount) / NULLIF(SUM(member_months), 0)"
    description: "Paid claims Per Member Per Month. Use for cross-LOB cost comparison."
  - name: premium_pmpm
    expr: "SUM(premium_amount) / NULLIF(SUM(member_months), 0)"
    description: "Premium revenue Per Member Per Month."
  - name: avoidable_paid_amount
    expr: "SUM(avoidable_paid_amount)"
    description: "Total paid claims attributable to avoidable utilization"
  - name: avoidable_share_of_spend
    expr: "SUM(avoidable_paid_amount) / NULLIF(SUM(paid_amount), 0)"
    description: "Avoidable spend as a share of total paid claims. Higher = more waste."
$$;

COMMENT ON VIEW `home_matthew_giglia`.`webinar_demo`.`mv_financial`
IS 'Governed financial metric view for health plan performance. Query with MEASURE() and GROUP BY ALL. Dimensions: lob, state, plan_type, year_month. Key measures: mlr, paid_pmpm, premium_pmpm, avoidable_share_of_spend.';
```

---

## mv_quality

```sql
CREATE OR REPLACE VIEW `home_matthew_giglia`.`webinar_demo`.`mv_quality`
WITH METRICS
LANGUAGE YAML
AS $$
source: home_matthew_giglia.webinar_demo.gold_quality_measures

dimensions:
  - name: measure_id
    expr: measure_id
    description: "HEDIS measure identifier (e.g., BCS, CDC-HBA1C, CBP)"
  - name: measure_name
    expr: measure_name
    description: "Human-readable measure name"
  - name: lob
    expr: lob
    description: "Line of business"
  - name: year_month
    expr: year_month
    description: "Measurement month"
  - name: condition_domain
    expr: condition_domain
    description: "Clinical domain: Diabetes, Cardiovascular, Cancer Screening, Behavioral Health, Pediatric/Preventive"

measures:
  - name: current_rate
    expr: "AVG(current_rate)"
    description: "Current performance rate (0.0 to 1.0). Compare to star cutpoints to assess STARS risk."
  - name: eligible_count
    expr: "SUM(eligible_count)"
    description: "Total members eligible for this measure"
  - name: gap_count
    expr: "SUM(gap_count)"
    description: "Total members with an open care gap"
  - name: gap_closure_rate
    expr: "1.0 - (SUM(gap_count) / NULLIF(SUM(eligible_count), 0))"
    description: "Percentage of eligible members who have completed the required service. Higher is better."
$$;

COMMENT ON VIEW `home_matthew_giglia`.`webinar_demo`.`mv_quality`
IS 'Governed quality metric view for HEDIS measure performance. Query with MEASURE() and GROUP BY ALL. Compare current_rate to star cutpoints in gold_quality_measures for STARS risk assessment.';
```

---

## mv_vbc_performance

```sql
CREATE OR REPLACE VIEW `home_matthew_giglia`.`webinar_demo`.`mv_vbc_performance`
WITH METRICS
LANGUAGE YAML
AS $$
source: home_matthew_giglia.webinar_demo.fact_vbc_performance

dimensions:
  - name: aco_id
    expr: aco_id
    description: "ACO identifier. Join to dim_aco_contract for ACO name and details."
  - name: measure_name
    expr: measure_name
    description: "VBC performance measure: Shared Savings YTD, TCOC PMPM, Quality Score, Readmission Rate, ED Rate per 1K, Pharmacy PMPM"
  - name: quarter
    expr: quarter
    description: "Calendar quarter (e.g., 2026-Q1)"

measures:
  - name: actual_value
    expr: "SUM(actual_value)"
    description: "Actual performance value"
  - name: target_value
    expr: "SUM(target_value)"
    description: "Contractual target or benchmark"
  - name: variance
    expr: "SUM(actual_value) - SUM(target_value)"
    description: "Variance from target. Positive = above target (good for savings/quality, bad for cost)."
  - name: trend_vs_prior_quarter
    expr: "AVG(trend_vs_prior_quarter)"
    description: "Average percentage change vs prior quarter"
$$;

COMMENT ON VIEW `home_matthew_giglia`.`webinar_demo`.`mv_vbc_performance`
IS 'Governed VBC performance metric view. Query with MEASURE() and GROUP BY ALL. Join dim_aco_contract for ACO name, executive medical director, and contract details.';
```

---

## Validation

After creating all 3 metric views, run these tests:

```sql
-- Test mv_financial: MLR by LOB for latest month
SELECT lob, MEASURE(mlr), MEASURE(paid_pmpm), MEASURE(premium_pmpm)
FROM `home_matthew_giglia`.`webinar_demo`.`mv_financial`
WHERE year_month = '2026-05-01'
GROUP BY ALL;

-- Test mv_quality: Measures below 4-star
SELECT measure_name, MEASURE(current_rate) AS rate, star_4_cutpoint
FROM `home_matthew_giglia`.`webinar_demo`.`mv_quality` q
WHERE lob = 'MA' AND year_month = '2026-05-01'
GROUP BY ALL;

-- Test mv_vbc_performance: AHP Q3
SELECT measure_name, MEASURE(actual_value), MEASURE(target_value), MEASURE(variance)
FROM `home_matthew_giglia`.`webinar_demo`.`mv_vbc_performance`
WHERE aco_id = 'ACO-001' AND quarter = '2026-Q3'
GROUP BY ALL;
```
