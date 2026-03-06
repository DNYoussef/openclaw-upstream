#!/usr/bin/env python3
"""Validate CLAIMS-REGISTRY.yaml against live code/data."""
import yaml, subprocess, sys, os

REGISTRY = os.path.join(os.path.dirname(__file__), "CLAIMS-REGISTRY.yaml")
FAIL = 0

def check(label, expected, actual):
    global FAIL
    ok = expected == actual
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: expected={expected}, actual={actual}")
    if not ok:
        FAIL += 1

with open(REGISTRY) as f:
    reg = yaml.safe_load(f)

# 1. Test count in codeguard-action
print("=== Test Counts ===")
r = subprocess.run(
    ["python", "-m", "pytest", "--co", "-q"],
    capture_output=True, text=True, cwd="D:/Projects/codeguard-action"
)
for line in r.stdout.splitlines():
    if "tests collected" in line:
        n = int(line.split()[0])
        check("codeguard-action tests", reg["tests"]["breakdown"]["codeguard-action"], n)
        break

# 2. Route count
print("=== Route Count ===")
r = subprocess.run(
    ["grep", "-rc", "@router\\.", "D:/Projects/GuardSpine/backend/app/routers/"],
    capture_output=True, text=True
)
total = sum(int(l.split(":")[-1]) for l in r.stdout.strip().splitlines() if l)
check("backend routes", reg["routes"]["total"], total)

# 3. No stale "758 test" in investor/strategy docs (excluding audit doc and this script)
print("=== Stale Numbers ===")
r = subprocess.run(
    ["grep", "-rn", "--include=*.md", "758 test", "C:/Users/17175/Desktop/guardspine/"],
    capture_output=True, text=True
)
hits = [l for l in r.stdout.strip().splitlines() if l
        and "ALIGNMENT-AUDIT" not in l and "validate-claims" not in l]
check("no '758 test' in docs", 0, len(hits))

# 4. No "satisfies DORA" in outreach
r = subprocess.run(
    ["grep", "-rn", "satisfies DORA", "C:/Users/17175/scripts/content-pipeline/"],
    capture_output=True, text=True
)
check("no 'satisfies DORA' in outreach", 0, len(r.stdout.strip().splitlines()) if r.stdout.strip() else 0)

print(f"\n{'ALL PASSED' if FAIL == 0 else f'{FAIL} FAILURE(S)'}")
sys.exit(FAIL)
