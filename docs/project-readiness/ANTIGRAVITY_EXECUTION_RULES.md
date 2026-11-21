# HeartXAI 2.0 — Antigravity Execution Rules
**Document ID:** HX-PR-017  
**Version:** 1.0.0  
**Phase:** 12 — Final Pre-Implementation Audit, Architecture Consolidation & Master Development Roadmap  
**Author:** Principal Software Architect & QA Architect  
**Status:** Approved for Implementation Planning — Mandatory Invariants  
**Date:** November 2026  

---

## 1. Executive Summary

This document establishes the binding, non-negotiable operational rules governing Antigravity (and all contributing automated agents) during the implementation phases of HeartXAI 2.0. These rules are designed to ensure safety, architectural fidelity, test-driven validation, and complete transparency.

---

## 2. The 15 Mandatory Execution Rules

```
+---------------------------------------------------------------------------------------------------------+
|                                    ANTIGRAVITY EXECUTION RULES                                          |
+----+------------------------------------+---------------------------------------------------------------+
| No | Rule Name                          | Concrete Operational Invariant                                |
+----+------------------------------------+---------------------------------------------------------------+
| 01 | **Atomic Milestone Execution**     | Work on exactly one approved milestone at a time. Never blend |
|    |                                    | tasks from future milestones into the active turn.            |
+----+------------------------------------+---------------------------------------------------------------+
| 02 | **Inspect Before Modification**    | Always read and inspect existing files before editing them.   |
|    |                                    | Never assume file contents or structure from memory.          |
+----+------------------------------------+---------------------------------------------------------------+
| 03 | **Preserve Working Functionality** | Existing tests, endpoints, and components must continue to    |
|    |                                    | pass after any modification. Regressions are blockers.        |
+----+------------------------------------+---------------------------------------------------------------+
| 04 | **Avoid Unnecessary Rewrites**     | Extend and refactor existing modules rather than throwing     |
|    |                                    | away working code and starting over.                          |
+----+------------------------------------+---------------------------------------------------------------+
| 05 | **Bounded Incremental Output**     | Avoid generating massive unverified codebases in a single     |
|    |                                    | turn. Commit working code incrementally.                      |
+----+------------------------------------+---------------------------------------------------------------+
| 06 | **Component & Service Reuse**      | Maximize reuse of established UI primitives, schemas, and     |
|    |                                    | database services. Do not duplicate business logic.           |
+----+------------------------------------+---------------------------------------------------------------+
| 07 | **Strict Architectural Fidelity**  | Follow approved ADRs (001–012), data dictionaries, and API    |
|    |                                    | specifications without unauthorized deviation.                |
+----+------------------------------------+---------------------------------------------------------------+
| 08 | **Dependency Pre-Validation**      | Never add a third-party package without verifying its license,|
|    |                                    | CVE history, maintenance status, and architectural necessity. |
+----+------------------------------------+---------------------------------------------------------------+
| 09 | **Test-Driven Implementation**     | Write automated unit and integration tests alongside every    |
|    |                                    | implementation task. Code without tests is not done.          |
+----+------------------------------------+---------------------------------------------------------------+
| 10 | **Execution Evidence Required**    | Execute the automated test suite and inspect actual command   |
|    |                                    | exit codes before reporting task completion.                  |
+----+------------------------------------+---------------------------------------------------------------+
| 11 | **Honest Error & Gap Reporting**   | Report actual exceptions, performance bottlenecks, and        |
|    |                                    | limitations immediately. Never obscure failures.              |
+----+------------------------------------+---------------------------------------------------------------+
| 12 | **Prohibition of Fabricated Passes**| Never claim a test has passed or code is verified without    |
|    |                                    | running the exact command and verifying stdout/stderr.        |
+----+------------------------------------+---------------------------------------------------------------+
| 13 | **Prohibition of Fabricated Proof**| Never fabricate screenshots, mock logs, synthetic commits, or  |
|    |                                    | fictitious deployment results.                                |
+----+------------------------------------+---------------------------------------------------------------+
| 14 | **Immediate Escalation on Conflict**| If an unresolvable contradiction or architectural conflict is |
|    |                                    | encountered, stop immediately and escalate to the user.       |
+----+------------------------------------+---------------------------------------------------------------+
| 15 | **Mandatory Approval Pause**       | At the end of each milestone, present completed deliverables, |
|    |                                    | test output, and pause. Wait for explicit user approval.      |
+----+------------------------------------+---------------------------------------------------------------+
```

---

## 3. Protocol for Handling Blockers and Escalations

If an unexpected condition arises during implementation (such as package version conflict, test failure, or database dialect mismatch):
1. **Halt execution:** Do not attempt blind workarounds or bypass safety checks.
2. **Isolate root cause:** Perform targeted diagnostics using sandboxed commands.
3. **Formulate options:** Propose 2–3 viable engineering solutions with tradeoffs.
4. **Present finding:** Document the issue clearly in the conversation turn and wait for stakeholder guidance.
