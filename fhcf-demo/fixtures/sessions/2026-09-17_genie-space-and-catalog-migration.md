# Session: Genie Space Build & Catalog Migration

**Date:** 2026-09-17  
**Branch:** `mg-genie-ddl-metrics-genie-space`  
**Bundle:** `fhcf-demo`  
**Target:** dev

---

## Summary

Built the Healthcare Finance Intelligence Genie Agent as a DABs resource, migrated the dev catalog from `hls_fde` to `hls_fde_dev`, and integrated 3 new metric views from a parallel session into the Genie space instructions.

## Problems & Root Causes

### 1. Genie API: Unknown field 'instruction'

**Problem:** `bundle deploy` failed with `Invalid serialized_space: Unknown field 'instruction'`.  
**Root cause:** The Genie Spaces API expects `content` (array of strings) not `instruction` (string) inside `text_instructions` objects.  
**Fix:** Changed field from `instruction` to `content` and wrapped value in an array.

### 2. Genie API: At most 1 text instruction

**Problem:** Original design had 4 separate text_instruction entries (glossary, rules, syntax, domains).  
**Root cause:** API limit: at most 1 text instruction per agent.  
**Fix:** Consolidated all 4 sections into a single `content` array within 1 text_instruction entry.

### 3. Genie API: Tables must be sorted

**Problem:** Unsorted collections cause validation errors.  
**Root cause:** API requires alphabetical sorting by `identifier` for tables, by `id` for sample_questions and text_instructions.  
**Fix:** Sorted all arrays alphabetically by the required key.

### 4. Genie space deployment ordering

**Problem:** First deploy attempt failed because Genie API validates that all referenced tables exist at creation time.  
**Root cause:** Schema + job deploy before seed job runs, so tables don't exist when Genie space creation fires.  
**Fix:** Two-phase deploy: (1) deploy schema + job, (2) run seed job, (3) deploy again to create Genie space.

### 5. databricks.yml catalog typo

**Problem:** Dev target had `catalog: hls_fde_de` (missing trailing `v`).  
**Root cause:** Manual edit in another session.  
**Fix:** Corrected to `hls_fde_dev`.

## Key Decisions

1. **Dev catalog: `hls_fde_dev`** -- Changed from `hls_fde`. Per-target variable override in databricks.yml. Prod keeps `hls_fde` as default.
2. **Geniespace table identifiers hardcoded per target** -- JSON file has `hls_fde_dev.dev_matthew_giglia_healthcare_finance.X` (dev). For prod, update to `hls_fde.healthcare_finance.X`. Future: refactor to `serialized_space` in YAML with `${resources.schemas.*}` refs.
3. **warehouse_id: demo-warehouse** -- Via lookup variable.
4. **CAN_RUN for all users** -- Genie space accessible to all workspace users.
5. **Two-phase deploy required** -- Seed job must run before Genie space creation.

## Changes Made

### Files Created

| File | Description |
| --- | --- |
| `src/healthcare_finance_intelligence.json` | Genie space definition (14 tables, 7 sample questions, 1 consolidated instruction) |
| `resources/healthcare_finance_intelligence.genie_space.yml` | DABs resource YAML for the Genie space |

### Files Modified

| File | Change |
| --- | --- |
| `databricks.yml` | Added `warehouse_id` lookup variable (demo-warehouse); added `variables: catalog: hls_fde_dev` under dev target |

### Incorporated from Parallel Session

3 new metric views created in the parallel DDL session were integrated into the Genie space:
- `mv_utilization` (per-1K utilization rates)
- `mv_budget_variance` (actual vs target MLR)
- `mv_member_risk` (risk stratification)

All 6 metric views are now covered in the Genie instructions with MEASURE() syntax examples.

## Deployment Status

- Schema `hls_fde_dev.dev_matthew_giglia_healthcare_finance`: Created (old `hls_fde` schema auto-dropped by DABs)
- Job 749445244992722: Updated, seed run 590205922781856 succeeded
- Genie Space `01f1b284db9618cc902e5cf68a43153c`: Created with 14 data sources, 7 sample questions
- All 8 tables seeded, all 6 metric views created

## Outstanding Work

1. Verify planted narrative with validation cell
2. Test each demo beat prompt in the Genie space
3. For prod: update geniespace.json identifiers to hls_fde.healthcare_finance (or refactor to serialized_space)
4. Git commit and push
