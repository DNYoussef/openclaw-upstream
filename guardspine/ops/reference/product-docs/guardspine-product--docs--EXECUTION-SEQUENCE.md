# GuardSpine Product Suite - Execution Sequence

## Task Summary (Updated with Templates)

| #   | Task                              | Template Coverage              | Effort   | Blockers  |
| --- | --------------------------------- | ------------------------------ | -------- | --------- |
| 8   | Dept-to-Guard-Lane Mapping        | 100% (namespace_schema.py)     | 1 day    | None      |
| 5   | Nomotic Policy Pack Loader        | 100% (nomotic-governance.yaml) | 1 day    | None      |
| 15  | Council Persona-to-Dept Mapping   | 50% (COUNCIL_PACK refs)        | 3-4 days | None      |
| 2   | Counter-KPIs / Secondary Metrics  | 80% (telemetry_schema.py)      | 2 days   | None      |
| 7   | Inter-Department Handoff Routing  | 95% (beads_bridge.py)          | 2-3 days | #8        |
| 9   | Beads Task Creation from Cycles   | 90% (beads_bridge.py)          | 1-2 days | #8        |
| 10  | Nomotic Rule Firing Tracker       | 70% (event_parser.py)          | 3-4 days | #8, #5    |
| 12  | Escalation Path Matrix            | 85% (config.yaml)              | 2-3 days | #8, #15   |
| 13  | Artifact Lineage Tracking         | 60% (namespace_schema.py)      | 3-4 days | #8        |
| 3   | 6 Inter-Department Feedback Loops | 70% (loop15_reflector.py)      | 3 days   | #7        |
| 11  | KPI Aggregation Dashboard         | 80% (telemetry_schema.py)      | 2-3 days | #2        |
| 16  | Nomotic-Beads Integration         | 60% (hook patterns)            | 2-3 days | #5, #9    |
| 14  | System-Wide Health Aggregation    | 70% (loops)                    | 2-3 days | #7, #11   |
| 17  | Full System Audit                 | 7-Analyzer Suite               | 1 day    | All above |
| 18  | Test Suite with Coverage          | pytest + cov                   | 1 day    | #17       |
| 19  | Dry Run Simulation                | End-to-end mock                | 1 day    | #18       |

## Optimal Execution Sequence

### Wave 1: Foundation (Parallel, No Blockers)

Start immediately - these have no dependencies:

1. **#8 Dept-to-Guard-Lane Mapping** (1 day)
   - Copy: `D:\2026-AI-EXOSKELETON\.claude\integrations\guardspine\adapters\namespace_schema.py`
   - Extend: Add department-specific action mappings
   - Critical: Unblocks 5 other tasks

2. **#5 Nomotic Policy Pack Loader** (1 day)
   - Copy: `D:\2026-AI-EXOSKELETON\.claude\integrations\guardspine\rubrics\nomotic-governance.yaml`
   - Add: Loader class with validation
   - Note: Requires Chris Hood approval

3. **#15 Council Persona-to-Dept Mapping** (3-4 days)
   - Reference: COUNCIL_PACK_v1.1.md
   - Build: PersonaDepartmentMapper class
   - Link: 13 personas to 24 departments

4. **#2 Counter-KPIs / Secondary Metrics** (2 days)
   - Copy: telemetry_schema.py
   - Add: counter_metrics field per department

**Wave 1 Duration: 4 days (parallel)**

### Wave 2: Core Integration (After #8 completes)

5. **#7 Inter-Department Handoff Routing** (2-3 days)
   - Copy: beads_bridge.py
   - Add: handoff_to_department() method
   - Unblocks: #3, #14

6. **#9 Beads Task Creation from Cycles** (1-2 days)
   - Extend: beads_bridge.py
   - Add: create_bead_from_cycle(), sync_department_beads()
   - Unblocks: #16

7. **#10 Nomotic Rule Firing Tracker** (3-4 days)
   - Requires: #8, #5
   - Create: NomoticTracker class
   - Log: WHO/WHEN/PROJECT/WHY tags

8. **#12 Escalation Path Matrix** (2-3 days)
   - Requires: #8, #15
   - Create: EscalationMatrix class
   - Map: (department, action, risk_tier) -> path

9. **#13 Artifact Lineage Tracking** (3-4 days)
   - Requires: #8
   - Use: GraphEdgeType relationships
   - Build: trace_artifact_path(), build_lineage_graph()

**Wave 2 Duration: 4-5 days (some parallel)**

### Wave 3: Advanced Features

10. **#3 6 Inter-Department Feedback Loops** (3 days)
    - Requires: #7
    - Implement: Product-to-Engineering, Sales-to-Product, etc.

11. **#11 KPI Aggregation Dashboard** (2-3 days)
    - Requires: #2
    - Aggregate: Department metrics to dashboard

12. **#16 Nomotic-Beads Integration** (2-3 days)
    - Requires: #5, #9
    - Trigger: Bead blocking on nomotic violations

**Wave 3 Duration: 3 days (parallel)**

### Wave 4: Health & Rollup

13. **#14 System-Wide Health Aggregation** (2-3 days)
    - Requires: #7, #11
    - Output: Red/yellow/green system status

**Wave 4 Duration: 2-3 days**

### Wave 5: Quality Validation

14. **#17 Full System Audit** (1 day)
    - Run: claude-dev quality analyze --profile strict
    - Target: Sigma >= 4.0, Theater < 20%, 0 critical
    - Output: SARIF report

15. **#18 Test Suite with Coverage** (1 day)
    - Run: pytest with --cov
    - Target: >= 80% coverage, 0 failures

16. **#19 Dry Run Simulation** (1 day)
    - Execute: Full flow without side effects
    - Output: Timing, bottlenecks, gaps

**Wave 5 Duration: 3 days (sequential)**

## Total Timeline

| Wave      | Duration     | Tasks                 |
| --------- | ------------ | --------------------- |
| Wave 1    | 4 days       | #8, #5, #15, #2       |
| Wave 2    | 5 days       | #7, #9, #10, #12, #13 |
| Wave 3    | 3 days       | #3, #11, #16          |
| Wave 4    | 3 days       | #14                   |
| Wave 5    | 3 days       | #17, #18, #19         |
| **Total** | **~18 days** | 16 tasks              |

## Template Source Files (Copy From)

| File                       | Location                                    | Reuse % |
| -------------------------- | ------------------------------------------- | ------- |
| namespace_schema.py        | `.claude\integrations\guardspine\adapters\` | 100%    |
| nomotic-governance.yaml    | `.claude\integrations\guardspine\rubrics\`  | 100%    |
| beads_bridge.py            | `.claude\integrations\guardspine\adapters\` | 95%     |
| config.yaml                | `.claude\hooks\guardspine\`                 | 90%     |
| telemetry_schema.py        | `.claude\cognitive_architecture\storage\`   | 80%     |
| event_parser.py            | `.claude\integrations\guardspine\adapters\` | 80%     |
| loop15_reflector.py        | `.claude\cognitive_architecture\loops\`     | 70%     |
| loop2_quality_collector.py | `.claude\cognitive_architecture\loops\`     | 70%     |

Base path: `D:\2026-AI-EXOSKELETON\`

## Audit Checklist (#17)

The 7-Analyzer Suite will check:

1. **Connascence** (9 types): CoN, CoT, CoM, CoP, CoA, CoE, CoT2, CoV, CoI
2. **NASA Safety**: Power of 10 rules (>95% compliance)
3. **MECE**: Code duplication (>80% uniqueness)
4. **Clarity Linter**: Cognitive load metrics
5. **Six Sigma**: DPMO < 6210, Sigma >= 4.0
6. **Theater Detection**: < 20% fake quality indicators
7. **Safety Violations**: 0 god objects, 0 parameter bombs

## Completed Tasks (Reference)

- [x] #1 Action-Category-to-Approver Routing
- [x] #4 Update Beads Tasks to Match 5-Lane Architecture
- [x] #6 Create GuardSpine Sales Product Package
