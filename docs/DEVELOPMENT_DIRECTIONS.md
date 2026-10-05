# Candidate Development Directions

## 1. Purpose

This document records proposed development directions for the master’s research work. These are not baseline facts; they are provisional directions derived from the current inherited codebase and should be treated as recommendations rather than confirmed requirements.

## 2. Direction 1: AI-assisted hiring and skill matching enhancement

### Current state
- Resume analysis is already implemented using an OpenAI-compatible API and Google Drive CV download flow.
- Project and skill models already exist for matching broad work categories.

### Proposed change
Extend the existing AI CV analysis into a structured skill extraction and project-fit recommendation workflow. Use project skills, freelancer skills, and ratings to suggest better matches and highlight missing capabilities.

### Why it is useful
- Builds on an existing feature instead of replacing core workflows.
- Aligns with the current business purpose of the application.
- Could improve the freelancer/project matching functionality while preserving the current monolithic architecture.

### Expected complexity
Medium

### Likely modules affected
- `freelancer`
- `project`
- `skill`
- `rating`
- `notification`

### Possible measurable outcomes
- structured skill extraction from CV content;
- improved relevance of freelancer/project matches;
- reduced manual review effort for employer project selection.

## 3. Direction 2: Work-request workflow hardening and approval lifecycle

### Current state
- `WorkRequest`, status transitions, and notifications already exist.
- The workflow is implemented but appears basic and not heavily validated.

### Proposed change
Formalize the request lifecycle, validation rules, and approval flow for employer/freelancer interactions. Add clearer status transitions and stronger notification semantics tied to project outcomes.

### Why it is useful
- Extends a current workflow without redesigning the application.
- Produces a more reliable collaboration process for both employers and freelancers.
- Gives the project a clearer operational lifecycle for future research work.

### Expected complexity
Medium

### Likely modules affected
- `workrequest`
- `project`
- `notification`
- `adminpannel`
- templates

### Possible measurable outcomes
- clearer acceptance/rejection workflow;
- reduced ambiguous project-status handling;
- stronger auditability for collaboration decisions.

## 4. Direction 3: Improved testing and regression safety for the platform

### Current state
- Some view tests exist, but many modules remain untested or placeholder-based.
- There is no visible CI pipeline or automated execution workflow in the repository.

### Proposed change
Build a targeted test suite around authentication, project lifecycle, freelancer flows, notification triggers, and major request flows. Add repeatable local/CI test execution as part of the baseline quality process.

### Why it is useful
- Reduces risk before future feature work.
- Creates a stable platform for agent-driven development.
- Improves confidence in changes to the inherited codebase.

### Expected complexity
Low to Medium

### Likely modules affected
- all app test modules
- repository automation configuration (if later added)
- settings and environment bootstrapping

### Possible measurable outcomes
- higher confidence in regressions;
- clearer validation of project and freelancer flows;
- a repeatable test baseline for future master’s research tasks.

## 5. Comparison Criteria for Selecting Final Directions

The selection criteria implicit in the current documentation are:

- relevance to the existing system;
- feasibility within the current architecture;
- differing complexity levels;
- clear acceptance criteria;
- suitability for agent-driven development;
- measurability of outcomes.

These directions are provisional and should be reviewed against the actual repository state before being adopted as the final master’s scope.

See [BASELINE.md](BASELINE.md) for the concise inherited baseline and [ARCHITECTURE.md](ARCHITECTURE.md) for the architecture background.
Testing, CI/CD, containerization, and validation improvements are treated as cross-cutting supporting activities and are described separately in [TESTING_DEVOPS_BASELINE.md](TESTING_DEVOPS_BASELINE.md).
