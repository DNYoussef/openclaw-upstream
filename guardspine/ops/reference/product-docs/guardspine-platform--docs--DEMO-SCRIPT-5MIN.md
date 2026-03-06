# GuardSpine 5-Minute Demo Script

> **Pitch**: "You don't need to trust me. Verify the bundle yourself."

## Setup (Before Demo)

- Terminal with `guardspine-verify` installed
- Browser with GuardSpine UI open (or screenshots)
- Sample bundle files ready:
  - `code-diff-bundle.json`
  - `pdf-diff-bundle.json`
  - `xlsx-diff-bundle.json`

---

## INTRO (30 seconds)

**Say**:

> "AI is changing how work gets done. But when an AI helps draft a contract or modify financial data, how do you prove what changed, who approved it, and that nothing was tampered with?
>
> GuardSpine creates verifiable evidence bundles for every change. And you don't need to trust us - you can verify them yourself."

---

## DEMO PART 1: The Problem (60 seconds)

**Show**: A PDF contract or spreadsheet

**Say**:

> "Here's a typical scenario. Someone updates a vendor contract - maybe an AI helped draft the changes.
>
> Questions your auditor will ask:
>
> - What exactly changed?
> - Who reviewed it?
> - Was this the same version that was approved?
>
> Without proper evidence, you're relying on trust. With GuardSpine, you get cryptographic proof."

---

## DEMO PART 2: The Diff Postcard (90 seconds)

**Show**: Diff Postcard UI (screenshot or live)

**Say**:

> "When a document changes, GuardSpine generates a 'Diff Postcard' - a visual summary showing exactly what changed.
>
> [Point to UI elements]
>
> - Left side: before
> - Right side: after
> - Red: removed
> - Green: added
>
> The AI doesn't decide - it summarizes. See here: 'AI suggests this is a payment term change from 30 to 45 days.' The human approver makes the decision.
>
> Approvers can review and sign off in under 10 seconds for simple changes."

---

## DEMO PART 3: The Evidence Bundle (90 seconds)

**Show**: Terminal

**Say**:

> "Every approval creates an evidence bundle - a cryptographically sealed package containing:
>
> - The exact diff
> - Who approved it
> - When they approved
> - What policies were checked
>
> Let me show you one."

**Run**:

```bash
cat code-diff-bundle.json | head -50
```

**Say**:

> "This is a real bundle. It has:
>
> - The diff with line-by-line changes
> - Policy evaluation results
> - The approver's signature
> - A hash chain proving the order of events
>
> But here's the key part..."

---

## DEMO PART 4: Offline Verification (60 seconds)

**Show**: Terminal

**Say**:

> "You don't need GuardSpine to verify this. You don't need to trust us at all. Our verification tool is open source."

**Run**:

```bash
guardspine-verify code-diff-bundle.json
```

**Show output**:

```
+------------------+--------+
| Check            | Status |
+------------------+--------+
| Hash Chain       | PASS   |
| Root Hash        | PASS   |
| Content Hashes   | PASS   |
| Signatures       | PASS   |
+------------------+--------+

BUNDLE VERIFIED
```

**Say**:

> "An auditor can run this command on an air-gapped laptop. No network, no trust required. The math proves it.
>
> That's the pitch: 'You don't need to trust me. Verify the bundle yourself.'"

---

## DEMO PART 5: The Ecosystem (30 seconds)

**Show**: Spec README or diagram

**Say**:

> "The bundle format is open. The verifier is open source. Anyone can build on it.
>
> What we sell is the workflow - the Diff Postcard UI, the approval inbox, the connectors to SharePoint and ServiceNow. The convenience layer.
>
> But the trust layer? That's verifiable by anyone."

---

## CLOSE (30 seconds)

**Say**:

> "GuardSpine: AI-mediated work governance with verifiable evidence.
>
> - Changes are tracked deterministically
> - Approvals are cryptographically signed
> - Bundles are verifiable offline
>
> Your auditor doesn't need to trust the vendor. They just run `verify`.
>
> Questions?"

---

## BACKUP DEMOS (if time permits)

### PDF Diff Demo

```bash
guardspine-verify pdf-diff-bundle.json --verbose
```

Show contract change with legal review.

### XLSX Diff Demo

```bash
guardspine-verify xlsx-diff-bundle.json --verbose
```

Show financial forecast change with coherence check.

### Tampered Bundle Demo

```bash
# Edit a hash in the bundle
guardspine-verify tampered-bundle.json
# Shows: VERIFICATION FAILED - Hash chain broken
```

---

## KEY MESSAGES TO REPEAT

1. **"You don't need to trust me"** - Say this at least twice
2. **"Deterministic, not AI-generated"** - The diff is math, not hallucination
3. **"Offline verification"** - No network, no vendor dependency
4. **"10-second approvals"** - Speed is a feature
5. **"Open spec, closed workflow"** - Trust is open, value is proprietary

---

## OBJECTION HANDLING

**"How is this different from Git?"**

> "Git tracks code. We track any artifact - PDFs, spreadsheets, contracts. And we add the approval layer with signatures."

**"Can't the AI make mistakes?"**

> "The AI suggests, it doesn't decide. And the diff is deterministic - same input, same output. The AI just summarizes."

**"What if I don't trust your signatures?"**

> "Bring your own keys. The bundle format supports any Ed25519, RSA, or ECDSA key. Your security team can sign with their HSM."

**"How do I know the bundle wasn't tampered with?"**

> "Run the verifier yourself. It's open source. The hash chain math is the proof."

---

**GuardSpine**: Verifiable governance evidence you don't have to trust.
