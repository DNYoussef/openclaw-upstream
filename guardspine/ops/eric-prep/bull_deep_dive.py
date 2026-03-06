"""Bull case deep dive: per-hire marginal MRR contribution and max speed."""

import staircase_growth as sg
from copy import deepcopy

sc = sg.scenarios['BULL']
orig_effects = sg.HIRE_EFFECTS[:]

# Run full staircase
results, be_month, hire_log = sg.simulate(sc, max_months=60, enable_hiring=True)
# Run static (no hires)
static, _, _ = sg.simulate(sc, max_months=60, enable_hiring=False)

# Isolate each hire's marginal contribution:
# Run N simulations, each allowing one more hire
cumulative_runs = {}
sg.HIRE_EFFECTS = []
r0, _, _ = sg.simulate(sc, max_months=60, enable_hiring=True)
cumulative_runs[0] = r0

for n in range(1, len(orig_effects) + 1):
    sg.HIRE_EFFECTS = orig_effects[:n]
    rn, _, hl = sg.simulate(sc, max_months=60, enable_hiring=True)
    cumulative_runs[n] = rn

sg.HIRE_EFFECTS = orig_effects  # restore

# ====================================================================
print("=" * 105)
print("BULL CASE: WHAT EACH HIRE CONTRIBUTES (Marginal MRR Isolation)")
print("Each row = difference between having N hires vs N-1 hires")
print("=" * 105)
print()

print("  MARGINAL MRR AT +3, +6, +12 MONTHS AFTER HIRE:")
print(f"  {'#':>2} {'Role':<24} {'Hired':>5} {'Marginal +3mo':>14} {'Marginal +6mo':>14} {'Marginal +12mo':>15} {'Payback':>8}")
print("  " + "-" * 90)

for n in range(1, len(orig_effects) + 1):
    h = orig_effects[n-1]
    rn = cumulative_runs[n]
    rn_prev = cumulative_runs[n-1]

    # Find when this hire happens
    hire_month = None
    for r in rn:
        if r['new_hire'] and r['new_hire']['role'] == h['role']:
            hire_month = r['m']
            break

    if hire_month is None:
        print(f"  {n:>2} {h['role']:<24}  --   (threshold not reached)")
        continue

    idx_3 = min(hire_month + 2, 59)
    idx_6 = min(hire_month + 5, 59)
    idx_12 = min(hire_month + 11, 59)

    marginal_3 = rn[idx_3]['mrr'] - rn_prev[idx_3]['mrr']
    marginal_6 = rn[idx_6]['mrr'] - rn_prev[idx_6]['mrr']
    marginal_12 = rn[idx_12]['mrr'] - rn_prev[idx_12]['mrr']

    # Payback: months until cumulative marginal MRR > cumulative cost
    cum_marginal = 0
    payback = None
    for offset in range(60 - hire_month):
        idx = hire_month + offset
        if idx >= 60:
            break
        cum_marginal += (rn[idx]['mrr'] - rn_prev[idx]['mrr'])
        cum_cost = sg.HIRE_COST * (offset + 1)
        if cum_marginal >= cum_cost and payback is None:
            payback = offset + 1
            break

    pb_str = f"{payback}mo" if payback else ">60mo"
    print(f"  {n:>2} {h['role']:<24} M{hire_month:<3}"
          f"  +${marginal_3:>10,.0f}  +${marginal_6:>10,.0f}  +${marginal_12:>11,.0f}  {pb_str:>7}")

# Cumulative effect
print()
print("  CUMULATIVE EFFECT (total MRR with N hires vs 0 hires):")
print(f"  {'Hires':>5} {'M12 MRR':>12} {'M24 MRR':>12} {'M36 MRR':>12} {'M48 MRR':>12} {'M60 MRR':>12} {'M60 ARR':>14}")
print("  " + "-" * 85)
for n in range(len(orig_effects) + 1):
    rn = cumulative_runs[n]
    label = "0 (static)" if n == 0 else str(n)
    m12 = rn[11]['mrr']
    m24 = rn[23]['mrr']
    m36 = rn[35]['mrr']
    m48 = rn[47]['mrr']
    m60 = rn[59]['mrr']
    print(f"  {label:>10} ${m12:>10,.0f} ${m24:>10,.0f} ${m36:>10,.0f} ${m48:>10,.0f} ${m60:>10,.0f}  ${m60*12:>12,.0f}")

# ====================================================================
print()
print("=" * 105)
print("BULL CASE: FULL ACCELERATION TIMELINE")
print("=" * 105)
print()

milestones = [
    ("Breakeven",                  lambda r: r['gross'] >= sg.BASE_BURN),
    ("$500K ARR",                  lambda r: r['arr'] >= 500_000),
    ("$1M ARR",                    lambda r: r['arr'] >= 1_000_000),
    ("$2M ARR",                    lambda r: r['arr'] >= 2_000_000),
    ("$5M ARR",                    lambda r: r['arr'] >= 5_000_000),
    ("$8.33M ARR (David $100M)",   lambda r: r['arr'] >= 8_330_000),
    ("$10M ARR",                   lambda r: r['arr'] >= 10_000_000),
    ("$16.7M ARR (David $200M)",   lambda r: r['arr'] >= 16_700_000),
    ("$25M ARR ($750M exit)",      lambda r: r['arr'] >= 25_000_000),
    ("$50M ARR ($1.5B exit)",      lambda r: r['arr'] >= 50_000_000),
    ("$100M ARR ($3B exit)",       lambda r: r['arr'] >= 100_000_000),
]

print(f"  {'Milestone':<32} {'Month':>6} {'Year':>5} {'Cust':>6} {'ARPA':>9} {'MRR':>12} {'Bank':>9} {'HC':>3}")
print("  " + "-" * 90)
for label, cond in milestones:
    for r in results:
        if cond(r):
            print(f"  {label:<32} M{r['m']:>4}  Y{r['m']/12:>3.1f} {r['cust']:>5.0f}"
                  f" ${r['arpa']:>7,.0f} ${r['mrr']:>10,.0f} ${r['bank']/1e6:>7.1f}M {2+r['headcount']:>3}")
            break
    else:
        last = results[-1]
        print(f"  {label:<32}  >M60  (at ${last['arr']/1e6:.1f}M ARR)")

# ====================================================================
print()
print("=" * 105)
print("BULL CASE: EXIT PAYOUT TABLE (30x strategic acquirer)")
print("=" * 105)
print()
print(f"  {'Mo':>4} {'ARR':>10} {'Exit Val':>11} {'David 40%':>11} {'Igor 40%':>11}"
      f" {'Angel 10%':>11} {'Kristen 2%':>10} {'Pool 8%':>10}")
print("  " + "-" * 85)
for r in results:
    m = r['m']
    if m in [3, 6, 9, 11, 12, 14, 17, 18, 24, 30, 36, 48, 60]:
        arr = r['arr']
        ev = arr * 30 / 1e6
        print(f"  M{m:>2} ${arr/1e6:>8.1f}M ${ev:>9.0f}M ${ev*0.40:>9.0f}M ${ev*0.40:>9.0f}M"
              f" ${ev*0.10:>9.0f}M ${ev*0.02:>8.1f}M ${ev*0.08:>8.1f}M")

# ====================================================================
print()
print("=" * 105)
print("HOW FAST CAN WE GO? (BULL + Staircase + 30x Strategic)")
print("=" * 105)
print()

targets = [
    ("David $100M", 8_330_000),
    ("David $200M", 16_700_000),
    ("David $250M", 20_833_333),
    ("David $500M", 41_666_667),
]

for label, target_arr in targets:
    for r in results:
        if r['arr'] >= target_arr:
            exit_v = r['arr'] / 1e6 * 30
            print(f"  {label:>14}:  Month {r['m']:>2} (Year {r['m']/12:.1f})"
                  f"  |  {r['cust']:.0f} customers  |  ARPA ${r['arpa']:,.0f}"
                  f"  |  Exit ${exit_v:.0f}M  |  Bank ${r['bank']/1e6:.1f}M")
            break
    else:
        last = results[-1]
        print(f"  {label:>14}:  >M60 (at ${last['arr']/1e6:.1f}M ARR)")

# ====================================================================
print()
print("MONTHLY NET NEW MRR (the acceleration curve):")
print("-" * 70)
prev_mrr = 0
for r in results:
    m = r['m']
    net_new = r['mrr'] - prev_mrr
    prev_mrr = r['mrr']
    if m <= 20 or m % 6 == 0:
        bar_len = min(int(net_new / 8000), 50)
        bar = "#" * bar_len
        event = ""
        if r['new_hire']:
            event = " <-- " + r['new_hire']['role']
        elif m == be_month:
            event = " <-- BREAKEVEN"
        print(f"  M{m:>2} +${net_new:>10,.0f}  {bar}{event}")

# ====================================================================
print()
print("=" * 105)
print("COMPOUND GROWTH MECHANICS (why each hire makes the next one faster)")
print("=" * 105)
print()

# Time between hires
if hire_log:
    prev_mo = be_month
    print(f"  {'#':>2} {'Role':<24} {'Hired':>5} {'Gap':>5} {'MRR':>10} {'ARPA':>8} {'Cust/mo':>8} {'Churn':>6} {'Why faster':<30}")
    print("  " + "-" * 105)
    for i, hl in enumerate(hire_log):
        gap = hl['month'] - prev_mo
        prev_mo = hl['month']
        r = results[hl['month'] - 1]
        why = orig_effects[i]['note']
        print(f"  {i+1:>2} {hl['role']:<24} M{hl['month']:<3}  {gap:>3}mo"
              f" ${hl['mrr_at_hire']:>8,.0f} ${r['arpa']:>6,.0f} {r['new_per_mo']:>6.1f}"
              f" {r['churn']*100:>4.1f}%  {why}")

    print()
    print("  Gap between hires SHRINKS because each hire accelerates MRR toward the next threshold.")
    print("  Hire 1 to Hire 2: higher MRR from more+better customers -> threshold hit sooner.")
    print("  Hire 2 (CSM): cuts churn 30% -> more retained MRR -> threshold hit even sooner.")
    print("  By Hire 5-6: the machine is running. Each threshold is cleared in ~1 month.")
