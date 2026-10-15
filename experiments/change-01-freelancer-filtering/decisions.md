# CHANGE-001 Human Decisions

## HD-001 — Multi-skill selection control

Initial decision:
Use an HTML multi-select control.

Status:
Superseded by HD-006 during implementation UI review.


## HD-002 — Skill matching mode

Decision:
Use an explicit skill matching selector.

Visible options:
- Будь-яка з вибраних
- Усі вибрані

Internal values may remain `any` and `all`.

Status:
Approved.


## HD-003 — Unrated freelancers during rating sorting

Decision:
Freelancers without ratings remain visible and are placed last
for both ascending and descending rating sorting.

Status:
Approved.


## HD-004 — Duplicate freelancer templates

Decision:
Keep the existing user and admin freelancer list templates separate
within CHANGE-001.

Status:
Approved.


## HD-005 — Default ordering

Decision:
Preserve the existing behavior when no explicit sorting option
is selected.

Status:
Approved.


## HD-006 — Skill selection UI refinement

Context:
During implementation review, the native multi-select / chip-based
selection UI was found to be visually awkward and less convenient
for the current server-rendered interface.

Decision:
Replace the previously approved HTML multi-select control with an
always-expanded checkbox list.

Selected skills are controlled directly through checkboxes.

Do not render:
- duplicate selected-skill chips;
- separate remove buttons;
- collapsible skill-selection UI.

The selected-skill count may be displayed separately.

Reason:
The checkbox list is simpler, clearer, and better aligned with the
existing frontend while preserving the approved multi-skill filtering
behavior.

Impact:
Presentation only.

The following behavior remains unchanged:
- multiple skill selection;
- ANY / ALL matching;
- backend request handling;
- filtering semantics;
- acceptance criteria.

This decision supersedes HD-001.

Status:
Approved by Human Reviewer.

## HD-007 — Freelancer filtering stylesheet

Decision:
Approve the addition of `devopssite/static/css/freelancers.css`
as a bounded presentation-only deviation required for CHANGE-001 UI styling.

No unrelated frontend components are included.

Status:
Approved by Human Reviewer.