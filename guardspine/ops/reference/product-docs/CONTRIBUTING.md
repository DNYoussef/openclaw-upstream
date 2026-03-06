# Contributing

## Development

1. Create a feature branch from `main`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```
3. Run local checks:
   ```bash
   python -m pytest -q
   python eval/run_eval.py --tier L0 --dataset hand-crafted --max-fp 45 --max-fn 5
   ```

## Pull Requests

1. Add or update tests for behavior changes.
2. Keep security-sensitive logic deterministic and explicit.
3. Do not introduce mutable dependency refs (for example `@main`).
4. Ensure CI is green before requesting review.
