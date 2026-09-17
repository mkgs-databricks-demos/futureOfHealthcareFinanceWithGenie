# The Future of Healthcare Finance with Genie

**Databricks HLS Quarterly Webinar — September 17, 2026**  
**Speaker:** Matt Giglia, Healthcare Field CTO, Databricks

End-to-end demo showing how a health plan CFO can use a **Genie Agent** as a data-smart AI coworker — grounded in governed metric views, semantic ontology, and synthetic healthcare finance data covering MLR trending, HEDIS quality measures, value-based care performance, and avoidable spend analytics.

---

## What's in This Repo

```
futureOfHealthcareFinanceWithGenie/
│
├── fhcf-demo/                 Declarative Automation Bundle
│                               ↳ Schema, seed job, Genie Agent, 8 tables, 6 metric views
│                               ↳ Full reproduction guide in fhcf-demo/README.md
│
├── webinar_slides/            Presentation slide deck (Flask app, 13 slides)
│                               ↳ Run as a Databricks App or locally
│
└── webinar_demo_docs/         Design documents (L100–L300) and Mermaid diagrams
```

---

## Quick Start

### 1. Deploy the data and Genie Agent

```bash
git clone https://github.com/mkgs-databricks-demos/futureOfHealthcareFinanceWithGenie.git
cd futureOfHealthcareFinanceWithGenie/fhcf-demo

# Edit databricks.yml to set your catalog, schema, and warehouse

databricks bundle deploy --target dev          # Creates schema + job
databricks bundle run seed_data --target dev   # Seeds 8 tables + 6 metric views
databricks bundle deploy --target dev          # Creates Genie space (tables must exist first)
```

See **[fhcf-demo/README.md](fhcf-demo/README.md)** for the complete step-by-step guide, including variable configuration, production deployment, validation, ontology setup, and customization.

### 2. Run the slide deck

```bash
cd webinar_slides
pip install -r requirements.txt
python app.py
# Open http://localhost:8000
```

Or deploy as a **Databricks App** by pointing to the `webinar_slides/` directory. Press **F** for fullscreen, **←/→** to navigate, **G** for grid overview.

---

## The Demo

The webinar follows a three-act structure:

**Act 1 — The Problem** (Slides 1–4c): Industry trends, silo pain, regulatory forcing functions (underwriting, NAIC AI, Rx rebates).

**Act 2 — The Solution** (Slides 5–7): Risk adjustment modernization (SAS → Python), unified data vision, transition to live demo.

**Act 3 — The Live Demo** (4 Beats, 8 Prompts):

| Beat | Prompt | What It Shows |
| --- | --- | --- |
| 1a | Morning briefing — flag off-track items | Genie as a scheduled intelligence agent |
| 1b | HEDIS measures below 4-star cutpoints | Drill-down into quality via governed metric views |
| 2a | Top 10 highest-risk members | Member-level detail with risk scores and care gaps |
| 2b | High-risk members in high avoidable ED states | Cross-referencing members with utilization patterns |
| 3a | Calendar integration (MCP connector) | Genie accessing external tools |
| 3b | AHP value-based care overview | ACO performance with synonym resolution |
| 3c | TCOC drill-down — is it pharmacy? | Root cause analysis (GLP-1 cost pressure) |
| 3d | Prepare a brief for Dr. Chen meeting | Synthesized meeting brief from live data |

**Act 4 — The Close** (Slides 9–10): Customer proof points (HSS, Humana, Premier) and sourced references.

---

## Planted Narrative

The synthetic data encodes a deterministic story verified by validation queries:

* Medicaid MLR ~106% (off track), Commercial ~87% (healthy)
* FL, TX, CA: 2x avoidable ED rate vs other states
* BCS at 72% and HbA1c at 58% — both below 4-star cutpoints
* AHP shared savings $2.1M YTD vs $1.8M target; pharmacy PMPM +8% QoQ from GLP-1

---

## What Gets Created

| Layer | Objects |
| --- | --- |
| Tables (8) | dim_aco_contract, dim_budget, dim_member, dim_provider_network, gold_financial_monthly, gold_quality_measures, gold_utilization_monthly, fact_vbc_performance |
| Metric Views (6) | mv_financial, mv_quality, mv_vbc_performance, mv_utilization, mv_budget_variance, mv_member_risk |
| Genie Agent | Healthcare Finance Intelligence — 14 data sources, 7 sample questions, 12 behavioral rules |
| Ontology | 18 UC Pages across Financial, Quality, VBC, and Organizational subdomains |
| Slides | 13 HTML slides with presenter console and speaker notes |

---

## Design Documents

The `webinar_demo_docs/docs/design/` directory contains the full specification:

| Level | Document | Content |
| --- | --- | --- |
| L100 | System Constitution | Overview, data model, demo beats, deploy order |
| L200 | Bundle 1 (Data Foundation) | Table schemas, seed data design |
| L200 | Bundle 2 (AI/BI Experience) | Genie Agent design, benchmark prompts |
| L200 | Glossary Pages | 18 UC Page definitions across 4 subdomains |
| L300 | Table Schemas, Metric Views, Instructions, Seed SQL | Column-level specs, YAML, behavioral rules, INSERT templates |

---

## Customizing

The bundle is designed to be portable. Change three variables in `fhcf-demo/databricks.yml` to deploy to any workspace:

```yaml
variables:
  catalog:
    default: your_catalog
  schema:
    default: your_schema
  warehouse_id:
    lookup:
      warehouse: "your-warehouse-name"
```

All Genie space table references use `${resources.schemas.*}` interpolation and resolve automatically per target. See **[fhcf-demo/README.md](fhcf-demo/README.md)** for details on modifying the narrative, Genie instructions, slides, and ontology.

---

## References

* [Declarative Automation Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-bundles)
* [Metric Views](https://docs.databricks.com/en/sql/language-manual/sql-ref-metric-views.html)
* [Genie Spaces](https://docs.databricks.com/en/genie/index.html)
* [Unity Catalog Pages](https://docs.databricks.com/en/discover/pages.html)

---

## License

See [LICENSE](LICENSE).
