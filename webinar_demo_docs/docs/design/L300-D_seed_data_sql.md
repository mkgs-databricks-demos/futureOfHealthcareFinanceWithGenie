# L300-D — Complete Seed Data SQL (Remaining 6 Tables)

## Overview
Complete INSERT statements for the 6 tables whose seed data was documented as strategies in L300-A. These are deterministic SQL statements using `EXPLODE`, `SEQUENCE`, and `CASE` logic — no randomness, fully reproducible. Run in order after the DDL from L300-A.

**Tables covered:**
1. `gold_financial_monthly` (~480 rows)
2. `dim_member` (~50,000 rows)
3. `gold_quality_measures` (~288 rows)
4. `gold_utilization_monthly` (~480 rows)
5. `fact_vbc_performance` (~120 rows)
6. `dim_provider_network` (~200 rows)

**Tables already seeded in L300-A:**
- `dim_aco_contract` (5 rows — complete INSERT in L300-A)
- `dim_budget` (48 rows — complete INSERT in L300-A)

---

## 1. gold_financial_monthly

This is the core Beat 1 table. The numbers are hand-tuned to produce the planted narrative:
- Medicaid MLR ~106%, MA ~100.3%, Commercial ~87%, Individual ~83%
- FL, TX, CA have 2× avoidable spend ratio
- Monthly variation with slight upward trend in Medicaid

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly`
WITH months AS (
  SELECT EXPLODE(SEQUENCE(DATE'2025-06-01', DATE'2026-05-01', INTERVAL 1 MONTH)) AS year_month
),
states AS (
  SELECT EXPLODE(ARRAY('NY','FL','TX','CA','PA','OH','IL','GA','NC','MI')) AS state
),
lobs AS (
  SELECT EXPLODE(ARRAY('Commercial','MA','Medicaid','Individual')) AS lob
),
base AS (
  SELECT l.lob, s.state, m.year_month,
    -- Month index for trending (0-11)
    MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') AS month_idx
  FROM lobs l CROSS JOIN states s CROSS JOIN months m
)
SELECT
  lob,
  state,
  'PPO' AS plan_type,
  year_month,

  -- paid_amount: base PMPM × member_months, with LOB-specific rates
  ROUND(
    CASE lob
      WHEN 'Commercial' THEN (520 + month_idx * 1.5 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 20)
      WHEN 'Individual' THEN (560 + month_idx * 1.2 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 18)
      WHEN 'MA'         THEN (1080 + month_idx * 2.0 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 30)
      WHEN 'Medicaid'   THEN (910 + month_idx * 2.5 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 25)
    END
    * -- member_months per state/LOB
    CASE lob
      WHEN 'Commercial' THEN (1800 + ABS(HASH(CONCAT(state, 'cm'))) % 400)
      WHEN 'Individual' THEN (400 + ABS(HASH(CONCAT(state, 'ind'))) % 150)
      WHEN 'MA'         THEN (1100 + ABS(HASH(CONCAT(state, 'ma'))) % 300)
      WHEN 'Medicaid'   THEN (1100 + ABS(HASH(CONCAT(state, 'med'))) % 300)
    END
  , 2) AS paid_amount,

  -- premium_amount: set so MLR hits target
  ROUND(
    CASE lob
      WHEN 'Commercial' THEN (600 + month_idx * 1.8 + HASH(CONCAT(state, lob, 'p', CAST(year_month AS STRING))) % 15)
      WHEN 'Individual' THEN (680 + month_idx * 1.5 + HASH(CONCAT(state, lob, 'p', CAST(year_month AS STRING))) % 12)
      WHEN 'MA'         THEN (1078 + month_idx * 1.5 + HASH(CONCAT(state, lob, 'p', CAST(year_month AS STRING))) % 20)
      WHEN 'Medicaid'   THEN (862 + month_idx * 1.0 + HASH(CONCAT(state, lob, 'p', CAST(year_month AS STRING))) % 15)
    END
    * CASE lob
      WHEN 'Commercial' THEN (1800 + ABS(HASH(CONCAT(state, 'cm'))) % 400)
      WHEN 'Individual' THEN (400 + ABS(HASH(CONCAT(state, 'ind'))) % 150)
      WHEN 'MA'         THEN (1100 + ABS(HASH(CONCAT(state, 'ma'))) % 300)
      WHEN 'Medicaid'   THEN (1100 + ABS(HASH(CONCAT(state, 'med'))) % 300)
    END
  , 2) AS premium_amount,

  -- member_months
  CAST(CASE lob
    WHEN 'Commercial' THEN (1800 + ABS(HASH(CONCAT(state, 'cm'))) % 400)
    WHEN 'Individual' THEN (400 + ABS(HASH(CONCAT(state, 'ind'))) % 150)
    WHEN 'MA'         THEN (1100 + ABS(HASH(CONCAT(state, 'ma'))) % 300)
    WHEN 'Medicaid'   THEN (1100 + ABS(HASH(CONCAT(state, 'med'))) % 300)
  END AS BIGINT) AS member_months,

  -- avoidable_paid_amount: FL, TX, CA get 2× rate
  ROUND(
    CASE lob
      WHEN 'Commercial' THEN (520 + month_idx * 1.5 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 20)
      WHEN 'Individual' THEN (560 + month_idx * 1.2 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 18)
      WHEN 'MA'         THEN (1080 + month_idx * 2.0 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 30)
      WHEN 'Medicaid'   THEN (910 + month_idx * 2.5 + HASH(CONCAT(state, lob, CAST(year_month AS STRING))) % 25)
    END
    * CASE lob
      WHEN 'Commercial' THEN (1800 + ABS(HASH(CONCAT(state, 'cm'))) % 400)
      WHEN 'Individual' THEN (400 + ABS(HASH(CONCAT(state, 'ind'))) % 150)
      WHEN 'MA'         THEN (1100 + ABS(HASH(CONCAT(state, 'ma'))) % 300)
      WHEN 'Medicaid'   THEN (1100 + ABS(HASH(CONCAT(state, 'med'))) % 300)
    END
    * CASE WHEN state IN ('FL','TX','CA') THEN 0.14 ELSE 0.07 END
  , 2) AS avoidable_paid_amount,

  -- risk_score_avg
  ROUND(CASE lob
    WHEN 'Commercial' THEN 1.00 + month_idx * 0.002
    WHEN 'Individual' THEN 1.05 + month_idx * 0.003
    WHEN 'MA'         THEN 1.15 + month_idx * 0.005
    WHEN 'Medicaid'   THEN 1.08 + month_idx * 0.003
  END, 4) AS risk_score_avg

FROM base;
```

**Validation after insert:**
```sql
-- Should show Medicaid MLR > 1.0, Commercial < 0.90
SELECT lob,
  ROUND(SUM(paid_amount) / SUM(premium_amount), 4) AS mlr,
  ROUND(SUM(paid_amount) / SUM(member_months), 2) AS paid_pmpm,
  ROUND(SUM(premium_amount) / SUM(member_months), 2) AS premium_pmpm,
  SUM(member_months) AS total_mm
FROM `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly`
WHERE year_month = '2026-05-01'
GROUP BY lob ORDER BY lob;
```

---

## 2. dim_member

50,000 synthetic members with deterministic distribution.

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`dim_member`
WITH member_ids AS (
  SELECT EXPLODE(SEQUENCE(1, 50000)) AS id
),
base AS (
  SELECT
    id,
    CONCAT('MBR-', LPAD(CAST(id AS STRING), 6, '0')) AS member_id,
    -- LOB distribution: Commercial 40%, MA 25%, Medicaid 25%, Individual 10%
    CASE
      WHEN id <= 20000 THEN 'Commercial'
      WHEN id <= 32500 THEN 'MA'
      WHEN id <= 45000 THEN 'Medicaid'
      ELSE 'Individual'
    END AS lob,
    -- State distribution
    ARRAY('NY','FL','TX','CA','PA','OH','IL','GA','NC','MI')[ABS(HASH(CONCAT('state', id))) % 10] AS state,
    -- Age band
    CASE ABS(HASH(CONCAT('age', id))) % 10
      WHEN 0 THEN '0-17'  WHEN 1 THEN '0-17'
      WHEN 2 THEN '18-34' WHEN 3 THEN '18-34'
      WHEN 4 THEN '35-49' WHEN 5 THEN '35-49'
      WHEN 6 THEN '50-64' WHEN 7 THEN '50-64'
      WHEN 8 THEN '65+'   ELSE '65+'
    END AS age_band,
    CASE ABS(HASH(CONCAT('gender', id))) % 2 WHEN 0 THEN 'M' ELSE 'F' END AS gender,
    'PPO' AS plan_type
  FROM member_ids
)
SELECT
  member_id,
  lob,
  state,
  age_band,
  gender,
  plan_type,

  -- risk_score: normal-ish distribution, higher for MA/Medicaid
  ROUND(GREATEST(0.2,
    CASE lob
      WHEN 'Commercial' THEN 1.0
      WHEN 'MA'         THEN 1.2
      WHEN 'Medicaid'   THEN 1.1
      WHEN 'Individual' THEN 1.05
    END
    + (ABS(HASH(CONCAT('risk', member_id))) % 100 - 50) * 0.02
    + CASE WHEN age_band = '65+' THEN 0.3 WHEN age_band = '50-64' THEN 0.15 ELSE 0 END
    -- Plant high-risk members: first 100 get very high scores
    + CASE WHEN id <= 100 THEN 2.0 + (ABS(HASH(CONCAT('highrisk', member_id))) % 100) * 0.02 ELSE 0 END
  ), 4) AS risk_score,

  -- cost_percentile
  CASE
    WHEN id <= 100 THEN 95 + ABS(HASH(CONCAT('pct', member_id))) % 5  -- top 100 are 95-99th percentile
    ELSE 1 + ABS(HASH(CONCAT('pct', member_id))) % 99
  END AS cost_percentile,

  -- open_gaps_count: high-risk members get 8+
  CASE
    WHEN id <= 100 THEN 8 + ABS(HASH(CONCAT('gaps', member_id))) % 5  -- 8-12 gaps
    WHEN ABS(HASH(CONCAT('gaps2', member_id))) % 10 < 3 THEN 1 + ABS(HASH(CONCAT('gaps3', member_id))) % 4  -- 30% have 1-4 gaps
    ELSE 0
  END AS open_gaps_count,

  -- nba_recommendation
  CASE
    WHEN id <= 100 THEN
      ARRAY('Schedule HbA1c test', 'Outreach for breast cancer screening', 'Care coordination referral',
            'Medication adherence follow-up', 'Diabetic eye exam reminder')[ABS(HASH(CONCAT('nba', member_id))) % 5]
    WHEN ABS(HASH(CONCAT('gaps2', member_id))) % 10 < 3 THEN
      ARRAY('Schedule preventive visit', 'Colorectal screening reminder', 'BP check follow-up',
            'Well-child visit reminder', 'Depression screening')[ABS(HASH(CONCAT('nba2', member_id))) % 5]
    ELSE NULL
  END AS nba_recommendation,

  -- attributed_aco_id: ~30% of MA members attributed to an ACO
  CASE
    WHEN lob = 'MA' AND ABS(HASH(CONCAT('aco', member_id))) % 10 < 3 THEN
      ARRAY('ACO-001','ACO-002','ACO-003','ACO-004','ACO-005')[ABS(HASH(CONCAT('aco2', member_id))) % 5]
    ELSE NULL
  END AS attributed_aco_id

FROM base;
```

**Validation:**
```sql
-- Distribution check
SELECT lob, COUNT(*) AS members, ROUND(AVG(risk_score), 3) AS avg_risk,
  SUM(CASE WHEN open_gaps_count > 0 THEN 1 ELSE 0 END) AS members_with_gaps
FROM `home_matthew_giglia`.`webinar_demo`.`dim_member`
GROUP BY lob ORDER BY lob;

-- High-risk members check (should be ~100 with risk > 3.0)
SELECT COUNT(*) AS high_risk_count
FROM `home_matthew_giglia`.`webinar_demo`.`dim_member`
WHERE risk_score > 3.0 AND open_gaps_count >= 8;
```

---

## 3. gold_quality_measures

6 HEDIS measures × 4 LOBs × 12 months = 288 rows. Planted so BCS and HbA1c are below 4-star for MA.

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`gold_quality_measures`
WITH months AS (
  SELECT EXPLODE(SEQUENCE(DATE'2025-06-01', DATE'2026-05-01', INTERVAL 1 MONTH)) AS year_month
),
lobs AS (
  SELECT EXPLODE(ARRAY('Commercial','MA','Medicaid','Individual')) AS lob
),
measures AS (
  SELECT * FROM VALUES
    ('BCS',       'Breast Cancer Screening',                    'Cancer Screening',       0.6800, 0.7400, 0.8000),
    ('CCS',       'Colorectal Cancer Screening',                'Cancer Screening',       0.6500, 0.7200, 0.7800),
    ('CDC-HBA1C', 'Diabetes HbA1c Control (<8.0%)',             'Diabetes',               0.5200, 0.6000, 0.6800),
    ('CDC-EYE',   'Diabetic Eye Examination',                   'Diabetes',               0.5500, 0.6500, 0.7200),
    ('CBP',       'Controlling High Blood Pressure (<140/90)',  'Cardiovascular',         0.5800, 0.6800, 0.7500),
    ('FUH-7',     'Follow-Up After Hospitalization (7 days)',   'Behavioral Health',      0.4000, 0.5000, 0.6000)
  AS t(measure_id, measure_name, condition_domain, star_3_cutpoint, star_4_cutpoint, star_5_cutpoint)
)
SELECT
  ms.measure_id,
  ms.measure_name,
  l.lob,
  m.year_month,

  -- current_rate: planted to tell the story
  ROUND(CASE
    -- BCS: MA below 4-star (0.72 vs 0.74 cutpoint)
    WHEN ms.measure_id = 'BCS' AND l.lob = 'MA' THEN 0.70 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
    WHEN ms.measure_id = 'BCS' THEN 0.74 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    -- HbA1c: MA below 4-star (0.58 vs 0.60 cutpoint)
    WHEN ms.measure_id = 'CDC-HBA1C' AND l.lob = 'MA' THEN 0.56 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
    WHEN ms.measure_id = 'CDC-HBA1C' THEN 0.60 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    -- CBP: healthy across all LOBs
    WHEN ms.measure_id = 'CBP' THEN 0.68 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    -- CCS: MA barely passing (0.73 vs 0.72 cutpoint)
    WHEN ms.measure_id = 'CCS' AND l.lob = 'MA' THEN 0.71 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
    WHEN ms.measure_id = 'CCS' THEN 0.73 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    -- Eye exam: moderate
    WHEN ms.measure_id = 'CDC-EYE' THEN 0.63 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    -- FUH-7: moderate
    WHEN ms.measure_id = 'FUH-7' THEN 0.48 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002

    ELSE 0.65
  END, 4) AS current_rate,

  ms.star_3_cutpoint,
  ms.star_4_cutpoint,
  ms.star_5_cutpoint,

  -- eligible_count: varies by LOB and measure
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 8000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 2000
    WHEN 'MA'         THEN 5000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 1500
    WHEN 'Medicaid'   THEN 5000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 1500
    WHEN 'Individual' THEN 2000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 500
  END AS INT) AS eligible_count,

  -- gap_count: derived from current_rate and eligible_count
  CAST(ROUND(
    CASE l.lob
      WHEN 'Commercial' THEN 8000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 2000
      WHEN 'MA'         THEN 5000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 1500
      WHEN 'Medicaid'   THEN 5000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 1500
      WHEN 'Individual' THEN 2000 + ABS(HASH(CONCAT(ms.measure_id, l.lob))) % 500
    END
    * (1.0 - CASE
      WHEN ms.measure_id = 'BCS' AND l.lob = 'MA' THEN 0.70 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'BCS' THEN 0.74 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CDC-HBA1C' AND l.lob = 'MA' THEN 0.56 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CDC-HBA1C' THEN 0.60 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CBP' THEN 0.68 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CCS' AND l.lob = 'MA' THEN 0.71 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CCS' THEN 0.73 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'CDC-EYE' THEN 0.63 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      WHEN ms.measure_id = 'FUH-7' THEN 0.48 + MONTHS_BETWEEN(m.year_month, DATE'2025-06-01') * 0.002
      ELSE 0.65
    END)
  ) AS INT) AS gap_count,

  ms.condition_domain

FROM measures ms CROSS JOIN lobs l CROSS JOIN months m;
```

**Validation:**
```sql
-- BCS for MA in May 2026 should be ~0.72 (below 0.74 cutpoint)
SELECT measure_name, lob, current_rate, star_4_cutpoint,
  CASE WHEN current_rate < star_4_cutpoint THEN 'BELOW 4-STAR' ELSE 'OK' END AS status
FROM `home_matthew_giglia`.`webinar_demo`.`gold_quality_measures`
WHERE year_month = '2026-05-01' AND lob = 'MA'
ORDER BY measure_name;
```

---

## 4. gold_utilization_monthly

4 LOBs × 10 states × 12 months = 480 rows. FL/TX/CA get 2× avoidable ratio.

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`gold_utilization_monthly`
WITH months AS (
  SELECT EXPLODE(SEQUENCE(DATE'2025-06-01', DATE'2026-05-01', INTERVAL 1 MONTH)) AS year_month
),
states AS (
  SELECT EXPLODE(ARRAY('NY','FL','TX','CA','PA','OH','IL','GA','NC','MI')) AS state
),
lobs AS (
  SELECT EXPLODE(ARRAY('Commercial','MA','Medicaid','Individual')) AS lob
)
SELECT
  l.lob, s.state, m.year_month,

  -- ip_admits
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 45 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 15
    WHEN 'MA'         THEN 65 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 20
    WHEN 'Medicaid'   THEN 55 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 18
    WHEN 'Individual' THEN 20 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 10
  END AS INT) AS ip_admits,

  -- ed_visits
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 180 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 40
    WHEN 'MA'         THEN 220 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 50
    WHEN 'Medicaid'   THEN 250 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 60
    WHEN 'Individual' THEN 80 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 20
  END AS INT) AS ed_visits,

  -- readmissions
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 5 + ABS(HASH(CONCAT(s.state, l.lob, 'ra', CAST(m.year_month AS STRING)))) % 4
    WHEN 'MA'         THEN 8 + ABS(HASH(CONCAT(s.state, l.lob, 'ra', CAST(m.year_month AS STRING)))) % 5
    WHEN 'Medicaid'   THEN 7 + ABS(HASH(CONCAT(s.state, l.lob, 'ra', CAST(m.year_month AS STRING)))) % 5
    WHEN 'Individual' THEN 2 + ABS(HASH(CONCAT(s.state, l.lob, 'ra', CAST(m.year_month AS STRING)))) % 3
  END AS INT) AS readmissions,

  -- avoidable_ed_visits: FL, TX, CA get ~35% avoidable rate; others ~17%
  CAST(ROUND(
    CASE l.lob
      WHEN 'Commercial' THEN 180 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 40
      WHEN 'MA'         THEN 220 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 50
      WHEN 'Medicaid'   THEN 250 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 60
      WHEN 'Individual' THEN 80 + ABS(HASH(CONCAT(s.state, l.lob, 'ed', CAST(m.year_month AS STRING)))) % 20
    END
    * CASE WHEN s.state IN ('FL','TX','CA') THEN 0.35 ELSE 0.17 END
  ) AS INT) AS avoidable_ed_visits,

  -- avoidable_ip_admits
  CAST(ROUND(
    CASE l.lob
      WHEN 'Commercial' THEN 45 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 15
      WHEN 'MA'         THEN 65 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 20
      WHEN 'Medicaid'   THEN 55 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 18
      WHEN 'Individual' THEN 20 + ABS(HASH(CONCAT(s.state, l.lob, CAST(m.year_month AS STRING)))) % 10
    END
    * CASE WHEN s.state IN ('FL','TX','CA') THEN 0.20 ELSE 0.10 END
  ) AS INT) AS avoidable_ip_admits,

  -- op_visits
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 1200 + ABS(HASH(CONCAT(s.state, l.lob, 'op', CAST(m.year_month AS STRING)))) % 300
    WHEN 'MA'         THEN 900 + ABS(HASH(CONCAT(s.state, l.lob, 'op', CAST(m.year_month AS STRING)))) % 250
    WHEN 'Medicaid'   THEN 800 + ABS(HASH(CONCAT(s.state, l.lob, 'op', CAST(m.year_month AS STRING)))) % 200
    WHEN 'Individual' THEN 400 + ABS(HASH(CONCAT(s.state, l.lob, 'op', CAST(m.year_month AS STRING)))) % 100
  END AS INT) AS op_visits,

  -- rx_fills
  CAST(CASE l.lob
    WHEN 'Commercial' THEN 3500 + ABS(HASH(CONCAT(s.state, l.lob, 'rx', CAST(m.year_month AS STRING)))) % 500
    WHEN 'MA'         THEN 4200 + ABS(HASH(CONCAT(s.state, l.lob, 'rx', CAST(m.year_month AS STRING)))) % 600
    WHEN 'Medicaid'   THEN 3800 + ABS(HASH(CONCAT(s.state, l.lob, 'rx', CAST(m.year_month AS STRING)))) % 500
    WHEN 'Individual' THEN 1200 + ABS(HASH(CONCAT(s.state, l.lob, 'rx', CAST(m.year_month AS STRING)))) % 200
  END AS INT) AS rx_fills

FROM lobs l CROSS JOIN states s CROSS JOIN months m;
```

---

## 5. fact_vbc_performance

5 ACOs × 6 measures × 4 quarters = 120 rows. AHP (ACO-001) has the planted narrative.

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`fact_vbc_performance`
WITH acos AS (
  SELECT EXPLODE(ARRAY('ACO-001','ACO-002','ACO-003','ACO-004','ACO-005')) AS aco_id
),
quarters AS (
  SELECT EXPLODE(ARRAY('2025-Q4','2026-Q1','2026-Q2','2026-Q3')) AS quarter
),
measures AS (
  SELECT EXPLODE(ARRAY(
    'Shared Savings YTD', 'TCOC PMPM', 'Quality Score',
    'Readmission Rate', 'ED Rate per 1K', 'Pharmacy PMPM'
  )) AS measure_name
)
SELECT
  a.aco_id,
  ms.measure_name,
  q.quarter,

  -- actual_value: AHP (ACO-001) has the planted story
  ROUND(CASE
    -- Shared Savings YTD
    WHEN ms.measure_name = 'Shared Savings YTD' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 1800000 WHEN '2026-Q1' THEN 520000 WHEN '2026-Q2' THEN 1250000 WHEN '2026-Q3' THEN 2100000 END
    WHEN ms.measure_name = 'Shared Savings YTD' THEN
      800000 + ABS(HASH(CONCAT(a.aco_id, q.quarter))) % 600000

    -- TCOC PMPM
    WHEN ms.measure_name = 'TCOC PMPM' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 855 WHEN '2026-Q1' THEN 868 WHEN '2026-Q2' THEN 878 WHEN '2026-Q3' THEN 892 END
    WHEN ms.measure_name = 'TCOC PMPM' THEN
      820 + ABS(HASH(CONCAT(a.aco_id, q.quarter, 'tcoc'))) % 80

    -- Quality Score
    WHEN ms.measure_name = 'Quality Score' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 4.05 WHEN '2026-Q1' THEN 4.10 WHEN '2026-Q2' THEN 4.15 WHEN '2026-Q3' THEN 4.20 END
    WHEN ms.measure_name = 'Quality Score' THEN
      3.5 + (ABS(HASH(CONCAT(a.aco_id, q.quarter, 'qs'))) % 10) * 0.1

    -- Readmission Rate
    WHEN ms.measure_name = 'Readmission Rate' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 0.125 WHEN '2026-Q1' THEN 0.120 WHEN '2026-Q2' THEN 0.115 WHEN '2026-Q3' THEN 0.112 END
    WHEN ms.measure_name = 'Readmission Rate' THEN
      0.10 + (ABS(HASH(CONCAT(a.aco_id, q.quarter, 'rr'))) % 5) * 0.01

    -- ED Rate per 1K
    WHEN ms.measure_name = 'ED Rate per 1K' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 305 WHEN '2026-Q1' THEN 298 WHEN '2026-Q2' THEN 290 WHEN '2026-Q3' THEN 285 END
    WHEN ms.measure_name = 'ED Rate per 1K' THEN
      270 + ABS(HASH(CONCAT(a.aco_id, q.quarter, 'ed'))) % 40

    -- Pharmacy PMPM (AHP trending up from GLP-1)
    WHEN ms.measure_name = 'Pharmacy PMPM' AND a.aco_id = 'ACO-001' THEN
      CASE q.quarter WHEN '2025-Q4' THEN 165 WHEN '2026-Q1' THEN 175 WHEN '2026-Q2' THEN 185 WHEN '2026-Q3' THEN 198 END
    WHEN ms.measure_name = 'Pharmacy PMPM' THEN
      150 + ABS(HASH(CONCAT(a.aco_id, q.quarter, 'rx'))) % 30

    ELSE 0
  END, 4) AS actual_value,

  -- target_value
  ROUND(CASE
    WHEN ms.measure_name = 'Shared Savings YTD' AND a.aco_id = 'ACO-001' THEN 1800000
    WHEN ms.measure_name = 'Shared Savings YTD' THEN 700000 + ABS(HASH(CONCAT(a.aco_id, 'tgt'))) % 400000
    WHEN ms.measure_name = 'TCOC PMPM' THEN 865
    WHEN ms.measure_name = 'Quality Score' THEN 4.00
    WHEN ms.measure_name = 'Readmission Rate' THEN 0.120
    WHEN ms.measure_name = 'ED Rate per 1K' THEN 300
    WHEN ms.measure_name = 'Pharmacy PMPM' THEN 175
    ELSE 0
  END, 4) AS target_value,

  -- benchmark_value (regional/national)
  ROUND(CASE
    WHEN ms.measure_name = 'Shared Savings YTD' THEN 1500000
    WHEN ms.measure_name = 'TCOC PMPM' THEN 880
    WHEN ms.measure_name = 'Quality Score' THEN 3.80
    WHEN ms.measure_name = 'Readmission Rate' THEN 0.130
    WHEN ms.measure_name = 'ED Rate per 1K' THEN 310
    WHEN ms.measure_name = 'Pharmacy PMPM' THEN 180
    ELSE 0
  END, 4) AS benchmark_value,

  -- trend_vs_prior_quarter (AHP specific)
  ROUND(CASE
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'TCOC PMPM' THEN 0.03
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'Pharmacy PMPM' THEN 0.08
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'Shared Savings YTD' THEN 0.15
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'Quality Score' THEN 0.02
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'Readmission Rate' THEN -0.01
    WHEN a.aco_id = 'ACO-001' AND ms.measure_name = 'ED Rate per 1K' THEN -0.02
    ELSE (ABS(HASH(CONCAT(a.aco_id, ms.measure_name, q.quarter))) % 10 - 5) * 0.01
  END, 4) AS trend_vs_prior_quarter

FROM acos a CROSS JOIN quarters q CROSS JOIN measures ms;
```

---

## 6. dim_provider_network

200 providers across 5 ACOs. AHP gets ~80 with real hospital affiliations.

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`dim_provider_network`
WITH provider_ids AS (
  SELECT EXPLODE(SEQUENCE(1, 200)) AS id
),
specialties AS (
  SELECT EXPLODE(ARRAY(
    'Primary Care', 'Primary Care', 'Primary Care', 'Primary Care',  -- 40%
    'Cardiology', 'Endocrinology', 'Orthopedics',                    -- 30%
    'Behavioral Health', 'Behavioral Health',                         -- 10%
    'Pulmonology'                                                     -- 10%
  )) AS specialty
)
SELECT
  CONCAT('PRV-', LPAD(CAST(id AS STRING), 4, '0')) AS provider_id,

  -- Synthetic provider names (deterministic)
  CONCAT(
    ARRAY('Dr. ', 'Dr. ', 'Dr. ', 'Dr. ')[ABS(HASH(CONCAT('title', id))) % 4],
    ARRAY('James','Maria','Robert','Linda','David','Patricia','Michael','Jennifer','William','Elizabeth',
          'Richard','Susan','Thomas','Karen','Charles','Nancy','Daniel','Lisa','Matthew','Sarah',
          'Anthony','Betty','Mark','Dorothy','Steven','Sandra','Paul','Ashley','Andrew','Kimberly',
          'Joshua','Emily','Kenneth','Donna','Kevin','Michelle','Brian','Carol','George','Amanda')[ABS(HASH(CONCAT('first', id))) % 40],
    ' ',
    ARRAY('Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez',
          'Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin',
          'Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson')[ABS(HASH(CONCAT('last', id))) % 30]
  ) AS provider_name,

  -- Specialty
  ARRAY('Primary Care','Primary Care','Primary Care','Primary Care',
        'Cardiology','Endocrinology','Orthopedics',
        'Behavioral Health','Behavioral Health','Pulmonology')[ABS(HASH(CONCAT('spec', id))) % 10] AS specialty,

  -- ACO assignment: first 80 to AHP, rest distributed
  CASE
    WHEN id <= 80  THEN 'ACO-001'
    WHEN id <= 110 THEN 'ACO-002'
    WHEN id <= 140 THEN 'ACO-003'
    WHEN id <= 170 THEN 'ACO-004'
    ELSE 'ACO-005'
  END AS aco_id,

  -- Hospital affiliation (AHP uses real names)
  CASE
    WHEN id <= 80 THEN
      ARRAY('Strong Memorial Hospital','Highland Hospital','F.F. Thompson Hospital',
            'Noyes Memorial Hospital','Jones Memorial Hospital')[ABS(HASH(CONCAT('hosp', id))) % 5]
    WHEN id <= 110 THEN
      ARRAY('Lakeside Medical Center','Harbor General')[ABS(HASH(CONCAT('hosp', id))) % 2]
    WHEN id <= 140 THEN
      ARRAY('Piedmont Regional','Mountain View Hospital')[ABS(HASH(CONCAT('hosp', id))) % 2]
    WHEN id <= 170 THEN
      ARRAY('Valley Medical Center','Sunrise Community Hospital')[ABS(HASH(CONCAT('hosp', id))) % 2]
    ELSE
      ARRAY('Gulf Coast Regional','Bayshore Medical Center')[ABS(HASH(CONCAT('hosp', id))) % 2]
  END AS hospital_affiliation,

  -- Attributed members
  CAST(500 + ABS(HASH(CONCAT('attr', id))) % 2000 AS INT) AS attributed_members,

  -- Cost efficiency score (0-5)
  ROUND(2.5 + (ABS(HASH(CONCAT('eff', id))) % 25) * 0.1, 2) AS cost_efficiency_score,

  -- Quality composite score (0-5)
  ROUND(2.5 + (ABS(HASH(CONCAT('qual', id))) % 25) * 0.1, 2) AS quality_composite_score

FROM provider_ids;
```

---

## Execution Order (Complete)

Run these in a single Genie Code session or notebook:

```
Step 1:  CREATE SCHEMA (from L300-A)
Step 2:  CREATE TABLE × 8 (DDL from L300-A)
Step 3:  INSERT dim_aco_contract (from L300-A)
Step 4:  INSERT dim_budget (from L300-A)
Step 5:  INSERT gold_financial_monthly (this document)
Step 6:  INSERT dim_member (this document)
Step 7:  INSERT gold_quality_measures (this document)
Step 8:  INSERT gold_utilization_monthly (this document)
Step 9:  INSERT fact_vbc_performance (this document)
Step 10: INSERT dim_provider_network (this document)
Step 11: CREATE VIEW WITH METRICS × 3 (from L300-B)
Step 12: Run validation queries (from L300-A and this document)
```

Total estimated execution time: ~5 minutes on serverless SQL warehouse.
