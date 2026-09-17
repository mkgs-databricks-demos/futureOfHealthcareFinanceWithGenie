# L200-B — Bundle 2: AI/BI Experience (`webinar-demo-aibi`)

## Overview
This bundle deploys the Genie Agent and AI/BI Dashboard that consume the data foundation from Bundle 1. The Genie Agent is the primary demo surface for the webinar; the dashboard provides a visual complement.

## Dependencies
- **Bundle 1** (`webinar-demo-data`) must be deployed first
- All 8 tables and 3 metric views must exist in `home_matthew_giglia.webinar_demo`
- Serverless SQL Warehouse for Genie Agent queries

## Bundle Structure
```
webinar-demo-aibi/
├── databricks.yml
├── resources/
│   ├── genie_agent/
│   │   ├── agent_config.yml        # Genie Agent metadata
│   │   ├── instructions.md         # Full instruction set
│   │   ├── example_queries.yml     # Example SQL for Genie
│   │   └── benchmark_prompts.yml   # Test prompts per demo beat
│   └── dashboard/
│       └── healthcare_finance.lvdash.json
└── tests/
    └── benchmark_results.md        # Expected answers for each prompt
```

## Genie Agent Design

### Metadata
| Field | Value |
|---|---|
| **Name** | Healthcare Finance Intelligence |
| **Description** | Executive-level health plan financial intelligence. Ask questions about MLR, PMPM, quality measures, utilization, care gaps, and value-based care performance across lines of business, states, and ACO contracts. Synthetic demo data. |
| **Mode** | Agent Mode (not classic) |
| **SQL Warehouse** | Serverless |

### Tables Attached (11)
**Metric Views (query these for KPIs):**
1. `home_matthew_giglia.webinar_demo.mv_financial`
2. `home_matthew_giglia.webinar_demo.mv_quality`
3. `home_matthew_giglia.webinar_demo.mv_vbc_performance`

**Dimension/Fact Tables (for detail drill-down):**
4. `home_matthew_giglia.webinar_demo.gold_financial_monthly`
5. `home_matthew_giglia.webinar_demo.dim_budget`
6. `home_matthew_giglia.webinar_demo.dim_member`
7. `home_matthew_giglia.webinar_demo.gold_quality_measures`
8. `home_matthew_giglia.webinar_demo.gold_utilization_monthly`
9. `home_matthew_giglia.webinar_demo.fact_vbc_performance`
10. `home_matthew_giglia.webinar_demo.dim_aco_contract`
11. `home_matthew_giglia.webinar_demo.dim_provider_network`

### Instruction Set (Summary)
Full text in L300-C. Key sections:

**Glossary:**
- MLR = paid medical claims / earned premium. Lower is better for the payer.
- PMPM = paid amount / member-months. Always normalize cross-LOB comparisons per member-month.
- Care gap = a HEDIS-eligible member who has not received the numerator event.
- Avoidable utilization = ED visits or IP admissions where avoidable flag = true.
- TCOC = Total Cost of Care PMPM for an attributed ACO population.
- Shared savings = actual TCOC below benchmark × sharing rate.
- AHP = Accountable Health Partners, a clinically integrated network of 4,000+ providers across 21 Upstate NY counties, anchored by UR Medicine.

**Behavioral Rules:**
- Always query metric views for KPIs, not raw tables
- "How is X trending" → monthly time series using year_month
- Cross-LOB comparison → normalize per member-month (PMPM)
- Financial questions → include budget variance from dim_budget
- VBC questions → identify the ACO name and executive medical director from dim_aco_contract
- Quality questions → compare current_rate to star_4_cutpoint; flag measures below threshold
- "Top members" or "drill to members" → return at most 10 rows from dim_member; never expose full_name or PII
- LOB values: Commercial, MA (Medicare Advantage), Medicaid, Individual

**Demo-Specific Instructions:**
- When asked about "AHP" or "Accountable Health Partners," pull from fact_vbc_performance joined to dim_aco_contract
- When asked about a "meeting" or "calendar," note that AHP's Executive Medical Director is Dr. Sarah Chen and the focus areas are shared savings, quality measures (HbA1c, BCS, CCS), and specialty pharmacy (GLP-1) trends
- When asked for a "morning briefing" or "what needs attention," prioritize: (1) LOBs with MLR > 1.0, (2) quality measures below 4-star cutpoint, (3) states with highest avoidable spend

### Benchmark Prompts (4 Demo Beats)

**Beat 1 — Morning Briefing:**
```
Give me a quick executive briefing on our financial performance — MLR by line of business, any lines where paid claims PMPM exceeds premium PMPM, and which states have the highest avoidable spend.
```
Expected: Medicaid MLR 106%, MA 100.3%, FL/TX/CA avoidable ED flagged.

**Beat 2a — Actuary Persona:**
```
Show me risk score trends by LOB over the last 12 months. Where are risk scores rising faster than premium PMPM?
```
Expected: MA risk scores trending up, premium flat.

**Beat 2b — Quality Director Persona:**
```
Which HEDIS measures are currently below 4-star cutpoints? What's the estimated financial exposure?
```
Expected: BCS at 72% (cutpoint 74%), HbA1c at 58% (cutpoint 60%).

**Beat 2c — Care Manager Persona:**
```
Show me the top 10 highest-risk members with the most open care gaps. What interventions are recommended?
```
Expected: 10 members with risk_score > 3.0 and open_gaps_count > 8.

**Beat 3 — CFO Meeting Prep:**
```
I have a meeting with Dr. Sarah Chen from AHP this Saturday. Tell me about AHP's value-based care performance — shared savings, quality scores, and any cost trends I should be aware of.
```
Expected: AHP shared savings $2.1M YTD, quality 4.2 stars, TCOC PMPM up 3% QoQ from GLP-1.

## AI/BI Dashboard Design

### Dashboard Name
**Healthcare Finance Executive View**

### Pages (3)
1. **Financial Overview** — MLR by LOB (bar), PMPM trend (line), budget variance (waterfall), avoidable spend by state (choropleth or bar)
2. **Quality & Gaps** — Measure performance vs star cutpoints (bar), gap closure trend (line), top measures at risk (table)
3. **VBC Performance** — Shared savings by ACO (bar), TCOC PMPM trend (line), quality score by ACO (table)

### Data Sources
All 3 metric views + dim_budget for variance calculations.

## Deployment
```bash
# After Bundle 1 is deployed:
cd webinar-demo-aibi
databricks bundle deploy --target dev
```

## Open Questions
- [ ] Confirm Genie Agent Mode is enabled on FEVM workspace
- [ ] Decide whether dashboard is needed for the webinar or if Genie-only is sufficient
- [ ] Test MCP calendar tool availability in Genie One on FEVM
