# Rating Knowledge / Contract Card

Status: Approved

## Purpose
This card summarizes the current repository evidence for how ratings are stored and how average rating values are derived for freelancer filtering and display.

## Current model contract
The `Rating` model in `devopssite/rating/models.py` currently defines:

- `id_evaluates`: user being evaluated
- `id_appraiser`: user who created the rating
- `id_project`: project associated with the rating
- `rating`: decimal field with `max_digits=3` and `decimal_places=2`

The model is persisted in the `rating` table via `db_table = 'rating'`.

## Current average-rating utility
The repository utility in `devopssite/rating/utils.py` implements:

- `get_average_rating_for_user(user_id)`
- uses `Rating.objects.filter(id_evaluates_id=user_id).aggregate(avg_rating=Avg('rating'))`
- returns the aggregated `avg_rating` value

This is the only visible utility used to calculate freelancer average ratings across the app.

## Current usage in freelancer views
The freelancer detail and freelancer list views call this utility to evaluate each freelancer's average rating.

Repository evidence:

- `devopssite/freelancer/views.py` calls `get_average_rating_for_user(f.id_user.id)` in the list view.
- `freelancer_detail` computes `raw_rating = get_average_rating_for_user(int(freelancer.id_user.id))`.
- admin list/detail views also call the same utility.

## Current behavior when no ratings exist
The utility returns the result of `Avg('rating')` over matching rows. If no rating rows exist for a user, the aggregate returns `None` in Django ORM semantics.

The list filtering code explicitly checks `is not None` before comparing the retrieved raw value:

- `if (raw := get_average_rating_for_user(f.id_user.id)) is not None and ops[...] (raw)`

This means freelancers without ratings are currently excluded from rating-based filtering when a rating comparison is requested.

## Known limitations
The current repository shows these limitations relevant to the change request:

- rating filtering is performed outside the ORM query pipeline;
- there is no explicit average-rating ordering in the list view;
- there is no explicit handling policy for missing ratings in sorting; 
- no dedicated tests cover rating-based list ordering or filtering.

## Human-approved decisions
The following decisions were approved by the human reviewer for CHANGE-001 and are recorded here without implementation start:

- OQ-03: freelancers without ratings remain visible during rating sorting and are placed last in both ascending and descending rating order.

This resolves the earlier uncertainty about the behavior for unrated freelancers during rating-based sorting; the implementation itself remains pending and the card stays Draft.

## Evidence summary
This card is based on the repository files:

- `devopssite/rating/models.py`
- `devopssite/rating/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/adminpannel/views.py`
- `devopssite/freelancer/tests.py`
- `changes/CHANGE-001-freelancer-filtering.md`
