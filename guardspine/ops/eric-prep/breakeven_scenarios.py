"""Breakeven scenario analysis: Bear, Base, Bull
Uses established models from 04-financial-math.md + Logan moat"""

# === CONSTANTS ===
DAVID = 10000
IGOR = 10000
OPS = 6500   # infra + legal + software + AI APIs (2 people x $1K, Kristen removed)
KRISTEN = 0  # 2% equity, no cash, no AI budget (agreed Mar 2)
BURN_BASE = DAVID + IGOR + OPS          # $26,500
BURN_FULL = BURN_BASE                    # $26,500 (no Kristen cash component)

# Tier pricing
TIERS = {
    'Starter':    {'price': 499,   'cogs': 15},
    'Team':       {'price': 2000,  'cogs': 50},
    'Org':        {'price': 12000, 'cogs': 200},
    'Enterprise': {'price': 50000, 'cogs': 500},
}

# === SCENARIO DEFINITIONS ===
# Each scenario defines:
#   - Monthly customer acquisition rate by phase
#   - Customer mix (what % land at each tier)
#   - Upgrade rate (monthly % of Starter->Team, Team->Org)
#   - Churn rate (monthly)
#   - Whether Kristen is paid from start
#   - Description of what drives this scenario

scenarios = {
    'BEAR': {
        'desc': 'Slow sales, longer cycles, low conversion, no probe premium yet',
        'burn': BURN_FULL,  # still paying Kristen (committed)
        'churn_mo': 0.02,   # 2%/mo = ~22% annual (high for early stage)
        'upgrade_starter_to_team': 0.02,  # 2%/mo of Starter upgrade
        'upgrade_team_to_org': 0.01,      # 1%/mo of Team upgrade
        # New customer acquisition per month by phase
        # Phase 1 (M1-3): pipeline building, almost no closes
        # Phase 2 (M4-6): first closes trickling in
        # Phase 3 (M7-12): probes launch but adoption slow
        # Phase 4 (M13+): steady but unspectacular
        'new_customers': [
            (3, 1),    # M1-3: 1 new/mo
            (6, 2),    # M4-6: 2 new/mo
            (12, 3),   # M7-12: 3 new/mo
            (999, 4),  # M13+: 4 new/mo
        ],
        # Landing mix: mostly Starter
        'mix': {'Starter': 0.85, 'Team': 0.10, 'Org': 0.04, 'Enterprise': 0.01},
    },
    'BASE': {
        'desc': 'Moderate sales, Logan probes live M7, steady upgrades',
        'burn': BURN_FULL,
        'churn_mo': 0.01,   # 1%/mo = ~11% annual
        'upgrade_starter_to_team': 0.04,  # 4%/mo
        'upgrade_team_to_org': 0.02,      # 2%/mo
        'new_customers': [
            (3, 2),    # M1-3: 2 new/mo
            (6, 4),    # M4-6: 4 new/mo
            (12, 6),   # M7-12: 6 new/mo (probes live, better demos)
            (999, 8),  # M13+: 8 new/mo (word of mouth + reinvestment)
        ],
        'mix': {'Starter': 0.75, 'Team': 0.15, 'Org': 0.08, 'Enterprise': 0.02},
    },
    'BULL': {
        'desc': 'Strong inbound from probes + regulatory pressure, fast upgrades',
        'burn': BURN_FULL,
        'churn_mo': 0.005,  # 0.5%/mo = ~6% annual
        'upgrade_starter_to_team': 0.06,  # 6%/mo
        'upgrade_team_to_org': 0.03,      # 3%/mo
        'new_customers': [
            (3, 3),    # M1-3: 3 new/mo
            (6, 6),    # M4-6: 6 new/mo
            (12, 10),  # M7-12: 10 new/mo (EU AI Act urgency + probe demos)
            (999, 14), # M13+: 14 new/mo (flywheel spinning)
        ],
        'mix': {'Starter': 0.65, 'Team': 0.20, 'Org': 0.12, 'Enterprise': 0.03},
    },
}

def get_new_per_month(scenario, month):
    for (end_month, rate) in scenario['new_customers']:
        if month <= end_month:
            return rate
    return scenario['new_customers'][-1][1]

def simulate(name, sc, max_months=48):
    """Simulate month-by-month with per-tier customer tracking."""
    burn = sc['burn']
    mix = sc['mix']
    churn = sc['churn_mo']
    up_s2t = sc['upgrade_starter_to_team']
    up_t2o = sc['upgrade_team_to_org']

    # Track customer count per tier
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = 1_000_000
    breakeven_month = None
    cashout_month = None

    results = []

    for m in range(1, max_months + 1):
        # 1. New customer acquisition
        new = get_new_per_month(sc, m)
        for tier, pct in mix.items():
            customers[tier] += new * pct

        # 2. Upgrades (applied to existing base)
        # Starter -> Team
        upgraded_s2t = customers['Starter'] * up_s2t
        customers['Starter'] -= upgraded_s2t
        customers['Team'] += upgraded_s2t

        # Team -> Org
        upgraded_t2o = customers['Team'] * up_t2o
        customers['Team'] -= upgraded_t2o
        customers['Org'] += upgraded_t2o

        # 3. Churn (applied uniformly)
        for tier in customers:
            customers[tier] *= (1 - churn)

        # 4. Revenue
        mrr = sum(customers[t] * TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        total_cust = sum(customers.values())

        # 5. Marketing reinvestment (60% of excess after burn)
        excess = gross - burn
        mktg = max(0, excess * 0.60) if excess > 0 else 0

        # 6. Cash
        net = gross - burn - mktg
        bank += net

        if breakeven_month is None and gross >= burn:
            breakeven_month = m

        if cashout_month is None and bank <= 0:
            cashout_month = m

        results.append({
            'm': m, 'cust': total_cust, 'mrr': mrr, 'cogs': cogs,
            'gross': gross, 'burn': burn, 'mktg': mktg, 'net': net,
            'bank': bank, 'customers': dict(customers),
        })

    return results, breakeven_month, cashout_month

# === RUN ALL SCENARIOS ===
print("=" * 80)
print("BREAKEVEN SCENARIO ANALYSIS")
print("=" * 80)
print(f"Burn rate: ${BURN_FULL:,}/mo (David + Igor + Ops + Kristen)")
print(f"Breakeven MRR needed: ~${BURN_FULL / 0.98:,.0f} (at 98% margin)")
print(f"Starting cash: $1,000,000")
print()

for name in ['BEAR', 'BASE', 'BULL']:
    sc = scenarios[name]
    results, be_month, co_month = simulate(name, sc)

    print("=" * 80)
    print(f"  {name} SCENARIO: {sc['desc']}")
    print("=" * 80)
    print(f"  New customers/mo: {' -> '.join(str(r) + '/mo (M' + str(e) + ')' for e, r in sc['new_customers'])}")
    print(f"  Landing mix: {', '.join(f'{t} {p:.0%}' for t, p in sc['mix'].items())}")
    print(f"  Monthly churn: {sc['churn_mo']:.1%} ({(1-(1-sc['churn_mo'])**12)*100:.0f}% annual)")
    print(f"  Upgrades: Starter->Team {sc['upgrade_starter_to_team']:.0%}/mo, Team->Org {sc['upgrade_team_to_org']:.0%}/mo")
    print()

    # Print monthly detail
    print(f"  {'Mo':>4} {'Cust':>6} {'S':>5} {'T':>5} {'O':>4} {'E':>3} {'MRR':>10} {'Gross':>10} {'Burn':>9} {'Net':>10} {'Bank':>12}")
    print("  " + "-" * 85)

    for r in results:
        m = r['m']
        c = r['customers']
        if m <= 18 or m % 6 == 0 or m == be_month:
            flag = " <-- BREAKEVEN" if m == be_month else ""
            print(f"  {m:>4} {r['cust']:>6.0f} {c['Starter']:>5.0f} {c['Team']:>5.0f} {c['Org']:>4.0f} {c['Enterprise']:>3.0f} "
                  f"${r['mrr']:>9,.0f} ${r['gross']:>9,.0f} ${r['burn']:>8,.0f} ${r['net']:>9,.0f} ${r['bank']:>11,.0f}{flag}")

    print()
    if be_month:
        be = results[be_month - 1]
        print(f"  BREAKEVEN: Month {be_month} (Y{be_month/12:.1f})")
        print(f"    Customers: {be['cust']:.0f} ({be['customers']['Starter']:.0f}S / {be['customers']['Team']:.0f}T / {be['customers']['Org']:.0f}O / {be['customers']['Enterprise']:.0f}E)")
        print(f"    MRR: ${be['mrr']:,.0f} | ARR: ${be['mrr']*12:,.0f}")
        print(f"    Cash remaining: ${be['bank']:,.0f} of $1M ({be['bank']/1_000_000:.0%} preserved)")
        print(f"    Cash burned to breakeven: ${1_000_000 - be['bank']:,.0f}")
    else:
        if co_month:
            print(f"  WARNING: Cash runs out at month {co_month} (Y{co_month/12:.1f})")
            co = results[co_month - 1]
            print(f"    Customers at cashout: {co['cust']:.0f}")
            print(f"    MRR at cashout: ${co['mrr']:,.0f}")
        else:
            print(f"  Never reaches breakeven in {len(results)} months")
            last = results[-1]
            print(f"    Month {last['m']}: {last['cust']:.0f} customers, ${last['mrr']:,.0f} MRR, ${last['bank']:,.0f} bank")

    print()

    # Milestones
    print(f"  KEY MILESTONES:")
    for target_label, target_arr in [("$1M ARR", 1_000_000), ("$5M ARR", 5_000_000), ("$9.3M ARR (David $50M at 12x)", 9_300_000)]:
        for r in results:
            if r['mrr'] * 12 >= target_arr:
                print(f"    {target_label}: Month {r['m']} (Y{r['m']/12:.1f}) -- {r['cust']:.0f} customers, ${r['bank']:,.0f} in bank")
                break
        else:
            last = results[-1]
            print(f"    {target_label}: Not reached by M{last['m']} (at ${last['mrr']*12:,.0f} ARR)")
    print()

# === SUMMARY TABLE ===
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print(f"{'Scenario':<10} {'Breakeven':>12} {'Cash Burned':>14} {'Cash Left':>12} {'$1M ARR':>10} {'$9.3M ARR':>12}")
print("-" * 72)

for name in ['BEAR', 'BASE', 'BULL']:
    sc = scenarios[name]
    results, be_month, co_month = simulate(name, sc)

    if be_month:
        be = results[be_month - 1]
        burned = 1_000_000 - be['bank']
        be_str = f"M{be_month} (Y{be_month/12:.1f})"
        burned_str = f"${burned:,.0f}"
        left_str = f"${be['bank']:,.0f}"
    else:
        be_str = "NEVER"
        burned_str = "N/A"
        left_str = "$0"

    # Find $1M ARR month
    arr1m = "N/A"
    for r in results:
        if r['mrr'] * 12 >= 1_000_000:
            arr1m = f"M{r['m']} (Y{r['m']/12:.1f})"
            break

    # Find $9.3M ARR month
    arr93m = "N/A"
    for r in results:
        if r['mrr'] * 12 >= 9_300_000:
            arr93m = f"M{r['m']} (Y{r['m']/12:.1f})"
            break

    print(f"{name:<10} {be_str:>12} {burned_str:>14} {left_str:>12} {arr1m:>10} {arr93m:>12}")

print()
print("$9.3M ARR = David $50M exit at 45% ownership, 12x revenue multiple")
print("All scenarios assume $1M pre-seed, no further raises, 98% gross margins")
print("60% of post-burn excess reinvested into marketing/sales")
