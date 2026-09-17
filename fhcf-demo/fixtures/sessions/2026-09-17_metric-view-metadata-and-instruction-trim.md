# Session: Metric View Metadata Enrichment & Instruction Trim

**Date:** 2026-09-17  
**Branch:** `mg-genie-ddl-metrics-genie-space`  
**Bundle:** fhcf-demo  
**Scope:** Migrate redundant Genie instruction content into metric view semantic metadata; retest all demo beats post-trim

---

## Problems Addressed

1. **Instruction bloat** — The Genie space instruction text contained a large GLOSSARY (11 definitions) and a CONDITION DOMAINS block that duplicated information already present in metric view `comment`, `synonyms`, and `format` metadata.
2. **Beat 1b routing weakness** — In the prior session, Beat 1b queried `gold_quality_measures` directly instead of `mv_quality`. While functionally equivalent, it bypassed the governed metric view.
3. **AHP synonym gap** — The `mv_vbc_performance.aco_name` dimension lacked "AHP" and "Accountable Health Partners" as synonyms, forcing Rule 8 in the instruction to carry the full routing burden.
4. **Weak authoritative-source signals** — `mv_budget_variance` and `mv_utilization` COMMENT ON VIEW strings didn't explicitly state they were the only authorized source for their respective KPIs.

## Root Causes

* The original instruction was written before metric views had rich semantic metadata. Glossary terms (MLR, PMPM, TCOC, care gap, avoidable utilization, HEDIS, STARS, LOB values) were placed in the instruction because metric view comments were minimal at the time.
* After the DDL & Metric View Improvements session enriched all 6 views with `display_name`, `synonyms`, `format`, and detailed `comment` fields, the instruction became partially redundant but was never trimmed.
* Condition-domain mappings (CDC-HBA1C → Diabetes, BCS → Cancer Screening, etc.) belonged in `mv_quality.condition_domain.comment` but were only in the instruction text.

## Analysis: What Can vs Cannot Move to Metric Views

### Migrated to metric view metadata (removed from instructions)

| Content | Former Location | New Location |
| --- | --- | --- |
| MLR, PMPM, TCOC, care gap, avoidable utilization definitions | GLOSSARY section | Already in measure `comment` fields across mv_financial, mv_vbc_performance |
| HEDIS, STARS, LOB value definitions | GLOSSARY section | Already in dimension `comment` fields |
| AHP = Accountable Health Partners = ACO-001 | GLOSSARY + Rule 8 | `mv_vbc_performance.aco_name` synonyms + COMMENT ON VIEW |
| Condition domain → HEDIS measure ID mappings | CONDITION DOMAINS section | `mv_quality.condition_domain.comment` + COMMENT ON VIEW |
| "Authoritative source" for budget variance | Implicit in Rule 4 | `mv_budget_variance` COMMENT ON VIEW |
| "Authoritative source" for utilization rates | Implicit in Rule 11 | `mv_utilization` COMMENT ON VIEW |

### Retained in instructions (cannot live in metric view metadata)

| Content | Reason |
| --- | --- |
| All 12 behavioral routing rules | Procedural ("for question type X, use view Y") |
| MEASURE() syntax examples (6 queries) | Query execution guidance |
| Morning briefing prioritization logic (Rule 10) | Multi-domain synthesis directive |
| Meeting brief synthesis directive (Rule 9) | Narrative generation — fixed Beat 3d |
| Privacy rule — hide member_id (Rule 7) | Behavioral constraint |
| Gainsharing 60/25/15 split | Domain knowledge, not a queryable column |
| "All data is synthetic" disclaimer (Rule 12) | Behavioral |

## Changes Made

### 1. Metric View Metadata Enrichment (4 cells in seed_all_data)

| Metric View | Changes |
| --- | --- |
| `mv_quality` | Enriched `condition_domain` dimension comment with explicit HEDIS code → domain mapping: "Diabetes: CDC-HBA1C, CDC-EYE; Cardiovascular: CBP; Cancer Screening: BCS, CCS; Behavioral Health: FUH-7". Added "measure family" synonym. Appended domain mappings to COMMENT ON VIEW. |
| `mv_vbc_performance` | Added "AHP" and "Accountable Health Partners" as synonyms on `aco_name` dimension. Updated `aco_name` comment to note AHP = ACO-001. Appended AHP identifier to COMMENT ON VIEW. |
| `mv_utilization` | Strengthened `member_months` comment to "authoritative denominator". Appended authoritative-source guidance to COMMENT ON VIEW: "all per-1K measures are pre-computed... should not be manually recalculated from raw counts." |
| `mv_budget_variance` | Strengthened `target_mlr` comment to "authoritative target". Appended authoritative-source guidance to COMMENT ON VIEW: "do not manually join dim_budget when these measures are needed." |

### 2. Genie Instruction Trim (genie_space.yml)

| Section | Change |
| --- | --- |
| GLOSSARY (11 definitions) | Replaced with DOMAIN CONTEXT containing only the gainsharing split (the one definition not covered by metric view metadata) |
| Rule 8 (AHP routing) | Simplified from `WHERE aco_name LIKE '%AHP%' or aco_id = 'ACO-001'` to `for aco_id = 'ACO-001'` — AHP synonyms now live in metric view |
| CONDITION DOMAINS block | Removed entirely — mappings now in mv_quality.condition_domain.comment and COMMENT ON VIEW |
| All other rules (1-7, 9-12) | Preserved unchanged |
| MEASURE() SYNTAX REMINDER | Preserved unchanged |

**Net instruction reduction:** ~25% shorter (removed glossary + condition domains, simplified Rule 8).

### 3. Bundle Deploy

* `bundle validate --strict --target dev` — Validation OK
* `bundle deploy --target dev --auto-approve` — 1 resource changed (genie_spaces.healthcare_finance_intelligence), 3 unchanged

### 4. Demo Beat Retest (7/7 Passing)

| Beat | Prompt | Result | Notes |
| --- | --- | --- | --- |
| 1a | Morning briefing | PASS | Flagged off-track items, 6 attachments, multi-query. Used mv_budget_variance. |
| 1b | Quality drill-down | PASS | **Now uses mv_quality** (was gold_quality_measures in prior session). MEASURE() syntax correct. Identified 4 measures below 4-star. |
| 2a | Top 10 high-risk members | PASS | Hid member_id, showed risk scores + NBA interventions. |
| 2b | Cross-domain (risk + ED) | PASS | Cross-joined dim_member with mv_utilization avoidable_ed_rate. |
| 3a | Calendar (MCP) | SKIP | External connector — not testable via API. |
| 3b | AHP overview | PASS | Used mv_vbc_performance. Showed AHP $2.1M savings, $892 TCOC, $198 pharmacy. |
| 3c | TCOC drill-down | PASS | Pharmacy PMPM trend isolated. Used LAG() over quarters. |
| 3d | Meeting brief | PASS | Synthesized numbered brief. Queried both mv_vbc_performance and mv_quality. No decline. |

### Planted Narrative Values Confirmed

* AHP shared savings: $2.1M YTD (Q3)
* AHP TCOC: $892 PMPM
* AHP Pharmacy: $198 PMPM
* BCS: 72.20% vs 74.00% 4-star cutpoint (1,402 gaps)
* HbA1c: 58.20% vs 60.00% 4-star cutpoint (2,610 gaps)

## Decisions

1. **Glossary removal is safe** — All definitions (MLR, PMPM, TCOC, etc.) already existed in metric view measure/dimension `comment` fields from the prior DDL session. The glossary was redundant.
2. **Gainsharing split stays in instructions** — The 60/25/15 provider distribution is domain knowledge with no corresponding metric view column. It's the only GLOSSARY item that couldn't migrate.
3. **Behavioral rules are load-bearing** — The routing rules, MEASURE() syntax, and synthesis directives are what make the Genie agent reliable. They cannot be expressed as column metadata and must remain in the instruction text.
4. **Beat 1b routing improved** — The enriched COMMENT ON VIEW on `mv_quality` appears to have helped Genie prefer the governed metric view over the raw table. This was a cosmetic concern flagged in the prior session and is now resolved without any instruction change.

## Files Modified

| File | Type | Changes |
| --- | --- | --- |
| `src/seed_all_data` | Notebook | 4 cells updated (mv_quality, mv_vbc_performance, mv_utilization, mv_budget_variance) |
| `resources/healthcare_finance_intelligence.genie_space.yml` | File | Instruction text trimmed ~25%: glossary → domain context, condition domains removed, Rule 8 simplified |

## Known Limitations / Follow-ups

* Metric view metadata changes are notebook-level edits only — `seed_all_data` must be re-run to recreate the views in UC with updated COMMENT ON VIEW strings.
* The AHP synonym enrichment on `mv_vbc_performance.aco_name` will take effect only after the notebook is re-executed and the Genie space cache refreshes.
* No window measures (trailing 3-month MLR, cumulative YTD spend) added yet — noted in prior session as potential enhancement.
