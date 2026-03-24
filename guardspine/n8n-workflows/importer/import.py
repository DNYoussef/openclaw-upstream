"""Import updated n8n workflows: list, replace existing, activate all."""
import json
import os
import glob
import urllib.request
import urllib.error
import time

N8N_URL = os.environ.get("N8N_URL", "http://n8n.railway.internal:5678")
API_KEY = os.environ.get("N8N_API_KEY", "")
if not API_KEY:
    print("WARNING: N8N_API_KEY is empty. All API calls will fail authentication.")
HEADERS = {"X-N8N-API-KEY": API_KEY, "Content-Type": "application/json"}
WORKFLOW_DIR = os.path.join(os.path.dirname(__file__), "workflows")


def api(method, path, data=None):
    """Make an n8n API request. Returns parsed JSON or None on error."""
    url = N8N_URL + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = ""
        if hasattr(e, "read"):
            err_body = e.read().decode()[:500]
        print(f"  API ERROR {method} {path}: {e.code} {err_body}")
        return None
    except Exception as e:
        print(f"  API ERROR {method} {path}: {e}")
        return None


def list_workflows():
    """Get all existing workflows as {name: id} map."""
    result = api("GET", "/api/v1/workflows")
    if not result:
        return {}
    workflows = result.get("data", [])
    name_map = {}
    for wf in workflows:
        name_map[wf["name"]] = wf["id"]
    return name_map


def delete_workflow(wf_id):
    """Delete a workflow by ID."""
    return api("DELETE", f"/api/v1/workflows/{wf_id}")


def create_workflow(wf_data):
    """Create a workflow. Returns the created workflow or None."""
    return api("POST", "/api/v1/workflows", wf_data)


def activate_workflow(wf_id):
    """Activate a workflow by ID. Try POST activate endpoint first, fall back to PUT."""
    result = api("POST", f"/api/v1/workflows/{wf_id}/activate")
    if result is not None:
        return result
    # Fallback: PUT the workflow with active=true
    return api("PUT", f"/api/v1/workflows/{wf_id}", {"active": True})


def main():
    print("=" * 60)
    print("n8n Workflow Importer")
    print("=" * 60)
    print(f"Target: {N8N_URL}")

    # Wait for n8n to be reachable (Railway internal networking)
    print("\nWaiting for n8n to be reachable...")
    for attempt in range(12):
        try:
            req = urllib.request.Request(
                N8N_URL + "/api/v1/workflows?limit=1",
                headers=HEADERS, method="GET"
            )
            urllib.request.urlopen(req, timeout=5)
            print("  n8n is reachable.")
            break
        except Exception:
            print(f"  Attempt {attempt + 1}/12 - waiting 10s...")
            time.sleep(10)
    else:
        print("FATAL: Could not reach n8n after 2 minutes. Exiting.")
        return

    # Step 1: List existing workflows
    print("\n--- Step 1: List existing workflows ---")
    existing = list_workflows()
    print(f"Found {len(existing)} existing workflow(s):")
    for name, wf_id in existing.items():
        print(f"  [{wf_id}] {name}")

    # Step 2: Load local workflow files
    print("\n--- Step 2: Load local workflow files ---")
    wf_files = sorted(glob.glob(os.path.join(WORKFLOW_DIR, "*.json")))
    if not wf_files:
        print("No workflow files found. Exiting.")
        return
    print(f"Found {len(wf_files)} workflow file(s).")

    created_ids = []

    for fpath in wf_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r") as f:
            wf_data = json.load(f)

        wf_name = wf_data.get("name", fname)
        print(f"\n  Processing: {wf_name} ({fname})")

        # Step 3: If workflow exists by name, delete the old version
        if wf_name in existing:
            old_id = existing[wf_name]
            print(f"    Deleting existing [{old_id}]...")
            delete_workflow(old_id)
            del existing[wf_name]

        # Step 4: Create the new version
        print(f"    Creating...")
        result = create_workflow(wf_data)
        if result:
            new_id = result.get("id")
            print(f"    Created [{new_id}]")
            created_ids.append(new_id)
        else:
            print(f"    FAILED to create {wf_name}")

    # Step 5: Activate all created workflows
    print("\n--- Step 3: Activate all workflows ---")
    for wf_id in created_ids:
        print(f"  Activating [{wf_id}]...")
        result = activate_workflow(wf_id)
        if result:
            print(f"    Active: {result.get('active', '?')}")
        else:
            print(f"    FAILED to activate {wf_id}")

    # Final summary
    print("\n" + "=" * 60)
    print(f"Done. {len(created_ids)}/{len(wf_files)} workflows imported and activated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
