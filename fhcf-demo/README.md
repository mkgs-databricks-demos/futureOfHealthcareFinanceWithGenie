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
| UC Schema | `hls_fde.healthcare_finance` | All tables and views land here (dev: `hls_fde_dev`, prefixed) |
| Job | `[FHCF] Seed Healthcare Finance Data` | Runs `seed_all_data` notebook to create and populate all objects |
| Genie Space | Healthcare Finance Intelligence | 14 data sources, 7 sample questions, lean instructions backed by metric view semantic metadata |

### Data Objects (created by the seed job)

**8 Delta Tables:**  
`dim_aco_contract`, `dim_budget`, `dim_member`, `dim_provider_network`, `gold_financial_monthly`, `gold_quality_measures`, `gold_utilization_monthly`, `fact_vbc_performance`

**6 Metric Views:**  
`mv_financial`, `mv_quality`, `mv_vbc_performance`, `mv_utilization`, `mv_budget_variance`, `mv_member_risk`

All metric views carry full semantic metadata — `display_name`, `synonyms`, `format`, and detailed `comment` on every column, plus COMMENT ON VIEW with authoritative-source guidance. The Genie instruction is intentionally lean: it contains only behavioral routing rules, MEASURE() syntax examples, and synthesis directives. Domain definitions (MLR, PMPM, TCOC, HEDIS measure-to-domain mappings, AHP synonyms) live in the metric view metadata, not the instruction text.

## Bundle Structure

```
fhcf-demo/
  databricks.yml              # Bundle config (variables: catalog, schema)
  resources/
    healthcare_finance.schema.yml                  # UC schema resource
    seed_data.job.yml                              # Seed job definition
    healthcare_finance_intelligence.genie_space.yml # Genie Agent resource
  src/
    seed_all_data.py                    # 26-cell notebook: widgets > DDL > seed data > metric views > validation
  fixtures/
    sessions/                           # Session summaries
```

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `catalog` | `hls_fde` | Unity Catalog catalog (dev override: `hls_fde_dev`) |
| `schema` | `healthcare_finance` | Schema name (dev mode prefixes automatically) |
| `warehouse_id` | lookup: `demo-warehouse` | SQL warehouse for Genie space |

## Targets

| Target | Mode | Default |
| --- | --- | --- |
| `dev` | development | Yes |
| `prod` | production | No |

Both targets deploy to `fevm-hls-fde.cloud.databricks.com`.

**Deployment ordering:** Seed job must run before Genie space deploy (API validates table existence). First deploy creates schema + job; run the seed job; then redeploy to create/update the Genie space. Table identifiers in the Genie space use `${resources.schemas.*}` refs that resolve per-target at deploy time.

## Demo Beats (7/7 passing)

| Beat | Prompt | Metric Views |
| --- | --- | --- |
| 1a | Morning briefing — flag off-track items | mv_budget_variance, mv_quality, mv_utilization |
| 1b | HEDIS measures below 4-star cutpoints | mv_quality (routes via governed view — not raw table) |
| 2a | Top 10 highest-risk members | dim_member |
| 2b | High-risk members in high avoidable ED states | dim_member, mv_utilization |
| 3a | Calendar (MCP connector) | External |
| 3b | AHP value-based care overview | mv_vbc_performance |
| 3c | TCOC drill-down — pharmacy driver | mv_vbc_performance |
| 3d | Dr. Chen meeting brief | mv_vbc_performance, mv_quality |

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
