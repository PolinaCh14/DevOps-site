# SPEC-001: Freelancer Filtering and Result Ordering

Status: Approved

## 1. Purpose
This specification defines the expected future behavior for the draft change described in `changes/CHANGE-001-freelancer-filtering.md`.

The purpose is to extend the current freelancer search and filtering behavior while preserving existing behavior that is already implemented in the repository.

## 2. Current repository evidence
The current repository shows that freelancer search already supports:

- filtering by name or surname;
- filtering by freelancer status;
- filtering by a single skill;
- filtering by experience comparison;
- filtering by average rating comparison.

This behavior is implemented in `devopssite/freelancer/views.py` and duplicated in `devopssite/adminpannel/views.py` for the admin list view.

The form controls are currently implemented as single-value filters in `devopssite/templates/freelancer_list.html` and `devopssite/templates/freelancer_list_a.html`.

## 3. Functional requirements
### FR-01: Multiple skill selection
The system must allow more than one freelancer skill to be selected in a single search request.

### FR-02: ANY skill matching
When multiple skills are selected, the user must be able to search for freelancers who match at least one selected skill.

### FR-03: ALL skill matching
When multiple skills are selected, the user must be able to search for freelancers who match all selected skills.

### FR-04: Combined filters
The multi-skill filter must remain compatible with the existing filters for:

- name/surname
- freelancer status
- experience
- rating

### FR-05: Experience ordering
The user must be able to sort freelancer results by experience in ascending or descending order.

### FR-06: Rating ordering
The user must be able to sort freelancer results by average rating in ascending or descending order.

### FR-07: Backward compatibility
When the new filtering and ordering options are not used, the existing behavior must remain unchanged.

## 4. Technical constraints
The implementation should remain within the current freelancer domain model and search flow unless repository analysis proves another approach is required.

The change should:

- reuse `Freelancer`, `FreelancerSkill`, `Skill`, and `Rating` as currently modeled;
- avoid introducing a new search service;
- avoid redesigning unrelated application workflows;
- keep filtering and ordering as database/queryset-oriented as reasonably possible.

## 5. Draft acceptance criteria
### AC-01
A user can select multiple freelancer skills in one search.

### AC-02
ANY mode returns freelancers who have at least one selected skill.

### AC-03
ALL mode returns only freelancers who have all selected skills.

### AC-04
Multi-skill filtering works together with freelancer status filtering.

### AC-05
Multi-skill filtering works together with experience filtering.

### AC-06
Multi-skill filtering works together with rating filtering.

### AC-07
The results can be ordered by experience ascending or descending.

### AC-08
The results can be ordered by average rating ascending or descending.

### AC-09
When the new options are not selected, current search behavior remains intact.

## 6. Human-approved decisions recorded for this draft
The following decisions were approved by the human reviewer and are recorded here for implementation planning without starting the implementation itself:

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.
- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.
- OQ-04: keep the existing freelancer list templates separate for this change; do not introduce template refactoring as part of CHANGE-001.
- OQ-05: preserve the current default behavior when no explicit sort option is selected.

These are human-approved requirements for the upcoming implementation but do not start the implementation work.

Final decision status: Resolved / Human approved.

## 7. Expected implementation boundary
The implementation should remain local to the freelancer search/filtering flow and directly related templates and utilities.

This includes:

- freelancer list view logic;
- admin list view logic if it duplicates the same contract;
- list form controls and GET parameter handling;
- any required utility logic for rating aggregation or ordering.

## 8. Explicitly out of scope for this draft
This draft does not include:

- redesign of the `Freelancer` model;
- unrelated application refactoring;
- user authentication changes;
- work-request workflow changes;
- rating creation workflow changes;
- AI CV analysis changes;
- broader project search redesign.

## 9. Verification expectation
Implementation should be verified through focused tests covering the new multi-skill logic and ordering logic and the unchanged legacy filter behavior.

The tests must confirm both the new acceptance criteria and the compatibility requirements described in `changes/CHANGE-001-freelancer-filtering.md`.
