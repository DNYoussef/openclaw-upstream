#!/usr/bin/env python3
"""
Phase 1 Dry Run Script

Manually verifies all Phase 1 functionality:
1.1 - Reject API with required message
1.2 - Frontend reject modal (manual check)
1.3 - Slack interactive endpoint
1.4 - Slack button handlers
1.5 - Message routing to author

Run: python scripts/dry-run-phase1.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
BACKEND_PATH = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))


def banner(text: str):
    """Print a banner."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def success(msg: str):
    print(f"  [PASS] {msg}")


def fail(msg: str):
    print(f"  [FAIL] {msg}")


def info(msg: str):
    print(f"  [INFO] {msg}")


def test_phase_1_1_reject_api():
    """Test 1.1: Reject API requires message."""
    banner("Phase 1.1: Reject API Validation")

    from app.models.schemas import ApprovalDecisionRequest

    # Test 1: Rejection with short message should fail
    try:
        ApprovalDecisionRequest(result="rejected", rationale="Short")
        fail("Should have rejected short rationale")
        return False
    except ValueError as e:
        if "10 characters" in str(e):
            success("Short rationale (5 chars) rejected")
        else:
            fail(f"Wrong error: {e}")
            return False

    # Test 2: Rejection with valid message should succeed
    try:
        req = ApprovalDecisionRequest(
            result="rejected",
            rationale="Missing CFO authorization. Please attach approval email.",
            requested_changes="Add CFO email attachment",
        )
        success(f"Valid rejection accepted: {req.result}")
    except ValueError as e:
        fail(f"Valid rejection failed: {e}")
        return False

    # Test 3: Approval can have short message
    try:
        req = ApprovalDecisionRequest(result="approved", rationale="LGTM")
        success(f"Short approval rationale accepted: {req.rationale}")
    except ValueError as e:
        fail(f"Short approval should be allowed: {e}")
        return False

    return True


def test_phase_1_3_slack_endpoint():
    """Test 1.3: Slack interactive endpoint exists."""
    banner("Phase 1.3: Slack Interactive Endpoint")

    from app.routers.slack import router

    # Check routes exist (paths include prefix)
    routes = {r.path for r in router.routes}

    if "/slack/interactivity" in routes:
        success("POST /slack/interactivity route exists")
    else:
        fail(f"Missing /slack/interactivity route (found: {routes})")
        return False

    if "/slack/send-approval" in routes:
        success("POST /slack/send-approval route exists")
    else:
        fail("Missing /slack/send-approval route")
        return False

    if "/slack/events" in routes:
        success("POST /slack/events route exists")
    else:
        fail("Missing /slack/events route")
        return False

    return True


def test_phase_1_4_slack_handlers():
    """Test 1.4: Slack button handlers work."""
    banner("Phase 1.4: Slack Button Handlers")

    from app.services.slack_integration import SlackIntegrationService, SlackConfig

    config = SlackConfig(
        bot_token=None,
        signing_secret="test",
        guardspine_base_url="http://localhost:5173",
    )
    service = SlackIntegrationService(config)

    # Test approval card building
    from app.models.schemas import Approval, RiskTier, ApprovalStatus

    approval = Approval(
        approval_id="test-001",
        bead_id="bead-001",
        artifact_id="contract.pdf",
        risk_tier=RiskTier.L3,
        risk_reasons=["Signature changed"],
        status=ApprovalStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    card = service.build_approval_card(approval)

    # Check approve button
    actions = [b for b in card["blocks"] if b.get("type") == "actions"]
    if actions:
        action_ids = [e["action_id"] for e in actions[0]["elements"]]
        if "approve_test-001" in action_ids:
            success("Approve button with correct action_id")
        else:
            fail("Missing approve button action_id")
            return False

        if "reject_test-001" in action_ids:
            success("Reject button with correct action_id")
        else:
            fail("Missing reject button action_id")
            return False
    else:
        fail("No action buttons in card")
        return False

    # Test rejection modal
    modal = service.build_rejection_modal("test-001", "contract.pdf")
    if modal["callback_id"] == "rejection_modal_test-001":
        success("Rejection modal has correct callback_id")
    else:
        fail("Wrong modal callback_id")
        return False

    # Check min_length on reason input
    inputs = [b for b in modal["blocks"] if b.get("type") == "input"]
    reason_input = [b for b in inputs if b.get("block_id") == "rejection_reason"]
    if reason_input and reason_input[0]["element"].get("min_length") == 10:
        success("Rejection reason has 10 char minimum")
    else:
        fail("Missing min_length on rejection reason")
        return False

    return True


def test_phase_1_5_message_routing():
    """Test 1.5: Message routing to author."""
    banner("Phase 1.5: Message Routing to Author")

    import tempfile
    from pathlib import Path

    from app.models.schemas import Approval, ApprovalDecision, RiskTier, ApprovalStatus
    from app.services.message_routing import (
        MessageRoutingService,
        MessageRoutingConfig,
    )

    # Create temp inbox
    with tempfile.TemporaryDirectory() as tmpdir:
        inbox_dir = Path(tmpdir) / "inbox"
        inbox_dir.mkdir()

        config = MessageRoutingConfig(
            github_token=None,
            slack_webhook=None,
            teams_webhook=None,
            inbox_dir=inbox_dir,
        )
        service = MessageRoutingService(config)

        approval = Approval(
            approval_id="test-001",
            bead_id="bead-001",
            artifact_id="contract.pdf",
            risk_tier=RiskTier.L3,
            status=ApprovalStatus.REJECTED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        decision = ApprovalDecision(
            result="rejected",
            rationale="Missing CFO authorization.",
            decided_by="reviewer@company.com",
            decided_at=datetime.utcnow(),
            requested_changes="Attach CFO approval email",
        )

        results = service.route_decision_to_author(approval, decision)

        # Check inbox routing
        inbox_results = [r for r in results if r.channel == "inbox"]
        if inbox_results and inbox_results[0].success:
            success("Message saved to inbox")
        else:
            fail("Inbox routing failed")
            return False

        # Verify file content
        inbox_files = list(inbox_dir.glob("*.json"))
        if inbox_files:
            with open(inbox_files[0]) as f:
                msg = json.load(f)
            if msg["approval_id"] == "test-001" and msg["decision"] == "rejected":
                success("Inbox message has correct content")
            else:
                fail("Inbox message has wrong content")
                return False
        else:
            fail("No inbox file created")
            return False

    return True


def main():
    """Run all dry-run tests."""
    print("\n" + "=" * 60)
    print("  GUARDSPINE PHASE 1 DRY RUN")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    results = {
        "1.1 Reject API": test_phase_1_1_reject_api(),
        "1.3 Slack Endpoint": test_phase_1_3_slack_endpoint(),
        "1.4 Slack Handlers": test_phase_1_4_slack_handlers(),
        "1.5 Message Routing": test_phase_1_5_message_routing(),
    }

    banner("SUMMARY")
    all_passed = True
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  ALL TESTS PASSED!")
        return 0
    else:
        print("  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
