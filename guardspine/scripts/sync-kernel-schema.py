#!/usr/bin/env python3
# sync-kernel-schema.py -- Copy JSON Schema from guardspine-kernel into backend.
# ASCII only. Standard library only.
"""
Sync the evidence-bundle.schema.json from the guardspine-kernel package
into the backend so kernel.py can load it at runtime.

Usage:
    python scripts/sync-kernel-schema.py
"""

import hashlib
import os
import shutil
import sys


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kernel_root = os.path.normpath(os.path.join(repo_root, "..", "guardspine-kernel"))

    src = os.path.join(kernel_root, "src", "schemas", "evidence-bundle.schema.json")
    dst_dir = os.path.join(repo_root, "backend", "app", "core", "schemas")
    dst = os.path.join(dst_dir, "evidence-bundle.schema.json")

    if not os.path.isfile(src):
        print("ERROR: Source schema not found at %s" % src)
        return 1

    os.makedirs(dst_dir, exist_ok=True)

    src_hash = file_sha256(src)

    # Check if already in sync
    if os.path.isfile(dst):
        dst_hash = file_sha256(dst)
        if src_hash == dst_hash:
            print("OK: Schema already in sync (sha256:%s)" % src_hash[:16])
            return 0
        else:
            print("UPDATING: Schema differs, copying fresh...")
    else:
        print("CREATING: First sync, copying schema...")

    shutil.copy2(src, dst)

    # Verify copy
    dst_hash = file_sha256(dst)
    if dst_hash != src_hash:
        print("ERROR: Hash mismatch after copy!")
        print("  Source:  %s" % src_hash)
        print("  Dest:    %s" % dst_hash)
        return 1

    print("OK: Schema synced (sha256:%s)" % dst_hash[:16])
    print("  From: %s" % src)
    print("  To:   %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
