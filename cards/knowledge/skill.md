# Skill Knowledge / Contract Card

Status: Approved

## Purpose
This card records the current repository evidence for the `Skill` domain model and how skill data is used in freelancer-related filtering.

## Current model contract
The `Skill` model in `devopssite/skill/models.py` currently defines:

- `skill`: `models.CharField(unique=True, max_length=20)`

This means the repository currently treats the skill name as a unique value and stores it in a dedicated `skill` table.

## Join model contract
The repository also defines `FreelancerSkill` in `devopssite/freelancer/models.py`.

`FreelancerSkill` maps a freelancer to a skill using:

- `id_freelancer`: foreign key to `Freelancer`
- `id_skill`: foreign key to `Skill`

The `Freelancer` profile creation and update flows both read `Skill.objects.all()` and then create or remove rows in `FreelancerSkill` based on `request.POST.getlist('skills')`.

## Current skill selection behavior
In the freelancer list views (`devopssite/freelancer/views.py` and `devopssite/adminpannel/views.py`):

- the form loads skill options from `Skill.objects.all()`;
- the GET parameter used in the view is `skill` (singular);
- the filter compares `id_skill_id=skill_id` to a single selected skill id;
- the queryset is filtered via `FreelancerSkill.objects.filter(id_skill_id=skill_id).values_list('id_freelancer', flat=True)`.

The templates `devopssite/templates/freelancer_list.html` and `devopssite/templates/freelancer_list_a.html` use a single `select` control for `name="skill"` with no multi-select element and no ANY/ALL selector.

## Current limitations
This matches the repository evidence that the search flow currently supports only a single selected skill at a time.

The change request in `changes/CHANGE-001-freelancer-filtering.md` describes this as a limitation to be extended.

## Human-approved decisions
The following decisions were approved by the human reviewer for CHANGE-001 and are recorded here without implementing the change yet:

- OQ-01: use an HTML multi-select for multiple skill selection.
- OQ-02: use an explicit ANY / ALL selector with a clear default value.

These decisions resolve the earlier uncertainty about the skill-selection UI, but the implementation itself is still pending and the artifact remains Draft.

## Evidence summary
This card is based on the following repository files:

- `devopssite/skill/models.py`
- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/freelancer_list.html`
- `devopssite/templates/freelancer_list_a.html`
- `changes/CHANGE-001-freelancer-filtering.md`
