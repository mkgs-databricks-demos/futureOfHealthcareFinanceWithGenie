# Session: Genie Space Testing & Instruction Tuning

**Date:** 2026-09-17  
**Branch:** `mg-genie-ddl-metrics-genie-space`  
**Bundle:** fhcf-demo  
**Scope:** End-to-end Genie space validation, instruction tuning, cleanup

---

## Problems Addressed

1. **Genie space untested** — the Healthcare Finance Intelligence space had been deployed but never validated against the 8 demo beat prompts.
2. **Beat 3d failure** — the Dr. Chen meeting brief prompt returned a factual disclaimer ("this database cannot provide meeting agendas") instead of synthesizing a brief from live data. Root cause: Rule 9 was passive ("note that...") and didn't direct the agent to synthesize.
3. **Orphaned JSON file** — `src/healthcare_finance_intelligence.json` was no longer referenced after the YAML was refactored to use inline `serialized_space`, but the file still existed in the repo.

## Root Causes

* **Beat 3d:** The instruction said "note that the Executive Medical Director is Dr. Sarah Chen and the key discussion topics are..." — this is informational, not directive. Genie agents are conservative about generating narrative content unless explicitly instructed to do so.
* **Orphaned file:** The refactoring from `file_path` to inline `serialized_space` removed the reference but didn't delete the source file.

## Changes Made

### 1. Seed Job Rerun
* Ran `bundle run seed_data --target dev` — job 749445244992722, run 686881950106253
* All 8 tables reseeded + 6 metric views recreated in `hls_fde_dev.dev_matthew_giglia_healthcare_finance`
* Confirmed 14 objects: 8 MANAGED tables + 6 METRIC_VIEWs

### 2. Bundle Deploy
* `bundle deploy --target dev --auto-approve` — 4 resources unchanged (schema, job, genie space, permissions all in sync)

### 3. Demo Beat Prompt Testing (7/7)

| Beat | Prompt | Result | Notes |
| --- | --- | --- | --- |
| 1a | Morning briefing | PASS | Flagged Medicaid MLR 107.37%, MA 100.66%. Used mv_budget_variance. |
| 1b | Quality drill-down | PASS | Found measures below 4-star cutpoints. Used MEASURE() syntax. |
| 2a | Top 10 high-risk members | PASS | Risk scores, gaps, NBA recommendations. Correctly hid member_id. |
| 2b | Cross-domain (risk + ED) | PASS | FL/TX/CA avoidable ED rates ~0.35. Pattern detected. |
| 3a | Calendar (MCP) | SKIP | External connector — not testable via API. |
| 3b | AHP overview | PASS | Shared savings $2.10M, quality 4.20, TCOC $892 PMPM. |
| 3c | TCOC drill-down | PASS | Pharmacy $165→$198, share 19.3%→22.2%. Correctly identified driver. |
| 3d | Meeting brief (pre-fix) | FAIL | Returned factual disclaimer instead of synthesizing brief. |
| 3d | Meeting brief (post-fix) | PASS | Structured brief with numbered talking points, queried both mv_vbc_performance and mv_quality. |

### 4. Planted Narrative Verification

All planted values confirmed from Genie responses:
* Medicaid MLR: 107.37% (expected ~106%)
* MA MLR: 100.66% (expected ~100.3%)
* FL/TX/CA avoidable ED rate: ~0.35 (expected 2× others)
* AHP shared savings: $2.10M YTD (expected $2.1M)
* AHP TCOC: $892 PMPM (expected $892)
* AHP Pharmacy: $198 PMPM (expected $198)
* AHP Quality score: 4.20 (trend improving)

### 5. Instruction Strengthening (Rule 9)

**Before:**
> When asked about a "meeting" or "calendar" related to AHP, note that the Executive Medical Director is Dr. Sarah Chen and the key discussion topics are: shared savings performance, quality measures (HbA1c, BCS, CCS), and specialty pharmacy trends (GLP-1 utilization).

**After:**
> When asked to prepare a "brief," "talking points," or anything related to a "meeting" with Dr. Chen or AHP leadership, SYNTHESIZE a structured meeting brief using live data. Query mv_vbc_performance for shared savings YTD, TCOC trend, and pharmacy PMPM; query mv_quality for HbA1c (CDC-HBA1C) and BCS rates vs 4-star cutpoints. Present the response as numbered talking points: (1) Shared savings YTD vs benchmark, (2) Quality measures at risk — HbA1c and BCS gap to 4-star, (3) Pharmacy/GLP-1 cost pressure on TCOC, (4) Recommended asks or discussion items. The Executive Medical Director is Dr. Sarah Chen (ACO-001, Accountable Health Partners, Finger Lakes / Upstate NY). Do NOT decline to generate a brief — the metric views contain all the data needed.

### 6. Orphaned File Cleanup
* Deleted `src/healthcare_finance_intelligence.json` (was ID 2824221228946158)
* YAML inline `serialized_space` is now the single source of truth

## Files Modified

| File | Change |
| --- | --- |
| `resources/healthcare_finance_intelligence.genie_space.yml` | Strengthened rule 9 for Beat 3d |
| `src/healthcare_finance_intelligence.json` | DELETED (orphaned) |

## Decisions

* **Inline `serialized_space` over `file_path`:** The YAML was refactored (prior session) to embed JSON directly with `${resources.schemas.*}` refs. This resolves correctly per-target at deploy time and eliminates the need for a separate JSON file.
* **Directive vs. informational instructions:** Genie agents require explicit directives ("SYNTHESIZE," "Do NOT decline") rather than passive context ("note that...") for narrative generation tasks.
* **Beat 1b cosmetic note:** The agent queried `gold_quality_measures` directly instead of `mv_quality` — functionally equivalent but doesn't leverage the governed metric view. Acceptable for demo; could strengthen rule 1 further if needed.

## Commits

1. `feat(fhcf-demo): Genie Agent resource, catalog migration, DDL improvements` — 22 files
2. `fix(genie-space): strengthen Beat 3d instruction, remove orphaned JSON` — 12 files
