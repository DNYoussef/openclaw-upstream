"""Staircase Growth Model v2: Revenue-gated hiring with per-hire MRR attribution.

Mental model (David, Mar 2 2026):
  1. Hit breakeven at $26.5K MRR
  2. Seed capital preserved (minus $100K legal/consulting reserve)
  3. Each hire unlocked when gross profit covers their cost
  4. Each hire accelerates growth through MULTIPLE channels:
     - More customers (acquisition)
     - Better customers (mix shift toward higher tiers)
     - Happier customers (churn reduction)
     - Expanding customers (upgrade rate boosts)
  5. Track each hire's MRR contribution vs. static baseline

Cap table: David 40% / Igor 40% / Kristen 2% / Angel 10% / Pool 8%
"""

# === CONSTANTS ===
BASE_BURN = 26500       # David $10K + Igor $10K + ops $6.5K
LEGAL_RESERVE = 100000  # Legal, consulting, accounting reserve from seed
SEED = 1_000_000
HIRE_SALARY = 10000     # Each hire: $10K/mo salary
HIRE_AI = 1000          # Each hire: $1K/mo AI tools
HIRE_COST = HIRE_SALARY + HIRE_AI  # $11K/mo per hire
HIRE_EQUITY = 0.015     # 1.5% avg per hire (from 8% pool)
MIN_CHURN = 0.003       # Floor: 0.3%/mo

# Tier pricing
TIERS = {
    'Starter':    {'price': 499,   'cogs': 15},
    'Team':       {'price': 2000,  'cogs': 50},
    'Org':        {'price': 12000, 'cogs': 200},
    'Enterprise': {'price': 50000, 'cogs': 500},
}

# Each hire has MULTI-DIMENSIONAL effects on growth
# acq_add:      additional customers/month
# mix_shift:    shift in tier distribution (applied to NEW customers only)
# upgrade_s2t:  additive boost to Starter->Team upgrade rate
# upgrade_t2o:  additive boost to Team->Org upgrade rate
# churn_mult:   multiply effective churn by this (0.7 = 30% reduction)
HIRE_EFFECTS = [
    {
        'role': 'Sales Engineer #1',
        'acq_add': 2.5,
        'mix_shift': {'Starter': -0.10, 'Team': +0.06, 'Org': +0.03, 'Enterprise': +0.01},
        'upgrade_s2t': 0.01,
        'upgrade_t2o': 0.0,
        'churn_mult': 1.0,
        'note': 'Closes deals, shifts mix upmarket. Demo-to-close pipeline.',
    },
    {
        'role': 'Customer Success',
        'acq_add': 0,
        'mix_shift': {},
        'upgrade_s2t': 0.02,
        'upgrade_t2o': 0.01,
        'churn_mult': 0.70,
        'note': 'Retention + expansion. QBRs drive upsell. 30% churn cut.',
    },
    {
        'role': 'SDR / BDR',
        'acq_add': 3.0,
        'mix_shift': {'Starter': -0.03, 'Team': +0.02, 'Org': +0.01},
        'upgrade_s2t': 0.0,
        'upgrade_t2o': 0.0,
        'churn_mult': 1.0,
        'note': 'Outbound pipeline. Slightly better leads than inbound.',
    },
    {
        'role': 'Sales Engineer #2',
        'acq_add': 2.0,
        'mix_shift': {'Starter': -0.08, 'Team': +0.02, 'Org': +0.05, 'Enterprise': +0.01},
        'upgrade_s2t': 0.0,
        'upgrade_t2o': 0.01,
        'churn_mult': 1.0,
        'note': 'Mid-market/enterprise focus. Bigger ACV deals.',
    },
    {
        'role': 'Product / Compliance',
        'acq_add': 0,
        'mix_shift': {'Starter': -0.02, 'Team': -0.01, 'Org': +0.01, 'Enterprise': +0.02},
        'upgrade_s2t': 0.01,
        'upgrade_t2o': 0.01,
        'churn_mult': 0.80,
        'note': 'SOC2/DORA certs. Enterprise-ready. Product quality -> retention.',
    },
    {
        'role': 'Marketing Lead',
        'acq_add': 3.5,
        'mix_shift': {'Starter': -0.05, 'Team': +0.04, 'Org': +0.01},
        'upgrade_s2t': 0.01,
        'upgrade_t2o': 0.0,
        'churn_mult': 1.0,
        'note': 'Content, events, brand. Higher-quality inbound.',
    },
]

# Scenarios (same as david_100m_calc.py)
scenarios = {
    'BEAR': {
        'desc': 'Slow sales, high churn, cautious market',
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


def get_acq(sc, month):
    for end, rate in sc['base_acq']:
        if month <= end:
            return rate
    return sc['base_acq'][-1][1]


def simulate(sc, max_months=60, enable_hiring=True):
    """Run the staircase simulation.

    If enable_hiring=False, runs with founders only (static baseline).
    Returns (results, be_month, hire_log).
    """
    customers = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    bank = SEED
    be_month = None

    # Cumulative hire effects
    hire_index = 0
    monthly_payroll = 0
    headcount = 0
    hire_log = []

    # Accumulated effects from all hires so far
    cum_acq_add = 0.0
    cum_mix_shift = {'Starter': 0, 'Team': 0, 'Org': 0, 'Enterprise': 0}
    cum_upgrade_s2t = 0.0
    cum_upgrade_t2o = 0.0
    cum_churn_mult = 1.0

    results = []

    for m in range(1, max_months + 1):
        # --- ACQUISITION ---
        base_new = get_acq(sc, m)
        total_new = base_new + (cum_acq_add if enable_hiring else 0)

        # Apply cumulative mix shift to new customers
        eff_mix = {}
        for t in sc['mix']:
            shift = cum_mix_shift[t] if enable_hiring else 0
            eff_mix[t] = max(0, sc['mix'][t] + shift)
        # Normalize mix to sum to 1
        mix_total = sum(eff_mix.values())
        if mix_total > 0:
            for t in eff_mix:
                eff_mix[t] /= mix_total

        for t, pct in eff_mix.items():
            customers[t] += total_new * pct

        # --- UPGRADES ---
        eff_s2t = sc['up_s2t'] + (cum_upgrade_s2t if enable_hiring else 0)
        eff_t2o = sc['up_t2o'] + (cum_upgrade_t2o if enable_hiring else 0)

        up = customers['Starter'] * eff_s2t
        customers['Starter'] -= up
        customers['Team'] += up

        up2 = customers['Team'] * eff_t2o
        customers['Team'] -= up2
        customers['Org'] += up2

        # --- CHURN ---
        eff_churn = sc['churn_mo'] * (cum_churn_mult if enable_hiring else 1.0)
        eff_churn = max(eff_churn, MIN_CHURN)
        for t in customers:
            customers[t] *= (1 - eff_churn)

        # --- REVENUE ---
        mrr = sum(customers[t] * TIERS[t]['price'] for t in customers)
        cogs = sum(customers[t] * TIERS[t]['cogs'] for t in customers)
        gross = mrr - cogs
        total_cust = sum(customers.values())

        # Calculate ARPA
        arpa = mrr / total_cust if total_cust > 0 else 0

        # --- BREAKEVEN ---
        if be_month is None and gross >= BASE_BURN:
            be_month = m

        # --- STAIRCASE HIRING ---
        new_hire = None
        if enable_hiring and be_month is not None and m > be_month:
            current_threshold = BASE_BURN + monthly_payroll
            next_threshold = current_threshold + HIRE_COST

            if hire_index < len(HIRE_EFFECTS) and gross >= next_threshold:
                h = HIRE_EFFECTS[hire_index]
                new_hire = h
                monthly_payroll += HIRE_COST
                headcount += 1

                # Apply this hire's effects
                cum_acq_add += h['acq_add']
                for t, shift in h['mix_shift'].items():
                    cum_mix_shift[t] += shift
                cum_upgrade_s2t += h['upgrade_s2t']
                cum_upgrade_t2o += h['upgrade_t2o']
                cum_churn_mult *= h['churn_mult']

                hire_log.append({
                    'month': m,
                    'role': h['role'],
                    'threshold': next_threshold,
                    'mrr_at_hire': mrr,
                    'arr_at_hire': mrr * 12,
                    'cust_at_hire': total_cust,
                    'arpa_at_hire': arpa,
                    'effects': h,
                })
                hire_index += 1

        # --- CASH ---
        team_cost = BASE_BURN + monthly_payroll
        net = gross - team_cost
        bank += net

        results.append({
            'm': m, 'cust': total_cust, 'mrr': mrr, 'arr': mrr * 12,
            'gross': gross, 'bank': bank, 'team_cost': team_cost,
            'net': net, 'headcount': headcount, 'churn': eff_churn,
            'new_per_mo': total_new, 'new_hire': new_hire,
            'monthly_payroll': monthly_payroll, 'arpa': arpa,
            'customers': dict(customers),
            'eff_mix': dict(eff_mix),
        })

    return results, be_month, hire_log


# ====================================================================
# OUTPUT
# ====================================================================
print("=" * 95)
print("STAIRCASE GROWTH MODEL v2: Per-Hire MRR Attribution")
print("Revenue-gated hiring. Each hire accelerates growth through multiple channels.")
print("=" * 95)
print()
print("Cap table: David 40% | Igor 40% | Kristen 2% | Angel 10% | Pool 8%")
print(f"Base burn: ${BASE_BURN:,}/mo | Legal reserve: ${LEGAL_RESERVE:,}")
print(f"Each hire: ${HIRE_COST:,}/mo (${HIRE_SALARY:,} salary + ${HIRE_AI:,} AI tools) + ~1.5% equity")
print()

# Show hire effects
print("HIRE EFFECTS (what each person contributes):")
print("-" * 95)
print(f"  {'#':>2} {'Role':<22} {'Acq':>5} {'Mix Shift':<30} {'Upgr S>T':>8} {'Upgr T>O':>8} {'Churn':>7}")
print("-" * 95)
for i, h in enumerate(HIRE_EFFECTS):
    acq = f"+{h['acq_add']:.1f}" if h['acq_add'] > 0 else "--"
    ms_parts = []
    for t, v in h['mix_shift'].items():
        if v != 0:
            ms_parts.append(f"{t[:3]}{v:+.0%}")
    ms = ", ".join(ms_parts) if ms_parts else "--"
    s2t = f"+{h['upgrade_s2t']:.0%}" if h['upgrade_s2t'] > 0 else "--"
    t2o = f"+{h['upgrade_t2o']:.0%}" if h['upgrade_t2o'] > 0 else "--"
    churn = f"x{h['churn_mult']:.2f}" if h['churn_mult'] < 1.0 else "--"
    threshold = BASE_BURN + HIRE_COST * (i + 1)
    print(f"  {i+1:>2} {h['role']:<22} {acq:>5} {ms:<30} {s2t:>8} {t2o:>8} {churn:>7}  @ ${threshold:,} MRR")
print()

# Staircase thresholds
print("STAIRCASE THRESHOLDS:")
print("-" * 70)
print(f"  Step 0: ${BASE_BURN:>8,} gross profit = Breakeven")
for i, h in enumerate(HIRE_EFFECTS):
    threshold = BASE_BURN + HIRE_COST * (i + 1)
    pool_left = 8.0 - 1.5 * (i + 1)
    print(f"  Step {i+1}: ${threshold:>8,} gross profit = Hire {h['role']:<22} ({pool_left:.1f}% pool left)")
print()


# === RUN SCENARIOS ===
for sc_name in ['BEAR', 'BASE', 'BULL']:
    sc = scenarios[sc_name]

    # Run WITH hiring (staircase)
    results, be_month, hire_log = simulate(sc, enable_hiring=True)
    # Run WITHOUT hiring (static baseline)
    static_results, static_be, _ = simulate(sc, enable_hiring=False)

    print("=" * 95)
    print(f"  {sc_name}: {sc['desc']}")
    print("=" * 95)
    print()

    # --- Breakeven ---
    if be_month:
        be_r = results[be_month - 1]
        burned = SEED - be_r['bank']
        preserved = be_r['bank']
        growth_cap = preserved - LEGAL_RESERVE
        print(f"  BREAKEVEN: Month {be_month} (Year {be_month/12:.1f})")
        print(f"    Customers: {be_r['cust']:.0f} | MRR: ${be_r['mrr']:,.0f} | ARR: ${be_r['arr']:,.0f}")
        print(f"    Cash burned: ${burned:,.0f} | Seed preserved: ${preserved:,.0f}")
        print(f"    Growth capital (safety net): ${growth_cap:,.0f}")
        print()

    # --- Per-Hire Impact Analysis ---
    if hire_log:
        print("  PER-HIRE MRR CONTRIBUTION:")
        print(f"  {'#':>3} {'Mo':>4} {'Role':<22} {'MRR at Hire':>12} {'MRR +6mo':>12} "
              f"{'Delta MRR':>10} {'Static MRR':>12} {'Hire Lift':>10} {'ROI':>6}")
        print("  " + "-" * 100)

        for i, hl in enumerate(hire_log):
            mo = hl['month']
            mrr_hire = hl['mrr_at_hire']

            # MRR 6 months after this hire
            idx_6 = min(mo + 5, len(results) - 1)  # 6 months later
            mrr_6mo = results[idx_6]['mrr']

            # What would MRR be at that same month WITHOUT any hiring?
            static_mrr_6mo = static_results[idx_6]['mrr']

            # Staircase vs static delta at +6mo
            hire_lift = mrr_6mo - static_mrr_6mo
            delta = mrr_6mo - mrr_hire

            # ROI: months for this hire to pay for itself
            # Approximate: hire's marginal MRR contribution vs $11K cost
            # Use the MRR growth rate after hire vs before
            if i == 0:
                mrr_before_hire = mrr_hire
            else:
                mrr_before_hire = hire_log[i-1]['mrr_at_hire']
            # Monthly MRR growth in the 6 months after hire
            monthly_mrr_growth = delta / 6.0 if delta > 0 else 0
            roi_months = f"{HIRE_COST / monthly_mrr_growth:.1f}" if monthly_mrr_growth > 0 else "n/a"

            print(f"  {i+1:>3} M{mo:<3} {hl['role']:<22} ${mrr_hire:>10,.0f} ${mrr_6mo:>10,.0f} "
                  f"+${delta:>8,.0f} ${static_mrr_6mo:>10,.0f} +${hire_lift:>8,.0f} {roi_months:>5}mo")

        # Total team lift
        last_mo = min(59, len(results) - 1)
        staircase_mrr = results[last_mo]['mrr']
        static_mrr = static_results[last_mo]['mrr']
        total_lift = staircase_mrr - static_mrr
        total_payroll = len(hire_log) * HIRE_COST
        print("  " + "-" * 100)
        print(f"  TOTAL at M{last_mo+1}: Staircase ${staircase_mrr:,.0f} vs Static ${static_mrr:,.0f}"
              f" = +${total_lift:,.0f} MRR lift (${total_lift*12:,.0f} ARR)")
        print(f"  Total hire payroll: ${total_payroll:,}/mo | MRR lift covers {total_lift/total_payroll:.1f}x payroll")
        print()

    # --- Acceleration visualization ---
    print("  GROWTH ACCELERATION (Staircase vs Static team):")
    print(f"  {'Mo':>4} {'Staircase':>12} {'Static':>12} {'Lift':>12} "
          f"{'Lift %':>8} {'Cust':>6} {'ARPA':>8} {'HC':>3} {'Event':<22}")
    print("  " + "-" * 100)

    for r, sr in zip(results, static_results):
        m = r['m']
        lift = r['mrr'] - sr['mrr']
        lift_pct = (lift / sr['mrr'] * 100) if sr['mrr'] > 0 else 0

        # Show at key months
        show = (m <= 12 or m % 6 == 0 or m == be_month
                or r['new_hire'] is not None)
        if not show:
            continue

        event = ""
        if m == be_month:
            event = "<-- BREAKEVEN"
        elif r['new_hire']:
            event = "<-- " + r['new_hire']['role']

        print(f"  M{m:<3} ${r['mrr']:>10,.0f} ${sr['mrr']:>10,.0f} +${lift:>10,.0f} "
              f"{lift_pct:>6.0f}%  {r['cust']:>5.0f} ${r['arpa']:>7,.0f} "
              f"{2+r['headcount']:>3}  {event}")
    print()

    # --- Mix shift over time ---
    print("  TIER MIX EVOLUTION (% of active customers):")
    print(f"  {'Mo':>4} {'Starter':>10} {'Team':>10} {'Org':>10} {'Ent':>10} {'ARPA':>10} {'Event':<22}")
    print("  " + "-" * 80)
    for r in results:
        m = r['m']
        tc = r['cust']
        if tc < 1:
            continue
        show = (m == 1 or m == be_month or r['new_hire'] is not None
                or m == 12 or m == 24 or m == 36 or m == 48 or m == 60)
        if not show:
            continue
        c = r['customers']
        s_pct = c['Starter'] / tc * 100
        t_pct = c['Team'] / tc * 100
        o_pct = c['Org'] / tc * 100
        e_pct = c['Enterprise'] / tc * 100
        event = ""
        if m == be_month:
            event = "<-- BREAKEVEN"
        elif r['new_hire']:
            event = "<-- " + r['new_hire']['role']
        print(f"  M{m:<3} {s_pct:>8.1f}%  {t_pct:>8.1f}%  {o_pct:>8.1f}%  {e_pct:>8.1f}%  ${r['arpa']:>8,.0f}  {event}")
    print()

    # --- Key milestones ---
    david_100m_arr = 8_330_000
    milestones = [
        ("Breakeven",                      lambda r: r['gross'] >= BASE_BURN),
        ("$1M ARR",                         lambda r: r['arr'] >= 1_000_000),
        ("$5M ARR",                         lambda r: r['arr'] >= 5_000_000),
        ("$8.33M ARR (David $100M)",        lambda r: r['arr'] >= david_100m_arr),
        ("$16.7M ARR (David $200M)",        lambda r: r['arr'] >= 16_700_000),
        ("$25M ARR ($750M exit)",           lambda r: r['arr'] >= 25_000_000),
    ]

    print(f"  MILESTONES (Staircase vs Static):")
    print(f"  {'Milestone':<30} {'Staircase':>12} {'Static':>12} {'Speedup':>10}")
    print("  " + "-" * 70)
    for label, cond in milestones:
        # Staircase
        stair_mo = None
        for r in results:
            if cond(r):
                stair_mo = r['m']
                break
        # Static
        static_mo = None
        for sr in static_results:
            if cond(sr):
                static_mo = sr['m']
                break

        s_str = f"M{stair_mo} (Y{stair_mo/12:.1f})" if stair_mo else ">M60"
        st_str = f"M{static_mo} (Y{static_mo/12:.1f})" if static_mo else ">M60"
        if stair_mo and static_mo:
            speedup = f"{static_mo - stair_mo} months faster"
        elif stair_mo and not static_mo:
            speedup = "ONLY w/ hires"
        else:
            speedup = "--"
        print(f"  {label:<30} {s_str:>12} {st_str:>12} {speedup:>15}")
    print()

    # --- David $100M snapshot ---
    for r in results:
        if r['arr'] >= david_100m_arr:
            exit_val = r['arr'] / 1e6 * 30
            print(f"  DAVID $100M SNAPSHOT (Month {r['m']}):")
            print(f"    ARR: ${r['arr']/1e6:.1f}M | MRR: ${r['mrr']/1e3:.0f}K | ARPA: ${r['arpa']:,.0f}")
            print(f"    Exit at 30x: ${exit_val:.0f}M")
            print(f"      David (40%):   ${exit_val * 0.40:.0f}M")
            print(f"      Igor (40%):    ${exit_val * 0.40:.0f}M")
            print(f"      Angel (10%):   ${exit_val * 0.10:.0f}M ({exit_val * 0.10:.0f}x return)")
            print(f"    Headcount: {2 + r['headcount']} | Bank: ${r['bank']/1e6:.1f}M")
            c = r['customers']
            print(f"    Customers: {r['cust']:.0f} ({c['Starter']:.0f}S / {c['Team']:.0f}T / {c['Org']:.0f}O / {c['Enterprise']:.0f}E)")
            print()
            break


# ====================================================================
# CROSS-SCENARIO SUMMARY
# ====================================================================
print("=" * 95)
print("CROSS-SCENARIO SUMMARY")
print("=" * 95)
print()

# David $100M timeline comparison
print("DAVID $100M ($8.33M ARR at 40% x 30x):")
print("-" * 80)
print(f"  {'Scenario':<8} {'Staircase':>12} {'Static':>12} {'Speedup':>15} {'Customers':>10} {'Bank':>10}")
print("-" * 80)
for sc_name in ['BEAR', 'BASE', 'BULL']:
    sc = scenarios[sc_name]
    results, _, _ = simulate(sc, enable_hiring=True)
    static, _, _ = simulate(sc, enable_hiring=False)

    stair_mo = None
    stair_r = None
    for r in results:
        if r['arr'] >= 8_330_000:
            stair_mo = r['m']
            stair_r = r
            break

    static_mo = None
    for sr in static:
        if sr['arr'] >= 8_330_000:
            static_mo = sr['m']
            break

    s_str = f"M{stair_mo} (Y{stair_mo/12:.1f})" if stair_mo else ">M60"
    st_str = f"M{static_mo} (Y{static_mo/12:.1f})" if static_mo else ">M60"
    if stair_mo and static_mo:
        speedup = f"{static_mo - stair_mo} months"
    elif stair_mo and not static_mo:
        speedup = "IMPOSSIBLE w/o"
    else:
        speedup = "--"
    cust = f"{stair_r['cust']:.0f}" if stair_r else "--"
    bank = f"${stair_r['bank']/1e6:.1f}M" if stair_r else "--"
    print(f"  {sc_name:<8} {s_str:>12} {st_str:>12} {speedup:>15} {cust:>10} {bank:>10}")
print()

# Per-hire summary across BASE
print("PER-HIRE ROI (BASE scenario):")
print("-" * 95)
sc = scenarios['BASE']
results, be_month, hire_log = simulate(sc, enable_hiring=True)
static, _, _ = simulate(sc, enable_hiring=False)

if hire_log:
    print(f"  {'#':>3} {'Mo':>4} {'Role':<22} {'Cost':>8} "
          f"{'MRR at Hire':>12} {'MRR +3mo':>10} {'MRR +6mo':>10} "
          f"{'Cum Lift':>10}")
    print("  " + "-" * 92)
    for i, hl in enumerate(hire_log):
        mo = hl['month']
        idx_3 = min(mo + 2, len(results) - 1)
        idx_6 = min(mo + 5, len(results) - 1)
        mrr_3 = results[idx_3]['mrr']
        mrr_6 = results[idx_6]['mrr']
        static_6 = static[idx_6]['mrr']
        cum_lift = mrr_6 - static_6

        print(f"  {i+1:>3} M{mo:<3} {hl['role']:<22} ${HIRE_COST:>6,}/mo "
              f"${hl['mrr_at_hire']:>10,.0f} ${mrr_3:>8,.0f} ${mrr_6:>8,.0f} "
              f"+${cum_lift:>8,.0f}")
    print()

# Key insight
print("KEY INSIGHT:")
print("-" * 80)
print("Each hire doesn't just add bodies -- they COMPOUND growth:")
print("  1. Sales hires add customers AND shift mix toward higher tiers (bigger ARPA)")
print("  2. Customer Success cuts churn AND drives upgrades (expansion MRR)")
print("  3. Product/Compliance enables enterprise deals (mix shift to Org/Ent)")
print("  4. Marketing adds volume AND brand credibility (better-quality inbound)")
print()
print("The staircase model means each hire funds the NEXT hire's threshold.")
print("By Hire #3 (SDR), the team is acquiring 10+ customers/mo with higher ARPA.")
print("This is why the staircase is faster than linear: it's a compound growth loop.")
print()
print("Seed money = safety net. Revenue funds growth. 98% margins make this possible.")
