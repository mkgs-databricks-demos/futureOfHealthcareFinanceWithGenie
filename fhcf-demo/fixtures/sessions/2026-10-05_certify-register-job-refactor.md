# 2026-10-05 — Certify & Register Job Refactor

## Summary

Refactored the certify_register job from a single-task notebook-driven approach to a
condition_task DAG with separate certify and register tasks. Discovered and integrated
the Entity Tag Assignments API for programmatic dashboard/Genie certification.

## Problems & Root Causes

1. **certify_assets was a notebook widget** — no way to skip certification at the job
   level without running the notebook. Needed job-parameter-driven branching.

2. **Condition task exclusion cascades** — Databricks Jobs cascades EXCLUDED status to
   all dependents, regardless of `run_if: ALL_DONE`. A task depending on an EXCLUDED
   task is itself EXCLUDED. Additionally, condition_task dependencies MUST specify an
   outcome ("true" or "false") — omitting it is an API error.

3. **Certification API was silently failing** — `PATCH /api/2.0/lakeview/dashboards/{id}`
   with a `certification` field returns 200 but ignores the field entirely. The dashboard
   appeared certified in the job output but was not.

4. **Bundle deploy stale cache** — `bundle run` doesn't always update the deployed job
   definition or notebook files. Had to patch the deployed copy manually.

## Key Discoveries

### Entity Tag Assignments API (certification)

- **Endpoint:** `POST /api/2.0/entity-tag-assignments`
- **Payload:** `{"entity_type": "dashboards", "entity_id": "<id>", "tag_key": "system.certification_status", "tag_value": "certified"}`
- **Supported entity_types:** `dashboards`, `geniespaces`, `notebooks`, `apps`, `designer-files`
- **Idempotent:** 409 ALREADY_EXISTS = already certified
- **Requires:** ASSIGN permission on `system.certification_status` governed tag + CAN EDIT on asset
- **Docs:** https://docs.databricks.com/api/tag-assignments/v1/create-tag-assignment
- **NOT the Lakeview PATCH API** — that silently ignores certification fields
- **NOT the UC tags API** (`/api/2.1/unity-catalog/tags`) — that's for UC securables, not workspace objects

### Condition Task DAG Pattern

Dual-dependency pattern for "always run" tasks after a condition:
```yaml
- task_key: register_and_setup
  depends_on:
    - task_key: certify_prod_assets       # true path: runs after certify
    - task_key: should_certify
      outcome: "false"                    # false path: runs immediately
  run_if: AT_LEAST_ONE_SUCCESS
```

When certify=false: should_certify(false) met → register runs.
When certify=true: certify_prod_assets completes → register runs.

## Changes Made

### databricks.yml
- Added `certify_assets` job parameter (default: "false")
- Replaced single `certify_and_register` task with 3-task DAG:
  - `should_certify` — condition_task evaluating `{{job.parameters.certify_assets}}`
  - `certify_prod_assets` — depends on should_certify outcome=true, mode=certify
  - `register_and_setup` — dual-dependency pattern, mode=register
- Each notebook task passes `mode` as base_parameter (certify or register)

### src/certify_and_register.py
- Replaced `certify_assets` widget with `mode` widget (certify|register|all)
- Added mode guards to certify, register, and Genie Code automation cells
- Replaced broken PATCH certification with Entity Tag Assignments API
- Handles 409 ALREADY_EXISTS as success (idempotent)
- Task values (catalog, schema) emitted unconditionally in register cell

### Deployed copy (754043939859691)
- Manually patched widgets cell (certify_assets → mode)
- Manually patched certify cell (PATCH → entity-tag-assignments)
- Manually patched register cell (added mode guard)

## Test Results

| Run | certify_assets | should_certify | certify_prod_assets | register_and_setup |
| --- | --- | --- | --- | --- |
| 619244210623730 | false | SUCCESS | EXCLUDED | SUCCESS |
| 1049994674280738 | true | SUCCESS | SUCCESS | SUCCESS |
| 1121541808005095 | true (with real API) | SUCCESS | SUCCESS | SUCCESS |

All 3 prod assets now certified (verified in UI with blue checkmark):
- CFO Executive Dashboard (01f1bc33b68c13d2aec3b993e9d29f35)
- CMO Performance Dashboard (01f1bc33b68d1fee9a13ac07c15adbad)
- Healthcare Finance Intelligence Genie Agent (01f1b2a18cde1845b9937112d70fe765)

## Commits

1. `refactor: condition_task for certify_assets job parameter` — job YAML + notebook mode widget
2. `fix: dual-dependency pattern for condition_task exclusion cascade` — register depends on both paths
3. `fix: replace silent certification API with manual instructions` — intermediate fix (superseded)
4. `fix: use Entity Tag Assignments API for certification` — correct API discovered and integrated

## Files Modified

- `fhcf-demo/databricks.yml` — condition_task DAG, dual-dependency pattern
- `fhcf-demo/src/certify_and_register.py` — mode widget, guards, entity-tag-assignments API

## Final End-to-End Verification (post bundle deploy)

Clean `bundle deploy --target prod` completed (28 files uploaded, 2 resources changed).
Both job paths re-tested on the freshly deployed bundle:

| Run | certify_assets | should_certify | certify_prod_assets | register_and_setup | Duration |
| --- | --- | --- | --- | --- | --- |
| 892517035986413 | true | SUCCESS | SUCCESS | SUCCESS | 49s |
| 792942375745783 | false | SUCCESS | EXCLUDED | SUCCESS | 28s |

All 3 prod assets verified certified via GET entity-tag-assignments.

## Additional Fix: CMO Dashboard

- `VBC Attribution Rate`: replaced manual `attributed_member_count / member_count` with `MEASURE(attribution_rate)` from the metric view
- `Quality-Adjusted MLR`: algebraically equivalent rewrite (`a*(1+b)` → `a + a*b`), no behavioral change

## Commits (9)

1. `405c4a1` fix(cfo-dashboard): remove phantom short_name from ACO scorecard widget
2. `e4ecb2d` feat: add prod-only certify & register domain assets job
3. `5a19bfb` fix: Config.authenticate() signature changed in latest SDK
4. `fd32f79` refactor: condition_task for certify_assets job parameter
5. `44368a1` fix: dual-dependency pattern for condition_task exclusion cascade
6. `720127a` fix: replace silent certification API with manual instructions
7. `4164079` fix: use Entity Tag Assignments API for certification
8. `1644a82` docs: session summary for 2026-10-05 certify-register refactor
9. `d747502` fix: CMO dashboard use attribution_rate measure directly

## Outstanding

- None — branch is clean and merge-ready.

## Branch

mg-genie-fix-aco-scorecard-widget
