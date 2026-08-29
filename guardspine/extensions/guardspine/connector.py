"""
GuardSpine <-> OpenClaw Hardening Connector

** NOT CURRENTLY WIRED IN. Confirmed during Phase 3A governance-routing
** consolidation (see ../../GOVERNANCE_ROUTING.md): the live OpenClaw
** governance extension is plugin.js in this same directory (declared as
** `main` in package.json / openclaw.plugin.json), and its `before_tool_call`
** hook calls its OWN self-contained 3-model council (runCouncilReview, via
** LiteLLM) directly. Nothing in plugin.js -- or anywhere else in this repo
** except one documentation file -- imports this module, spawns Python, or
** references OpenClawConnector. That's checked mechanically by
** ../lib/check-governance-routing.cjs, with a positive control proving the
** check would catch it if that ever changed.
**
** This file is left in place, not deleted, because it's real, working
** design intent for a governance path that was apparently never finished
** wiring up -- deleting it would erase that intent rather than resolve it.
** If this bridge is ever meant to be live, that's a deliberate, reviewed
** activation decision (a real policy change, adding a second governance
** system alongside plugin.js's), not something to do silently.

This is the ONLY file that lives in GuardSpine proper.
It provides the adapter interface between GuardSpine's
existing governance engine and the openclaw-hardening project.

This connector:
1. Translates GuardSpine action requests into openclaw-hardening format
2. Routes evidence packs to the council runner
3. Forwards L4 approvals through OpenClaw's Discord integration
4. Returns verdicts back to GuardSpine's governance engine
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Add openclaw-hardening to path for imports
# Env var > sibling directory > skip
_openclaw_env = os.environ.get("OPENCLAW_ROOT")
if _openclaw_env:
    OPENCLAW_ROOT = Path(_openclaw_env)
else:
    OPENCLAW_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "openclaw-hardening"
if OPENCLAW_ROOT.is_dir() and str(OPENCLAW_ROOT) not in sys.path:
    sys.path.insert(0, str(OPENCLAW_ROOT))


class OpenClawConnector:
    """Bridge between GuardSpine governance and openclaw-hardening."""

    def __init__(self):
        self._council = None
        self._gate = None
        self._quarantine = None

    @property
    def council(self):
        if not self._council:
            from council.council_runner import run_council
            self._council = run_council
        return self._council

    @property
    def gate(self):
        if not self._gate:
            from approvals.approval_gate import ApprovalGate
            self._gate = ApprovalGate()
        return self._gate

    @property
    def quarantine(self):
        if not self._quarantine:
            from quarantine.quarantine_manager import QuarantineManager
            self._quarantine = QuarantineManager()
        return self._quarantine

    def evaluate_evidence(self, pack: dict, mode: str) -> dict:
        """Run 3-model council on evidence pack."""
        return self.council(pack, mode)

    def check_approval(self, tier: str, evidence: dict | None = None, council: dict | None = None) -> dict:
        """Check if action is approved at given tier."""
        return self.gate.check(tier, evidence, council)

    def quarantine_download(self, source: Path, origin: str, meta: dict | None = None) -> dict:
        """Place download in quarantine."""
        return self.quarantine.receive(source, origin, meta)

    def promote_download(self, filename: str, council_result: dict, target: str = "") -> dict:
        """Promote quarantined file after council pass."""
        return self.quarantine.promote(filename, council_result, target)
