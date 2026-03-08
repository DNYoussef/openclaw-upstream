#!/usr/bin/env python3
"""
Phase 2 Dry Run Script

Manually verifies all Phase 2 functionality:
2.1 - Postcard schema normalization across all 4 lanes
2.2 - Auditor pack export endpoint
2.3 - Search filters (risk, type, date)

Run: python scripts/dry-run-phase2.py
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


def test_phase_2_1_postcard_schema():
    """Test 2.1: Postcard schema normalization."""
    banner("Phase 2.1: Postcard Schema Normalization")

    from app.models.schemas import (
        DiffPostcard,
        ArtifactKind,
        RiskTier,
        RiskDriver,
        CodeChange,
        PDFChange,
        SheetChange,
        ImageChange,
        AISuggestion,
    )

    # Test 1: Code lane postcard
    try:
        postcard = DiffPostcard(
            artifact_id="auth/login.py",
            artifact_type=ArtifactKind.CODE,
            version_from="v1.0",
            version_to="v1.1",
            summary="Auth changes",
            risk_tier=RiskTier.L3,
            code_changes=[
                CodeChange(
                    file_path="auth/login.py",
                    line_start=45,
                    line_end=67,
                    change_type="modified",
                )
            ],
        )
        success(f"Code lane postcard: {postcard.artifact_type.value}")
    except Exception as e:
        fail(f"Code lane postcard failed: {e}")
        return False

    # Test 2: PDF lane postcard
    try:
        postcard = DiffPostcard(
            artifact_id="contract.pdf",
            artifact_type=ArtifactKind.PDF,
            version_from="v1",
            version_to="v2",
            summary="Clause changed",
            risk_tier=RiskTier.L4,
            pdf_changes=[
                PDFChange(
                    page_number=3,
                    change_type="signature_changed",
                )
            ],
        )
        success(f"PDF lane postcard: {postcard.artifact_type.value}")
    except Exception as e:
        fail(f"PDF lane postcard failed: {e}")
        return False

    # Test 3: XLSX lane postcard
    try:
        postcard = DiffPostcard(
            artifact_id="financials.xlsx",
            artifact_type=ArtifactKind.XLSX,
            version_from="v1",
            version_to="v2",
            summary="Formula changed",
            risk_tier=RiskTier.L3,
            sheet_changes=[
                SheetChange(
                    sheet_name="Revenue",
                    cell_range="C10:C50",
                    change_type="formula_changed",
                )
            ],
        )
        success(f"XLSX lane postcard: {postcard.artifact_type.value}")
    except Exception as e:
        fail(f"XLSX lane postcard failed: {e}")
        return False

    # Test 4: Image lane postcard
    try:
        postcard = DiffPostcard(
            artifact_id="slide12.png",
            artifact_type=ArtifactKind.IMAGE,
            version_from="v1",
            version_to="v2",
            summary="QR code added",
            risk_tier=RiskTier.L3,
            image_changes=[
                ImageChange(
                    region="bottom-right",
                    change_type="object_added",
                    pixel_diff_percent=2.5,
                )
            ],
        )
        success(f"Image lane postcard: {postcard.artifact_type.value}")
    except Exception as e:
        fail(f"Image lane postcard failed: {e}")
        return False

    # Test 5: Risk drivers
    try:
        postcard = DiffPostcard(
            artifact_id="test",
            artifact_type=ArtifactKind.CODE,
            version_from="v1",
            version_to="v2",
            summary="Test",
            risk_tier=RiskTier.L3,
            risk_drivers=[
                RiskDriver(category="auth", description="Auth changed", weight=5),
                RiskDriver(category="pii", description="PII exposed", weight=8),
            ],
        )
        success(f"Risk drivers: {len(postcard.risk_drivers)} drivers")
    except Exception as e:
        fail(f"Risk drivers failed: {e}")
        return False

    # Test 6: AI suggestions
    try:
        postcard = DiffPostcard(
            artifact_id="test",
            artifact_type=ArtifactKind.CODE,
            version_from="v1",
            version_to="v2",
            summary="Test",
            risk_tier=RiskTier.L2,
            ai_suggestions=[
                AISuggestion(
                    suggestion_id="sug-001",
                    suggestion_type="review_focus",
                    content="Focus on auth changes",
                    confidence=0.85,
                ),
            ],
        )
        success(f"AI suggestions: {len(postcard.ai_suggestions)} suggestions")
    except Exception as e:
        fail(f"AI suggestions failed: {e}")
        return False

    return True


def test_phase_2_2_auditor_pack_export():
    """Test 2.2: Auditor pack export."""
    banner("Phase 2.2: Auditor Pack Export")

    from app.models.schemas import AuditorPackRequest, AuditorPackSummary, RiskTier

    # Test 1: Auditor pack request
    try:
        request = AuditorPackRequest(
            from_date=datetime(2025, 1, 1),
            to_date=datetime(2025, 1, 31),
            risk_tiers=[RiskTier.L3, RiskTier.L4],
        )
        success(f"Auditor pack request: {request.from_date} to {request.to_date}")
    except Exception as e:
        fail(f"Auditor pack request failed: {e}")
        return False

    # Test 2: Auditor pack summary
    try:
        from datetime import timedelta
        summary = AuditorPackSummary(
            pack_id="pack-test123",
            date_range="2025-01-01 to 2025-01-31",
            bundle_count=42,
            total_size_bytes=2100000,
            risk_breakdown={"L0": 10, "L1": 15, "L2": 8, "L3": 7, "L4": 2},
            download_url="/api/v1/bundles/export/pack-test123/download",
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        success(f"Auditor pack summary: {summary.bundle_count} bundles")
    except Exception as e:
        fail(f"Auditor pack summary failed: {e}")
        return False

    # Test 3: Check export endpoint exists
    try:
        from app.routers.bundles import router
        routes = {r.path for r in router.routes}

        if "/bundles/export" in routes:
            success("GET /bundles/export route exists")
        else:
            fail(f"Missing /bundles/export route (found: {routes})")
            return False

        if "/bundles/export/{pack_id}/download" in routes:
            success("GET /bundles/export/{pack_id}/download route exists")
        else:
            fail("Missing /bundles/export/{pack_id}/download route")
            return False

    except Exception as e:
        fail(f"Export endpoint check failed: {e}")
        return False

    return True


def test_phase_2_3_search_filters():
    """Test 2.3: Search filters."""
    banner("Phase 2.3: Search Filters")

    # Test 1: Check search endpoint exists
    try:
        from app.routers.search import router
        routes = {r.path for r in router.routes}

        if "/search" in routes:
            success("GET /search route exists")
        else:
            fail(f"Missing /search route (found: {routes})")
            return False

    except Exception as e:
        fail(f"Search endpoint check failed: {e}")
        return False

    # Test 2: Check search service supports filters
    try:
        from app.services.search_service import SearchFilter, EntityType

        filters = SearchFilter(
            entity_types=[EntityType.APPROVAL],
            risk_tiers=["L3", "L4"],
            statuses=["pending"],
        )
        success(f"SearchFilter with risk_tiers: {filters.risk_tiers}")
    except Exception as e:
        fail(f"SearchFilter failed: {e}")
        return False

    # Test 3: Check advanced search endpoint
    try:
        from app.routers.search import router
        routes = {r.path for r in router.routes}

        if "/search/advanced" in routes:
            success("POST /search/advanced route exists")
        else:
            fail("Missing /search/advanced route")
            return False

    except Exception as e:
        fail(f"Advanced search check failed: {e}")
        return False

    # Test 4: Check filters endpoint
    try:
        from app.routers.search import router
        routes = {r.path for r in router.routes}

        if "/search/filters" in routes:
            success("GET /search/filters route exists")
        else:
            fail("Missing /search/filters route")
            return False

    except Exception as e:
        fail(f"Filters endpoint check failed: {e}")
        return False

    return True


def test_postcard_endpoint():
    """Test postcard endpoint exists."""
    banner("Phase 2: Postcard Endpoint")

    try:
        from app.routers.artifacts import router
        routes = {r.path for r in router.routes}

        # Note: FastAPI may show path with parameter placeholder
        postcard_routes = [r for r in routes if "postcard" in r.lower()]
        if postcard_routes:
            success(f"Postcard endpoint found: {postcard_routes[0]}")
        else:
            fail(f"Missing postcard route (found: {routes})")
            return False

    except Exception as e:
        fail(f"Postcard endpoint check failed: {e}")
        return False

    return True


def main():
    """Run all dry-run tests."""
    print("\n" + "=" * 60)
    print("  GUARDSPINE PHASE 2 DRY RUN")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    results = {
        "2.1 Postcard Schema": test_phase_2_1_postcard_schema(),
        "2.2 Auditor Pack Export": test_phase_2_2_auditor_pack_export(),
        "2.3 Search Filters": test_phase_2_3_search_filters(),
        "2.x Postcard Endpoint": test_postcard_endpoint(),
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
