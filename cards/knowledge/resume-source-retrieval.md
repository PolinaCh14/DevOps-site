# Resume Source / Retrieval Contract

Status: Draft

## Purpose

Record the repository-confirmed source and retrieval behavior for freelancer
resume analysis. This card describes the current implementation; it does not
approve a replacement or modification.

## Current source contract

The `Freelancer` model stores `cv` as a nullable, optional `CharField`. It is
not a `FileField` and does not itself enforce that the value is a URL, a
Google Drive link, or resume text.

Profile creation accepts `cv` from a textarea and profile editing accepts it
from a text input. Profile detail templates render the value as the `href` of
a resume link. The analysis view passes the stored value to the analysis
service as a file URL.

Evidence:

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/views.py`: `create_freelancer_profile`,
  `update_freelancer_profile`, and `analyze_resume_view`
- `devopssite/templates/freelancer_profile_create.html`
- `devopssite/templates/freelancer_profile_edit.html`
- `devopssite/templates/user_freelancer_detail.html`

## Current retrieval contract

`devopssite/freelancer/utils.py` implements the following sequence:

1. `extract_file_id` searches the given string for `/d/<id>`, where the ID
   contains letters, digits, underscores, or hyphens.
2. `download_from_google_drive` makes a streaming `requests.Session().get`
   request to `https://drive.google.com/uc?export=download`, passing the ID as
   an `id` parameter.
3. If the response contains a cookie whose name starts with
   `download_warning`, the code repeats the request with its cookie value as
   `confirm`.
4. `_save_response_content` writes non-empty chunks to the provided local
   destination.
5. `analyze_resume` always selects `downloaded_cv_<freelancer_id>.docx` as
   that destination.

There is no Google Drive SDK, OAuth flow, service account, or authenticated
Drive API client in the inspected implementation. The actual accessibility
requirements of the file in a deployed Drive account are To be verified.

## Current retrieval limitations

- The link parser recognizes the `/d/<id>` form; other Drive URL forms are not
  confirmed as supported.
- The HTTP request does not set an explicit timeout, check the response status,
  validate content type or file size, or explicitly close the session.
- A response body is written regardless of whether it represents a successful
  Drive download.
- The path is relative to the process working directory and uses a stable
  per-freelancer filename. Concurrent requests for one freelancer can therefore
  target the same file.
- No cleanup of downloaded files is present in the service.
- The destination suffix is always `.docx`, irrespective of the actual
  downloaded format.
- `read_file` has PDF and DOCX branches, but the fixed DOCX suffix means PDF
  retrieval is not confirmed end-to-end and is likely misclassified.
- There is no OCR path for image-only or scanned documents.

## Current supported types

The text reader branches on the local filename extension:

- `.pdf`: PyMuPDF page text extraction.
- `.docx`: python-docx paragraph and table text extraction.
- Other extensions: `ValueError` for unsupported type.

This is a reader-level capability, not proof that retrieval correctly
identifies or preserves either type. No other types or OCR behavior are
confirmed.

## Relevant change constraints

CHANGE-003 says to preserve the existing CV retrieval flow where practical and
not replace Google Drive unless repository analysis reveals a blocking reason.
Whether format detection, download validation, or other retrieval hardening is
included in this change remains Pending Human Approval under SPEC-003 OQ-06,
OQ-07, and OQ-11.

## Evidence

- Detailed Drive retrieval contract:
  `cards/knowledge/resume-google-drive-retrieval.md`
- Detailed extraction contract: `cards/knowledge/resume-text-extraction.md`
- `devopssite/freelancer/models.py`
- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `devopssite/templates/freelancer_profile_create.html`
- `devopssite/templates/freelancer_profile_edit.html`
- `devopssite/templates/user_freelancer_detail.html`
- `changes/CHANGE-003-structured-ai-resume-analysis.md`
