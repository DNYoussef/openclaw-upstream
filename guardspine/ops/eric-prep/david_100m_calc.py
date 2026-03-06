"""David $100M exit calculator.
Cap table: David 40% / Igor 40% / Kristen 2% / Angel 10% / Pool 8%
Exit multiple: 30x (strategic acquirer: Vanta / ServiceNow / Microsoft)
Burn: $26.5K/mo"""

DAVID_PCT = 0.40
MULTIPLE = 30

print("=" * 80)
print("DAVID $100M EXIT MATH")
print("Cap table: David 40% | Igor 40% | Kristen 2% | Angel 10% | Pool 8%")
print("Exit multiple: 30x (strategic acquirer: Vanta / ServiceNow / Microsoft)")
print("=" * 80)
print()

targets_personal = [50e6, 75e6, 100e6, 150e6, 200e6]
print("PERSONAL TARGET -> ARR NEEDED (at 40% ownership, 30x multiple)")
print("-" * 65)
print(f"{'David Gets':<18} {'Exit Valuation':>15} {'ARR Needed':>15} {'MRR Needed':>15}")
print("-" * 65)
for p in targets_personal:
    exit_val = p / DAVID_PCT
    arr = exit_val / MULTIPLE
    mrr = arr / 12
    print(f"${p/1e6:,.0f}M {' '*6}${exit_val/1e6:,.0f}M {' '*6}${arr/1e6:,.1f}M {' '*6}${mrr/1e3:,.0f}K")

print()
print("Igor gets the SAME numbers (also 40%).")
print(f"Kristen at 2%: $5M at $250M exit, $10M at $500M exit.")
print(f"Angel at 10%: $25M at $250M exit (25x return on $1M).")
print()

TARGET_ARR = 8_333_333
print("=" * 80)
print("THE KEY NUMBER: $8.33M ARR = David $100M = Igor $100M")
print("=" * 80)
print()

TIERS_ARR = {'Starter': 5988, 'Team': 24000, 'Org': 144000, 'Enterprise': 600000}

mixes = [
    ("Current model (early)",    {'Starter': 0.55, 'Team': 0.25, 'Org': 0.15, 'Enterprise': 0.05}),
    ("Maturing (Y2-3)",          {'Starter': 0.40, 'Team': 0.30, 'Org': 0.22, 'Enterprise': 0.08}),
    ("Enterprise gravity (Y3+)", {'Starter': 0.30, 'Team': 0.28, 'Org': 0.30, 'Enterprise': 0.12}),
]

print("CUSTOMER BLENDS TO HIT $8.33M ARR:")
print()
for name, mix in mixes:
    arpa = sum(mix[t] * TIERS_ARR[t] for t in mix)
    n = TARGET_ARR / arpa
    print(f"  {name} (ARPA ${arpa:,.0f})")
    s, t, o, e = n*mix['Starter'], n*mix['Team'], n*mix['Org'], n*mix['Enterprise']
    print(f"    {n:.0f} total: {s:.0f} Starter + {t:.0f} Team + {o:.0f} Org + {e:.0f} Enterprise")
    print()

print("  Single-tier extremes:")
for t, arr in TIERS_ARR.items():
    print(f"    {t} only: {TARGET_ARR / arr:.0f} customers")
print()

# === SIMULATION ===
BURN = 26500
SIM_TIERS = {
    'Starter': {'price': 499, 'cogs': 15},
    'Team': {'price': 2000, 'cogs': 50},
    'Org': {'price': 12000, 'cogs': 200},
    'Enterprise': {'price': 50000, 'cogs': 500},
}

scenarios = {
    'BEAR': {
        'burn': BURN, 'churn_mo': 0.02,
        'upgrade_starter_to_team': 0.02, 'upgrade_team_to_org': 0.01,
        'new_customers': [(3, 1), (6, 2), (12, 3), (999, 4)],
        'mix': {'Starter': 0.85, 'Team': 0.10, 'Org': 0.04, 'Enterprise': 0.01},
    },
    'BASE': {
        'burn': BURN, 'churn_mo': 0.01,
        'upgrade_starter_to_team': 0.04, 'upgrade_team_to_org': 0.02,
        'new_customers': [(3, 2), (6, 4), (12, 6), (999, 8)],
        'mix': {'Starter': 0.75, 'Team': 0.15, 'Org': 0.08, 'Enterprise': 0.02},
    },
    'BULL': {
        'burn': BURN, 'churn_mo': 0.005,
        'upgrade_starter_to_team': 0.06, 'upgrade_team_to_org': 0.03,
        'new_customers': [(3, 3), (6, 6), (12, 10), (999, 14)],
        'mix': {'Starter': 0.65, 'Team': 0.20, 'Org': 0.12, 'Enterprise': 0.03},
    },
}

def get_new(sc, m):
    for (end, rate) in sc['new_customers']:
        if m <= end: return rate
    return sc['new_customers'][-1][1]

def simulate(sc, max_m=60):
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = 1_000_000
    results = []
    for m in range(1, max_m + 1):
        new = get_new(sc, m)
        for t, pct in sc['mix'].items():
            customers[t] += new * pct
        up = customers['Starter'] * sc['upgrade_starter_to_team']
        customers['Starter'] -= up; customers['Team'] += up
        up = customers['Team'] * sc['upgrade_team_to_org']
        customers['Team'] -= up; customers['Org'] += up
        for t in customers:
            customers[t] *= (1 - sc['churn_mo'])
        mrr = sum(customers[t] * SIM_TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * SIM_TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        excess = gross - sc['burn']
        mktg = max(0, excess * 0.60) if excess > 0 else 0
        bank += gross - sc['burn'] - mktg
        results.append({
            'm': m, 'arr': mrr * 12, 'mrr': mrr,
            'cust': sum(customers.values()), 'bank': bank,
            'customers': dict(customers),
        })
    return results

arr_milestones = [
    ("David/Igor $50M each",  4_170_000),
    ("David/Igor $100M each", 8_330_000),
    ("David/Igor $150M each", 12_500_000),
    ("David/Igor $200M each", 16_670_000),
]

print("=" * 80)
print("TIMELINE: When do you hit each target? (Bear / Base / Bull)")
print("=" * 80)
print()
print(f"{'Personal Target':<28} {'BEAR':>14} {'BASE':>14} {'BULL':>14}")
print("-" * 72)

for label, target_arr in arr_milestones:
    row = [label]
    for name in ['BEAR', 'BASE', 'BULL']:
        results = simulate(scenarios[name], 60)
        found = False
        for r in results:
            if r['arr'] >= target_arr:
                row.append(f"M{r['m']} (Y{r['m']/12:.1f})")
                found = True
                break
        if not found:
            last = results[-1]
            row.append(f">M60 (${last['arr']/1e6:.1f}M)")
    print(f"{row[0]:<28} {row[1]:>14} {row[2]:>14} {row[3]:>14}")

print()
print("=" * 80)
print("SNAPSHOT AT $8.33M ARR (David/Igor $100M each)")
print("=" * 80)
print()

for name in ['BEAR', 'BASE', 'BULL']:
    results = simulate(scenarios[name], 60)
    for r in results:
        if r['arr'] >= 8_330_000:
            c = r['customers']
            exit_val = r['arr'] / 1e6 * 30
            print(f"{name}: Month {r['m']} (Year {r['m']/12:.1f})")
            print(f"  Customers: {r['cust']:.0f} total ({c['Starter']:.0f}S / {c['Team']:.0f}T / {c['Org']:.0f}O / {c['Enterprise']:.0f}E)")
            print(f"  ARR: ${r['arr']/1e6:.1f}M | MRR: ${r['mrr']/1e3:.0f}K")
            print(f"  Cash in bank: ${r['bank']/1e6:.1f}M")
            print(f"  Exit at 30x: ${exit_val:.0f}M")
            print(f"    David (40%):   ${exit_val * 0.40:.0f}M")
            print(f"    Igor (40%):    ${exit_val * 0.40:.0f}M")
            print(f"    Kristen (2%):  ${exit_val * 0.02:.1f}M")
            print(f"    Angel (10%):   ${exit_val * 0.10:.0f}M ({exit_val * 0.10:.0f}x return)")
            print(f"    Pool (8%):     ${exit_val * 0.08:.1f}M")
            print()
            break
    else:
        last = results[-1]
        print(f"{name}: Not reached by M60 (at ${last['arr']/1e6:.1f}M ARR)")
        print(f"  Would need ~M{60 * 8_330_000 / last['arr']:.0f} at current trajectory")
        print()

# Everyone's payout table at key exit valuations
print("=" * 80)
print("PAYOUT TABLE AT KEY EXIT VALUATIONS (30x multiple)")
print("=" * 80)
print()
print(f"{'ARR':<10} {'Exit Val':<12} {'David 40%':<12} {'Igor 40%':<12} {'Kristen 2%':<12} {'Angel 10%':<12} {'Pool 8%':<10}")
print("-" * 80)
for arr_m in [5, 8.33, 10, 15, 20, 30, 50]:
    ev = arr_m * 30
    print(f"${arr_m:<8.1f}M ${ev:<10.0f}M ${ev*0.40:<10.0f}M ${ev*0.40:<10.0f}M ${ev*0.02:<10.1f}M ${ev*0.10:<10.0f}M ${ev*0.08:<8.1f}M")
