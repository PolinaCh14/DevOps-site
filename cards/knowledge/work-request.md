Status: Approved

# Work Request — Current Repository Facts

## Scope

This card records confirmed behavior in the repository reviewed for CHANGE-002. It does not define desired future behavior.

## Models and relationships

- `WorkRequestStatus` stores a `status` string with maximum length 20.
- `WorkRequest` has a required foreign key to `WorkRequestStatus`.
- `WorkRequest` has nullable foreign keys to `Freelancer` and `Project`; both are configured with `SET_NULL`.
- `WorkRequest.created_at` is a date field.
- The work-request migration history shown in the repository creates these tables and later makes the freelancer and project links nullable. No lifecycle constraints or project/freelancer uniqueness constraint are declared there.

## Creation

- The authenticated `create_work_request` view resolves a `Freelancer` for the current user.
- Before creating a request, it searches for an existing request with the same project and freelancer. If found, it reports an error message and redirects.
- Otherwise, it assigns `WorkRequestStatus.objects.first()` as the initial status. The initial state therefore depends on database ordering.
- If there are no status rows, the view reports an error and does not create the request.
- The view creates the request with the current date and redirects after reporting success.
- The check and create are separate operations; the repository does not enforce uniqueness at the database level.

## Listing and filtering

- The freelancer listing resolves the current user's freelancer record and lists that freelancer's requests. A `status` query parameter filters by status ID.
- The employer listing starts from projects owned by the current user, then lists requests whose project belongs to that set. A `status` query parameter filters by status ID.
- Both listings pass all `WorkRequestStatus` rows to the shared template.

## Status updates

- The work-request status route accepts `project_id` and `freelancer_id`; the status-changing branch handles POST requests.
- It parses a submitted `status_id` as an integer and returns a bad-request response for missing or non-integer values.
- It fetches the project by ID, but does not verify that the authenticated user owns it.
- When submitted status ID is `2`, that handler loops through every request for the project, sets the matching freelancer's request to the submitted ID, and assigns ID `3` to every other request. It saves every row.
- In this handler, assigning `project.status.id = 2` does not assign the project's foreign-key field. The repository code does not establish that this changes the persisted project status.
- For other submitted status IDs, the handler changes the matching project/freelancer request without checking whether the transition is allowed.
- A second status-edit path exists in `adminpannel.views.update_work_request`. It accepts status and project values, can alter a request's project, and on status ID `2` updates all requests for that project, assigning ID `2` to the selected freelancer and ID `3` to the others. It also sets the project's `status_id` to `2`. This path is protected by login, but this view does not establish project-owner authorization.
- The admin edit path and the work-request handler are separate routes and have different details of their approval behavior.
- Status labels and the mappings `1=очікує`, `2=схвалено`, `3=відхилено`, `4=на розгляді` are not defined in the inspected model or work-request migrations. Their actual database values are **To be verified**.
- No server-side transition matrix or terminal-state rule is present in the inspected work-request model/views.

## Direct status consumers

- `project.views.user_projects_search_view` filters accepted requests using status ID `2`.
- `rating.views` also filters work requests using status ID `2`.
- The work-request views, templates, and admin paths use status IDs for filtering or update selection.
- The meaning of status ID `2` in production data is **To be verified**.

## Known limitations

- Initial status depends on the first status row.
- Duplicate prevention is an application-level check without a database uniqueness constraint or a single atomic check-and-create operation.
- Status IDs are used directly in business behavior.
- The ordinary employer update path does not confirm project ownership.
- Separate update paths can produce different project/request effects.
- Status updates do not validate transition eligibility.

## Repository evidence

- `devopssite/workrequest/models.py`
- `devopssite/workrequest/views.py`
- `devopssite/workrequest/urls.py`
- `devopssite/workrequest/migrations/0001_initial.py`
- `devopssite/workrequest/migrations/0002_alter_workrequest_id_freelancer_and_more.py`
- `devopssite/project/views.py`
- `devopssite/adminpannel/views.py`
- `devopssite/rating/views.py`
- `devopssite/templates/freelancer-work-request.html`
