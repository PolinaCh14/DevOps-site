# Testing and DevOps Baseline

## 1. Purpose

This document captures the inherited current testing and DevOps state of the repository before master’s research work begins. It records only what is visible in the repository as it currently exists and does not assume broader operational maturity beyond the codebase evidence.

## 2. Current Testing State

### Test framework
The repository uses Django’s built-in testing framework via `django.test.TestCase` and Django `Client`. No pytest configuration or alternate framework configuration was found.

### Test files visible in the repository
Visible test files include:

- `devopssite/freelancer/tests.py`
- `devopssite/project/tests.py`
- `devopssite/users/tests.py`
- `devopssite/chat/tests.py`
- `devopssite/adminpannel/tests.py`
- `devopssite/notification/tests.py`
- `devopssite/portfolio/tests.py`
- `devopssite/rating/tests.py`
- `devopssite/skill/tests.py`
- `devopssite/workrequest/tests.py`

### Existing test coverage
The visible active tests include:

- freelancer profile creation/update/detail checks;
- portfolio creation/update/delete/listing checks;
- project listing/detail/create/delete validation;
- basic project model assertions.

The visible evidence is concentrated in `devopssite/freelancer/tests.py` and `devopssite/project/tests.py`.

### Testing gaps
A significant number of test modules are still placeholder files containing only:

- `from django.test import TestCase`
- `# Create your tests here.`

This includes, at minimum, the test files for chat, adminpannel, notification, rating, skill, users, and workrequest. The repository therefore has partial test coverage rather than a full regression suite.

### Unit/integration/e2e status
The repository shows:

- unit-like view tests for selected project and freelancer flows;
- integration-like tests using Django `Client` for request and response flow checks;
- no visible end-to-end browser test suite;
- no coverage report or coverage tooling found in the repository.

## 3. Existing Test Coverage

The repository demonstrates some working Django tests for core project flow and freelancer profile flow, but not enough to claim complete coverage. The current evidence indicates that the system is only partially validated in its current state.

## 4. Testing Gaps

Confirmed obvious gaps:

- AI CV analysis is not covered by visible automated tests.
- WebSocket chat behavior is not covered by visible automated tests.
- Notification email logic is not covered by visible automated tests.
- Admin and workflow modules remain largely untested.
- There is no project-wide CI pipeline that executes the suite automatically.

## 5. Current Git State

- A Git repository is present at the root of the project.
- `.gitignore` exists.
- No specific branch protection, release process, or repo policy file was found in the repository content inspected.
- The current branch, tag, and commit SHA were not reliably confirmed from repository files alone and are therefore To be verified.

## 6. Containerization

### Docker / Docker Compose
Status: Not found
Evidence:

- No `Dockerfile` was found at the repo root or project directories.
- No `docker-compose.yml` or `docker-compose.yaml` files were found.

## 7. CI/CD

Status: Not found
Evidence:

- No `.github/workflows` directory or workflow YAML files were found.
- No other build/test automation configuration was visible in the repository.

## 8. Deployment Configuration

Status: Not found or not configured in repo
Evidence:

- `devopssite/devopssite/settings.py` contains development-oriented settings such as `DEBUG = True` and `ALLOWED_HOSTS = []`.
- No deployment manifest, environment-specific config, reverse proxy configuration, or production settings file was found.

## 9. Environment Configuration

Status: Present, with a dependency manifest and environment-specific values
Evidence:

- Root-level `requirements.txt` exists and is used for installation via `pip install -r requirements.txt`.
- Root-level `.env` exists for local machine-specific values.
- `env_example` lists DB variables and `DJANGO_SECRET_KEY`.
- These values are loaded using `python-dotenv`.
- The project still depends on external services such as PostgreSQL, Redis, SMTP, and an LLM endpoint configured through environment variables.

## 10. Tooling and Scripts

Visible tooling and scripts include:

- `devopssite/manage.py` — Django project entry point
- `devopssite/locustfile.py` — load-testing script using Locust
- `.env` and `env_example` — environment configuration templates
- Python-dotenv integration in settings and utility code

### Linting / formatting
Status: Not found
Evidence:

- No configuration for Black, Flake8, Ruff, isort, or similar tooling was found.
- No pre-commit configuration was found.

### Automated test execution
Status: Not configured in repo
Evidence:

- Django tests exist, but no project-level CI or makefile/task runner was visible.
- No `tox.ini`, `pytest.ini`, `setup.cfg` with test commands, or GitHub Actions workflow was found.
- Manual execution via Django commands is implied but not automated in the repository.

## 11. Current DevOps Limitations

The following limitations are supported by the repository contents:

- The project is not configured as a production deployment baseline.
- The repository has a dependency manifest, but environment-specific runtime services remain external to the codebase.
- There are partial tests and placeholder test files rather than a full regression suite.
- There is no CI/CD pipeline or container orchestration configuration.
- There are no visible linting or formatting gate checks.

## 12. Open Questions

The repository does not reliably confirm the following:

- exact Python version in the active environment;
- full dependency list and package versions from the real environment;
- whether the repository is connected to a remote Git provider and the current origin URL;
- exact deployment setup outside the repository;
- whether the system is live or only local prototype state;
- the actual runtime environment for PostgreSQL, Redis, SMTP, and AI endpoint configuration.

See [BASELINE.md](BASELINE.md) for the concise project baseline and [ARCHITECTURE.md](ARCHITECTURE.md) for the architecture and domain model details.
