# Baseline of the Existing System

## 1. Purpose

This document captures the inherited state of the system before agent-driven development begins in the master’s research project. It records only what is confirmed by the current repository contents and does not assume behavior beyond the visible source, configuration, migrations, tests, and documentation.

## 2. System Overview

### What the system does
The repository contains a Django-based application for connecting employers/project owners with freelancers. The visible implementation includes:

- user registration and login with a custom email-based authentication model;
- project creation, listing, viewing, updating, deletion, and search/filtering;
- freelancer profiles, portfolio management, and CV-related analysis;
- work request lifecycle handling between freelancers and employers;
- rating records associated with projects;
- messaging between users through Django Channels/WebSockets;
- notification creation and email delivery;
- admin functionality for user and project/freelancer management.

### Target users
The code indicates at least three categories of users:

- registered users represented by the custom `User` model;
- freelancers represented by the `Freelancer` model and related profile data;
- project owners or employers represented by the project ownership and workflow logic.

### Main business purpose
The current code supports a freelance marketplace or collaboration platform where users can:

- create and manage projects;
- browse and search for freelancers or project opportunities;
- submit and track work requests;
- evaluate collaboration outcomes;
- communicate and coordinate work.

### Main user roles
The repository confirms a role-based user model and role-specific workflows, but the exact role taxonomy beyond the model structure is not fully enumerated in the code. See [ARCHITECTURE.md](ARCHITECTURE.md) for the detailed domain model.

## 3. Current Technology Stack

### Programming language and version
- Python is used throughout the repository.
- A specific Python version is not pinned in the repository. No `pyproject.toml`, `runtime.txt`, or equivalent version file was found.
- Some Django 5.1 documentation references are visible in comments, but the actual installed framework version is not confirmed from project files alone.

### Backend framework
- Django is the main backend framework.
- Django REST Framework is enabled and configured.
- Django Channels is included for WebSocket messaging.
- DRF SimpleJWT is configured for JWT-based authentication.

### Database
- PostgreSQL is configured via the Django backend and environment-driven variables.
- The repository includes migrations and ORM models, indicating a relational database setup.

### Frontend technologies
- The application uses server-rendered Django templates.
- Static assets are organized in the static directories.
- No independent SPA framework is visible in the repository.

### AI/LLM integrations
- OpenAI client usage is confirmed in the resume-analysis workflow.
- The app uses environment variables for API key, base URL, and model selection.
- This is visible in the freelancer resume-analysis code.

### External APIs/services
- Google Drive file download flow is used for CV processing.
- SMTP email delivery is configured for notifications.
- Redis is configured for the Channels layer.

### Package/dependency management
- A root-level `requirements.txt` is present and is now the current dependency manifest.
- Dependency installation is documented as `pip install -r requirements.txt`.
- See [TESTING_DEVOPS_BASELINE.md](TESTING_DEVOPS_BASELINE.md) for the related DevOps environment notes.

## 4. Current Implemented Functionality Summary

The repository confirms the following areas, with evidence drawn from the current code and tests:

- Authentication: Implemented
- User/profile management: Implemented
- Freelancer functionality: Implemented
- Employer functionality: Implemented
- Projects: Implemented
- Search/filtering: Partially implemented
- Work requests: Implemented
- Ratings: Partially implemented
- Messaging: Implemented
- Notifications: Implemented
- Administration: Implemented
- AI resume analysis: Implemented

For detailed implementation evidence, see [ARCHITECTURE.md](ARCHITECTURE.md) and the relevant app modules.

## 5. Known Current Limitations Summary

The current repository state shows the following limitations:

- development-oriented security settings (`DEBUG = True`, `ALLOWED_HOSTS = []`);
- partial rather than complete automated test coverage;
- no visible CI/CD pipeline or Docker automation;
- external service configuration remains environment-dependent;
- AI resume analysis and notification flows are operational but not deeply hardened;
- search/filtering is present but not broad or comprehensive;
- some code appears legacy or partially migrated.

See [TESTING_DEVOPS_BASELINE.md](TESTING_DEVOPS_BASELINE.md) for the detailed testing and DevOps baseline and [DEVELOPMENT_DIRECTIONS.md](DEVELOPMENT_DIRECTIONS.md) for future proposal directions.

## 6. Baseline Constraints

The following constraints should guide all future development work:

- The current system must not be rewritten from scratch.
- Existing behavior must not be silently changed.
- Significant future changes should remain traceable from requirement to implementation and validation.
- Unknown facts must remain explicit and marked as “To be verified” rather than assumed.
- The inherited bachelor’s project state is a baseline for research, not a production-ready system.

## 7. Baseline Version

- Baseline date: To be filled
- Git commit SHA: To be filled
- Git tag: To be filled
- Branch: To be filled

## 8. Open Questions / To Be Verified

The following items could not be reliably determined from the repository alone:

- exact Python version in the active environment;
- full dependency list and package versions from the live environment;
- current Git branch, commit SHA, and tag state;
- whether the system is deployed externally or only local prototype state;
- the exact production deployment configuration, if any exists outside the repository;
- exact business rules for freelancer statuses, project approval, and work request states;
- whether the AI resume-analysis integration is using OpenAI, OpenRouter, or another provider in the live environment;
- whether the production database schema matches the migration state.

See [ARCHITECTURE.md](ARCHITECTURE.md), [TESTING_DEVOPS_BASELINE.md](TESTING_DEVOPS_BASELINE.md), and [DEVELOPMENT_DIRECTIONS.md](DEVELOPMENT_DIRECTIONS.md) for the detailed current-system references.
