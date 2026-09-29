# Session: CMO Dashboard & Managed Warehouse Resource

**Date:** 2026-09-29  
**Branch:** mg-genie-cmo-dashboard (from mg-genie-cfo-dashboard)  
**Bundle:** fhcf-demo  
**Thread:** Add Health Plan CMO Dashboard to Bundle

---

## Summary

Added the Health Plan CMO Performance Dashboard (12 pages, 9 datasets, 271K chars) as a serialized bundle resource. Introduced a bundle-managed SQL warehouse resource, eliminating the `warehouse_id` lookup variable. Migrated all resource YAML files from `${var.*}` to `${resources.*}` syntax for warehouse, catalog, and schema references — ensuring proper dependency ordering with no chicken-and-egg deployment issues.

## Changes

### New Files

| File | Description |
| --- | --- |
| `src/dashboards/health_plan_cmo_performance.lvdash.json` | Serialized dashboard (271K, 12 pages, 9 datasets). Sources: mv_member_risk, mv_quality, mv_financial, mv_utilization, mv_budget_variance, mv_vbc_performance, dim_member, gold_financial_monthly, dim_provider_network. |
| `resources/health_plan_cmo_performance.dashboard.yml` | Dashboard resource YAML with `${resources.schemas.healthcare_finance.*}` and `${resources.sql_warehouses.demo_warehouse.id}` refs. |
| `resources/demo_warehouse.sql_warehouse.yml` | New SQL warehouse resource: 2X-Small serverless PRO, auto-stop 10 min, 1 cluster. Named `[FHCF] Healthcare Finance Warehouse`. |

### Modified Files

| File | Change |
| --- | --- |
| `databricks.yml` | Removed `warehouse_id` lookup variable — warehouse now managed as a resource. |
| `resources/cfo_executive_dashboard.dashboard.yml` | Migrated `warehouse_id`, `dataset_catalog`, `dataset_schema` from `${var.*}` to `${resources.*}` refs. |
| `resources/healthcare_finance_intelligence.genie_space.yml` | Migrated `warehouse_id` from `${var.warehouse_id}` to `${resources.sql_warehouses.demo_warehouse.id}`. |

### No Changes

| File | Reason |
| --- | --- |
| `resources/seed_data.job.yml` | Already used `${resources.schemas.healthcare_finance.*}` — no warehouse ref needed. |
| `resources/healthcare_finance.schema.yml` | Schema resource is the source of `${var.catalog}` / `${var.schema}` — correctly uses variables. |

## Decisions

1. **Bundle-managed warehouse over lookup variable.** The `warehouse_id: lookup: demo-warehouse` pattern required the warehouse to pre-exist. A managed resource ensures the warehouse is created by the bundle and dependency ordering is automatic.

2. **All resource YAMLs use `${resources.*}` syntax.** Following the project convention (already used by seed_data.job.yml and Genie space table identifiers). The schema resource itself is the only place that uses `${var.catalog}` / `${var.schema}` — everything else references the schema resource.

3. **Dashboard content unchanged.** The CMO dashboard was serialized as-is from workspace. All KPI widgets reference metric views via `MEASURE()` — already aligned with Genie Agent conventions.

## Verification

### Bundle Validation
- `bundle validate --target dev` — OK
- `bundle validate --target prod` — OK

### Dev Deployment
- Deploy: 3 created (warehouse, 2 dashboards), 2 changed (job, Genie space), 2 unchanged (schemas)
- Seed job run ID: 947527817242476 — SUCCESS (86s)
- All 8 tables populated, all 6 metric views returning data
- Redeploy: 0 changed, 7 unchanged — all resources stable

### Data Consistency (Genie Agent vs CMO Dashboard)

| Domain | Match | Notes |
| --- | --- | --- |
| Financial (MLR by LOB) | Exact | Both paths: Medicaid 108.1%, MA 100.8%, Commercial 86.5%, Individual 82.1% |
| VBC (AHP actuals/targets) | Exact | Shared Savings $2.1M, TCOC $892, Pharmacy $198 |
| Utilization (IP/ED per 1K) | Exact | All 4 LOBs match to 1 decimal |
| Budget Variance (MLR vs target) | Exact | All 4 LOBs match |
| Member Risk (high_risk_pct) | Exact | Dashboard uses MEASURE(mv_member_risk.high_risk_pct) directly |
| Quality (distance_to_4_star) | Exact | Dashboard uses MEASURE(Quality__Stars.distance_to_4_star) directly |

All dashboard KPI widgets delegate to metric view MEASURE() — no custom SQL divergence.

### Dev Resource IDs

| Resource | ID |
| --- | --- |
| SQL Warehouse | 1be43d05d0d903f4 |
| CMO Dashboard | 01f1bbc0377d184aaab81612a310442a |
| CFO Dashboard | 01f1bbc037791ae5bb101a4d4ce318d9 |
| Seed Job Run | 947527817242476 |

## Git

**Commit 1:** `feat: add Health Plan CMO Performance Dashboard as serialized bundle resource`  
**Commit 2:** `feat: add managed SQL warehouse resource; migrate all refs to ${resources.*} syntax`  
**Branch:** mg-genie-cmo-dashboard — ready for PR to main.
