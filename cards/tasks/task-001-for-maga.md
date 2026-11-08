# TASK-001: Extend freelancer filtering and ordering

**Status:** Approved  
**Specification:** `cards/specs/SPEC-001-freelancer-filtering.md`  
**Change request:** `changes/CHANGE-001-freelancer-filtering.md`  
**Implementation role:** Implementer  
**Verification role:** Reviewer

## 1. Objective

Extend the existing freelancer search functionality to support:

- Multiple skill selection.
- ANY / ALL skill matching.
- Sorting by experience (ascending / descending).
- Sorting by average rating (ascending / descending).
- Preservation of existing search behavior when advanced options are not selected.

## 2. Current Repository Context

The existing functionality is located in the following components:

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`
- `devopssite/adminpannel/views.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `devopssite/rating/utils.py`
- `devopssite/skill/models.py`

The current implementation supports single-skill searching and rating filtering. Explicit ordering by experience and average rating is not implemented, and automated tests for the requested behavior are absent.

## 3. Approved Scope

The Implementer is allowed to modify:

- Freelancer search logic in `freelancer/views.py`.
- Related admin search logic in `adminpannel/views.py`, if required.
- Freelancer list templates.
- Supporting skill and rating utilities, if necessary.
- Relevant Django automated tests.

The following changes are not allowed without additional approval:

- Redesigning the `Freelancer` model.
- Modifying authentication or work-request workflows.
- Changing AI resume-analysis functionality.
- Refactoring unrelated components.

## 4. Implementation Tasks

1. Implement multiple skill selection using an always-expanded checkbox list.
2. Preserve selected checkbox values after form submission.
3. Implement ANY / ALL skill matching.
4. Integrate the new logic with existing search filters.
5. Add sorting by experience and average rating.
6. Place freelancers without ratings last in both rating sort directions.
7. Preserve existing default search behavior.
8. Add automated tests for the new functionality.

## 5. Acceptance Criteria

The implementation must satisfy **AC-01–AC-09** defined in:

`cards/specs/SPEC-001-freelancer-filtering.md`

Required verification includes:

- Multi-skill selection.
- ANY / ALL matching.
- Combined filtering by status, experience and rating.
- Ascending and descending sorting.
- Correct handling of freelancers without ratings.
- Backward compatibility with existing search behavior.
- Compliance with the approved scope.

## 6. Human-Approved Decisions

The following decisions were approved before implementation:

- **OQ-02:** Explicit ANY / ALL selector.
- **OQ-03:** Freelancers without ratings appear last in both sorting directions.
- **OQ-04:** Existing freelancer list templates remain separate.
- **OQ-05:** Existing default behavior is preserved.

**HD-006 — Approved amendment**

The original HTML multi-select decision (OQ-01) was superseded.

Final approved UI:

- Always-expanded checkbox list.
- Selected state preserved after submission.
- No chips or remove buttons.

Reference: `experiments/change-01-freelancer-filtering/decisions.md`

## 7. Expected Deliverables

The Implementer must provide:

- Source code changes within the approved scope.
- Automated tests covering acceptance criteria.
- A Git commit identifying the implementation.
- A list of modified files.
- Executed test commands and their results.
- Known limitations or unresolved issues.

The implementation is then submitted to Reviewer for independent verification against the approved specification.