Status: Approved

# TASK-002 — Implement Approved Work Request Lifecycle

## Status and readiness

Status: Approved

**Implementation-ready: Yes.** OQ-01 through OQ-08 and this task's bounded scope have been human-approved. The decisions are recorded in `experiments/change-02-work-request-lifecycle/decisions.md` and specified in SPEC-002. Implement only within the allowed scope and behavior defined here.

## Objective

After approval, implement the confirmed WorkRequest lifecycle and project-owner authorization with focused automated tests, preserving existing listing, filtering, creation, and notification contracts except where explicitly changed by approved decisions.

## Allowed scope

- Work-request creation/status-change paths and their directly related transition logic.
- The alternate `adminpannel` WorkRequest status-edit path, to enforce the same approved lifecycle and prevent bypass. This path does not receive a privileged lifecycle override.
- WorkRequest notification signal behavior necessary to notify exactly once for actual status transitions, not unchanged saves, and only after commit.
- Direct WorkRequest status consumers identified in `project/views.py` and `rating/views.py`, to remove unexplained numeric status-ID coupling while preserving accepted-request behavior.
- Focused tests for the behaviors and acceptance criteria below.
- No model/schema change is presumed necessary. Any proposed migration, uniqueness constraint, or model change requires separate justification and separate approval before expanding scope.

## Proposed allowed files

Paths are relative to `devopssite/`:

- `workrequest/views.py`
- `workrequest/urls.py` only if required for the approved authorization/interface contract
- `workrequest/tests.py`
- `adminpannel/views.py` and `adminpannel/tests.py` for the alternate WorkRequest status mutation route
- `notification/signals.py` and `notification/tests.py` for the approved transition-notification contract
- `project/views.py` and `project/tests.py` for accepted-state filtering
- `rating/views.py` and `rating/tests.py` for accepted-state filtering

Any additional file is out of scope unless the implementer reports a blocking dependency and receives approval. Do not modify templates unless a separately approved UX requirement makes it necessary.

## Required implementation behavior after approval

1. Assign `очікує` as the initial WorkRequest status by explicit label, not row ordering or numeric ID; fail explicitly if missing or ambiguous.
2. Enforce exactly this transition matrix: `очікує → на розгляді`; `на розгляді → схвалено` or `відхилено`. No direct decision from `очікує`; approved and rejected are terminal for ordinary owner actions. Reject invalid transitions without mutation.
3. Treat `на розгляді` as an explicit project-owner action to begin review; do not assign it automatically at creation.
4. Enforce server-side project ownership for status changes on every applicable mutation route, including the admin-panel edit route; that route must not bypass the contract or provide a privileged override.
5. Change only the selected WorkRequest. Multiple freelancers may be accepted for one project; never reject or otherwise mutate competing requests.
6. Resolve lifecycle statuses by their explicit labels rather than unexplained numeric primary-key literals; fail explicitly on missing/ambiguous configuration.
7. Notify the freelancer once for every actual status transition, never for unchanged saves. Preserve the employer notification on creation; dispatch status-change side effects only after successful commit.
8. Leave Project status unchanged for all WorkRequest transitions in this change.
9. Apply atomic transaction handling and serialize concurrent transitions on the selected WorkRequest so transition validation uses its current state.
10. Preserve employer/freelancer status filtering and duplicate-request protection.

## Required tests

- Explicit `очікує` initial status independent of row ordering; missing/ambiguous configuration failure.
- Both valid transitions and representative invalid transitions, including direct decision from `очікує` and transitions out of terminal states; assert no mutation on rejection.
- Owner authorization success and non-owner/unauthenticated denial for every applicable mutation route, including the admin-panel route.
- Multiple requests on one project: changing the selected request must leave every other request unchanged, including previously rejected and already approved requests.
- Project status remains unchanged for transitions to `на розгляді`, `схвалено`, and `відхилено`.
- Transaction rollback and consistency behavior; verify or exercise row-level concurrency control where practical.
- Exactly one notification for an actual status transition, no notification for unchanged saves, and no status notification if the update transaction fails.
- Employer and freelancer status filters.
- Duplicate request protection remains.

## Acceptance criteria mapping

| Acceptance criteria | Task verification |
|---|---|
| AC-01, AC-06 | Explicit initial-status creation tests |
| AC-02, AC-03, AC-15, AC-16 | Complete approved transition matrix tests and rejected-edge state-preservation tests |
| AC-04, AC-05, AC-17, AC-18 | Owner, non-owner, and unauthenticated request tests on all applicable status mutation routes |
| AC-07 | Review of lifecycle status resolution and direct status consumers; focused behavior tests |
| AC-08, AC-19 | Test that approval does not reject or otherwise change any competing request |
| AC-09 | Atomic update/rollback and concurrent transition consistency tests |
| AC-10, AC-11, AC-20 | Actual-transition notification, unchanged-save suppression, and post-commit behavior tests |
| AC-12, AC-13 | Employer and freelancer filter regression tests |
| AC-14 | Duplicate request regression test |

## Explicitly out of scope

- Implementation before the human approves this Draft task and related Draft specification.
- New WorkRequest statuses or redesign of the Project lifecycle.
- Payments, billing, contracts, chat, rating workflow, matching, or AI features.
- General notification/email redesign.
- General UI redesign or template changes not separately approved.
- Broad refactoring, unrelated cleanup, or unrelated app changes.
- Schema/migration changes or database uniqueness constraints unless separately justified, reviewed against existing data, and approved.
- Any Project status synchronization; all WorkRequest transitions leave Project status unchanged.
- Any privileged administrative lifecycle override.

## Completion evidence expected

Record changed files, focused test command/results, acceptance-criteria-to-test mapping, transaction/concurrency evidence, and any remaining risks. This task does not authorize commits or acceptance.
