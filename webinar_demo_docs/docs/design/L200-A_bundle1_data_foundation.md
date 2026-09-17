# L200-A — Bundle 1: Data Foundation (`webinar-demo-data`)

## Overview
This bundle deploys the governed data layer: 8 Delta tables, 3 metric views, and UC Glossary Pages into `home_matthew_giglia.webinar_demo`. It is the foundation that Bundle 2 (AI/BI Experience) depends on.

## Dependencies
- **Catalog:** `home_matthew_giglia` (must exist; FEVM home catalog)
- **Schema:** `webinar_demo` (created by this bundle)
- **Compute:** Serverless SQL Warehouse (for metric view creation)

## Bundle Structure
```
webinar-demo-data/
├── databricks.yml
├── resources/
│   ├── schema.yml              # CREATE SCHEMA
│   ├── tables/
│   │   ├── gold_financial_monthly.sql
│   │   ├── dim_budget.sql
│   │   ├── dim_member.sql
│   │   ├── gold_quality_measures.sql
│   │   ├── gold_utilization_monthly.sql
│   │   ├── fact_vbc_performance.sql
│   │   ├── dim_aco_contract.sql
│   │   └── dim_provider_network.sql
│   ├── metric_views/
│   │   ├── mv_financial.sql
│   │   ├── mv_quality.sql
│   │   └── mv_vbc_performance.sql
│   └── glossary/
│       └── healthcare_finance_glossary.yml
├── data/
│   ├── seed_financial.sql       # INSERT statements with planted narrative
│   ├── seed_budget.sql
│   ├── seed_members.sql
│   ├── seed_quality.sql
│   ├── seed_utilization.sql
│   ├── seed_vbc.sql
│   ├── seed_aco_contracts.sql
│   └── seed_providers.sql
└── tests/
    └── validate_narrative.sql   # Assertions that planted story holds
```

## Design

### Table Creation Order
Tables have no foreign key constraints (synthetic data), but logical order matters for readability:

1. `dim_aco_contract` — reference data (5 ACOs including AHP)
2. `dim_member` — 50K synthetic members
3. `dim_budget` — budget targets by LOB/month
4. `dim_provider_network` — 200 providers across 5 ACOs
5. `gold_financial_monthly` — financial aggregates (the core Beat 1 table)
6. `gold_quality_measures` — HEDIS measures (Beat 2)
7. `gold_utilization_monthly` — utilization aggregates (Beat 2)
8. `fact_vbc_performance` — VBC contract performance (Beat 3)

### Metric View Creation Order
Metric views depend on their source tables:

1. `mv_financial` ← `gold_financial_monthly`
2. `mv_quality` ← `gold_quality_measures`
3. `mv_vbc_performance` ← `fact_vbc_performance` JOIN `dim_aco_contract`

### Synthetic Data Generation Strategy
- **Deterministic seeding:** Use `EXPLODE(SEQUENCE(...))` and modular arithmetic to generate rows without randomness — ensures reproducibility
- **Planted narrative:** Financial numbers are hand-tuned to tell the demo story (Medicaid underwater, MA borderline, etc.)
- **Realistic distributions:** Member demographics follow US health plan distributions (age bands, gender, state)
- **AHP realism:** Use real entity names, real quality measures, real gainsharing structure per L100 AHP Realism Rules

### Column Comments (Mandatory)
Every column must have a COMMENT that Genie can use for context. Format:
```sql
`mlr` DECIMAL(10,6) COMMENT 'Medical Loss Ratio = paid claims / earned premium. Lower is better for the payer. Values above 1.0 indicate claims exceed premium.'
```

### Table Comments (Mandatory)
Every table must include:
```sql
COMMENT ON TABLE `home_matthew_giglia`.`webinar_demo`.`gold_financial_monthly`
IS 'Monthly financial performance aggregates by line of business, state, and plan type. Synthetic demo data for Healthcare Finance Webinar (Sep 2026). Query mv_financial metric view for governed KPIs.';
```

## NFRs
- All tables must be queryable within 5 seconds on serverless SQL warehouse
- Metric views must support `MEASURE()` syntax and `GROUP BY ALL`
- No JOINs inside metric view definitions (Spark limitation — use base table JOINs in seed SQL)
- Total data volume < 10 MB (synthetic, not production scale)

## Testing
`tests/validate_narrative.sql` contains assertions:
```sql
-- Beat 1: Medicaid MLR must be > 1.0
SELECT MEASURE(mlr) FROM mv_financial WHERE lob = 'Medicaid' AND year_month = '2026-05-01'
HAVING MEASURE(mlr) > 1.0;

-- Beat 1: Commercial MLR must be < 0.90
SELECT MEASURE(mlr) FROM mv_financial WHERE lob = 'Commercial' AND year_month = '2026-05-01'
HAVING MEASURE(mlr) < 0.90;

-- Beat 3: AHP must exist in dim_aco_contract
SELECT * FROM dim_aco_contract WHERE aco_name LIKE '%Accountable Health Partners%';
```

## Deployment
```bash
cd webinar-demo-data
databricks bundle deploy --target dev
databricks bundle run seed_all --target dev
```

## Open Questions
- [ ] Confirm `home_matthew_giglia` catalog exists and has CREATE SCHEMA permission
- [ ] Confirm serverless SQL warehouse is available for metric view creation
- [ ] Decide whether to use `ai_query` for synthetic member name generation or deterministic names
