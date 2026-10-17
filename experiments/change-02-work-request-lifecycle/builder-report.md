Status: Draft

# Builder Report

## Agent Configuration

Experiment:
CHANGE-002 / Experiment 2

Role:
Builder

Environment:
VS Code integrated agent

Model:
Not exposed by environment

Session type:
Independent session

Repository starting commit:
710fd006e706d559587ba82b540054718fc8b80c

Repository starting tag:
None (no exact tag reported for the starting commit)

Working tree state:
Clean (`git status --short` produced no entries when the artifacts were created)

Previous accepted change:
CHANGE-001

Previous accepted tag:
change-001-accepted

The previous Builder analysis session was read-only and no files were changed during that session. This follow-up creates documentation/card artifacts only.

## Repository State Reviewed

- Methodology: `docs/METHODOLOGY.md`.
- Handoff: `cards/handoff/HANDOFF-001.md`. The differently named `HANDOFF-001-change-001.md` requested in the initial instructions was not present.
- Change request: `changes/CHANGE-002-work-request-lifecycle.md`.
- Work Request model, views, URLs, tests, and migrations.
- Work-request templates: `freelancer-work-request.html`, `all_work_request.html`, `delete_work_request_a.html`, `update_work_request.html`.
- Project model/views, notification model/signals/tasks/app registration, freelancer model, user model, and directly related admin/rating status consumers.
- No application code, templates, tests, migrations, settings, or runtime configuration were modified.

## Confirmed Current Behavior

- `WorkRequestStatus` has a text `status` field. `WorkRequest` has a required status foreign key, nullable freelancer/project foreign keys, and a date field. The inspected migrations do not define a state machine or a uniqueness constraint for a freelancer/project pair.
- `create_work_request` resolves the logged-in user's freelancer record, checks for an existing project/freelancer request, then creates a request with `WorkRequestStatus.objects.first()`. That initial state is database-order-dependent. The existence check is not atomic with creation.
- The freelancer listing filters to the current user's freelancer record. The employer listing first scopes projects to `Project.user_id == request.user.id`; both accept a status query filter.
- The work-request status route is login-protected, parses an integer status ID on POST, and fetches the project by URL ID. It does not verify project ownership before mutation.
- On submitted status ID `2`, the work-request route saves every request for the project, assigning ID `2` to the selected freelancer's request and ID `3` to all other requests, regardless of their prior state. Other submitted IDs directly update the selected request; there is no transition validation.
- The work-request handler sets `project.status.id = 2`, not `project.status_id`. The inspected code does not establish that this persists the foreign-key change.
- `adminpannel.views.update_work_request` provides a separate update path. It can change a request's project; on status ID `2` it sets matching requests to IDs `2`/`3`, sets the selected project's `status_id` to `2`, and saves. It is login-protected but the view does not verify project ownership.
- `project.views` and `rating.views` also consume WorkRequest status ID `2` as an accepted-state filter.
- The templates display database status rows and, in the employer view, offer all statuses as choices. This UI does not enforce a server-side transition policy.
- WorkRequest creation causes an employer notification. Every save of an existing request with a valid freelancer/user relationship causes a freelancer notification; the signal does not check if status changed. The approval loops save every project request, so they can emit notifications for unchanged requests. A Notification save triggers the email function.
- `workrequest/tests.py` contains no lifecycle tests.
- Status rows and labels `1=очікує`, `2=схвалено`, `3=відхилено`, `4=на розгляді` are not evidenced in inspected source/migrations. Their existence/mapping must be confirmed against deployed data. The project status text and meaning of project status ID `2` are likewise not established.

## Relevant Dependencies

- `workrequest.models`: status and request schema.
- `workrequest.views` and `urls`: creation, listing, filtering, and owner-facing state mutation.
- `adminpannel.views`: a distinct state mutation path that could bypass lifecycle rules.
- `notification.signals`, `notification.models`, `notification.tasks`, and notification app signal registration: creation/update notification and email side effect.
- `project.models` and `project.views`: project ownership and accepted-request filtering.
- `freelancer.models` and `users.models`: requester/owner identity association.
- `rating.views`: another consumer of accepted-request status ID `2`.
- Work-request templates: display/filter/status form behavior; no change is currently proposed unless separately approved.

## Existing Contracts and Invariants

- A project has a required `user` owner.
- A WorkRequest can exist with null project/freelancer references due to model nullability and `SET_NULL`.
- Employer listing is owner-scoped; the POST status-change view is not.
- Application code currently attempts to prevent duplicate project/freelancer requests, but the check is not protected against concurrent submissions and no database unique constraint is shown.
- Employer and freelancer status filtering is part of existing behavior.
- Creating a WorkRequest notifies the employer. Existing WorkRequest updates notify the freelancer under the current save-based signal.
- The current approval behavior attempts a one-selected-request/other-requests rejection policy, but its database-ID dependence, treatment of all other requests, project synchronization, and two separate update paths make this an unconfirmed business contract rather than a safe invariant.

## Risks

- Status labels/order in deployment may differ from assumptions in the change request; explicit name resolution requires confirming data and uniqueness.
- The two status mutation routes can diverge or one can bypass authorization/lifecycle enforcement.
- The owner-facing route permits a logged-in non-owner to submit status changes when they know the route IDs.
- Status updates do not validate the current state under a row lock; competing writes to the same request may race.
- Notification signals can send misleading or repeated notifications for saves that do not change status; email is a side effect.
- Project status synchronization is inconsistent between the two current update paths and numeric semantics are unknown; the approved target contract explicitly leaves Project status unchanged.
- Nullable request relations require guards in operations and signals.
- Duplicate check/create can race; moving to a database constraint requires existing-data review and scope approval.
- Moving from numeric IDs to label lookups without validating production data can make creation or accepted-request filtering fail or misclassify records.

## Conflicts

- CHANGE-002 states status-ID/name mappings as current facts, but those values are not established by the inspected source or migrations. Verify them against the target database before implementation.
- CHANGE-002 says approval changes Project status; evidence differs by path. The work-request route mutates a related object's `id` attribute, while the admin route assigns the FK field. Neither proves the deployed business meaning of Project status ID `2`; the approved OQ-08 decision is to leave Project status unchanged.
- The main handler's approval loop currently updates all other requests without regard to current state. Human-approved OQ-05/OQ-06 replace this with selected-request-only updates; competitors must remain unchanged.
- The ordinary work-request handler and admin edit flow differ in project/status handling. The approved implementation scope must apply the same lifecycle and authorization checks to both paths, with no privileged lifecycle override.

## Open Questions Analysis

OQ-01 through OQ-08 have all been resolved and human-approved. Final decisions are recorded in `experiments/change-02-work-request-lifecycle/decisions.md`; the recommendations below are analysis history, not unresolved choices.

### OQ-01

Current repository behavior:

Creation assigns `WorkRequestStatus.objects.first()`, so the effective initial state depends on row ordering. Actual labels/IDs are not confirmed by source/migrations.

Options:

- `очікує`: request is submitted and awaits any owner action.
- `на розгляді`: creation itself means review has started.
- Another confirmed existing state, if deployed data or business terminology requires it.

Trade-offs:

`очікує` separates submission from active review and matches an explicit review step. `на розгляді` reduces one owner action but obscures whether review actually began. A different state may be necessary if deployed labels differ. Any option resolved only by a numeric ID remains brittle.

Builder recommendation:

Use `очікує`, resolved by a confirmed, unique explicit status label; fail explicitly if absent or ambiguous. Confirm the row exists in deployment.

Final decision:
Human approved: Initial WorkRequest status is `очікує`. Resolve by explicit label, not row order or numeric ID. Fail explicitly if missing or ambiguous.

### OQ-02

Current repository behavior:

No lifecycle matrix exists. The update UI offers all statuses, and the views accept arbitrary integer IDs without transition checks.

Options:

- Staged transitions: `очікує → на розгляді → (схвалено | відхилено)`.
- Permit direct decisions from `очікує` as well as decisions after `на розгляді`.
- Permit broader reversals or reopening with explicitly enumerated edges.

Trade-offs:

A staged workflow records that review began but requires an additional action. Direct decisions preserve the current one-step employer interaction while still enabling a review state. Reversals allow correction but make competing-request and notification semantics harder and require more tests.

Builder recommendation:

Use the staged-only matrix: `очікує → на розгляді`; from `на розгляді` to approved/rejected. Do not permit direct approval or rejection from `очікує`.

Final decision:
Human approved: Use staged-only lifecycle: `очікує → на розгляді → схвалено | відхилено`. No direct approval/rejection from `очікує`.

### OQ-03

Current repository behavior:

Approved/rejected are not enforced as terminal; arbitrary updates are accepted.

Options:

- Make both terminal for ordinary owner actions.
- Permit reopening/reversals through explicit transition edges.
- Permit only a privileged administrative correction path.

Trade-offs:

Terminal states simplify lifecycle guarantees and avoid accidental reversals, but errors are harder to correct. Reopen rules add complexity to re-approval and notifications. An admin override introduces a distinct authorization contract.

Builder recommendation:

Treat approved and rejected as terminal for ordinary owner actions; if correction is needed, approve a separately specified privileged path.

Final decision:
Human approved: `схвалено` and `відхилено` are terminal for ordinary owner actions.

### OQ-04

Current repository behavior:

The inspected source contains no operation that assigns or documents the business meaning of `на розгляді`; actual status data is unverified.

Options:

- Owner explicitly moves a submitted request into active review.
- It is the initial state at submission.
- It is not used in the lifecycle if business owners do not need the distinction.

Trade-offs:

Explicit owner action provides a meaningful event but adds a transition and user action. Using it at creation does not distinguish submitted from reviewed. Not using it simplifies lifecycle but conflicts with the listed current-state inventory if that status exists.

Builder recommendation:

If confirmed in data, use it for an explicit project-owner action marking active review, not as an implicit initial state.

Final decision:
Human approved: `на розгляді` means the project owner explicitly started reviewing the request. It is not assigned automatically at creation.

### OQ-05

Current repository behavior:

Both approval paths attempt to approve the selected freelancer and reject all other requests on the project. The model does not enforce one accepted freelancer per project.

Options:

- Retain exclusive acceptance and reject eligible competing requests.
- Permit multiple accepted requests and leave other requests unchanged.
- Make exclusivity a per-project configuration/business rule (would broaden scope).

Trade-offs:

Exclusivity matches existing code but may encode an undocumented assumption. Multiple acceptances permit team hiring but changes project search/rating implications. Configurable behavior increases scope.

Builder recommendation:

Multiple acceptance is supported by the approved target contract; approving a request does not reject competing requests.

Final decision:
Human approved: Multiple freelancers may be accepted for one project. Approving one request must not reject competing requests.

### OQ-06

Current repository behavior:

When status ID `2` is submitted, all other requests are assigned ID `3` and saved, regardless of their previous state.

Options:

- Rewrite every other request, including previously rejected ones.
- Change only requests in approved active states (`очікує`, `на розгляді`).
- Change only the selected request.

Trade-offs:

Rewriting terminal states may erase useful history and causes needless saves/notifications. Filtering to active states preserves prior decisions but depends on the approved lifecycle and status data. Selected-only behavior supports multiple acceptance.

Builder recommendation:

Change only the selected WorkRequest; do not mutate any other request, whatever its current status.

Final decision:
Human approved: Only the selected WorkRequest changes. All other requests remain unchanged, including already rejected requests.

### OQ-07

Current repository behavior:

The employer is notified on request creation. A freelancer is notified for every save of an existing WorkRequest (subject to related-user presence), not only when status changes. Notifications initiate email sending.

Options:

- Notify on every actual status transition.
- Notify only on selected transitions (for example final approval/rejection).
- Notify on state changes only for the directly selected request, or also cascade-affected requests.

Trade-offs:

Every-transition notifications provide visibility but can be noisy. Final-only notifications reduce noise but hide review progress. Cascade notifications inform affected freelancers but can multiply messages. Email side effects should not occur for rolled-back state changes.

Builder recommendation:

Notify exactly once for every actual WorkRequest status transition, not on unchanged saves. Dispatch status-change side effects after successful commit and preserve the employer creation notification.

Final decision:
Human approved: Notify the freelancer once for every actual WorkRequest status transition. Do not notify on unchanged saves. Preserve the employer notification on request creation. Dispatch status-change notification side effects only after successful commit.

### OQ-08

Current repository behavior:

The regular status handler assigns `project.status.id = 2`, not `status_id`; the admin path sets `project.status_id = 2`. Project status values and ID semantics are unknown.

Options:

- Do not synchronize Project status as part of WorkRequest lifecycle.
- Set a project status on approval using a confirmed mapping.
- Define a broader project lifecycle relation, including resets/reversals.

Trade-offs:

No synchronization avoids extending an unclear project contract but may leave project discovery/status unchanged. A mapping can keep UI/search behavior aligned but numeric assumptions and reverse transitions must be defined. Broader synchronization exceeds a small lifecycle task.

Builder recommendation:

Do not synchronize Project status with WorkRequest status in CHANGE-002. Any future mapping requires a separate approved change after Project status values and semantics are confirmed.

Final decision:
Human approved: Do not synchronize Project status with WorkRequest status in CHANGE-002. Transitions to `на розгляді`, `схвалено`, or `відхилено` leave Project status unchanged. Any future Project/WorkRequest status mapping requires a separate approved change. This final decision supersedes an earlier accidental choice to synchronize.

## Proposed Implementation Scope

The approved bounded scope is explicit initial-status resolution; the staged transition matrix; server-side project-owner authorization on every WorkRequest status mutation route; selected-request-only updates; actual-transition notifications after commit; and focused regression tests. Apply lifecycle and authorization rules to the separate admin update route so it cannot bypass the contract. Replace unexplained numeric WorkRequest status comparisons in directly related accepted-state consumers while preserving behavior. Project status remains unchanged.

Use `transaction.atomic()` for the state change and reliable post-commit notification scheduling. Lock the selected WorkRequest (or use an equivalent concurrency-safe approach) so two concurrent updates cannot validate against a stale state. There is no multi-request approval cascade under the approved decisions.

## Proposed Allowed Files

Allowed files, as approved in TASK-002:

- `devopssite/workrequest/views.py`
- `devopssite/workrequest/urls.py` only if required by the authorization/interface contract
- `devopssite/workrequest/tests.py`
- `devopssite/adminpannel/views.py` and `devopssite/adminpannel/tests.py`
- `devopssite/notification/signals.py` and `devopssite/notification/tests.py`
- `devopssite/project/views.py` and `devopssite/project/tests.py`
- `devopssite/rating/views.py` and `devopssite/rating/tests.py`

No model/migration changes are presumed. Additional files require a reported dependency and human approval.

## Explicitly Out of Scope

- Any implementation in this Builder task.
- New WorkRequest statuses or broad Project lifecycle redesign.
- Payments, contracts, chat, rating workflow redesign, matching, AI features.
- General notification/email or UI redesign.
- Unrelated refactoring or application changes.
- Schema/uniqueness migrations absent separate justification, data review, and approval.
- Any Project status synchronization.
- Any privileged administrative lifecycle override.

## Transaction / Consistency Assessment

The current approval paths perform separate saves without a transaction; the work-request path also updates competing requests. The approved target removes that cascade and changes only the selected WorkRequest. Wrap the selected state transition in `transaction.atomic()` and serialize updates on that WorkRequest (for example, with a row lock) to prevent stale-state transition validation. Schedule notification side effects only after successful commit. Project status is not part of this transaction because it remains unchanged. The separate duplicate creation check can race; a database uniqueness change is not presumed in scope and requires existing-data review and approval.

## Authorization Assessment

The employer listing filters by project ownership, but the status-change handler only fetches the project by ID and has no explicit ownership comparison. Login protection is not sufficient. Enforce `project.user_id == request.user.id` server-side before any write and apply the same approved lifecycle and authorization policy to every route capable of changing WorkRequest status, including the admin edit path. No privileged lifecycle override is included. Reject missing/null relations safely and ensure denied attempts leave all state unchanged.

## Notification Assessment

Creation notification to the employer is preserved. Existing request saves currently trigger a freelancer notification regardless of whether status changed. Target behavior compares actual state changes: notify the freelancer once for every actual transition, never for unchanged saves, and defer status-change side effects until successful commit. No competing-request cascade notifications occur because other requests remain unchanged.

## Proposed Test Plan

1. Create with deliberately reordered status rows and assert explicit `очікує`; cover missing/ambiguous configuration.
2. Test both valid transitions and invalid edges, including direct decisions from `очікує` and transitions out of terminal states; assert state remains unchanged after rejection.
3. Exercise owner success, non-owner denial, and unauthenticated denial for every status-changing route, including the admin edit route; verify no unauthorized mutation.
4. Put multiple requests in varied states on one project, transition the selected request, and assert every other request remains unchanged.
5. Assert Project status remains unchanged for each valid WorkRequest transition.
6. Force failure during a state change and assert rollback; test or otherwise verify serialization of concurrent transitions on the same WorkRequest.
7. Assert exactly one notification for each actual transition, no notification on unchanged saves, and no status notification if the transaction fails.
8. Retain employer/freelancer status-filter and duplicate-request regression tests.

## Acceptance Criteria Mapping

| Criteria | Proposed verification |
|---|---|
| AC-01, AC-06 | Explicit initial state tests, independent of row ordering |
| AC-02, AC-03, AC-15, AC-16 | Full approved matrix and invalid-transition state preservation |
| AC-04, AC-05, AC-17, AC-18 | Owner and unauthorized tests across applicable routes |
| AC-07 | Search for numeric status coupling in scoped consumers plus behavior tests |
| AC-08, AC-19 | Assert only the selected request changes; competing requests in any status remain unchanged |
| AC-09 | Atomic rollback and concurrent transition consistency tests |
| AC-10, AC-11, AC-20 | Actual-transition notification, unchanged-save suppression, and post-commit tests |
| AC-12, AC-13 | Employer and freelancer filter regression tests |
| AC-14 | Duplicate request protection regression test |

## Produced Artifacts

- `cards/knowledge/work-request.md`
- `cards/knowledge/work-request-lifecycle.md`
- `cards/knowledge/project-work-request-contract.md`
- `cards/knowledge/work-request-notifications.md`
- `cards/specs/SPEC-002-work-request-lifecycle.md`
- `cards/tasks/TASK-002-work-request-lifecycle.md`
- `experiments/change-02-work-request-lifecycle/builder-report.md`
- `experiments/change-02-work-request-lifecycle/decisions.md`
