# L300-C — Genie Agent Instructions & Benchmark Prompts

## Overview
Complete instruction text for the "Healthcare Finance Intelligence" Genie Agent, plus benchmark prompts for each demo beat with expected answers.

---

## Full Instruction Text

Paste this verbatim into the Genie Agent's Settings → Instructions:

```
GLOSSARY

MLR (Medical Loss Ratio) = paid medical claims / earned premium. Lower is better for the payer. Values above 1.0 indicate claims exceed premium revenue.
PMPM (Per Member Per Month) = dollar amount divided by member-months. Always normalize cross-LOB comparisons per member-month.
Care gap = a HEDIS-eligible member who has not received the numerator event in the measurement window.
Avoidable utilization = ED visits or inpatient admissions classified as preventable or treatable in a lower-cost setting.
TCOC (Total Cost of Care) = total medical expenditure for an attributed population, expressed as PMPM.
Shared savings = financial reward when actual TCOC is below the contractual benchmark.
Gainsharing = distribution of shared savings to providers. AHP split: 60% PCPs, 25% specialists, 15% hospitals.
AHP (Accountable Health Partners) = a clinically integrated network of 4,000+ providers across 21 Upstate NY counties, anchored by UR Medicine / University of Rochester Medical Center. AHP holds value-based contracts with Excellus BCBS and MVP Health Care.
HEDIS = Healthcare Effectiveness Data and Information Set. Standardized quality measures maintained by NCQA.
STARS = CMS 5-star quality rating system for Medicare Advantage plans. Higher stars = higher CMS bonus payments.
LOB values: Commercial, MA (Medicare Advantage), Medicaid, Individual.

BEHAVIORAL RULES

1. Always query metric views (mv_financial, mv_quality, mv_vbc_performance) for KPIs. Do not query raw gold_ tables for aggregate metrics.
2. When comparing across LOBs, always normalize per member-month (use PMPM measures, not raw sums).
3. "How is X trending" → render a monthly time series using year_month dimension.
4. When discussing financial performance, always include budget variance by joining dim_budget on lob and year_month.
5. For VBC questions, always identify the ACO name and executive medical director from dim_aco_contract.
6. For quality questions, compare current_rate to star_4_cutpoint. Flag any measure where current_rate < star_4_cutpoint.
7. "Top members" or "drill to members" → return at most 10 rows from dim_member. Never expose member_id in results — use for filtering only.
8. When asked about "AHP" or "Accountable Health Partners," query fact_vbc_performance WHERE aco_id = 'ACO-001' and join dim_aco_contract for context.
9. When asked about a "meeting" or "calendar" related to AHP, note that the Executive Medical Director is Dr. Sarah Chen and the key discussion topics are: shared savings performance, quality measures (HbA1c, BCS, CCS), and specialty pharmacy trends (GLP-1 utilization).
10. When asked for a "morning briefing" or "what needs attention," prioritize: (a) LOBs with MLR > 1.0, (b) quality measures below 4-star cutpoint, (c) states with highest avoidable spend share.
11. All data is synthetic. If asked, acknowledge this is demo data for illustration purposes.

MEASURE() SYNTAX REMINDER

Metric views require MEASURE() function for all measures. Example:
  SELECT lob, MEASURE(mlr), MEASURE(paid_pmpm)
  FROM mv_financial
  WHERE year_month = '2026-05-01'
  GROUP BY ALL

Do NOT use JOINs with metric views. If you need to combine metric view data with dimension tables, query them separately and present results together.

CONDITION DOMAINS FOR QUALITY MEASURES

Diabetes: CDC-HBA1C (HbA1c control), CDC-EYE (Diabetic eye exam)
Cardiovascular: CBP (Blood pressure control)
Cancer Screening: BCS (Breast cancer screening), CCS (Colorectal cancer screening)
Behavioral Health: FUH-7 (Follow-up after hospitalization)
```

---

## Benchmark Prompts & Expected Answers

### Beat 1: CFO Morning Briefing

**Prompt:**
```
I'm a health plan CFO starting my morning. Give me a quick executive briefing on our financial performance — specifically MLR by line of business, any lines where paid claims PMPM is trending above premium PMPM, and which states have the highest avoidable spend. Flag anything that needs attention.
```

**Expected Answer Should Include:**
- Medicaid MLR ~106% — claims exceeding premium, $1.2M behind budget YTD
- MA MLR ~100.3% — borderline, $0.3M behind budget
- Commercial MLR ~87% — healthy, on track
- Individual MLR ~83% — healthy
- FL, TX, CA flagged for avoidable ED spend (2× plan average)
- Recommendation: focus on Medicaid margin and avoidable utilization in FL/TX/CA

**Follow-up Prompt:**
```
Which states are driving the Medicaid MLR problem? Show me avoidable spend by state for Medicaid.
```

---

### Beat 2a: Actuary Persona

**Prompt:**
```
Show me risk score trends by LOB over the last 12 months. Where are risk scores rising faster than premium PMPM?
```

**Expected Answer Should Include:**
- MA risk scores trending up ~0.05 YoY
- MA premium PMPM relatively flat
- Gap between risk acuity and pricing = margin pressure
- Commercial risk scores stable

---

### Beat 2b: Quality Director Persona

**Prompt:**
```
Which HEDIS measures are currently below 4-star cutpoints for our MA population? What's the gap count and estimated financial exposure?
```

**Expected Answer Should Include:**
- BCS at 72% (4-star cutpoint 74%) — 2 percentage points below
- CDC-HBA1C at 58% (cutpoint 60%) — 2 percentage points below
- Gap counts for each measure
- Note: these measures directly impact STARS bonus payments

---

### Beat 2c: Care Manager Persona

**Prompt:**
```
Show me the top 10 highest-risk members with the most open care gaps. What are the recommended interventions?
```

**Expected Answer Should Include:**
- 10 members with risk_score > 3.0 and open_gaps_count > 8
- NBA recommendations: HbA1c test, BCS outreach, care coordination referral
- No member_id or PII exposed — show lob, state, age_band, risk_score, gaps, NBA only

---

### Beat 3: CFO Calendar + Meeting Prep

**Prompt:**
```
I have a meeting with Dr. Sarah Chen from Accountable Health Partners this Saturday. Tell me about AHP's value-based care performance — shared savings, quality scores, and any cost trends I should be aware of.
```

**Expected Answer Should Include:**
- AHP = Accountable Health Partners, CIN with 4,000+ providers, 21 counties, anchored by UR Medicine
- Dr. Sarah Chen is the Executive Medical Director
- Shared savings: $2.1M YTD (above $1.8M target) ✅
- Quality score: 4.2 (above 4.0 target) ✅
- TCOC PMPM: $892 (above $865 target) ⚠️ — trending up 3% QoQ
- Pharmacy PMPM: $198 (above $175 target) ⚠️ — trending up 8% QoQ from GLP-1
- Readmission rate: 11.2% (below 12.0% target) ✅
- Recommendation: discuss GLP-1 utilization management and diabetes care gap closure

**Follow-up Prompt:**
```
What specific quality measures should I discuss with Dr. Chen? Which ones are AHP's providers struggling with?
```

---

### Beat 4: The Reveal

No data prompt needed. Speaker says:
> "By the way — this presentation was built in Genie One. I literally do my whole job in this tool."

---

## Pre-Demo Checklist

- [ ] All 8 tables populated with synthetic data
- [ ] All 3 metric views created and queryable
- [ ] Genie Agent created with all 11 tables/views attached
- [ ] Instructions pasted verbatim
- [ ] Each benchmark prompt tested and returns expected narrative
- [ ] Saturday calendar event created matching AHP details
- [ ] Genie One scheduled task configured for morning briefing
- [ ] Backup screenshots taken in case of live demo issues
