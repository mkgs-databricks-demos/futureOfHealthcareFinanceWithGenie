# L300-A — Table Schemas & Synthetic Data SQL

## Overview
Complete DDL and INSERT statements for all 8 tables. Data is deterministically generated with planted narrative values per L100 Data Narrative.

## Schema Creation
```sql
CREATE SCHEMA IF NOT EXISTS `home_matthew_giglia`.`webinar_demo`
COMMENT 'Synthetic healthcare finance demo data for Sep 2026 webinar. All data is fictional.';
```

---

## Table 1: `dim_aco_contract`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`dim_aco_contract` (
  `aco_id` STRING NOT NULL COMMENT 'Unique ACO identifier',
  `aco_name` STRING NOT NULL COMMENT 'Full name of the Accountable Care Organization or clinically integrated network',
  `aco_short_name` STRING COMMENT 'Abbreviated name for display',
  `parent_system` STRING COMMENT 'Parent health system or organization',
  `exec_medical_director` STRING COMMENT 'Name of the Executive Medical Director or equivalent clinical leader',
  `exec_title` STRING COMMENT 'Title of the clinical executive (e.g., Executive Medical Director, CMO)',
  `contract_type` STRING COMMENT 'Type of value-based arrangement: Shared Savings, Capitation, Bundled Payment, CIN',
  `payers` STRING COMMENT 'Comma-separated list of payer partners',
  `region` STRING COMMENT 'Geographic region served',
  `counties_served` INT COMMENT 'Number of counties in the network footprint',
  `attributed_members` INT COMMENT 'Total members attributed to this ACO across all payer contracts',
  `provider_count` INT COMMENT 'Number of providers in the network',
  `hospital_count` INT COMMENT 'Number of hospitals in the network',
  `gainsharing_split_pcp_pct` DECIMAL(5,2) COMMENT 'Percentage of gainsharing pool allocated to PCPs',
  `gainsharing_split_specialist_pct` DECIMAL(5,2) COMMENT 'Percentage allocated to specialists',
  `gainsharing_split_hospital_pct` DECIMAL(5,2) COMMENT 'Percentage allocated to hospitals',
  `contract_start_date` DATE COMMENT 'Date the current VBC contract period began',
  `key_hospitals` STRING COMMENT 'Comma-separated list of major hospitals in the network'
)
COMMENT 'ACO and clinically integrated network reference data. Synthetic demo data. 5 fictional ACOs including one modeled on real AHP (Accountable Health Partners) structure.';
```

### Seed Data
```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`dim_aco_contract` VALUES
-- AHP: modeled on real Accountable Health Partners structure
('ACO-001', 'Accountable Health Partners (AHP)', 'AHP', 'UR Medicine / University of Rochester Medical Center',
 'Dr. Sarah Chen', 'Executive Medical Director', 'Multi-payer CIN (Shared Savings)',
 'Excellus BCBS, MVP Health Care', 'Finger Lakes, Upstate NY', 21, 150000, 4200, 13,
 60.00, 25.00, 15.00, '2024-01-01',
 'Strong Memorial, Highland, F.F. Thompson, Noyes Memorial, Jones Memorial'),

-- 4 additional fictional ACOs for comparison
('ACO-002', 'Lakeshore Health Alliance', 'LHA', 'Great Lakes Health System',
 'Dr. Michael Torres', 'Chief Medical Officer', 'MSSP Track 2 (Shared Savings)',
 'Anthem BCBS', 'Great Lakes, OH', 8, 85000, 1800, 5,
 55.00, 30.00, 15.00, '2024-01-01',
 'Lakeside Medical Center, Harbor General'),

('ACO-003', 'Piedmont Integrated Care', 'PIC', 'Piedmont Health Network',
 'Dr. Angela Washington', 'Executive Medical Director', 'Shared Savings + Quality Bonus',
 'BCBS of NC, Aetna', 'Piedmont, NC', 12, 110000, 2500, 7,
 60.00, 25.00, 15.00, '2023-07-01',
 'Piedmont Regional, Mountain View Hospital'),

('ACO-004', 'Valley Care Partners', 'VCP', 'Central Valley Medical Group',
 'Dr. James Park', 'Chief Medical Officer', 'Capitation + Shared Savings',
 'Blue Shield of CA, Health Net', 'Central Valley, CA', 6, 72000, 1200, 4,
 50.00, 30.00, 20.00, '2024-01-01',
 'Valley Medical Center, Sunrise Community Hospital'),

('ACO-005', 'Gulf Coast Health Collaborative', 'GCHC', 'Gulf Coast Medical Partners',
 'Dr. Maria Gonzalez', 'VP Clinical Integration', 'MSSP Track 1+ (Shared Savings)',
 'Florida Blue, Humana', 'Gulf Coast, FL', 10, 95000, 2100, 6,
 55.00, 25.00, 20.00, '2024-01-01',
 'Gulf Coast Regional, Bayshore Medical Center');
```

---

## Table 2: `dim_budget`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`dim_budget` (
  `lob` STRING NOT NULL COMMENT 'Line of business: Commercial, MA, Medicaid, Individual',
  `year_month` DATE NOT NULL COMMENT 'First day of the month (e.g., 2026-01-01)',
  `target_mlr` DECIMAL(6,4) COMMENT 'Target Medical Loss Ratio for this LOB/month. Values like 0.8500 = 85%.',
  `target_paid_pmpm` DECIMAL(10,2) COMMENT 'Target paid claims PMPM for this LOB/month',
  `target_premium_pmpm` DECIMAL(10,2) COMMENT 'Target premium PMPM for this LOB/month',
  `budget_premium` DECIMAL(14,2) COMMENT 'Total budgeted premium revenue for this LOB/month',
  `budget_paid_claims` DECIMAL(14,2) COMMENT 'Total budgeted paid claims for this LOB/month'
)
COMMENT 'Monthly budget targets by line of business. Used to calculate variance vs actuals. Synthetic demo data.';
```

### Seed Data Strategy
Generate 4 LOBs × 12 months (Jun 2025 – May 2026). Targets are set so that:
- **Commercial:** target MLR 0.85, actuals come in at 0.87 (slightly over but healthy)
- **Individual:** target MLR 0.82, actuals come in at 0.83 (on track)
- **MA:** target MLR 0.98, actuals come in at 1.003 (over target — borderline)
- **Medicaid:** target MLR 1.00, actuals come in at 1.057 (significantly over — the problem)

```sql
INSERT INTO `home_matthew_giglia`.`webinar_demo`.`dim_budget`
SELECT
  lob,
  year_month,
  CASE lob
    WHEN 'Commercial' THEN 0.8500
    WHEN 'Individual' THEN 0.8200
    WHEN 'MA' THEN 0.9800
    WHEN 'Medicaid' THEN 1.0000
  END AS target_mlr,
  CASE lob
    WHEN 'Commercial' THEN 520.00
    WHEN 'Individual' THEN 560.00
    WHEN 'MA' THEN 1070.00
    WHEN 'Medicaid' THEN 880.00
  END AS target_paid_pmpm,
  CASE lob
    WHEN 'Commercial' THEN 612.00
    WHEN 'Individual' THEN 683.00
    WHEN 'MA' THEN 1092.00
    WHEN 'Medicaid' THEN 880.00
  END AS target_premium_pmpm,
  -- budget_premium and budget_paid_claims derived from PMPM × expected member months
  CASE lob
    WHEN 'Commercial' THEN 12200000.00
    WHEN 'Individual' THEN 3410000.00
    WHEN 'MA' THEN 13700000.00
    WHEN 'Medicaid' THEN 11060000.00
  END AS budget_premium,
  CASE lob
    WHEN 'Commercial' THEN 10370000.00
    WHEN 'Individual' THEN 2796000.00
    WHEN 'MA' THEN 13426000.00
    WHEN 'Medicaid' THEN 11060000.00
  END AS budget_paid_claims
FROM (
  SELECT EXPLODE(ARRAY('Commercial', 'Individual', 'MA', 'Medicaid')) AS lob
) lobs
CROSS JOIN (
  SELECT EXPLODE(SEQUENCE(DATE'2025-06-01', DATE'2026-05-01', INTERVAL 1 MONTH)) AS year_month
) months;
```

---

## Table 3: `gold_financial_monthly`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly` (
  `lob` STRING NOT NULL COMMENT 'Line of business: Commercial, MA, Medicaid, Individual',
  `state` STRING NOT NULL COMMENT 'US state abbreviation (e.g., NY, FL, TX, CA)',
  `plan_type` STRING NOT NULL COMMENT 'Plan type: PPO, HMO, EPO, POS',
  `year_month` DATE NOT NULL COMMENT 'First day of the month',
  `paid_amount` DECIMAL(14,2) COMMENT 'Total paid medical claims for this segment/month',
  `premium_amount` DECIMAL(14,2) COMMENT 'Total earned premium revenue for this segment/month',
  `member_months` BIGINT COMMENT 'Total member-months for this segment/month',
  `avoidable_paid_amount` DECIMAL(14,2) COMMENT 'Paid claims attributable to avoidable utilization (preventable ED, avoidable IP)',
  `risk_score_avg` DECIMAL(6,4) COMMENT 'Average HCC risk score for members in this segment/month'
)
COMMENT 'Monthly financial performance aggregates by LOB, state, and plan type. Synthetic demo data. Query mv_financial metric view for governed KPIs.';
```

### Seed Data Strategy
- 4 LOBs × 10 states × 1 plan type × 12 months = ~480 rows (simplified from 2,400)
- States: NY, FL, TX, CA, PA, OH, IL, GA, NC, MI
- Plant the narrative: FL, TX, CA have 2× avoidable spend rate
- Medicaid paid_amount > premium_amount (MLR > 1.0)
- MA paid_amount ≈ premium_amount (MLR ≈ 1.0)
- Commercial and Individual: paid_amount < premium_amount (healthy)

> Full INSERT SQL to be generated by Genie Code session using deterministic EXPLODE + CASE logic.

---

## Table 4: `dim_member`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`dim_member` (
  `member_id` STRING NOT NULL COMMENT 'Unique member identifier (synthetic)',
  `lob` STRING NOT NULL COMMENT 'Line of business',
  `state` STRING NOT NULL COMMENT 'Member state of residence',
  `age_band` STRING COMMENT 'Age band: 0-17, 18-34, 35-49, 50-64, 65+',
  `gender` STRING COMMENT 'Member gender: M, F',
  `plan_type` STRING COMMENT 'Plan type: PPO, HMO, EPO, POS',
  `risk_score` DECIMAL(6,4) COMMENT 'HCC risk adjustment factor. 1.0 = average. Higher = sicker/costlier.',
  `cost_percentile` INT COMMENT 'Cost percentile within LOB (1-100). 99 = top 1% costliest.',
  `open_gaps_count` INT COMMENT 'Number of open HEDIS care gaps for this member',
  `nba_recommendation` STRING COMMENT 'Next Best Action recommendation from care management model',
  `attributed_aco_id` STRING COMMENT 'ACO ID if member is attributed to a VBC contract (nullable)'
)
COMMENT 'Member-level demographics and risk profile. Synthetic demo data. Do NOT expose member_id in user-facing queries — use for aggregation only.';
```

### Seed Data Strategy
- 50,000 members distributed across 4 LOBs (Commercial 40%, MA 25%, Medicaid 25%, Individual 10%)
- Risk scores: normal distribution centered at 1.0 for Commercial, 1.2 for MA, 1.1 for Medicaid
- Plant high-risk members: top 100 members have risk_score > 3.0 and open_gaps_count > 8
- NBA recommendations: "Schedule HbA1c test", "Outreach for BCS", "Care coordination referral", "Medication adherence follow-up"
- ~30% of MA members attributed to one of the 5 ACOs

> Full INSERT SQL to be generated by Genie Code using EXPLODE + RAND with seed.

---

## Table 5: `gold_quality_measures`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`gold_quality_measures` (
  `measure_id` STRING NOT NULL COMMENT 'HEDIS measure identifier (e.g., BCS, CDC-HBA1C, CBP)',
  `measure_name` STRING NOT NULL COMMENT 'Human-readable measure name',
  `lob` STRING NOT NULL COMMENT 'Line of business',
  `year_month` DATE NOT NULL COMMENT 'Measurement month',
  `current_rate` DECIMAL(6,4) COMMENT 'Current performance rate (0.0 to 1.0). E.g., 0.72 = 72% of eligible members completed.',
  `star_3_cutpoint` DECIMAL(6,4) COMMENT 'Rate threshold for 3-star rating',
  `star_4_cutpoint` DECIMAL(6,4) COMMENT 'Rate threshold for 4-star rating',
  `star_5_cutpoint` DECIMAL(6,4) COMMENT 'Rate threshold for 5-star rating',
  `eligible_count` INT COMMENT 'Number of members eligible for this measure',
  `gap_count` INT COMMENT 'Number of members with an open care gap (eligible but not completed)',
  `condition_domain` STRING COMMENT 'Clinical domain: Diabetes, Cardiovascular, Cancer Screening, Behavioral Health, Pediatric/Preventive'
)
COMMENT 'HEDIS quality measure performance by LOB and month. Synthetic demo data. Query mv_quality metric view for governed KPIs.';
```

### Measures to Include (from AHP real measures)
| measure_id | measure_name | condition_domain | star_4_cutpoint |
|---|---|---|---|
| BCS | Breast Cancer Screening | Cancer Screening | 0.7400 |
| CCS | Colorectal Cancer Screening | Cancer Screening | 0.7200 |
| CDC-HBA1C | Diabetes HbA1c Control (<8.0%) | Diabetes | 0.6000 |
| CDC-EYE | Diabetic Eye Examination | Diabetes | 0.6500 |
| CBP | Controlling High Blood Pressure (<140/90) | Cardiovascular | 0.6800 |
| FUH-7 | Follow-Up After Hospitalization (7 days) | Behavioral Health | 0.5000 |

### Planted Narrative
- BCS current_rate = 0.72 (below 4-star cutpoint of 0.74) — **flagged**
- CDC-HBA1C current_rate = 0.58 (below 4-star cutpoint of 0.60) — **flagged**
- CBP current_rate = 0.70 (above 4-star cutpoint of 0.68) — healthy
- CCS current_rate = 0.73 (above 4-star cutpoint of 0.72) — barely passing

---

## Table 6: `gold_utilization_monthly`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`gold_utilization_monthly` (
  `lob` STRING NOT NULL COMMENT 'Line of business',
  `state` STRING NOT NULL COMMENT 'US state abbreviation',
  `year_month` DATE NOT NULL COMMENT 'First day of the month',
  `ip_admits` INT COMMENT 'Inpatient admissions',
  `ed_visits` INT COMMENT 'Emergency department visits',
  `readmissions` INT COMMENT '30-day all-cause readmissions',
  `avoidable_ed_visits` INT COMMENT 'ED visits classified as avoidable (could have been treated in lower-cost setting)',
  `avoidable_ip_admits` INT COMMENT 'Inpatient admissions classified as potentially preventable',
  `op_visits` INT COMMENT 'Outpatient visits',
  `rx_fills` INT COMMENT 'Prescription fills'
)
COMMENT 'Monthly utilization aggregates by LOB and state. Synthetic demo data.';
```

### Planted Narrative
- FL, TX, CA: avoidable_ed_visits / ed_visits ratio = ~35% (2× plan average of ~17%)
- NY, PA, OH: avoidable ratio = ~15% (below average — well-managed)

---

## Table 7: `fact_vbc_performance`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`fact_vbc_performance` (
  `aco_id` STRING NOT NULL COMMENT 'Foreign key to dim_aco_contract',
  `measure_name` STRING NOT NULL COMMENT 'VBC performance measure: Shared Savings YTD, TCOC PMPM, Quality Score, Readmission Rate, ED Rate per 1K, Pharmacy PMPM',
  `quarter` STRING NOT NULL COMMENT 'Calendar quarter (e.g., 2026-Q1)',
  `actual_value` DECIMAL(14,4) COMMENT 'Actual performance value for this measure/quarter',
  `target_value` DECIMAL(14,4) COMMENT 'Contractual target or benchmark value',
  `benchmark_value` DECIMAL(14,4) COMMENT 'Regional or national benchmark for comparison',
  `trend_vs_prior_quarter` DECIMAL(8,4) COMMENT 'Percentage change vs prior quarter (e.g., 0.03 = +3%)'
)
COMMENT 'Quarterly value-based care performance by ACO and measure. Synthetic demo data. Query mv_vbc_performance metric view for governed KPIs.';
```

### Planted Narrative for AHP (ACO-001)
| measure_name | Q3 2026 actual | target | trend_vs_prior |
|---|---|---|---|
| Shared Savings YTD | 2,100,000 | 1,800,000 | +0.15 |
| TCOC PMPM | 892.00 | 865.00 | +0.03 |
| Quality Score | 4.20 | 4.00 | +0.02 |
| Readmission Rate | 0.112 | 0.120 | -0.01 |
| ED Rate per 1K | 285.0 | 300.0 | -0.02 |
| Pharmacy PMPM | 198.00 | 175.00 | +0.08 |

**Story:** AHP is performing well on shared savings ($2.1M vs $1.8M target) and quality (4.2 vs 4.0 target), but TCOC PMPM is trending up 3% QoQ driven by pharmacy PMPM (+8% QoQ from GLP-1 utilization). This is the conversation topic for the Saturday meeting with Dr. Sarah Chen.

---

## Table 8: `dim_provider_network`

### DDL
```sql
CREATE OR REPLACE TABLE `home_matthew_giglia`.`webinar_demo`.`dim_provider_network` (
  `provider_id` STRING NOT NULL COMMENT 'Unique provider identifier (synthetic)',
  `provider_name` STRING NOT NULL COMMENT 'Provider display name (synthetic)',
  `specialty` STRING COMMENT 'Medical specialty: Primary Care, Cardiology, Endocrinology, Orthopedics, etc.',
  `aco_id` STRING NOT NULL COMMENT 'Foreign key to dim_aco_contract',
  `hospital_affiliation` STRING COMMENT 'Primary hospital affiliation',
  `attributed_members` INT COMMENT 'Number of members attributed to this provider',
  `cost_efficiency_score` DECIMAL(4,2) COMMENT 'Cost efficiency score (0-5 scale). 5 = most efficient.',
  `quality_composite_score` DECIMAL(4,2) COMMENT 'Quality composite score (0-5 scale). 5 = highest quality.'
)
COMMENT 'Provider-level network data by ACO. Synthetic demo data.';
```

### Seed Data Strategy
- 200 providers across 5 ACOs (AHP gets ~80, others get ~30 each)
- AHP providers affiliated with real hospital names (Strong Memorial, Highland, etc.)
- Specialties: Primary Care (40%), Cardiology (10%), Endocrinology (10%), Orthopedics (10%), Behavioral Health (10%), Other (20%)
- Synthetic provider names generated deterministically

---

## Validation Queries

```sql
-- Verify planted narrative holds
-- Beat 1: Medicaid MLR > 1.0
SELECT 'Beat 1: Medicaid MLR' AS test,
  SUM(paid_amount) / SUM(premium_amount) AS mlr
FROM `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly`
WHERE lob = 'Medicaid' AND year_month = '2026-05-01';

-- Beat 1: Commercial MLR < 0.90
SELECT 'Beat 1: Commercial MLR' AS test,
  SUM(paid_amount) / SUM(premium_amount) AS mlr
FROM `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly`
WHERE lob = 'Commercial' AND year_month = '2026-05-01';

-- Beat 2: BCS below 4-star
SELECT 'Beat 2: BCS below 4-star' AS test, current_rate, star_4_cutpoint
FROM `home_matthew_giglia`.`webinar_demo`.`gold_quality_measures`
WHERE measure_id = 'BCS' AND lob = 'MA' AND year_month = '2026-05-01';

-- Beat 3: AHP exists
SELECT 'Beat 3: AHP exists' AS test, aco_name, exec_medical_director
FROM `home_matthew_giglia`.`webinar_demo`.`dim_aco_contract`
WHERE aco_id = 'ACO-001';

-- Beat 3: AHP shared savings > $2M
SELECT 'Beat 3: AHP shared savings' AS test, actual_value
FROM `home_matthew_giglia`.`webinar_demo`.`fact_vbc_performance`
WHERE aco_id = 'ACO-001' AND measure_name = 'Shared Savings YTD' AND quarter = '2026-Q3';
```
