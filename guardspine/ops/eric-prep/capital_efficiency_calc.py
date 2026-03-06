"""Capital Efficiency Model: Do we actually need more than $1M pre-seed?
Uses 98% margins + $26.5K burn from 04-financial-math.md"""

# === CONSTANTS FROM DOCS ===
DAVID_PAY = 10000       # $/mo
IGOR_PAY = 10000        # $/mo
OPS = 6500              # $/mo (infra, tools, AI APIs for 2 people -- Kristen removed)
KRISTEN = 0             # 2% equity, no cash, no AI budget (agreed Mar 2)

BURN_BASE = DAVID_PAY + IGOR_PAY + OPS           # $26,500
BURN_FULL = BURN_BASE                              # $26,500 (no Kristen cash component)

# Tier economics (from doc)
TIERS = {
    'Starter': {'price_mo': 499, 'cogs_mo': 15, 'margin': 0.970},
    'Team':    {'price_mo': 2000, 'cogs_mo': 50, 'margin': 0.975},
    'Org':     {'price_mo': 12000, 'cogs_mo': 200, 'margin': 0.983},
    'Enterprise': {'price_mo': 50000, 'cogs_mo': 500, 'margin': 0.990},
}

raise_amount = 1_000_000

print("=" * 70)
print("WHERE DOES $1M GO?")
print("=" * 70)
print(f"David:    ${DAVID_PAY:,}/mo")
print(f"Igor:     ${IGOR_PAY:,}/mo")
print(f"Ops:      ${OPS:,}/mo")
print(f"Kristen:  ${KRISTEN:,}/mo (optional)")
print(f"Base burn: ${BURN_BASE:,}/mo")
print(f"Full burn: ${BURN_FULL:,}/mo")
print()
print(f"$1M / ${BURN_BASE:,} = {raise_amount/BURN_BASE:.0f} months runway (base)")
print(f"$1M / ${BURN_FULL:,} = {raise_amount/BURN_FULL:.0f} months runway (full)")
print()

# === MONTH-BY-MONTH CASH FLOW MODEL ===
# After-Logan projections: close rate 8-15%, Y1 ~$937K ARR target
# Assume linear ramp: 0 customers month 1, building to ~60 by month 12
# Customer mix: 70% Starter, 20% Team, 8% Org, 2% Enterprise (early stage = Starter-heavy)

print("=" * 70)
print("MONTH-BY-MONTH CASH FLOW (After Logan, $1M pre-seed only)")
print("=" * 70)

# Customer acquisition ramp (cumulative)
# Month 1-3: building pipeline, few closes
# Month 4-6: cognitive probes not yet live, moderate closes
# Month 7-12: probes live, close rate kicks in

def customers_at_month(m):
    if m <= 3:
        return max(0, m * 2)        # 2, 4, 6 cumulative
    elif m <= 6:
        return 6 + (m - 3) * 4      # 10, 14, 18
    elif m <= 12:
        return 18 + (m - 6) * 7     # 25, 32, 39, 46, 53, 60
    elif m <= 24:
        return 60 + (m - 12) * 8    # organic + reinvestment growth
    elif m <= 36:
        return 60 + 12*8 + (m - 24) * 12  # accelerating with marketing spend
    else:
        return 60 + 12*8 + 12*12 + (m - 36) * 15

# Revenue per customer (blended, early = Starter-heavy)
def mrr_per_customer(m):
    # Early: mostly Starter. Over time, upgrades to Team/Org
    if m <= 6:
        # 80% Starter, 15% Team, 4% Org, 1% Enterprise
        return 0.80*499 + 0.15*2000 + 0.04*12000 + 0.01*50000
    elif m <= 12:
        # 70% Starter, 20% Team, 8% Org, 2% Enterprise
        return 0.70*499 + 0.20*2000 + 0.08*12000 + 0.02*50000
    elif m <= 24:
        # Mix shifts as upgrades happen: 55% Starter, 25% Team, 15% Org, 5% Enterprise
        return 0.55*499 + 0.25*2000 + 0.15*12000 + 0.05*50000
    else:
        # Mature: 40% Starter, 25% Team, 25% Org, 10% Enterprise
        return 0.40*499 + 0.25*2000 + 0.25*12000 + 0.10*50000

def cogs_per_customer(m):
    if m <= 6:
        return 0.80*15 + 0.15*50 + 0.04*200 + 0.01*500
    elif m <= 12:
        return 0.70*15 + 0.20*50 + 0.08*200 + 0.02*500
    elif m <= 24:
        return 0.55*15 + 0.25*50 + 0.15*200 + 0.05*500
    else:
        return 0.40*15 + 0.25*50 + 0.25*200 + 0.10*500

# Should we pay Kristen? Yes if we can afford it
def burn_at_month(m, mrr):
    if mrr > 40000 or m <= 18:  # Pay Kristen from start or when revenue supports it
        return BURN_FULL
    return BURN_BASE

# Marketing budget: whatever is left after burn, capped at reasonable amounts
# Early: $0 (surviving on pre-seed). After breakeven: reinvest margins.

print(f"{'Mo':>4} {'Cust':>5} {'MRR':>10} {'COGS':>8} {'Gross':>10} {'Burn':>9} {'Mktg':>8} {'Net':>10} {'Bank':>12}")
print("-" * 80)

bank = raise_amount
breakeven_month = None
marketing_total = 0
first_hire_month = None

for m in range(1, 49):
    cust = customers_at_month(m)
    mrr = cust * mrr_per_customer(m)
    cogs = cust * cogs_per_customer(m)
    gross = mrr - cogs
    burn = burn_at_month(m, mrr)

    # Marketing: reinvest excess after burn
    excess = gross - burn
    if excess > 0:
        # Reinvest 60% of excess into marketing, keep 40% as buffer
        mktg = excess * 0.60
        # Can hire first sales rep when marketing budget sustains $8K/mo
        if mktg >= 8000 and first_hire_month is None:
            first_hire_month = m
    else:
        mktg = 0

    marketing_total += mktg
    net = gross - burn - mktg
    bank += net

    if breakeven_month is None and gross >= burn:
        breakeven_month = m

    if m <= 24 or m % 6 == 0:
        print(f"{m:>4} {cust:>5} ${mrr:>9,.0f} ${cogs:>6,.0f} ${gross:>9,.0f} ${burn:>8,.0f} ${mktg:>7,.0f} ${net:>9,.0f} ${bank:>11,.0f}")

print()
print(f"Breakeven month: {breakeven_month}")
print(f"First sales hire affordable (month): {first_hire_month}")
print(f"Cumulative marketing spend by M24: ${marketing_total:,.0f}")
print()

# === ARR TRAJECTORY (pre-seed only path) ===
print("=" * 70)
print("ARR AT KEY POINTS (Pre-seed only, organic growth)")
print("=" * 70)

for m in [6, 12, 18, 24, 30, 36, 42, 48]:
    cust = customers_at_month(m)
    mrr = cust * mrr_per_customer(m)
    arr = mrr * 12
    print(f"  Month {m:>2} (Y{m/12:.1f}): {cust:>4} customers, ${mrr:,.0f}/mo MRR, ${arr/1000:,.0f}K ARR")

print()

# === OWNERSHIP COMPARISON ===
print("=" * 70)
print("DAVID $50M: VC PATH vs CAPITAL-EFFICIENT PATH")
print("=" * 70)

paths = [
    ("Pre-seed only (45%)", 0.45, "Organic growth, no further dilution"),
    ("+ Seed (36%)", 0.36, "One raise for sales acceleration"),
    ("+ Series A (27%)", 0.27, "Two raises for market expansion"),
    ("Full VC through C (19%)", 0.19, "Traditional VC path"),
]

print(f"{'Path':<30} {'David %':>8} {'Exit for $50M':>14} {'ARR at 12x':>12}")
print("-" * 66)
for name, pct, desc in paths:
    exit_val = 50 / pct
    arr_needed = exit_val / 12
    print(f"{name:<30} {pct:>7.1%} ${exit_val:>12.1f}M ${arr_needed:>10.1f}M")

print()
print("$1B EXIT:")
print(f"{'Path':<30} {'David %':>8} {'David gets':>12} {'ARR at 12x':>12}")
print("-" * 64)
for name, pct, desc in paths:
    david_gets = 1000 * pct
    arr_needed = 1000 / 12
    print(f"{name:<30} {pct:>7.1%} ${david_gets:>10.1f}M ${arr_needed:>10.1f}M")

print()

# === PROBABILITY RECOMPUTE ===
print("=" * 70)
print("PROBABILITY: CAPITAL-EFFICIENT PATH (fewer gates)")
print("=" * 70)

# VC Path (from previous calc):
# P($50M) = P(raise) * P($1M ARR) * P(raise follow-on) * P($15M ARR) * P(exit $185M+)
# = 0.356 * 0.398 * 0.55 = 7.8%

# Capital-efficient path:
# Fewer gates! No "raise follow-on" gate. Just:
# G1: Raise pre-seed ($1M)
# G2: Reach $10M ARR organically (harder without VC $, but no fundraising risk)
# G3: Exit at $111M+ (lower bar!)

p_raise = 0.647  # after Logan improvement
p_1m_arr = 0.55  # same
p_10m_arr_organic = 0.40  # harder than funded, but 98% margins help
p_exit_111m = 0.60  # lower bar = higher probability

p_50m_efficient = p_raise * p_1m_arr * p_10m_arr_organic * p_exit_111m
p_50m_vc = 0.078  # from previous calc

# Hybrid: raise pre-seed, maybe one small seed ($500K-$1M for 8-10%)
# David at ~40% after small seed
p_10m_arr_hybrid = 0.50  # easier with some extra capital
p_exit_125m = 0.58  # $50M / 0.40 = $125M needed
p_50m_hybrid = p_raise * p_1m_arr * p_10m_arr_hybrid * p_exit_125m

print(f"VC Path (raise through Series A):")
print(f"  P(David $50M) = {p_50m_vc*100:.1f}%")
print(f"  David owns 27% at exit, needs $185M exit = $15.4M ARR at 12x")
print()
print(f"Capital-Efficient Path (pre-seed only):")
print(f"  P(raise) * P($1M ARR) * P($10M ARR organic) * P($111M+ exit)")
print(f"  = {p_raise:.3f} * {p_1m_arr:.2f} * {p_10m_arr_organic:.2f} * {p_exit_111m:.2f}")
print(f"  P(David $50M) = {p_50m_efficient*100:.1f}%")
print(f"  David owns 45% at exit, needs $111M exit = $9.3M ARR at 12x")
print()
print(f"Hybrid Path (pre-seed + small seed, ~40% ownership):")
print(f"  P(David $50M) = {p_50m_hybrid*100:.1f}%")
print(f"  David owns ~40% at exit, needs $125M exit = $10.4M ARR at 12x")
print()

# $1B comparison
print(f"$1B EXIT COMPARISON:")
p_1b_vc = 0.0147  # from previous calc
# Capital-efficient: need $83M ARR at 12x for $1B. Organic is hard.
p_100m_arr_organic = 0.12  # very hard without VC funding for sales team
p_1b_exit_organic = 0.45
p_1b_efficient = p_raise * p_1m_arr * p_10m_arr_organic * 0.30 * p_1b_exit_organic
# Hybrid
p_1b_hybrid = p_raise * p_1m_arr * p_10m_arr_hybrid * 0.35 * p_1b_exit_organic

print(f"  VC Path:              {p_1b_vc*100:.2f}%  (David gets $190M at 19%)")
print(f"  Capital-Efficient:    {p_1b_efficient*100:.2f}%  (David gets $450M at 45%)")
print(f"  Hybrid:               {p_1b_hybrid*100:.2f}%  (David gets $400M at 40%)")
print()

# === THE REAL INSIGHT ===
print("=" * 70)
print("THE MATH YOUR MARGINS UNLOCK")
print("=" * 70)
print()
print("Traditional SaaS needs VC because margins are 70-80% and burn is high.")
print("You have 98% margins and $26.5K burn. Revenue IS your growth capital.")
print()
print("At 98% margin, every $1 of MRR = $0.98 available for reinvestment.")
print(f"At $55K MRR (breakeven): $0 available -- covers burn only.")
print(f"At $100K MRR: ${(100000*0.98 - BURN_FULL):,.0f}/mo for marketing/sales hires.")
print(f"At $200K MRR: ${(200000*0.98 - BURN_FULL):,.0f}/mo for marketing/sales hires.")
print(f"At $500K MRR: ${(500000*0.98 - BURN_FULL):,.0f}/mo for marketing/sales hires.")
print()
print("Once past breakeven, you're self-funding a sales team without dilution.")
print(f"A $8K/mo sales rep is affordable at ~${(BURN_FULL + 8000)/0.98:,.0f} MRR ({(BURN_FULL + 8000)/0.98/499:.0f} Starter-equivalents).")
print(f"A $15K/mo sales lead is affordable at ~${(BURN_FULL + 15000)/0.98:,.0f} MRR.")
print()
print("CONCLUSION:")
print(f"  $50M David: Capital-efficient path ({p_50m_efficient*100:.1f}%) BEATS VC path ({p_50m_vc*100:.1f}%)")
print(f"  $1B exit:   VC path ({p_1b_vc*100:.2f}%) beats capital-efficient ({p_1b_efficient*100:.2f}%)")
print(f"              because $1B requires scale that takes VC-level sales spend.")
print(f"  BEST OF BOTH: Hybrid path -- small seed for acceleration, keep ~40%.")
print(f"              $50M: {p_50m_hybrid*100:.1f}% | $1B: {p_1b_hybrid*100:.2f}%")
