# GuardSpine Product Suite

Enterprise Content Governance for AI-Powered Organizations

## Overview

GuardSpine is a comprehensive content governance platform that provides graduated risk assessment and approval workflows for various content types. Built on a unified architecture with 11 specialized guard lanes, it ensures your organization maintains security, compliance, and quality standards across all content flows.

## Products

### Core Products (Customer-Facing)

| Product         | Description                            | Key Features                                                            |
| --------------- | -------------------------------------- | ----------------------------------------------------------------------- |
| **Code Guard**  | AI governance for software development | Multi-model audits, L0-L4 risk classification, rubric-based evaluation  |
| **PDF Guard**   | Document verification and compliance   | PII detection, OCR analysis, signature verification, redaction checking |
| **Image Guard** | Visual content safety                  | Content safety classification, face detection, metadata extraction      |
| **Sheet Guard** | Spreadsheet/data validation            | Schema compliance, formula auditing, PII detection, reference checking  |

### Internal Beta (Dogfooding)

These lanes are used internally to automate business operations. Once perfected, they become product offerings:

| Lane           | Purpose                                         |
| -------------- | ----------------------------------------------- |
| Comms Guard    | Internal communications (Slack, Discord, Email) |
| Ticket Guard   | Support ticket triage and routing               |
| Deal Guard     | Sales pipeline gating                           |
| Contract Guard | Legal document review (MSA/DPA)                 |
| Deploy Guard   | Deployment and release gating                   |

### Future Products

| Product        | Description                                |
| -------------- | ------------------------------------------ |
| Data Guard     | Data boundary and privacy validation       |
| Evidence Guard | Audit evidence and compliance verification |

## Risk Tiers (L0-L4)

All guard lanes use a unified 5-tier risk classification:

| Tier | Name          | Auto-Approve | SLA | Description                   |
| ---- | ------------- | ------------ | --- | ----------------------------- |
| L0   | Informational | Yes          | 0h  | Low-impact, auto-approved     |
| L1   | Low Risk      | No           | 4h  | Async review, single approver |
| L2   | Medium Risk   | No           | 8h  | Sync review before action     |
| L3   | High Risk     | No           | 24h | Multi-party approval required |
| L4   | Critical      | No           | 72h | Human-in-the-loop required    |

## Installation

```bash
# From PyPI (when published)
pip install guardspine-product

# From source
git clone https://github.com/DNYoussef/guardspine-product.git
cd guardspine-product
pip install -e .
```

**Note**: This package uses `guardspine-kernel-py` for canonical hashing and bundle sealing.
Evidence bundles produced are v0.2.0 compliant.

## Quick Start

### Code Guard

```python
from guardspine_product.code_guard import get_codeguard_service

service = get_codeguard_service()

# Classify risk level
classification = service.classify(["src/auth/login.py"])
print(f"Risk Level: {classification.level_name}")

# Run audit
result = await service.audit(code_content, "src/auth/login.py")
print(f"Passed: {result.passed}, Findings: {len(result.aggregated_findings)}")
```

### PDF Guard

```python
from guardspine_product.pdf_guard import get_pdfguard_service

service = get_pdfguard_service()

# Analyze and classify
with open("document.pdf", "rb") as f:
    result = await service.analyze_and_classify(f.read(), "document.pdf")

print(f"Risk Level: {result['classification']['level_name']}")
print(f"PII Types: {result['classification']['pii_types']}")
```

### Image Guard

```python
from guardspine_product.image_guard import get_imageguard_service

service = get_imageguard_service()

# Analyze image
with open("image.png", "rb") as f:
    result = await service.analyze_and_classify(f.read(), "image.png")

print(f"Contains Faces: {result['analysis']['faces_detected']}")
print(f"Safety Flags: {result['analysis']['safety_flags']}")
```

### Sheet Guard

```python
from guardspine_product.sheet_guard import get_sheetguard_service

service = get_sheetguard_service()

# Analyze spreadsheet
sheet_data = {
    "columns": ["Name", "Email", "SSN", "Salary"],
    "row_count": 1500,
    "formulas": [],
    "external_refs": [],
    "has_macros": False,
}

result = await service.analyze_and_classify(sheet_data, "employees.xlsx")
print(f"PII Columns: {result['classification']['pii_columns']}")
print(f"Requires Encryption: {result['classification']['requires_encryption']}")
```

## Architecture

```
guardspine-product/
    common/                 # Shared components
        base_guard_lane.py  # Abstract base class for all lanes
        risk_tiers.py       # L0-L4 tier definitions
        evidence.py         # Evidence bundle management (v0.2.0)
    code_guard/            # Code Guard product
    pdf_guard/             # PDF Guard product
    image_guard/           # Image Guard product
    sheet_guard/           # Sheet Guard product
    adapters/              # File format adapters (PDF, XLSX, images)
    docs/                  # Documentation
    tests/                 # Test suite
```

## Evidence Bundles

All guard lanes emit v0.2.0 evidence bundles that can be verified with `guardspine-verify`:

```bash
guardspine-verify evidence-bundle.json
```

Bundles include:

- Canonical hash chain (via `guardspine-kernel-py`)
- Immutability proof with root hash
- Optional Ed25519 signatures

## Creating Custom Guard Lanes

```python
from guardspine_product.common import (
    BaseGuardLane,
    GuardLaneType,
    TriggerType,
    GuardEvent,
    LaneEvaluationResult,
    RiskTier,
    ApprovalSet,
    register_lane,
)

@register_lane
class AudioGuard(BaseGuardLane):
    @property
    def lane_name(self) -> str:
        return "AUDIO_GUARD"

    @property
    def lane_type(self) -> GuardLaneType:
        return GuardLaneType.AUDIO_GUARD  # Add to enum first

    @property
    def supported_triggers(self) -> set:
        return {TriggerType.AUDIO_UPLOADED}

    async def evaluate_event(self, event: GuardEvent) -> LaneEvaluationResult:
        # Your evaluation logic here
        pass
```

## Compliance Frameworks

GuardSpine helps maintain compliance with:

- **GDPR** - EU personal data protection
- **HIPAA** - Healthcare data privacy
- **SOC 2** - Security controls
- **PCI-DSS** - Payment card data
- **ISO 27001** - Information security

## Eval Harness

The `eval/` directory contains a self-contained evaluation harness for measuring CodeGuard detection accuracy against known-vulnerable and known-safe code samples.

### Quick Start

```bash
cd guardspine-product

# Dry run (rubric-only, no API calls)
python eval/run_eval.py --dry-run

# L1 eval (single model)
python eval/run_eval.py --l1

# L3 eval (3-model adversarial)
python eval/run_eval.py --l3

# Single sample
python eval/run_eval.py --l1 --sample sqli_01_raw_format.py
```

### Setup

1. Copy your OpenRouter API key into `eval/.codeguard/.secrets.toml`:
   ```toml
   openrouter_api_key = "sk-or-v1-..."
   ```
2. Configure models in `eval/codeguard.toml` (defaults to Claude Opus 4.6 + GPT-5.2 Codex + Gemini 3 Pro).

### Sample Results (L1 - Claude Opus 4.6)

```
CodeGuard Eval Harness v1.0
============================================================
Backend:  openrouter
Models:   ['anthropic/claude-opus-4.6', 'openai/gpt-5.2-codex', 'google/gemini-3-pro-preview']
Rubrics:  5 rules loaded
Samples:  15
============================================================

clean\general_safe_utility.py       merge                  [PASS]
clean\secrets_safe_env.py           merge                  [PASS]
clean\sqli_safe_parameterized.py    merge                  [PASS]
clean\xss_safe_escaped.py           merge                  [PASS]
vulnerable\secrets_01_hardcoded.py  merge-with-conditions  [DETECTED]
vulnerable\sqli_01_raw_format.py    block                  [PASS]
vulnerable\sqli_02_fstring.py       merge-with-conditions  [DETECTED]
vulnerable\sqli_03_concat.py        merge-with-conditions  [DETECTED]
vulnerable\sqli_04_multiline.py     merge-with-conditions  [DETECTED]
vulnerable\sqli_05_orm_raw.py       block                  [PASS]
vulnerable\xss_01_direct.py         merge-with-conditions  [DETECTED]
vulnerable\xss_02_template.py       merge                  [MISS]
vulnerable\xss_03_innerhtml.py      merge-with-conditions  [DETECTED]
vulnerable\xss_04_stored.py         merge-with-conditions  [DETECTED]
vulnerable\xss_05_jsonp.py          merge-with-conditions  [DETECTED]

============================================================
EVAL SUMMARY
============================================================
Strict accuracy:    6/15 (40.0%) - decision == expected
Detection accuracy: 14/15 (93.3%) - vuln found (block OR conditions)
Total tokens:       8,607
```

**Key insight**: The gap between strict (40%) and detection (93.3%) accuracy reflects the Decision Engine's design -- LLM-generated findings are marked `provable=False` and cannot hard-block merges. Only deterministic rubric matches (regex) produce `provable=True` findings that trigger hard blocks. This is intentional: model opinions flag issues for human review, but only provable detections can autonomously block a merge.

### Test Matrix

| Category                  | Samples                                                          | Coverage             |
| ------------------------- | ---------------------------------------------------------------- | -------------------- |
| SQL Injection             | 5 variants (format string, f-string, concat, multiline, ORM raw) | OWASP A03            |
| Cross-Site Scripting      | 5 variants (reflected, template, innerHTML, stored, JSONP)       | OWASP A07            |
| Hardcoded Secrets         | 1 (Stripe keys)                                                  | OWASP A02            |
| Clean (negative controls) | 4 (parameterized SQL, escaped XSS, env-based secrets, utility)   | False positive check |

## License

Commercial License - See LICENSE for terms.

## Support

For enterprise support, contact: support@guardspine.ai
