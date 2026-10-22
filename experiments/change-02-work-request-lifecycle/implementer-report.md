# Implementer Report

## Implementer Stage Status

Completed for the approved CHANGE-002 scope. This is not an independent review or a CHANGE-002 acceptance decision.

## Agent Configuration

Experiment:
CHANGE-002 / Experiment 2

Role:
Implementer

Environment:
VS Code integrated agent

Model:
Model name not exposed in this session

Session type:
Independent session

Repository starting commit:
43c0bc812a4d6ebba82cd72c29ab589782d5fedf

Repository starting tag:
change-002-builder-approved

Expected starting tag:
change-002-builder-approved

Working tree state:
Initial implementation session: clean. On resuming after the human label decision, the working tree contained the pre-implementation report/evidence and the human-approved HD-009 addition to `decisions.md`; those changes were preserved.

---

## Approved Inputs

- `changes/CHANGE-002-work-request-lifecycle.md`
- `cards/knowledge/work-request.md`
- `cards/knowledge/work-request-lifecycle.md`
- `cards/knowledge/project-work-request-contract.md`
- `cards/knowledge/work-request-notifications.md`
- `cards/specs/SPEC-002-work-request-lifecycle.md`
- `cards/tasks/TASK-002-work-request-lifecycle.md`
- `experiments/change-02-work-request-lifecycle/decisions.md`, including human-approved HD-009 and superseding HD-010:
  - `В очікуванні`
  - `На розгляді`
  - `Схвалено`
  - `Відхилено`
  - lifecycle from HD-010: `В очікуванні → На розгляді`, `В очікуванні → Схвалено`, `В очікуванні → Відхилено`, `На розгляді → Схвалено`, and `На розгляді → Відхилено`
  - existing status rows are not renamed
- Human-approved bounded extension: add one WorkRequest data migration to introduce `На розгляді` when missing, fail if ambiguous, and make no schema changes.
- `docs/METHODOLOGY.md`
- `cards/handoff/HANDOFF-001.md`

---

## Pre-Implementation Verification

The initial baseline was commit `43c0bc812a4d6ebba82cd72c29ab589782d5fedf`, tag `change-002-builder-approved`, with a clean working tree. Repository inspection confirmed that the existing initial status selection used row ordering and that the existing ordinary and admin status paths used numeric IDs and had no shared transition guard.

The configured database was queried read-only and contained one row each for `В очікуванні`, `Відхилено`, and `Схвалено`; it did not yet contain `На розгляді`. The human approved HD-009 to use these exact deployed labels as canonical and approved the bounded migration extension. Existing labels were left unchanged. The migration was applied by Django's test-database migration setup during tests; the configured application database was not migrated or modified.

After implementation, the human approved HD-010, making `На розгляді` optional before a final decision. The transition matrix and tests were updated to allow direct approval/rejection from `В очікуванні`; terminal-state rules and all other OQ decisions were preserved.

---

## Files Changed

Implementation:

- `cards/specs/SPEC-002-work-request-lifecycle.md` — updated to the superseding HD-010 lifecycle matrix
- `cards/tasks/TASK-002-work-request-lifecycle.md` — updated transition behavior and test expectations for optional review
- `devopssite/workrequest/views.py`
- `devopssite/workrequest/migrations/0003_ensure_reviewing_work_request_status.py` — bounded scope extension approved before implementation; data-only migration, no schema change
- `devopssite/workrequest/tests.py`
- `devopssite/adminpannel/views.py`
- `devopssite/notification/signals.py`
- `devopssite/project/views.py`
- `devopssite/rating/views.py`
- `experiments/change-02-work-request-lifecycle/decisions.md` — recorded superseding HD-010; the duplicate equivalent HD-010 section was consolidated after user approval

Requested experiment evidence:

- `experiments/change-02-work-request-lifecycle/implementer-report.md`
- `experiments/change-02-work-request-lifecycle/evidence/commands.txt`
- `experiments/change-02-work-request-lifecycle/evidence/test-results.txt`
- `experiments/change-02-work-request-lifecycle/evidence/diff.patch`

The human-added HD-009 was present before implementation resumed and its text was preserved. HD-010 was added to record the subsequent human decision.

## Implementation Summary

- Resolve lifecycle statuses by exact canonical labels. Missing or duplicate labels raise an explicit `ImproperlyConfigured` error; invalid requested transitions return HTTP 400.
- Create new requests with `В очікуванні`, independent of status row order.
- Add a data migration that creates `На розгляді` only when absent, does not rename or update existing rows, and fails if duplicate exact rows exist. Its reverse is intentionally a no-op so it cannot delete a status row that may already be referenced.
- Use the human-approved final lifecycle: `В очікуванні → На розгляді`, `В очікуванні → Схвалено`, `В очікуванні → Відхилено`, `На розгляді → Схвалено`, and `На розгляді → Відхилено`. `Схвалено` and `Відхилено` are terminal; active review is optional.
- Use one shared status transition operation for ordinary and admin-panel routes. It enforces project ownership, only changes the selected request, rejects project reassignment through the admin edit path, and leaves Project status untouched.
- Allow final approval or rejection directly from `В очікуванні` as well as from `На розгляді`; entering active review remains an explicit optional owner action.
- Use actual deployed WorkRequest labels consistently: `В очікуванні`, `На розгляді`, `Схвалено`, and `Відхилено`. Existing labels are not renamed; the data migration supplies the missing active-review label.
- Preserve multiple accepted freelancers per project: transitions affect only the selected WorkRequest and do not reject competing requests.
- Preserve employer and freelancer status filtering, duplicate-request protection, the employer creation notification, and unrelated project/notification behavior.
- Wrap state transitions in `transaction.atomic()` and lock the selected WorkRequest with `select_for_update()` before validating its current state.
- Replace save-based freelancer status notifications with an `on_commit` notification for each actual transition; unchanged status saves do not notify. The existing employer creation notification remains.
- Replace accepted WorkRequest filtering by numeric status ID in `project.views` and `rating.views` with the canonical `Схвалено` label.
- Add focused lifecycle, authorization, filtering, notification, transaction, row-lock, migration-status, and duplicate-protection tests.

## Human Manual Verification (Supplemental Evidence)

The human reports manually reviewing the implemented behavior and finding it acceptable. The reported manual verification covered:

- creating a new WorkRequest;
- verifying its initial status is `В очікуванні`;
- exercising valid transitions under the final HD-010 matrix;
- verifying terminal behavior for `Схвалено` and `Відхилено`;
- multiple WorkRequests attached to one project;
- confirming Project status remains unchanged;
- confirming project-owner authorization behavior;
- confirming notifications are associated with actual status transitions;
- employer/freelancer status filtering;
- duplicate WorkRequest protection.

This is supplemental human-reported evidence, not a substitute for the automated tests or independent Reviewer verification.

## Acceptance Criteria Mapping

- **AC-01 — Implemented.** Explicit initial label and order-independence test: `workrequest/views.py` (`INITIAL_STATUS`, `create_work_request`); `workrequest/tests.py::test_initial_status_is_selected_by_label_not_row_order`.
- **AC-02 — Implemented.** Superseding HD-010 matrix: `workrequest/views.py::ALLOWED_TRANSITIONS`; all five valid transitions, including direct decisions from `В очікуванні`, are tested in `workrequest/tests.py::test_each_approved_transition_succeeds`.
- **AC-03 — Implemented.** Rejected transitions return 400 without changing state: `workrequest/views.py::apply_work_request_status_transition`; `test_terminal_transitions_do_not_mutate` and `test_non_lifecycle_status_is_rejected_without_mutation`.
- **AC-04 — Implemented.** Owner valid transitions: shared operation in `workrequest/views.py`; `test_each_approved_transition_succeeds` and `test_admin_mutation_uses_same_lifecycle_and_owner_authorization`.
- **AC-05 — Implemented.** Non-owner is denied: shared operation ownership check; `test_owner_authorization_and_unauthorized_denial` and `test_admin_route_rejects_non_owner_project_change_and_anonymous_user`.
- **AC-06 — Implemented.** No first-row status selection in application logic; explicit initial lookup and `test_initial_status_is_selected_by_label_not_row_order`.
- **AC-07 — Implemented.** Lifecycle status lookups use canonical labels in `workrequest/views.py`; accepted-state queries use `Схвалено` in `project/views.py` and `rating/views.py`; migration creates `На розгляді`; `test_migration_provides_exactly_one_reviewing_status` and missing/ambiguous configuration test.
- **AC-08 — Implemented against the final approved contract.** The earlier “approve one, reject others” proposal was superseded by approved OQ-05/OQ-06: no competing request is rejected or changed. Evidence: `test_only_selected_request_changes_and_project_status_is_unchanged`.
- **AC-09 — Implemented.** Atomic selected-row transition and rollback behavior: `workrequest/views.py::apply_work_request_status_transition`; `test_rolled_back_transition_does_not_notify` and `test_transition_query_locks_the_selected_request_where_supported`.
- **AC-10 — Implemented.** A status notification is scheduled only for an actual transition after commit: `workrequest/views.py::apply_work_request_status_transition`, `notification/signals.py::notify_freelancer_on_status_change`; notification test.
- **AC-11 — Implemented.** Unchanged saves do not emit a status notification; `test_status_change_notification_occurs_once_only_for_real_transition`.
- **AC-12 — Implemented.** Employer status filtering preserved; `test_owner_and_freelancer_status_filters_remain_available`.
- **AC-13 — Implemented.** Freelancer status filtering preserved; `test_owner_and_freelancer_status_filters_remain_available`.
- **AC-14 — Implemented.** Duplicate request guard preserved; `test_duplicate_work_request_protection_remains`.
- **AC-15 — Implemented.** All five approved transition edges are exercised by `test_each_approved_transition_succeeds`.
- **AC-16 — Implemented.** Transitions from terminal states and submission of a non-lifecycle status are rejected without mutation by `test_terminal_transitions_do_not_mutate` and `test_non_lifecycle_status_is_rejected_without_mutation`. Direct decisions from `В очікуванні` are valid under HD-010.
- **AC-17 — Implemented.** Owner authorization is checked in the shared operation used by both mutation routes; ordinary and admin owner tests.
- **AC-18 — Implemented.** Non-owner and unauthenticated denial tested on ordinary and admin routes; see authorization tests above.
- **AC-19 — Implemented.** Only the selected request changes; competing approved and rejected requests remain unchanged; `test_only_selected_request_changes_and_project_status_is_unchanged`.
- **AC-20 — Implemented.** Exactly-one notifications on real transitions, none on unchanged saves, and none on rollback; notification tests above.

## Tests Added or Updated

- `devopssite/workrequest/tests.py`: 15 focused lifecycle tests, including:
  - initial status by explicit label and row-order independence;
  - missing and ambiguous lifecycle status failures;
  - migration-provided review status;
  - all valid edges, including direct final decisions from the initial state, and invalid terminal-state/non-lifecycle transitions;
  - owner, non-owner, and anonymous access;
  - selected-only changes, competing request preservation, and unchanged Project status;
  - exactly-once transition notifications, unchanged saves, and rollback;
  - row-lock SQL verification where supported;
  - employer/freelancer status filters and duplicate request protection;
  - admin path lifecycle and authorization behavior.
- Existing `project` tests were run as regression coverage; no test file changes were needed there.

## Commands Executed

- `git rev-parse HEAD`
- `git status --short`
- `git tag --points-at HEAD`
- Read-only configured status-label queries using `..\venv\Scripts\python.exe manage.py shell ...`
- `..\venv\Scripts\python.exe manage.py test workrequest adminpannel notification project rating --keepdb --verbosity 1`
- `..\venv\Scripts\python.exe manage.py check`
- `..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run`
- `..\venv\Scripts\python.exe manage.py showmigrations workrequest`
- `git diff --check`

## Test Results

- Focused WorkRequest, admin-panel, notification, project, and rating suites: **20 tests passed** after applying the superseding HD-010 lifecycle.
- Django system check: passed, no issues.
- Migration drift check: passed, no model changes detected.
- Patch whitespace check: passed.
- `showmigrations workrequest` against the configured application database shows the new migration pending; it was intentionally not applied to that database. The test runner applied migrations to its test database and the migration status test passed.

## Deviations

None. The single migration file was an approved, bounded scope extension. No schema or model change was made.

## Unfinished Work

None within the approved implementation scope. The new data migration remains pending on the configured application database by design and should be applied through the normal deployment migration process. An unrelated pre-existing worktree change in `devopssite/freelancer/views.py` was left untouched and excluded from the CHANGE-002 implementation commit.

## Final Implementation Version

Commit:
`2d713d82f8250b4a20c3803d456fe32327a25ab9` — `Implement CHANGE-002 work request lifecycle`

Tag:
`change-002-implemented` — annotated tag points to `2d713d82f8250b4a20c3803d456fe32327a25ab9`. This is the implementation tag, not an acceptance tag.
