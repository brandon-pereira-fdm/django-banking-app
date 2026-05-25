---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Automated tests are mandatory for banking MVP rules. Include
`TEST-###` tasks for every applicable requirement and, at minimum, Personal
Account creation without opening deposit, Personal Account starting at SGD 0.00,
Business Account creation with SGD 7,000.00 or more, rejection below
SGD 7,000.00, duplicate email, duplicate Personal Account phone,
duplicate Business Account UEN rejection, password hashing,
positive deposits for both account types, zero/negative deposit rejection,
Personal Account withdrawal/transfer success and negative-balance rejection,
Business Account approved withdrawal success, unapproved outgoing Business
Account non-completion, Business Account minimum-balance rejection, phone-number
Personal transfer lookup, UEN Business transfer lookup, mismatched recipient
identifier rejection, safe recipient confirmation, unknown recipient rejection,
zero/negative transfer rejection, incoming Business Account money without
approval, multiple PENDING Business requests, no fund reservation while PENDING,
FAILED approval-time revalidation outcomes, absence of persisted APPROVED
status, UUID transaction IDs, linked transfer operation IDs, and atomic rollback
on failed financial operations.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- Include `BR-###`, `FR-###`, `SEC-###`, `NFR-###`, and `TEST-###`
  traceability references where applicable

## Path Conventions

- **Django banking MVP**: Django project/apps plus Django templates and tests
- Paths shown below assume a Django banking MVP structure - adjust based on
  plan.md without introducing technology outside the constitution

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit-tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management
- [ ] T010 Configure SGD-only Decimal-based money validation helpers
- [ ] T011 Configure Personal Account phone and Business Account UEN recipient identifier validation
- [ ] T012 Configure immutable UUID transaction IDs and transfer operation IDs
- [ ] T013 Configure PENDING/COMPLETED/REJECTED/CANCELLED/FAILED approval lifecycle without persisted APPROVED status
- [ ] T014 Configure secrets loading from environment or ignored local config
- [ ] T015 Configure `.gitignore` for secrets, local SQLite DBs, and virtual environments

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (MANDATORY for applicable banking rules) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] [TEST-###] Test [BR-###/FR-###] in tests/test_[name].py
- [ ] T017 [P] [US1] [TEST-###] Integration test for [user journey] in tests/test_[name].py

### Implementation for User Story 1

- [ ] T018 [P] [US1] Create [Entity1] model in [app]/models.py
- [ ] T019 [P] [US1] Create [Entity2] model in [app]/models.py
- [ ] T020 [US1] Implement [Service] in [app]/services.py (depends on T018, T019)
- [ ] T021 [US1] Implement [view/form/template] in [app]/[location]/[file]
- [ ] T022 [US1] Add server-side validation, ownership, recipient identifier, balance, approval, and atomicity checks
- [ ] T023 [US1] Update traceability matrix for [BR-###/FR-###/TEST-###] with code and test paths

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (MANDATORY for applicable banking rules) ⚠️

- [ ] T024 [P] [US2] [TEST-###] Test [BR-###/FR-###] in tests/test_[name].py
- [ ] T025 [P] [US2] [TEST-###] Integration test for [user journey] in tests/test_[name].py

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create [Entity] model in [app]/models.py
- [ ] T027 [US2] Implement [Service] in [app]/services.py
- [ ] T028 [US2] Implement [view/form/template] in [app]/[location]/[file]
- [ ] T029 [US2] Integrate with User Story 1 components (if needed)
- [ ] T030 [US2] Update traceability matrix for [BR-###/FR-###/TEST-###] with code and test paths

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (MANDATORY for applicable banking rules) ⚠️

- [ ] T031 [P] [US3] [TEST-###] Test [BR-###/FR-###] in tests/test_[name].py
- [ ] T032 [P] [US3] [TEST-###] Integration test for [user journey] in tests/test_[name].py

### Implementation for User Story 3

- [ ] T033 [P] [US3] Create [Entity] model in [app]/models.py
- [ ] T034 [US3] Implement [Service] in [app]/services.py
- [ ] T035 [US3] Implement [view/form/template] in [app]/[location]/[file]
- [ ] T036 [US3] Update traceability matrix for [BR-###/FR-###/TEST-###] with code and test paths

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional regression tests for financial, authorization, and
  traceability rules
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before views/forms/templates
- Core implementation before integration
- Traceability matrix updates before story checkpoint
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test [FR-###] [business rule] in tests/test_[name].py"
Task: "Integration test for [user journey] in tests/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in [app]/models.py"
Task: "Create [Entity2] model in [app]/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Do not add databases, frontend frameworks, payment platforms, or distributed
  infrastructure without a constitutional amendment
