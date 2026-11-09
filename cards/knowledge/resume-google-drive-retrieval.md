# Resume Google Drive Retrieval Contract

Status: Draft

## Purpose

Record only the repository-confirmed Google Drive link parsing and download
behavior used by resume analysis. This is a current-state contract, not an
approval to retain or change it.

## Current Drive reference

`Freelancer.cv` is a nullable string field and the profile create/edit forms
accept a general text value. There is no model-level validation requiring a
Drive link. The analysis service treats the value as a Drive file URL.

`extract_file_id` in `devopssite/freelancer/utils.py` searches for a path
segment matching `/d/<id>` using letters, digits, underscores, and hyphens.
Other link formats, such as URLs without that path segment, are not confirmed
as supported.

## Current download sequence

`download_from_google_drive(file_id, destination)`:

1. Creates a `requests.Session`.
2. Sends a streamed GET to
   `https://drive.google.com/uc?export=download` with `id=<file_id>`.
3. Checks response cookies for a name beginning with `download_warning`.
4. If found, sends a second streamed GET with the same ID and a `confirm`
   parameter containing the cookie value.
5. Saves non-empty response chunks of 32,768 bytes to the destination.

There is no Google Drive SDK, OAuth flow, service account, or authenticated
Drive API client in the inspected implementation. Actual sharing/permission
requirements and deployed access are To be verified.

## Confirmed limitations and failure behavior

- The requests do not pass an explicit timeout.
- The code does not call `raise_for_status` or otherwise validate HTTP status.
- It does not validate content type or maximum download size.
- Response content is saved even if it is an error page or other unexpected
  payload.
- The session/response lifecycle is not explicitly closed in this function.
- Network/request errors can propagate; downstream failures are caught by the
  analysis view's broad exception handler and returned as status-500 JSON
  containing the exception string.
- The caller supplies a relative path named
  `downloaded_cv_<freelancer_id>.docx`; the Drive response's real type/name is
  not used to select the extension.
- The same freelancer ID produces the same path for concurrent calls, and
  this flow does not clean up the staged file.

## CHANGE-003 boundary

The change request prefers preserving retrieval where practical and says not
to replace Drive unless a blocking reason is found. Whether to fix file type
detection, HTTP validation, timeouts, cleanup, or any other retrieval behavior
is Pending Human Approval under SPEC-003 OQ-06, OQ-07, OQ-11, and OQ-12.

## Evidence

- `devopssite/freelancer/models.py`
- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `requirements.txt`
- `changes/CHANGE-003-structured-ai-resume-analysis.md`
