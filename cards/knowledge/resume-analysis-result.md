# Resume Analysis Result / Rendering Contract

Status: Draft

## Purpose

Document how the current resume-analysis response travels from service to
browser, including persistence, rendering, and access boundaries.

## Current result contract

The `analyze_resume` service returns the first AI choice's message content as
a free-form string. It does not persist the response or any extracted text.

For POST requests, `analyze_resume_view`:

- resolves the `Freelancer` whose `id_user` is the current user;
- returns status 400 and `{"error": "CV не знайдено."}` if its `cv` is falsey;
- calls the analysis service;
- converts returned text from Markdown to HTML with the `fenced_code`
  extension; and
- returns status 200 with `{"analysis": "<rendered HTML>"}`.

There is no stored structured result, timestamp, source fingerprint, or stale
result policy.

## Current template behavior

`devopssite/templates/analyze_resume.html` presents an analysis button when
`has_cv` is true. Its JavaScript posts to the current page with a CSRF header,
parses JSON, and puts a successful `analysis` value into `resultDiv.innerHTML`.
For an error response it displays `data.error` using `textContent` and colors
the result red.

The template does not currently render a structured schema. The Markdown
conversion call does not show a sanitization step before the HTML is inserted.
The effect of arbitrary provider-produced markup is therefore a security and
rendering concern; this card does not assert a tested exploit.

## Current errors and fallback

- Missing CV: status 400, Ukrainian error JSON.
- Any exception in the POST analysis path: status 500 with `str(e)` in error
  JSON; the template displays that text.
- No cached or previously successful analysis is returned on a failure.
- No explicit user-facing loading, timeout, retry, or stale-result behavior is
  implemented in the inspected page.
- Non-POST requests follow the page-rendering path; the view has no explicit
  method-not-allowed response.

## Current authorization

The view is decorated with `login_required`. The analysis route has no
freelancer ID parameter and queries the current user's own freelancer profile,
so one authenticated caller cannot select a different profile through this
endpoint. If a caller has no profile, `get_object_or_404` returns not found.
There is no explicit role check in the view. The `user_menu.html` link is
conditionally shown for role ID 2, but a hidden menu link is not server-side
role authorization.

The login decorator's unauthenticated behavior is Django's configured login
redirect; `LOGIN_URL` is `/users/login/`.

## Relevant tests

`devopssite/freelancer/tests.py` tests freelancer profile creation, update,
and detail behavior, but contains no resume-analysis endpoint, result contract,
rendering, persistence, or authorization tests for this feature.

## CHANGE-003 constraints

Any structured response shape, HTML/JSON rendering decision, raw-response
retention, persistence, error UX, and permitted user roles remain subject to
human approval. See SPEC-003 OQ-03, OQ-04, OQ-08 through OQ-10, and OQ-12.

## Evidence

- `devopssite/freelancer/views.py`
- `devopssite/freelancer/urls.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/templates/user_menu.html`
- `devopssite/freelancer/tests.py`
- `devopssite/devopssite/settings.py`
