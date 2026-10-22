Status: Approved

# SPEC-002 — Work Request Lifecycle

## Status and approval gate

Status: Approved

The business decisions for OQ-01 through OQ-08 have been human-approved and are recorded in `experiments/change-02-work-request-lifecycle/decisions.md`. This specification is approved for implementation.

## Goal

Make work-request creation and status changes explicit, validated, permission-aware, consistent, and testable while preserving request listing/filtering and existing collaboration behavior that is approved for retention.

## Current facts and constraints

- A work request references status, freelancer, and project; project and freelancer references may be null.
- Creation currently chooses the first status row.
- More than one status-update path exists: the work-request endpoint and the admin work-request edit view.
- Approval behavior in those paths is implemented using numeric IDs and is not fully consistent.
- Employer listing is owner-scoped; the status-change endpoint itself does not verify project ownership.
- Update notifications currently occur on any save of an existing work request.
- Status labels/IDs in CHANGE-002, actual database contents, and Project-status meanings are not proven by source/migrations and must be checked against deployed data before implementation.

## Target contract

### Initial state — OQ-01 (resolved)

New WorkRequests start in `В очікуванні`. Resolve the status using its exact explicit label, not database row ordering or numeric ID. If the label is missing or ambiguous, fail explicitly; do not choose a fallback.

### Lifecycle transitions — OQ-02, OQ-03, OQ-04 (resolved)

| Current state | Allowed next state | Notes |
|---|---|---|
| `В очікуванні` | `На розгляді` | Optional explicit owner action to begin active review |
| `В очікуванні` | `Схвалено` or `Відхилено` | Owner may decide without first entering active review |
| `На розгляді` | `Схвалено` or `Відхилено` | Owner decides after beginning active review |
| `Схвалено` | none | Terminal for ordinary owner actions |
| `Відхилено` | none | Terminal for ordinary owner actions |

Every attempted transition not present in the human-approved matrix must be rejected without changing the target or related request state.

Direct approval or rejection from `В очікуванні` is permitted. `На розгляді` is optional and entered only through an explicit owner action, never automatically at creation. Approved and rejected requests cannot be reopened or reversed by ordinary owner actions.

This matrix supersedes the staged-only lifecycle previously recorded for OQ-02. The change is recorded as HD-010 in `experiments/change-02-work-request-lifecycle/decisions.md`; the canonical status labels and other approved OQ decisions are unchanged.

### Approval and competing requests — OQ-05, OQ-06 (resolved)

Multiple freelancers may be accepted for one project. A transition changes only the selected WorkRequest. Every other WorkRequest remains unchanged, including requests that are already rejected. There is no automatic competitor rejection or other multi-request cascade.

### Authorization

- Status changes are POST-only and must be authorized server-side.
- Before mutation, the acting authenticated user must own the target request's project (`project.user_id == request.user.id`).
- The request must exist and have a non-null project/freelancer as required by the operation.
- Listing visibility is not authorization.
- Apply equivalent lifecycle and authorization checks to every route that can change a WorkRequest status; the separate admin editing route must not bypass the approved contract. This change does not define a privileged lifecycle override.
- Unauthorized requests must not mutate any request or project.

### Status resolution and invalid input

- Resolve status identities using explicit, confirmed status labels or another human-approved stable business key; do not use unexplained status primary-key literals.
- Missing/ambiguous configured lifecycle statuses must produce an explicit failure, not a first-row or success-shaped fallback.
- Validate submitted statuses and current-to-target transitions before writing.
- Invalid input or invalid transition must leave all involved records unchanged. The exact user-facing response/redirect behavior is an implementation detail to preserve existing UX where possible; server-side rejection is required.

### Notifications — OQ-07 (resolved)

The employer notification on WorkRequest creation is preserved. Notify the freelancer once for every actual WorkRequest status transition, but do not notify on unchanged saves. Dispatch status-change notification side effects only after the status update commits successfully. Preserve the existing notification model and email flow; do not broaden this task into notification redesign.

### Project status synchronization — OQ-08 (resolved)

Do not synchronize Project status with WorkRequest status in CHANGE-002. Transitions to `На розгляді`, `Схвалено`, or `Відхилено` leave Project status unchanged. Any future Project/WorkRequest status mapping requires a separate approved change.

## Consistency requirements

- A transition updates only the selected WorkRequest and leaves every other request and Project status unchanged.
- Persist each state change atomically and serialize concurrent transitions on the selected WorkRequest so validation applies to its current state.
- Status-change notification side effects must follow successful commit; failed transactions must not produce corresponding notifications.
- Existing request creation, employer/freelancer listings, and status filters must continue functioning.
- Existing duplicate-request protection must continue functioning. Whether to add database uniqueness/concurrency protection is a separate scope decision and requires checking existing data first.

## Acceptance criteria mapping

| AC | Required outcome | Proposed evidence |
|---|---|---|
| AC-01 | New request uses the explicitly approved initial state | Creation test with non-order-dependent status rows |
| AC-02 | Approved lifecycle matrix is explicit and implemented | Transition table review and matrix-driven tests |
| AC-03 | Invalid transition is rejected with no state mutation | Invalid-transition tests asserting all affected rows unchanged |
| AC-04 | Owner can make a valid change on own project | Authenticated owner POST test |
| AC-05 | Non-owner cannot alter another user's project request | Unauthorized POST test asserting no mutation |
| AC-06 | Initial state does not depend on `objects.first()` | Code-level check plus creation test where row order differs |
| AC-07 | Business behavior avoids unexplained numeric status IDs | Review all directly related status consumers and targeted tests |
| AC-08 | The selected request is approved without rejecting competing requests | Multi-request test asserting every non-selected request remains unchanged |
| AC-09 | The approved operation leaves all affected state consistent | Transaction rollback and concurrent-transition strategy review/test |
| AC-10 | Actual status change triggers the approved notification | Signal/service test for approved transition |
| AC-11 | Unchanged save does not create status notification | Test saving same status |
| AC-12 | Employer status filter still works | Employer listing filter test |
| AC-13 | Freelancer status filter still works | Freelancer listing filter test |
| AC-14 | Duplicate protection remains | Duplicate creation test |
| AC-15 | Valid transitions covered | Tests cover all five approved transitions, including direct final decisions from `В очікуванні` |
| AC-16 | Invalid transitions covered | Tests cover rejected terminal-state transitions and non-lifecycle status submissions |
| AC-17 | Project-owner authorization covered | Owner test for all applicable status mutation routes |
| AC-18 | Unauthorized attempts covered | Non-owner and unauthenticated tests; no mutation assertion |
| AC-19 | Approved multiple-request behavior covered | Test that only the selected WorkRequest changes while other requests have varied states |
| AC-20 | Notification changes and unchanged saves covered | Notification-count/content tests for actual transitions and unchanged saves |

## Explicit non-goals

No new WorkRequest statuses, project lifecycle redesign, billing, contracts, chat/rating redesign, freelancer matching, AI recommendations, broad notification redesign, general UI redesign, or unrelated refactoring.

## Implementation preconditions and remaining scope notes

- Confirm the actual configured WorkRequestStatus rows include exactly one row for each required label before deployment; explicit resolution must fail visibly if configuration is invalid.
- Apply approved lifecycle checks to every WorkRequest status mutation route, including the separate admin edit path. It must not bypass transition policy or provide an unapproved privileged override.
- Database uniqueness/concurrency changes for duplicate request creation are not included; preserve the current duplicate-request protection.
