#!/usr/bin/env python3
"""
Phase 4 Dry Run Script

Manually verifies all Phase 4 functionality:
3.9 - Board Packet Workflow (Multi-Artifact)

Run: python scripts/dry-run-phase4.py
"""

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


def test_board_packet_service():
    """Test Board Packet Service."""
    banner("Phase 4: Board Packet Service")

    try:
        from app.services.board_packet_service import BoardPacketService

        service = BoardPacketService()

        # Test 1: Service instantiation
        success("BoardPacketService instantiated")

        # Test 2: Create packet
        packet = service.create_packet(
            title="Dry Run Test Packet",
            description="Testing Phase 4 functionality",
            created_by="dryrun@test.com",
            target_meeting="2026-03-01",
        )
        if packet and "packet_id" in packet:
            success(f"Packet created: {packet['packet_id']}")
        else:
            fail("Failed to create packet")
            return False

        packet_id = packet["packet_id"]

        # Test 3: Add artifacts
        artifact1 = service.add_artifact(
            packet_id=packet_id,
            artifact_type="pdf_document",
            name="Board Presentation",
            risk_tier="L2",
        )
        artifact2 = service.add_artifact(
            packet_id=packet_id,
            artifact_type="spreadsheet",
            name="KPI Dashboard",
            risk_tier="L3",
        )
        artifact3 = service.add_artifact(
            packet_id=packet_id,
            artifact_type="governance_change",
            name="Policy Amendment",
            risk_tier="L4",
        )
        if artifact1 and artifact2 and artifact3:
            success("Added 3 artifacts (PDF L2, Spreadsheet L3, Governance L4)")
        else:
            fail("Failed to add artifacts")
            return False

        # Test 4: Submit for markers
        submitted = service.submit_for_markers(packet_id)
        if submitted and submitted["status"] == "pending_markers":
            success("Submitted for marker approvals")
        else:
            fail("Failed to submit for markers")
            return False

        # Test 5: Get stats
        stats = service.get_stats()
        if "total_packets" in stats and "by_status" in stats:
            success(f"Stats: {stats['total_packets']} packets, {stats['total_artifacts']} artifacts")
        else:
            fail("Failed to get stats")
            return False

    except Exception as e:
        fail(f"Board Packet Service error: {e}")
        return False

    return True


def test_phase4_multi_artifact_workflow():
    """Test Phase 4 multi-artifact workflow features."""
    banner("Phase 4: Multi-Artifact Workflow")

    try:
        from app.services.board_packet_service import BoardPacketService

        service = BoardPacketService()

        # Create test packet
        packet = service.create_packet(
            title="Multi-Artifact Test",
            description="Testing Phase 4 workflow",
            created_by="test@test.com",
        )
        packet_id = packet["packet_id"]

        # Add multiple artifact types
        service.add_artifact(packet_id, "pdf_document", "Annual Report", risk_tier="L2")
        service.add_artifact(packet_id, "spreadsheet", "Budget Model", risk_tier="L3")
        service.add_artifact(packet_id, "governance_change", "Rubric Update", risk_tier="L4")
        success("Added multi-artifact mix (PDF, Sheet, Governance)")

        # Test 1: Link to Beads
        link_result = service.link_to_beads(packet_id, "bead_test_12345")
        if link_result and "beads_task_id" in link_result:
            success(f"Linked to Beads task: {link_result['beads_task_id']}")
        else:
            fail("Failed to link to Beads")
            return False

        # Test 2: Trigger audit
        audit_result = service.trigger_audit(packet_id)
        if audit_result:
            info(f"Artifacts audited: {audit_result['artifacts_audited']}")
            info(f"L3/L4 items for approval: {audit_result['approval_queue_count']}")

            # Check postcards generated
            all_have_postcards = all(
                r["postcard_generated"] for r in audit_result["audit_results"]
            )
            if all_have_postcards:
                success("Audit complete - postcards generated for all artifacts")
            else:
                fail("Some artifacts missing postcards")
                return False
        else:
            fail("Failed to trigger audit")
            return False

        # Test 3: Check L3/L4 detection
        l3_l4_count = len(audit_result["l3_l4_items"])
        if l3_l4_count == 2:  # L3 spreadsheet + L4 governance
            success(f"Correctly detected {l3_l4_count} L3/L4 items for approval queue")
        else:
            fail(f"Expected 2 L3/L4 items, got {l3_l4_count}")
            return False

        # Test 4: Risk drivers detection
        for result in audit_result["audit_results"]:
            if result["artifact_type"] == "spreadsheet":
                drivers = result["risk_drivers"]
                if drivers and drivers[0]["category"] == "formula_change":
                    success("Risk drivers detected (formula_change for spreadsheet)")
                    break
        else:
            fail("Failed to detect risk drivers")
            return False

    except Exception as e:
        fail(f"Multi-artifact workflow error: {e}")
        return False

    return True


def test_ready_for_board():
    """Test ready-for-board gating."""
    banner("Phase 4: Ready-for-Board Gating")

    try:
        from app.services.board_packet_service import BoardPacketService

        service = BoardPacketService()

        # Test 1: Draft packet should not be ready
        packet = service.create_packet(
            title="Ready Test",
            description="Test",
            created_by="test@test.com",
        )
        result = service.check_ready_for_board(packet["packet_id"])
        if not result["ready"]:
            success("Draft packet correctly blocked from ready-for-board")
        else:
            fail("Draft packet should not be ready")
            return False

        # Test 2: Approved packet should be ready
        # Use demo approved packet
        packets = service.list_packets(status="approved")
        if packets:
            approved_id = packets[0]["packet_id"]
            result = service.check_ready_for_board(approved_id)
            if result["ready"]:
                success("Approved packet correctly marked as ready-for-board")
            else:
                fail(f"Approved packet should be ready: {result.get('reason')}")
                return False
        else:
            info("No approved demo packets to test")

    except Exception as e:
        fail(f"Ready-for-board error: {e}")
        return False

    return True


def test_evidence_pack_export():
    """Test evidence pack export."""
    banner("Phase 4: Evidence Pack Export")

    try:
        from app.services.board_packet_service import BoardPacketService

        service = BoardPacketService()

        # Use demo approved packet
        packets = service.list_packets(status="approved")
        if not packets:
            fail("No approved packets to export")
            return False

        packet_id = packets[0]["packet_id"]
        evidence_pack = service.export_evidence_pack(packet_id)

        if not evidence_pack:
            fail("Failed to generate evidence pack")
            return False

        # Test 1: Has pack_id and hash
        if "pack_id" in evidence_pack and "pack_hash" in evidence_pack:
            success(f"Evidence pack generated: {evidence_pack['pack_id']}")
            info(f"Pack hash: {evidence_pack['pack_hash'][:32]}...")
        else:
            fail("Missing pack_id or pack_hash")
            return False

        # Test 2: Has index structure
        index = evidence_pack.get("index", {})
        if all(k in index for k in ["packet_summary", "artifacts", "markers", "verification"]):
            success("Index structure complete")
        else:
            fail("Incomplete index structure")
            return False

        # Test 3: Has verification info
        verify_info = evidence_pack.get("verification_info", {})
        if verify_info.get("offline_verifiable"):
            success("Offline verification enabled")
        else:
            fail("Offline verification not enabled")
            return False

        # Test 4: Artifact details
        artifacts_detail = evidence_pack.get("artifacts_detail", [])
        info(f"Artifacts in pack: {len(artifacts_detail)}")
        for artifact in artifacts_detail:
            if "postcard_ref" in artifact and "diff_ref" in artifact:
                continue
            else:
                fail("Artifact missing postcard_ref or diff_ref")
                return False
        success("All artifacts have postcard and diff references")

    except Exception as e:
        fail(f"Evidence pack export error: {e}")
        return False

    return True


def test_timeline():
    """Test timeline generation."""
    banner("Phase 4: Timeline Generation")

    try:
        from app.services.board_packet_service import BoardPacketService

        service = BoardPacketService()

        # Use demo approved packet (has activity)
        packets = service.list_packets(status="approved")
        if not packets:
            fail("No approved packets to get timeline")
            return False

        packet_id = packets[0]["packet_id"]
        timeline = service.get_timeline(packet_id)

        if not timeline:
            fail("Failed to generate timeline")
            return False

        # Test 1: Has events
        info(f"Timeline events: {len(timeline)}")

        # Test 2: Has packet_created event
        event_types = [e["event"] for e in timeline]
        if "packet_created" in event_types:
            success("Timeline includes packet_created event")
        else:
            fail("Missing packet_created event")
            return False

        # Test 3: Has marker events (for approved packet)
        marker_events = [e for e in timeline if "marker" in e["event"]]
        if marker_events:
            success(f"Timeline includes {len(marker_events)} marker decision events")
        else:
            info("No marker events in timeline")

        # Test 4: Events are sorted
        timestamps = [e["timestamp"] for e in timeline if e["timestamp"]]
        if timestamps == sorted(timestamps):
            success("Timeline events sorted chronologically")
        else:
            fail("Timeline events not sorted")
            return False

    except Exception as e:
        fail(f"Timeline error: {e}")
        return False

    return True


def test_board_packet_api_routes():
    """Test Board Packet API routes exist."""
    banner("Phase 4: Board Packet API Routes")

    try:
        from app.routers.board_packets import router

        routes = {r.path for r in router.routes}

        # Core routes
        if any("board-packets" in r and r.endswith("") for r in routes):
            success("GET/POST /board-packets route exists")
        else:
            fail("Missing /board-packets route")
            return False

        if any("stats" in r for r in routes):
            success("GET /board-packets/stats route exists")
        else:
            fail("Missing /board-packets/stats route")
            return False

        # Phase 4 specific routes
        if any("trigger-audit" in r for r in routes):
            success("POST /board-packets/{id}/trigger-audit route exists")
        else:
            fail("Missing trigger-audit route")
            return False

        if any("ready-for-board" in r for r in routes):
            success("GET /board-packets/{id}/ready-for-board route exists")
        else:
            fail("Missing ready-for-board route")
            return False

        if any("export" in r for r in routes):
            success("GET /board-packets/{id}/export route exists")
        else:
            fail("Missing export route")
            return False

        if any("timeline" in r for r in routes):
            success("GET /board-packets/{id}/timeline route exists")
        else:
            fail("Missing timeline route")
            return False

        if any("link-beads" in r for r in routes):
            success("POST /board-packets/{id}/link-beads route exists")
        else:
            fail("Missing link-beads route")
            return False

    except ImportError as e:
        fail(f"Could not import board_packets router: {e}")
        return False
    except Exception as e:
        fail(f"Board Packet API routes test failed: {e}")
        return False

    return True


def main():
    """Run all dry-run tests."""
    print("\n" + "=" * 60)
    print("  GUARDSPINE PHASE 4 DRY RUN")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    results = {
        "4.x Board Packet Service": test_board_packet_service(),
        "4.x Multi-Artifact Workflow": test_phase4_multi_artifact_workflow(),
        "4.x Ready-for-Board Gating": test_ready_for_board(),
        "4.x Evidence Pack Export": test_evidence_pack_export(),
        "4.x Timeline Generation": test_timeline(),
        "4.x Board Packet API Routes": test_board_packet_api_routes(),
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
