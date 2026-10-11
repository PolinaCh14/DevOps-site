# Freelancer Search Knowledge / Contract Card

Status: Approved

## Purpose
This card records the current freelancer search behavior revealed by the repository and identifies the contract that the upcoming filtering change must respect.

## Search entry points
The repository contains two relevant list views:

- user-facing: `devopssite/freelancer/views.py` -> `freelancer_list`
- admin-facing: `devopssite/adminpannel/views.py` -> `freelancer_list`

Both use the same search/filter pattern and render:

- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`

The URL configuration is defined in `devopssite/freelancer/urls.py` and root routes in `devopssite/devopssite/urls.py`.

## Current filter contract
The search form in both templates supports:

- name or surname input (`name`)
- freelancer status select (`status`)
- single skill select (`skill`)
- experience numeric input (`experience`)
- experience comparator (`experience_filter`)
- rating numeric input (`rating`)
- rating comparator (`rating_filter`)

The corresponding Django view logic applies these values from `request.GET` in sequence to the queryset or list-based result set.

## Current rating filtering behavior
The repository evidence shows that average rating filtering is handled in `freelancer/views.py` by computing the current user rating from `rating.utils.get_average_rating_for_user` and comparing it in Python.

The code path is:

- query `Freelancer.objects.select_related(...)`
- for each freelancer, evaluate `get_average_rating_for_user(f.id_user.id)`
- compare against the selected threshold using a lambda mapping
- include the freelancer only when `raw is not None` and the comparison passes

This means rating filtering is not implemented as a queryset annotation and is therefore a list-based filter after the initial queryset is built.

## Current result ordering
The current implementation does not contain an explicit `.order_by(...)` call for the freelancer list.

This means the repository does not confirm: 

- ascending/descending order by experience; 
- ascending/descending order by average rating; 
- a default ordering policy when no explicit ordering is requested.

## Relevant invariants
From the repository evidence:

- the search flow is queryset-driven for the initial collection and name/status/skill fields;
- rating filtering is evaluated in Python after queryset building;
- the skill filter currently expects exactly one selected skill value;
- the templates are duplicated rather than shared through a single component.

## Human-approved decisions
The following decisions were approved by the human reviewer for CHANGE-001 and are recorded here without implementation start:

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.
- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.
- OQ-04: keep the existing freelancer list templates separate for this change; do not introduce template refactoring as part of CHANGE-001.
- OQ-05: preserve the current default behavior when no explicit sort option is selected.

These decisions resolve the earlier uncertainty around search UX, sorting behavior, and template scope; they do not mark the implementation as started.

## Evidence summary
This card is based on the repository files:

- `devopssite/freelancer/views.py`
- `devopssite/adminpannel/views.py`
- `devopssite/freelancer/urls.py`
- `devopssite/devopssite/urls.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `changes/CHANGE-001-freelancer-filtering.md`
