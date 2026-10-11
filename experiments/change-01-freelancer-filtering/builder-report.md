# Builder Report

Status: Approved

## Repository State Reviewed
Relevant files inspected for this change include:

- `docs/BASELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/METHODOLOGY.md`
- `docs/TESTING_DEVOPS_BASELINE.md`
- `changes/CHANGE-001-freelancer-filtering.md`
- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`
- `devopssite/freelancer/tests.py`
- `devopssite/freelancer/urls.py`
- `devopssite/skill/models.py`
- `devopssite/rating/models.py`
- `devopssite/rating/utils.py`
- `devopssite/adminpannel/views.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `devopssite/devopssite/urls.py`

## Confirmed Current Behavior
The current repository confirms that freelancer search supports:

- filtering by name or surname;
- filtering by freelancer status;
- filtering by a single skill;
- filtering by experience comparison operators;
- filtering by average rating comparison operators.

The repository also confirms that:

- the user-facing and admin-facing freelancer list views share the same pattern;
- rating-based filtering is calculated in Python after the initial queryset is built;
- there is no explicit `.order_by(...)` call for entrepreneur or rating sorting in the list view;
- the current templates use a single-value `skill` selector and no multi-skill input controls.

## Relevant Dependencies
Relevant models, views, templates, utilities, and modules include:

- `Freelancer` model in `devopssite/freelancer/models.py`
- `FreelancerStatus` model in the same file
- `FreelancerSkill` relation in the same file
- `Skill` model in `devopssite/skill/models.py`
- `Rating` model in `devopssite/rating/models.py`
- `get_average_rating_for_user` in `devopssite/rating/utils.py`
- `freelancer_list` in `devopssite/freelancer/views.py`
- duplicated admin list logic in `devopssite/adminpannel/views.py`
- route registration in `devopssite/freelancer/urls.py`
- root app resourcing from `devopssite/devopssite/urls.py`
- list templates `freelancer_list.html` and `freelancer_list_a.html`

## Risks
The main technical and behavioral risks identified are:

- the current rating filter is list-based rather than queryset-based, which may make query optimization and ordering harder;
- the skill filter is currently singular and therefore incompatible with multi-skill matching without a contract change;
- the code duplicates freelancer search logic in both regular and admin list views, which increases the chance of inconsistent behavior;
- the repository does not yet define the expected UI contract for ANY/ALL matching or multi-select skill input;
- the repository does not confirm how freelancers without ratings should behave during rating sorting or filtering.

## Conflicts
The current repository code and the change request are not in direct contradiction, but they do show the following mismatch to resolve before implementation:

- the current repository supports only one skill and no multi-skill matching mode;
- the change request expects multi-skill ANY/ALL semantics, while current templates and view logic only support a singular skill value;
- the change request expects sorting by experience and average rating, but the repository currently has no explicit ordering established in the list view.

## Human-approved Decisions
The following questions were resolved by human approval and are recorded here as approved decisions for CHANGE-001. The Builder stage for CHANGE-001 is completed and approved; implementation has not started.

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.
- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.
- OQ-04: keep the existing freelancer list templates separate for this change; do not introduce template refactoring as part of CHANGE-001.
- OQ-05: preserve the current default behavior when no explicit sort option is selected.

Final decision status: Resolved / Human approved.

## Proposed Scope
The implementation scope expected to be needed is limited to:

- `devopssite/freelancer/views.py`
- `devopssite/adminpannel/views.py` if the admin list duplicates the same contract
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- any necessary support in `devopssite/rating/utils.py` if the filtering/sorting can be made more queryset-oriented without altering unrelated logic
- relevant Django tests in `devopssite/freelancer/tests.py` or adjacent test modules

## Explicitly Out of Scope
The following are explicitly out of scope for this draft implementation:

- redesign of the `Freelancer` domain model
- authentication or session changes
- work-request lifecycle changes
- AI CV analysis changes
- unrelated project or user workflow refactoring
- introducing a separate external search service
- broader application redesign

## Proposed Test Plan
The test plan should map directly to the accepted criteria from `cards/specs/SPEC-001-freelancer-filtering.md`:

- AC-01: test multiple skill selection in a single request
- AC-02: test ANY matching for at least one selected skill
- AC-03: test ALL matching for all selected skills
- AC-04: test combination with status filter
- AC-05: test combination with experience filter
- AC-06: test combination with rating filter
- AC-07: test experience ordering ascending/descending
- AC-08: test average-rating ordering ascending/descending
- AC-09: test legacy behavior without advanced selection or sorting remains unchanged

## Produced Artifacts
The following draft artifacts were created for review:

- `cards/knowledge/freelancer.md`
- `cards/knowledge/skill.md`
- `cards/knowledge/freelancer-search.md`
- `cards/knowledge/rating.md`
- `cards/specs/SPEC-001-freelancer-filtering.md`
- `cards/tasks/TASK-001-freelancer-filtering.md`
- `experiments/change-01-freelancer-filtering/builder-report.md`
