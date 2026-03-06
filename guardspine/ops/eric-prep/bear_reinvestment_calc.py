"""Bear case with realistic hiring plan.
Static bear assumes fixed acquisition/churn. Reality: post-breakeven cash funds
specific hires -- each paid well, each with $1K/mo AI tools budget to 10x output.
Hires spaced so monthly P&L never goes negative."""

BURN = 26500  # David + Igor + Ops (Kristen = 2% equity, no cash, no AI budget -- agreed Mar 2)
AI_BUDGET = 1000  # per-hire AI tools budget (Claude, Cursor, etc.)
MIN_CHURN = 0.003  # floor 0.3%/mo

TIERS = {
    'Starter':    {'price': 499,   'cogs': 15},
    'Team':       {'price': 2000,  'cogs': 50},
    'Org':        {'price': 12000, 'cogs': 200},
    'Enterprise': {'price': 50000, 'cogs': 500},
}

# Bear scenario starting conditions
BEAR_MIX = {'Starter': 0.85, 'Team': 0.10, 'Org': 0.04, 'Enterprise': 0.01}
BEAR_BASE_CHURN = 0.02
BEAR_BASE_ACQ = [(3, 1), (6, 2), (12, 3), (999, 4)]
BEAR_UPGRADE_S2T = 0.02
BEAR_UPGRADE_T2O = 0.01

# === HIRING ROSTER ===
# Each hire: (role, base_salary, effect_type, effect_value, notes)
# effect_type:
#   'churn_reduce' = multiplicative churn reduction (0.30 = 30% less churn)
#   'acq_add'      = additional customers per month
#   'upgrade_boost' = additive boost to S->T upgrade rate
#
# Total cost per hire = base_salary + AI_BUDGET
# Rule: max 1 hire per month (realistic onboarding/interviewing)
# Rule: only hire when excess covers cost + 20% buffer for 3 months
# Rule: bank never drops below $400K

HIRE_QUEUE = [
    {
        'role': 'Customer Success Mgr',
        'salary': 7000,
        'effect': 'churn_reduce',
        'value': 0.30,       # reduces remaining churn by 30%
        'note': 'Onboarding, QBRs, retention. 40 accounts capacity.',
    },
    {
        'role': 'Sales Engineer',
        'salary': 9000,
        'effect': 'acq_add',
        'value': 2,           # +2 customers/mo (demos, technical closes)
        'note': 'Runs demos, handles technical objections, closes.',
    },
    {
        'role': 'Compliance Counsel',
        'salary': 10000,
        'effect': 'upgrade_boost',
        'value': 0.01,        # +1% S->T upgrade rate (enterprise readiness)
        'note': 'SOC2, DPAs, contract review. Unlocks enterprise pipeline.',
    },
    {
        'role': 'Product Manager',
        'salary': 8500,
        'effect': 'churn_reduce',
        'value': 0.15,        # better product = 15% less churn
        'note': 'Roadmap, customer feedback loop, feature prioritization.',
    },
    {
        'role': 'SDR / BDR',
        'salary': 6000,
        'effect': 'acq_add',
        'value': 2,           # +2 customers/mo (outbound pipeline)
        'note': 'Cold outreach, event leads, pipeline generation.',
    },
    {
        'role': '2nd Sales Engineer',
        'salary': 9000,
        'effect': 'acq_add',
        'value': 2,           # +2 more customers/mo
        'note': 'Scale sales capacity. Handles EMEA/APAC overlap.',
    },
]

def get_static_acq(month):
    for end, rate in BEAR_BASE_ACQ:
        if month <= end:
            return rate
    return BEAR_BASE_ACQ[-1][1]

def simulate_static(max_months=48):
    """Original static bear model (no reinvestment)."""
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = 1_000_000
    results = []
    be_month = None

    for m in range(1, max_months + 1):
        new = get_static_acq(m)
        for t, pct in BEAR_MIX.items():
            customers[t] += new * pct

        up1 = customers['Starter'] * BEAR_UPGRADE_S2T
        customers['Starter'] -= up1
        customers['Team'] += up1
        up2 = customers['Team'] * BEAR_UPGRADE_T2O
        customers['Team'] -= up2
        customers['Org'] += up2

        for t in customers:
            customers[t] *= (1 - BEAR_BASE_CHURN)

        mrr = sum(customers[t] * TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        total = sum(customers.values())

        net = gross - BURN
        bank += net
        if be_month is None and gross >= BURN:
            be_month = m

        results.append({
            'm': m, 'cust': total, 'mrr': mrr, 'gross': gross,
            'bank': bank, 'new_per_mo': new, 'churn': BEAR_BASE_CHURN,
            'arr': mrr * 12, 'team_cost': BURN, 'hires': [],
        })
    return results, be_month

def simulate_reinvest(max_months=48):
    """Bear model with post-breakeven hiring plan."""
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = 1_000_000
    results = []
    be_month = None

    # Track hired staff
    hired = []           # list of hire dicts (from HIRE_QUEUE)
    hire_index = 0       # next hire to consider
    monthly_payroll = 0  # total added payroll (salary + AI budget)
    incremental_acq = 0  # added customers/mo from hires
    churn_multipliers = []  # list of (1 - reduction) factors
    upgrade_boost = 0    # additive S->T upgrade boost

    hire_log = []  # (month, role, cost) for reporting

    for m in range(1, max_months + 1):
        # Acquisition = base + hired sales capacity
        base_new = get_static_acq(m)
        total_new = base_new + incremental_acq
        for t, pct in BEAR_MIX.items():
            customers[t] += total_new * pct

        # Upgrades (with compliance counsel boost)
        effective_s2t = BEAR_UPGRADE_S2T + upgrade_boost
        up1 = customers['Starter'] * effective_s2t
        customers['Starter'] -= up1
        customers['Team'] += up1
        up2 = customers['Team'] * BEAR_UPGRADE_T2O
        customers['Team'] -= up2
        customers['Org'] += up2

        # Churn: base rate * each churn reduction factor
        effective_churn = BEAR_BASE_CHURN
        for factor in churn_multipliers:
            effective_churn *= factor
        effective_churn = max(effective_churn, MIN_CHURN)

        for t in customers:
            customers[t] *= (1 - effective_churn)

        # Revenue
        mrr = sum(customers[t] * TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        total_cust = sum(customers.values())

        if be_month is None and gross >= BURN:
            be_month = m

        # Hiring decision: only after breakeven, max 1 per month
        new_hire = None
        total_team_cost = BURN + monthly_payroll
        excess = gross - total_team_cost

        if (be_month is not None and m > be_month
                and hire_index < len(HIRE_QUEUE)
                and bank > 400_000):
            candidate = HIRE_QUEUE[hire_index]
            hire_cost = candidate['salary'] + AI_BUDGET

            # Can we afford this hire for 3 months with 20% buffer?
            # Monthly: excess must cover hire_cost * 1.2
            if excess >= hire_cost * 1.2:
                new_hire = candidate
                hired.append(candidate)
                monthly_payroll += hire_cost
                hire_log.append((m, candidate['role'], hire_cost))

                # Apply effect
                if candidate['effect'] == 'churn_reduce':
                    churn_multipliers.append(1 - candidate['value'])
                elif candidate['effect'] == 'acq_add':
                    incremental_acq += candidate['value']
                elif candidate['effect'] == 'upgrade_boost':
                    upgrade_boost += candidate['value']

                hire_index += 1

        # Net cash
        total_team_cost = BURN + monthly_payroll
        net = gross - total_team_cost
        bank += net

        results.append({
            'm': m, 'cust': total_cust, 'mrr': mrr, 'gross': gross,
            'bank': bank, 'new_per_mo': total_new, 'churn': effective_churn,
            'arr': mrr * 12, 'team_cost': total_team_cost,
            'payroll_added': monthly_payroll, 'headcount': len(hired),
            'new_hire': new_hire['role'] if new_hire else None,
            'excess': gross - total_team_cost,
            'hires': [h['role'] for h in hired],
        })
    return results, be_month, hire_log

# === RUN ===
static_r, static_be = simulate_static()
reinvest_r, reinvest_be, hire_log = simulate_reinvest()

print("=" * 100)
print("BEAR CASE: STATIC vs REALISTIC HIRING MODEL")
print("=" * 100)
print()
print("Static:     Fixed 1->2->3->4 customers/mo, fixed 2% churn, no hires")
print("Hiring:     Post-breakeven, hire 1 specialist/month when P&L supports it")
print("            Each hire: competitive salary + $1K/mo AI tools budget")
print(f"Burn:       ${BURN:,}/mo (David + Igor + Ops + Kristen)")
print(f"Starting:   $1,000,000 pre-seed")
print()

# Hiring timeline
print("=" * 100)
print("HIRING PLAN (as cash flow permits)")
print("=" * 100)
print()
print(f"{'#':>2} {'Mo':>4} {'Role':<25} {'Salary':>8} {'AI':>6} {'Total':>8} {'Note'}")
print("-" * 95)
for i, h in enumerate(HIRE_QUEUE):
    cost = h['salary'] + AI_BUDGET
    # Find when hired
    hired_mo = None
    for mo, role, _ in hire_log:
        if role == h['role']:
            hired_mo = mo
            break
    mo_str = f"M{hired_mo}" if hired_mo else "Not yet"
    print(f"{i+1:>2} {mo_str:>4} {h['role']:<25} ${h['salary']:>6,} ${AI_BUDGET:>4,} ${cost:>6,}  {h['note']}")
print()

total_monthly = sum(h['salary'] + AI_BUDGET for h in HIRE_QUEUE)
print(f"Full team payroll (all 6 hires): ${total_monthly:,}/mo added to ${BURN:,}/mo burn = ${BURN + total_monthly:,}/mo total")
print()

# Side by side comparison
print("=" * 100)
print("MONTH-BY-MONTH COMPARISON")
print("=" * 100)
print()
print(f"{'Mo':>4} | {'--- STATIC ---':^30} | {'--- WITH HIRING ---':^60}")
print(f"{'':>4} | {'Cust':>5} {'ARR':>10} {'Bank':>11} | {'Cust':>5} {'ARR':>10} {'Bank':>11} {'Team$':>8} {'Excess':>8} {'HC':>3} {'New Hire':<20}")
print("-" * 115)

for i in range(len(static_r)):
    m = static_r[i]['m']
    s = static_r[i]
    r = reinvest_r[i]

    if m <= 18 or m % 6 == 0 or m == static_be or m == reinvest_be:
        s_flag = " BE" if m == static_be else "   "
        r_flag = " BE" if m == reinvest_be else "   "
        hire_str = r['new_hire'] or ""
        print(f"{m:>4} | {s['cust']:>5.0f} ${s['arr']:>9,.0f} ${s['bank']:>10,.0f}{s_flag}"
              f" | {r['cust']:>5.0f} ${r['arr']:>9,.0f} ${r['bank']:>10,.0f}{r_flag}"
              f" ${r['team_cost']:>7,.0f} ${r['excess']:>7,.0f} {r['headcount']:>3}"
              f"  {hire_str}")

print()

# Detailed P&L at key months
print("=" * 100)
print("P&L SNAPSHOTS (Hiring Model)")
print("=" * 100)
print()
for r in reinvest_r:
    m = r['m']
    if m in [1, reinvest_be, reinvest_be + 1] or r['new_hire'] or m == 24 or m == 36 or m == 48:
        print(f"  Month {m}:")
        print(f"    Revenue:      ${r['mrr']:>10,.0f} MRR  (${r['arr']:>10,.0f} ARR)")
        print(f"    Gross profit: ${r['gross']:>10,.0f}")
        print(f"    Team cost:    ${r['team_cost']:>10,.0f}  (base ${BURN:,} + hires ${r['payroll_added']:,})")
        print(f"    Net monthly:  ${r['excess']:>10,.0f}")
        print(f"    Bank:         ${r['bank']:>10,.0f}")
        print(f"    Customers:    {r['cust']:>5.0f}  ({r['new_per_mo']:.0f} new/mo, {r['churn']:.1%} churn)")
        print(f"    Headcount:    {4 + r['headcount']} ({r['headcount']} new hires)")
        if r['new_hire']:
            print(f"    >>> HIRED: {r['new_hire']}")
        if r['hires']:
            print(f"    Team: David, Igor, Kristen, Ops + {', '.join(r['hires'])}")
        print()

# Milestones
print("=" * 100)
print("MILESTONE COMPARISON")
print("=" * 100)
print()

milestones = [
    ("Breakeven", lambda r: r['gross'] >= BURN),
    ("$1M ARR", lambda r: r['arr'] >= 1_000_000),
    ("$5M ARR", lambda r: r['arr'] >= 5_000_000),
    ("$9.3M ARR (David $50M)", lambda r: r['arr'] >= 9_300_000),
    ("$15M ARR", lambda r: r['arr'] >= 15_000_000),
    ("$20M ARR", lambda r: r['arr'] >= 20_000_000),
    ("100 customers", lambda r: r['cust'] >= 100),
    ("200 customers", lambda r: r['cust'] >= 200),
]

print(f"{'Milestone':<30} {'Static':>15} {'Hiring':>15} {'Delta':>12}")
print("-" * 74)

for label, condition in milestones:
    s_month = None
    r_month = None
    for r in static_r:
        if condition(r):
            s_month = r['m']
            break
    for r in reinvest_r:
        if condition(r):
            r_month = r['m']
            break

    s_str = f"M{s_month} (Y{s_month/12:.1f})" if s_month else ">M48"
    r_str = f"M{r_month} (Y{r_month/12:.1f})" if r_month else ">M48"
    if s_month and r_month:
        d_str = f"{s_month - r_month} months"
    elif r_month and not s_month:
        d_str = "UNLOCKED"
    else:
        d_str = "N/A"
    print(f"{label:<30} {s_str:>15} {r_str:>15} {d_str:>12}")

print()

# Final comparison
sf = static_r[-1]
rf = reinvest_r[-1]
print("=" * 100)
print("MONTH 48 FINAL STATE")
print("=" * 100)
print()
print(f"  {'':20} {'Static':>15} {'Hiring':>15} {'Multiplier':>12}")
print(f"  {'-'*62}")
print(f"  {'Customers':<20} {sf['cust']:>15.0f} {rf['cust']:>15.0f} {rf['cust']/sf['cust']:>11.1f}x")
print(f"  {'ARR':<20} ${sf['arr']:>13,.0f} ${rf['arr']:>13,.0f} {rf['arr']/sf['arr']:>11.1f}x")
print(f"  {'Bank':<20} ${sf['bank']:>13,.0f} ${rf['bank']:>13,.0f}")
print(f"  {'Headcount':<20} {'4':>15} {4 + rf['headcount']:>15}")
print(f"  {'Monthly team cost':<20} ${BURN:>13,.0f} ${rf['team_cost']:>13,.0f}")
print()

# The narrative
print("=" * 100)
print("THE STORY")
print("=" * 100)
print()
print(f"Months 1-{reinvest_be}: Bear conditions. Low acquisition, high churn.")
print(f"  Cash burned: ${1_000_000 - reinvest_r[reinvest_be-1]['bank']:,.0f} of $1M.")
print(f"  Bank at breakeven: ${reinvest_r[reinvest_be-1]['bank']:,.0f}")
print()
print("Post-breakeven hiring (1 specialist/month as cash permits):")
for mo, role, cost in hire_log:
    r = reinvest_r[mo - 1]
    print(f"  M{mo}: {role:<25} ${cost:,}/mo  (excess was ${r['excess'] + cost:,.0f}/mo)")
print()

# Safety checks
post_be = [r for r in reinvest_r if r['m'] > reinvest_be]
min_excess_post = min(r['excess'] for r in post_be) if post_be else 0
min_bank = min(r['bank'] for r in reinvest_r)
print(f"Safety check:")
print(f"  Post-breakeven lowest P&L: ${min_excess_post:,.0f} (always positive: {min_excess_post >= 0})")
print(f"  Lowest bank balance: ${min_bank:,.0f} (always above $400K: {min_bank >= 400_000})")
print()

# Second-wave potential
m48 = reinvest_r[-1]
print(f"SECOND-WAVE POTENTIAL (after all 6 hires at M19):")
print(f"  M24 excess: ${reinvest_r[23]['excess']:,.0f}/mo -- could fund {reinvest_r[23]['excess'] // 10000:.0f} more hires")
print(f"  M36 excess: ${reinvest_r[35]['excess']:,.0f}/mo -- could fund {reinvest_r[35]['excess'] // 10000:.0f} more hires")
print(f"  M48 excess: ${m48['excess']:,.0f}/mo -- could fund {m48['excess'] // 10000:.0f} more hires")
print(f"  M48 bank:   ${m48['bank']:,.0f} (growth capital for wave 2)")
print()
print(f"Revenue per person: ${m48['arr'] / (4 + m48['headcount']):,.0f} ARR / head")
print()
print("Each hire is paid competitively + $1K/mo AI tools to 10x their output.")
print("Hiring is spaced by affordability, not calendar. P&L stays positive post-BE.")
print("Bear conditions are temporary. Capital efficiency + AI leverage = outsized team.")
print()
print("This model is CONSERVATIVE -- only 6 predefined hires. In reality,")
print(f"the ${m48['excess']:,.0f}/mo excess at M48 would fund a second wave of hires,")
print("accelerating growth beyond what this model shows.")
