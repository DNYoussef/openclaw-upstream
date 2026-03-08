# GuardSpine Document Governance Template

Track changes to PDF, spreadsheet, and image files with automated governance.

## What It Does

This repository template uses GuardSpine to apply the same code-review
governance workflow to binary document files. When you open a pull request
that adds or modifies files in the `pdfs/`, `sheets/`, or `images/`
directories, the **codeguard-action** GitHub Action runs automatically:

1. Detects the file type from the extension.
2. Routes the change to the correct guard lane (`pdf`, `sheet`, or `image`).
3. Computes a diff (binary hash comparison or content extraction).
4. Assigns a risk tier (L0-L4) based on the change profile.
5. Creates an approval request when the risk exceeds your threshold.
6. Generates a tamper-evident evidence bundle for the audit trail.

## Setup

1. Fork or use this repository as a template.
2. Add a repository secret named `GUARDSPINE_API_URL` with your GuardSpine
   instance URL (e.g., `https://guardspine.example.com`).
3. The `GITHUB_TOKEN` secret is provided automatically by GitHub Actions.

## Folder Structure

```
pdfs/       -- PDF documents
sheets/     -- Excel spreadsheets (.xlsx, .xlsm)
images/     -- Image files (.png, .jpg, .jpeg, .bmp, .tiff)
```

## Workflow

1. Create a branch and add or replace files in the appropriate folder.
2. Open a pull request.
3. The `codeguard.yml` workflow triggers and scans the changed files.
4. Review the Decision Card comment posted on the PR.
5. If the risk tier requires approval, a designated reviewer must approve
   before the PR can be merged.

## Git LFS

Binary files are tracked with Git LFS via `.gitattributes`. Make sure
Git LFS is installed (`git lfs install`) before cloning or pushing.
