# CHANGE-001: Advanced Freelancer Filtering and Result Ordering

## 1. Status

Draft

This change has not yet been approved for implementation.

No application code should be modified based on this document alone.

---

## 2. Purpose

Improve the existing freelancer search and filtering functionality without redesigning the current freelancer domain model or unrelated application workflows.

The goal is to make freelancer search more flexible and useful for employers while preserving the existing behavior of the application.

---

## 3. Current State

The current freelancer list supports:

- search by freelancer name or surname;
- filtering by freelancer status;
- filtering by one skill;
- filtering by experience using comparison operators;
- filtering by average rating using comparison operators.

The current implementation uses the existing:

- `Freelancer` model;
- `FreelancerStatus` model;
- `Skill` model;
- `FreelancerSkill` relation;
- `Rating` model.

Current limitations relevant to this change:

- only one skill can be selected at a time;
- there is no explicit result ordering by experience;
- there is no explicit result ordering by average rating;
- rating filtering currently evaluates average rating separately for freelancers after the initial queryset is built;
- automated tests do not currently cover freelancer filtering behavior.

---

## 4. Need

Employers need a more flexible way to narrow down freelancer search results when several technical skills are relevant to a project.

The current single-skill filter is limited for searches where a freelancer may be expected to have several related technical skills.

Search results should also be easier to compare by experience and average rating.

---

## 5. Desired Result

Extend the existing freelancer filtering functionality while preserving current behavior.

The improved freelancer search should support:

- selecting multiple skills;
- matching freelancers by any selected skill;
- matching freelancers by all selected skills;
- sorting results by experience;
- sorting results by average rating;
- combining the new filtering options with existing filters.

Existing filtering behavior must continue to work when the new options are not used.

---

## 6. Functional Requirements

### FR-01: Multiple skill selection

The user must be able to select more than one freelancer skill in a single search request.

### FR-02: ANY skill matching

The user must be able to search for freelancers who have at least one of the selected skills.

Example:

Selected skills:

- AWS
- Terraform
- Docker

In `ANY` mode, a freelancer should match if they have one or more of the selected skills.

### FR-03: ALL skill matching

The user must be able to search for freelancers who have all selected skills.

Example:

Selected skills:

- AWS
- Terraform

In `ALL` mode, only freelancers who have both skills should be returned.

### FR-04: Combined filtering

Multi-skill filtering must remain compatible with the existing filters:

- name / surname;
- freelancer status;
- experience;
- rating.

### FR-05: Experience ordering

The user must be able to order freelancer results by experience:

- ascending;
- descending.

### FR-06: Rating ordering

The user must be able to order freelancer results by average rating:

- ascending;
- descending.

### FR-07: Existing behavior preservation

Existing freelancer filtering behavior must continue to work when the new filtering and ordering options are not used.

---

## 7. Technical Requirements

### TR-01: Existing domain model reuse

The implementation should use the existing:

- `Freelancer`;
- `Skill`;
- `FreelancerSkill`;
- `Rating`;

models unless repository analysis demonstrates that a model change is required.

Model changes must not be introduced without explicit justification and approval.

### TR-02: Query-oriented filtering and ordering

Filtering and ordering should remain database/queryset-oriented where reasonably possible.

Average rating filtering and ordering should not require executing one separate rating aggregation query for every freelancer if the same behavior can be expressed through the Django ORM.

### TR-03: Compatibility

The change must not break existing:

- freelancer profile creation;
- freelancer profile update;
- portfolio functionality;
- rating creation;
- work-request functionality;
- authentication;
- AI CV analysis.

### TR-04: Relevant freelancer list pages

Filtering behavior should remain consistent across relevant freelancer list/search pages that use the same functionality.

---

## 8. Constraints

The implementation must not:

- rewrite the freelancer subsystem;
- redesign the overall application architecture;
- introduce a separate search service;
- modify authentication logic;
- modify work-request lifecycle logic;
- modify AI resume analysis;
- change unrelated models;
- introduce unrelated refactoring without explicit justification.

The change should remain local to freelancer search/filtering functionality and directly related supporting code.

---

## 9. Acceptance Criteria

### AC-01

A user can select multiple freelancer skills in one search.

### AC-02

`ANY` mode returns freelancers having at least one selected skill.

### AC-03

`ALL` mode returns only freelancers having all selected skills.

### AC-04

Multi-skill filtering can be combined with freelancer status filtering.

### AC-05

Multi-skill filtering can be combined with experience filtering.

### AC-06

Multi-skill filtering can be combined with rating filtering.

### AC-07

Freelancer results can be ordered by experience ascending.

### AC-08

Freelancer results can be ordered by experience descending.

### AC-09

Freelancer results can be ordered by average rating ascending.

### AC-10

Freelancer results can be ordered by average rating descending.

### AC-11

Existing name, status, experience, skill, and rating filtering continues to function when the new options are not used.

### AC-12

Automated tests cover the new multi-skill filtering behavior.

### AC-13

Automated tests cover the new ordering behavior.

### AC-14

Regression tests cover the existing freelancer filtering behavior affected by this change.

### AC-15

Average rating filtering and ordering does not require one separate rating aggregation query per freelancer in the final result set.

---

## 10. Out of Scope

The following are explicitly outside this change:

- pagination;
- freelancer profile redesign;
- AI-based freelancer recommendations;
- AI-based skill matching;
- changes to the work-request workflow;
- authentication changes;
- general UI redesign;
- project filtering;
- notification changes;
- Docker implementation;
- CI/CD implementation;
- broad refactoring of unrelated modules.

These items may be handled in separate future changes.

---

## 11. Known Relevant Components

The following components are currently known to be relevant:

- `freelancer/views.py`;
- `freelancer/models.py`;
- `freelancer/tests.py`;
- freelancer list/search templates;
- `skill/models.py`;
- `rating/models.py`;
- `rating/utils.py`.

This list identifies currently known dependencies.

It does not automatically define the final allowed modification scope.

The Builder must confirm the actual dependency and modification scope during repository analysis.

---

## 12. Verification Expectations

The implementation should be verifiable through:

- automated tests;
- mapping between acceptance criteria and tests;
- documented test commands;
- recorded test results;
- implementation diff;
- repository commit SHA;
- independent Reviewer assessment.

Manual UI verification may be used as additional evidence but should not replace automated verification of core filtering behavior.

---

## 13. Open Questions

The following questions should be resolved before implementation if they affect user-visible behavior:

### OQ-01: Skill selection UI

How should multiple skills be selected?

Possible options include:

- multi-select control;
- checkboxes;
- another UI element consistent with the existing application.

### OQ-02: ANY / ALL selection

How should the user choose between `ANY` and `ALL` skill matching?

### OQ-03: Freelancers without ratings

When sorting by average rating, how should freelancers without ratings be handled?

Possible options include:

- always placed last;
- always placed first;
- excluded from rating-sorted results.

### OQ-04: Duplicate freelancer list templates

Should the existing freelancer list/search templates remain separate, or should shared filtering UI be extracted?

This should only be changed if required by the approved implementation scope.

### OQ-05: Default ordering

The current default result ordering should be identified and preserved unless a different default is explicitly approved.

---

## 14. Traceability References

This change defines the initial need, requirements, constraints, and acceptance criteria for the first agent-driven development cycle.

Detailed methodology, agent responsibilities, approval gates, evidence requirements, and the full traceability process are defined in:

`docs/METHODOLOGY.md`

The next artifacts expected for this change are:

- relevant knowledge / contract cards;
- `SPEC-001-freelancer-filtering.md`;
- bounded implementation task prepared by the Builder.