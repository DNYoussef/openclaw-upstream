# GuardSpine SaaS P&L Model

## Board-Grade Financial Model -- Built from Operator Doctrine Framework

## Date: 2026-02-18

## Status: Pre-revenue. Blanks = unmeasured. All projections labeled as such.

---

## CURRENT MODEL ISSUES (audit before presenting)

### CRITICAL ISSUES IN EXISTING generate_model.py

| #   | Issue                                                                                                     | Location                                        | Impact                                                               |
| --- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| 1   | Round terms stale: $300K/3%/$10M pre throughout                                                           | generate_model.py lines 274-291                 | Charts show wrong round size. Trust-destroying if investor sees it   |
| 2   | BOOTSTRAP_PATH valuation says $15M pre but NOTE-FOR-CONSULTANT says $9M pre                               | generate_model.py:276 vs NOTE:10                | Contradictory valuation. Pick one.                                   |
| 3   | Dilution says 6.25% in code but NOTE says 10%                                                             | generate_model.py:276 vs NOTE:13                | Math doesn't match. $1M at $15M pre = 6.25%. $1M at $9M pre = 10%.   |
| 4   | DAVID_EQUITY = 0.45 but after 10% dilution = 40.5%, code says 42.19%                                      | generate_model.py:304                           | Stale from old round terms                                           |
| 5   | Y1 ARR contradiction (previously flagged, reportedly fixed)                                               | CONTEXT-AND-STRATEGY:490 vs MARKET-ANALYSIS:396 | Board will catch immediately                                         |
| 6   | UNICORN_PROBABILITIES hardcoded, not computed from RISK_FACTORS                                           | generate_model.py:209-216                       | Presented as computed but is stated directly. CRITIQUE flagged this. |
| 7   | Enterprise revenue assumptions (Netflix $200K Y1, IBM $150K Y1) have no validation                        | generate_model.py:164-165                       | Pure speculation with named companies                                |
| 8   | TEAM equity split sums to 100% but no vesting schedule documented                                         | generate_model.py:251-256                       | Investors will ask about vesting                                     |
| 9   | ~~Kristen at 10% equity but role unclear~~ RESOLVED Mar 2: Kristen = 2% equity advisor, no cliff, no cash | generate_model.py:253                           | Update generate_model.py to reflect 2%                               |
| 10  | No current monthly burn or cash position documented                                                       | nowhere                                         | Cannot compute real runway                                           |
| 11  | All unit economics (CAC, LTV, NRR, churn) are assumed, not measured                                       | generate_model.py:114-142                       | Every metric is a guess                                              |
| 12  | No PLG conversion funnel in product (no pricing page, no upgrade path)                                    | product gap                                     | Revenue engine doesn't exist                                         |
| 13  | No budget-line mapping (where does GuardSpine sit in buyer's P&L?)                                        | nowhere                                         | Kristen's #1 concern                                                 |
| 14  | 4-lane horizontal positioning contradicts wedge-first strategy                                            | all investor docs                               | Narrative inconsistency                                              |
| 15  | Consumption/usage-based pricing not modeled (only flat subscription)                                      | generate_model.py                               | May need per-PR or per-bundle pricing                                |

---

## SHEET 1: INCOME STATEMENT (P&L) -- ANNUAL

### Revenue (Top Line)

```
                                    ACTUAL     PROJECTED  PROJECTED  PROJECTED  PROJECTED  PROJECTED
                                    Y0         Y1         Y2         Y3         Y4         Y5
                                    (Today)    (Base)     (Base)     (Base)     (Base)     (Base)
LINE ITEM                           FY2026     FY2027     FY2028     FY2029     FY2030     FY2031
==================================  =========  =========  =========  =========  =========  =========

REVENUE
  Subscription / Platform Revenue   $0         $650K      $5.0M      $15.0M     $40.0M     $80.0M
    Community (Free, $0/mo)         $0         $0         $0         $0         $0         $0
    Starter ($499/mo)               $0         $72K       $360K      $720K      $1.4M      $2.4M
    Team ($2,000/mo)                $0         $192K      $960K      $2.2M      $4.8M      $8.0M
    Org ($12,000/mo)                $0         $288K      $2.9M      $10.8M     $28.8M     $57.6M
    Enterprise ($50,000/mo)         $0         $98K       $780K      $1.3M      $5.0M      $12.0M
  Services Revenue                  $0         $0         $0         $0         $0         $0
    (BYOK = self-serve install.     $0         $0         $0         $0         $0         $0
     No services component.)
-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL REVENUE (GAAP)                $0         $650K      $5.0M      $15.0M     $40.0M     $80.0M

  ENDING ARR (non-GAAP top line)    $0         $1.3M      $8.0M      $25.0M     $60.0M     $100.0M
  YoY ARR Growth %                  n/a        n/a        515%       213%       140%       67%
  YoY GAAP Growth %                 n/a        n/a        669%       200%       167%       100%
```

### Revenue Build-Up (Base Scenario from generate_model.py)

```
SOURCE: REVENUE_MILESTONES + UNICORN_SCENARIOS["Base"] + SCENARIOS["Base"]
Month 0 = angel close. 15%/mo customer growth, $30K avg ACV, 1.20 NRR.

CUSTOMER COUNT (cumulative paid)
  Starting customers                0          0          37         110        250        430
  + New logos added                 0          37         85         165        220        230
  - Churned logos (5% annual)       0          0          (2)        (6)        (13)       (25)
  = Ending customers                0          37         110        250        430        610

  Avg ACV (blended)                 n/a        $30,000    $35,000    $42,000    $50,000    $55,000
  Starting ARR                      $0         $0         $1.3M      $8.0M      $25.0M     $60.0M
  + New ARR                         $0         $1.1M      $3.0M      $6.9M      $11.0M     $12.7M
  + Expansion ARR (NRR-1)           $0         $0         $520K      $1.6M      $5.0M      $12.0M
  + Enterprise deals                $0         $350K      $1.1M      $1.9M      $3.3M      $5.5M
  - Contraction ARR                 $0         $0         ($20K)     ($100K)    ($400K)    ($800K)
  - Churned ARR                     $0         $0         ($60K)     ($400K)    ($1.3M)    ($2.5M)
  = Ending ARR                      $0         $1.3M*     $8.0M      $25.0M     $60.0M     $100.0M

  Free users (GitHub Action)        0          2,000      8,000      20,000     50,000     100,000
  Free-to-Paid conversion rate      n/a        1.9%       1.4%       1.1%       0.9%       0.6%
    (declines as base broadens)

* Y1 ending ARR aligns with REVENUE_MILESTONES: $1M at M10 (62% prob), $3M at M16 (48%)
  $1.3M at M12 is interpolated. See milestone probability table below.

REVENUE MILESTONES (from generate_model.py, probability-adjusted):
  Milestone          Month   Probability   Implied Customer Count
  First customer     3       88%           1
  $500K ARR          7       72%           ~17
  $1M ARR            10      62%           ~33
  $3M ARR            16      48%           ~80
  $10M ARR           22      33%           ~180
  $30M ARR           30      24%           ~430
  $100M ARR          42      14%           ~1,200

NOTES:
  - ALL NUMBERS ARE PROJECTIONS. Zero measured values exist.
  - GAAP revenue < ending ARR because customers onboard throughout the year.
    Y1 GAAP ~ 50% of ending ARR (heavy back-weighting).
    Y2+ GAAP approaches ARR as base stabilizes.
  - Tier mix shifts toward Enterprise over time (higher ACV, longer contracts).
  - Enterprise deals from UNICORN_SCENARIOS["Base"]["enterprise"] dict.
  - 15%/mo customer growth decays 20%/yr (decay=0.20 in model).
  - Free-to-paid conversion assumed at 3% (industry 1-5%), but actual
    conversion rate shown declines because free base grows faster than paid.
```

### COGS (Cost of Goods Sold) -- Above the Line

```
                                    ACTUAL     PROJECTED  PROJECTED  PROJECTED  PROJECTED  PROJECTED
                                    Y0         Y1         Y2         Y3         Y4         Y5
LINE ITEM                           FY2026     FY2027     FY2028     FY2029     FY2030     FY2031
==================================  =========  =========  =========  =========  =========  =========

COGS
  Cloud Infrastructure (AWS/GCP)
    Platform hosting                $___/mo    $44K       $264K      $780K      $1.9M      $3.2M
    Database (Postgres)             incl       incl       incl       incl       incl       incl
    CI/CD (GitHub Actions)          $0         $0         $10K       $25K       $50K       $80K
    Monitoring / observability      $0         $5K        $20K       $50K       $100K      $150K
  LLM API Costs                     $0         $0         $0         $0         $0         $0
    (BYOK: customer pays own keys.
     GuardSpine pays ZERO.)
  Support (customer-facing hours)   $0         $30K       $174K      $530K      $1.5M      $2.8M
  Cognitive attestation license     $0         $14K       $95K       $340K      $1.1M      $2.2M
    (Logan/Proprioceptive AI --
     Enterprise tier only, $150/mo)
-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL COGS                          $___       $93K       $563K      $1.73M     $4.65M     $8.43M

GROSS PROFIT                        ($___K)    $557K      $4.44M     $13.27M    $35.35M    $71.57M
GROSS MARGIN %                      n/a        85.7%      88.7%      88.5%      88.4%      89.5%

COGS DERIVATION (updated Mar 4 -- canonical 5-tier pricing):
  Per-customer monthly COGS:
    Starter:    $15 hosting + $0 support + $0 cognitive   = $15/mo
    Team:       $150 hosting + $100 support + $0 cognitive = $250/mo
    Org:        $300 hosting + $200 support + $0 cognitive = $500/mo
    Enterprise: $500 hosting + $400 support + $150 cognitive = $1,050/mo

  Per-customer gross margin (fully loaded):
    Starter:    ($499 - $15)     / $499    = 97.0%
    Team:       ($2,000 - $250)  / $2,000  = 87.5%
    Org:        ($12,000 - $500) / $12,000 = 95.8%
    Enterprise: ($50,000 - $1,050) / $50,000 = 97.9%

  Y1 COGS estimate: ~37 customers * blended $210/mo avg * 12mo = ~$93K
  Blended improves as Enterprise share grows (highest margin tier).
  BYOK eliminates the largest SaaS COGS line (LLM API/compute).

NOTES:
  - BYOK is the structural advantage. Zero LLM inference cost.
  - CURRENT COGS (pre-revenue): Only dev/staging infra. Amount: $___/mo
  - Hosting COGS scales with customer count, not usage (flat tier pricing).
  - Support COGS will jump when first dedicated CS hire is made (~$80-120K/yr).
```

### Operating Expenses (Below the Line / Opex / SG&A)

```
                                    ACTUAL     PROJECTED  PROJECTED  PROJECTED  PROJECTED  PROJECTED
                                    Y0         Y1         Y2         Y3         Y4         Y5
LINE ITEM                           FY2026     FY2027     FY2028     FY2029     FY2030     FY2031
==================================  =========  =========  =========  =========  =========  =========

SALES & MARKETING (S&M)
  Founder sales (David, 40%)        $___       $48K       $48K       $90K       $120K      $150K
  GTM lead (Kristen)                $___       $0-96K     $120K      $140K      $160K      $180K
  Sales hires                       $0         $0         $250K      $500K      $1.2M      $2.5M
  Marketing programs                $0         $15K       $120K      $400K      $1.0M      $2.0M
  Events / conferences              $0         $5K        $50K       $150K      $300K      $500K
  Content / SEO / community         $0         $10K       $60K       $150K      $300K      $500K
  Sales tooling (CRM, outreach)     $0         $5K        $20K       $40K       $60K       $80K
-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL S&M                           $___       $83-179K   $668K      $1.47M     $3.14M     $5.91M
  S&M as % of Revenue               n/a        13-28%     13%        10%        8%         7%
  Target benchmark:                             40-50%     40-50%     35-45%     30-40%     25-35%
  NOTE: S&M % is LOW because founder-led sales + PLG (no AE team Y1).
        Kristen Y1: $0 if equity-only, $96K if cash retainer.
        Will rise as sales team scales in Y2-Y3.

RESEARCH & DEVELOPMENT (R&D)
  Engineering (Igor, full-time)     $___       $120K      $170K      $190K      $210K      $230K
  Engineering (David, 60%)          $___       $72K       $72K       $135K      $0         $0
  Engineering hires                 $0         $80K       $400K      $900K      $2.0M      $4.0M
  AI agent APIs (3 x $1K/mo)        $___       $36K       $48K       $60K       $72K       $84K
  Infra / dev tooling               $___       $15K       $40K       $80K       $120K      $180K
  OSS contributor stipends          $0         $0         $20K       $50K       $80K       $100K
-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL R&D                           $___       $323K      $750K      $1.42M     $2.48M     $4.59M
  R&D as % of Revenue               n/a        50%        15%        9%         6%         6%
  Target benchmark:                             30-40%     30-40%     25-35%     20-30%     20-25%
  NOTE: R&D % is HIGH in Y1 (team is mostly engineering).
        Will compress as revenue scales. This is normal for pre-revenue.

GENERAL & ADMINISTRATIVE (G&A)
  Legal (incorporation, IP, patents) $___      $30K       $50K       $80K       $120K      $200K
  Accounting / bookkeeping          $0         $12K       $24K       $48K       $72K       $100K
  Finance/ops hire                  $0         $0         $100K      $130K      $150K      $170K
  Insurance (D&O, E&O)             $0         $8K        $15K       $25K       $40K       $60K
  Software subscriptions            $___       $12K       $24K       $40K       $60K       $80K
  Office / remote stipends          $0         $6K        $12K       $20K       $30K       $40K
-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL G&A                           $___       $68K       $225K      $343K      $472K      $650K
  G&A as % of Revenue               n/a        10%        5%         2%         1%         <1%
  Target benchmark:                             <20%       <20%       <15%       <12%       <10%

-------                             ---------  ---------  ---------  ---------  ---------  ---------
TOTAL OPERATING EXPENSES            $___       $474-570K  $1.64M     $3.23M     $6.09M     $11.15M

EBITDA (Operating Income/Loss)      ($___K)    ($13)-83K  $2.80M     $10.04M    $29.26M    $60.42M
EBITDA MARGIN %                     n/a        (2)-13%    56%        67%        73%        76%

RULE OF 40                          n/a        n/a        572%       279%       213%       143%
  (= ARR Growth % + EBITDA Margin %)
  NOTE: Rule of 40 is meaningless at this stage. The metric matters
        after $10M+ ARR when growth/profitability tradeoff is real.

NOTES:
  - Y1 total spend: $474-570K opex + $93K COGS = $567-663K total.
    Angel ($1M) covers it with $337-433K remaining at Y1 end.
  - Y1 GAAP revenue: ~$650K. Near breakeven in Y1.
  - Kristen compensation RESOLVED Mar 2: 2% equity, no cash, no AI budget. Burn = $26.5K/mo.
  - $10K/mo founder salaries = $240K/yr for David+Igor combined.
    This is the STRONGEST signal to investors: founders with skin in game.

  BURN DECOMPOSITION (ACTUAL -- updated 2026-03-02):
      David salary:    $10K/mo ($120K/yr)  -- AGREED
      Igor salary:     $10K/mo ($120K/yr)  -- AGREED
      Floor:           $5K/mo each if needed
      Kristen:         $0/mo (2% equity, no cliff, no cash -- agreed Mar 2)
      AI agent APIs:   $2K/mo ($24K/yr)    -- 2 people * $1K/mo each (Kristen removed)
        (Claude/GPT/Gemini for dev, content, outreach, testing)
        Classification: R&D infra/tooling (productivity multiplier)
      Infra:           $1.5K/mo ($18K/yr)  -- hosting, DB, CI
      Legal:           $2K/mo ($24K/yr) avg
      Software:        $1K/mo ($12K/yr)    -- CRM, monitoring, etc.
      TOTAL:           $26.5K/mo ($318K/yr)

      Runway at $26.5K/mo: 37.7 months (3+ years)

  Hire plan with $1M:
      Engineer #1 (M3-M4):    $120K/yr + benefits (~$10K/mo)
      Legal (outsourced Y1):  $30K/yr (hourly, not FTE)
      Finance (Y2):           $100K/yr
```

### Bottom Line

```
                                    ACTUAL     PROJECTED  PROJECTED  PROJECTED  PROJECTED  PROJECTED
LINE ITEM                           FY2026     FY2027     FY2028     FY2029     FY2030     FY2031
==================================  =========  =========  =========  =========  =========  =========

EBITDA                              ($___K)    ($13)-83K  $2.80M     $10.04M    $29.26M    $60.42M
  Depreciation & Amortization       $0         $0         $0         ($50K)     ($100K)    ($200K)
  Interest Expense                  $0         $0         $0         $0         $0         $0
  Taxes (25% effective rate)        $0         $0         ($700K)    ($2.5M)    ($7.3M)    ($15.1M)
  Other Income / (Expense)          $0         $0         $0         $0         $0         $0
-------                             ---------  ---------  ---------  ---------  ---------  ---------
NET INCOME / (LOSS)                 ($___K)    ($13)-83K  $2.10M     $7.49M     $21.86M    $45.12M

SUMMARY TABLE
  GAAP Revenue                      $0         $650K      $5.0M      $15.0M     $40.0M     $80.0M
  Ending ARR                        $0         $1.3M      $8.0M      $25.0M     $60.0M     $100.0M
  Gross Margin                      n/a        85.7%      88.7%      88.5%      88.4%      89.5%
  EBITDA Margin                     n/a        (2)-13%    56%        67%        73%        76%
  Headcount                         3          4-5        12         25         50         80
  Monthly Burn (net of revenue)     $26.5K     POSITIVE  POSITIVE   POSITIVE   POSITIVE   POSITIVE

CAVEAT: Y2-Y5 projections assume Base scenario growth holds. At 48%
probability for $3M ARR (M16) and 33% for $10M ARR (M22), these
numbers are aspirational targets, not commitments. Use Bear scenario
for downside planning and capital adequacy testing.
```

---

## SHEET 2: ARR BRIDGE (Board Top Line)

```
Assumes angel close M0 = Q1'27 start. 15%/mo customer growth with 20%/yr decay.

                                    Q1'27      Q2'27      Q3'27      Q4'27      FY2027     FY2028
==================================  =========  =========  =========  =========  =========  =========
Starting ARR                        $0         $90K       $360K      $750K      $0         $1.3M

+ New Logo ARR                      $90K       $270K      $400K      $340K      $1.1M      $3.0M
  New logos closed                  3          9          14         11         37         85
  Avg new logo ACV                  $30K       $30K       $29K       $31K       $30K       $35K

+ Expansion ARR                     $0         $0         $15K       $40K       $55K       $520K
  Upsells (tier upgrade)            $0         $0         $15K       $40K       $55K       $400K
  Cross-sell (new lanes)            $0         $0         $0         $0         $0         $120K

- Contraction ARR                   $0         $0         $0         $0         $0         ($20K)

- Churned ARR                       $0         $0         ($5K)      ($10K)     ($15K)     ($60K)
  Logos lost                        0          0          0          0          0          2

-------                             ---------  ---------  ---------  ---------  ---------  ---------
Ending ARR                          $90K       $360K      $770K      $1.3M      $1.3M      $8.0M
ARR Growth (QoQ)                    n/a        300%       114%       69%        n/a        515%

Net New ARR                         $90K       $270K      $410K      $530K      $1.3M      $6.7M

QUARTERLY NOTES:
  Q1: First 3 paid customers (design partners from Kristen network + Brent Foster).
  Q2: PLG starts contributing. GitHub Action installs drive inbound.
  Q3: Enterprise pilot(s) close. Growth rate starts compounding.
  Q4: Expansion revenue begins as Q1-Q2 customers upsell.

  Y1 ending ARR of $1.3M aligns with milestone interpolation:
    $1M at M10 (62% prob), $3M at M16 (48% prob)
    $1.3M at M12 sits between these.
```

---

## SHEET 3: UNIT ECONOMICS

```
                                    MEASURED   PROJECTED  PROJECTED  TARGET     BENCHMARK
                                    (TODAY)    Y1         Y2         STEADY     (SaaS med)
==================================  =========  =========  =========  =========  =========

ACQUISITION
  Fully-loaded CAC                  INF        $5,486     $8,141     $15,000    varies
    = Total S&M spend / New logos   ($0/0)     ($203K/37) ($692K/85)
  CAC Payback (months)              n/a        2.6mo      3.5mo      12mo       12-18mo
    = CAC / (Avg MRR * Gross Margin%)          ($5.5K/(2.5K*0.86))
  S&M Efficiency (Magic Number)     n/a        n/a        6.4x       >0.75      0.75-1.5
    = Net New ARR / Prior Qtr S&M              ($1.3M/$203K)

  CAUTION: Y1 CAC is artificially LOW because founder sales = sweat equity.
  Founder time is not costed at market rate. At market ($200K AE salary),
  real CAC would be ~$12K-15K per customer. This is the number to quote.

RETENTION (all assumed -- zero measured data)
  Gross Revenue Retention (GRR)     n/a        ~95%       ~93%       >90%       85-95%
  Net Revenue Retention (NRR)       n/a        ~115%      ~120%      >120%      110-130%
  Logo Retention Rate               n/a        ~100%      ~98%       >90%       85-90%
  Avg Contract Length                n/a        12mo       12mo       12-24mo    12-36mo

VALUE (from generate_model.py constants)
  Customer Lifetime (months)        n/a        36mo       36mo       36mo       36-60mo
    = 1 / Monthly Churn Rate                   (assumed)  (assumed)
  LTV (margin-weighted)             n/a        $77,400    $90,720    $108,360   varies
    = ACV * GM% * Lifetime(yrs)                ($30K*0.86*3) ($35K*0.864*3)
  LTV : CAC Ratio                   n/a        14.1x      11.1x      >3x        3-5x
    NOTE: Inflated by low CAC. At market-rate CAC ($15K), LTV:CAC = 5.2x.
  Magic Number                      n/a        n/a        6.4x       >0.75      0.75-1.5
    NOTE: Also inflated. Will normalize as paid acquisition starts.

MARGIN BY TIER (updated Mar 4 -- canonical 5-tier pricing)
                                    Monthly    COGS/mo    Margin $   Margin %   CAC
  Free                              $0         $0         $0         n/a        $0
  Starter                           $499       $15        $484       97.0%      $500
  Team                              $2,000     $250       $1,750     87.5%      $5,000
  Org                               $12,000    $500       $11,500    95.8%      $15,000
  Enterprise                        $50,000    $1,050     $48,950    97.9%      $50,000
  Blended Y1                        $3,200     $180       $3,020     94.4%      $4,800

PER-TIER UNIT ECONOMICS
                            Starter     Team        Org         Enterprise
  Annual Revenue             $5,988      $24,000     $144,000    $600,000
  Annual COGS                $180        $3,000      $6,000      $12,600
  Gross Profit               $5,808      $21,000     $138,000    $587,400
  Gross Margin               97.0%       87.5%       95.8%       97.9%
  CAC                        $5,000      $15,000     $50,000
  CAC Payback (months)       2.9mo       3.3mo       4.6mo
  LTV (36mo)                 $63,000     $162,000    $394,200
  LTV:CAC                    12.6x       10.8x       7.9x
  NRR (assumed)              115%        120%        130%

NOTES:
  - CAC is currently INFINITE (>0 spend, 0 conversions)
  - Current "sales motion" = cold outreach. 42 messages, 2 responses, 0 conversions
  - PLG funnel (free Action -> paid dashboard) does not exist in product yet
  - No pricing page, no upgrade path, no self-serve billing
  - All retention metrics require minimum 12 months of customer data to be meaningful
  - CAC payback looks excellent because founder sales is "free." This will worsen
    as paid sales team ramps. Budget for 12-month payback at steady state.
```

---

## SHEET 4: CASH FLOW & RUNWAY

```
                                    ACTUAL     PROJECTED  PROJECTED  PROJECTED
                                    TODAY       M1-6       M7-12      M13-24
                                    (Pre-raise) (Post-raise)
==================================  =========  =========  =========  =========

CASH POSITION
  Starting cash                     $___       $1,000K    $757K      $733K
  + Angel round proceeds            $0         $1,000K    $0         $0
  + Revenue (cash collected)        $0         $57K       $285K      $3.5M
  - Operating expenses              ($___/mo)  ($300K)    ($309K)    ($1.65M)
  - Capital expenditures            $0         $0         $0         $0
-------                             ---------  ---------  ---------  ---------
  Ending cash                       $___       $757K      $733K      $2.58M
  Monthly burn rate (net)           $___/mo    $40.5K     $4K net    POSITIVE
  Runway remaining (at burn rate)   ___mo      18.7mo     183mo      INFINITE

  M1-6: Revenue starts M3 (first customer). ~$57K collected by M6.
         Burn: ~$50K/mo (incl eng hire M4). Cash consumed: ~$243K net.
  M7-12: Revenue ramps. ~$285K collected. Burn: ~$52K/mo.
         Approaching breakeven by M10-12.
  M13-24: Revenue exceeds burn. Cash accumulates.

BURN RATE DECOMPOSITION (post-raise)
  FOUNDER AGREEMENT: David + Igor = $10K/mo each (floor: $5K/mo each)

  SCENARIO A: $10K/mo each (comfortable)
    David salary                    $10,000
    Igor salary                     $10,000
    Kristen:                        $0         (2% equity, no cash, no AI budget -- agreed Mar 2)
    AI agent APIs (2 x $1K/mo)      $2,000     (Claude/GPT/Gemini -- David + Igor only)
    Cloud infrastructure            $1,500
    Legal / IP / patents            $2,000     (averaged; front-loaded)
    Software subscriptions          $1,000
    TOTAL                           $26.5K/mo
    Runway at $26.5K:               37.7 months (3+ years)

  SCENARIO B: $5K/mo each (aggressive cash preservation)
    David salary                    $5,000
    Igor salary                     $5,000
    Kristen:                        $0         (equity only)
    AI agent APIs (2 x $1K/mo)      $2,000
    Cloud + Legal + Software        $4,500
    TOTAL                           $16.5K/mo
    Runway at $16.5K:               60.6 months (5 years)

  RECOMMENDED FOR INVESTOR NARRATIVE:
    Present Scenario A ($10K each) = $26.5K/mo = 37+ months runway.
    This is EXCELLENT. Most angels want to see 18-24 months.
    Having 37+ months = credible "we won't run out of money" story.
    Kristen is equity-only with no AI budget (agreed Mar 2).
    AI agent cost is a FEATURE: "2-person team + AI = 6-8 person output."

  WITH ENG HIRE AT M4:
    Scenario A + $10K eng hire + $1K AI = $37.5K/mo
    Runway (from remaining ~$894K at M4): 23.8 months. Still strong.

BREAKEVEN ANALYSIS
  At $26.5K/mo burn (Scenario A, Kristen equity-only, no AI budget):
    Breakeven MRR = $26.5K / 0.86 GM = $30.8K MRR = $370K ARR
    Required customers: ~13 Pro OR ~7 Business OR ~3 Enterprise
    Target month: M4-M6 (Base scenario) -- VERY ACHIEVABLE

  At $46.5K/mo burn (Scenario A + eng hire):
    Breakeven MRR = $46.5K / 0.86 GM = $54.1K MRR = $649K ARR
    Required customers: ~22 Pro OR ~11 Business OR ~5 Enterprise
    Target month: M8-M10 (Base scenario)

NOTES:
  - Pre-raise cash position: $___  <-- FILL IN BEFORE MEETING
  - Founders currently self-funding? Personal savings? Side income?
  - DSO assumption: 30 days (SaaS standard, annual prepaid = 0 DSO)
  - No debt. No line of credit. Cash = angel proceeds + revenue.
```

---

## SHEET 5: PIPELINE & GTM METRICS

```
                                    MEASURED   TARGET     TARGET     BENCHMARK
                                    (TODAY)    Q1 Y1      Q2 Y1      (SaaS)
==================================  =========  =========  =========  =========

PIPELINE
  Total prospects in DB             139        150        200        n/a
  Qualified pipeline ($)            $0         $180K      $500K      n/a
  Pipeline coverage (vs quota)      0x         3-5x       3-5x       4-5x
  Avg deal size in pipeline         n/a        $30K       $30K       n/a

FUNNEL (stage definitions needed)
  Prospect (identified)             139        150        200        n/a
  Contacted                         42         60         100        n/a
  Responded                         2          10         25         n/a
  Demo/Eval                         0          5          12         n/a
  Proposal                          0          3          6          n/a
  Closed Won                        0          3          6          n/a
  Response rate                     4.8%       6.7%       12.5%      n/a
  Contacted->Closed Won             0%         5%         6%         2-5%

SALES CYCLE
  Avg days to close                 n/a        60-90d     60-90d     90-180d
  # active evaluations              2          5+         10+        n/a
    - Brent Foster (TD Bank)        Technical question (buyer, score 92)
    - Phil Venables (Ballistic VC)  DD questions (investor, score 88)

CHANNELS
  Inbound (GitHub Action installs)  0          50+        200+       n/a
  Outbound (cold LinkedIn/email)    127 sent   160        250        n/a
  Referral (Kristen/network)        0          5+         10+        n/a
  Content / SEO                     0          1+ posts   5+ posts   n/a

NOTES:
  - Pipeline is currently a PROSPECT LIST, not dollarized qualified pipeline.
  - No CRM. Outreach tracked in SQLite DB (outreach.db).
  - No stage definitions. No conversion rates measurable.
  - 300 prospects: 40 investors, 160 buyers, 96 builders, 4 connectors (verified 2026-02-23).
  - Of 127 messages sent: 10 responses (7.9% response rate, 9 green / 1 yellow).
  - Zero have entered a sales process (no demo, no eval, no pilot).
  - Brent Foster asked 1 technical question -- first buyer engagement signal.
  - Phil Venables asked 3 DD questions -- investor engagement.
  - Neither has received a demo, trial, or pricing proposal.
  - CRITICAL GAP: Need to define sales stages and start tracking time-in-stage.
```

---

## SHEET 6: MILESTONE P&L SNAPSHOTS (Kristen's likely ask)

### At $384K ARR -- BREAKEVEN (~Month 5-7, Scenario A)

```
Customers:              ~13 paid (mostly Pro tier)
MRR:                    ~$32K
GAAP Revenue (monthly): ~$32K
COGS (monthly):         ~$2.7K (13 * $210 avg)
Gross Profit (monthly): ~$29.3K
Monthly burn:           ~$26.5K (David $10K + Igor $10K + AI APIs $2K + infra/legal/sw $4.5K)
Net cash flow:          ~$1.8K/mo POSITIVE (breakeven achieved)
Cash remaining:         ~$850K (of $1M raised)
Headcount:              3 (David, Igor, Kristen equity-only)
```

### At $500K ARR (~Month 7, 72% probability)

```
Customers:              ~17 paid (mix Pro + Business)
MRR:                    ~$41.7K
GAAP Revenue (annualized): ~$500K
COGS (monthly):         ~$3.6K
Gross Profit (monthly): ~$38.1K
Gross Margin:           91.4%
Monthly burn:           ~$37.5K (founders $20K + eng hire $10K + AI APIs $3K + overhead $4.5K)
Net cash flow:          ~$3.6K/mo POSITIVE
Cash remaining:         ~$860K
Headcount:              4 (David, Igor, Eng hire #1, Kristen equity)
```

### At $1M ARR (~Month 10, 62% probability)

```
Customers:              ~33 paid
MRR:                    ~$83.3K
GAAP Revenue (annualized): $1M
COGS (monthly):         ~$6.9K
Gross Profit (monthly): ~$76.4K
Gross Margin:           91.7%
Monthly burn:           ~$47.5K (founders $20K + 2 eng $20K + AI APIs $3K + overhead $4.5K)
Net cash flow:          ~$31.9K/mo POSITIVE
Cash remaining:         ~$900K+ (growing)
Headcount:              5 (+ second eng hire)
```

### At $5M ARR (~Month 18, 40% probability)

```
Customers:              ~100 paid (tier mix shifting to Business/Enterprise)
MRR:                    ~$417K
GAAP Revenue (annualized): $5M
COGS (monthly):         ~$42K
Gross Profit (monthly): ~$375K
Gross Margin:           89.9%
Headcount:              12-15
Monthly opex:           ~$150K (salaries + programs + G&A)
EBITDA (monthly):       ~$225K
EBITDA Margin:          54%
Rule of 40:             ~250%+ growth + 54% margin = 300%+
Cash position:          $2M+ (accumulated from operations)
```

### At $10M ARR (~Month 22, 33% probability)

```
Customers:              ~180 paid
MRR:                    ~$833K
GAAP Revenue (annualized): $10M
COGS (monthly):         ~$83K
Gross Profit (monthly): ~$750K
Gross Margin:           90%
Headcount:              25-30
Monthly opex:           ~$300K
EBITDA (monthly):       ~$450K
EBITDA Margin:          54%
Rule of 40:             ~100% growth + 54% = ~154%
LTV:CAC:                5-8x (at market-rate CAC)
NRR:                    120%+ (target)
Cash position:          $5M+ (no additional raise needed)
```

---

## SHEET 7: BUYER'S BUDGET MAP (gap identified by Kristen -- NEW)

```
WHERE DOES GUARDSPINE SIT IN THE BUYER'S P&L?

PRIMARY BUDGET LINE:    DevSecOps Tooling
  Department:           Engineering / Platform Engineering
  Budget owner:         VP Engineering Practices OR Head of DevSecOps
  Typical allocation:   $200K - $2M/yr at Tier 1 banks
  Category neighbors:   Snyk ($24K-100K/yr), SonarQube ($15K-60K/yr),
                        GitHub Advanced Security ($49/seat/mo),
                        Checkmarx ($50K-200K/yr)
  Purchase trigger:     Audit finding, regulatory deadline (DORA),
                        board mandate on AI governance
  GuardSpine position:  COMPLEMENTARY (not replacing existing tools,
                        adds governance layer on top)
  ACV range:            $24K-144K/yr ($2K-12K/mo by tier)

SECONDARY BUDGET LINE:  GRC / Compliance Software
  Department:           Risk / Compliance / Legal
  Budget owner:         CISO, Chief Risk Officer, Compliance Director
  Typical allocation:   $500K - $5M/yr at Tier 1 banks
  Category neighbors:   Vanta ($___/yr), Drata ($___/yr),
                        ServiceNow GRC ($___/yr)
  Purchase trigger:     Regulatory examination, audit failure,
                        board reporting gap
  GuardSpine position:  Evidence bundles feed GRC reporting.
                        NOT a GRC platform replacement.

TERTIARY (FUTURE):      AI Governance Platform (emerging category)
  WARNING: This budget line DOES NOT EXIST yet at most enterprises.
  Creating a new budget category = political capital + exec sponsorship
  + dramatically longer sales cycle. DO NOT LEAD WITH THIS.

RECOMMENDED SALES POSITIONING:
  Lead:    "DevSecOps add-on for AI code governance" (existing budget)
  Expand:  "Evidence bundles for compliance reporting" (adjacent budget)
  Avoid:   "AI governance platform" (new budget = long cycle)

EVIDENCE NEEDED (per Kristen's framework):
  [ ] 10-15 buyer validation conversations confirming budget line
  [ ] 1-3 design partners at meaningful ACV ($24K+ ARR)
  [ ] Documented procurement path at one enterprise
  [ ] Named budget owner who signed off on evaluation
  [ ] Willingness-to-pay data at specific price points
```

---

## SHEET 8: COMPETITIVE PRICING ANALYSIS (gap)

```
TOOL                        PRICING MODEL           ACV RANGE        POSITIONING
========================    ====================    ==============   ===========================
Snyk (Teams)                Per developer/mo        $24K-100K/yr     SAST/DAST/SCA
SonarQube (Developer)       Per instance/yr         $15K-60K/yr      Static analysis
GitHub Advanced Security    Per committer/mo ($49)  $59K-500K/yr     Native GitHub security
Checkmarx                   Per project/yr          $50K-200K/yr     AppSec testing
Veracode                    Per app/yr              $50K-300K/yr     AppSec platform
Vanta                       Per employee/mo         $30K-100K/yr     Compliance automation
Drata                       Per employee/mo         $25K-75K/yr      Compliance automation
Semgrep (Team)              Per developer/mo        $24K-100K/yr     Code analysis
Wiz                         Per workload/mo         $100K-500K/yr    Cloud security

GuardSpine (Pro)            Flat monthly            $24K/yr          AI code governance
GuardSpine (Business)       Flat monthly            $60K/yr          Multi-lane governance
GuardSpine (Enterprise)     Flat monthly            $144K/yr         Full governance + attestation

OBSERVATIONS:
  1. GuardSpine Pro ($24K) is at the LOW END of DevSecOps tooling. Easy budget fit.
  2. GuardSpine Enterprise ($144K) is competitive with Checkmarx/Veracode range.
  3. Per-developer pricing (like Snyk) might scale better. Not modeled.
  4. Usage-based pricing (per PR, per evidence bundle) not modeled but could be
     more natural for the product ("pay per governance event").
  5. No competitive tool produces evidence bundles. This is the differentiation.
  6. None of these prices are validated by buyer feedback.
```

---

## SHEET 9: RISK-ADJUSTED PROBABILITY MATRIX

```
From generate_model.py RISK_FACTORS (column: "current", Feb 2026):

RISK FACTOR              FAILURE PROB    SURVIVAL PROB    NOTES
=======================  =============  ==============   =====================================
Technical Execution      5%             95%              737 tests, shipped, kernels verified
Product-Market Fit       7%             93%              DORA catalyst, but 0 paying customers
GTM / Sales              8%             92%              Cold outreach only, no sales motion
Scaling                  12%            88%              Untested beyond 2-person team
Competitive Moat         5%             95%              9/9 MECE, no direct competitor
Capital Access           3%             97%              Phil DD + Kristen angel network
Founder Dynamics         12%            88%              Igor + David synced, Kristen TBD
Legal / Liability        4%             96%              MIT license, patent filing pending

STATED UNICORN PROBABILITY (from model):
  Current (Feb 2026):    34%
  Note: This is hardcoded in generate_model.py, NOT computed from above factors.
  Product of survival rates: 0.95*0.93*0.92*0.88*0.95*0.97*0.88*0.96 = 0.537
  Discrepancy: 53.7% implied vs 34% stated. The 34% includes unmodeled risks
  and correlation effects. But the gap is large and should be explained.

SEPARATE TRACKING (from MEMORY.md, different methodology):
  8-factor model with different dimensions, composite geometric mean = 0.64
  These two models should be reconciled. Having two probability models
  with different numbers is a trust risk per failure mode #1.
```

---

## SHEET 10: DEFINITIONS & METHODOLOGY

```
METRIC DEFINITIONS (for consistency -- per Operator Doctrine failure mode #1):

ARR:            Annualized Recurring Revenue. Sum of all active subscription
                contracts annualized. Excludes: trials, one-time services,
                termination-for-convenience contracts.

MRR:            Monthly Recurring Revenue = ARR / 12.

GAAP Revenue:   Revenue recognized per ASC 606 performance obligations.
                For SaaS with immediate platform access, GAAP ~ ARR over time.

Gross Margin:   (Revenue - COGS) / Revenue. COGS includes: hosting, support
                labor (customer-facing hours only), third-party licenses.
                COGS does NOT include: R&D, S&M, G&A.

CAC:            Fully-loaded Cost to Acquire a Customer.
                = Total S&M Spend (period) / New Logos Closed (period).
                Includes: salaries allocated to sales, marketing programs,
                events, tooling. Excludes: CS/support (that's COGS).

CAC Payback:    Months to recoup CAC from a new customer.
                = CAC / (Avg MRR per customer * Gross Margin %).

LTV:            Lifetime Value of a customer (margin-weighted).
                = Avg ACV * Gross Margin % * Avg Customer Lifetime (years).

LTV:CAC:        LTV / CAC. Target: >3x (viable), 3-5x (strong), >5x (excellent).

NRR:            Net Revenue Retention. For a cohort of customers at period start,
                what % of their ARR remains + expanded at period end.
                = (Starting ARR + Expansion - Contraction - Churn) / Starting ARR.
                Target: 110-130%.

GRR:            Gross Revenue Retention. Same as NRR but without expansion.
                = (Starting ARR - Contraction - Churn) / Starting ARR.
                Target: 85-95%.

Rule of 40:     ARR YoY Growth % + EBITDA Margin %. Target: >40%.

Magic Number:   Net New ARR (quarter) / S&M Spend (prior quarter).
                >0.75 = efficient. >1.0 = excellent.

METHODOLOGY NOTES:
  - All projections use generate_model.py Base scenario unless noted
  - generate_model.py round terms are STALE ($300K). Current: $1M at $9M pre.
  - Two separate probability models exist (generate_model.py 8-factor +
    MEMORY.md 8-factor). These need reconciliation.
  - No measured values exist for any operating metric. All are projected.
  - "Target" columns use SaaS industry medians from public company benchmarks.
```

---

## ACTION ITEMS BEFORE PRESENTING TO INVESTORS

```
PRIORITY 1 (before Kristen meeting / angel intros):
  [x] Document monthly burn rate: $10K each + $3K AI APIs = $27.5-35.5K/mo
  [ ] Choose ONE wedge: CodeGuard for regulated fintech (DORA)
  [ ] Fix generate_model.py round terms ($1M / $9M pre / 10% dilution)
  [ ] Create Buyer's Budget Map (Sheet 7 above -- validate with Brent Foster)
  [ ] Document current cash position (pre-raise personal runway)
  [ ] Clarify Kristen's role: advisor (equity only) vs part-time vs co-founder
  [ ] Reconcile two probability models (generate_model.py vs MEMORY.md)
  [ ] Reframe all investor docs: "CodeGuard now, multi-artifact roadmap"

PRIORITY 2 (before angel round):
  [ ] Build milestone P&L at $1M / $5M / $10M ARR (Sheet 6 above -- DONE)
  [ ] Get 10-15 buyer validation conversations (Kristen's network)
  [ ] Secure 1-3 design partners or paid pilots
  [ ] Build PLG conversion funnel (pricing page, upgrade path, billing)
  [ ] Document first measured unit economics (even from design partners)
  [ ] Create board packet template (Sheet structure from this document)

PRIORITY 3 (before Series A, if applicable):
  [ ] 12+ months of measured retention data (NRR, GRR)
  [ ] Measured CAC and CAC payback from real sales cycles
  [ ] Pipeline with stage definitions, dollarized, with conversion rates
  [ ] Audited financial statements (GAAP)
  [ ] Rule of 40 trajectory demonstrated
```

---

## SHEET 11: OPERATOR DOCTRINE -- WEEKLY/MONTHLY CADENCE

(Source: Michaela Lehr P&L Walkthrough, adapted for GuardSpine pre-revenue stage)

```
Operating principle: Run the business on driver metrics (weekly),
reconcile to board metrics (monthly), keep a standing "trust ledger"
that explains variance, timing, and definition changes before anyone asks.

WEEKLY CADENCE (operator control loop -- starts NOW, pre-revenue)
==================================================================

REVENUE ENGINE (forward-looking):
  [ ] New pipeline created: # prospects contacted, # responded
  [ ] Active evaluations: who, stage, next action, blockers
  [ ] GitHub Action installs (when live): weekly delta
  [ ] Deal quality flags: any non-standard terms discussed?
  [ ] Outreach messages sent vs weekly budget (10-20 max)

DELIVERY / RECOGNITION READINESS:
  [ ] Product blockers: what's not shippable? ETA?
  [ ] Time-to-first-value estimate for next prospect
  [ ] CI/CD pipeline status (737 tests passing? any regressions?)
  [ ] Deploy readiness: can a prospect install and run today?

RETENTION / EXPANSION (once customers exist):
  [ ] Customer health: usage, engagement, ticket severity
  [ ] Expansion signals: new use cases, team growth, tier upgrade interest
  [ ] Churn risk: any conversations indicating dissatisfaction?

CASH & RUNWAY:
  [ ] Cash balance (bank account)
  [ ] Net burn this week (actual spend vs budget)
  [ ] Collections status: any invoices >30 days?
  [ ] Forecast accuracy: did last week's predictions hold?

MONTHLY CADENCE (board-grade package -- starts at angel close)
===============================================================

TOP LINE (board view):
  ARR / MRR: ending, net new, gross adds, expansion, contraction, churn
  GAAP revenue vs plan (and bridge explaining ARR-to-GAAP gap)
  Bookings vs plan + bookings mix (term length, discounting)

REVENUE QUALITY:
  NRR and GRR (once 6+ months of data exist)
  Renewal rate (separate from retention for multi-year)
  Cohort retention (by quarter of start)

MARGINS:
  Gross margin overall + by tier (Pro vs Business vs Enterprise)
  COGS breakdown: hosting, support, cognitive license
  Any COGS surprises (cloud cost spikes, support burden)

OPEX EFFICIENCY:
  S&M / R&D / G&A as % of ARR (or revenue)
  CAC payback (standard definition) + LTV:CAC
  Rule of 40 (once >$1M ARR -- meaningless before that)

CASH DISCIPLINE:
  Operating cash flow, runway remaining
  DSO / collections aging
  Hiring plan vs actual + ROI narrative for each hire

TRUST LEDGER (see Sheet 13):
  Any metric definition changes this month
  Any reclassifications or one-time adjustments
  Why they don't change underlying reality
```

---

## SHEET 12: LEADING INDICATORS PER P&L LINE

(Source: Operator Doctrine framework, mapped to GuardSpine specifics)

```
1) REVENUE (GAAP) -- "recognizable value delivered"
   Leading indicators for GuardSpine:
   - GitHub Action install rate (top of PLG funnel)
   - Time from install to first evidence bundle (activation)
   - Time from demo to contract signature (sales cycle length)
   - Implementation velocity: TTFV for paid tier onboarding
   Interpretation: If installs are growing but activations are flat,
   the free product isn't delivering value. Fix onboarding first.

2) ARR (non-GAAP top line) -- "committed recurring base"
   Leading indicators:
   - Qualified bookings that are ARR-eligible (annual contracts, no TFC)
   - Renewal pipeline coverage for next 2 quarters
   - Expansion signals: new guard lanes enabled, seat growth
   Interpretation: Contract structure can disqualify ARR even when
   "sales celebrates." Watch for trials, TFC clauses, custom terms.

3) COGS -- "cost to run and deliver the product"
   Leading indicators:
   - Cloud cost per active customer (should decline with scale)
   - Support tickets per customer, severity, hours per ticket
   - Cognitive attestation license cost vs Enterprise revenue
   Interpretation: BYOK eliminates the biggest COGS line (LLM API).
   Watch for hosting cost creep and support burden per customer.

4) GROSS MARGIN -- "fuel available to fund growth"
   Leading indicators:
   - Tier mix (Enterprise = 91.25% vs Pro = 87.5%)
   - Services attach rate (currently zero -- keep it that way)
   - Hosting cost optimization (reserved instances, right-sizing)
   Interpretation: GuardSpine's 87-91% GM is STRUCTURAL (BYOK).
   This is the #1 investor story. Protect it. Never take on LLM costs.

5) S&M -- "cost to create and close demand"
   Leading indicators:
   - Pipeline creation efficiency ($ pipeline per outreach hour)
   - Win rate and sales cycle time
   - Discount depth (NEVER >10% per generate_model.py)
   - Rep productivity (founder-led now, track for when AEs hired)
   Interpretation: S&M spend can look "right" even when CAC is bad
   if ramp timing is explained. Track time-to-productivity for hires.

6) R&D -- "rate of product capability creation"
   Leading indicators:
   - Shipped features vs planned (guard lanes, integrations)
   - Test pass rate (currently 428/428 = 100%)
   - Customer-request closure rate for top renewal drivers
   - CI pipeline reliability
   Interpretation: Under-investing in R&D improves EBITDA short-term
   while detonating retention later. 2-person eng team is lean.

7) G&A -- "org overhead and control systems"
   Leading indicators:
   - Close process health (forecast accuracy, days to close)
   - Compliance readiness for enterprise procurement (SOC2, etc.)
   - Billing/collections performance
   Interpretation: "Lean G&A" is good until it breaks controls,
   slows collections, or creates audit surprises.

8) EBITDA / OPERATING MARGIN -- "operational profitability"
   Leading indicators:
   - Margin trend over 3 months (improving? stable? degrading?)
   - Operating leverage: revenue growth vs headcount growth
   - One-time items tracked separately
   Interpretation: Boards tolerate losses if the path to leverage
   is coherent and consistently measured. $10K/mo founder salaries
   demonstrate commitment and extend runway -- good narrative.
```

---

## SHEET 13: TRUST LEDGER (Initial Entry)

(Source: Operator Doctrine failure mode #1 -- metric definition drift)

```
PURPOSE: Track every change to metric definitions, reclassifications,
and one-time adjustments. Show the board BEFORE they ask. Consistency
is the currency of credibility. Surprises destroy trust.

DATE        ITEM                        OLD VALUE    NEW VALUE    WHY
==========  ==========================  ===========  ===========  ==================
2026-02-18  Round size                  $300K        $1,000,000   Updated terms
2026-02-18  Pre-money valuation         $10M ($15M?) $9,000,000   Updated terms
2026-02-18  Dilution %                  3% (6.25%?)  10%          Updated terms
2026-02-18  Monthly burn target         $40K/mo      $26.5K       Founders $10K/mo + AI APIs $2K
2026-02-18  David salary                $15K/mo      $10K/mo      Agreed with Igor
2026-02-18  Igor salary                 $12.5K/mo    $10K/mo      Agreed with David
2026-02-18  Runway (at $26.5K burn)     25 months    37.7 months  Lower burn rate + AI APIs
2026-03-02  Kristen compensation        $8K/mo?      $0/mo        RESOLVED: 2% equity, no cash, no AI budget
(pending)   BOOTSTRAP_PATH valuation    $15M pre     $9M pre      Must update code

TOP 10 FAILURE MODES (from Operator Doctrine, applied to GuardSpine)
=====================================================================

1. METRIC DEFINITION DRIFT [ACTIVE RISK]
   Two probability models exist (generate_model.py vs MEMORY.md).
   Round terms are stale in code. Fix before investor sees generate_model.py.

2. BOOKINGS CELEBRATED, REVENUE DISAPPOINTS [NOT YET APPLICABLE]
   Pre-revenue. But watch for: design partner "handshakes" counted as bookings
   before contract is signed.

3. RETENTION WEAKNESS RATIONALIZED AS "CS PROBLEM" [NOT YET]
   No customers to retain. When first churn happens, do root-cause analysis
   across ICP fit, sales quality, product value, and onboarding.

4. GROSS MARGIN EROSION HIDDEN BEHIND GROWTH [LOW RISK]
   BYOK makes this structurally hard. But watch cognitive attestation license
   costs if Enterprise tier grows faster than expected.

5. RECLASSIFICATIONS AS CAMOUFLAGE [LOW RISK]
   At 3-5 people, no complex classification decisions. But document early
   choices about CS in COGS vs S&M so they don't create surprises later.

6. PIPELINE OPTICS WITHOUT INTEGRITY [ACTIVE RISK]
   139 prospects is not $X pipeline. Need dollarized, staged pipeline with
   time-in-stage tracking. Brent Foster and Phil Venables are real signals,
   but 2 conversations is not "pipeline coverage."

7. CAC PAYBACK DETERIORATION WITH NO RAMP NARRATIVE [FUTURE RISK]
   When first AEs are hired, CAC will spike. Have the narrative ready:
   "Ramp time is X months, productivity curve shows Y."

8. DISCOUNTING AS HIDDEN CHURN [WATCH]
   generate_model.py says "never discount >10%." Enforce this.
   Design partner pricing should be documented as temporary, not permanent.

9. CASH SURPRISES [MANAGED]
   $10K/mo founder salaries + $3K AI APIs + $1M raise = 36+ months runway.
   Cash risk is LOW. But track pre-raise personal cash position.

10. "ONE-TIME" BECOMES HABITUAL [NOT YET]
    No history yet. Start clean. Log everything in this ledger.
```

---

## BEAR/BULL SCENARIO BOUNDS (for sensitivity analysis)

```
                            BEAR           BASE           BULL
                            (pessimistic)  (plan)         (optimistic)
==========================  =============  =============  =============
Y1 customers (ending)       5              37             80
Y1 avg ACV                  $18,000        $30,000        $50,000
Y1 ending ARR               $90K           $1.3M          $4.0M
Y1 GAAP revenue              $45K           $650K          $2.0M

Y2 ending ARR               $300K          $8.0M          $25.0M
Y3 ending ARR               $1.0M          $25.0M         $80.0M

Growth rate (mo, initial)   8%             15%            20%
Growth decay (annual)       15%            20%            15%
NRR                         110%           120%           130%

Breakeven month             M18-24         M5-7           M3-4
Runway consumed before BE   $440-600K      $140-220K      $70-120K

Probability of scenario     ~25%           ~50%           ~25%
Source: generate_model.py SCENARIOS + REVENUE_MILESTONES
```
