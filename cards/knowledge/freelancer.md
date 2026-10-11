# Freelancer Knowledge / Contract Card

Status: Approved

## Purpose
This card records the current repository evidence for the `Freelancer` domain object and the filters currently associated with freelancer search.

## Current model contract
The `Freelancer` model in `devopssite/freelancer/models.py` currently defines:

- `id_user`: foreign key to the application user model.
- `id_status`: foreign key to `FreelancerStatus`.
- `cv`: optional string field.
- `experience`: nullable integer field.

The same file also defines `FreelancerSkill` and `Portfolio`.

`FreelancerSkill` joins a freelancer to a skill via:

- `id_freelancer` -> `Freelancer`
- `id_skill` -> `skill.Skill`

`Portfolio` links to a freelancer via `id_freelancer` and includes a title, photo, description, and url.

## Current behavior
The repository confirms these freelancer-related flows:

- create freelancer profile: `freelancer/views.py` exposes `create_freelancer_profile`.
- update freelancer profile: `freelancer/views.py` exposes `update_freelancer_profile`.
- detail view: `freelancer/views.py` exposes `freelancer_detail` and `user_freelancer_detail`.
- portfolio CRUD flows: `freelancer/views.py` contains portfolio create/update/delete handlers.
- skill selection on profile create/update: `request.POST.getlist('skills')` is used to store selected skill ids in `FreelancerSkill` rows.

## Current search/filter contract
The freelancer list view in `devopssite/freelancer/views.py` builds a queryset from `Freelancer.objects.select_related('id_user', 'id_status').all()` and applies filters from `request.GET`:

- `name`: filters by user `name` or `surname` using `icontains`.
- `status`: filters by `id_status_id`.
- `skill`: filters by a single `id_skill_id` using `FreelancerSkill` values.
- `experience`: filters by comparison operators (`lt`, `lte`, `eq`, `gte`, `gt`).
- `rating`: filters by average rating using a Python-level comparison against `get_average_rating_for_user(...)`.
- `rating_filter`: comparison operator for rating.

The same logic is duplicated in the admin list view in `devopssite/adminpannel/views.py` and rendered with `templates/freelancer_list_a.html`.

## Current ordering contract
The current repository does not show an explicit queryset ordering for the freelancer list.

- `freelancer_list` does not call `.order_by(...)`.
- the default database ordering is therefore not explicitly defined in code.
- `default ordering behavior`: preserve the current default behavior when no explicit sort option is selected.

## Known limitations
The current implementation includes the following confirmed limitations:

- only one skill can be selected in the list form because the template uses a single `select` element with name `skill`.
- rating filtering is applied after the initial queryset is constructed and uses a list comprehension rather than a queryset annotation.
- there is no explicit ordering by experience in the view.
- there is no explicit ordering by average rating in the view.
- automated tests in `devopssite/freelancer/tests.py` cover profile/detail flows, but not the advanced filtering and ordering behavior described in `changes/CHANGE-001-freelancer-filtering.md`.

## Human-approved decisions
The following decisions were approved by the human reviewer for CHANGE-001 and are recorded here without implementation start:

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.
- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.
- OQ-04: keep the existing freelancer list templates separate for this change; do not introduce template refactoring as part of CHANGE-001.
- OQ-05: preserve the current default behavior when no explicit sort option is selected.

These decisions resolve the earlier uncertainty around the filtering contract and the default ranking policy; they do not mark the implementation as started.

Final decision status: Resolved / Human approved.

## Evidence summary
This card is based on the repository files:

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`
- `devopssite/freelancer/tests.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `changes/CHANGE-001-freelancer-filtering.md`
