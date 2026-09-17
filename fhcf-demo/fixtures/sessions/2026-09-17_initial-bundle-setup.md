# Session: Initial Bundle Setup & Data Foundation

**Date:** 2026-09-17  
**Branch:** `mg-init`  
**Bundle:** `fhcf-demo`  
**Target:** dev (default)

---

## Summary

Stood up the complete `fhcf-demo` Declarative Automation Bundle from scratch, consolidating the original two-bundle design (L100 doc) into a single bundle for webinar time efficiency. Created 8 Delta tables, 3 metric views, and a seed job with deterministic synthetic data encoding a planted narrative for 4 demo beats.

## Problems & Root Causes

### 1. USE CATALOG/SCHEMA with widget substitution

**Problem:** Original DDL used backtick interpolation which is unsafe and doesn't handle widget values properly.  
**Root cause:** Backtick syntax treats the value as raw text substitution, not as a proper identifier.  
**Fix:** Changed to `USE CATALOG IDENTIFIER('${catalog}')` / `USE SCHEMA IDENTIFIER('${schema}')` per Databricks SQL docs.

### 2. Metric view Invalid YAML version null

**Problem:** Job run 669021950781837 failed with `METRIC_VIEW_INVALID_VIEW_DEFINITION ... Invalid YAML version: null`.  
**Root cause:** `CREATE VIEW WITH METRICS LANGUAGE YAML` requires a `version:` field as the first entry in the YAML body. The initial implementation started directly with `source:`.  
**Fix:** Added `version: 1.1` as the first line of each metric view YAML body (mv_financial, mv_quality, mv_vbc_performance).

## Key Decisions

1. **Single bundle** -- Consolidated fhcf-data and fhcf-ai (from L100 design) into one fhcf-demo bundle. Saves deploy cycles for a webinar demo.
2. **Catalog: hls_fde** -- Changed from home_matthew_giglia (design docs) per user requirement.
3. **Schema: healthcare_finance** -- Dev mode auto-prefixes as dev_matthew_giglia_healthcare_finance.
4. **USE + bare names** -- Notebook sets context with USE CATALOG/SCHEMA then uses bare table names in DDL/DML. Metric view source fields use ${catalog}.${schema}.table (widget substitution) since stored metadata needs full qualification.
5. **Job parameters via schema resource refs** -- ${resources.schemas.healthcare_finance.catalog_name} and .name ensure dependency ordering.
6. **Notebook stored as .py** -- Python default language with %sql magic for SQL cells.
7. **Metric view YAML version 1.1** -- Required by the metric view engine.

## Changes Made

### Files Created

| File | Description |
| --- | --- |
| databricks.yml | Bundle config with catalog/schema variables, dev (default) and prod targets |
| resources/healthcare_finance.schema.yml | UC schema resource definition |
| resources/seed_data.job.yml | Seed job definition, passes catalog/schema via base_parameters |
| src/seed_all_data.py | 23-cell notebook: widgets, DDL (8 tables), INSERT (8 tables), metric views (3), validation |

### Files Modified

| File | Change |
| --- | --- |
| databricks.yml | Added variables block (catalog, schema) |
| src/seed_all_data.py cell 3 | USE CATALOG/SCHEMA changed from backtick to IDENTIFIER() syntax |
| src/seed_all_data.py cells 20-22 | Added version: 1.1 to metric view YAML bodies |

## Deployment Status

- bundle deploy --target dev: Succeeded. Schema dev_matthew_giglia_healthcare_finance created in hls_fde.
- Job registered: [dev matthew_giglia] [FHCF] Seed Healthcare Finance Data (ID: 749445244992722)
- First job run: Failed (metric view version error). Fix applied but not yet redeployed/rerun.

## Outstanding Work

1. Redeploy bundle and rerun seed job to validate metric view fix
2. Verify planted narrative holds (validation cell 23)
3. Create Genie Agent space Healthcare Finance Intelligence (11 tables/views, instructions from L300-C)
4. Commit and push to mg-init branch
