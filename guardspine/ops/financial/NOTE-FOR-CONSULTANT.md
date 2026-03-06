# Note for Consultant

## CRITICAL: Round Terms Have Changed

The `generate_model.py` source code was written when the round was $300K at
$10M pre-money (3% dilution). **The current terms are:**

| Parameter    | OLD (in source code) | CURRENT (use this) |
| ------------ | -------------------- | ------------------ |
| Round size   | $300K                | **$1,000,000**     |
| Pre-money    | $10M                 | **$9,000,000**     |
| Post-money   | $10.3M               | **$10,000,000**    |
| Dilution     | 3%                   | **10%**            |
| Monthly burn | $15K                 | **$40,000**        |
| Runway       | ~20 months           | **25 months**      |

All narrative blocks in generate_model.py referencing "$300K", "3% dilution",
"$10M valuation", or "$15K burn" are STALE. The charts and formulas for
revenue, TAM, probability, and competition are still valid -- only the
round-terms narrative is outdated.

The canonical round terms are in `DECK-SPECIFICATION.md` and `PRODUCT-SUMMARY.md`.

---

The `generate_model.py` file produces the Excel workbook and all chart figures.
It contains company financial projections AND personal founder financial
modeling. The personal content is deeply embedded and cannot be cleanly
removed without breaking the model. Use this guide to know what to use
and what to ignore.

## What to USE from this file:

- Revenue projections (Bear/Base/Bull scenarios)
- TAM/SAM/SOM sizing
- Pricing tier margins and COGS
- Probability analysis (risk-adjusted, 8 risk factors)
- Speed timeline
- Competitive radar data
- MECE heatmap data
- Dilution waterfall (company-level equity splits)

## What to EXCLUDE from the deck:

### In generate_model.py:

- Lines 299-305: `PERSONAL_TARGET = 100e6` and "$100M personal target math"
- Lines 330-340: `LIQUIDITY_THRESHOLDS` (personal milestone targets)
- Lines 805-836: `compute_personal_liquidity()` function
- Lines 839-859: `compute_path_comparison()` function (personal post_tax outcomes)
- Lines 878-882: Personal post_tax calculations in dilution waterfall
- Lines 1295-1337: Figure generation for "personal_liquidity.png" ("David's Liquidity Path")
- Lines 1461-1531: Subplot "Personal Liquidity at Exit (post-tax, 25% rate)"
- Lines 2225-2244: Excel "Exit for $100M post-tax" rows
- Lines 2266-2274: Excel personal post_tax dilution costs
- Lines 2970-3039: PDF Section 7c "Capital Strategy & Founder Liquidity"
- Lines 3247-3252: "David's personal outcome" at various exits
- Lines 3500-3517: "David post-tax $XXM" calculations

### Figures already removed from figures/ directory:

- personal_liquidity.png
- fee_cascade.png
- acquirer_scorecard.png
- acquisition_trajectory.png

### In strategy/CONTEXT-AND-STRATEGY.md:

- Already redacted (sections replaced with "[Personal financial details redacted]")

### In strategy/INVESTOR-BRIEF.md:

- Clean -- no personal financial content found.

## Summary

The Excel workbook contains multiple sheets. Sheets related to company
revenue, market sizing, probability, and competitive analysis are fair game.
Any sheet or row referencing "personal target", "David's take-home",
"post-tax personal", or "founder liquidity" should not appear in the deck.

The deck should focus on COMPANY metrics: revenue, margins, market size,
traction, probability, team, and competitive position. The investor return
math ($62.5K becomes ~$2.0M at 31.6x at current 10% terms) is company-level
and IS appropriate for the deck.

### Stale narrative blocks in generate_model.py (round terms only):

- Lines 2974-2977: "$300K angel round at $10M valuation (3% dilution)"
- Lines 3186-3187: "$300K angel round (3% dilution)"
- Lines 3205: "Total raised: $300K"
  These generate PDF narrative -- the charts they sit alongside are still valid.
