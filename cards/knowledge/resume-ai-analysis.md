# Resume AI Analysis Contract

Status: Draft

## Purpose

Capture the current AI request contract and provider configuration used by
freelancer resume analysis. It is not approval of a new prompt, provider, or
schema.

## Current request flow

`devopssite/freelancer/utils.py` defines `analyze_resume(file_url,
freelancer_id)`. It:

1. extracts a Drive file ID and downloads a local file;
2. calls `read_file` to extract resume text;
3. constructs `openai.OpenAI` with environment values `API_KEY` and
   `OPEN_AI_BASE_URL`;
4. calls `client.chat.completions.create` using `AI_MODEL`;
5. sends one system and one user message; and
6. returns `response.choices[0].message.content` without parsing or validating
   its structure.

No model response-format/schema parameter, application-level retry policy,
application-level timeout setting, or result persistence is visible in this
flow.

## Current prompt

System instruction (Ukrainian, paraphrased here only for readability): act as
a resume-writing expert; carefully analyze the candidate's resume; provide
clear, constructive recommendations in Ukrainian about improving structure,
content, style, errors, and similar issues.

The user message prefixes the extracted text with “Ось текст резюме:” and
includes the entire extracted resume text.

The prompt does not define fields, JSON syntax, evidence requirements, limits,
scoring, uncertainty rules, or a method to distinguish missing CV evidence
from a candidate lacking a skill.

## Current response contract

The service returns the provider's first choice message content as a free-form
string. The code does not check for `None`, empty content, Markdown validity,
or semantic correctness. There is no structured output contract today.

## Configuration and dependencies

- Python package: `openai==1.76.0` in `requirements.txt`; the SDK is configured
  with a custom base URL, making the specific live provider/model To be
  verified.
- `API_KEY`, `OPEN_AI_BASE_URL`, and `AI_MODEL` are passed to the web
  container by `docker-compose.yml`, each with an empty default.
- `env_example` does not document these three AI variables.
- `python-dotenv` is loaded in the utility module.

No actual credentials, configured endpoint, or selected model can be inferred
from repository source. The live provider, model capabilities, rate limits,
structured-output support, token limits, privacy terms, and provider-side
retry/timeout behavior are To be verified.

## Failure behavior and constraints

Provider construction/request/response errors are not translated in the
utility. They propagate to `analyze_resume_view`, whose broad exception
handler returns status 500 and the exception string in JSON. Empty extracted
text is not rejected before calling the model. The utility has no application
retry for malformed output because output is not currently parsed.

The full extracted resume is sent to the configured external AI service.
Retention and processing practices of that service are To be verified.

## CHANGE-003 considerations

The target direction is structured analysis, but the exact response schema and
invalid-output behavior are not approved. See SPEC-003 OQ-01 through OQ-05 and
OQ-12. Its proposed field set is a Draft proposal only.

## Evidence

- `devopssite/freelancer/utils.py`
- `devopssite/freelancer/views.py`
- `requirements.txt`
- `docker-compose.yml`
- `env_example`
- `changes/CHANGE-003-structured-ai-resume-analysis.md`
