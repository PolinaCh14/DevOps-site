# TASK-001: Extend freelancer filtering and ordering

Status: Approved

## Objective
Implement the accepted change described in `changes/CHANGE-001-freelancer-filtering.md` by extending the existing freelancer search behavior to support multi-skill selection, ANY/ALL matching, and sorting by experience and average rating while preserving the current non-advanced behavior.

## Current repository evidence
The existing implementation is confirmed in:

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`
- `devopssite/adminpannel/views.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `devopssite/rating/utils.py`
- `devopssite/skill/models.py`

The current code supports single-skill search and rating filtering in a Python-level comparison loop. There is no explicit ordering by experience or average rating, and no automated tests cover the requested behavior.

## Allowed scope
The implementation task is bounded to the following files and concerns:

- freelancer list search view logic in `devopssite/freelancer/views.py`
- admin freelancer list search view logic in `devopssite/adminpannel/views.py` if the same contract is duplicated there
- freelancer list form controls in `devopssite/templates/freelancer_list.html`
- admin freelancer list form controls in `devopssite/templates/freelancer_list_a.html`
- supporting rating and skill utility logic only if required for a queryset-safe implementation
- new or updated automated tests in the relevant Django test module(s)

## Not allowed
The task must not include:

- redesigning the `Freelancer` model
- changing the authentication system
- changing work-request lifecycle logic
- changing AI resume-analysis logic
- modifying unrelated business workflows
- broad refactoring not directly required by the selected change

## Proposed implementation steps
1. Confirm the exact UI control and request parameter contract for multi-skill selection.
2. Add support for multiple selected skills while preserving the existing single-skill case.
3. Add ANY vs ALL matching logic for the skill set.
4. Combine the new skill logic with existing name/status/experience/rating filters.
5. Add explicit ordering by experience and by average rating in both ascending and descending directions.
6. Preserve the old behavior when no new filters or sort options are used.
7. Add focused Django tests for the new search behavior and backward compatibility.

## Acceptance criteria to satisfy
- AC-01 to AC-09 from `cards/specs/SPEC-001-freelancer-filtering.md`

## Required tests
The task requires focused validation of:

- multiple skill selection in a single request;
- ANY matching behavior;
- ALL matching behavior;
- combination of multi-skill filtering with status filter;
- combination with experience filter;
- combination with rating filter;
- sorting by experience ascending and descending;
- sorting by average rating ascending and descending;
- legacy behavior with no advanced filters or sort options.

## Human-approved decisions recorded before implementation
The following decisions were approved by the human reviewer and are now treated as the working contract for this task without marking the implementation as started:

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.
- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.
- OQ-04: keep the existing freelancer list templates separate for this change; do not introduce template refactoring as part of CHANGE-001.
- OQ-05: preserve the current default behavior when no explicit sort option is selected.

Final decision status: Resolved / Human approved.

## Deliverable expectations
The implementation should produce:

- a bounded patch to the freelancer search flow;
- tests that prove the acceptance criteria; 
- no unrelated changes beyond the approved scope.
