# Builder Report

Status: Draft

## Agent Configuration

Experiment:
CHANGE-003 / Experiment 3

Role:
Builder

Environment:
VS Code integrated agent

Model:
Not exposed by environment

Session type:
Independent session

Repository starting commit:
`2617f1f7e9d386f3dcddf9204010caad29867f81`

Repository starting tag:
None

Expected previous accepted baseline:
CHANGE-002 final accepted state / latest accepted tag `change-002-accepted`
(accepted commit `2d713d82f8250b4a20c3803d456fe32327a25ab9`)

Working tree state:

```text
?? cards/knowledge/resume-ai-analysis.md
?? cards/knowledge/resume-analysis-dependencies.md
?? cards/knowledge/resume-analysis-result.md
?? cards/knowledge/resume-google-drive-retrieval.md
?? cards/knowledge/resume-source-retrieval.md
?? cards/knowledge/resume-text-extraction.md
?? cards/specs/SPEC-003-structured-ai-resume-analysis.md
?? cards/tasks/TASK-003-structured-ai-resume-analysis.md
?? changes/CHANGE-003-structured-ai-resume-analysis.md
?? experiments/change-03-structured-ai-resume-analysis/
```

This state was captured at the start of the expanded Builder-artifact stage.
The untracked card/spec/task/report drafts from the preceding persistence
stage already existed and were being updated; the untracked CHANGE-003 was
the human-approved starting description. No application source changes were
present in that starting status.

## Repository State Reviewed

Governing documents:

- `docs/METHODOLOGY.md`
- `cards/handoff/HANDOFF-002.md`
- `changes/CHANGE-003-structured-ai-resume-analysis.md`
- `docs/ARCHITECTURE.md`
- `docs/BASELINE.md`

Implementation/configuration/tests:

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/migrations/0001_initial.py`
- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/freelancer/urls.py`
- `devopssite/freelancer/tests.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/templates/freelancer_profile_create.html`
- `devopssite/templates/freelancer_profile_edit.html`
- `devopssite/templates/user_freelancer_detail.html`
- `devopssite/templates/user_menu.html`
- `devopssite/devopssite/settings.py`
- `devopssite/devopssite/urls.py`
- `devopssite/users/models.py`
- `requirements.txt`
- `docker-compose.yml`
- `env_example`
- `promt.txt` (an unrelated CHANGE-001 prompt)
- `devopssite/downloaded_cv_3.docx` (exists in the repository; origin is To be
  verified)

No application code was changed. No tests were run in this Builder stage.

## Confirmed Current Flow

1. `Freelancer.cv` is a nullable string field, not file storage. Profile forms
   accept free text, while analysis treats the value as a Drive URL.
2. `extract_file_id` recognizes `/d/<id>`. The download function uses
   `requests.Session` against Google's `uc?export=download` endpoint, with a
   warning-cookie confirmation request when present.
3. The downloader writes to relative `downloaded_cv_<freelancer_id>.docx`
   regardless of actual file type. It does not explicitly set a timeout,
   check HTTP status, validate MIME/size, or remove the file.
4. `read_file` extracts PDF text with PyMuPDF and DOCX paragraphs/tables with
   python-docx based on local extension; other extensions raise `ValueError`.
   The fixed `.docx` suffix means PDF support is not confirmed end-to-end.
   There is no OCR.
5. The service constructs `openai.OpenAI` with `API_KEY` and
   `OPEN_AI_BASE_URL`, and uses `AI_MODEL` for chat completions. It sends the
   full extracted CV text. The system prompt requests constructive Ukrainian
   resume-improvement advice covering structure, content, style, errors, and
   similar issues.
6. The model response is free-form first-choice message content; no structured
   parsing or validation is performed. The view converts it from Markdown to
   HTML and returns `{"analysis": "<html>"}`. The template inserts the result
   using `innerHTML`.
7. The result is not persisted. On POST, missing CV returns status 400; caught
   exceptions return status 500 with raw exception text. Empty text can reach
   the AI.
8. The analysis view uses `login_required` and retrieves the profile associated
   with `request.user`; no explicit role check is made. The endpoint exposes no
   caller-selected profile ID. The menu link's role condition is not
   server-side authorization.
9. `freelancer/tests.py` has no dedicated analysis retrieval, extraction,
   provider, schema, rendering, or authorization tests.
10. `requirements.txt` pins OpenAI, requests, PyMuPDF, python-docx, and
    Markdown. Compose passes `API_KEY`, `OPEN_AI_BASE_URL`, and `AI_MODEL`
    with empty defaults; `env_example` omits those keys. The live provider,
    model, credentials, and runtime availability are To be verified.

## Current Limitations

- CV field accepts arbitrary string; analysis assumes a supported Drive URL.
- Drive download response status/content/type is not explicitly validated.
- All downloads are staged as `.docx`; format detection is not end-to-end.
- No explicit timeout, download limit, cleanup, OCR, empty-text guard, or
  parser recovery.
- Shared freelancer filename can collide across concurrent analysis requests.
- Model output is free-form and unvalidated.
- Markdown HTML is assigned to `innerHTML` without a visible sanitization
  step.
- Raw exception text is returned to the user.
- No result persistence or dedicated feature tests.
- AI configuration and provider behavior are environment-dependent.

## External Dependencies

- Google Drive public-download endpoint and sharing/access permissions.
- `requests==2.32.3` for retrieval.
- `PyMuPDF==1.25.5` for PDF extraction.
- `python-docx==1.1.2` for DOCX extraction.
- `openai==1.76.0` SDK pointed to a configurable OpenAI-compatible endpoint.
- `Markdown==3.8` for current Markdown-to-HTML path.
- `python-dotenv` and Compose-provided environment values.

The full extracted resume is currently sent externally. Provider identity,
retention/processing terms, deployed credentials/configuration, and installed
runtime dependencies are To be verified. No policy conclusion about those
external practices is made here.

## Risks

- Sensitive CV text is sent to an externally configured service.
- Invalid Drive responses may be written and passed to parsers.
- DOCX suffix may misclassify PDF; malformed files can raise parser errors.
- Local files remain and concurrent requests can collide.
- Provider/model output may be malformed or incomplete.
- Provider-generated HTML risk exists because output reaches `innerHTML`;
  this is a code-path risk, not a claim of a tested exploit.
- Exception strings may disclose internal details.
- Configuration, endpoint availability, and provider limits are not
  confirmed from the repository.
- Analysis lacks focused automated tests.

## Final Human Decisions

All OQ-01 through OQ-12 are resolved; full decision wording and rationale are
in `experiments/change-03-structured-ai-resume-analysis/decisions.md`.

- Exactly five required result keys: `summary`, `detected_skills`,
  `strengths`, `improvement_areas`, `recommendations`; arrays may be empty.
- No score or ranking values.
- Raw AI output is transient only, never persisted/logged in full.
- Strictly reject malformed/incomplete output; exactly one repair attempt only
  after a received response fails JSON/schema validation.
- Google Drive remains the source; retrieval failure stops before AI, no
  automatic retry/fallback. Narrow correctness/error handling is allowed.
- DOCX/PDF only. Extraction failure or empty/whitespace text stops before AI.
  No OCR/conversion.
- On-demand analysis only; no persistence/cache/history/fallback.
  OQ-09 is Not Applicable.
- Authenticated owner of the associated profile only; no extra role check and
  no employer/admin access.
- Provider/network timeout/service failure is a controlled non-sensitive
  failure with no automatic retry; user may retry manually.

## Proposed Structured Result and Validation

The five required keys and their exact bounds are specified in SPEC-003:

| Field | Purpose | Proposed type/bounds | Required | Validation and ambiguity/risk |
|---|---|---|---|---|
| `summary` | Describe the resume's overall presentation | String, 1–1,000 Unicode code points | Yes | Trim outer whitespace; non-empty. Risk: subjective; prompt must ground claims. |
| `detected_skills` | Skills evidenced in CV | 0–20 `{name, evidence}` objects; name 1–100, evidence 1–500 code points | Yes; empty list allowed | Exact nested keys, non-empty strings; dedupe by normalized name. Mention does not prove proficiency. |
| `strengths` | Resume strengths | 0–10 `{strength, evidence}` objects; strength 1–300, evidence 1–500 | Yes; empty list allowed | Exact nested keys; dedupe by normalized strength. Subjective and can overlap with skills. |
| `improvement_areas` | Areas not demonstrated by the document | 0–10 `{area, rationale}` objects; area 1–300, rationale 1–500 | Yes; empty list allowed | Exact nested keys; dedupe by normalized area. Must not assert the person lacks a skill merely because CV omits it. |
| `recommendations` | Actionable resume improvements | 0–10 strings, 1–500 code points each | Yes; empty list allowed | Non-empty; dedupe by normalized string. Generic advice may be low value. |

Validation rejects all missing/extra top-level and nested keys, duplicate JSON
object keys, wrong/null types, blank/over-limit strings, Unicode control
characters (General Category `Cc`), over-limit arrays, duplicate items,
Markdown fences, trailing prose, and non-standard constants. Trim outer
whitespace and preserve internal whitespace; duplicate identity collapses
Unicode whitespace runs and Unicode-casefolds primary display values.
Evidence/rationale are Ukrainian concise paraphrases of resume content (skill
names may retain standard spelling), not fabricated quotes. Improvement areas
describe only what is not demonstrated in the document; recommendations are
actionable and resume-related. Semantic truth is not fully mechanically
verifiable; automated tests assert schema/shape.

No score, confidence, dimension rating, or ranking value is part of the
contract.

## Approved HTTP/User-Facing Failure Contract

Success: HTTP 200 JSON exactly `{"analysis": <structured result>}`.
Errors: JSON exactly
`{"error":{"code":"...","message":"..."}}`, with no analysis/partial result
or raw details. The exact status/code/Ukrainian message mapping for auth,
profile, CV reference, Drive, extraction, malformed AI, provider, unexpected
error, and method failures is in SPEC-003. Unauthenticated GET retains
Django's login redirect; authenticated GET without a profile shows a
no-profile state; POST without a profile returns controlled 404. Render model
strings only through safe text APIs (`textContent` or equivalent); no
`innerHTML` or Markdown interpretation.

Drive uses a 5-second connect and 30-second read timeout. The AI request uses
a 30-second timeout, with SDK automatic retries disabled so the only
additional AI request can be the single approved repair attempt for a
received schema-invalid response.

## Bounded Implementation Scope

### Proposed allowed files

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/freelancer/tests.py`

No model/migration, storage, config, dependency, Docker, environment, global
auth, unrelated template, or other AI feature changes. Any blocking
dependency beyond this list requires separate approval before editing.

### Explicitly out of scope

- Replacing Google Drive or adding another storage provider.
- Broad freelancer-profile redesign or CV storage changes beyond minimal
  reference parsing correctness.
- General AI matching/recommendations, employer ranking, unrelated prompt
  engineering.
- Global authentication changes, new role checks, employer/admin access.
- Unrelated frontend modernization; CI/CD/deployment redesign.
- OCR, scans, conversion, or file types beyond DOCX/PDF.
- Persistence, caching, history, stale-result logic, raw-output storage.
- Automatic retrieval/provider/network retry.
- New dependency, migration, or settings/config change.

## Final Acceptance Criteria

1. DOCX/PDF Drive downloads are correctly validated and routed to matching
   parsers; invalid/unsupported/mismatched content never reaches AI.
2. Drive failure returns exact safe 502 contract with zero retry/fallback.
3. Extraction failure or empty/whitespace text returns exact safe 422 with
   zero AI calls; no OCR/conversion/partial analysis.
4. Valid output returns HTTP 200 with exactly five required keys and specified
   type/count/length/trimming/duplicate rules; no score or extra key.
5. Invalid JSON/schema is rejected; exactly one repair attempt occurs only
   for received invalid output; second invalid response returns controlled
   502 without partial result.
6. Provider timeout/service/configuration failures return safe 504/503; no
   automatic retry and no raw sensitive details returned/logged.
7. Authenticated owner-only access and no-profile/unauthenticated behavior
   match the GET/POST contract; no role-ID or employer/admin access.
8. All model-derived rendering is safe text; HTML-looking content is not
   interpreted as markup or Markdown.
9. No structured/raw result persistence, cache, history, full-content logs,
   or stale fallback; each trigger performs fresh analysis.
10. Tests mock external services, require no credentials/real CVs, and focused
    freelancer tests/applicable Django checks pass.
11. Only allowed files change absent separate scope approval.

## Proposed Test Strategy

- Mock Drive: successful DOCX/PDF metadata/content, type/parser selection,
  exact connect/read timeouts, HTTP/network/timeout/invalid response, no
  retry/fallback.
- Test parser successes, parser errors, empty/whitespace input, and zero AI
  calls for failed extraction.
- Test exact schema, extra/missing keys at both levels, duplicate JSON keys,
  wrong/null types, blank strings, lengths/counts at and above boundaries,
  trimming, normalized duplicates, fences, trailing prose, and constants.
- Test AI call counts, 30-second provider timeout, and disabled SDK retries
  for first-response success, one valid repair, two invalid responses, and
  provider failures before/during repair.
- Test auth/owner/no-profile/missing-CV/method responses and exact JSON
  statuses/codes/messages; assert no raw exception disclosure.
- Test HTML-looking content remains text and no model content enters an HTML
  or Markdown rendering path.
- Verify no storage/cache/history and fresh requests on repeat user trigger.
- Run focused freelancer tests and applicable Django checks; record exact
  commands and outcomes. Never call external services from automated tests.

## Produced Artifacts

Knowledge cards:

- `cards/knowledge/resume-source-retrieval.md`
- `cards/knowledge/resume-google-drive-retrieval.md`
- `cards/knowledge/resume-text-extraction.md`
- `cards/knowledge/resume-ai-analysis.md`
- `cards/knowledge/resume-analysis-result.md`
- `cards/knowledge/resume-analysis-dependencies.md`

Specification/task/decision/report:

- `cards/specs/SPEC-003-structured-ai-resume-analysis.md`
- `cards/tasks/TASK-003-structured-ai-resume-analysis.md`
- `experiments/change-03-structured-ai-resume-analysis/decisions.md`
- `experiments/change-03-structured-ai-resume-analysis/builder-report.md`

This Builder report remains Draft. CHANGE-003, SPEC-003, and TASK-003 were
subsequently approved by the human; TASK-003 is
`Implementation-ready: Yes`. Implementation is delegated to a separate
Implementer session and no application code was changed by the Builder.
