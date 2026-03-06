# Screenshots Needed

This folder is intentionally empty. The following product screenshots
must be captured and placed here before the deck can be finalized:

1. **dashboard.png** -- Main GuardSpine dashboard (governed repos, recent activity, risk distribution)
2. **decision-card.png** -- A real GitHub PR showing the APPROVED/CONDITIONAL/BLOCKED decision card posted by codeguard-action
3. **evidence-bundle.png** -- BundleDetailPage showing hash chain, items, verification status
4. **rubric-editor.png** -- RubricEditorPage showing a compliance rubric being edited
5. **approvals.png** -- ApprovalsPage showing pending/approved/rejected decisions
6. **guard-lanes.png** -- GuardLanesPage showing PDF/Sheet/Image/Code lane configuration

## How to capture

Run the GuardSpine platform locally:

```bash
cd D:\Projects\GuardSpine\backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://localhost:5173 (frontend) and screenshot each page.
Crop to 16:9 aspect ratio. Save as PNG at 2x resolution (2560x1440).
