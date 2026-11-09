# TASK-003 — Structured AI Resume Analysis

Status: Approved
Implementation-ready: Yes

The human has approved this task and SPEC-003. Implementation may proceed in a
separate Implementer session, strictly within the allowed files and behavior
below. This approval does not authorize scope expansion.

## Objective

Implement the approved structured resume-analysis flow in the existing
freelancer profile owner workflow. Keep Google Drive as the source, accept
only valid DOCX/PDF files, validate the exact five-field qualitative AI
response, render it safely, and implement the error/retry/access contract
defined in SPEC-003.

## Approved decisions reflected in this task

- Exactly five required top-level result keys: `summary`, `detected_skills`,
  `strengths`, `improvement_areas`, and `recommendations`.
- No numeric score, dimension scores, confidence, or ranking values.
- Raw AI output is transient only and is never persisted or logged in full.
- Invalid/malformed/incomplete output is rejected with no partial success.
- Exactly one additional repair attempt is allowed only after a response is
  received and fails JSON/schema validation.
- Google Drive retrieval failure stops before AI; no automatic retry or
  fallback source/file.
- Extraction failure or empty/whitespace text stops before AI.
- No OCR, conversion, or file types other than DOCX/PDF.
- Analysis is on-demand only; no result persistence, cache, history, or
  previous-result fallback. OQ-09 is Not Applicable.
- Only the authenticated owner of the associated Freelancer profile may
  trigger/view analysis; no new role check or employer/admin access.
- Google Drive remains the source; narrow retrieval correctness/error-handling
  fixes are allowed.
- Provider timeout/network/service failure returns a controlled,
  non-sensitive failure with no automatic retry. Manual retry is user-triggered.

## Allowed files

Only the following files may be modified for implementation:

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/freelancer/tests.py`

No model or migration change is allowed or required. Do not change
`Freelancer.cv`, global authentication, settings/configuration, dependencies,
Docker/environment files, unrelated templates, or other AI features. If a
blocking issue requires another file, stop and request explicit scope approval
before modifying it.

## Required implementation contract

Implement all target behaviors and exact bounds, JSON shape, safe messages,
HTTP statuses, error codes, retries, and rendering rules from SPEC-003,
including:

1. Correctly identify and validate Drive response content as DOCX or PDF,
   preserve a type-appropriate local extension for extraction, reject
   unsupported/mismatched content, use a 5-second connect and 30-second read
   timeout for Drive requests, and check HTTP status before processing.
   Require PDF `%PDF-` signature within the first 1,024 bytes or a valid DOCX
   ZIP/OOXML package containing `[Content_Types].xml` and
   `word/document.xml`. A recognized non-generic MIME type or filename
   extension conflicting with content is invalid; generic
   `application/octet-stream` is neutral.
2. Stop before AI on Drive retrieval errors, parser failures, or empty/
   whitespace-only text. Do not automatically retry Drive or provider
   network/service failures; do not use a fallback source/file.
   The existing Drive `download_warning` confirmation request remains part
   of the download protocol and is not a failure retry.
3. Request and validate exactly the approved five-key JSON schema. Enforce
   exact top-level and nested keys, strict JSON parsing, trimming, type,
   emptiness, control-character, item-count, string-length, and duplicate
   rules. Prompt for Ukrainian prose (skill names may retain standard
   spelling), concise paraphrased evidence grounded in the resume, no
   fabricated quotes/details, document-based improvement areas, and
   actionable recommendations.
4. Allow exactly one additional repair call only after a successfully
   received but malformed/schema-invalid response. If it remains invalid,
   return the specified controlled failure and no analysis payload.
   Configure a 30-second provider timeout and disable SDK automatic retries
   (`max_retries=0` or equivalent).
5. Enforce authenticated owner-only access server-side by resolving the
   profile from `request.user`; do not accept a profile selector or add a new
   role-ID check.
6. Return only the specified success or error JSON contracts for POST. Do not
   expose exception text, secrets, CV text, or raw model output.
7. Render model-derived strings as text using safe DOM APIs; never interpret
   them as HTML or Markdown.
8. Persist/cache neither structured results nor raw responses; do not log full
   CV text or full raw model output.
9. Keep the implementation limited to the four allowed files and preserve
   unrelated behavior.

## Required tests

Implement the SPEC-003 test strategy, including:

- mocked successful DOCX/PDF retrieval and correct parser selection;
- invalid/mismatched/unsupported file, Drive HTTP/network/timeout failures,
  and assertions of zero AI calls, zero fallback, and zero retry;
- PDF/DOCX parser errors and empty/whitespace extraction with zero AI calls;
- valid schema and all key/type/shape/limit/duplicate/extra-key failure cases,
  including boundary and one-over-boundary values;
- exact repair retry counts: valid first response (one call), invalid then
  valid (two calls), two invalid responses (two calls then failure), and
  provider failures (no automatic retry);
- auth, profile ownership, missing profile, missing CV, and unsupported
  method behavior;
- exact HTTP status, JSON shape, code, message, and absence of raw exception
  detail for every failure category;
- rendering safety with HTML-looking model strings and checks that no
  model-derived HTML/Markdown interpretation is used;
- no result persistence/cache and fresh work on each explicit trigger; and
- regression tests for existing freelancer behavior.

All Drive and model calls must be mocked. No live external requests,
credentials, or real CV documents are permitted in automated tests.

## Acceptance criteria mapping

| AC | Verification |
|---|---|
| AC-01: Supported DOCX/PDF retrieval and type validation | Mock successful metadata/content for both types; assert correct parser. Mock invalid, mismatched, and unsupported content; assert no AI call. |
| AC-02: Retrieval failures | Mock timeout, network error, HTTP failure, and invalid download; assert no extraction/AI as applicable, no retry/fallback, and exact 502 safe error. |
| AC-03: Extraction failures/empty text | Mock parser exception and empty/whitespace text; assert no AI call and exact 422 error. |
| AC-04: Valid structured response | Assert exact five keys, no score/extra key, types, limits, trimming, and normalized duplicate rules. |
| AC-05: Invalid AI response | Cover JSON/schema invalidity and boundary violations; assert exactly one repair attempt, then exact failure on second invalid result, never partial success. |
| AC-06: Provider failure | Mock timeout and service/configuration errors on initial and repair requests; assert no network retry and exact 504/503 response with no raw details. |
| AC-07: Access control | Assert unauthenticated GET redirect, unauthenticated POST 401, owner access, no-profile GET/POST behavior, and no cross-profile selection/access. |
| AC-08: Safe rendering | Assert model output is inserted only as text and HTML-like payloads do not create elements/markup. |
| AC-09: No persistence | Verify no result model/file/cache/history is written and each user-triggered request performs fresh analysis. |
| AC-10: Isolated verification/regression | Run focused freelancer tests with external calls mocked; run applicable Django checks and record output. |
| AC-11: Scope | Review diff; only the four allowed files are modified, unless separate scope approval was obtained first. |

## Explicitly out of scope

- Replacing Google Drive or adding another storage provider.
- Broad freelancer-profile redesign or changing CV storage/reference contract
  except a minimal parsing fix.
- General AI matching/recommendations or employer ranking.
- Unrelated prompt engineering.
- Global authentication changes, role checks, or employer/admin access.
- Unrelated frontend modernization.
- CI/CD or deployment redesign.
- OCR, scanned documents, conversion, or non-PDF/DOCX formats.
- Persistence, caching, history, stale-result logic, or raw output storage.
- Automatic retrieval or provider/network retry.
- New dependency, migration, or settings/configuration changes.

## Completion evidence expected

Report actual changed files, focused test commands/results, acceptance
criterion-to-test mapping, mock coverage, HTTP/error behavior, and residual
risks. Do not commit or claim acceptance; those are separate workflow stages.
