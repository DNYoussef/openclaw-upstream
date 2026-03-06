import sqlite3
import os

conn = sqlite3.connect(os.path.expanduser("~/.claude/outreach/outreach.db"))
cur = conn.cursor()

updates = []

# 1. Moriah Hara (3f3aa9e42034)
updates.append(("3f3aa9e42034",
"""Hi Moriah,

Building the global VISA PCI Security Assessor program -- certifying thousands of practitioners -- is the kind of work that makes this pitch easy to land.

AI-generated code is creating a governance gap auditors are starting to ask about: who approved the code, and where is the evidence? Current tooling can not answer that.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=e18ff814#roi

- David""",
"Building the VISA PCI Security Assessor program is the kind of work that makes this pitch easy to land."))

# 2. Nashira Spencer (889223276f0d)
updates.append(("889223276f0d",
"""Hi Nashira,

Going from DTCC -- critical financial infrastructure -- to Stitch Fix means adapting governance rigor to a fast-moving AI-heavy engineering culture. That transition is exactly where the gap shows up.

AI-generated code is shipping faster than teams can review. Regulators are asking: who approved it, and where is the evidence?

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=2ecb4a04#roi

- David""",
"Going from DTCC to Stitch Fix means adapting governance rigor to a fast-moving AI-heavy engineering culture."))

# 3. Nasrin Rezai (e7e89be0a188)
updates.append(("e7e89be0a188",
"""Hi Nasrin,

Your RSAC 2025 panel on AI-era authentication and the NACD cyber risk handbook landed -- boards are asking for evidence on AI code governance and current tooling can not produce it.

Protecting 90M+ consumers under FCC compliance while navigating AI authentication challenges is exactly where this gap shows up.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, ISO 27001.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=ac223872#roi

- David""",
"Your RSAC 2025 panel on AI-era authentication and the NACD cyber risk handbook landed."))

# 4. Neil Daswani (5392b4421d1e) - HIPAA wrong for academia, fix to ISO 27001
updates.append(("5392b4421d1e",
"""Hi Neil,

Teaching AI security at Stanford with Dan Boneh while running a consultancy on trustworthy AI systems -- you see both the theory and the implementation gap.

AI-generated code is shipping faster than governance can keep up. Auditors are asking: who approved it, and where is the evidence? Academic security programs need real-world tools to point to.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, ISO 27001.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=f4c62a27#roi

- David""",
"Teaching AI security at Stanford with Dan Boneh while running a consultancy on trustworthy AI -- you see both the theory and the implementation gap."))

# 5. Nick Sturgeon (68e23733b942)
updates.append(("68e23733b942",
"""Hi Nick,

The Medical Device Security Lab at IU Health -- that work is exactly why this pitch makes sense for you.

Connected medical devices, social engineering, and HIPAA compliance in a system where patient safety is at stake. The governance gap around AI-generated code is where the audit exposure lives.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=ad9bbe3a#roi

- David""",
"The Medical Device Security Lab at IU Health -- that work is exactly why this pitch makes sense for you."))

# 6. Nicole Perlroth (6b806985c796) - CRITICAL Ballistic connection
updates.append(("6b806985c796",
"""Hi Nicole,

I have been in conversation with Phil Venables at Ballistic about GuardSpine -- open-source AI code governance with tamper-proof audit trails. Given your cybersecurity investment lens at Ballistic, wanted to get this on your radar too.

Risk-tiered L0-L4, multi-model deliberation, offline-verifiable hash chain. Maps to SOC 2, ISO 27001. The kind of infrastructure-level category Phil knows well.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=e7dd398e#roi

- David""",
"I have been in conversation with Phil Venables at Ballistic about GuardSpine -- wanted to get this on your radar too."))

# 7. Oren Yunger (80d5e4d626c2)
updates.append(("80d5e4d626c2",
"""Hi Oren,

SVCI -- a CISO angel syndicate -- means you evaluate code governance tools from both operator and investor perspectives. That is exactly the lens I need.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2. Open-source core, paid tiers for team and enterprise.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=3302f6f9#roi

- David""",
"SVCI -- a CISO angel syndicate -- means you evaluate code governance tools from both operator and investor perspectives."))

# 8. Pat Opet (c49f72b9c237) - Great research (open letter to SaaS vendors)
updates.append(("c49f72b9c237",
"""Hi Pat,

Your open letter to SaaS vendors -- security by default, transparency, accountability -- is exactly the governance gap I am building to fill on the code side.

AI-generated code is shipping faster than teams can review. Auditors are asking: who approved the AI code that handles customer financial data? Current tooling can not answer that with evidence.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=2da47bac#roi

- David""",
"Your open letter to SaaS vendors -- security by default, transparency, accountability -- is exactly the governance gap I am building to fill."))

# 9. Philip Martin (dd0ccbe87936)
updates.append(("dd0ccbe87936",
"""Hi Philip,

"Calculated, knowing, understood risk" -- that philosophy is exactly the gap I am building to fill. Most AI code governance tools block or approve. None produce evidence of the decision.

Crypto exchange facing nation-state attacks, AI-powered scammers, and regulatory scrutiny across global jurisdictions. You need governance that moves at the speed of product.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=7806d811#roi

- David""",
'"Calculated, knowing, understood risk" -- that philosophy is exactly the gap I am building to fill.'))

# 10. Prashant Kalia (4fbbeec41003)
updates.append(("4fbbeec41003",
"""Hi Prashant,

Joining Flutterwave as CRCO after the fraud incidents means you inherited a compliance story that investors and regulators are watching closely. Pre-IPO, every governance artifact matters.

AI-generated code is shipping faster than teams can review. Auditors ask: who approved it, where is the evidence? Current tooling can not answer that.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=a89c76ea#roi

- David""",
"Joining Flutterwave as CRCO after the fraud incidents means every governance artifact matters pre-IPO."))

# 11. Randall Frietzsche (9044429e659a) - "specifically, [raw research paste]" dossier language
updates.append(("9044429e659a",
"""Hi Randall,

CISO of the Year, FBI CISO Academy grad, and teaching risk management at Harvard -- you know exactly how hard it is to produce governance evidence at a safety-net hospital budget.

AI-generated code is creating a new audit exposure. HIPAA auditors are starting to ask: who approved the AI code, and where is the evidence? Current tooling can not answer that.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=1b1dbb35#roi

- David""",
"CISO of the Year, FBI CISO Academy, teaching risk at Harvard -- you know how hard governance evidence is on a safety-net hospital budget."))

# 12. Rich Baich (10f25a264737) - "Reference your" leaked instruction
updates.append(("10f25a264737",
"""Hi Rich,

CIA CISO to AT&T CISO -- your career is built on embedding security into infrastructure rather than bolting it on. That philosophy is exactly what I am building.

200M+ subscribers, FCC compliance, and AI integration into network products. The governance gap around AI-generated code is where the audit exposure lives.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, ISO 27001.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=cea5867c#roi

- David""",
"CIA CISO to AT&T CISO -- your career is built on embedding security into infrastructure rather than bolting it on."))

# 13. Rinki Sethi (e381d2288a05) - "Reference your" leaked, "you evaluates" grammar error
updates.append(("e381d2288a05",
"""Hi Rinki,

Lockstep Ventures plus CISO roles at Twitter, Rubrik, and BILL -- you evaluate security tools from both operator and investor perspectives. That is exactly the lens I need.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, ISO 27001.

Open-source core with paid team and enterprise tiers. The kind of infrastructure-level category Lockstep invests in.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=8fa725f0#roi

- David""",
"Lockstep Ventures plus CISO at Twitter, Rubrik, BILL -- you evaluate security tools from both operator and investor perspectives."))

# 14. Ryan Field (1e4ba89d6358) - "specifically, [raw research paste]" dossier language
updates.append(("1e4ba89d6358",
"""Hi Ryan,

Top Cybersecurity Leaders 2024, PwC pen testing background, and teaching CISSP at Hawaii Pacific -- you have seen vendor risk and compliance from every angle.

At Bank of Hawaii, OCC and FDIC regulatory pressure plus multi-vendor supply chain risk. The governance gap around AI-generated code is where the audit exposure lives.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=65259752#roi

- David""",
"Top Cybersecurity Leaders 2024, PwC pen testing, teaching CISSP -- you have seen compliance from every angle."))

# 15. Sahan Fernando (fadc9b060a11) - Hook generic "the angle on code governance resonated" -- tighten
updates.append(("fadc9b060a11",
"""Hi Sahan,

Your MedCity piece on the three key challenges for healthcare CISOs -- compliance evidence is core to every one of them. That is exactly the gap I am building to fill.

Pediatric healthcare, sensitive population data, HIPAA. AI-generated code is creating new audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=81231618#roi

- David""",
"Your MedCity piece on the three key challenges for healthcare CISOs -- compliance evidence is core to every one of them."))

# 16. Salman Khan (7853bfb8863d) - "Reference your" leaked, truncated hook
updates.append(("7853bfb8863d",
"""Hi Salman,

Your HealthSec 2026 panel on cybersecurity budget allocation -- that is the exact tension I built GuardSpine to solve. Open-source, so budget is not the blocker. Governance evidence is the output.

Public health system, HIPAA compliance, constrained budgets. AI-generated code is creating new audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=a2bab305#roi

- David""",
"Your HealthSec 2026 panel on budget allocation -- that is the exact tension I built GuardSpine to solve."))

# 17. Sarah Browne (eee01d1d8ce8) - WRONG COMPANY (now at Payoneer, not Stripe). Fix.
updates.append(("eee01d1d8ce8",
"""Hi Sarah,

CRO at Stripe, now bringing that compliance rigor to Payoneer -- DORA, PCI DSS, and SOC 2 requirements are tightening across both.

AI-generated code is shipping faster than teams can review. Regulators are starting to ask: who approved the AI code that handles customer financial data? Current tooling can not answer that with evidence.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=65edc164#roi

- David""",
"CRO at Stripe, now bringing that compliance rigor to Payoneer -- requirements are tightening across both."))

# 18. Sebastian Lange (6247d88d3c06) - "Reference your" leaked, "your's" typo, verbose hook
updates.append(("6247d88d3c06",
"""Hi Sebastian,

Risk-based exception management at SAP scale -- that blog post landed because it is the exact problem nobody has tooling for yet.

Managing security at massive enterprise SaaS with an ever-increasing attack surface. You need automated governance that scales with SAP cloud, not more manual review.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, EU AI Act.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=c45fa65f#roi

- David""",
"Risk-based exception management at SAP scale -- that blog post landed because nobody has tooling for it yet."))

# 19. Shamla Naidoo (feef92cfec4c) - Broken sentence "you demonstrable governance artifacts (audit trails, s)"
updates.append(("feef92cfec4c",
"""Hi Shamla,

"The Cyber Savvy Boardroom" with Homaira Akbari -- your entire career is translating security into board language. Boards need governance artifacts they can understand and trust.

AI-generated code is creating a new blind spot. Auditors are asking: who approved it, and where is the evidence? Current tooling can not produce artifacts boards can review.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, ISO 27001.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=94233d79#roi

- David""",
'"The Cyber Savvy Boardroom" -- your entire career is translating security into board language. Boards need governance artifacts they can trust.'))

# 20. Sherron Burgess (929d5dd0d7ad) - OK but second paragraph is third-person description. Fix.
updates.append(("929d5dd0d7ad",
"""Hi Sherron,

Managing security across 109 countries and 12 brands is no small thing. That scale is exactly why a blind spot I keep seeing matters for your team.

PCI DSS compliance across global franchise operations, expanding scope into privacy and trust. You need governance automation that scales across jurisdictions, not more manual review.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to PCI DSS, SOC 2, DORA.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=3af5d0e0#roi

- David""",
"Managing security across 109 countries and 12 brands -- that scale is exactly why this blind spot matters for your team."))

# 21. Shyama Rose (dc326ff62812) - "Your point that [self-description] stuck with me" wrong template
updates.append(("dc326ff62812",
"""Hi Shyama,

Hands-on leader with a hacker's mindset, CIS benchmark author, AppSec lecturer at NYU -- you understand code-level security governance deeply. That is exactly the gap I am building to fill.

Fintech CISO dealing with consumer financial data at scale. AI-generated code is creating audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=ead753a0#roi

- David""",
"CIS benchmark author, AppSec lecturer at NYU, hacker mindset -- you understand code-level security governance deeply."))

# 22. Sibongile Ngako (6e8a84666ad3) - "Reference your" leaked, "your described" grammar
updates.append(("6e8a84666ad3",
"""Hi Sibongile,

"The bar is incredibly high for AI when handling money" -- your Banking Dive quote is exactly the gap I am building to fill. AI guardrails for fintech code deployments need automated governance, not just policy documents.

Building compliance frameworks at a fast-moving fintech that uses AI across underwriting, fraud, and product. You need tooling that keeps pace.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=781ec794#roi

- David""",
'"The bar is incredibly high for AI when handling money" -- your Banking Dive quote is exactly the gap I am building to fill.'))

# 23. Stephen Bennett (dcec21f83711) - Hook OK but "the angle on code governance resonated" is generic filler
updates.append(("dcec21f83711",
"""Hi Stephen,

"7 Pizzas per second" at Black Hat MEA -- building a security program from scratch across 3,700+ stores and 13 regions means every governance tool needs to scale from day one.

PCI DSS compliance across global franchise operations. AI-generated code is creating new audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to PCI DSS, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=644c67e9#roi

- David""",
'"7 Pizzas per second" at Black Hat MEA -- building security from scratch across 3,700+ stores means every governance tool needs to scale from day one.'))

# 24. Steven Ramirez (a36e65f9c96a) - "Reference your" leaked, truncated words "ation"
updates.append(("a36e65f9c96a",
"""Hi Steven,

Dual CISO/CTO, teaching cybersecurity at Harvard, and your HIMSS talk on building cyber resilience from the top down -- you see both the technical and the governance side.

Regional health system managing rapid digital transformation and third-party vendor risk. AI-generated code is creating new HIPAA audit exposure.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=6cc10e20#roi

- David""",
"Dual CISO/CTO, teaching cybersecurity at Harvard, HIMSS talk on resilience from the top -- you see both sides."))

# 25. Susan Koski (c99b5c9befed) - "since puts you" broken template
updates.append(("c99b5c9befed",
"""Hi Susan,

700-person security team, Global Fusion Center converging physical, fraud, and cyber ops, and a board seat at Cyber Risk Institute -- you are operating at a scale where manual governance does not work.

Top-10 US bank, OCC/FDIC regulatory pressure. AI-generated code is creating new audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=3f47f41b#roi

- David""",
"700-person team, Global Fusion Center, Cyber Risk Institute board -- you operate at a scale where manual governance does not work."))

# 26. Ted Schlein (b6c0de23b80e) - "Reference Phil Venables" leaked instruction, verbose
updates.append(("b6c0de23b80e",
"""Hi Ted,

I have been in conversation with Phil Venables at Ballistic about GuardSpine. Given Ballistic's cybersecurity-only thesis and your track record backing category creators, wanted to get this on your radar directly.

Open-source AI code governance with tamper-proof audit trails. Risk-tiered L0-L4, multi-model deliberation, offline-verifiable hash chain. Maps to SOC 2. Open-source core, paid team and enterprise tiers.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=cfd6653f#roi

- David""",
"I have been in conversation with Phil at Ballistic about GuardSpine -- wanted to get this on your radar directly."))

# 27. Tim Brown (05d7a21bdb76) - "since puts you" broken, but GREAT research (SEC prosecution). Rewrite.
updates.append(("05d7a21bdb76",
"""Hi Tim,

First CISO ever charged by the SEC. Your AISA CyberCon keynote on trust, context, and leading through crisis -- nobody in the world understands the need for tamper-proof governance evidence better than you.

Supply chain security governance is your lived experience. AI-generated code is creating the next version of that exposure.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, EU AI Act.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=85b19181#roi

- David""",
"First CISO ever charged by the SEC -- nobody understands the need for tamper-proof governance evidence better."))

# 28. Tim Held (a1635adac6d2) - "Your point that [patent name] stuck with me" wrong template
updates.append(("a1635adac6d2",
"""Hi Tim,

Co-inventing Source Request Monitoring -- a patent for detecting fraudulent transactions -- tells me you think in terms of provable evidence chains. That is exactly what I am building for code governance.

Global Payments, PCI DSS, OCC regulatory requirements at global scale. AI-generated code is creating new audit exposure and current tooling can not produce the evidence trail.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=12cf4268#roi

- David""",
"Co-inventing Source Request Monitoring tells me you think in terms of provable evidence chains -- that is exactly what I am building."))

# 29. Tim McKnight (94d91e0e3066) - "since puts you" broken template
updates.append(("94d91e0e3066",
"""Hi Tim,

Hired 8 months after the Change Healthcare ransomware attack to rebuild security at the largest US health insurer. The pressure to demonstrate governance improvements with tamper-proof evidence is enormous.

AI-generated code is creating new HIPAA audit exposure. Regulators ask: who approved it, where is the evidence? Current tooling can not answer that.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to HIPAA, SOC 2.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=b353bc1d#roi

- David""",
"Hired to rebuild security after the Change Healthcare attack -- the pressure for tamper-proof governance evidence is enormous."))

# 30. Tomas Maldonado (24a63571fa18) - "specifically, [truncated raw research]" dossier language
updates.append(("24a63571fa18",
"""Hi Tomas,

Securing the Super Bowl -- a SEAR 1 designated event -- plus 32 franchises, 30 stadiums, and hundreds of millions of fans. That attack surface is why automated governance matters.

AI-generated code is creating new audit exposure. Current tooling can not produce evidence of who approved what.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, PCI DSS.

Cost model for what this saves on audit prep: https://guardspine.ai/security?utm_source=linkedin_connect&utm_campaign=ciso100_feb26&utm_content=59954ba2#roi

- David""",
"Securing the Super Bowl, 32 franchises, 30 stadiums -- that attack surface is why automated governance matters."))

# 31. Wade Bicknell (3f8bdd690cdb) - "since puts you" variant, but GREAT quote. Rewrite to use it.
updates.append(("3f8bdd690cdb",
"""Hi Wade,

"You can not audit how AI thinks, but you can audit what it does" -- your Help Net Security interview is exactly what I built. That quote could be our tagline.

Building a SOC team at CFA Institute, DHS and Deutsche Bank background. You are actively articulating the problem and hiring to solve it.

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof hash chain. Maps to SOC 2, DORA, PCI DSS.

Cost model: https://guardspine.ai/security?utm_source=linkedin_dm&utm_campaign=ciso100_feb26&utm_content=92e4e95d#roi

- David""",
'"You can not audit how AI thinks, but you can audit what it does" -- your Help Net Security interview is exactly what I built.'))

# Execute all updates
conn.executemany(
    "UPDATE prospects SET message_draft=?, hook_text=? WHERE id=?",
    [(msg, hook, pid) for pid, msg, hook in updates]
)
conn.commit()
print(f"Updated {len(updates)} prospects")

# Verify
cur.execute("SELECT id, name, hook_text FROM prospects WHERE id IN (%s)" % ",".join(["'%s'" % u[0] for u in updates]))
for row in cur.fetchall():
    print(f"  OK: {row[1]} ({row[0][:8]}...) hook={row[2][:60]}...")
conn.close()
