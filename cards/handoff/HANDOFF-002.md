# HANDOFF-002 — CHANGE-002

Status: Accepted

## Completed change

CHANGE-002: Work Request Lifecycle Validation and Access Control.

The change completed the Builder → Implementer → Independent Reviewer → Human
Acceptance cycle. The human accepted the implementation after reviewing the
Reviewer result of `PASS WITH MINOR FINDINGS`.

## Accepted behavior

- New WorkRequests start in `В очікуванні`, resolved by exact label.
- The approved transitions are:
  - `В очікуванні` → `На розгляді`
  - `В очікуванні` → `Схвалено`
  - `В очікуванні` → `Відхилено`
  - `На розгляді` → `Схвалено`
  - `На розгляді` → `Відхилено`
- `На розгляді` is an optional, explicit owner action. `Схвалено` and
  `Відхилено` are terminal for ordinary owner actions.
- Only the selected WorkRequest changes. Multiple freelancers may be accepted
  for the same project; competing requests are not automatically rejected.
- Status changes require authenticated project ownership on both applicable
  mutation paths, including the admin-panel edit route.
- WorkRequest transitions leave Project status unchanged.
- Status-change notifications are sent once per actual transition and only
  after commit. Unchanged saves do not send status notifications. The employer
  notification on creation is preserved.
- Employer/freelancer status filters and duplicate-request protection remain.
- Lifecycle and accepted-state consumers use explicit status labels rather than
  unexplained numeric status IDs.

## Final accepted version

Implementation commit:
`2d713d82f8250b4a20c3803d456fe32327a25ab9`

Implementation tag:
`change-002-implemented`

Acceptance tag:
`change-002-accepted`

The acceptance tag points to the exact reviewed implementation commit.
`experiments/change-02-work-request-lifecycle/acceptance.md` records the human
acceptance and accepted non-blocking findings.

## Verification result

Independent Reviewer focused suite:
20 tests passed across `workrequest`, `adminpannel`, `notification`, `project`,
and `rating`.

Additional checks:
- Django system check passed.
- Migration drift check reported no changes.
- Implementation source diff passed `git diff --check`; the committed diff
  evidence file itself contains trailing whitespace.

## Accepted non-blocking observations

- `experiments/change-02-work-request-lifecycle/evidence/diff.patch` contains
  trailing whitespace.
- The Reviewer session initially opened a later checkout, but the exact
  `change-002-implemented` tag was independently reviewed and tested.

These observations were explicitly accepted by the human and do not change
application behavior.

## Baseline for the next cycle

Use `change-002-accepted` at
`2d713d82f8250b4a20c3803d456fe32327a25ab9` as the accepted CHANGE-002 baseline.
The repository checkout may have later commits; those commits are not included
in the CHANGE-002 acceptance and must be independently assessed before being
treated as part of this accepted baseline.
