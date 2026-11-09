# Resume Analysis Dependencies / Failure Behavior

Status: Draft

## Purpose

Record direct runtime dependencies and confirmed failure points along the
current resume-analysis path.

## Dependency chain

| Stage | Repository implementation / dependency | Confirmed behavior and failure exposure |
|---|---|---|
| Profile source | Django `Freelancer.cv` string field | Nullable string, not file storage; may be text or URL, while the analysis flow expects a Drive link. |
| Drive retrieval | `requests==2.32.3`, public `drive.google.com/uc?export=download` endpoint | `/d/<id>` extraction; streaming download; optional warning-cookie confirmation. No explicit timeout, HTTP status validation, content-type check, or size limit. |
| Local staging | Python filesystem; `downloaded_cv_<id>.docx` | Stable relative filename, no cleanup; same-freelancer concurrent calls can collide. |
| PDF extraction | `PyMuPDF==1.25.5` (`fitz`) | Extracts page text when extension is `.pdf`; no OCR. Fixed `.docx` download suffix makes end-to-end PDF recognition uncertain. |
| DOCX extraction | `python-docx==1.1.2` | Reads paragraphs and tables when extension is `.docx`. Invalid/mismatched content can raise. |
| LLM request | `openai==1.76.0` with configurable `API_KEY`, `OPEN_AI_BASE_URL`, `AI_MODEL` | Full extracted CV text is sent to an OpenAI-compatible chat-completions endpoint. Provider/model and live configuration are To be verified. |
| Result formatting | `Markdown==3.8` | Converts free-form model text to HTML with fenced-code support; no explicit sanitization is called before template `innerHTML`. |
| Web handling | Django view and template | A broad exception handler returns status 500 and exception text; browser displays it as text. No stale-result fallback. |
| Configuration | `python-dotenv`; Docker Compose environment pass-through | Compose AI variables default to empty; `env_example` omits them. Missing/invalid values can cause provider errors, surfaced through the broad catch. |

## Confirmed failure points

- A CV string that does not contain a matching `/d/<id>` raises `ValueError`.
- Drive network failures can raise, but HTTP error responses are not explicitly
  rejected before saving.
- Empty or invalid downloads may be passed to extraction.
- Unsupported file extensions raise `ValueError`; parsing errors propagate.
- Empty extracted text is not checked and may be submitted to the model.
- Provider setup, request, and response errors propagate to the view.
- The view converts any caught exception into a 500 with its raw string.
- No analysis retry, cleanup, persistence, or previous-result fallback is
  implemented in the application code.

## Privacy and security considerations

- The complete extracted resume text is included in a request to an
  externally configured AI service. Provider identity, terms, retention, and
  processing location are To be verified; no privacy-policy conclusion is
  established by repository source.
- Downloaded files are written to a predictable relative local path and are
  not cleaned up by this flow. Their runtime access permissions and hosting
  storage lifecycle are To be verified.
- The view returns raw exception strings to the browser. The contents of
  provider or transport errors are not constrained in this code.
- The model response is converted from Markdown to HTML and assigned to
  `innerHTML` by the template. No sanitization step is visible. This is a
  security/rendering risk requiring validation; this Builder analysis does
  not claim a tested exploit.
- The endpoint is login-protected and resolves the caller's own profile, but
  it does not explicitly check the user's role in the view. The role-2 menu
  condition is presentation logic rather than endpoint authorization.

## Important boundary

Package versions are repository-pinned dependencies; actual installed runtime
versions and production availability are not verified here. Provider
configuration, Google Drive permissions/availability, data-retention terms,
and provider timeout/retry behavior are To be verified.

Whether to modify retrieval, timeout, retry, logging, sanitization, or storage
behavior for CHANGE-003 is not decided by this card. Refer to SPEC-003 OQ-04
through OQ-12 and human approval.

## Evidence

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/analyze_resume.html`
- `devopssite/templates/user_menu.html`
- `requirements.txt`
- `docker-compose.yml`
- `env_example`
