"""
Generate professionally designed PDFs from Eric Skiff prep docs.
Uses Playwright for HTML-to-PDF conversion.
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).parent / "pdf-package"
OUT_DIR.mkdir(exist_ok=True)

# --- Brand palette (print-optimized) ---
TEAL = "#0d9488"
DARK = "#111827"
MEDIUM = "#374151"
LIGHT_TEXT = "#6b7280"
BORDER = "#e5e7eb"
ACCENT_BG = "#f0fdfa"
TABLE_HEADER = "#0f766e"
WHITE = "#ffffff"

CSS = f"""
@page {{
    size: A4;
    margin: 24mm 20mm 20mm 20mm;
    @bottom-center {{
        content: counter(page);
        font-size: 9px;
        color: {LIGHT_TEXT};
    }}
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: {DARK};
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}
.cover-band {{
    background: linear-gradient(135deg, {TEAL}, #0f766e);
    color: white;
    padding: 28px 32px;
    margin: -24mm -20mm 24px -20mm;
    width: calc(100% + 40mm);
}}
.cover-band h1 {{
    font-size: 22pt;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}}
.cover-band .subtitle {{
    font-size: 11pt;
    opacity: 0.9;
    font-weight: 400;
}}
.cover-band .meta {{
    font-size: 9pt;
    opacity: 0.7;
    margin-top: 8px;
}}
h2 {{
    font-size: 14pt;
    font-weight: 700;
    color: {TEAL};
    margin: 24px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid {TEAL};
}}
h3 {{
    font-size: 11.5pt;
    font-weight: 700;
    color: {DARK};
    margin: 16px 0 6px 0;
}}
h4 {{
    font-size: 10.5pt;
    font-weight: 600;
    color: {MEDIUM};
    margin: 12px 0 4px 0;
}}
p {{ margin-bottom: 8px; }}
strong {{ font-weight: 700; color: {DARK}; }}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 16px 0;
    font-size: 9.5pt;
}}
thead th {{
    background: {TABLE_HEADER};
    color: white;
    font-weight: 600;
    padding: 8px 10px;
    text-align: left;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
tbody td {{
    padding: 7px 10px;
    border-bottom: 1px solid {BORDER};
    vertical-align: top;
}}
tbody tr:nth-child(even) {{ background: #f9fafb; }}
tbody tr:hover {{ background: {ACCENT_BG}; }}
.callout {{
    background: {ACCENT_BG};
    border-left: 3px solid {TEAL};
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 10pt;
}}
.callout strong {{ color: {TEAL}; }}
.metric-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin: 14px 0;
}}
.metric-card {{
    background: #f9fafb;
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 12px 14px;
    text-align: center;
}}
.metric-card .value {{
    font-size: 18pt;
    font-weight: 800;
    color: {TEAL};
    line-height: 1.2;
}}
.metric-card .label {{
    font-size: 8pt;
    color: {LIGHT_TEXT};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-top: 2px;
}}
ul, ol {{ margin: 6px 0 12px 20px; }}
li {{ margin-bottom: 4px; }}
code {{
    background: #f3f4f6;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9.5pt;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
}}
pre {{
    background: #1e293b;
    color: #e2e8f0;
    padding: 14px 16px;
    border-radius: 6px;
    font-size: 9pt;
    line-height: 1.5;
    margin: 10px 0 14px 0;
    overflow-x: auto;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
}}
.footer {{
    margin-top: 30px;
    padding-top: 12px;
    border-top: 1px solid {BORDER};
    font-size: 8.5pt;
    color: {LIGHT_TEXT};
    text-align: center;
}}
.page-break {{ page-break-before: always; }}
blockquote {{
    border-left: 3px solid {BORDER};
    padding-left: 14px;
    color: {MEDIUM};
    margin: 10px 0;
    font-style: italic;
}}
.objection {{
    background: #fef2f2;
    border-left: 3px solid #ef4444;
    padding: 10px 14px;
    margin: 10px 0 4px 0;
    font-weight: 600;
    font-size: 10pt;
    color: #991b1b;
}}
.answer {{
    padding: 4px 0 12px 0;
    font-size: 10pt;
}}
.signal-badge {{
    display: inline-block;
    background: {TEAL};
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 8pt;
    font-weight: 600;
    text-transform: uppercase;
}}
hr {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 16px 0;
}}
"""


def wrap(title, subtitle, body, date="February 2026"):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="cover-band">
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
    <div class="meta">GuardSpine | Confidential | {date}</div>
</div>
{body}
<div class="footer">
    GuardSpine -- Tamper-Proof Code Governance | guardspine.ai | Confidential
</div>
</body></html>"""


# ============================================================
# DOC 1: Executive Summary
# ============================================================
def build_exec_summary():
    body = """
<div class="metric-grid">
    <div class="metric-card">
        <div class="value">98%+</div>
        <div class="label">Gross Margins (BYOK)</div>
    </div>
    <div class="metric-card">
        <div class="value">36 mo</div>
        <div class="label">Runway at $1M Raise</div>
    </div>
    <div class="metric-card">
        <div class="value">$0</div>
        <div class="label">LLM Inference Cost</div>
    </div>
</div>

<h2>What Is It</h2>
<p>GuardSpine is an open-source governance layer that creates tamper-proof audit trails for every code change -- whether written by humans or AI. It is not a code review tool. It is insurance against the question: <strong>"Who is liable when AI-generated code causes a breach?"</strong></p>

<h2>Who Buys It</h2>
<p><strong>Primary buyer:</strong> CISO or Chief Compliance Officer at companies with 500+ engineers in regulated industries (finance, healthcare, insurance, legal).</p>
<p><strong>End users:</strong> Developers install it as a GitHub Action in 5 minutes. They keep working the way they already work. The CISO gets the dashboard and evidence.</p>

<h2>Pricing</h2>
<table>
<thead><tr><th>Tier</th><th>Price</th><th>For</th></tr></thead>
<tbody>
<tr><td><strong>Free</strong></td><td>$0/mo</td><td>Open-source GitHub Action, full review engine, unlimited repos</td></tr>
<tr><td><strong>Starter</strong></td><td>$499/mo</td><td>Cloud dashboard, Slack alerts, evidence management, 10 repos</td></tr>
<tr><td><strong>Team</strong></td><td>$2,000/mo</td><td>Custom rubrics, Jira + Teams, compliance reports, unlimited repos</td></tr>
<tr><td><strong>Org</strong></td><td>$12,000/mo</td><td>Multi-team RBAC, ServiceNow, SSO/SAML, dedicated CSM</td></tr>
<tr><td><strong>Enterprise</strong></td><td>Custom</td><td>On-prem/airgap, SLA, compliance consulting</td></tr>
</tbody>
</table>
<div class="callout"><strong>BYOK model:</strong> Customers bring their own AI model API keys. GuardSpine never touches inference costs. Gross margins: 97-99%.</div>

<h2>Why Now</h2>
<p><strong>1. AI is writing code faster than anyone can review it.</strong> 65% of PRs ship with minimal or zero review (Graphite, 2025). AI-generated code has 1.7x more defects (CodeRabbit) and 2.74x more security issues (Veracode).</p>
<p><strong>2. Regulations are closing in.</strong> EU AI Act enforcement begins August 2026 (fines up to 7% of global turnover). DORA enforceable since January 2025 (2% of turnover). SOC 2 auditors are asking for code-level governance evidence.</p>
<p><strong>3. Nobody else does this.</strong> Vanta and Drata prove infrastructure is configured correctly. Snyk and Checkmarx find vulnerabilities. Neither proves that AI-generated code was governed before reaching production. That is the gap.</p>

<h2>ROI Snapshot</h2>
<div class="metric-grid">
    <div class="metric-card">
        <div class="value">16,337%</div>
        <div class="label">Engineering ROI (Team tier)</div>
    </div>
    <div class="metric-card">
        <div class="value">1,999%</div>
        <div class="label">Compliance ROI (Org tier)</div>
    </div>
    <div class="metric-card">
        <div class="value">~2 days</div>
        <div class="label">Payback Period</div>
    </div>
</div>

<table>
<thead><tr><th>Audience</th><th>Key Metric</th><th>Annual Value</th></tr></thead>
<tbody>
<tr><td>Engineering (50 devs, Team tier $19.2K/yr)</td><td>Prevented defects + recovered review time</td><td>$3.1M savings</td></tr>
<tr><td>Compliance (200 devs, Org tier $120K/yr)</td><td>Audit automation + regulatory risk reduction</td><td>$2.5M savings</td></tr>
</tbody>
</table>

<h2>Proof of Interest</h2>
<table>
<thead><tr><th>Signal</th><th>Who</th><th>Significance</th></tr></thead>
<tbody>
<tr><td><span class="signal-badge">Landing Page Signup</span></td><td><strong>Andy Ellis</strong> -- ex-CSO Akamai (20yr), Partner at YL Ventures (cybersecurity VC), CISO Series podcast co-host, CSO Hall of Fame</td><td>Cybersecurity VC partner and 20-year CISO signed up within 48 hours of launch -- unprompted</td></tr>
<tr><td><span class="signal-badge">Cold Reply</span></td><td><strong>Brent Foster</strong> -- VP Eng, TD Bank</td><td>Top-5 NA bank VP responded to unknown founder's cold email asking technical differentiation questions</td></tr>
<tr><td><span class="signal-badge">DD Questions</span></td><td><strong>Phil Venables</strong> -- Ballistic Ventures, ex-CISO Google Cloud</td><td>Cybersecurity-focused VC asked team/pipeline/ICP questions independently</td></tr>
<tr><td><span class="signal-badge">Response Rate</span></td><td>4.8% cold response rate</td><td>Industry average: 1-3% for unknown founders selling pre-revenue product</td></tr>
</tbody>
</table>
<p><strong>What is missing:</strong> Zero paying customers. Zero pilots. This is the gap between "interesting project" and "investable business." Landing pages live since Feb 22, 2026.</p>

<h2>The Team</h2>
<table>
<thead><tr><th>Name</th><th>Role</th><th>Key Credentials</th></tr></thead>
<tbody>
<tr><td><strong>David Youssef</strong></td><td>CEO (full-time)</td><td>Vision, 1:1 sales, domain expertise</td></tr>
<tr><td><strong>Igor Malovitsa</strong></td><td>CTO (full-time)</td><td>MSc Experimental Nuclear Physics (4.0 GPA). 8.5yr Senior Eng at DataArt. CTO obox.systems (Rust). Published O(1) hash collision attacks + shipped fix upstream. Rust/C++/WASM/Python.</td></tr>
<tr><td><strong>Kristen Hengst Smith</strong></td><td>GTM Advisor</td><td>Product-to-market experience, angel network</td></tr>
<tr><td><strong>Chris Hood</strong></td><td>Advisor</td><td>Noematic AI framework, Google connections</td></tr>
</tbody>
</table>

<h2>Validation Strategy: Three Angles</h2>
<table>
<thead><tr><th>Angle</th><th>Partner</th><th>What It Validates</th></tr></thead>
<tbody>
<tr><td><strong>Enterprise</strong></td><td>Ishwar Chandrasekharan (Z-Inspection, IBM)</td><td>Internal friction and risk thresholds for governance tool adoption at Fortune 100</td></tr>
<tr><td><strong>Government / Standards</strong></td><td>Jacob Friedman (G7/NIST, Permion)</td><td>SBOM complementarity, airgap/offline requirements, gov procurement pathways</td></tr>
<tr><td><strong>Direct Buyer</strong></td><td>CISO/CCO outreach in regulated industries</td><td>Buy-trigger validation, pricing sensitivity, ICP confirmation</td></tr>
</tbody>
</table>
"""
    return wrap("GuardSpine: Executive Summary", "For CISOs, CTOs, CFOs, and Advisors", body)


# ============================================================
# DOC 2: Competitive Landscape
# ============================================================
def build_competitive():
    body = """
<h2>Market Map</h2>
<table>
<thead><tr><th>Company</th><th>Category</th><th>ARR</th><th>Customers</th><th>Last Funding</th><th>Founded</th></tr></thead>
<tbody>
<tr><td><strong>Vanta</strong></td><td>Compliance Automation</td><td>~$220M [est]</td><td>15,000+</td><td>$150M Series D (2025)</td><td>2018</td></tr>
<tr><td><strong>Drata</strong></td><td>Compliance Automation</td><td>$100M+</td><td>8,000+</td><td>$200M Series C (2022)</td><td>2020</td></tr>
<tr><td><strong>CrowdStrike</strong></td><td>Endpoint Security / XDR</td><td>$4.92B</td><td>29,000+</td><td>Public (CRWD)</td><td>2011</td></tr>
<tr><td><strong>Snyk</strong></td><td>Developer Security</td><td>~$300M [est]</td><td>3,000+</td><td>$530M Series G (2022)</td><td>2015</td></tr>
<tr><td><strong>Greptile</strong></td><td>AI Code Review</td><td>&lt;$5M [est]</td><td>Early</td><td>$4.1M Seed (2024)</td><td>2023</td></tr>
<tr><td><strong>CodeRabbit</strong></td><td>AI Code Review</td><td>&lt;$10M [est]</td><td>10,000+</td><td>$16M Series A (2024)</td><td>2023</td></tr>
<tr><td><strong>LinearB</strong></td><td>Dev Productivity</td><td>~$20M [est]</td><td>3,000+</td><td>$50M Series B (2022)</td><td>2019</td></tr>
</tbody>
</table>
<p style="font-size: 8.5pt; color: #6b7280;">Sources: SEC filings (CRWD), Sacra estimates (Vanta/Drata), Crunchbase (all others). Figures marked [est] are third-party estimates.</p>

<h2>Category Map</h2>
<div class="callout"><strong>There are THREE distinct categories here. GuardSpine is in governance, not code review.</strong></div>
<table>
<thead><tr><th>Governance / Compliance</th><th>Code Review / Quality</th><th>Dev Productivity</th></tr></thead>
<tbody>
<tr><td>Vanta -- audit evidence</td><td>Greptile -- code search</td><td>LinearB -- eng metrics</td></tr>
<tr><td>Drata -- framework mapping</td><td>CodeRabbit -- PR suggestions</td><td>Jellyfish -- planning</td></tr>
<tr><td><strong>GUARDSPINE -- AI artifact governance</strong></td><td>Codacy -- static analysis</td><td></td></tr>
<tr><td>Holistic AI -- AI risk management</td><td></td><td></td></tr>
</tbody>
</table>
<p>Vanta/Drata automate SOC 2 and ISO 27001 evidence collection for auditors. Greptile/CodeRabbit suggest code improvements on pull requests. GuardSpine governs what AI-generated artifacts are allowed into production, with cryptographic proof that the governance actually happened. These are not the same problem.</p>

<h2>Why GuardSpine Wins</h2>
<p><strong>Open-core + BYOK = ~98% gross margins.</strong> Vanta and Drata run inference on their own infrastructure. GuardSpine customers bring their own model keys. We route, orchestrate, and sign -- we do not pay per token. Structurally different cost model.</p>
<p><strong>Tamper-proof judgment receipts.</strong> Every governance decision produces a signed JSON bundle: model identity, prompt hash, response hash, consensus vote, timestamp. No other compliance platform produces cryptographic proof of AI governance decisions.</p>
<p><strong>AI-native from day one.</strong> Vanta and Drata were built to prove humans configured AWS correctly. GuardSpine was built to prove AI models made safe decisions. EU AI Act (Aug 2026), NIST AI RMF, and ISO 42001 require exactly this -- incumbents are bolting it on, not building it in.</p>
<p><strong>Works where incumbents do not.</strong> Offline/airgap (Ollama), GitLab, GitHub Enterprise, self-hosted. Vanta requires cloud integrations. GuardSpine runs as a single GitHub Action or GitLab CI job with zero infrastructure.</p>

<h2>The Gap</h2>
<div class="callout">
<strong>Nobody in the market produces tamper-proof governance for AI-generated artifacts with a cryptographic proof chain.</strong><br><br>
Vanta and Drata prove your firewall is on. CrowdStrike proves it stopped a threat. Neither proves that the AI model that wrote your code, reviewed your PR, or generated your infrastructure config was actually governed before the artifact reached production.<br><br>
That is the gap. The EU AI Act makes it a legal requirement by August 2026. Over 1,100 AI-related bills were introduced across U.S. states in 2025. The market for this does not exist yet -- GuardSpine is building it.
</div>
<p style="font-size: 9pt; color: #6b7280;"><em>GRC market: $49-63B (2024), 13-16% CAGR. AI governance sub-segment growing faster.</em></p>
"""
    return wrap("Competitive Landscape", "Where GuardSpine Sits and Why It Matters", body)


# ============================================================
# DOC 3: Financial Reference Card
# ============================================================
def build_financial():
    body = """
<div class="metric-grid">
    <div class="metric-card">
        <div class="value">55</div>
        <div class="label">Starter Customers to Breakeven</div>
    </div>
    <div class="metric-card">
        <div class="value">36 mo</div>
        <div class="label">Runway ($1M Raise)</div>
    </div>
    <div class="metric-card">
        <div class="value">98%+</div>
        <div class="label">Gross Margin (All Tiers)</div>
    </div>
</div>

<h2>20 Key Numbers</h2>
<table>
<thead><tr><th>#</th><th>Metric</th><th>Value</th><th>Why It Matters</th></tr></thead>
<tbody>
<tr><td>1</td><td>Breakeven (Starter)</td><td><strong>55 customers</strong></td><td>$27.4K MRR from Starter alone</td></tr>
<tr><td>1b</td><td>Breakeven (blended)</td><td><strong>30 Starter + 3 Team</strong></td><td>Multiple paths to breakeven</td></tr>
<tr><td>2</td><td>Breakeven (Org)</td><td><strong>3 customers</strong></td><td>$36K MRR from 3 enterprise contracts</td></tr>
<tr><td>3</td><td>Runway at $1M raise</td><td><strong>37+ months</strong></td><td>3+ years at base burn</td></tr>
<tr><td>4</td><td>Monthly burn</td><td><strong>$26.5K</strong></td><td>2 founders + ops (Kristen = equity only)</td></tr>
<tr><td>6</td><td>Gross margin</td><td><strong>98%+</strong></td><td>BYOK = zero inference cost</td></tr>
<tr><td>7</td><td>Series A trigger</td><td><strong>$5-10M ARR</strong></td><td>18-24 month target</td></tr>
<tr><td>8</td><td>Pre-money valuation</td><td><strong>$9M</strong></td><td>10% dilution = $10M post-money</td></tr>
<tr><td>9</td><td>Starter ARR/customer</td><td><strong>$5,988</strong></td><td>$499/mo = bridge tier</td></tr>
<tr><td>10</td><td>Team ARR/customer</td><td><strong>$24K</strong></td><td>$2K/mo = standard SMB</td></tr>
<tr><td>11</td><td>Org ARR/customer</td><td><strong>$144K</strong></td><td>$12K/mo = mid-market</td></tr>
<tr><td>12</td><td>Enterprise ARR/customer</td><td><strong>$600K</strong></td><td>$50K/mo = white glove</td></tr>
<tr><td>13</td><td>Weighted avg ARPA</td><td><strong>$30.5K</strong></td><td>60:25:10:5 tier mix</td></tr>
<tr><td>14</td><td>Founder ownership at exit</td><td><strong>80% (40% each)</strong></td><td>No further dilution (staircase model)</td></tr>
<tr><td>15</td><td>Investor return at $1B</td><td><strong>42.2x</strong></td><td>$1M becomes $42.2M</td></tr>
<tr><td>16</td><td>Sales cycle</td><td><strong>3-6 months</strong></td><td>Enterprise governance deals</td></tr>
<tr><td>17</td><td>Close rate</td><td><strong>5-10%</strong></td><td>Standard B2B SaaS</td></tr>
<tr><td>18</td><td>Contribution margin</td><td><strong>98.3%</strong></td><td>Holds at any scale</td></tr>
<tr><td>19</td><td>Rounds to profitability</td><td><strong>1</strong></td><td>Pre-seed only (staircase model)</td></tr>
<tr><td>20</td><td>CAC payback</td><td><strong>6-12 months</strong></td><td>At $70.8K ARPA with 98% CM</td></tr>
</tbody>
</table>

<h2>Customer Count Matrix</h2>
<p><strong>How many customers at each tier for target ARR?</strong></p>
<table>
<thead><tr><th>ARR Target</th><th>$499/mo Starter</th><th>$2K/mo Team</th><th>$12K/mo Org</th><th>$50K/mo Enterprise</th></tr></thead>
<tbody>
<tr><td>$1M</td><td>167</td><td>42</td><td>7</td><td>2</td></tr>
<tr><td>$5M</td><td>835</td><td>208</td><td>35</td><td>8</td></tr>
<tr><td>$10M</td><td>1,670</td><td>417</td><td>69</td><td>17</td></tr>
<tr><td>$100M</td><td>16,700</td><td>4,167</td><td>694</td><td>167</td></tr>
</tbody>
</table>
<div class="callout"><strong>Key insight:</strong> Starter is the WEDGE, not the target. The play: land 50+ Starter, convert 15% to Team quarterly, Team/Org carry the ARR. Realistic Y1 blended: 30 Starter + 8 Team + 2 Org = $55K MRR ($660K ARR).</div>

<h2>Runway Scenarios</h2>
<table>
<thead><tr><th>Burn Rate</th><th>$1M Raise</th><th>$500K Raise</th></tr></thead>
<tbody>
<tr><td>$26.5K/mo</td><td><strong>37+ months</strong></td><td>18+ months</td></tr>
<tr><td>$35.5K/mo (with advisors)</td><td><strong>28 months</strong></td><td>14 months</td></tr>
</tbody>
</table>

<h2>Equity Dilution Waterfall</h2>
<table>
<thead><tr><th>Round</th><th>Dilution</th><th>David %</th><th>Igor %</th><th>Pre-Seed %</th><th>Seed %</th><th>Series A %</th></tr></thead>
<tbody>
<tr><td>Founding</td><td>--</td><td>50%</td><td>50%</td><td>--</td><td>--</td><td>--</td></tr>
<tr><td>After Pre-Seed</td><td>10%</td><td>45%</td><td>45%</td><td>10%</td><td>--</td><td>--</td></tr>
<tr><td>After Seed</td><td>20%</td><td>36%</td><td>36%</td><td>8%</td><td>20%</td><td>--</td></tr>
<tr><td>After Series A</td><td>25%</td><td>27%</td><td>27%</td><td>6%</td><td>15%</td><td>25%</td></tr>
<tr><td>After Series C</td><td>12%</td><td>19%</td><td>19%</td><td>4.2%</td><td>10.6%</td><td>17.6%</td></tr>
</tbody>
</table>

<h2>Investor Return at Exit</h2>
<table>
<thead><tr><th>Exit Valuation</th><th>Investor Value</th><th>Ownership</th><th>Return Multiple</th></tr></thead>
<tbody>
<tr><td>$50M</td><td>$2.1M</td><td>4.2%</td><td>2.1x</td></tr>
<tr><td>$100M</td><td>$4.2M</td><td>4.2%</td><td>4.2x</td></tr>
<tr><td>$250M</td><td>$10.6M</td><td>4.2%</td><td><strong>10.6x</strong></td></tr>
<tr><td>$500M</td><td>$21.1M</td><td>4.2%</td><td><strong>21.1x</strong></td></tr>
<tr><td>$1B</td><td>$42.2M</td><td>4.2%</td><td><strong>42.2x</strong></td></tr>
</tbody>
</table>

<h2>Gross Margin by Tier</h2>
<table>
<thead><tr><th>Tier</th><th>Annual Revenue</th><th>Annual COGS</th><th>Gross Margin</th></tr></thead>
<tbody>
<tr><td>Starter ($499/mo)</td><td>$5,988</td><td>$180</td><td><strong>97.0%</strong></td></tr>
<tr><td>Team ($2K/mo)</td><td>$24K</td><td>$600</td><td><strong>97.5%</strong></td></tr>
<tr><td>Org ($12K/mo)</td><td>$144K</td><td>$2.4K</td><td><strong>98.3%</strong></td></tr>
<tr><td>Enterprise ($50K/mo)</td><td>$600K</td><td>$6K</td><td><strong>99.0%</strong></td></tr>
</tbody>
</table>
<div class="callout"><strong>Strongest number:</strong> BYOK means zero LLM inference cost. The largest expense for AI-powered SaaS does not exist in our model.</div>
"""
    return wrap("Financial Reference Card", "Pre-Seed Investor Conversations", body)


# ============================================================
# DOC 4: VC Objections
# ============================================================
def build_objections():
    objections = [
        ("Code review tools already exist (Greptile, CodeRabbit). How are you different?",
         "We are not code review. We are code governance. Code review suggests changes. We create tamper-proof judgment receipts proving WHO approved WHAT and WHEN -- admissible in court. Different buyer (CISO, not dev lead), different budget line (compliance, not DevOps)."),
        ("You have no customers, no revenue, no pilots. Why should I invest?",
         "Andy Ellis (ex-CSO Akamai, Partner at YL Ventures) signed up on our landing page within 48 hours of launch -- unprompted. TD Bank's VP of Engineering responded to cold outreach asking about differentiators. Phil Venables (ex-CISO Google Cloud, Ballistic Ventures) independently asked DD questions. 4.8% cold response rate from unknown founders. Market pull at zero spend is the strongest signal at pre-seed."),
        ("Microsoft/GitHub could just build this.",
         "A proprietary company cannot build a credible governance standard -- would you trust Microsoft to audit Microsoft's code? Open-source core is structurally required for governance legitimacy, and incumbents cannot open-source without cannibalizing their platform economics."),
        ("Your sales cycle is 3-6 months. That's long.",
         "The free GitHub Action installs in 2 minutes and delivers value on the first PR. Starter tier at $499/mo with 30-day free trial converts without a sales call. The 3-6 month cycle is for Team ($2K) and Org ($12K) -- by then the customer already has months of governance data proving value. Product-led, not sales-led."),
        ("Open source means anyone can fork you.",
         "They can fork the kernel, but they cannot fork the audit history. Once a company builds 6 months of tamper-proof governance records, switching costs are enormous. The open core IS the moat -- it drives adoption that locks in the paid tiers."),
        ("AI governance is not a real category yet. You're creating a market.",
         "We are not. DORA (already in effect), EU AI Act, SOC2, HIPAA -- these are existing compliance mandates. We are the first tool that generates court-admissible proof of compliance for AI-generated code changes. The market exists, the budget exists."),
        ("How do you get to $1B?",
         "7,000 customers at $12K/month (Org tier). That is CrowdStrike scale. Our 97-99% margins mean every dollar of revenue is almost pure profit. Realistic Year 1: $660K ARR from 30 Starter + 8 Team + 2 Org. Starter is the volume wedge that feeds Team/Org upgrades."),
        ("Two founders, no sales team. How do you sell enterprise?",
         "$1M raise buys 37+ months of runway at $26.5K/month burn. First 12 months: David sells, Igor builds. At 3 Org customers we are breakeven and hire a sales rep. AI-native operations ($1K/month API budget) replace 3-4 FTEs worth of manual work."),
        ("What's your moat? This seems replicable.",
         "Five moats from the Seven Powers framework: (1) Counter-positioning -- incumbents cannot open-source their audit trail. (2) Switching costs -- audit history is sticky after 6 months. (3) Network effect -- every participant strengthens the governance standard. (4) Potential cornered resource -- exclusive partnership for model confidence scoring (provisional patents). (5) Process power -- AI-native compound automation loop."),
        ("Managed services don't get tech multiples.",
         "White-glove is 5% of revenue (Enterprise tier only). 95% is pure SaaS with 97-99% margins. We lead with Starter ($499/mo self-serve), Team ($2K), and Org ($12K) -- managed service is upsell, not core model."),
    ]
    items = ""
    for i, (q, a) in enumerate(objections, 1):
        items += f"""
<div class="objection">{i}. "{q}"</div>
<div class="answer">{a}</div>
"""
    body = f"""
<p style="margin-bottom: 16px;">The 10 most common investor objections, with crisp answers grounded in data.</p>
{items}
<div class="callout"><strong>Preparation note:</strong> These answers are drilled and ready for live conversation. Every claim is backed by the financial model, competitive landscape analysis, and market signals documented in the accompanying package.</div>
"""
    return wrap("10 VC Objections -- Answered", "Pre-Emptive Responses for Investor Conversations", body)


# ============================================================
# DOC 5: Developer ROI Calculator
# ============================================================
def build_dev_roi():
    body = """
<div class="callout"><strong>The question for every engineering team:</strong> If 65% of your PRs ship with no real review, and AI is generating code 1.7x more likely to have defects, what is the cost of doing nothing?</div>

<h2>Default Inputs (50-Developer Team)</h2>
<table>
<thead><tr><th>Input</th><th>Default Value</th></tr></thead>
<tbody>
<tr><td>Number of developers</td><td>50</td></tr>
<tr><td>Avg fully-loaded annual compensation</td><td>$175,000</td></tr>
<tr><td>PRs per developer per week</td><td>4</td></tr>
<tr><td>% of PRs that get meaningful review today</td><td>35%</td></tr>
<tr><td>Using AI coding assistants?</td><td>Yes</td></tr>
<tr><td>Production incidents per quarter</td><td>4</td></tr>
</tbody>
</table>

<h2>1. Rubber-Stamp Cost: Unreviewed PRs</h2>
<p>65% of merged PRs are approved after minimal review -- zero comments or fewer than 3 words total (Graphite, 2025 study of 50M+ PRs).</p>
<pre>Unreviewed PRs/year = 50 devs x 4 PRs/wk x 52 wks x 0.65 = 6,760
Defects (1 per 10 unreviewed)                              = 676/year
Cost to fix in production (30x multiplier, NIST)           = $4,500 each

Annual cost of escaped defects = 676 x $4,500 = $3,042,000</pre>

<h3>With AI Coding Assistants (the Multiplier)</h3>
<p>AI-generated code: 1.7x more issues (CodeRabbit, 470-PR study), 2.74x more security vulns (Veracode), 322% increase in privilege escalation (Apiiro).</p>
<pre>AI-adjusted defects   = 676 x 1.7 = 1,149/year
AI-adjusted cost      = 1,149 x $4,500 = $5,170,500/year

Security incidents (1% of 1,852 security issues)
  = 18 x $150,000 = $2,700,000</pre>

<h2>2. Production Incident Cost</h2>
<pre>Annual = 16 incidents x 8 hrs x 3 people x $84/hr = $32,256 direct
Fully loaded (7x multiplier)                       = $225,792/year</pre>

<h2>3. Manual Review Time Tax</h2>
<pre>Current review labor = 50 x 4 x 1.5 hrs x 52 x $84/hr = $1,310,400/year
GuardSpine saves 40-60% (automates L0-L2)              = $655,200/year recovered</pre>

<h2>4. Technical Debt Prevention</h2>
<pre>Debt labor = 50 devs x 13.5 hrs/wk x 52 wks x $84/hr  = $2,948,400/year
GuardSpine prevents 15-25% of new debt                  = $589,680/year avoided</pre>

<h2>Total Annual Cost Without GuardSpine</h2>
<table>
<thead><tr><th>Risk Category</th><th>Annual Cost</th></tr></thead>
<tbody>
<tr><td>Escaped defects from rubber-stamped PRs</td><td>$3,042,000</td></tr>
<tr><td>AI code defect multiplier</td><td>+$2,128,500</td></tr>
<tr><td>Production incident costs (fully loaded)</td><td>$225,792</td></tr>
<tr><td>Code review labor (opportunity cost)</td><td>$1,310,400</td></tr>
<tr><td>Technical debt accumulation</td><td>$589,680</td></tr>
<tr style="background: #fef2f2;"><td><strong>Total annual risk exposure</strong></td><td><strong>$7,296,372</strong></td></tr>
</tbody>
</table>

<h2>ROI with GuardSpine (Team Tier: $19,200/year)</h2>
<div class="metric-grid">
    <div class="metric-card">
        <div class="value">$3.1M</div>
        <div class="label">Annual Value (conservative)</div>
    </div>
    <div class="metric-card">
        <div class="value">16,337%</div>
        <div class="label">ROI</div>
    </div>
    <div class="metric-card">
        <div class="value">~2 days</div>
        <div class="label">Payback Period</div>
    </div>
</div>

<table>
<thead><tr><th>Value Driver</th><th>% Captured</th><th>Annual Value</th></tr></thead>
<tbody>
<tr><td>Defects caught pre-merge</td><td>40%</td><td>$1,216,800</td></tr>
<tr><td>AI defect multiplier reduction</td><td>30%</td><td>$638,550</td></tr>
<tr><td>Incidents prevented</td><td>25%</td><td>$56,448</td></tr>
<tr><td>Review time recovered</td><td>50%</td><td>$655,200</td></tr>
<tr><td>Tech debt avoided</td><td>20%</td><td>$589,680</td></tr>
<tr style="background: #f0fdfa;"><td><strong>Total annual value</strong></td><td></td><td><strong>$3,156,678</strong></td></tr>
<tr><td>GuardSpine Team cost</td><td></td><td>($19,200)</td></tr>
<tr style="background: #f0fdfa;"><td><strong>Net savings</strong></td><td></td><td><strong>$3,137,478</strong></td></tr>
</tbody>
</table>
<div class="callout"><strong>Even at 10% of these estimates,</strong> the ROI is 1,633% -- $315K savings on a $19K investment.</div>

<h2>Benchmarks Cited</h2>
<table>
<thead><tr><th>Claim</th><th>Source</th><th>Year</th></tr></thead>
<tbody>
<tr><td>65% of PRs approved with minimal/zero review</td><td>Graphite (50M+ PRs)</td><td>2025</td></tr>
<tr><td>30x cost multiplier: production vs review</td><td>NIST, HackerOne</td><td>2024</td></tr>
<tr><td>1.7x more issues in AI-generated code</td><td>CodeRabbit (470 PRs)</td><td>2024</td></tr>
<tr><td>2.74x more security issues in AI code</td><td>Veracode (100+ LLMs)</td><td>2025</td></tr>
<tr><td>322% increase in privilege escalation</td><td>Apiiro</td><td>2025</td></tr>
<tr><td>$4.44M avg breach cost (global)</td><td>IBM Cost of a Data Breach</td><td>2025</td></tr>
<tr><td>13.5 hrs/week on tech debt per dev</td><td>Stripe/HackerOne</td><td>2024</td></tr>
</tbody>
</table>
"""
    return wrap("Developer ROI Calculator", "The Cost of Uncaught AI Code Issues", body)


# ============================================================
# GENERATE ALL PDFs
# ============================================================
def main():
    docs = [
        ("01-Executive-Summary.pdf", build_exec_summary),
        ("02-Competitive-Landscape.pdf", build_competitive),
        ("03-Financial-Reference.pdf", build_financial),
        ("04-VC-Objections-Answered.pdf", build_objections),
        ("05-Developer-ROI-Calculator.pdf", build_dev_roi),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for filename, builder in docs:
            html = builder()
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            path = OUT_DIR / filename
            page.pdf(
                path=str(path),
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "12mm", "left": "0"},
                display_header_footer=True,
                header_template="<span></span>",
                footer_template='<div style="width:100%;text-align:center;font-size:9px;color:#9ca3af;padding-top:4px;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
            )
            page.close()
            sz = path.stat().st_size / 1024
            print(f"  {filename} ({sz:.0f} KB)")

        browser.close()
    print(f"\nAll PDFs saved to: {OUT_DIR}")


if __name__ == "__main__":
    main()
