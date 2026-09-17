# fhcf-demo

Declarative Automation Bundle for the **Databricks HLS Quarterly Webinar** (September 17, 2026).  
Demonstrates Genie Agent over synthetic healthcare finance data — MLR trending, HEDIS quality measures, VBC performance, and avoidable spend analytics.

## Quick Start

1. **Deploy** -- Click the deployment rocket in the left sidebar, then click **Deploy** (or `databricks bundle deploy --target dev`).
2. **Seed data** -- Run the `[FHCF] Seed Healthcare Finance Data` job from the Deployments panel (or `databricks bundle run seed_data --target dev`).
3. **Verify** -- Open `src/seed_all_data` and run the final validation cell to confirm the planted narrative holds.

## What Gets Created

| Resource | Name | Description |
| --- | --- | --- |
| UC Schema | `hls_fde.healthcare_finance` | All tables and views land here (dev mode prefixes with `dev_<user>_`) |
| Job | `[FHCF] Seed Healthcare Finance Data` | Runs `seed_all_data` notebook to create and populate all objects |

### Data Objects (created by the seed job)

**8 Delta Tables:**  
`dim_aco_contract`, `dim_budget`, `dim_member`, `dim_provider_network`, `gold_financial_monthly`, `gold_quality_measures`, `gold_utilization_monthly`, `fact_vbc_performance`

**3 Metric Views:**  
`mv_financial`, `mv_quality`, `mv_vbc_performance`

## Bundle Structure

```
fhcf-demo/
  databricks.yml              # Bundle config (variables: catalog, schema)
  resources/
    healthcare_finance.schema.yml   # UC schema resource
    seed_data.job.yml               # Seed job definition
  src/
    seed_all_data.py          # 23-cell notebook: widgets > DDL > seed data > metric views > validation
  fixtures/
    sessions/                 # Session summaries
```

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `catalog` | `hls_fde` | Unity Catalog catalog |
| `schema` | `healthcare_finance` | Schema name (dev mode prefixes automatically) |

## Targets

| Target | Mode | Default |
| --- | --- | --- |
| `dev` | development | Yes |
| `prod` | production | No |

Both targets deploy to `fevm-hls-fde.cloud.databricks.com`.

## Demo Beats

1. **CFO morning briefing** -- MLR by LOB, avoidable spend hotspots
2. **Persona rotation** -- Actuary, quality officer, care manager
3. **AHP meeting prep** -- Dr. Sarah Chen (ACO-001), shared savings, TCOC, pharmacy trends
4. **Reveal** -- Platform capabilities

## Planted Narrative

The seed data encodes a deterministic narrative verified by the validation cell:

- Medicaid MLR ~106%, MA ~100%, Commercial ~87%, Individual ~83%
- FL, TX, CA: 2x avoidable ED rate
- BCS at 72% (4-star cutpoint 74%), HbA1c at 58% (cutpoint 60%)
- AHP shared savings $2.1M YTD vs $1.8M target

## Documentation

- [Declarative Automation Bundles in the workspace](https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-bundles)
- [Declarative Automation Bundles Configuration reference](https://docs.databricks.com/aws/en/dev-tools/bundles/reference)
- Design docs: `webinar_demo_docs/docs/design/` (L100-L300 at repo root)
