# CHANGE-002: Work Request Lifecycle Validation and Access Control

## 1. Status

Draft

This change has not yet been approved for implementation.

No application code should be modified based on this document alone.

---

## 2. Purpose

Improve the existing work request workflow by making status transitions explicit, validated, permission-aware, and testable.

The goal is to preserve the current collaboration workflow while reducing ambiguous behavior, hard-coded status handling, and unauthorized or invalid state changes.

---

## 3. Current State

The current system contains the following work request statuses:

- `1` — `очікує`
- `2` — `схвалено`
- `3` — `відхилено`
- `4` — `на розгляді`

A `WorkRequest` is linked to:

- a `WorkRequestStatus`;
- a `Freelancer`;
- a `Project`.

The current implementation supports:

- creating a work request for a project;
- preventing duplicate requests from the same freelancer for the same project;
- listing work requests for freelancers;
- listing work requests for employers;
- filtering work requests by status;
- changing the status of a work request;
- notifying the employer when a new request is created;
- notifying the freelancer when a work request is updated.

Current behavior also includes a special rule:

- when a work request is assigned status ID `2`,
  the selected request is approved and other requests for the same project are assigned status ID `3`.

---

## 4. Current Limitations

The current implementation has several lifecycle and validation limitations.

### 4.1 Hard-coded status IDs

Business behavior currently depends directly on numeric status IDs such as:

- `2` for approval;
- `3` for rejection.

The lifecycle meaning is therefore coupled to database IDs.

### 4.2 No explicit lifecycle rules

The system does not currently define which transitions between statuses are valid.

For example, there is no explicit rule preventing arbitrary transitions such as:

- `відхилено` → `схвалено`;
- `схвалено` → `очікує`;
- `схвалено` → `на розгляді`.

Whether such transitions should be permitted is not currently defined.

### 4.3 Initial status is implicit

New work requests use the first available `WorkRequestStatus` as their initial status.

The initial lifecycle state is therefore dependent on database ordering rather than an explicit business rule.

### 4.4 Status change authorization is not explicit

The current status update flow retrieves a project by project ID, but the change request does not explicitly verify in the same flow that the authenticated user owns that project.

The required authorization rule should be explicit and testable.

### 4.5 Notifications are update-based rather than transition-based

The current notification logic creates a freelancer notification whenever an existing `WorkRequest` is saved.

The current implementation does not explicitly verify that the status value actually changed before generating the status-change notification.

### 4.6 Acceptance behavior is implicit

When one work request is approved, all other requests for the same project are currently rejected automatically.

This behavior exists in implementation but is not explicitly documented as a business contract.

---

## 5. Need

Employers and freelancers need predictable and consistent handling of collaboration requests.

A work request lifecycle should clearly define:

- the initial request state;
- allowed status transitions;
- who is allowed to perform each transition;
- what happens to competing requests when one request is approved;
- when notifications are generated.

The workflow should not depend on undocumented numeric status IDs or implicit database ordering.

---

## 6. Desired Result

Formalize the existing work request lifecycle without redesigning the overall project or collaboration model.

The improved workflow should:

- define an explicit initial status;
- define allowed transitions between existing statuses;
- reject invalid transitions;
- enforce authorization for employer-side status changes;
- preserve and explicitly define the existing "approve one, reject others" behavior if approved as a business rule;
- avoid direct dependence on unexplained numeric status IDs where reasonably possible;
- generate notifications only for actual relevant status changes;
- preserve current work request creation and listing behavior;
- provide automated tests for lifecycle and authorization rules.

---

## 7. Functional Requirements

### FR-01: Explicit initial status

A newly created work request must receive an explicitly defined initial status.

The initial status must not depend only on `WorkRequestStatus.objects.first()` or database row ordering.

The expected initial status should be confirmed during specification.

### FR-02: Explicit lifecycle transitions

The allowed transitions between the existing statuses must be defined before implementation.

The lifecycle must use only the currently existing statuses unless a separate approved change introduces new ones:

- `очікує`;
- `на розгляді`;
- `схвалено`;
- `відхилено`.

### FR-03: Invalid transition rejection

A status transition that is not allowed by the approved lifecycle must be rejected.

The current work request state must remain unchanged after an invalid transition attempt.

### FR-04: Employer authorization

Only an authorized owner of the relevant project may perform employer-side work request status changes.

A user must not be able to change a work request status for a project they do not own.

### FR-05: Approval behavior

The current behavior where approval of one freelancer affects other work requests for the same project must be explicitly defined.

If the existing behavior is retained:

- the selected request becomes `схвалено`;
- other applicable requests for the same project become `відхилено`.

The exact set of requests affected must be specified.

### FR-06: Status filtering preservation

Existing employer and freelancer work request filtering by status must continue to function.

### FR-07: Duplicate request protection preservation

A freelancer must not be able to create duplicate work requests for the same project.

### FR-08: Meaningful status-change notifications

A freelancer notification should be created only when a relevant work request status actually changes.

Saving a work request without a status change should not create a misleading status-change notification.

---

## 8. Technical Requirements

### TR-01: Existing domain model reuse

The implementation should continue to use the existing:

- `WorkRequest`;
- `WorkRequestStatus`;
- `Project`;
- `Freelancer`;
- `Notification`;
- `NotificationType`;

models unless repository analysis demonstrates that a model change is necessary.

Any model change requires explicit justification and approval.

### TR-02: Avoid implicit numeric business logic where reasonably possible

Business logic should not rely on unexplained literal values such as:

- `status_id == 2`;
- `status_id = 3`;

when the same behavior can be expressed using an explicit status lookup or a defined lifecycle contract.

### TR-03: Atomic consistency

A workflow operation that approves one request and rejects other requests for the same project should leave the related work requests in a consistent state.

The Builder should determine whether transaction handling is required.

### TR-04: Authorization validation

Authorization must be enforced server-side.

UI visibility alone must not be treated as sufficient protection.

### TR-05: Existing behavior compatibility

The change must not break:

- work request creation;
- employer work request listing;
- freelancer work request listing;
- status filtering;
- project functionality unrelated to request lifecycle;
- notification functionality unrelated to work requests;
- freelancer profile behavior;
- authentication.

---

## 9. Constraints

The implementation must not:

- redesign the entire project lifecycle;
- add new work request statuses without explicit approval;
- change freelancer profile behavior;
- redesign authentication;
- modify AI CV analysis;
- introduce unrelated notification features;
- introduce unrelated project model changes;
- perform broad refactoring outside the work request lifecycle without justification.

The change should remain focused on lifecycle correctness, authorization, notifications, and related tests.

---

## 10. Acceptance Criteria

### AC-01

A newly created work request receives the explicitly defined initial status.

### AC-02

Allowed work request status transitions are documented and implemented.

### AC-03

An invalid status transition is rejected and does not modify the current work request state.

### AC-04

A project owner can change the status of a work request belonging to their own project when the transition is valid.

### AC-05

A user cannot change the status of a work request belonging to another user's project.

### AC-06

The implementation does not depend on `WorkRequestStatus.objects.first()` as the sole mechanism for determining the initial status.

### AC-07

Lifecycle behavior does not depend on unexplained hard-coded numeric status IDs where a status can be resolved explicitly.

### AC-08

If the "approve one, reject others" rule is retained, approving one work request updates the other relevant requests for the same project according to the approved specification.

### AC-09

The "approve one, reject others" operation leaves all affected work requests in a consistent state.

### AC-10

A status-change notification is created when a work request status actually changes.

### AC-11

Saving or updating a work request without changing its status does not create a misleading status-change notification.

### AC-12

Existing employer work request filtering by status continues to function.

### AC-13

Existing freelancer work request filtering by status continues to function.

### AC-14

Existing duplicate work request protection continues to function.

### AC-15

Automated tests cover valid lifecycle transitions.

### AC-16

Automated tests cover invalid lifecycle transitions.

### AC-17

Automated tests cover project-owner authorization.

### AC-18

Automated tests cover unauthorized status-change attempts.

### AC-19

Automated tests cover the approved multi-request behavior when one freelancer is accepted.

### AC-20

Automated tests cover notification behavior for actual and non-actual status changes.

---

## 11. Out of Scope

The following are explicitly outside this change:

- adding new lifecycle statuses such as `in_progress`, `completed`, or `cancelled`;
- redesigning the entire project status lifecycle;
- payment or billing workflows;
- contract management;
- chat changes;
- rating workflow changes;
- freelancer matching;
- AI recommendations;
- general notification redesign;
- general UI redesign;
- Docker implementation;
- CI/CD implementation;
- broad refactoring of unrelated modules.

These may be addressed in separate future changes.

---

## 12. Known Relevant Components

The following components are currently known to be relevant:

- `workrequest/models.py`;
- `workrequest/views.py`;
- `workrequest/urls.py`;
- `workrequest/tests.py`;
- work request templates;
- `project/models.py`;
- `notification/models.py`;
- `notification/signals.py`;
- `notification/tasks.py`.

This list identifies currently known dependencies.

It does not automatically define the final allowed modification scope.

The Builder must confirm the actual dependency and modification scope during repository analysis.

---

## 13. Verification Expectations

The implementation should be verifiable through:

- automated lifecycle tests;
- automated authorization tests;
- automated notification tests;
- mapping between acceptance criteria and tests;
- documented test commands;
- recorded test results;
- implementation diff;
- repository commit SHA;
- independent Reviewer assessment.

Manual UI verification may be used as additional evidence, but it should not replace automated verification of lifecycle and permission rules.

---

## 14. Open Questions

The following questions must be resolved during specification before implementation where they affect business behavior.

### OQ-01: Initial status

Which existing status must be assigned to a newly created work request?

Current candidates include:

- `очікує`;
- `на розгляді`.

The current implementation does not define this explicitly.

### OQ-02: Allowed lifecycle

What exact transitions are permitted between:

- `очікує`;
- `на розгляді`;
- `схвалено`;
- `відхилено`?

A proposed lifecycle must be reviewed and approved before implementation.

### OQ-03: Terminal states

Should `схвалено` and `відхилено` be terminal states?

If not, the allowed outgoing transitions must be defined explicitly.

### OQ-04: Meaning of "на розгляді"

What business event should move a request from `очікує` to `на розгляді`?

This is not clearly defined by the current implementation.

### OQ-05: Approval of one freelancer

When one request becomes `схвалено`, should all other requests for the project always become `відхилено`?

The current implementation behaves this way, but the rule must be explicitly approved.

### OQ-06: Already rejected requests

If one request is approved, should already rejected requests be updated again, or should only active/pending requests be affected?

### OQ-07: Notification behavior

Which lifecycle transitions should trigger notifications?

The specification should define whether every valid transition or only selected transitions are notification-worthy.

### OQ-08: Project status synchronization

The current implementation also changes project status when a work request is approved.

The required relationship between work request status and project status must be confirmed before implementation.

---

## 15. Traceability References

This change defines the initial need, requirements, constraints, and acceptance criteria for the second agent-driven development cycle.

Detailed methodology, agent responsibilities, approval gates, evidence requirements, and the full traceability process are defined in:

`docs/METHODOLOGY.md`

The next artifacts expected for this change are:

- relevant knowledge / contract cards;
- `SPEC-002-work-request-lifecycle.md`;
- bounded implementation task prepared by the Builder.