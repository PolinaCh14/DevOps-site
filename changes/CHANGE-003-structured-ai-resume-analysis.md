# CHANGE-003 — Structured AI Resume Analysis

Status: Approved

## Purpose

Evolve the existing resume/CV analysis functionality into a structured, validated, and testable AI-assisted analysis flow.

Repository analysis confirmed that the current flow retrieves a CV through a
Google Drive download URL, extracts PDF/DOCX text, and sends the extracted
content to a configured external OpenAI-compatible chat-completions service.
See the approved SPEC-003 and associated knowledge cards for the verified
current contract and target behavior.

## High-level goals

- preserve the existing CV retrieval flow where practical;
- replace or supplement free-form AI output with a structured analysis result;
- validate AI output before using or displaying it;
- handle malformed, incomplete, empty, or failed AI responses safely;
- preserve existing useful behavior unless explicitly changed;
- make the analysis flow objectively testable and reviewable.

## Approved target direction

The structured result contains exactly five required keys:

- `summary`;
- `detected_skills`;
- `strengths`;
- `improvement_areas`;
- `recommendations`.

Arrays may be empty when no supported items are found. No numeric score,
dimension scores, or ranking values are included. Exact field types,
validation limits, failure behavior, allowed files, and acceptance criteria
are specified in the approved SPEC-003 and TASK-003.

## Constraints

- do not replace Google Drive unless repository analysis shows a blocking reason;
- do not redesign the entire freelancer profile;
- do not introduce general AI matching or employer ranking;
- do not redesign unrelated authentication or notification behavior;
- do not broaden this change into frontend modernization or CI/CD redesign.

## Approval state

CHANGE-003, SPEC-003, and TASK-003 are approved for implementation. The
implementation is to be performed in a separate Implementer session and must
remain within the approved task scope.
