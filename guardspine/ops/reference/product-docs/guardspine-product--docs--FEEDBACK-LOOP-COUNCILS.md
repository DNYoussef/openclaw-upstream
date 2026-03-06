# Feedback Loop Council Assignments

Each of the 12 feedback loops has a 3-member Council panel for escalation.

## Council Assignment Matrix

### Assignment Logic

1. **Source Owner**: Department lead who generates the loop output
2. **Target Owner**: Department lead who receives/implements the output
3. **Neutral Arbiter**: Third party with no direct stake in either side

**Same-Owner Rule**: If same persona owns both source and target, expand council based on:

- Risk blast radius (how many departments affected)
- Add representatives from affected departments
- Minimum 3 members, expand to 5 for high blast radius

### TIER 1: Core Operations (6 Loops)

| Loop                       | Source Owner               | Target Owner               | Neutral Arbiter    | Blast Radius         | Expansion if Needed                      |
| -------------------------- | -------------------------- | -------------------------- | ------------------ | -------------------- | ---------------------------------------- |
| **Product-to-Engineering** | Product Owner              | Architecture Reviewer      | Executive Sponsor  | Medium (2 depts)     | +DevOps Lead, +QA                        |
| **Sales-to-Product**       | Finance Controller (Sales) | Product Owner              | Customer Advocate  | Medium (2 depts)     | +Marketing, +Support                     |
| **Support-to-Engineering** | Customer Advocate          | Architecture Reviewer      | DevOps Lead        | Medium (2 depts)     | +Product Owner, +QA                      |
| **Marketing-to-Sales**     | Finance Controller (Mktg)  | Finance Controller (Sales) | Customer Advocate  | Low (2 depts)        | _Same owner: +Executive, +Product Owner_ |
| **Legal-to-Sales**         | Legal Counsel              | Finance Controller         | Compliance Officer | Medium (2 depts)     | +Risk Analyst, +Ethics                   |
| **Ops-to-All**             | DevOps Lead                | _Varies by target_         | Executive Sponsor  | **High (all depts)** | +Security, +Compliance, +Finance         |

### TIER 2: Quality & Compliance (3 Loops)

| Loop                  | Source Owner         | Target Owner          | Neutral Arbiter    | Blast Radius       | Expansion if Needed            |
| --------------------- | -------------------- | --------------------- | ------------------ | ------------------ | ------------------------------ |
| **Security-to-All**   | Security Auditor     | _Varies by target_    | Compliance Officer | **Critical (all)** | +Legal, +Executive, +DevOps    |
| **QA-to-Engineering** | Performance Engineer | Architecture Reviewer | DevOps Lead        | Medium (2 depts)   | +Product Owner, +Security      |
| **Compliance-to-All** | Compliance Officer   | _Varies by target_    | Legal Counsel      | **Critical (all)** | +Security, +Executive, +Ethics |

### TIER 3: Strategic & Data (3 Loops)

| Loop                    | Source Owner                 | Target Owner               | Neutral Arbiter    | Blast Radius     | Expansion if Needed                 |
| ----------------------- | ---------------------------- | -------------------------- | ------------------ | ---------------- | ----------------------------------- |
| **Customer-to-Product** | Customer Advocate            | Product Owner              | Executive Sponsor  | Medium (3 depts) | +Support, +Sales, +Marketing        |
| **Data-to-Product**     | Architecture Reviewer (Data) | Product Owner              | Finance Controller | Medium (2 depts) | +Security, +Compliance              |
| **Finance-to-Revenue**  | Finance Controller           | Finance Controller (Sales) | Executive Sponsor  | High (3 depts)   | _Same owner: +Risk Analyst, +Legal_ |

### Blast Radius Definitions

| Radius       | Affected Depts | Council Size | SLA Multiplier |
| ------------ | -------------- | ------------ | -------------- |
| **Low**      | 1-2            | 3 members    | 1.0x           |
| **Medium**   | 3-4            | 3-4 members  | 1.25x          |
| **High**     | 5-7            | 4-5 members  | 1.5x           |
| **Critical** | 8+ (all)       | 5+ members   | 2.0x           |

### Same-Owner Expansion Protocol

When source and target have same owner:

```python
def expand_council_for_same_owner(loop: FeedbackLoop) -> List[Persona]:
    council = [loop.source_owner]  # Start with owner

    # Add affected department representatives
    affected_depts = get_affected_departments(loop)
    for dept in affected_depts[:3]:  # Max 3 additional
        council.append(get_department_lead(dept))

    # Always add Executive Sponsor for oversight
    council.append(EXECUTIVE_SPONSOR)

    return council
```

## Escalation Rules by Risk Tier

### L0 - Informational (Auto-Approve)

- No council involvement required
- Logged for audit trail only

### L1 - Low Risk (4h SLA)

- **Primary** council member notified
- Single approval sufficient
- Async review acceptable

### L2 - Medium Risk (8h SLA)

- **Primary + Secondary** council members notified
- Majority approval required (2 of 3)
- Sync review recommended

### L3 - High Risk (24h SLA)

- **All 3** council members notified
- Supermajority required (2 of 3 with Primary included)
- Sync review required
- Cannot delegate

### L4 - Critical (72h SLA)

- **All 3** council members + **Executive Sponsor** (if not already included)
- Unanimous approval required
- Live review session required
- Human-in-the-loop mandatory

## Inter-Departmental Conflict Resolution

When source and target departments disagree on loop outcomes:

### Conflict Types

| Type                    | Example                                           | Resolution Path                        |
| ----------------------- | ------------------------------------------------- | -------------------------------------- |
| **Priority Conflict**   | Engineering says "not now", Product says "urgent" | Primary council member arbitrates      |
| **Resource Conflict**   | Both depts claim insufficient capacity            | Finance Controller + Executive Sponsor |
| **Quality Conflict**    | QA blocks, Engineering disagrees                  | Architecture Reviewer decides          |
| **Compliance Conflict** | Dept wants exception to policy                    | Compliance Officer + Legal Counsel     |
| **Data Conflict**       | Disagreement on metrics interpretation            | Data owner + Risk Analyst              |

### Resolution by Loop

| Loop                   | Source           | Target          | Conflict Arbiter                   |
| ---------------------- | ---------------- | --------------- | ---------------------------------- |
| Product-to-Engineering | Product          | Engineering     | Architecture Reviewer              |
| Sales-to-Product       | Sales            | Product         | Customer Advocate                  |
| Support-to-Engineering | Support          | Engineering     | Customer Advocate                  |
| Marketing-to-Sales     | Marketing        | Sales           | Finance Controller                 |
| Legal-to-Sales         | Legal            | Sales           | Compliance Officer                 |
| Ops-to-All             | Ops              | Any             | Executive Sponsor                  |
| Security-to-All        | Security         | Any             | Security Auditor (final authority) |
| QA-to-Engineering      | QA               | Engineering     | Architecture Reviewer              |
| Compliance-to-All      | Compliance       | Any             | Legal Counsel                      |
| Customer-to-Product    | Customer Success | Product         | Customer Advocate                  |
| Data-to-Product        | Data             | Product         | Product Owner                      |
| Finance-to-Revenue     | Finance          | Sales/Marketing | Executive Sponsor                  |

### Escalation Ladder for Inter-Departmental Issues

```
Level 1: Department Leads meet (4h to resolve)
    |
    v (unresolved)
Level 2: Primary Council member arbitrates (8h)
    |
    v (unresolved)
Level 3: Full 3-member Council panel (24h)
    |
    v (unresolved)
Level 4: Executive Sponsor + Category Directors (48h)
    |
    v (unresolved)
Level 5: Executive Committee (72h - final decision)
```

### Special Rules

1. **Security Override**: Security-to-All loop has veto power on all other loops
2. **Compliance Override**: Compliance-to-All can block any action pending review
3. **Customer Escalation**: Any loop touching customer data requires Customer Advocate sign-off
4. **Cross-Category Conflicts**: Require Executive Sponsor involvement at Level 2

### Beads Integration for Conflicts

When inter-departmental conflict detected:

```
bd.exe add "Conflict: {source_dept} vs {target_dept} on {loop_name}"
bd.exe label add {bead_id} conflict:interdepartmental
bd.exe label add {bead_id} loop:{loop_id}
bd.exe label add {bead_id} arbiter:{council_member}
bd.exe label add {bead_id} tier:L{tier_level}
```

## Council Member Conflict Protocol

When council members disagree:

1. **L1-L2**: Tie-breaker has final say
2. **L3**: Escalate to Executive Sponsor if not already involved
3. **L4**: Requires executive committee (3+ Executive Sponsors)

## Council Persona Reference

| ID  | Persona               | Primary Domain | Loops as Primary                                                                  |
| --- | --------------------- | -------------- | --------------------------------------------------------------------------------- |
| 01  | Security Auditor      | Security       | Security-to-All                                                                   |
| 02  | Compliance Officer    | Compliance     | Compliance-to-All                                                                 |
| 03  | Risk Analyst          | Risk           | (Tie-breaker x2)                                                                  |
| 04  | Architecture Reviewer | Technical      | QA-to-Engineering                                                                 |
| 05  | Performance Engineer  | Performance    | (Secondary x3)                                                                    |
| 06  | DevOps Lead           | Operations     | Ops-to-All                                                                        |
| 07  | Product Owner         | Product        | Data-to-Product                                                                   |
| 08  | Legal Counsel         | Legal          | Legal-to-Sales                                                                    |
| 09  | Finance Controller    | Finance        | Finance-to-Revenue                                                                |
| 10  | HR Representative     | People         | (Not assigned - internal ops)                                                     |
| 11  | Customer Advocate     | Customer       | Customer-to-Product, Sales-to-Product, Support-to-Engineering, Marketing-to-Sales |
| 12  | Ethics Officer        | Ethics         | (Tie-breaker x1)                                                                  |
| 13  | Executive Sponsor     | Strategy       | (Tie-breaker x5)                                                                  |

## Implementation Notes

The `FeedbackLoop` dataclass should include:

```python
@dataclass
class LoopCouncil:
    primary: Persona
    secondary: Persona
    tie_breaker: Persona

    def get_approvers_for_tier(self, tier: RiskTier) -> List[Persona]:
        if tier == RiskTier.L0:
            return []
        elif tier == RiskTier.L1:
            return [self.primary]
        elif tier == RiskTier.L2:
            return [self.primary, self.secondary]
        elif tier in (RiskTier.L3, RiskTier.L4):
            return [self.primary, self.secondary, self.tie_breaker]
```
