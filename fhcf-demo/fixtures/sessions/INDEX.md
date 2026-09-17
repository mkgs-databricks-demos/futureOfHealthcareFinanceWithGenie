# Session Index -- fhcf-demo

| Date | Session | Summary |
| --- | --- | --- |
| 2026-09-17 | [Genie Space & Catalog Migration](2026-09-17_genie-space-and-catalog-migration.md) | Built Genie Agent resource, migrated dev catalog to hls_fde_dev, fixed API format issues, two-phase deploy. 14 data sources, 7 sample questions, consolidated instructions. |
| 2026-09-17 | [DDL & Metric View Improvements](2026-09-17_ddl-metric-view-improvements.md) | Reviewed schema quality; added PK/FK constraints, liquid clustering, member_months to utilization DDL; enriched 3 metric views with format/display_name/synonyms; fixed mv_vbc aggregation with filtered measures + ACO join; added 3 new metric views (mv_utilization, mv_budget_variance, mv_member_risk). Notebook pending Run All. |
| 2026-09-17 | [Initial Bundle Setup](2026-09-17_initial-bundle-setup.md) | Stood up fhcf-demo bundle: 8 tables, 3 metric views, seed job. Fixed IDENTIFIER() syntax and metric view YAML version. First deploy succeeded; seed job pending rerun after metric view fix. |
