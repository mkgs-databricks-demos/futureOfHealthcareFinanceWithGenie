# L200-C — UC Glossary Pages: Healthcare Finance Ontology

## Overview
Business term definitions for the Genie ontology. These are structured for Unity Catalog Pages and serve as the semantic layer that makes Genie answers "correct" (not just "accurate"). Each term follows the UC Pages format: definition, business context, data usage, related terms.

## Dependencies
- Schema `home_matthew_giglia.webinar_demo` must exist
- Terms reference tables and metric views from Bundle 1

## Glossary Terms (18)

### Financial Domain

#### 1. Medical Loss Ratio (MLR)
- **Definition:** The ratio of paid medical claims to earned premium revenue. Expressed as a decimal (0.87 = 87%). Values above 1.0 indicate the plan is paying out more in claims than it collects in premium.
- **Business Context:** The ACA requires health plans to maintain MLR ≥ 80% (individual/small group) or ≥ 85% (large group). MLR is the single most-watched financial metric for health plan CFOs. A rising MLR signals margin compression.
- **Data Usage:** `MEASURE(mlr)` from `mv_financial`. Calculated as `SUM(paid_amount) / NULLIF(SUM(premium_amount), 0)`.
- **Related Terms:** PMPM, Premium, Paid Claims, Avoidable Spend

#### 2. Per Member Per Month (PMPM)
- **Definition:** A normalized cost or revenue metric calculated by dividing a total dollar amount by the number of member-months in the period. Used to compare across LOBs with different membership sizes.
- **Business Context:** PMPM is the standard unit of comparison in health plan finance. Always use PMPM (not raw totals) when comparing across lines of business, states, or time periods.
- **Data Usage:** `MEASURE(paid_pmpm)` or `MEASURE(premium_pmpm)` from `mv_financial`.
- **Related Terms:** MLR, Member Months, Paid Claims

#### 3. Avoidable Spend
- **Definition:** Medical expenditures on services that could have been prevented through better care management, care coordination, or appropriate site-of-service steering. Includes avoidable ED visits and preventable inpatient admissions.
- **Business Context:** Avoidable spend is a key lever for margin improvement. Reducing avoidable ED visits by steering to urgent care or telehealth can save $1,500–$2,500 per visit.
- **Data Usage:** `avoidable_paid_amount` in `gold_financial_monthly`; `avoidable_ed_visits` and `avoidable_ip_admits` in `gold_utilization_monthly`.
- **Related Terms:** PMPM, Utilization, Care Gap

#### 4. Incurred But Not Reported (IBNR)
- **Definition:** An actuarial estimate of claims that have been incurred (services delivered) but not yet submitted or processed. IBNR is a liability on the health plan's balance sheet.
- **Business Context:** IBNR is critical for accurate MLR calculation. A plan that underestimates IBNR will report artificially low MLR, then face a correction in future periods.
- **Data Usage:** Not directly in demo tables (mentioned in talk track only).
- **Related Terms:** MLR, Paid Claims, Premium

#### 5. Premium
- **Definition:** The monthly payment collected from members or employers for health insurance coverage. Premium revenue is the denominator of MLR.
- **Business Context:** Under ACA community rating, premiums are set by age, geography, and tobacco use — not by individual health status. This constraint makes margin management a portfolio optimization problem.
- **Data Usage:** `premium_amount` in `gold_financial_monthly`; `MEASURE(premium_pmpm)` from `mv_financial`.
- **Related Terms:** MLR, PMPM, Member Months

#### 6. Line of Business (LOB)
- **Definition:** A segment of a health plan's membership defined by the insurance product type. Common LOBs: Commercial (employer-sponsored), Medicare Advantage (MA), Medicaid, Individual (ACA Marketplace).
- **Business Context:** Each LOB has different regulatory requirements, reimbursement structures, risk profiles, and margin characteristics. Cross-LOB comparisons must be normalized per member-month.
- **Data Usage:** `lob` dimension in all tables and metric views. Values: Commercial, MA, Medicaid, Individual.
- **Related Terms:** MLR, PMPM, Premium

### Quality Domain

#### 7. HEDIS
- **Definition:** Healthcare Effectiveness Data and Information Set. A standardized set of performance measures maintained by NCQA, used by health plans to measure quality of care across clinical domains.
- **Business Context:** HEDIS measures directly impact STARS ratings (Medicare Advantage) and quality bonuses. Plans with higher STARS ratings receive higher per-member payments from CMS.
- **Data Usage:** `gold_quality_measures` table; `mv_quality` metric view. Measures include HbA1c control, BCS, CCS, BP control, diabetic eye exam.
- **Related Terms:** STARS, Care Gap, Gap Closure Rate, Star Cutpoint

#### 8. STARS Rating
- **Definition:** CMS's 5-star quality rating system for Medicare Advantage plans. Based on HEDIS measures, patient experience (CAHPS), and operational metrics. Higher stars = higher CMS payments.
- **Business Context:** The difference between 3 stars and 5 stars can be worth $50–$100+ PMPM in bonus payments. Quality improvement is a direct revenue lever for MA plans.
- **Data Usage:** `star_3_cutpoint` and `star_4_cutpoint` in `gold_quality_measures`.
- **Related Terms:** HEDIS, Care Gap, Quality Bonus

#### 9. Care Gap
- **Definition:** A HEDIS-eligible member who has not received the required clinical service (the "numerator event") within the measurement window. Example: a diabetic member who hasn't had an HbA1c test in the last 12 months.
- **Business Context:** Closing care gaps improves STARS ratings, quality bonuses, and patient outcomes. Care gap outreach is a primary activity for care management teams.
- **Data Usage:** `gap_count` and `eligible_count` in `gold_quality_measures`; `open_gaps_count` in `dim_member`.
- **Related Terms:** HEDIS, Gap Closure Rate, STARS

#### 10. Gap Closure Rate
- **Definition:** The percentage of eligible members who have completed the required clinical service. Calculated as 1 - (gap_count / eligible_count).
- **Business Context:** Gap closure rate is the operational metric that care management teams track daily. It directly drives HEDIS measure performance and STARS ratings.
- **Data Usage:** `MEASURE(gap_closure_rate)` from `mv_quality`.
- **Related Terms:** Care Gap, HEDIS, STARS

### VBC Domain

#### 11. Total Cost of Care (TCOC)
- **Definition:** The total medical expenditure for an attributed population, expressed as PMPM. Includes all claims (medical, pharmacy, behavioral health) for members attributed to a provider or ACO.
- **Business Context:** TCOC is the primary financial metric in value-based contracts. If actual TCOC is below the benchmark, the provider/ACO earns shared savings.
- **Data Usage:** `actual_value` in `fact_vbc_performance` where measure_name = 'TCOC PMPM'.
- **Related Terms:** Shared Savings, Attribution, Benchmark

#### 12. Shared Savings
- **Definition:** The financial reward earned by a provider or ACO when actual TCOC is below the contractual benchmark. Calculated as (benchmark - actual TCOC) × attributed member-months × sharing rate.
- **Business Context:** Shared savings is the primary incentive mechanism in value-based contracts. AHP distributes gainsharing 60% to PCPs, 25% to specialists, 15% to hospitals.
- **Data Usage:** `actual_value` in `fact_vbc_performance` where measure_name = 'Shared Savings YTD'.
- **Related Terms:** TCOC, Gainsharing, Attribution

#### 13. Attribution
- **Definition:** The process of assigning a member/patient to a primary care provider or ACO for purposes of measuring cost and quality performance. Attribution can be prospective (assigned at start of year) or retrospective (based on claims patterns).
- **Business Context:** Attribution methodology determines which members "count" toward an ACO's performance. Disputes over attribution are common in VBC contracts.
- **Data Usage:** `attributed_members` in `dim_aco_contract` and `dim_provider_network`.
- **Related Terms:** TCOC, Shared Savings, ACO

#### 14. Gainsharing
- **Definition:** The distribution of shared savings to participating providers based on their contribution to cost and quality performance. AHP's published split: 60% PCPs, 25% specialists, 15% hospitals.
- **Business Context:** Gainsharing aligns provider incentives with plan financial goals. AHP has distributed gainsharing every year since 2014.
- **Data Usage:** `gainsharing_split` in `dim_aco_contract`.
- **Related Terms:** Shared Savings, VBC, AHP

#### 15. Clinically Integrated Network (CIN)
- **Definition:** A network of physicians, hospitals, and other providers that collaborate on clinical quality, care coordination, and cost management under value-based contracts with payers. AHP is a CIN.
- **Business Context:** CINs are the organizational structure through which providers participate in value-based care. They are not insurance companies — they contract with payers (like Excellus BCBS) to manage attributed populations.
- **Data Usage:** `contract_type` in `dim_aco_contract`.
- **Related Terms:** AHP, VBC, Attribution, Gainsharing

### Organizational Domain

#### 16. AHP (Accountable Health Partners)
- **Definition:** A Rochester-based clinically integrated network of 4,000+ providers across 21 Upstate NY counties and 3 PA counties, anchored by UR Medicine / University of Rochester Medical Center. AHP holds value-based contracts with Excellus BCBS, MVP Health Care, and Monroe Plan.
- **Business Context:** AHP is the value-based care arm of UR Medicine. It is NOT a health plan or insurance company. It distributes gainsharing annually (60/25/15 split) and tracks quality through the PCP Reward Plan.
- **Data Usage:** `dim_aco_contract` where aco_name = 'Accountable Health Partners (AHP)'.
- **Related Terms:** CIN, UR Medicine, Excellus BCBS, Gainsharing

#### 17. UR Medicine
- **Definition:** University of Rochester Medicine — an academic health system with 8 hospitals, 32,000+ employees, ~$6B annual revenue, serving 27+ counties in the Finger Lakes and Southern Tier regions of New York.
- **Business Context:** UR Medicine is the parent system of AHP. Its flagship is Strong Memorial Hospital (897 beds, Level I Trauma). Rebranded from "URMC" to "University of Rochester Medicine" in April 2026.
- **Data Usage:** `parent_system` in `dim_aco_contract`.
- **Related Terms:** AHP, Strong Memorial, Finger Lakes

#### 18. Excellus BlueCross BlueShield
- **Definition:** The dominant commercial health plan in the Rochester/Finger Lakes region. Excellus is AHP's primary payer partner for value-based contracts.
- **Business Context:** AHP's quality reporting during the 2024 Health Catalyst transition was initially Excellus-only (Commercial and Medicare scorecards). Excellus is the Tier 1 payer for University of Rochester employee health plans.
- **Data Usage:** `payers` in `dim_aco_contract`.
- **Related Terms:** AHP, MVP Health Care, VBC

## Implementation Priority
All 18 terms should be created as UC Glossary Pages before the Genie Agent is configured. The Genie ontology uses these definitions to ground its answers.

## Deployment
Glossary pages are created via the Databricks UI or API as part of Bundle 1 deployment. They are not SQL objects — they are UC metadata.
