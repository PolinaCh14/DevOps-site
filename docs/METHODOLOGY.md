# Agent-Driven Development Methodology

## Status

Draft

This document defines the current working methodology for agent-driven development used in the master's research.

The methodology may be refined during the research based on results from completed development cycles.

---

## 1. Core Workflow

The development process follows this sequence:

Need
→ Requirements
→ Constraints
→ Acceptance Criteria
→ Knowledge / Contract Cards
→ Specification Card
→ Task Card
→ Implementation
→ Independent Review
→ Validation Evidence
→ Acceptance
→ Handoff

No implementation should begin before the requirements, constraints, and acceptance criteria for the selected change are defined.

---

## 2. Human Responsibility

The human researcher remains responsible for:

- selecting development directions;
- defining the initial need and expected outcome;
- reviewing and approving requirements;
- reviewing and approving cards;
- approving task scope before implementation;
- making the final accept/reject decision.

AI agents may prepare drafts and analysis, but they must not silently redefine the intended requirement or expand the approved scope.

---

## 3. Builder Role

The Builder is responsible for analysis and preparation before implementation.

The Builder may:

- inspect the repository;
- analyze the current system state;
- identify dependencies and affected components;
- create draft knowledge / contract cards;
- create draft specification cards;
- identify ambiguities, risks, and open questions;
- prepare a bounded task card;
- define allowed modification scope;
- define required validation and tests.

The Builder must not:

- modify application code;
- implement the requested change;
- silently expand the scope;
- invent requirements that are not supported by the approved change request.

If repository evidence conflicts with the requested change, the Builder must report the conflict instead of making an assumption.

---

## 4. Implementer Role

The Implementer receives only approved inputs required for implementation.

Typical inputs include:

- approved change request;
- approved knowledge / contract cards;
- approved specification card;
- approved task card.

The Implementer is responsible for:

- implementing only the approved task;
- modifying only allowed components unless a blocking dependency is discovered;
- adding or updating required automated tests;
- documenting actual files changed;
- documenting commands used;
- reporting test results;
- reporting unfinished or blocked work.

The Implementer must not silently change requirements or expand the approved task.

---

## 5. Reviewer Role

The Reviewer performs an independent assessment of the implementation.

The Reviewer should receive:

- approved requirements;
- approved cards;
- approved task card;
- implementation diff;
- test results;
- relevant verification evidence.

The Reviewer checks:

- compliance with requirements;
- compliance with acceptance criteria;
- scope violations;
- unintended changes;
- test adequacy;
- consistency with existing contracts;
- missing evidence;
- unresolved risks.

The Reviewer should not rely on undocumented assumptions from the Implementer session.

---

## 6. Structured Cards

The methodology uses several card types.

### Knowledge / Contract Cards

Describe the current system state relevant to a development task.

They may include:

- domain entities;
- interfaces;
- dependencies;
- current behavior;
- invariants;
- known limitations;
- constraints.

These cards describe what is currently true in the system.

### Specification Cards

Describe the required future behavior of a selected change.

They may include:

- functional requirements;
- technical requirements;
- interface expectations;
- constraints;
- failure cases;
- acceptance criteria.

### Task Cards

Describe one bounded implementation task.

A task card should include:

- task objective;
- allowed scope;
- allowed files or components;
- prohibited changes;
- acceptance criteria;
- required tests;
- expected outputs.

### Validation Records

Record evidence that a completed implementation satisfies the approved requirements.

They may include:

- code version / commit SHA;
- test commands;
- test results;
- relevant inputs;
- parameters;
- observed results;
- requirement-to-evidence mapping.

### Handoff Records

Summarize the accepted system state after a completed development cycle.

They allow the next task or agent session to continue without relying on previous chat history.

---

## 7. Human Approval Gates

Human approval is required before major stage transitions.

Recommended gates:

1. approve the selected change and requirements;
2. approve knowledge / contract cards;
3. approve specification card;
4. approve task card;
5. review Reviewer findings;
6. accept or reject the completed change.

---

## 8. Scope Control

Each development cycle should represent one clearly bounded change.

Unrelated refactoring, architectural redesign, or feature expansion is not permitted unless explicitly approved.

If additional work is discovered during implementation, it should be:

- reported;
- documented;
- separated into a future task where appropriate.

---

## 9. Traceability

Each significant change should support traceability through:

Requirement
→ Specification
→ Task
→ Code Change
→ Test
→ Evidence
→ Reviewer Decision
→ Acceptance

Each acceptance criterion should have corresponding verification evidence where reasonably possible.

---

## 10. Reproducibility and Evidence

Each development cycle should preserve enough information to reproduce and verify the result.

This may include:

- repository version;
- cards;
- task definition;
- implementation diff;
- test data or fixtures where required;
- test commands;
- test results;
- reviewer findings;
- validation record;
- final decision.

The process should not depend only on conversational history.

---

## 11. Research Metrics

The following metrics may be collected for each development cycle:

- total cycle time;
- implementation time;
- number of agent iterations;
- number of Reviewer findings;
- number of rework cycles;
- first-pass acceptance;
- acceptance criteria passed / total;
- tests passed / total;
- scope violations;
- human interventions;
- requirement-to-evidence coverage.

The final set of metrics may be refined during the research.

---

## 12. Planned Development Cycles

The methodology will be evaluated through several development cycles of different complexity.

Each cycle should follow the same general process:

1. select a change;
2. define requirements and acceptance criteria;
3. prepare structured cards;
4. prepare bounded task;
5. implement;
6. independently review;
7. validate;
8. accept or reject;
9. create handoff;
10. record metrics and observations.

---

## 13. Current Methodology Status

This methodology is intentionally considered a working research methodology rather than a final fixed process.

Changes to the methodology should be documented and justified based on observations from completed development cycles.