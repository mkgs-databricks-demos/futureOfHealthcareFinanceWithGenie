# Databricks notebook source
# DBTITLE 1,Install latest Databricks SDK
# MAGIC %pip install --upgrade databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,[FHCF] Certify & Register Domain Assets
# MAGIC %md
# MAGIC # [FHCF] Certify & Register Domain Assets
# MAGIC
# MAGIC Production-only workflow for:
# MAGIC 1. **Certifying** prod dashboards and Genie Agent (`system.certification_status = certified`)
# MAGIC 2. **Registering** dashboards and Genie Agent in a UC Discover domain
# MAGIC 3. **Creating** a Genie Code automation for UC Pages research and creation
# MAGIC
# MAGIC **Parameters** (passed from job via bundle resource refs):
# MAGIC - `certify_assets` — `true` to certify, `false` to skip (default: `false`)
# MAGIC - `domain_name` — Target Discover domain name (default: `mkgs_hc_finance`)
# MAGIC - `catalog`, `schema` — UC catalog and schema
# MAGIC - `cfo_dashboard_id`, `cmo_dashboard_id` — Prod dashboard IDs
# MAGIC - `genie_space_id` — Prod Genie Agent ID
# MAGIC
# MAGIC **How pages were originally created (2026-09-17):**
# MAGIC Genie Code's Discover-page agent was used with `addAssetToCurrentDomain` and bulk page creation.
# MAGIC Source material: `webinar_demo_docs/docs/design/L200-C_glossary_pages.md` (18 terms, 4 subdomains).
# MAGIC All pages were created as DRAFT and must be published individually in the Discover UI.

# COMMAND ----------

# DBTITLE 1,Configuration — widgets and parameters
dbutils.widgets.text("certify_assets", "false", "Certify Assets (true/false)")
dbutils.widgets.text("domain_name", "mkgs_hc_finance", "Domain Name")
dbutils.widgets.text("catalog", "hls_fde", "Catalog")
dbutils.widgets.text("schema", "healthcare_finance", "Schema")
dbutils.widgets.text("cfo_dashboard_id", "", "CFO Dashboard ID")
dbutils.widgets.text("cmo_dashboard_id", "", "CMO Dashboard ID")
dbutils.widgets.text("genie_space_id", "", "Genie Space ID")

certify = dbutils.widgets.get("certify_assets").lower() == "true"
domain_name = dbutils.widgets.get("domain_name")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
cfo_dashboard_id = dbutils.widgets.get("cfo_dashboard_id")
cmo_dashboard_id = dbutils.widgets.get("cmo_dashboard_id")
genie_space_id = dbutils.widgets.get("genie_space_id")

print(f"Certify assets: {certify}")
print(f"Domain: {domain_name}")
print(f"Target schema: {catalog}.{schema}")
print(f"CFO Dashboard: {cfo_dashboard_id or '(not set)'}")
print(f"CMO Dashboard: {cmo_dashboard_id or '(not set)'}")
print(f"Genie Space: {genie_space_id or '(not set)'}")

# Emit catalog and schema as task values so the downstream genie_task can reference them
try:
    dbutils.jobs.taskValues.set(key="catalog", value=catalog)
    dbutils.jobs.taskValues.set(key="schema", value=schema)
except Exception:
    pass  # Not running as a job task (interactive mode)

# COMMAND ----------

# DBTITLE 1,SDK client and helpers
from databricks.sdk import WorkspaceClient
import requests, json

w = WorkspaceClient()
host = w.config.host
uid = w.current_user.me().id

def _headers():
    """Get authenticated headers for REST calls."""
    h = {}
    w.config.authenticate(h)
    return h

def _api(method, path, body=None):
    """Helper for REST calls with logging."""
    url = f"{host}{path}"
    resp = requests.request(method, url, headers=_headers(), json=body)
    return resp

results = []  # Track outcomes for summary
print(f"Authenticated as user {uid}")

# COMMAND ----------

# DBTITLE 1,Certify production assets
if not certify:
    print("Skipping certification (certify_assets=false)")
else:
    assets_to_certify = []
    if cfo_dashboard_id:
        assets_to_certify.append(("CFO Executive Dashboard", "dashboard", cfo_dashboard_id))
    if cmo_dashboard_id:
        assets_to_certify.append(("CMO Performance Dashboard", "dashboard", cmo_dashboard_id))
    if genie_space_id:
        assets_to_certify.append(("Healthcare Finance Intelligence", "genie_space", genie_space_id))

    for name, asset_type, asset_id in assets_to_certify:
        # Attempt certification via PATCH with certification field
        if asset_type == "dashboard":
            resp = _api("PATCH", f"/api/2.0/lakeview/dashboards/{asset_id}",
                        {"certification": {"status": "CERTIFIED"}})
        else:
            resp = _api("PATCH", f"/api/2.0/genie/spaces/{asset_id}",
                        {"certification": {"status": "CERTIFIED"}})

        if resp.status_code == 200:
            print(f"  CERTIFIED: {name} ({asset_id})")
            results.append({"asset": name, "action": "certify", "status": "success"})
        else:
            print(f"  API returned {resp.status_code} for {name}: {resp.text[:200]}")
            results.append({"asset": name, "action": "certify", "status": f"http_{resp.status_code}",
                            "detail": resp.text[:200]})

    # Report manual fallback for any failures
    failed = [r for r in results if r["status"] != "success"]
    if failed:
        print("\n--- Manual Certification Fallback ---")
        print("For assets the API could not certify, open each in the UI:")
        for f in failed:
            print(f"  {f['asset']}: three-dot menu > Assign certification > Certified")
        print(f"  Or use Discover > {domain_name} > asset page > Certify")

# COMMAND ----------

# DBTITLE 1,Register assets to domain
# Discover domains use governed tags for asset assignment.
# The domain's governed tag must exist at the account level.
# We attempt the Domains API first, then governed tag assignment.

# Step 1: Verify domain exists
resp = _api("GET", f"/api/2.0/unity-catalog/domains/{domain_name}")
if resp.status_code == 200:
    domain_info = resp.json()
    print(f"Domain found: {domain_info.get('display_name', domain_name)}")
else:
    # Try listing domains to find by name
    resp = _api("GET", "/api/2.0/unity-catalog/domains")
    if resp.status_code == 200:
        domains = resp.json().get("domains", [])
        match = [d for d in domains if d.get("name") == domain_name or d.get("display_name") == domain_name]
        if match:
            domain_info = match[0]
            print(f"Domain found: {domain_info.get('display_name', domain_name)} (id={domain_info.get('id')})")
        else:
            print(f"Domain '{domain_name}' not found. Available: {[d.get('name') for d in domains]}")
            domain_info = None
    else:
        print(f"Domains API returned {resp.status_code}: {resp.text[:200]}")
        domain_info = None

# Step 2: Register dashboards and Genie space to the domain
if domain_info:
    workspace_assets = []
    if cfo_dashboard_id:
        workspace_assets.append(("CFO Executive Dashboard", "DASHBOARD", cfo_dashboard_id))
    if cmo_dashboard_id:
        workspace_assets.append(("CMO Performance Dashboard", "DASHBOARD", cmo_dashboard_id))
    if genie_space_id:
        workspace_assets.append(("Healthcare Finance Intelligence", "GENIE_SPACE", genie_space_id))

    domain_id = domain_info.get("id", domain_info.get("name", domain_name))

    for name, asset_type, asset_id in workspace_assets:
        # Try adding asset to domain
        resp = _api("POST", f"/api/2.0/unity-catalog/domains/{domain_id}/assets",
                    {"asset_type": asset_type, "asset_id": asset_id})
        if resp.status_code in (200, 201):
            print(f"  REGISTERED: {name} -> {domain_name}")
            results.append({"asset": name, "action": "register", "status": "success"})
        else:
            print(f"  API returned {resp.status_code} for {name}: {resp.text[:200]}")
            results.append({"asset": name, "action": "register", "status": f"http_{resp.status_code}",
                            "detail": resp.text[:200]})

    reg_failed = [r for r in results if r["action"] == "register" and r["status"] != "success"]
    if reg_failed:
        print("\n--- Manual Registration Fallback ---")
        print(f"Open Discover > {domain_name} > Add assets, and add:")
        for f in reg_failed:
            print(f"  {f['asset']}")
else:
    print(f"\nSkipping registration — domain '{domain_name}' could not be resolved.")
    print("Create it in Discover or verify the name, then re-run.")

# COMMAND ----------

# DBTITLE 1,Create Genie Code automation for page creation
# Creates a Genie Code scheduled automation (no schedule — driven by the job's genie_task)
# that researches the schema and creates UC Pages for the domain.
# Idempotent: checks for an existing automation first; always emits the task value
# so the downstream genie_task resolves its configuration_id at runtime.

AUTOMATION_DISPLAY_PREFIX = f"[FHCF] Pages — {domain_name}"

page_creation_prompt = f"""Research the healthcare finance domain in catalog `{catalog}`, schema `{schema}`.
Review all tables and metric views, their comments, column descriptions, and semantic metadata.

Then create UC Pages in the `{domain_name}` domain for the key business terms found in
the schema. Use the design document at `webinar_demo_docs/docs/design/L200-C_glossary_pages.md`
as the source template for term definitions.

For each page:
1. Set a clear Name (the canonical business term)
2. Write a Description (one-line summary, max 160 chars)
3. Write a Body with ## Definition, ## Business use, and ## Data usage sections
4. Add Synonyms (abbreviations and alternate names)
5. Add Related Assets: link to the relevant tables, metric views, dashboards, and the
   Genie Agent "Healthcare Finance Intelligence" in `{catalog}.{schema}`
6. Add the design document as a Source

Organize across four subdomains: Financial, Quality, VBC (Value-Based Care), Organizational.
Create all pages as drafts. Report what was created."""

configuration_id = None

# --- Check for existing automation ---
try:
    existing = w.api_client.do(
        "GET",
        "/api/2.0/alerts-internal/scheduled-insights",
        query={"parent_asset_name": f"users/{uid}"},
    )
    for item in existing.get("scheduled_insights", []):
        prompt = item.get("scheduled_insight", {}).get("user_prompt", "")
        if domain_name in prompt and catalog in prompt and "UC Pages" in prompt:
            configuration_id = item["name"]
            print(f"Reusing existing Genie Code automation: {configuration_id}")
            break
except Exception:
    pass  # List endpoint may not exist; fall through to create

# --- Create if none found ---
if not configuration_id:
    try:
        resp = w.api_client.do(
            "POST",
            "/api/2.0/alerts-internal/scheduled-insights",
            body={
                "parent_asset_name": f"users/{uid}",
                "scheduled_insight": {
                    "insight_type": "GENIE_CODE",
                    "user_prompt": page_creation_prompt,
                },
            },
        )
        configuration_id = resp["name"]
        print(f"Created new Genie Code automation: {configuration_id}")
    except Exception as e:
        print(f"Error creating Genie Code automation: {e}")
        print("The automation can be created manually via Genie Code scheduled tasks.")
        results.append({"asset": "Genie Code automation", "action": "create",
                        "status": "error", "detail": str(e)})

# --- Always emit as task value for the downstream genie_task ---
if configuration_id:
    try:
        dbutils.jobs.taskValues.set(key="genie_pages_automation_id", value=configuration_id)
    except Exception:
        pass  # Interactive mode — no job context
    print(f"\nTask value set: genie_pages_automation_id = {configuration_id}")
    print("The downstream create_domain_pages genie_task will pick this up automatically.")
    results.append({"asset": "Genie Code automation", "action": "create",
                    "status": "success", "detail": configuration_id})

# COMMAND ----------

# DBTITLE 1,Summary
print("=" * 60)
print("CERTIFICATION & REGISTRATION SUMMARY")
print("=" * 60)

for r in results:
    status_icon = "OK" if r["status"] == "success" else "MANUAL"
    print(f"  [{status_icon:6s}] {r['action']:10s} | {r['asset']}")
    if r.get("detail") and r["status"] != "success":
        print(f"           {r['detail'][:80]}")

success_count = sum(1 for r in results if r["status"] == "success")
manual_count = len(results) - success_count
print(f"\nTotal: {success_count} succeeded, {manual_count} need manual action")

if manual_count > 0:
    print(f"\nOpen Discover > {domain_name} to complete manual steps.")