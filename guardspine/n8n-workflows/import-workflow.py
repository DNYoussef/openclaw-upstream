"""Import n8n workflow via API. Run inside Railway network.

Usage: python import-workflow.py <workflow-json-path>
Or set N8N_INTERNAL_URL and N8N_API_KEY env vars and run directly.
"""

import json
import os
import sys
import urllib.request

N8N_URL = os.environ.get("N8N_INTERNAL_URL", "http://n8n.railway.internal:5678")
API_KEY = os.environ.get("N8N_API_KEY", "")
if not API_KEY:
    print("WARNING: N8N_API_KEY is empty. All API calls will fail authentication.")

def import_workflow(workflow_path):
    with open(workflow_path) as f:
        workflow = json.load(f)

    # Create workflow via n8n API
    data = json.dumps(workflow).encode()
    req = urllib.request.Request(
        f"{N8N_URL}/api/v1/workflows",
        data=data,
        headers={
            "X-N8N-API-KEY": API_KEY,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        wf_id = result.get("id", "unknown")
        print(f"OK: Workflow created: {result.get('name')} (id={wf_id})")

        # Activate workflow
        activate_data = json.dumps({"active": True}).encode()
        activate_req = urllib.request.Request(
            f"{N8N_URL}/api/v1/workflows/{wf_id}",
            data=activate_data,
            headers={
                "X-N8N-API-KEY": API_KEY,
                "Content-Type": "application/json",
            },
            method="PATCH",
        )
        activate_resp = urllib.request.urlopen(activate_req, timeout=10)
        print(f"OK: Workflow activated")
        return wf_id

    except urllib.error.HTTPError as e:
        print(f"ERROR: {e.code} {e.reason}")
        print(f"Body: {e.read().decode()[:500]}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "definitions/cmo-outreach-pipeline.json"
    import_workflow(path)
