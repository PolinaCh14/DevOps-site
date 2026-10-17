Status: Approved

# Work Request Lifecycle — Current Repository Facts

## Current state representation

- A request points to a `WorkRequestStatus` row, whose `status` field is a text value.
- Neither the model nor the inspected work-request migrations constrain which labels exist or define a state machine.
- The labels and numeric IDs described in CHANGE-002 are **To be verified** against database/deployment data; they are not established by the inspected source or migrations.

## Current creation state

The creation view assigns the first row returned by `WorkRequestStatus.objects.first()`. No ordering or explicit status lookup is supplied. Therefore, the source code does not guarantee a particular initial lifecycle state.

## Current transitions

- The employer-facing work-request view accepts a status ID without validating it against a transition policy.
- On status ID `2`, it updates all work requests attached to the project: the selected freelancer receives ID `2`; all other requests receive ID `3`.
- For any other integer status ID, it updates the matching project/freelancer request directly.
- The admin update view is a second path and performs its own status updates. On status ID `2`, it assigns ID `2` to the selected freelancer and ID `3` to all other requests for the selected project.
- No transition guard, terminal state, or defined meaning for a review-in-progress state appears in the inspected code.
- The UI offers all status rows as choices; it does not provide a transition policy.

## State and consistency observations

- The model permits nullable project and freelancer references, so lifecycle paths must account for missing relations if they access those objects.
- Approval is implemented as multiple separate saves without an enclosing transaction in either inspected status-update path.
- The source does not lock the project or its requests while approving one.
- The standard work-request view mutates `project.status.id`, not `project.status_id`; persistence of that assignment is not established by this code.
- The admin view writes `project.status_id = 2`; what that project status means is **To be verified**.

## Not established by current source

- Actual configured status rows/IDs in deployed data.
- Whether only one freelancer may be accepted for a project.
- Whether accepted or rejected requests are intended to be terminal.
- The business meaning and trigger for `на розгляді`.
- Whether and when Project status should track a WorkRequest status.
