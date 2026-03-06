# Council Weekly Review & Escalation Ladder Design

## Overview

The Council Review system creates a continuous improvement loop by:

1. Collecting feedback and telemetry from all 24 departments
2. Aggregating into weekly review packages
3. Council analyzes patterns and proposes improvements
4. Changes escalate through a ladder based on impact
5. Approved changes feed back into department configurations

---

## PART 1: DATA COLLECTION (Per Department)

### Telemetry Metrics (Automatic - [D])

| Metric              | Type      | Frequency      | Source                 |
| ------------------- | --------- | -------------- | ---------------------- |
| Latency (ms)        | Float     | Per execution  | LoopTelemetryCollector |
| Throughput          | Count/min | Rolling 1-hour | Aggregated             |
| Error Rate          | Ratio     | Per execution  | Pass/Fail              |
| Block Rate          | Ratio     | Per execution  | Nomotic checker        |
| Escalation Rate     | Ratio     | Per execution  | When L2+ triggered     |
| Council Involvement | Ratio     | Per execution  | When council votes     |
| Success Rate        | Ratio     | Per execution  | Completed successfully |
| Nomotic Compliance  | Ratio     | Per execution  | Pre+Post check pass    |

### KPI/Counter-KPI Snapshots (Per Department)

```
For each department:
  Primary KPIs: [list of primary metrics with current values]
  Counter KPIs: [list of counter metrics with current values]
  Balance Score: 0.0-1.0 (healthy balance between primary/counter)
  Gaming Alerts: [any detected gaming patterns]
  Trend: improving | stable | degrading
```

### Feedback Loop Data (From TRUE FEEDBACK LOOP)

```
FeedbackResponse:
  - accepted: bool
  - processing_status: completed | partial | deferred | rejected
  - actual_effort vs estimated_effort
  - quality_score: 0.0-1.0
  - issues_found: [list]
  - suggestions: [list]
  - blockers_encountered: [list]
  - adjustment_requests: [list]

SourceAdjustment:
  - patterns_detected: [list of recurring patterns]
  - priority_adjustments: {kpi: delta}
  - process_changes: [suggested changes]
  - threshold_changes: {metric: new_value}
```

---

## PART 2: WEEKLY AGGREGATION

### WeeklyDepartmentReport (Data Structure)

```python
@dataclass
class WeeklyDepartmentReport:
    """Weekly report for a single department."""
    department: GuardDepartment
    week_start: datetime
    week_end: datetime

    # Telemetry Aggregates
    total_executions: int
    avg_latency_ms: float
    p95_latency_ms: float
    error_count: int
    block_count: int
    escalation_count: int
    council_involvements: int

    # KPI Summary
    kpi_balance_score: float  # 0.0-1.0
    gaming_alerts: List[GamingAlert]
    kpi_trend: str  # improving, stable, degrading

    # Feedback Summary
    feedback_received: int
    avg_quality_score: float
    common_issues: List[str]  # Top 5 recurring issues
    common_blockers: List[str]  # Top 3 blockers
    suggested_changes: List[str]

    # Comparison
    vs_previous_week: Dict[str, float]  # Metric deltas
    vs_30_day_avg: Dict[str, float]  # Variance from baseline
```

### WeeklySystemReport (Aggregated)

```python
@dataclass
class WeeklySystemReport:
    """Weekly report across all departments for council review."""
    report_id: str
    week_start: datetime
    week_end: datetime

    # Department Reports (24)
    department_reports: Dict[GuardDepartment, WeeklyDepartmentReport]

    # Category Summaries
    category_summaries: Dict[GuardDepartmentCategory, CategorySummary]

    # Cross-Department Analysis
    inter_department_friction: List[FrictionPoint]
    bottleneck_departments: List[GuardDepartment]
    high_performers: List[GuardDepartment]

    # Nomotic Rule Analysis
    most_violated_rules: List[Tuple[NomoticRuleId, int]]
    compliance_by_department: Dict[GuardDepartment, float]

    # Improvement Candidates
    proposed_changes: List[ProposedChange]

    # Council Assignment
    assigned_reviewers: List[CouncilPersona]
    due_date: datetime
```

---

## PART 3: COUNCIL REVIEW PROCESS

### 3.1 Review Cadence

| Review Type            | Frequency     | Attendees               | Focus                 |
| ---------------------- | ------------- | ----------------------- | --------------------- |
| **Weekly Operational** | Every Monday  | 3 personas (rotating)   | Tactical improvements |
| **Monthly Strategic**  | First Monday  | All 13 personas         | Strategic changes     |
| **Quarterly Planning** | Every quarter | All + Executive Sponsor | Roadmap alignment     |

### 3.2 Rotating Council Assignment

Each week, 3 council personas are assigned based on:

1. **Primary Owner**: Owns the category with most issues
2. **Secondary Owner**: Cross-functional expertise needed
3. **Tiebreaker**: Neutral party for escalated decisions

```python
def get_weekly_reviewers(report: WeeklySystemReport) -> List[CouncilPersona]:
    """Assign 3 reviewers for the week."""

    # Find category with most issues
    worst_category = max(
        report.category_summaries.items(),
        key=lambda x: x[1].issue_count
    )[0]

    # Map category to primary persona
    primary = CATEGORY_OWNERS[worst_category]

    # Secondary based on issue type
    if report.has_security_issues:
        secondary = CouncilPersona.SECURITY_AUDITOR
    elif report.has_compliance_issues:
        secondary = CouncilPersona.COMPLIANCE_OFFICER
    elif report.has_performance_issues:
        secondary = CouncilPersona.PERFORMANCE_ENGINEER
    else:
        secondary = CouncilPersona.ARCHITECTURE_REVIEWER

    # Tiebreaker rotates
    tiebreaker = ROTATION_SCHEDULE[report.week_number % len(ROTATION_SCHEDULE)]

    return [primary, secondary, tiebreaker]
```

### 3.3 Review Outputs

The council produces:

1. **Approved Changes**: Ready to implement
2. **Escalated Changes**: Needs higher approval
3. **Deferred Changes**: Need more data
4. **Rejected Changes**: Not recommended

---

## PART 4: ESCALATION LADDER

### Change Impact Levels

| Level  | Name     | Description                | Examples                                |
| ------ | -------- | -------------------------- | --------------------------------------- |
| **L0** | Trivial  | No approval needed         | Threshold tuning <5%                    |
| **L1** | Minor    | Single persona approval    | Add logging, adjust weights             |
| **L2** | Standard | 2 persona approval         | New validation rule, process step       |
| **L3** | Major    | 3 persona + category owner | New department workflow, KPI change     |
| **L4** | Critical | Full council + executive   | Cross-category change, new nomotic rule |

### Escalation Rules

```python
@dataclass
class ProposedChange:
    """A proposed improvement from feedback analysis."""
    change_id: str
    source_department: GuardDepartment
    change_type: ChangeType  # threshold, process, workflow, rule, architecture
    description: str
    impact_score: float  # 0.0-1.0 based on blast radius
    risk_score: float  # 0.0-1.0 based on reversibility
    evidence: List[str]  # Supporting data

    @property
    def escalation_level(self) -> int:
        """Compute required escalation level."""
        # Combine impact and risk
        combined = (self.impact_score + self.risk_score) / 2

        if combined < 0.1:
            return 0  # L0: Trivial
        elif combined < 0.3:
            return 1  # L1: Minor
        elif combined < 0.5:
            return 2  # L2: Standard
        elif combined < 0.7:
            return 3  # L3: Major
        else:
            return 4  # L4: Critical
```

### Approval Requirements by Level

```python
APPROVAL_REQUIREMENTS = {
    0: {
        "approvers_needed": 0,
        "auto_approve": True,
        "timeout_hours": 0,
        "timeout_action": "apply",
    },
    1: {
        "approvers_needed": 1,
        "auto_approve": False,
        "timeout_hours": 24,
        "timeout_action": "escalate",
    },
    2: {
        "approvers_needed": 2,
        "auto_approve": False,
        "timeout_hours": 48,
        "timeout_action": "escalate",
    },
    3: {
        "approvers_needed": 3,
        "auto_approve": False,
        "timeout_hours": 72,
        "timeout_action": "defer",
        "requires_category_owner": True,
    },
    4: {
        "approvers_needed": 7,  # Majority of 13
        "auto_approve": False,
        "timeout_hours": 168,  # 1 week
        "timeout_action": "reject",
        "requires_executive": True,
    },
}
```

---

## PART 5: CHANGE TYPES AND IMPACTS

### 5.1 Threshold Changes (Usually L0-L1)

| Change                        | Impact Score | Risk Score | Level |
| ----------------------------- | ------------ | ---------- | ----- |
| KPI warning threshold +/- 5%  | 0.05         | 0.02       | L0    |
| KPI critical threshold +/- 5% | 0.08         | 0.05       | L0    |
| Latency SLA adjustment        | 0.15         | 0.10       | L1    |
| Error rate tolerance          | 0.20         | 0.15       | L1    |

### 5.2 Process Changes (Usually L1-L2)

| Change                  | Impact Score | Risk Score | Level |
| ----------------------- | ------------ | ---------- | ----- |
| Add validation step     | 0.25         | 0.10       | L1    |
| Modify handoff sequence | 0.35         | 0.20       | L2    |
| Add pre-check rule      | 0.40         | 0.25       | L2    |
| Change approval routing | 0.45         | 0.30       | L2    |

### 5.3 Workflow Changes (Usually L2-L3)

| Change                    | Impact Score | Risk Score | Level |
| ------------------------- | ------------ | ---------- | ----- |
| New feedback loop         | 0.50         | 0.30       | L2    |
| Modify department lanes   | 0.55         | 0.35       | L3    |
| Change escalation path    | 0.60         | 0.40       | L3    |
| Add new department action | 0.65         | 0.45       | L3    |

### 5.4 Rule/Architecture Changes (Usually L3-L4)

| Change                        | Impact Score | Risk Score | Level |
| ----------------------------- | ------------ | ---------- | ----- |
| New nomotic rule              | 0.70         | 0.50       | L3    |
| Modify existing rule severity | 0.75         | 0.55       | L3    |
| New guard lane                | 0.80         | 0.60       | L4    |
| Cross-category process change | 0.85         | 0.70       | L4    |
| New department creation       | 0.95         | 0.80       | L4    |

---

## PART 6: FEEDBACK-TO-CHANGE PIPELINE

### 6.1 Pattern Detection (Automatic)

```python
class ImprovementDetector:
    """Detects improvement opportunities from feedback patterns."""

    def analyze_feedback_patterns(
        self,
        feedbacks: List[FeedbackResponse],
        window_days: int = 7
    ) -> List[ProposedChange]:
        """Analyze feedback to propose changes."""

        proposals = []

        # Pattern 1: Consistent effort underestimation
        effort_ratios = [f.actual_effort / f.estimated_effort
                        for f in feedbacks if f.estimated_effort]
        if avg(effort_ratios) > 1.3:  # 30% underestimation
            proposals.append(ProposedChange(
                change_type=ChangeType.THRESHOLD,
                description="Increase effort estimation buffer by 25%",
                impact_score=0.15,
                risk_score=0.05,
            ))

        # Pattern 2: Recurring blockers
        blocker_counts = Counter([b for f in feedbacks
                                  for b in f.blockers_encountered])
        for blocker, count in blocker_counts.most_common(3):
            if count > len(feedbacks) * 0.2:  # >20% of executions
                proposals.append(ProposedChange(
                    change_type=ChangeType.PROCESS,
                    description=f"Add pre-check for blocker: {blocker}",
                    impact_score=0.30,
                    risk_score=0.15,
                ))

        # Pattern 3: Quality score degradation
        recent_quality = avg([f.quality_score for f in feedbacks[-10:]])
        baseline_quality = avg([f.quality_score for f in feedbacks[:10]])
        if recent_quality < baseline_quality * 0.9:  # 10% drop
            proposals.append(ProposedChange(
                change_type=ChangeType.WORKFLOW,
                description="Add quality gate before handoff",
                impact_score=0.45,
                risk_score=0.25,
            ))

        return proposals
```

### 6.2 Council Review Workflow

```
Week N: Data Collection
  |
  v
Monday Week N+1: Report Generation
  |
  v
Tuesday: Council Reviews (async)
  |
  v
Wednesday: Voting Closes
  |
  v
Thursday: L0-L1 Changes Applied
  |
  v
Friday: L2+ Changes Queued for Implementation
  |
  v
Week N+2: Changes Go Live
```

### 6.3 Change Application

```python
def apply_approved_change(change: ProposedChange, approvals: List[Approval]):
    """Apply an approved change to the system."""

    if change.change_type == ChangeType.THRESHOLD:
        # Update configuration
        update_department_config(
            change.source_department,
            change.target_field,
            change.new_value
        )

    elif change.change_type == ChangeType.PROCESS:
        # Add/modify process step
        update_feedback_loop(
            change.source_department,
            change.process_modification
        )

    elif change.change_type == ChangeType.WORKFLOW:
        # Modify workflow
        update_orchestrator_config(change.workflow_changes)

    elif change.change_type == ChangeType.RULE:
        # Add/modify nomotic rule
        update_nomotic_pack(change.rule_changes)

    # Record change for audit
    log_change_application(change, approvals)

    # Notify affected personas
    notify_stakeholders(change)
```

---

## PART 7: MEMORY MCP PERSISTENCE

### Namespace Structure

```
guard:council:weekly:{week_id}        # Weekly report
guard:council:changes:{change_id}     # Proposed changes
guard:council:approvals:{change_id}   # Approval records
guard:council:applied:{change_id}     # Applied changes
guard:telemetry:dept:{dept_id}:{date} # Daily telemetry
guard:feedback:loop:{loop_id}:{date}  # Daily feedback
guard:kpi:dept:{dept_id}:{date}       # Daily KPI snapshots
```

### Retention Policy

| Data Type        | Retention | Purpose              |
| ---------------- | --------- | -------------------- |
| Raw telemetry    | 30 days   | Operational analysis |
| Daily aggregates | 90 days   | Trend analysis       |
| Weekly reports   | 1 year    | Strategic planning   |
| Applied changes  | Forever   | Audit trail          |
| Rejected changes | 90 days   | Pattern detection    |

---

## PART 8: EXAMPLE FLOW

### Scenario: Engineering->QA Loop Performance Degradation

**Week 1: Data Collection**

```
Feedback patterns detected:
  - Avg quality_score dropped from 0.88 to 0.72
  - Blocker "missing_test_data" in 35% of executions
  - Effort variance increased 40%
```

**Week 2: Report Generated**

```
WeeklyDepartmentReport for PRODUCT_ENGINEERING:
  - error_rate: 0.15 (up from 0.08)
  - avg_quality_score: 0.72 (down from 0.88)
  - common_blockers: ["missing_test_data", "unclear_requirements"]
  - kpi_trend: "degrading"

Proposed Changes:
  1. Add test data validation pre-check (L2)
  2. Increase estimation buffer 25% (L1)
  3. Add requirement clarity checkpoint (L2)
```

**Council Review (Tuesday)**

```
Reviewers: ARCHITECTURE_REVIEWER, PRODUCT_OWNER, PERFORMANCE_ENGINEER

Votes:
  Change 1 (test data pre-check): 3 APPROVE -> APPROVED
  Change 2 (estimation buffer): 3 APPROVE -> APPROVED
  Change 3 (requirement checkpoint): 2 APPROVE, 1 DEFER -> DEFERRED
```

**Thursday: Changes Applied**

```
- L1 change (estimation buffer) applied immediately
- L2 change (test data pre-check) queued for Friday deploy
- Deferred change scheduled for next week review with more data
```

**Week 3: Validation**

```
Metrics after change:
  - quality_score: 0.81 (improving)
  - blocker "missing_test_data": 8% (down from 35%)

Feedback loop successfully tightened.
```

---

## PART 9: DATA STRUCTURES

### Core Types for Implementation

```python
class ChangeType(str, Enum):
    THRESHOLD = "threshold"
    PROCESS = "process"
    WORKFLOW = "workflow"
    RULE = "rule"
    ARCHITECTURE = "architecture"

@dataclass
class Approval:
    approver: CouncilPersona
    vote: str  # approve, reject, defer
    timestamp: datetime
    comments: str = ""

@dataclass
class AppliedChange:
    change: ProposedChange
    approvals: List[Approval]
    applied_at: datetime
    applied_by: str
    rollback_available: bool = True
    rollback_deadline: Optional[datetime] = None

@dataclass
class CategorySummary:
    category: GuardDepartmentCategory
    departments: List[GuardDepartment]
    total_executions: int
    avg_success_rate: float
    issue_count: int
    top_issues: List[str]

@dataclass
class FrictionPoint:
    source_dept: GuardDepartment
    target_dept: GuardDepartment
    friction_type: str  # handoff_delay, rejection_rate, quality_mismatch
    severity: float
    suggested_fix: str
```

---

## Summary

This design creates a **closed-loop continuous improvement system**:

1. **COLLECT**: Telemetry + Feedback + KPIs from 24 departments
2. **AGGREGATE**: Weekly reports with pattern detection
3. **REVIEW**: Council analyzes, proposes changes
4. **ESCALATE**: Changes ladder based on impact (L0-L4)
5. **APPLY**: Approved changes modify department configs
6. **VALIDATE**: Next week's data shows improvement

The key insight: **The TRUE FEEDBACK LOOP we built at the department level now has a meta-loop at the council level**, creating recursive improvement.

```
Department Loop (hourly):
  Source -> Target -> Feedback -> Source Adjustment

Council Loop (weekly):
  All Depts -> Weekly Report -> Council Review -> System Changes

The council loop TUNES the department loops.
```
