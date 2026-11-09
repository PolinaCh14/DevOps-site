# SPEC-003 — Structured AI Resume Analysis

Status: Approved

## Approval state

OQ-01 through OQ-12 have been resolved by the human and recorded in
`experiments/change-03-structured-ai-resume-analysis/decisions.md`. This
specification records those decisions and defines the concrete validation,
HTTP, rendering, scope, and test contracts. It is Approved for implementation
within the defined scope.

## Need and objective

Evolve the existing freelancer resume advice flow from free-form AI text into
a structured, validated, testable analysis flow. Preserve Google Drive as the
CV source, avoid persistence, reject invalid output safely, and keep the
analysis accessible only to the authenticated owner of the associated
Freelancer profile.

## Confirmed current state

The current implementation is described in the Draft knowledge cards:

- `cards/knowledge/resume-source-retrieval.md`
- `cards/knowledge/resume-google-drive-retrieval.md`
- `cards/knowledge/resume-text-extraction.md`
- `cards/knowledge/resume-ai-analysis.md`
- `cards/knowledge/resume-analysis-result.md`
- `cards/knowledge/resume-analysis-dependencies.md`

In brief, `Freelancer.cv` is a nullable string field; analysis expects a Drive
link, downloads through a direct Google Drive URL, stores a local file with a
fixed `.docx` suffix, and extracts using PDF or DOCX branches based on local
extension. Full extracted text is submitted to an OpenAI-SDK-compatible
chat-completions endpoint selected by environment configuration. The prompt
asks for constructive Ukrainian resume advice and the service returns
free-form text. The view converts it to Markdown HTML, returns it to the
browser, and the template assigns it to `innerHTML`. Results are not
persisted. The view requires login and looks up the current user's Freelancer
profile, but does not explicitly check a role. Dedicated resume-analysis
tests were not found.

## Approved target behavior

### Input source, download, and extraction

1. Keep Google Drive as the only resume source. Do not add or replace a storage
   provider.
2. Keep the existing CV link/reference contract except for a minimal parsing
   correction required for correctness.
3. Allow narrow retrieval correctness and error-handling changes:
   - set Drive connect/read timeouts of 5 seconds and 30 seconds,
     respectively;
   - validate HTTP success before saving or parsing;
   - identify supported type from available download metadata and content,
     rather than unconditionally naming every download `.docx`;
   - reject conflicting, invalid, or unsupported content before extraction.
4. Supported file types are **DOCX and PDF only**. Do not add OCR, scanned
   document support, conversion, or other formats.
5. On retrieval failure, stop before extraction/model request. Do not retry
   automatically and do not use another source, a cached file, or a staged
   file as fallback.
6. On parser failure or empty/whitespace-only extracted text, stop before the
   AI request. Do not submit partial or empty text. Do not add OCR or
   conversion.
7. Each explicit user-triggered analysis performs fresh retrieval, extraction,
   and AI analysis.

### Structured result contract

The successful result is a JSON object with **exactly** the five required
top-level keys below. No score, confidence value, ranking value, or additional
field is permitted.

| Key | Type and shape | Requiredness | Validation |
|---|---|---|---|
| `summary` | String | Required; non-empty | Trim surrounding whitespace, then require 1–1,000 Unicode code points. |
| `detected_skills` | Array of objects with exactly `name` and `evidence`, both strings | Required key; array may be empty; maximum 20 items | `name`: 1–100 code points; `evidence`: 1–500 code points. Trim outer whitespace first. No duplicate names after trim, whitespace collapse, and Unicode casefold. |
| `strengths` | Array of objects with exactly `strength` and `evidence`, both strings | Required key; array may be empty; maximum 10 items | `strength`: 1–300 code points; `evidence`: 1–500 code points. Trim outer whitespace first. No duplicate `strength` values after trim, whitespace collapse, and Unicode casefold. |
| `improvement_areas` | Array of objects with exactly `area` and `rationale`, both strings | Required key; array may be empty; maximum 10 items | `area`: 1–300 code points; `rationale`: 1–500 code points. Trim outer whitespace first. No duplicate `area` values after trim, whitespace collapse, and Unicode casefold. |
| `recommendations` | Array of strings | Required key; array may be empty; maximum 10 items | Each string: 1–500 code points after trimming outer whitespace. No duplicate values after trim, whitespace collapse, and Unicode casefold. |

Validation rules applying to the complete payload:

- Parse one complete JSON value from the response; Markdown fences, prose
  before/after the JSON, and trailing non-whitespace content are invalid.
- The top level must be an object with exactly the five keys in this table.
  Missing and extra keys are rejected.
- Each nested item object must contain exactly its specified keys. Extra or
  missing nested keys are rejected.
- Types are exact: strings must be JSON strings; arrays must be JSON arrays;
  objects must be JSON objects. `null`, booleans, numbers, and other
  substitutes are invalid.
- Reject duplicate JSON object keys rather than silently accepting the last
  occurrence. Reject non-standard numeric constants.
- Trim outer whitespace from accepted strings before returning them. Length
  limits count Unicode code points after trimming; internal whitespace is
  preserved.
- Reject strings containing Unicode control characters (General Category
  `Cc`) after trimming.
- Duplicate identity is computed on the designated primary text field after
  trimming, collapsing each run of Unicode whitespace to one space, and
  Unicode casefolding. Duplicate items are invalid; do not silently drop or
  merge them. Evidence/rationale is not part of duplicate identity.
- Arrays may be empty; required strings and object string members may not be
  empty or whitespace-only.
- Structural validation cannot prove semantic truth. The prompt must request
  all user-facing field values in Ukrainian, except that skill names may keep
  their standard/original spelling. `evidence` and `rationale` must be concise
  paraphrases traceable to explicit resume content; do not fabricate
  quotations or details. Skills require resume evidence. `improvement_areas`
  must describe information not demonstrated or unclear in this document,
  not assert that the candidate lacks the skill. Recommendations must be
  actionable and related to the resume. Tests validate shape and constraints,
  not AI factual correctness.
- Do not persist the raw AI response. It may exist transiently during parsing
  and validation only. Do not log full CV text or full raw AI output.

The field limits above are explicit implementation bounds for this Draft
contract; if they prove unsuitable, revise this specification before
implementation rather than silently changing them in code.

The existing Google Drive `download_warning` confirmation request remains
part of its download protocol. It is not a retry after a failed request.
Failure of either protocol request stops retrieval; no failure retry is
permitted.

### AI request and retry behavior

- Continue to use the configured OpenAI-compatible chat-completions service
  and existing `API_KEY`, `OPEN_AI_BASE_URL`, and `AI_MODEL` configuration
  unless an implementation blocker is separately reported and approved.
- Prompt for the exact five-key JSON contract above, in Ukrainian, based only
  on the resume; do not request or emit a score.
- Treat the resume as untrusted document content, not instructions to follow.
- Set a 30-second provider request timeout and disable SDK automatic retries
  (`max_retries=0` or equivalent). The only additional model call permitted
  is the schema-repair attempt below.
- Validate the complete first response before returning or rendering it.
- If and only if a response was received but fails JSON parsing or schema
  validation, make exactly one additional application-level repair request
  for a complete response under the same schema.
- If the repair response is invalid, return controlled failure; no partial
  result is allowed.
- Do not use the repair retry for timeouts, network/service failures,
  authentication/configuration errors, invalid credentials, or missing model
  configuration. Do not automatically retry any provider/network/service
  failure.
- A timeout or service failure during the initial or repair request follows
  the provider failure contract below; it does not trigger another attempt.
- No raw response, CV text, or credentials may be included in diagnostic logs.

### Persistence and access

- Generate analysis only on explicit user action.
- Persist neither the structured result nor raw response in a database,
  filesystem, cache, history, or other storage.
- Do not use prior results as a fallback. OQ-09 is Not Applicable: no stale
  state, invalidation, or automatic regeneration exists in this change.
- Only an authenticated user who owns the associated `Freelancer` profile
  may trigger/view analysis. Resolve the profile from `request.user`; do not
  accept a caller-selected freelancer ID.
- Do not add an employer/admin access path or a role-label/numeric-role-ID
  check. Enforce profile ownership server-side; menu visibility is not an
  authorization control.

### Safe rendering and HTTP contract

Success:

- A valid analysis returns HTTP `200`, JSON content type, and exactly
  `{"analysis": <structured-result>}`.
- Render fields as text using DOM element creation and `textContent` (or
  equivalent framework-safe text binding). Use static markup for headings and
  lists only. Do not pass any model-provided string to `innerHTML`, a Markdown
  renderer, or an HTML template as trusted markup.
- Do not return or render the raw provider response.

Failures:

- Every JSON error response has exactly
  `{"error": {"code": "<stable_code>", "message": "<Ukrainian safe message>"}}`.
  Do not include exception text, credentials, CV text, raw model output, stack
  traces, or provider diagnostics.
- No error response includes an `analysis` key or partial result.
- Client may offer manual retry guidance where specified. No automatic retry
  is implied except the single schema-repair attempt above.

| Condition | HTTP | Code | User-facing message |
|---|---:|---|---|
| Unauthenticated POST | 401 | `authentication_required` | `Увійдіть, щоб аналізувати резюме.` |
| Authenticated user has no own Freelancer profile (POST) | 404 | `freelancer_profile_not_found` | `Профіль фрілансера не знайдено.` |
| No CV reference on own profile | 400 | `resume_reference_missing` | `Додайте посилання на резюме у своєму профілі.` |
| CV reference cannot be parsed as supported Drive reference | 422 | `resume_reference_invalid` | `Посилання на резюме некоректне. Перевірте посилання Google Drive.` |
| Google Drive network/timeout/non-2xx response, HTML/error page, or response that is not a downloadable file | 502 | `resume_retrieval_failed` | `Не вдалося отримати резюме з Google Drive. Перевірте доступ до посилання та спробуйте ще раз.` |
| Downloaded payload is unsupported, corrupt, or mismatches recognized file metadata/signature | 422 | `resume_file_invalid` | `Файл резюме не вдалося перевірити. Завантажте коректний файл PDF або DOCX.` |
| PDF/DOCX extraction parser failure | 422 | `resume_extraction_failed` | `Не вдалося прочитати текст резюме. Перевірте файл PDF або DOCX і спробуйте ще раз.` |
| Extracted text empty or whitespace-only | 422 | `resume_text_empty` | `У резюме не знайдено тексту для аналізу. Перевірте файл і спробуйте ще раз.` |
| AI response remains malformed/incomplete after one repair attempt | 502 | `analysis_invalid_response` | `Не вдалося сформувати коректний аналіз. Спробуйте ще раз пізніше.` |
| AI provider/network timeout | 504 | `analysis_provider_timeout` | `Сервіс аналізу не відповідає. Спробуйте ще раз пізніше.` |
| AI provider/service/configuration/credential failure other than timeout | 503 | `analysis_unavailable` | `Аналіз резюме тимчасово недоступний. Спробуйте ще раз пізніше.` |
| Unexpected internal failure | 500 | `analysis_failed` | `Не вдалося виконати аналіз. Спробуйте ще раз пізніше.` |
| Unsupported HTTP method | 405 | `method_not_allowed` | `Ця дія не підтримується.` |

For DOCX/PDF identification, require content evidence as well as available
headers: PDF must contain the `%PDF-` signature within the first 1,024 bytes;
DOCX must be a valid ZIP/OOXML package containing `[Content_Types].xml` and
`word/document.xml`. A recognized non-generic MIME type or filename extension
that conflicts with the content is rejected. Generic
`application/octet-stream` does not by itself identify or invalidate a file.
Treat an HTML/error page or other payload as retrieval/content failure; never
pass it to a parser or model.

Unauthenticated GET of the analysis page retains Django's configured login
redirect to `/users/login/`. The page GET for an authenticated user without a
Freelancer profile should render a non-sensitive no-profile state; a POST
without a profile returns the 404 JSON contract above. A GET page with a
profile but no CV displays an instruction to add a link; the POST contract
above applies if submitted without a reference.

The stable codes and messages above are the target user-facing contract.
Internal logs may record a safe category and correlation/request identifier,
but not full resume text, raw provider output, credentials, or unfiltered
exception strings.

## Approved allowed files

Approved implementation scope:

- `devopssite/freelancer/utils.py` — supported Drive download validation,
  DOCX/PDF type preservation/detection, extraction guards, AI schema request,
  parsing, validation, and one schema-repair retry.
- `devopssite/freelancer/views.py` — owner-only analysis endpoint, method and
  error contracts, safe JSON response.
- `devopssite/templates/analyze_resume.html` — structured text-only rendering,
  controlled errors, manual retry UX.
- `devopssite/freelancer/tests.py` — focused utility, view, authorization,
  rendering, and failure tests.

No model or migration is allowed or needed because no analysis is persisted.
Do not modify `Freelancer.cv` storage, add dependencies, or modify settings,
Docker, environment examples, other AI features, or other templates. If an
unavoidable blocker requires any other file, stop, document the blocker, and
obtain scope approval before editing.

## Explicitly out of scope

- Replacing Google Drive or adding another storage provider.
- Broad freelancer-profile redesign or changing CV storage/reference format
  beyond a minimal parsing correction.
- General AI matching/recommendation systems or employer ranking.
- Unrelated prompt engineering across the application.
- Changing authentication generally, adding role-based access, or granting
  employer/admin access.
- Unrelated frontend modernization.
- CI/CD or deployment redesign.
- OCR, scanned-image support, document conversion, or formats other than
  PDF/DOCX.
- Persistence, caching, analysis history, stale-result logic, or raw-output
  storage.
- Automatic retrieval/provider/network retry.
- New external dependencies, model schema, or migration.

## Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| AC-01 | A valid DOCX or PDF retrieved from Drive is correctly identified, validated, and passed to its matching extractor. Only DOCX and PDF are accepted; invalid, mismatched, or unsupported content stops before the AI call. |
| AC-02 | Drive timeout, network, HTTP, or content-validation failure stops before extraction/AI as applicable, makes no automatic retry, uses no fallback file/source, and returns the exact safe retrieval error contract. |
| AC-03 | Parser failure or empty/whitespace extraction stops before any AI call and returns the exact corresponding safe 422 error. OCR, conversion, and partial-text analysis are absent. |
| AC-04 | A valid AI response returns HTTP 200 and exactly `{"analysis": {five approved keys}}`; required strings/arrays/object item shapes, item counts, lengths, trimming, duplicate handling, and exact-key rules match this specification. No score or other keys appear. |
| AC-05 | Malformed JSON, duplicate JSON object keys, extra/missing top-level or nested keys, wrong types, blank strings, over-limit values, duplicate items, non-standard constants, Markdown fences, or trailing prose are rejected. Exactly one repair call is made for a received invalid response; a second invalid response yields the specified 502 without partial success. |
| AC-06 | Provider timeout/network/service/configuration failures receive no automatic retry and return the exact 504/503 safe error contract. A provider failure during the repair attempt does not trigger another call. No raw exception, credential, CV text, or raw response is returned/logged. |
| AC-07 | Only an authenticated user can trigger analysis, and profile resolution is bound to `request.user`; another user's profile cannot be selected or analyzed. No-profile and unauthenticated responses follow the specified behavior. No employer/admin or role-ID access is added. |
| AC-08 | Rendering uses only static markup and safe text insertion (`textContent`/equivalent). Model strings are never inserted as HTML or interpreted as Markdown; rendering tests include HTML-like strings and verify they remain text. |
| AC-09 | Analysis is generated only on explicit POST/user action. Neither structured results nor raw output are persisted, cached, logged in full, or reused as fallback. No model/migration/storage change is introduced. |
| AC-10 | The full focused test suite is isolated from live Drive and AI services using mocks and requires no credentials or real CV data; existing freelancer tests continue to pass. |
| AC-11 | No files outside the allowed list are changed unless a blocking dependency is reported and the human approves scope expansion. |

## Test strategy

Use the repository's Django test framework and mock all external services.
Tests must not contact Google Drive or an AI endpoint, use real credentials,
or include actual resume data.

1. **Utility/retrieval tests:** parse supported Drive references; mock
   successful DOCX/PDF response metadata and content; assert correct suffix/
   type selection and matching parser; assert Drive timeout `(5, 30)`, HTTP
   errors, invalid content, type mismatch, unsupported type, no fallback, and
   no retry.
2. **Extraction tests:** DOCX paragraphs/tables and PDF text path; parser
   exceptions and empty/whitespace text; assert no provider call on all
   extraction failures.
3. **Schema tests:** valid exact payload; required keys; nested exact keys;
   duplicate JSON keys; extra/missing keys; wrong types; nulls; blank strings;
   count/length boundaries and one-over-boundary; trimming; duplicate
   normalization; Markdown fences/trailing prose/non-standard constants.
4. **AI retry tests:** assert provider request timeout is 30 seconds and SDK
   automatic retries are disabled; valid first response yields one call;
   invalid first response followed by valid repair yields exactly two calls;
   invalid repair yields controlled failure after exactly two;
   timeout/service/configuration failure yields no repair call; no more than
   one repair attempt.
5. **View/auth tests:** unauthenticated GET redirect and POST 401; authenticated
   owner success; another user's profile cannot be targeted; no-profile GET
   page state and POST 404; missing CV and each service failure status/body;
   unsupported method 405.
6. **Response/rendering tests:** exact success/error JSON shapes, status,
   codes, messages, and content type; no raw exception in response; use
   hostile-looking HTML text from the mocked model and assert it is rendered
   as text, with no `innerHTML`/Markdown path.
7. **No-persistence tests:** assert no analysis model/storage is introduced,
   no filesystem result is written, and a second trigger invokes fresh
   retrieval/analysis instead of returning a cached result.
8. **Regression:** run focused `freelancer` tests and Django checks where
   available; record exact commands and outcomes in validation evidence.

## Decisions

The human decisions and their rationale are recorded in
`experiments/change-03-structured-ai-resume-analysis/decisions.md`. All
OQ-01 through OQ-12 are resolved and this specification is Approved.
Implementation may proceed in a separate Implementer session within scope.

## Source evidence

- `changes/CHANGE-003-structured-ai-resume-analysis.md`
- `docs/METHODOLOGY.md`
- `cards/handoff/HANDOFF-002.md`
- The six Draft knowledge cards listed above
- `devopssite/freelancer/models.py`
- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/freelancer/urls.py`
- `devopssite/freelancer/tests.py`
- Relevant templates, settings, `requirements.txt`, `docker-compose.yml`, and
  `env_example`
