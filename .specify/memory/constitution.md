<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections:
  - Principle I: Code Quality
  - Principle II: Testing Standards
  - Principle III: User Experience Consistency
  - Principle IV: Performance Requirements
  - Section: Quality Gates
  - Section: Development Workflow
  - Governance
- Removed sections: N/A
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ aligned (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ aligned (Success Criteria covers performance/UX)
  - .specify/templates/tasks-template.md ✅ aligned (test-first, polish phase covers performance)
- Follow-up TODOs: None
-->

# Project Constitution

## Core Principles

### I. Code Quality (NON-NEGOTIABLE)

- All code MUST pass static analysis (linting, formatting) before merge; zero warnings policy enforced in CI.
- Every function/method MUST have a single, clear responsibility. Functions exceeding 40 lines MUST be refactored or explicitly justified.
- Naming MUST be descriptive and consistent: variables, functions, classes, and files follow the project's established naming convention (e.g., camelCase for JS/TS, snake_case for Python).
- Dead code, commented-out code, and TODO hacks MUST NOT be merged into the main branch. Temporary workarounds require a tracked issue with a deadline.
- All public APIs (functions, classes, endpoints) MUST have documentation describing purpose, parameters, return values, and error conditions.
- Code duplication MUST be eliminated: any logic repeated in three or more locations MUST be extracted into a shared utility or module.

**Rationale**: Consistent code quality reduces review friction, lowers defect density, and accelerates onboarding. Enforcement at CI level ensures no human oversight gaps.

### II. Testing Standards (NON-NEGOTIABLE)

- Unit test coverage MUST meet or exceed 80% line coverage for all new code. Critical paths (authentication, payment, data persistence) MUST reach 95%.
- Test-first development is REQUIRED for bug fixes: a failing test reproducing the bug MUST exist before the fix is implemented.
- Integration tests MUST cover every cross-service boundary, database interaction, and external API call.
- Tests MUST be deterministic: no flaky tests allowed in CI. Any test failing intermittently MUST be quarantined and fixed within 48 hours.
- Test naming MUST follow the pattern `test_<unit>_<scenario>_<expected>` (or framework equivalent) so intent is immediately clear.
- End-to-end (E2E) tests MUST validate all P1 user stories defined in the feature specification.

**Rationale**: Rigorous testing catches regressions early, enables fearless refactoring, and serves as executable documentation of expected behavior.

### III. User Experience Consistency

- All user-facing interfaces MUST follow a shared design system (component library, color palette, typography, spacing scale). Deviations require explicit design review approval.
- Response messages, error messages, and notifications MUST use consistent tone, terminology, and formatting across the entire application.
- Interaction patterns (navigation flow, form validation, loading states, empty states, error states) MUST be uniform: identical actions produce identical feedback regardless of context.
- Accessibility MUST meet WCAG 2.1 AA compliance at minimum: keyboard navigability, screen reader compatibility, sufficient color contrast (≥4.5:1 for normal text).
- All UI changes MUST be reviewed against the design system checklist before merge. Visual regression tests are RECOMMENDED for critical flows.

**Rationale**: Consistency builds user trust and reduces cognitive load. A predictable interface accelerates task completion and lowers support burden.

### IV. Performance Requirements

- Page/screen initial load MUST complete within 2 seconds on a standard broadband connection (≥10 Mbps). Subsequent navigations MUST complete within 500ms.
- API response time MUST NOT exceed 200ms at p95 under normal load. Endpoints exceeding this threshold MUST be profiled and optimized or explicitly exempted with documented justification.
- Memory consumption MUST remain stable under sustained load: no memory leaks. Long-running processes MUST demonstrate stable memory usage over a 24-hour soak test.
- Bundle size (frontend) MUST NOT exceed the established budget (defined per project). Any dependency adding >50KB gzipped MUST be approved in a design review.
- Database queries MUST avoid N+1 patterns. All queries on tables exceeding 10K rows MUST use appropriate indexes and MUST be reviewed via EXPLAIN/query plan analysis.
- Performance benchmarks MUST be included in CI for critical paths. Any regression exceeding 10% MUST block the merge.

**Rationale**: Performance directly impacts user retention and satisfaction. Budgets and automated checks prevent gradual degradation that manual review misses.

## Quality Gates

- **Pre-commit**: Linting, formatting, and type checking MUST pass locally before commit.
- **Pull Request**: All unit tests, integration tests, and performance benchmarks MUST pass. Code review by at least one team member is REQUIRED.
- **Pre-merge**: E2E tests for affected user stories MUST pass. Coverage thresholds MUST be met. No new accessibility violations detected.
- **Pre-deploy**: Staging environment smoke tests MUST pass. Performance benchmarks MUST show no regression beyond 10% tolerance.

## Development Workflow

- All changes MUST go through feature branches following the naming convention `<issue-number>-<short-description>`.
- Commits MUST follow Conventional Commits format (e.g., `feat:`, `fix:`, `refactor:`, `test:`, `docs:`).
- Pull requests MUST reference the related spec or issue. PR description MUST include: what changed, why, and how to test.
- Breaking changes MUST be documented in the PR, flagged in the commit message (`BREAKING CHANGE:`), and communicated to affected teams before merge.
- Hotfixes MUST follow the same testing and review standards; expedited review is permitted but MUST NOT skip tests.

## Governance

- This constitution supersedes all other development practices and conventions. In case of conflict, the constitution takes precedence.
- Amendments REQUIRE: (1) a written proposal with rationale, (2) review by at least two team members, (3) a migration plan for existing code if the change affects current practices.
- All code reviews and PR approvals MUST verify compliance with these principles. Reviewers MUST cite the specific principle when requesting changes.
- Complexity beyond what the constitution prescribes MUST be justified in writing and approved before implementation.
- Constitution version follows semantic versioning: MAJOR for principle removals/redefinitions, MINOR for additions/expansions, PATCH for clarifications.
- Compliance review SHOULD be conducted quarterly to identify drift and update the constitution as needed.

**Version**: 1.0.0 | **Ratified**: 2026-02-14 | **Last Amended**: 2026-02-14
