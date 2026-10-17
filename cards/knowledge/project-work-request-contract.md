Status: Approved

# Project / Work Request Contract — Current Repository Facts

## Relationships

- `Project.user` references the configured user model and is required.
- `Project.status` references `project.Status`; this status has a text field.
- `WorkRequest.id_project` references `Project` but is nullable and uses `SET_NULL`.
- `WorkRequest.id_freelancer` is likewise nullable and uses `SET_NULL`.

## Ownership and authorization

- The employer listing scopes projects by `user_id=request.user.id`, then lists requests attached to those projects.
- The work-request status-change route is login-protected and fetches the target project by its ID. It does not compare `project.user_id` with the current user's ID before changing requests.
- The admin work-request edit route is login-protected, but its view does not show project-owner authorization. It also allows changing the request's project.
- The repository evidence does not establish whether a separate role-based middleware or permission layer restricts those routes. **To be verified**; it does not replace an explicit ownership check in the status-change operation.

## Current synchronization behavior

- The work-request status handler attempts to set the project's status by assigning `project.status.id = 2`; it does not assign the foreign-key field.
- The admin edit handler explicitly sets the selected project's `status_id` to `2` when approving.
- The Project status model defines only a text field; no mapping between Project status and WorkRequest status is represented by the inspected model.
- Project status row values and the business meaning of ID `2` are **To be verified**.

## Known contract gaps

- No confirmed one-accepted-freelancer domain constraint exists in the models/migrations.
- There is no shared lifecycle operation evident between the standard work-request endpoint and the admin edit endpoint.
- The authorization guarantee for status updates is absent from these view implementations.
- A future target synchronization rule requires human approval; this card does not imply one.
