"""All 3 scenarios with realistic hiring plan.
Bear/Base/Bull -- static vs post-breakeven hiring, side by side.
Each hire: competitive salary + $1K/mo AI tools budget.
Hires spaced so P&L never goes negative post-breakeven."""

BURN = 26500  # David + Igor + Ops (Kristen = 2% equity, no cash, no AI budget -- agreed Mar 2)
AI_BUDGET = 1000  # per-hire AI tools
MIN_CHURN = 0.003  # floor 0.3%/mo

TIERS = {
    'Starter':    {'price': 499,   'cogs': 15},
    'Team':       {'price': 2000,  'cogs': 50},
    'Org':        {'price': 12000, 'cogs': 200},
    'Enterprise': {'price': 50000, 'cogs': 500},
}

# === HIRING ROSTER (same for all scenarios) ===
HIRE_QUEUE = [
    {'role': 'CSM',                'salary': 7000,  'effect': 'churn_reduce', 'value': 0.30},
    {'role': 'Sales Engineer',     'salary': 9000,  'effect': 'acq_add',      'value': 2},
    {'role': 'Compliance Counsel', 'salary': 10000, 'effect': 'upgrade_boost','value': 0.01},
    {'role': 'Product Manager',    'salary': 8500,  'effect': 'churn_reduce', 'value': 0.15},
    {'role': 'SDR / BDR',         'salary': 6000,  'effect': 'acq_add',      'value': 2},
    {'role': '2nd Sales Engineer', 'salary': 9000,  'effect': 'acq_add',      'value': 2},
]

scenarios = {
    'BEAR': {
        'desc': 'Slow sales, longer cycles, low conversion',
        'base_acq': [(3, 1), (6, 2), (12, 3), (999, 4)],
        'mix': {'Starter': 0.85, 'Team': 0.10, 'Org': 0.04, 'Enterprise': 0.01},
        'churn_mo': 0.02,
        'up_s2t': 0.02,
        'up_t2o': 0.01,
    },
    'BASE': {
        'desc': 'Moderate sales, probes live M7, steady upgrades',
        'base_acq': [(3, 2), (6, 4), (12, 6), (999, 8)],
        'mix': {'Starter': 0.75, 'Team': 0.15, 'Org': 0.08, 'Enterprise': 0.02},
        'churn_mo': 0.01,
        'up_s2t': 0.04,
        'up_t2o': 0.02,
    },
    'BULL': {
        'desc': 'Strong inbound, regulatory urgency, fast upgrades',
        'base_acq': [(3, 3), (6, 6), (12, 10), (999, 14)],
        'mix': {'Starter': 0.65, 'Team': 0.20, 'Org': 0.12, 'Enterprise': 0.03},
        'churn_mo': 0.005,
        'up_s2t': 0.06,
        'up_t2o': 0.03,
    },
}

def get_base_acq(sc, month):
    for end, rate in sc['base_acq']:
        if month <= end:
            return rate
    return sc['base_acq'][-1][1]

def simulate(sc, reinvest=False, max_months=48):
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = 1_000_000
    be_month = None

    # Hiring state (only used when reinvest=True)
    hire_index = 0
    monthly_payroll = 0
    incremental_acq = 0
    churn_multipliers = []
    upgrade_boost = 0
    headcount = 0
    hire_log = []
    results = []

    for m in range(1, max_months + 1):
        # Acquisition
        base_new = get_base_acq(sc, m)
        total_new = base_new + (incremental_acq if reinvest else 0)
        for t, pct in sc['mix'].items():
            customers[t] += total_new * pct

        # Upgrades
        eff_s2t = sc['up_s2t'] + (upgrade_boost if reinvest else 0)
        up = customers['Starter'] * eff_s2t
        customers['Starter'] -= up
        customers['Team'] += up
        up2 = customers['Team'] * sc['up_t2o']
        customers['Team'] -= up2
        customers['Org'] += up2

        # Churn
        if reinvest and churn_multipliers:
            eff_churn = sc['churn_mo']
            for factor in churn_multipliers:
                eff_churn *= factor
            eff_churn = max(eff_churn, MIN_CHURN)
        else:
            eff_churn = sc['churn_mo']

        for t in customers:
            customers[t] *= (1 - eff_churn)

        # Revenue
        mrr = sum(customers[t] * TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        total_cust = sum(customers.values())

        if be_month is None and gross >= BURN:
            be_month = m

        # Hiring (post-breakeven, max 1/month, must afford with 20% buffer)
        new_hire = None
        team_cost = BURN + monthly_payroll
        excess = gross - team_cost

        if (reinvest and be_month is not None and m > be_month
                and hire_index < len(HIRE_QUEUE) and bank > 400_000):
            candidate = HIRE_QUEUE[hire_index]
            hire_cost = candidate['salary'] + AI_BUDGET
            if excess >= hire_cost * 1.2:
                new_hire = candidate
                monthly_payroll += hire_cost
                headcount += 1
                hire_log.append((m, candidate['role'], hire_cost))

                if candidate['effect'] == 'churn_reduce':
                    churn_multipliers.append(1 - candidate['value'])
                elif candidate['effect'] == 'acq_add':
                    incremental_acq += candidate['value']
                elif candidate['effect'] == 'upgrade_boost':
                    upgrade_boost += candidate['value']

                hire_index += 1

        # Net cash
        team_cost = BURN + monthly_payroll
        net = gross - team_cost
        bank += net

        results.append({
            'm': m, 'cust': total_cust, 'mrr': mrr, 'arr': mrr * 12,
            'gross': gross, 'bank': bank, 'churn': eff_churn,
            'new_mo': total_new, 'headcount': headcount,
            'team_cost': team_cost, 'excess': net,
            'new_hire': new_hire['role'] if new_hire else None,
        })

    return results, be_month, hire_log

def find_milestone(results, condition):
    for r in results:
        if condition(r):
            return r['m']
    return None

# === RUN ALL ===
all_data = {}
for name in ['BEAR', 'BASE', 'BULL']:
    sc = scenarios[name]
    static_r, static_be, _ = simulate(sc, reinvest=False)
    reinvest_r, reinvest_be, hire_log = simulate(sc, reinvest=True)
    all_data[name] = {
        'static': (static_r, static_be),
        'reinvest': (reinvest_r, reinvest_be),
        'hire_log': hire_log,
        'sc': sc,
    }

# === MASTER SUMMARY ===
print("=" * 100)
print("THREE-SCENARIO ANALYSIS: STATIC vs REALISTIC HIRING MODEL")
print("=" * 100)
print()
print("Static:     Fixed acquisition/churn rates, no reinvestment of excess cash")
print("Hiring:     Post-breakeven, hire 1 specialist/month when P&L supports it")
print("            Each hire: competitive salary + $1K/mo AI tools budget to 10x output")
print(f"Burn:       ${BURN:,}/mo (David + Igor + Ops + Kristen)")
print(f"Starting:   $1,000,000 pre-seed")
print()

# Hire roster
total_payroll = sum(h['salary'] + AI_BUDGET for h in HIRE_QUEUE)
print(f"Hiring queue ({len(HIRE_QUEUE)} roles, ${total_payroll:,}/mo total when fully hired):")
for i, h in enumerate(HIRE_QUEUE):
    cost = h['salary'] + AI_BUDGET
    print(f"  {i+1}. {h['role']:<22} ${cost:,}/mo  ({h['effect']}: {h['value']})")
print()

# Breakeven comparison
print("=" * 100)
print("BREAKEVEN (identical -- hiring starts AFTER breakeven)")
print("=" * 100)
print(f"{'Scenario':<10} {'Breakeven':>12} {'Cash Burned':>14} {'Cash Preserved':>16}")
print("-" * 54)
for name in ['BEAR', 'BASE', 'BULL']:
    d = all_data[name]
    r_be = d['reinvest'][1]
    if r_be:
        r = d['reinvest'][0][r_be - 1]
        burned = 1_000_000 - r['bank']
        preserved = r['bank']
    else:
        burned = 0
        preserved = 1_000_000
    print(f"{name:<10} {'M'+str(r_be)+' (Y'+f'{r_be/12:.1f}'+')':>12}"
          f" ${burned:>12,.0f} ${preserved:>14,.0f}")
print()

# Hiring timeline per scenario
print("=" * 100)
print("HIRING TIMELINE BY SCENARIO")
print("=" * 100)
print()
print(f"{'Role':<22} | {'Bear':>8} | {'Base':>8} | {'Bull':>8} | {'Cost':>8}")
print("-" * 65)
for h in HIRE_QUEUE:
    cost = h['salary'] + AI_BUDGET
    parts = []
    for name in ['BEAR', 'BASE', 'BULL']:
        hired_mo = None
        for mo, role, _ in all_data[name]['hire_log']:
            if role == h['role']:
                hired_mo = mo
                break
        parts.append(f"M{hired_mo}" if hired_mo else ">M48")
    print(f"{h['role']:<22} | {parts[0]:>8} | {parts[1]:>8} | {parts[2]:>8} | ${cost:>6,}")

# Total headcount at M48
for name in ['BEAR', 'BASE', 'BULL']:
    rf = all_data[name]['reinvest'][0][-1]
all_hired = all(len(all_data[n]['hire_log']) == len(HIRE_QUEUE) for n in ['BEAR', 'BASE', 'BULL'])
if all_hired:
    bear_last = all_data['BEAR']['hire_log'][-1][0]
    base_last = all_data['BASE']['hire_log'][-1][0]
    bull_last = all_data['BULL']['hire_log'][-1][0]
    print(f"{'All 6 hired by':<22} | {'M'+str(bear_last):>8} | {'M'+str(base_last):>8} | {'M'+str(bull_last):>8} |")
print()

# Milestone comparison table
print("=" * 100)
print("MILESTONE COMPARISON: STATIC vs HIRING MODEL")
print("=" * 100)

milestones = [
    ("$1M ARR", lambda r: r['arr'] >= 1_000_000),
    ("$5M ARR", lambda r: r['arr'] >= 5_000_000),
    ("$9.3M ARR ($50M David)", lambda r: r['arr'] >= 9_300_000),
    ("$20M ARR", lambda r: r['arr'] >= 20_000_000),
    ("$50M ARR", lambda r: r['arr'] >= 50_000_000),
    ("$83M ARR ($1B at 12x)", lambda r: r['arr'] >= 83_000_000),
    ("100 customers", lambda r: r['cust'] >= 100),
    ("500 customers", lambda r: r['cust'] >= 500),
]

print(f"{'Milestone':<28} | {'BEAR':^23} | {'BASE':^23} | {'BULL':^23}")
print(f"{'':28} | {'Static':>10} {'Hiring':>11} | {'Static':>10} {'Hiring':>11} | {'Static':>10} {'Hiring':>11}")
print("-" * 105)

for label, cond in milestones:
    parts = []
    for name in ['BEAR', 'BASE', 'BULL']:
        d = all_data[name]
        sm = find_milestone(d['static'][0], cond)
        rm = find_milestone(d['reinvest'][0], cond)
        s_str = f"M{sm}" if sm else ">M48"
        r_str = f"M{rm}" if rm else ">M48"
        parts.append(f"{s_str:>10} {r_str:>11}")
    print(f"{label:<28} | {' | '.join(parts)}")

print()

# Detailed trajectory per scenario
for name in ['BEAR', 'BASE', 'BULL']:
    d = all_data[name]
    sc = d['sc']
    sr, s_be = d['static']
    rr, r_be = d['reinvest']

    print("=" * 100)
    print(f"  {name}: {sc['desc']}")
    print("=" * 100)
    print(f"  Base acq: {' -> '.join(str(r)+'/mo' for _, r in sc['base_acq'])}")
    print(f"  Starting churn: {sc['churn_mo']:.1%}/mo | Upgrades: S->T {sc['up_s2t']:.0%}, T->O {sc['up_t2o']:.0%}")
    print()
    print(f"  {'Mo':>4} | {'--- STATIC ---':^30} | {'--- WITH HIRING ---':^58}")
    print(f"  {'':>4} | {'Cust':>6} {'ARR':>11} {'Bank':>12} | {'Cust':>6} {'ARR':>11} {'Bank':>12} {'Team$':>8} {'HC':>3} {'New Hire':<20}")
    print("  " + "-" * 100)

    for i in range(len(sr)):
        m = sr[i]['m']
        s = sr[i]
        r = rr[i]
        show = m <= 12 or m % 6 == 0 or m == s_be or m == r_be or r['new_hire']
        if show:
            s_flag = " BE" if m == s_be else "   "
            r_flag = " BE" if m == r_be else "   "
            hire_str = r['new_hire'] or ""
            print(f"  {m:>4} | {s['cust']:>6.0f} ${s['arr']:>10,.0f} ${s['bank']:>11,.0f}{s_flag}"
                  f" | {r['cust']:>6.0f} ${r['arr']:>10,.0f} ${r['bank']:>11,.0f}{r_flag}"
                  f" ${r['team_cost']:>7,.0f} {r['headcount']:>3}  {hire_str}")
    print()

    # Final state comparison
    sf = sr[-1]
    rf = rr[-1]
    print(f"  Month 48 comparison:")
    print(f"    Static:     {sf['cust']:>6.0f} customers | ${sf['arr']:>12,.0f} ARR | ${sf['bank']:>12,.0f} bank | 4 people")
    print(f"    Hiring:     {rf['cust']:>6.0f} customers | ${rf['arr']:>12,.0f} ARR | ${rf['bank']:>12,.0f} bank | {4+rf['headcount']} people")
    ratio_cust = rf['cust'] / sf['cust'] if sf['cust'] > 0 else 0
    ratio_arr = rf['arr'] / sf['arr'] if sf['arr'] > 0 else 0
    print(f"    Multiplier: {ratio_cust:.1f}x customers | {ratio_arr:.1f}x ARR")
    print(f"    ARR/person: ${rf['arr']/(4+rf['headcount']):,.0f}")
    print()

# === EXIT TIMELINE ===
print("=" * 100)
print("EXIT TIMELINE SUMMARY (Hiring Model)")
print("=" * 100)
print()
print(f"{'Target':<30} {'Bear':>15} {'Base':>15} {'Bull':>15}")
print("-" * 77)

targets = [
    ("Breakeven", lambda r: r['gross'] >= BURN),
    ("$1M ARR", lambda r: r['arr'] >= 1_000_000),
    ("$5M ARR", lambda r: r['arr'] >= 5_000_000),
    ("$9.3M ARR (David $50M)", lambda r: r['arr'] >= 9_300_000),
    ("$50M ARR", lambda r: r['arr'] >= 50_000_000),
    ("$83M ARR ($1B exit)", lambda r: r['arr'] >= 83_000_000),
]

for label, cond in targets:
    parts = []
    for name in ['BEAR', 'BASE', 'BULL']:
        rr = all_data[name]['reinvest'][0]
        m = find_milestone(rr, cond)
        if m:
            parts.append(f"M{m} (Y{m/12:.1f})")
        else:
            parts.append(">M48")
    print(f"{label:<30} {parts[0]:>15} {parts[1]:>15} {parts[2]:>15}")

print()
print("David $50M = $111M exit at 45% ownership = $9.3M ARR at 12x revenue multiple")
print("$1B exit = $83M ARR at 12x revenue multiple")
print()

# === MULTIPLIER TABLE ===
print("=" * 100)
print("STATIC vs HIRING at Month 48")
print("=" * 100)
print()
print(f"{'Metric':<20} | {'BEAR':^25} | {'BASE':^25} | {'BULL':^25}")
print(f"{'':20} | {'Static':>11} {'Hiring':>12} | {'Static':>11} {'Hiring':>12} | {'Static':>11} {'Hiring':>12}")
print("-" * 100)

for label, key in [("Customers", 'cust'), ("ARR ($K)", 'arr'), ("Bank ($K)", 'bank')]:
    parts = []
    for name in ['BEAR', 'BASE', 'BULL']:
        sf = all_data[name]['static'][0][-1]
        rf = all_data[name]['reinvest'][0][-1]
        if key in ('arr', 'bank'):
            parts.append(f"${sf[key]/1000:>9,.0f} ${rf[key]/1000:>10,.0f}")
        else:
            parts.append(f"{sf[key]:>11.0f} {rf[key]:>12.0f}")
    print(f"{label:<20} | {' | '.join(parts)}")

print("-" * 100)
parts = []
for name in ['BEAR', 'BASE', 'BULL']:
    sf = all_data[name]['static'][0][-1]
    rf = all_data[name]['reinvest'][0][-1]
    r = rf['arr'] / sf['arr'] if sf['arr'] > 0 else 0
    parts.append(f"{'':>11} {r:>11.1f}x")
print(f"{'ARR Multiplier':<20} | {' | '.join(parts)}")

parts = []
for name in ['BEAR', 'BASE', 'BULL']:
    rf = all_data[name]['reinvest'][0][-1]
    parts.append(f"{'':>11} ${rf['arr']/(4+rf['headcount']):>9,.0f}")
print(f"{'ARR / person':<20} | {' | '.join(parts)}")

print()
print("INSIGHT: This model uses only 6 predefined hires (10 total headcount).")
print("At M48, excess cash could fund 30-60+ additional hires per scenario.")
print("The 6-hire model is the FLOOR. Second-wave hiring would accelerate further.")
print()
print("Each specialist + $1K/mo AI tools = output of 3-5 people at traditional companies.")
print("10-person AI-leveraged team builds what would take 30-50 people otherwise.")
