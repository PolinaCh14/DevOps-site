# CHANGE-003 Decisions

Status: Draft

## Decision record state

OQ-01 through OQ-12 are resolved by explicit human decisions. This record
captures those decisions and the implementation details needed to make the
approved direction testable. This decision record remains a Draft working
record; SPEC-003 and TASK-003 were subsequently approved by the human.

## Human-resolved Open Questions

### OQ-01 — Exact structured fields

**Decision: Resolved.** The result has exactly five required top-level keys:

- `summary`: string.
- `detected_skills`: array of `{name, evidence}` objects.
- `strengths`: array of `{strength, evidence}` objects.
- `improvement_areas`: array of `{area, rationale}` objects.
- `recommendations`: array of strings.

All five keys are present in every valid result. Array fields may be empty
when no supported items are found. Exact limits, duplicate handling, and
evidence wording are specified in SPEC-003. Do not add a numeric score under
this decision.

### OQ-02 — Numeric score

**Decision: Resolved — no numeric score.** Do not include an overall score,
dimension scores, or ranking/comparison values. There is no approved scoring
rubric or calibration basis; a number could imply unsupported precision.

### OQ-03 — Raw AI response retention

**Decision: Resolved — do not persist raw response.** Raw provider output may
exist transiently during parsing/validation only. Do not store it in the
database, filesystem, or another persistent mechanism. Do not log full CV
text or full raw output. The structured result's persistence is separately
resolved by OQ-08.

### OQ-04 — Malformed or incomplete output

**Decision: Resolved — strict rejection.** Reject malformed JSON, missing
keys, wrong types, invalid nested structure, and other schema violations.
Never return partial structured data as success, fabricate missing fields, or
render incomplete output as valid. Return a controlled failure; the exact
user-facing response is specified in SPEC-003.

### OQ-05 — Retry invalid output

**Decision: Resolved — one schema-repair attempt only.** Validate the initial
response. If a response was received but fails JSON parsing/schema validation,
make exactly one additional request for a complete valid result under the
same schema. If that response is also invalid, return the OQ-04/OQ-12
controlled failure. Do not retry permanent configuration/authentication
errors. Provider/network/timeout/service retries are not included and are
resolved separately by OQ-12.

### OQ-06 — Google Drive retrieval failure

**Decision: Resolved — controlled failure, no automatic retry or fallback.**
Stop immediately on retrieval failure before the AI request. Do not use
another source, cached file, staged file, or prior result. Return a
non-sensitive message; the user may manually retry. The existing
`download_warning` confirmation request is part of the Drive download
protocol, not a retry after a failed request.

### OQ-07 — Extraction failure or empty content

**Decision: Resolved — controlled failure before AI.** Stop on parser failure
or empty/whitespace-only extracted text. Do not send partial, empty, or
whitespace-only content to the provider. Do not expose parser exceptions.
Do not add OCR or conversion; such support is a separate possible change.

### OQ-08 — Persistence or on-demand

**Decision: Resolved — on-demand only, no persistence/cache.** Generate only
on explicit user action. Do not store structured results or raw output in the
database, filesystem, cache, history, or another mechanism. Each trigger
performs fresh retrieval, extraction, and analysis. Do not use previous
results as fallback.

### OQ-09 — Staleness and regeneration

**Decision: Resolved — Not Applicable.** OQ-08 means no persisted/cached
analysis or stale state exists. Do not implement invalidation, automatic
regeneration, or staleness-specific tests. Any future persistence change must
define its own policy.

### OQ-10 — Users allowed to trigger/view

**Decision: Resolved — authenticated profile owner only.** Require an
authenticated user and resolve only the Freelancer profile associated with
`request.user`. Do not accept another profile selector. Users without a
profile receive controlled failure; unauthenticated users are denied. Do not
add employer/admin access or a new role-label/numeric-role-ID check.
Enforce ownership server-side; menu visibility is not authorization.

### OQ-11 — Keep Google Drive mechanism

**Decision: Resolved — keep Google Drive, permit narrow correctness/error
handling fixes.** Do not replace Drive or add another storage provider. Keep
the CV reference contract unless a minimal parsing correction is required.
May validate download response, add timeouts/error handling, correctly
identify/preserve type rather than forcing `.docx`, and reject unsupported or
invalid content before extraction/AI. Supported types are DOCX and PDF only.
Do not add OCR, scanned-image support, or other formats.

### OQ-12 — Provider timeout/service failure UX

**Decision: Resolved — controlled failure and manual retry only.** On
provider timeout, network failure, or service error, return a controlled,
non-sensitive error. Do not expose raw provider exceptions, credentials,
configuration details, CV text, or raw AI output. Do not return partial or
success-shaped results. Do not automatically retry provider/network/service
failures; the user may trigger another analysis manually. Permanent
authentication/configuration errors are not retried. The schema-repair retry
under OQ-05 remains allowed only for a received invalid response.

## Final schema validation decisions

These are the concrete bounds recorded in SPEC-003:

| Field | Exact shape and bounds |
|---|---|
| `summary` | Required non-empty string, 1–1,000 Unicode code points after trimming outer whitespace. |
| `detected_skills` | Required array, 0–20 objects; each object exactly `name` (1–100 code points) and `evidence` (1–500 code points), both non-empty strings. |
| `strengths` | Required array, 0–10 objects; each object exactly `strength` (1–300 code points) and `evidence` (1–500 code points), both non-empty strings. |
| `improvement_areas` | Required array, 0–10 objects; each object exactly `area` (1–300 code points) and `rationale` (1–500 code points), both non-empty strings. |
| `recommendations` | Required array, 0–10 non-empty strings, each 1–500 code points after trimming. |

Top-level and nested objects reject every missing or extra key. Reject
duplicate JSON object keys, non-standard constants, wrong types, `null`,
blank strings, Markdown fences, and trailing non-whitespace content. Trim
outer whitespace on accepted strings; preserve internal whitespace. Reject
Unicode control characters (General Category `Cc`). Duplicate identity uses
the primary display field after trim, collapsing each Unicode-whitespace run
to one space, and Unicode casefold; reject duplicates rather than silently
merge/drop them. Evidence/rationale is not part of duplicate identity. Empty
arrays are valid.

Prompt language and evidence rule: user-facing prose is Ukrainian, except
skill names may retain standard/original spelling. Evidence and rationale
are concise paraphrases traceable to explicit resume content; do not
fabricate quotations or details. Skills require resume evidence. Improvement
areas describe information not demonstrated or unclear in the document, not
that the candidate lacks a skill. Recommendations are actionable and
resume-related. Semantic grounding cannot be fully proven by validation;
tests assert schema/shape rather than factual correctness.

## Final HTTP and rendering contract

Successful POST: HTTP 200 JSON exactly `{"analysis": <five-key object>}`.
Errors: JSON exactly
`{"error":{"code":"<stable_code>","message":"<safe Ukrainian message>"}}`;
no error response includes `analysis` or partial data. No exception text,
secrets, CV text, raw AI output, or stack trace is returned.

Error status/code/message mapping:

| Condition | HTTP | Code | Message |
|---|---:|---|---|
| Unauthenticated POST | 401 | `authentication_required` | `Увійдіть, щоб аналізувати резюме.` |
| No own Freelancer profile (POST) | 404 | `freelancer_profile_not_found` | `Профіль фрілансера не знайдено.` |
| Missing CV reference | 400 | `resume_reference_missing` | `Додайте посилання на резюме у своєму профілі.` |
| Invalid Drive reference | 422 | `resume_reference_invalid` | `Посилання на резюме некоректне. Перевірте посилання Google Drive.` |
| Drive retrieval failure | 502 | `resume_retrieval_failed` | `Не вдалося отримати резюме з Google Drive. Перевірте доступ до посилання та спробуйте ще раз.` |
| Unsupported/invalid/mismatched document | 422 | `resume_file_invalid` | `Файл резюме не вдалося перевірити. Завантажте коректний файл PDF або DOCX.` |
| Extraction parser failure | 422 | `resume_extraction_failed` | `Не вдалося прочитати текст резюме. Перевірте файл PDF або DOCX і спробуйте ще раз.` |
| Empty/whitespace extraction | 422 | `resume_text_empty` | `У резюме не знайдено тексту для аналізу. Перевірте файл і спробуйте ще раз.` |
| Invalid AI result after repair attempt | 502 | `analysis_invalid_response` | `Не вдалося сформувати коректний аналіз. Спробуйте ще раз пізніше.` |
| Provider/network timeout | 504 | `analysis_provider_timeout` | `Сервіс аналізу не відповідає. Спробуйте ще раз пізніше.` |
| Provider/service/configuration/credential failure | 503 | `analysis_unavailable` | `Аналіз резюме тимчасово недоступний. Спробуйте ще раз пізніше.` |
| Unexpected internal error | 500 | `analysis_failed` | `Не вдалося виконати аналіз. Спробуйте ще раз пізніше.` |
| Unsupported method | 405 | `method_not_allowed` | `Ця дія не підтримується.` |

Drive requests use 5-second connect and 30-second read timeouts. AI provider
requests use a 30-second timeout and disable SDK automatic retries
(`max_retries=0` or equivalent), ensuring the sole additional request is the
approved schema-repair attempt.

Unauthenticated GET retains the configured Django login redirect. Authenticated
GET without a Freelancer profile renders a non-sensitive no-profile state;
POST without a profile returns the 404 JSON response above. GET with a profile
but no CV shows an instruction to add a link. POST error messages are not
provider/parser exception text.

Render only static markup and model-derived strings through
`textContent`/equivalent safe text binding. Do not insert model strings via
`innerHTML`, render them as Markdown, or treat them as trusted markup.

## Scope decisions

Allowed implementation files:

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/freelancer/tests.py`

No model/migration is needed or allowed. No config, dependency, Docker,
environment, global authentication, CV storage, unrelated template, or other
AI feature changes. Stop and seek separate approval if a blocker requires
scope expansion.

## Acceptance criteria

1. Valid DOCX/PDF Drive responses are identified and passed to the matching
   parser; invalid/mismatched/unsupported content never reaches AI.
2. Drive failures return the exact 502 retrieval error; no extraction/AI
   after failure, automatic retry, or fallback source/file.
3. Parser error or empty/whitespace text returns the exact 422 error and
   makes zero AI calls; no OCR/conversion/partial analysis.
4. Valid AI output returns 200 with exactly the five required keys and all
   specified types, bounds, trimming, duplicate, and exact-key rules; no
   score or extras.
5. Invalid JSON/schema responses are rejected; exactly one repair attempt is
   used only for a received invalid response; a second invalid response
   returns the specified 502 with no partial success.
6. Provider timeout/service/configuration failure returns exact 504/503
   contract; no automatic network/provider retry; no raw details exposed or
   logged.
7. Access is authenticated and bound to the caller's own profile; no profile
   and unauthenticated behavior matches the specified GET/POST contracts; no
   role-ID, employer, or admin access is added.
8. Model strings render as text only; HTML-looking strings never become
   markup and are not processed as Markdown.
9. Analysis is on-demand; no analysis result/raw output persistence, cache,
   history, logging of full content, or stale fallback exists.
10. Tests mock all external services and use no real credentials/CV data;
    focused freelancer tests and applicable Django checks pass.
11. Only allowed files are changed absent prior explicit scope approval.

## Proposed test plan

- Mock Drive requests and assert timeout/status handling, type detection,
  supported DOCX/PDF parser routing, and no retry/fallback.
- Test extraction success, parser errors, empty/whitespace text, and zero
  downstream model calls for failure inputs.
- Test exact schema boundaries, all invalid key/type/content conditions,
  duplicate JSON keys, duplicate normalized items, trimming, and count/length
  limits at and above boundaries.
- Assert provider call counts for valid first response, one repair producing
  valid output, two invalid outputs, and timeout/configuration/service errors
  on either attempt.
- Test authentication, owner binding, no profile, missing CV, method
  handling, exact statuses/JSON/error messages, and no raw exception leakage.
- Test safe rendering with HTML-looking model text and ensure no
  model-controlled HTML/Markdown rendering.
- Assert no storage/cache/history and fresh retrieval/model work on a second
  explicit user trigger.
- Run existing focused freelancer tests and applicable Django checks. Record
  exact commands/results; no live Drive/provider call in tests.

## Review gate

All OQs are resolved. CHANGE-003, SPEC-003, and TASK-003 were subsequently
marked Approved by the human. TASK-003 is Implementation-ready: Yes.
