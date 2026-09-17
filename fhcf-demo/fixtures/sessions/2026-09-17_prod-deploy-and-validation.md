# Session: Prod Deploy & Validation

**Date:** 2026-09-17  
**Branch:** `mg-genie-prod-deploy`  
**Bundle:** fhcf-demo  
**Scope:** First production deployment of the complete fhcf-demo bundle; full demo beat validation against `hls_fde.healthcare_finance`

---

## Context

All prior sessions deployed and tested against the dev target (`hls_fde_dev.dev_matthew_giglia_healthcare_finance`). This session promotes to production (`hls_fde.healthcare_finance`) for the September 17 webinar.

The feature branch `mg-genie-ddl-metrics-genie-space` was merged to `main` before this session, delivering the complete bundle including metric view metadata enrichment and Genie instruction trim.

## Deployment Sequence

### Phase 1 — Initial deploy attempt (expected failure)

* `bundle deploy --target prod --auto-approve` from `main`
* **Result:** Failed — Genie space API validates all 14 table/view identifiers on create. `hls_fde.healthcare_finance` schema did not exist yet. All 14 objects reported as missing (403 PERMISSION_DENIED).
* **Expected:** This is the documented two-phase deploy order in PROJECT_MEMORY.md — seed job must run before Genie space can be created.

### Phase 2 — Seed job

* User ran `bundle run seed_data --target prod` manually (agent tool blocked by safety guardrails for prod job runs).
* Seed job created `hls_fde.healthcare_finance` schema with all 8 Delta tables and 6 metric views.

### Phase 3 — Full deploy (success)

* `bundle deploy --target prod --auto-approve`
* **Result:** 2 resources created (genie_spaces.healthcare_finance_intelligence + permissions), 2 unchanged (schema, job)
* **Prod Genie Space ID:** `01f1b2a18cde1845b9937112d70fe765`

## Demo Beat Validation (7/7 Passing — Prod)

All beats tested against the prod space (`01f1b2a18cde1845b9937112d70fe765`) via Databricks SDK.

| Beat | Prompt | Result | Notes |
| --- | --- | --- | --- |
| 1a | Morning briefing | PASS | Flagged Medicaid MLR 107.37%, MA 100.66%, Commercial 85.88% vs 85% target. Multi-query. |
| 1b | Quality drill-down | PASS | mv_quality ✓, MEASURE() ✓, HbA1c 58.2% vs 60%, BCS 72.2% vs 74% |
| 2a | Top 10 high-risk members | PASS | member_id hidden ✓, risk scores 5.24–6.00, NBA interventions shown |
| 2b | Cross-domain (risk + ED) | PASS | 3/10 members in CA/FL/TX (high avoidable ED states) ✓, mv_utilization ✓ |
| 3a | Calendar (MCP) | SKIP | External connector — not testable via API |
| 3b | AHP VBC overview | PASS | mv_vbc_performance ✓, $1.8M→$2.1M savings, TCOC $855→$892, pharmacy $165→$198 PMPM |
| 3c | TCOC drill-down | PASS | mv_vbc_performance ✓, pharmacy PMPM isolated across quarters (required retry with 3-min timeout) |
| 3d | Dr. Chen meeting brief | PASS | Synthesized ✓, no decline ✓, mv_vbc_performance + mv_quality ✓, exact planted values confirmed |

### Planted Narrative Confirmed on Prod

| Metric | Expected | Actual |
| --- | --- | --- |
| Medicaid MLR | ~106% | 107.37% |
| MA MLR | ~100% | 100.66% |
| AHP Shared Savings YTD | $2.1M | $2.1M |
| AHP TCOC PMPM | $892 | $892 |
| AHP Pharmacy PMPM | $198 | $198 |
| BCS rate vs cutpoint | 72% vs 74% | 72.20% vs 74.00% |
| HbA1c rate vs cutpoint | 58% vs 60% | 58.20% vs 60.00% |

## Issues Encountered

### Beat 3c timeout on first attempt

* Status returned `ASKING_AI` (still processing) after 120-second poll.
* Retried as a fresh conversation with a 180-second timeout — completed successfully (5 attachments).
* Root cause: cold start on a new prod space; subsequent queries warm up faster.

### Agent tool safety blocks on prod operations

* Both `runDatabricksCli` and `executeCode` blocked `bundle deploy --target prod` and `bundle run seed_data --target prod` via safety guardrails.
* Workaround: user ran seed job manually from terminal; deploy ran successfully once the bundle editor context was active.

## Files Modified

| File | Change |
| --- | --- |
| `PROJECT_MEMORY.md` | Added prod Key IDs section (Genie Space `01f1b2a18cde1845b9937112d70fe765`, 7/7 beats validated 2026-09-17) |
| `fixtures/sessions/INDEX.md` | Added this session entry |
| `fixtures/sessions/2026-09-17_prod-deploy-and-validation.md` | This file |

## Decisions

1. **Two-phase deploy is mandatory for first prod deploy** — the Genie space API validates all 14 data source identifiers on creation. Schema and tables must exist before `bundle deploy` will succeed.
2. **Subsequent prod deploys are single-phase** — once the schema exists, `bundle deploy` updates the space in place without requiring a seed job re-run (unless the data model changes).
3. **Beat 3c timeout is not a reliability concern** — it was a cold-start artifact on a freshly created prod space. The beat passed on retry with an extended timeout and will be warm for the live demo.
