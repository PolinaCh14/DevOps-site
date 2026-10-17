Status: Draft

# CHANGE-002 Decisions

Human-approved decisions for Open Questions OQ-01 through OQ-08.

OQ-01:
Initial WorkRequest status is `очікує`.
Resolve by explicit label, not row order or numeric ID.
Fail explicitly if missing or ambiguous.

OQ-02:
Use staged-only lifecycle:
`очікує → на розгляді → схвалено | відхилено`
No direct approval/rejection from `очікує`.

OQ-03:
`схвалено` and `відхилено` are terminal for ordinary owner actions.

OQ-04:
`на розгляді` means the project owner explicitly started reviewing the request.
It is not assigned automatically at creation.

OQ-05:
Multiple freelancers may be accepted for one project.
Approving one request must not reject competing requests.

OQ-06:
Only the selected WorkRequest changes.
All other requests remain unchanged, including already rejected requests.

OQ-07:
Notify the freelancer once for every actual WorkRequest status transition.
Do not notify on unchanged saves.
Preserve the employer notification on request creation.
Dispatch status-change notification side effects only after successful commit.

OQ-08:
Do not synchronize Project status with WorkRequest status in CHANGE-002.
Transitions to `на розгляді`, `схвалено`, or `відхилено` leave Project status unchanged.
Any future Project/WorkRequest status mapping requires a separate approved change.

OQ-08 final decision supersedes the earlier accidental synchronization choice.
