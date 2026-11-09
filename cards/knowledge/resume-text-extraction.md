# Resume Text Extraction Contract

Status: Draft

## Purpose

Capture the current local-file text extraction behavior and its format
limitations for freelancer resume analysis.

## Current extraction flow

`analyze_resume` in `devopssite/freelancer/utils.py` downloads a file to
`downloaded_cv_<freelancer_id>.docx`, then passes that local path to
`read_file`.

`read_file` chooses its extraction logic from the filename extension:

- `.pdf`: opens the file with PyMuPDF (`fitz`) and concatenates `get_text()`
  results from each page.
- `.docx`: opens the file with `python-docx`; extracts text from paragraphs
  and tables in document-body order.
- Any other extension: raises `ValueError` for unsupported type.

## Supported-type boundary

PDF and DOCX are the only confirmed branches in the reader. This does not
establish that both formats work end-to-end: the current downloader always
assigns a `.docx` suffix, independent of the content downloaded from Drive.
Therefore retrieved PDF documents may be sent to the DOCX parser, and
end-to-end PDF support is To be verified.

No OCR or image-based text recognition path is present. Text extraction
quality for scanned/image-only files is not guaranteed. No explicit check
rejects an empty or whitespace-only extracted result before it is sent to the
AI service.

## Failure behavior

- Unsupported extension raises `ValueError`.
- Invalid/mismatched PDF or DOCX content can raise parser errors.
- Parser exceptions propagate through the analysis service and are caught by
  the analysis view's broad exception handler, which responds with status 500
  and the exception string.
- Empty extracted content is currently allowed to proceed to the AI request.
- No cleanup of the staged file is performed by this extraction flow.

## Dependencies

- `PyMuPDF==1.25.5` in `requirements.txt` for PDF extraction.
- `python-docx==1.1.2` in `requirements.txt` for DOCX extraction.

Installed runtime availability is To be verified. No additional formats or
conversion behavior are confirmed.

## CHANGE-003 boundary

Handling extraction failures and empty content is unresolved in SPEC-003
OQ-04, OQ-07, and OQ-12. Adding OCR or additional formats is out of the
proposed bounded scope unless separately approved.

## Evidence

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `requirements.txt`
- `changes/CHANGE-003-structured-ai-resume-analysis.md`
