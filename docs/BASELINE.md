# Baseline of the Existing System

## 1. Purpose

This document captures the state of the system inherited from the bachelor’s project before agent-driven development in the master’s research begins. It records only what can be confirmed from the repository as it currently exists, without modifying the application code or assuming functionality that is not visible in the source, configuration, migrations, tests, and templates.

## 2. System Overview

### What the system does
The repository contains a Django-based web application for connecting employers/project owners with freelancers. The visible implementation includes:
- user registration and login with a custom email-based authentication model;
- project creation, listing, viewing, updating, deletion, and search/filtering;
- freelancer profiles, portfolio management, and CV-related analysis;
- work request lifecycle handling between freelancers and employers;
- rating data associated with projects;
- messaging between users through Django Channels/WebSockets;
- notification creation and email delivery;
- an admin panel for user and project/freelancer management.

### Target users
The code indicates at least three categories of users:
- registered users, represented by the custom User model;
- freelancers, represented by the Freelancer model and related profile data;
- project owners/employers, represented by the relationship between Project.user and WorkRequest/project workflow.

### Main business purpose
The primary business purpose visible in the code is to support a freelance marketplace or project collaboration platform where users can:
- create and manage projects;
- find or be matched with freelancers;
- submit work requests;
- evaluate and rate collaboration outcomes;
- communicate and track project-related decisions.

### Main user roles
The code includes a Role model and a role foreign key on the User model. The repository also includes distinct views and app logic for employer and freelancer workflows. The explicit roles are not fully enumerated in documentation, but the code confirms a role-based user model and role-specific flows.

## 3. Current Technology Stack

### Programming language and version
- Python is clearly used throughout the repository.
- A specific Python version is not pinned in the repository. No pyproject.toml, runtime.txt, setup.cfg, or similar version file was found.
- The repository comments reference Django 5.1 documentation in settings.py, but the actual installed framework version is not confirmed from project files alone.

### Backend framework
- Django is the main backend framework.
- Django REST Framework is included in the installed apps and configured in settings.py.
- Django Channels is included for WebSocket messaging.
- DRF SimpleJWT is configured for JWT authentication.

### Database
- PostgreSQL is configured in settings.py through the django.db.backends.postgresql engine.
- Database connection settings are environment-driven via os.getenv(...) values.
- The repository includes migrations for the domain models, indicating a relational database workflow.

### Frontend technologies
- The application uses server-rendered Django templates.
- Static assets are organized under the static and templates directories.
- No React, Vue, Angular, or other SPA framework is visible in the repository.
- JavaScript is present in static assets, but the frontend stack is not a modern component framework based on the repository contents.

### AI/LLM integrations
Confirmed in code:
- The freelancer analysis utility imports the OpenAI Python client.
- It calls a configured OpenAI-compatible API endpoint using environment variables API_KEY, OPEN_AI_BASE_URL, and AI_MODEL.
- The code analyzes uploaded CV text and returns LLM feedback in Ukrainian.

This is confirmed in freelancer/utils.py and in the resume analysis view logic.

### External APIs/services
Confirmed integrations visible in the code:
- Google Drive file retrieval for CV analysis, using a file ID extracted from a Drive URL.
- OpenAI-compatible chat completions endpoint for resume analysis.
- SMTP email delivery for notifications through Django email settings and send_mail in notification/tasks.py.
- Redis Channel Layer for WebSockets in settings.py.

### Package/dependency management
- A root-level requirements.txt file is present in the repository and is the current dependency manifest.
- Dependency installation is performed with: `pip install -r requirements.txt`.
- The listed packages are consistent with the Django-based stack visible in the code: Django, Django REST Framework, Channels, Celery, Daphne, and supporting libraries for email, Redis, and OpenAI integrations.
- The environment still requires a local virtual environment and `.env` configuration for database and secret settings.

### Development tools/configuration visible in repo
Visible configuration and tooling:
- Django manage.py entry point.
- Locust load-test script at devopssite/locustfile.py.
- Python-dotenv via load_dotenv() in settings and utility code.
- .env and env_example files for environment variables.
- Many Django test files using django.test.TestCase.
- No visible lint configuration, formatter configuration, or CI workflow files were found.

## 4. Current Architecture

### Main applications/modules
The main Django project is devopssite, and the repository contains the following major apps:
- users: authentication, base user model, profile access
- project: project creation, listing, search, details, and status handling
- skill: skill metadata model
- freelancer: freelancer profiles, portfolio, CV-related analysis, profile management
- workrequest: project collaboration requests and status changes
- rating: rating records linked to projects and users
- notification: notification model, signals, and email delivery
- adminpannel: admin-focused views for user/project/freelancer administration
- chat: messaging and WebSocket chat support
- portfolio: portfolio-related app presence alongside freelancer-specific portfolio logic

### Separation of responsibilities
The repository follows a conventional Django modular structure:
- models and business logic are organized by domain app;
- URL routing is split by app;
- views handle request/response logic and template rendering;
- migrations handle schema versioning for each app;
- static/templates directories serve the HTML and asset layer.

### Backend/frontend relationship
The system is predominantly server-rendered. Django views render HTML templates, and template files exist under devopssite/templates. The frontend is not implemented as a separate API client or a SPA architecture in the repository.

### Database interaction
Database usage is via Django ORM models and migrations. The core data model includes foreign-key relationships such as User -> Role, Project -> User/Status, Freelancer -> User/Status, WorkRequest -> Project/Freelancer, Notification -> Sender/Receiver/Type, and Message -> Sender/Receiver.

### External integrations
The code confirms the following external dependencies:
- PostgreSQL database;
- Redis for Channels;
- SMTP email;
- OpenAI-compatible API for CV analysis;
- Google Drive download flow for resume files.

### Important directories
- devopssite/manage.py — project entry point
- devopssite/devopssite/settings.py — project settings and environment configuration
- devopssite/devopssite/urls.py — root URL routing
- devopssite/templates — UI templates
- devopssite/static — static assets
- devopssite/media — media storage
- devopssite/*/migrations — schema history per app
- devopssite/locustfile.py — performance/load test script

### Architecture summary
This is a monolithic Django web application with multiple domain apps and a template-based UI. It uses the Django ORM for persistence, Redis + Channels for WebSocket chat, OpenAI-compatible LLM integration for CV analysis, and a conventional project URL/view/model structure. It is not structured as a microservice system or a decoupled frontend-backend architecture.

## 5. Main Domain Entities

The following entities are directly visible in the source code and migrations.

### User
- Purpose: application user identity and authentication.
- Important relationships: linked to Role; used by Project, Freelancer, Notification, Message, and Rating.
- Evidence: users/models.py

### Role
- Purpose: user roles classification.
- Important relationships: foreign key on User.
- Evidence: users/models.py

### Freelancer
- Purpose: freelancer profile record, containing CV/text and experience.
- Important relationships: linked to User; can have many portfolio entries, skill associations, and work requests.
- Evidence: freelancer/models.py

### FreelancerStatus
- Purpose: status for freelancer profile state.
- Important relationships: Freelancer.id_status.
- Evidence: freelancer/models.py

### FreelancerSkill
- Purpose: mapping of skills to freelancer records.
- Important relationships: many-to-many-like join table via freelancer and skill.
- Evidence: freelancer/models.py

### Portfolio
- Purpose: freelancer portfolio items with title, description, photo, and URL.
- Important relationships: linked to Freelancer.
- Evidence: freelancer/models.py or portfolio-related logic in views and templates.

### Skill
- Purpose: reusable skill taxonomy.
- Important relationships: used by FreelancerSkill and ProjectSkill.
- Evidence: skill/models.py

### Project
- Purpose: project/project-request record created by a user.
- Important relationships: linked to User (owner/employer) and Status; may be associated with ProjectSkill and WorkRequest.
- Evidence: devopssite/project/models.py

### Status
- Purpose: generic status classification for projects.
- Important relationships: used by Project.status.
- Evidence: project/models.py

### ProjectSkill
- Purpose: mapping of skills onto projects.
- Important relationships: Project and Skill.
- Evidence: project/models.py

### WorkRequestStatus
- Purpose: status values for collaboration requests.
- Important relationships: WorkRequest.id_status.
- Evidence: workrequest/models.py

### WorkRequest
- Purpose: freelancer request to collaborate on a project.
- Important relationships: linked to Project and Freelancer; has a lifecycle status.
- Evidence: workrequest/models.py and views.py

### Message
- Purpose: asynchronous chat message record.
- Important relationships: sender and receiver users; timestamp and deletion booleans.
- Evidence: chat/models.py and chat/consumers.py

### Rating
- Purpose: user/project evaluation record.
- Important relationships: appraiser, evaluated user, project.
- Evidence: rating/models.py

### NotificationType
- Purpose: notification category/type.
- Important relationships: Notification.id_type.
- Evidence: notification/models.py

### Notification
- Purpose: application notification record delivered to a user.
- Important relationships: sender, receiver, type, creation time.
- Evidence: notification/models.py and notification/signals.py

## 6. Current Implemented Functionality

The following functionality is assessed based on the repository code and tests.

### Authentication
Status: Implemented
Evidence:
- User model is a custom AbstractBaseUser + PermissionsMixin in users/models.py.
- Custom EmailBackend is present in users/my_authentication_backend.py.
- Routes for register/login/logout/profile exist in users/urls.py and users/views.py.
- settings.py configures LOGIN_URL and JWT auth.

### User/profile management
Status: Implemented
Evidence:
- Users can register, log in, log out, and retrieve/update profile information.
- update_user_profile route exists in users/urls.py.
- adminpannel includes user profile update and delete flows.
- freelancer profile creation/update views exist and are exercised by tests.

### Freelancer functionality
Status: Implemented
Evidence:
- Freelancer model, skills, CV, and experience fields are present.
- freelancer/views.py includes freelancer list, detail, profile creation/update, and portfolio actions.
- freelancer/tests.py contains tests for create/update/detail flows and portfolio operations.

### Employer functionality
Status: Implemented
Evidence:
- Project creation and management views exist in project/views.py.
- Employers can view projects and project requests through workrequest/views.py.
- Work request status changes are implemented around project and freelancer IDs.

### Projects
Status: Implemented
Evidence:
- Project model and CRUD-oriented views exist.
- project/urls.py contains users_projects, create_project, project_delete, update_project, and search views.
- project/tests.py verifies project list, detail, create, and delete behavior.

### Search/filtering
Status: Partially implemented
Evidence:
- Search endpoints exist for user projects and project listing, and views include search parameters and filters by user, status, and skill.
- The repository does not show a broad or highly robust search framework; there are no advanced filters, full-text search, or indexing configuration visible.

### Work requests
Status: Implemented
Evidence:
- WorkRequest model and views for employer/freelancer work request listings and status changes exist.
- Signals create notifications when a request is submitted or modified.
- The project includes status handling for accepted/rejected or in-flight workflows.

### Ratings
Status: Partially implemented
Evidence:
- Rating model and create_rating view exist.
- The repository indicates ratings are associated with user/project evaluations.
- There are no substantial tests or usage flows visible beyond the model and route structure, so implementation appears present but not deeply validated.

### Messaging
Status: Implemented
Evidence:
- chat/models.py defines Message entities.
- chat/consumers.py implements async websocket connection, message history retrieval, and sending logic.
- chat/routing.py exposes websocket_urlpatterns.
- ASGI configuration routes websockets through the chat consumer.

### Notifications
Status: Implemented
Evidence:
- Notification model and NotificationType are present.
- Signals create notifications on work request creation and status changes.
- Email sending is implemented via Django mail in notification/tasks.py.
- This is a confirmed integration path, though the workflow is basic and not fully hardened.

### Administration
Status: Implemented
Evidence:
- Django admin is enabled in settings.py.
- adminpannel URLs and views provide extra administrative actions for user/project/freelancer management.
- adminpannel app is present.

### AI resume analysis
Status: Implemented
Evidence:
- freelancer/utils.py contains extract_file_id, download_from_google_drive, read_file, and analyze_resume.
- The view analyze_resume_view in freelancer/views.py invokes the function and renders the analysis result.
- The route exists in freelancer/urls.py.
- This is a real implementation, although it is environment-dependent and not covered by a dedicated test suite.

### Missing or not found functionality
The repository does not confirm the following features in the current code:
- separate microservices architecture;
- production deployment automation;
- CI pipeline configuration;
- infrastructure-as-code or container orchestration files;
- a project-wide dependency lock file;
- comprehensive test coverage for all modules;
- a dedicated job-matching engine beyond the existing model structure and basic filter views.

## 7. Current Testing State

### Test framework
The repository uses Django’s built-in testing framework via django.test.TestCase and Client. No pytest configuration or alternate framework configuration was found.

### Test directories/files
Visible test files include:
- devopssite/freelancer/tests.py
- devopssite/project/tests.py
- devopssite/users/tests.py
- devopssite/chat/tests.py
- devopssite/adminpannel/tests.py
- devopssite/notification/tests.py
- devopssite/portfolio/tests.py
- devopssite/rating/tests.py
- devopssite/skill/tests.py
- devopssite/workrequest/tests.py

### What functionality is covered
The repository shows active tests for:
- freelancer profile creation/update/detail;
- portfolio creation/update/delete/listing;
- project listing/detail/create/delete;
- basic project model assertions.

The visible evidence is in freelancer/tests.py and project/tests.py.

### What appears untested or still placeholder-like
Many test files exist but are essentially placeholder files with only:
- from django.test import TestCase
- # Create your tests here.

This includes chat, adminpannel, notification, rating, skill, users, and workrequest test modules. The codebase therefore has partial test coverage, not a full regression suite.

### Unit/integration/e2e status
- Unit-like view tests: present for a subset of project and freelancer flows.
- Integration tests using Django Client are present for some request/response flows.
- End-to-end browser tests are not visible.
- No coverage report or coverage tooling was found.

### Obvious gaps confirmed from the repo
- Large portions of the application lack dedicated tests.
- No test runner automation or CI pipeline is configured.
- AI CV analysis, email notifications, and WebSocket chat are not covered by visible automated tests.
- This is a confirmed limitation in the current repository state.

## 8. Current DevOps State

### Git-related configuration
- A Git repository is present at the root of the project.
- .gitignore exists.
- No specific branch protection, release process, or repo policy file was found in the repository content inspected.

### Docker/Docker Compose
Status: Not found
Evidence:
- No Dockerfile was found at the repo root or project directories.
- No docker-compose.yml or docker-compose.yaml files were found.

### CI/CD workflows
Status: Not found
Evidence:
- No .github/workflows directory or workflow YAML files were found.
- No other build/test automation configuration was visible in the repository.

### Deployment configuration
Status: Not found or not configured in repo
Evidence:
- settings.py is a development-oriented configuration with DEBUG = True and ALLOWED_HOSTS = [].
- No deployment manifest, environment-specific config, reverse proxy configuration, or production settings file was found.

### Environment configuration
Status: Present, with a dependency manifest and environment-specific values
Evidence:
- Root-level requirements.txt exists and is used for installation via `pip install -r requirements.txt`.
- Root-level .env exists for local machine-specific values.
- env_example lists DB variables and DJANGO_SECRET_KEY.
- These values are loaded using python-dotenv.
- The project still depends on external services such as PostgreSQL, Redis, and SMTP/LLM configuration defined in settings and environment variables.

### Scripts
Visible scripts include:
- devopssite/manage.py
- devopssite/locustfile.py
These are present and confirm a Django project entry point and load-testing script.

### Linting/formatting
Status: Not found
Evidence:
- No configuration for black, flake8, ruff, isort, or equivalent was found.
- No pre-commit configuration was found.

### Automated test execution
Status: Not configured in repo
Evidence:
- Django tests exist, but no project-level CI or makefile/task runner was visible.
- No tox.ini, pytest.ini, setup.cfg with test commands, or GitHub Actions workflow was found.
- Manual execution via Django commands is implied but not repo-automated.

## 9. External Integrations

The following integrations are confirmed by code and configuration:

### PostgreSQL database
- Confirmed in settings.py.
- Data source is environment-based and managed by Django ORM.

### Redis for Channels
- Confirmed in settings.py via CHANNEL_LAYERS and host 127.0.0.1:6379.
- Used for Django Channels WebSocket communication.

### OpenAI-compatible LLM API
- Confirmed in freelancer/utils.py.
- API client is initialized with API_KEY, OPEN_AI_BASE_URL, and AI_MODEL.
- The application sends CV text to the model and renders the response.

### Google Drive
- Confirmed in freelancer/utils.py.
- A Google Drive file ID is extracted from a Drive URL and downloaded.
- This is used to pull CV files for resume analysis.

### SMTP email
- Confirmed in settings.py through EMAIL_BACKEND and email variables.
- Notification sending is implemented in notification/tasks.py using Django send_mail.

### Not confirmed or not present
- No confirmed OpenRouter integration was found.
- No confirmed Google Drive API client library or OAuth flow was found; the implementation uses direct URL/file ID download logic.
- No SSO or third-party identity provider integration is visible.
- No payment gateway or external marketplace API integration is visible.

## 10. Known Current Limitations

The following limitations are supported by the repository contents:

### Development-only security settings
- settings.py sets DEBUG = True and ALLOWED_HOSTS = [].
- This strongly indicates the project is not configured as a production deployment baseline.
- Evidence: devopssite/devopssite/settings.py

### Dependency installation is now reproducible, but environment setup remains external
- The repository now includes requirements.txt, so dependency installation is reproducible with `pip install -r requirements.txt`.
- The application still requires local environment configuration and external services (PostgreSQL, Redis, SMTP, AI endpoint) to run correctly.
- Evidence: root requirements.txt, env_example, and environment-driven values in settings.py.

### Partial and incomplete automated test coverage
- Several modules have placeholder test files and some active tests only cover a subset of flows.
- Important modules such as chat, notification, rating, and adminpannel are not meaningfully tested in the visible repository state.
- Evidence: test files containing only “Create your tests here.” and the limited visible test cases in freelancer/tests.py and project/tests.py.

### AI analysis is environment-dependent and likely fragile
- CV analysis depends on external environment variables and a remote API endpoint.
- Error handling is minimal and there is no visible retry, validation, or queueing layer.
- Evidence: freelancer/utils.py and freelancer/views.py.

### Notification workflow is basic and not fully hardened
- Notifications are created via signals and email is sent immediately.
- The code uses print-based exception handling and basic HTML templates.
- Evidence: notification/signals.py and notification/tasks.py.

### Search/filtering is not clearly comprehensive
- Search routes exist, but there is no evidence of a broader search framework or complete filtering model across the whole platform.
- Evidence: project/views.py and related URLs.

### Some code appears to be legacy or partially migrated
- In settings.py, there are duplicate imports and some conflicting settings values (for example STATIC_URL defined twice).
- The codebase includes some older naming patterns and rough implementations that suggest an evolving prototype rather than a fully hardened production system.
- Evidence: devopssite/devopssite/settings.py and various model files.

## 11. Candidate Development Directions

The following are recommendations for future master’s work. They are not baseline facts; they are realistic directions derived from the current system state.

### 1. AI-assisted hiring and skill matching enhancement
Current state:
- Resume analysis is already implemented using an OpenAI-compatible API and Google Drive CV download flow.
- Project and skill models already exist for matching broad work categories.

Proposed change:
- Extend the existing AI CV analysis into a structured skill extraction and project-fit recommendation workflow.
- Use project skills, freelancer skills, and ratings to suggest better matches and missing capabilities.

Why it is useful:
- It builds on an existing feature instead of replacing the platform.
- It aligns with the application’s current business purpose and available data model.

Expected complexity: Medium
Likely modules affected:
- freelancer
- project
- skill
- rating
- notification

### 2. Work-request workflow hardening and approval lifecycle
Current state:
- WorkRequest, status transitions, and notifications already exist.
- The workflow is implemented but appears basic and not heavily validated.

Proposed change:
- Formalize request lifecycle states, validation rules, audit history, and clearer employer/freelancer status transitions.
- Add robust validation and stronger notifications tied to project outcomes.

Why it is useful:
- It extends the existing collaboration process without redesigning the platform.
- It creates a more reliable project execution flow for both users and administrators.

Expected complexity: Medium
Likely modules affected:
- workrequest
- project
- notification
- adminpannel
- templates

### 3. Improved testing and regression safety for the platform
Current state:
- Some view tests exist, but many test files are placeholders and critical areas remain untested.
- There is no CI pipeline or automated execution workflow.

Proposed change:
- Build a targeted test suite around authentication, project lifecycle, freelancer flows, notification triggers, and API-like view behavior.
- Add repeatable local/CI test execution.

Why it is useful:
- It reduces risk before further feature development.
- It creates a stable baseline for future agent-driven changes.

Expected complexity: Low to Medium
Likely modules affected:
- all app test modules
- repository automation configuration (if added later)
- settings and environment bootstrapping

## 12. Baseline Constraints

The following constraints should govern future work and any agent-driven development:
- The system must not be rewritten from scratch.
- Existing behavior must not be silently changed.
- Future significant changes should be traceable from requirement to implementation and validation.
- Unknown facts must remain explicit and should be marked as To be verified rather than assumed.
- The current state must be treated as a inherited bachelor’s baseline, not a production-ready system.

## 13. Baseline Version

- Baseline date: To be filled
- Git commit SHA: To be filled
- Git tag: To be filled
- Branch: To be filled

## Open Questions / To Be Verified

The following items could not be reliably determined from the repository and should be confirmed manually before or during the master’s research:
- exact Python version in the active environment;
- full dependency list and package versions from the real environment;
- whether the repository is connected to a remote Git provider and the current origin URL;
- exact production deployment setup, if any exists outside this repo;
- whether the live system is currently deployed or only a local prototype;
- the exact domain/business rules for freelancer status, project approval, and work request states;
- whether the AI resume analysis integration is expected to use OpenAI, OpenRouter, or another provider; and which model is configured in the live environment;
- the actual database schema in production versus the local migration state;
- whether any undocumented functionality exists in local branches or uncommitted code.

## Short summary

1. Main system state: This repository is a Django monolith for a freelance/project collaboration platform with user accounts, projects, freelancer profiles, work requests, chat, notifications, ratings, and a CV-analysis feature powered by an OpenAI-compatible API.
2. Strongest candidate development directions: AI-assisted skill/project matching; work-request lifecycle hardening; and testing/validation improvements for the existing platform.
3. Important missing or uncertain information to verify manually: exact runtime/dependency versions, production deployment status, live environment configuration, and the actual current branch/commit state.
