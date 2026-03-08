#!/usr/bin/env python3
"""
Phase 3 Dry Run Script

Manually verifies all Phase 3 functionality:
3.7 - nomotic.yaml implementation
3.8 - Governed adaptation workflow

Run: python scripts/dry-run-phase3.py
"""

import sys
import yaml
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


def test_phase_3_7_nomotic_core_yaml():
    """Test 3.7: nomotic.yaml implementation."""
    banner("Phase 3.7: nomotic.yaml Implementation")

    rubrics_path = Path(__file__).parent.parent / "rubrics" / "nomotic.yaml"

    # Test 1: File exists
    if rubrics_path.exists():
        success(f"nomotic.yaml exists at {rubrics_path}")
    else:
        fail(f"nomotic.yaml not found at {rubrics_path}")
        return False

    # Test 2: Valid YAML
    try:
        with open(rubrics_path, "r") as f:
            data = yaml.safe_load(f)
        success("nomotic.yaml is valid YAML")
    except Exception as e:
        fail(f"Invalid YAML: {e}")
        return False

    # Test 3: Has bundle_extensions
    if "bundle_extensions" in data:
        extensions = data["bundle_extensions"]
        extension_names = [e["name"] for e in extensions]
        if "authority_basis" in extension_names:
            success("bundle_extension: authority_basis defined")
        else:
            fail("Missing bundle_extension: authority_basis")
            return False

        if "constraints_applied" in extension_names:
            success("bundle_extension: constraints_applied defined")
        else:
            fail("Missing bundle_extension: constraints_applied")
            return False

        if "interrupts_triggered" in extension_names:
            success("bundle_extension: interrupts_triggered defined")
        else:
            fail("Missing bundle_extension: interrupts_triggered")
            return False
    else:
        fail("Missing bundle_extensions section")
        return False

    # Test 4: Has required rules
    if "rules" in data:
        rule_ids = [r["id"] for r in data["rules"]]

        if "NOM-AUTH-001" in rule_ids:
            success("Rule NOM-AUTH-001 (explicit_authority) defined")
        else:
            fail("Missing rule NOM-AUTH-001")
            return False

        if "NOM-INT-001" in rule_ids:
            rule = next(r for r in data["rules"] if r["id"] == "NOM-INT-001")
            triggers = [t["condition"] for t in rule.get("triggers", [])]
            info(f"NOM-INT-001 triggers: {len(triggers)} conditions")
            if "external_link_added" in triggers and "signature_changed" in triggers:
                success("Rule NOM-INT-001 (interrupt_rights) with required triggers")
            else:
                fail("NOM-INT-001 missing required triggers")
                return False
        else:
            fail("Missing rule NOM-INT-001")
            return False

        if "NOM-GOV-001" in rule_ids:
            rule = next(r for r in data["rules"] if r["id"] == "NOM-GOV-001")
            if rule.get("risk_tier") == "L4":
                success("Rule NOM-GOV-001 (governed_adaptation) with L4 risk tier")
            else:
                fail("NOM-GOV-001 should be L4")
                return False
        else:
            fail("Missing rule NOM-GOV-001")
            return False
    else:
        fail("Missing rules section")
        return False

    return True


def test_phase_3_7_nomotic_schemas():
    """Test 3.7: Nomotic extension schemas."""
    banner("Phase 3.7: Nomotic Extension Schemas")

    # Test 1: AuthorityBasis schema
    try:
        from app.models.evidence_schemas import AuthorityBasis

        authority = AuthorityBasis(
            approver_id="user-123",
            approver_role="security_reviewer",
            authority_source="codeowners",
        )
        success(f"AuthorityBasis schema: {authority.approver_role}")
    except Exception as e:
        fail(f"AuthorityBasis schema failed: {e}")
        return False

    # Test 2: ConstraintApplied schema
    try:
        from app.models.evidence_schemas import ConstraintApplied

        constraint = ConstraintApplied(
            constraint_id="NOM-AUTH-001",
            constraint_name="explicit_authority",
            constraint_source="nomotic",
            triggered=True,
            result="pass",
        )
        success(f"ConstraintApplied schema: {constraint.constraint_id}")
    except Exception as e:
        fail(f"ConstraintApplied schema failed: {e}")
        return False

    # Test 3: InterruptTriggered schema
    try:
        from app.models.evidence_schemas import InterruptTriggered

        interrupt = InterruptTriggered(
            interrupt_id="int-001",
            interrupt_type="mandatory_review",
            trigger_condition="external_link_added",
        )
        success(f"InterruptTriggered schema: {interrupt.interrupt_type}")
    except Exception as e:
        fail(f"InterruptTriggered schema failed: {e}")
        return False

    # Test 4: NomoticExtensions schema
    try:
        from app.models.evidence_schemas import NomoticExtensions

        extensions = NomoticExtensions(
            authority_basis=authority,
            constraints_applied=[constraint],
            interrupts_triggered=[interrupt],
        )
        success(f"NomoticExtensions schema: {extensions.rubric_version}")
    except Exception as e:
        fail(f"NomoticExtensions schema failed: {e}")
        return False

    # Test 5: EvidenceBundle with nomotic_extensions
    try:
        from app.models.evidence_schemas import (
            EvidenceBundle,
            EvidenceScope,
            RetentionConfig,
            RetentionPolicy,
        )
        from app.models.schemas import RiskTier

        bundle = EvidenceBundle(
            bundle_id="bun-test",
            bead_id="bead-test",
            artifact_id="rubrics/test.yaml",
            from_version_id="v1",
            to_version_id="v2",
            risk_tier=RiskTier.L4,
            scope=EvidenceScope(
                assertion_type="change_approved",
                assertion_text="Test",
                artifact_id="rubrics/test.yaml",
                version_from="v1",
                version_to="v2",
                risk_tier_assessed=RiskTier.L4,
            ),
            retention=RetentionConfig.from_policy(RetentionPolicy.STANDARD),
            nomotic_extensions=extensions,
        )
        success(f"EvidenceBundle with nomotic_extensions: {bundle.bundle_id}")
    except Exception as e:
        fail(f"EvidenceBundle with nomotic_extensions failed: {e}")
        return False

    return True


def test_phase_3_8_governed_adaptation():
    """Test 3.8: Governed adaptation workflow."""
    banner("Phase 3.8: Governed Adaptation Workflow")

    try:
        from app.services.governance_service import GovernanceService, GOVERNANCE_APPROVERS

        service = GovernanceService()

        # Test 1: Check governed adaptation for rubrics
        result = service.check_governed_adaptation("rubrics/security.yaml")
        if result["requires_governance"] and result["risk_tier"] == "L4":
            success("Rubric changes require L4 governance")
        else:
            fail("Rubric changes should require L4 governance")
            return False

        # Test 2: Check governed adaptation for policies
        result = service.check_governed_adaptation("policies/pci-dss.yaml")
        if result["requires_governance"]:
            success("Policy changes require governance")
        else:
            fail("Policy changes should require governance")
            return False

        # Test 3: Non-governed artifacts
        result = service.check_governed_adaptation("src/app.py")
        if not result["requires_governance"]:
            success("Regular code does not require governed adaptation")
        else:
            fail("Regular code should not require governed adaptation")
            return False

        # Test 4: GOVERNANCE_APPROVERS defined
        if "rubric" in GOVERNANCE_APPROVERS:
            approvers = GOVERNANCE_APPROVERS["rubric"]
            success(f"Rubric approvers defined: {len(approvers)} roles")
        else:
            fail("Missing rubric approvers definition")
            return False

        # Test 5: Build Nomotic extensions
        extensions = service.build_nomotic_extensions(
            request_id="gapr_demo002",
            approver_id="test-user",
            approver_role="governance_owner",
        )
        if extensions and "authority_basis" in extensions:
            success("build_nomotic_extensions returns authority_basis")
        else:
            fail("build_nomotic_extensions failed")
            return False

    except Exception as e:
        fail(f"Governed adaptation test failed: {e}")
        return False

    return True


def test_governance_api_routes():
    """Test governance API routes exist."""
    banner("Phase 3: Governance API Routes")

    try:
        from app.routers.governance import router

        routes = {r.path for r in router.routes}

        # Routes include the full prefix /api/v1/governance/
        if any("changes" in r for r in routes):
            success("GET /governance/changes route exists")
        else:
            fail(f"Missing /governance/changes route (found: {routes})")
            return False

        if any("requests" in r and "{request_id}" not in r for r in routes):
            success("GET /governance/requests route exists")
        else:
            fail("Missing /governance/requests route")
            return False

        if any("stats" in r for r in routes):
            success("GET /governance/stats route exists")
        else:
            fail("Missing /governance/stats route")
            return False

        if any("approve" in r for r in routes):
            success("POST /governance/requests/{id}/approve route exists")
        else:
            fail("Missing /governance/requests/{id}/approve route")
            return False

        if any("reject" in r for r in routes):
            success("POST /governance/requests/{id}/reject route exists")
        else:
            fail("Missing /governance/requests/{id}/reject route")
            return False

    except ImportError as e:
        fail(f"Could not import governance router: {e}")
        return False
    except Exception as e:
        fail(f"Governance API routes test failed: {e}")
        return False

    return True


def main():
    """Run all dry-run tests."""
    print("\n" + "=" * 60)
    print("  GUARDSPINE PHASE 3 DRY RUN")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    results = {
        "3.7 nomotic.yaml": test_phase_3_7_nomotic_core_yaml(),
        "3.7 Nomotic Schemas": test_phase_3_7_nomotic_schemas(),
        "3.8 Governed Adaptation": test_phase_3_8_governed_adaptation(),
        "3.x Governance API Routes": test_governance_api_routes(),
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
