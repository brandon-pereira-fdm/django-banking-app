# Tasks: Banking MVP v3.0.0

**Input**: Design documents from `specs/001-banking-mvp/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/server-rendered-flows.md`, `quickstart.md`, `traceability.md`, `refactoring-impact.md`, `checklists/requirements-quality-v3.md`

**Tests**: Automated tests are mandatory for banking, authentication, employee-access security, approval permissions, auditability, and financial integrity.

**Organization**: Tasks are dependency ordered by the required v3 phases. User story labels map to the specification user stories:

- `US1`: Register for the correct account product
- `US2`: Use a Personal Account
- `US3`: Create a Business Account as initial AUTHORISER
- `US4`: Provision and govern employee access
- `US5`: Transfer money safely
- `US6`: Submit and resolve Business outgoing requests
- `US7`: Navigate the Midnight Ledger interface
- `US8`: View Transaction, Approval, and Access Audit histories

## Phase 1: Superseded Implementation Review and Safe Reset/Refactor Preparation

**Purpose**: Inventory v2/v1 implementation remnants and prepare the approved local reset/refactor path before building the v3 model.

- [ ] T001 Inspect `banking/models.py`, `users/models.py`, `banking/migrations/`, and `users/migrations/` for invitation, multi-membership, authorised-Personal-Account, exactly-one-Authoriser, and persisted APPROVED assumptions; document findings in `specs/001-banking-mvp/refactoring-impact.md` for FR-066, BR-016, BR-036 verification by review.
- [ ] T002 Inspect `banking/services/`, `banking/forms.py`, `banking/views.py`, and `banking/urls.py` for invitation acceptance, Business Account selector, multi-Business membership, and old transfer ownership logic; document replacement targets in `specs/001-banking-mvp/refactoring-impact.md` for FR-032-FR-034, FR-066 verification by review.
- [ ] T003 Inspect `templates/`, `static/css/`, and `staticfiles/css/` for `Invitations`, `Invite Business User`, `Store Invitation`, invitation registration, Business Account selector, and sparse v2 UI assumptions; document UI replacement targets in `specs/001-banking-mvp/refactoring-impact.md` for UX-009-UX-029 verification by review.
- [ ] T004 Inspect `users/tests/` and `banking/tests/` for invitation, multiple Business membership, Personal Account authorisation, exactly-one-Authoriser, and old selector tests; document which tests must be replaced in `specs/001-banking-mvp/refactoring-impact.md` for TEST-012, TEST-034, TEST-035 verification by review.
- [ ] T005 Identify active obsolete checklist files in `specs/001-banking-mvp/checklists/` and record archival actions needed before implementation gates in `specs/001-banking-mvp/refactoring-impact.md` for CHK-VERSION-007 verification by checklist scan.
- [ ] T006 Identify local SQLite database files and generated migration state affected by the v3 schema redesign; record the approved local reset or forward-migration strategy in `specs/001-banking-mvp/refactoring-impact.md` for NFR-001, NFR-005 verification by review.
- [ ] T007 Verify the Phase 1 inventory by searching for `Invitation`, `Invite Business User`, `Store Invitation`, `Business Account selector`, `authorised_personal`, `APPROVED`, and multi-membership terms across `users/`, `banking/`, `templates/`, `static/`, and `specs/001-banking-mvp/`; record all active implementation hits in `specs/001-banking-mvp/refactoring-impact.md` for FR-066, BR-036 verification by search output.

**Checkpoint**: Superseded v1/v2 implementation components are listed for replacement/removal before v3 model work starts.

## Phase 2: Project Configuration, Repository Hygiene, and Test Bootstrap

**Purpose**: Establish the Django project baseline and repository hygiene needed before schema work.

- [ ] T008 Validate the Django project package, `users` app, and `banking` app are registered correctly in `bankapp/settings.py` for plan architecture verification by `python3 manage.py check`.
- [ ] T009 Configure or validate `AUTH_USER_MODEL` and authentication settings in `bankapp/settings.py` before fresh v3 migrations for FR-002, FR-006-FR-007 verification by settings review.
- [ ] T010 Validate template and static directories in `bankapp/settings.py` for server-rendered templates and custom CSS per UX-001 verification by `python3 manage.py check`.
- [ ] T011 Validate dependencies in `requirements.txt` contain only Django and Waitress unless explicitly justified by `plan.md` for NFR-001 verification by dependency review.
- [ ] T012 Configure environment-based `DJANGO_SECRET_KEY` loading in `bankapp/settings.py` and document local fallback behavior for SEC-011 verification by settings review.
- [ ] T013 Update `.gitignore` to exclude `.env`, local SQLite databases, virtual environments, Python caches, local secret files, and generated local assets for SEC-011 verification by `git status --ignored`.
- [ ] T014 Establish baseline Django test command behavior with `python3 manage.py test` and record current expected failures caused by pending v3 refactor in implementation notes for TEST-001-TEST-069 verification by test output.
- [ ] T015 Verify local app startup check with `python3 manage.py check` after configuration changes for NFR-001 verification by command output.

## Phase 3: Login Identity Model and Authentication Context Enforcement

**Purpose**: Implement immutable Personal versus Business Employee login identity and route protection.

### Tests

- [ ] T016 [P] [US1] Create identity model tests in `users/tests/test_authentication.py` for Personal identity, Business employee identity, duplicate email rejection, password hashing, valid sign-in, and invalid sign-in covering FR-002-FR-005 and TEST-003, TEST-011.
- [ ] T017 [P] [US1] Create access context tests in `users/tests/test_access_context.py` for Personal denial from Business routes and Business Employee denial from Personal routes covering FR-006-FR-010, SEC-002-SEC-003, TEST-004-TEST-006.

### Implementation

- [ ] T018 [US1] Refactor `users/models.py` to define `CustomUser` fields for globally unique email, display name/username, and `login_context` values `PERSONAL` and `BUSINESS_EMPLOYEE` covering FR-001-FR-003 verification by model tests.
- [ ] T019 [US1] Refactor `users/managers.py` to normalize email, require login context, and use Django password hashing for `CustomUser` creation covering FR-002, SEC-001 verification by authentication tests.
- [ ] T020 [US1] Refactor `users/forms.py` login and identity forms so access context is set server-side by the selected route, never by a visible editable field, covering FR-006-FR-010 verification by form tests.
- [ ] T021 [US1] Refactor `users/views.py` and `users/urls.py` for sign-in, sign-out, and context-specific post-login routing covering FR-004-FR-005 verification by client tests.
- [ ] T022 [US1] Implement context guard helpers in `users/permissions.py` for Personal-only, Business-employee-only, authenticated-only, and safe denial behavior covering SEC-001-SEC-003 verification by access-context tests.
- [ ] T023 [US1] Run `python3 manage.py test users.tests.test_authentication users.tests.test_access_context` and fix only identity/context defects for TEST-003-TEST-006, TEST-011 verification by passing tests.

## Phase 4: Revised Banking, Employee Access, Request, Transaction, and Audit Models

**Purpose**: Replace v2 invitation/membership schema with the v3 data model.

### Tests

- [ ] T024 [US1] Create v3 structural model tests in `banking/tests/test_models.py` for PersonalAccount owner context, unique phone, BusinessAccount unique UEN, BusinessEmployeeAccess one-account scope, no employee balance/receiving identifier, role choices, access statuses, request statuses, no APPROVED, UUIDs, and distinct history entities covering FR-011-FR-097 and TEST-034, TEST-056.

### Implementation

- [ ] T025 [US1] Apply the approved local reset/refactor strategy by removing or replacing superseded uncommitted development migration files in `banking/migrations/` and `users/migrations/` without touching the database state, covering NFR-001 verification by file review.
- [ ] T026 [US1] Replace invitation and multi-membership model definitions in `banking/models.py` with `PersonalAccount`, `BusinessAccount`, `BusinessEmployeeAccess`, `CompletedFinancialTransaction`, `TransferOperation`, `BusinessOutgoingRequest`, and `AccessAuditEvent` per `data-model.md` covering FR-011-FR-097 verification by model tests.
- [ ] T027 [US1] Add model choice constants in `banking/models.py` for employee roles, employee access statuses, transaction types, request types, request statuses, and access audit event types covering FR-035-FR-036, FR-083-FR-084, FR-094 verification by model tests.
- [ ] T028 [US1] Add model validation in `banking/models.py` for exactly-one financial account references, Business employee user context, Personal owner context, positive completed transaction amounts, and no `APPROVED` status covering BR-001-BR-006, BR-036 verification by model tests.
- [ ] T029 [US1] Generate fresh v3 migration files with `python3 manage.py makemigrations --dry-run --check` first, then planned migration creation only during implementation task execution, covering NFR-005 verification by migration dry-run and file review.
- [ ] T030 [US1] Run `python3 manage.py test banking.tests.test_models` and fix only v3 model/schema defects for TEST-034, TEST-056 verification by passing tests.

## Phase 5: Shared Money Validation, Permission Guards, and Domain Service Foundations

**Purpose**: Build reusable validations, permission gates, and service patterns before workflows.

### Tests

- [ ] T031 [P] [US2] Create money validation tests in `banking/tests/test_money_validation.py` for valid Decimal, zero, negative, malformed, non-numeric, excessive precision, Personal `SGD 0.00`, Business `SGD 7,000.00`, and Business `SGD 6,999.99` boundaries covering BR-001-BR-006, TEST-038, TEST-059-TEST-060.
- [ ] T032 [P] [US4] Create permission helper tests in `banking/tests/test_access_control.py` for Personal owner, Business active employee, AUTHORISER-only, password-change-required denial, deactivated denial, and final-AUTHORISER protection covering SEC-001-SEC-007, TEST-050, TEST-066-TEST-067.

### Implementation

- [ ] T033 [US2] Implement SGD Decimal parsing, validation, and `SGD 0.00` formatting in `banking/services/money.py` covering BR-001-BR-006 verification by money validation tests.
- [ ] T034 [US4] Implement Business employee access lookup, active employee gate, AUTHORISER gate, password-change-required gate, deactivated gate, and final-active-AUTHORISER helper in `banking/services/access.py` covering FR-036-FR-066, SEC-004-SEC-007 verification by access-control tests.
- [ ] T035 [US1] Implement shared domain exceptions or validation result types in `banking/services/exceptions.py` and wire usage in `banking/services/__init__.py` covering NFR-003 verification by service tests.
- [ ] T036 [US1] Establish transaction-safe service patterns using `transaction.atomic()` in `banking/services/base.py` or service modules covering NFR-004 verification by later atomicity tests.
- [ ] T037 [US2] Run `python3 manage.py test banking.tests.test_money_validation banking.tests.test_access_control` and fix only foundational validation/permission defects for TEST-038, TEST-050, TEST-066 verification by passing tests.

## Phase 6: Public Midnight Ledger Foundation and Account Product Selection

**Purpose**: Provide public onboarding UI with clear product separation and no invitation terminology.

- [ ] T038 [P] [US7] Create public onboarding view tests in `users/tests/test_public_onboarding_views.py` for product separation, sign-in page access, no invitation terminology, and Midnight Ledger content covering UX-004-UX-006, TEST-068.
- [ ] T039 [US7] Replace or improve public base layout in `templates/base_public.html` and shared includes in `templates/includes/` for Midnight Ledger typography, alerts, and form error structure covering UX-001-UX-003 verification by view tests and manual review.
- [ ] T040 [US7] Implement product-selection route in `users/views.py`, `users/urls.py`, and `templates/users/account_type_selection.html` showing Personal phone/no-opening-deposit/individual-login and Business UEN/SGD7000/employee-access comparison covering UX-004-UX-006 verification by view tests.
- [ ] T041 [US7] Implement initial design tokens and public components in `static/css/midnight-ledger.css` covering UX-001-UX-003 verification by manual UI review.
- [ ] T042 [US7] Run `python3 manage.py test users.tests.test_public_onboarding_views` and manually verify no Invitation wording appears on public pages for TEST-068.

## Phase 7: Personal Registration and Personal Account Creation

**Purpose**: Implement Personal registration as a complete independent increment.

### Tests

- [ ] T043 [P] [US1] Create Personal registration tests in `banking/tests/test_personal_registration.py` for success, `SGD 0.00`, no opening deposit, duplicate email, duplicate phone, password hashing, no Business access, and Business page denial covering FR-011-FR-020, TEST-001, TEST-007-TEST-008.

### Implementation

- [ ] T044 [US1] Implement Personal registration form in `users/forms.py` for display name, email, password confirmation, unique phone number, and server-side `PERSONAL` context covering FR-011-FR-014 verification by registration tests.
- [ ] T045 [US1] Implement Personal registration service in `banking/services/registration.py` to atomically create `PERSONAL` user and PersonalAccount at `SGD 0.00` with no opening transaction covering FR-011-FR-015 verification by tests.
- [ ] T046 [US1] Implement Personal registration view and route in `users/views.py` and `users/urls.py` covering FR-011-FR-015 verification by client tests.
- [ ] T047 [US1] Implement Personal registration template in `templates/users/register_personal.html` with no Business controls and clear phone/no-opening-deposit messaging covering UX-005 verification by view tests.
- [ ] T048 [US1] Run `python3 manage.py test banking.tests.test_personal_registration users.tests.test_access_context` and fix only Personal registration defects for TEST-001, TEST-004, TEST-007-TEST-008.

## Phase 8: Business Account Registration and Initial AUTHORISER Creation

**Purpose**: Implement company Business Account opening with active initial AUTHORISER.

### Tests

- [ ] T049 [P] [US3] Create Business registration tests in `banking/tests/test_business_registration.py` for exact/above opening deposit, below/invalid amount rejection, display name, UEN, duplicate UEN, UEN normalization, active initial AUTHORISER, opening transaction UUID, initial audit events, no Personal Account, and atomic rollback covering FR-021-FR-031, TEST-002, TEST-009-TEST-010.

### Implementation

- [ ] T050 [US3] Implement Business registration form in `users/forms.py` for initial AUTHORISER display name, unique email, password, business display name, UEN normalization, and opening deposit covering FR-021, FR-028-FR-031 verification by tests.
- [ ] T051 [US3] Implement Business registration service in `banking/services/registration.py` to atomically create `BUSINESS_EMPLOYEE` user, BusinessAccount, active AUTHORISER access, opening transaction, and Access Audit events covering FR-022-FR-027 verification by tests.
- [ ] T052 [US3] Implement Business registration view and route in `users/views.py` and `users/urls.py` covering FR-021-FR-027 verification by client tests.
- [ ] T053 [US3] Implement Business registration template in `templates/users/register_business.html` explaining UEN, opening funding, provisioned employee access, and approval controls covering UX-006 verification by view tests.
- [ ] T054 [US3] Run `python3 manage.py test banking.tests.test_business_registration users.tests.test_access_context` and fix only Business registration defects for TEST-002, TEST-005, TEST-009-TEST-010.

## Phase 9: Authenticated Personal and Business Application Shells

**Purpose**: Create role-specific app shells and remove v2 navigation.

- [ ] T055 [P] [US7] Create UI permission/navigation tests in `banking/tests/test_ui_permissions.py` for Personal nav, Business nav, no Invitations nav, no Business Account selector, hidden controls plus server-side denial covering UX-007-UX-010, TEST-068-TEST-069.
- [ ] T056 [US7] Implement Personal authenticated shell in `templates/base_personal.html` with Dashboard, Personal Account, Deposit, Withdraw, Transfer, Transactions, and Sign Out only covering UX-007-UX-008 verification by UI tests.
- [ ] T057 [US7] Implement Business authenticated shell in `templates/base_business.html` with Business Dashboard, Deposit, Request Withdrawal, Request Transfer, Approvals, Team Access, Access Audit, Transactions, and Sign Out only covering UX-009-UX-010 verification by UI tests.
- [ ] T058 [US7] Remove or replace Invitations navigation and Business Account selector references in shared templates under `templates/` covering FR-034, FR-066 verification by UI tests and search.
- [ ] T059 [US7] Add reusable balance card, metric card, status badge, alert, confirmation, and data panel includes in `templates/includes/` covering UX-002-UX-003 verification by manual UI review.
- [ ] T060 [US7] Extend responsive authenticated layout CSS in `static/css/midnight-ledger.css` covering UX-001-UX-003, UX-027-UX-029 verification by manual UI review.
- [ ] T061 [US7] Run `python3 manage.py test banking.tests.test_ui_permissions` and fix only shell/navigation defects for TEST-068-TEST-069.

## Phase 10: Mandatory First-Login Password Change

**Purpose**: Enforce password-change-required status before normal Business access.

### Tests

- [ ] T062 [P] [US4] Create mandatory password-change tests in `banking/tests/test_password_workflows.py` for provisioned sign-in routing, Business page blocking, successful activation, post-activation access, and no password content in audit covering FR-039-FR-042, SEC-004, TEST-017-TEST-020.

### Implementation

- [ ] T063 [US4] Implement password-change-required guard in `users/permissions.py` or middleware selected by `plan.md` covering SEC-004 verification by password workflow tests.
- [ ] T064 [US4] Implement mandatory password-change service in `banking/services/access.py` using Django password setting, access transition to `ACTIVE`, and Access Audit event covering FR-041-FR-042, FR-094 verification by tests.
- [ ] T065 [US4] Implement mandatory password-change view and route in `users/views.py` and `users/urls.py` covering FR-041-FR-042 verification by client tests.
- [ ] T066 [US4] Implement branded password-change template in `templates/users/password_change_required.html` with restricted navigation and clear security checkpoint messaging covering UX-019 verification by UI review.
- [ ] T067 [US4] Run `python3 manage.py test banking.tests.test_password_workflows` and fix only mandatory password-change defects for TEST-017-TEST-020.

## Phase 11: Business Dashboard Redesign

**Purpose**: Deliver a non-sparse Business Dashboard with account context and operational summaries.

- [ ] T068 [P] [US7] Add Business Dashboard tests in `banking/tests/test_ui_permissions.py` for business name, UEN, employee name, role, access state, balance, retained minimum, pending count, recent activity, and AUTHORISER-only Team Access summary covering UX-011-UX-012, TEST-068-TEST-069.
- [ ] T069 [US7] Implement Business Dashboard query/service helpers in `banking/services/dashboard.py` for balance, pending count, recent transactions, recent approvals, and Team Access summary covering UX-011 verification by dashboard tests.
- [ ] T070 [US7] Implement Business Dashboard view in `banking/views.py` and route in `banking/urls.py` with active employee permission enforcement covering FR-048, SEC-003-SEC-005 verification by tests.
- [ ] T071 [US7] Implement redesigned Business Dashboard template in `templates/banking/business_dashboard.html` using summary cards and data panels covering UX-011-UX-012, UX-029 verification by UI tests and manual review.
- [ ] T072 [US7] Run `python3 manage.py test banking.tests.test_ui_permissions` and manually verify desktop layout uses content area effectively for TEST-068-TEST-069.

## Phase 12: Team Access Data Model Operations and Access Audit Foundations

**Purpose**: Replace Invitations with Team Access overview and audit utilities.

### Tests

- [ ] T073 [P] [US4] Create Team Access overview tests in `banking/tests/test_employee_access.py` for AUTHORISER management data, MEMBER read-only/denied controls, no active Invitations route, role/status display, and no password output covering FR-048, FR-066, FR-094, TEST-012, TEST-020.

### Implementation

- [ ] T074 [US4] Implement Access Audit event creation utility in `banking/services/access_audit.py` that never stores password values or hashes covering FR-094, SEC-008 verification by tests.
- [ ] T075 [US4] Implement Team Access list/query service in `banking/services/access.py` for employee rows and counts by active, AUTHORISER, PASSWORD_CHANGE_REQUIRED, and DEACTIVATED covering UX-014-UX-016 verification by tests.
- [ ] T076 [US4] Remove or replace invitation routes in `banking/urls.py` and invitation view handlers in `banking/views.py` with Team Access routes covering FR-066 verification by route tests and search.
- [ ] T077 [US4] Replace invitation screens and labels with Team Access template `templates/banking/team_access.html` covering UX-013-UX-018 verification by UI tests.
- [ ] T078 [US4] Remove or quarantine superseded invitation tests in `banking/tests/test_invitations_memberships.py` by replacing them with v3 employee-access tests covering TEST-012 verification by test suite.
- [ ] T079 [US4] Run `python3 manage.py test banking.tests.test_employee_access` and search for active invitation routes/labels for TEST-012, TEST-020 verification.

## Phase 13: Add Employee Access Provisioning

**Purpose**: AUTHORISERS directly create employee credentials scoped to one Business Account.

### Tests

- [ ] T080 [P] [US4] Extend `banking/tests/test_employee_access.py` for AUTHORISER creates MEMBER, AUTHORISER creates AUTHORISER, MEMBER denial, duplicate email, one Business Account scope, PASSWORD_CHANGE_REQUIRED, hashed temporary password, no plaintext/audit password, no invitation record, and atomic audit covering FR-037-FR-040, TEST-013-TEST-017, TEST-020.

### Implementation

- [ ] T081 [US4] Implement Add Employee Access form in `banking/forms.py` with display name, email, role, temporary password, confirmation, and AUTHORISER role warning validation covering FR-038 verification by tests.
- [ ] T082 [US4] Implement `provision_employee_access` service in `banking/services/access.py` for active AUTHORISER permission, global email uniqueness, Django password hashing, scoped BusinessEmployeeAccess creation, `PASSWORD_CHANGE_REQUIRED`, and Access Audit events covering FR-037-FR-040 verification by tests.
- [ ] T083 [US4] Implement Add Employee Access view and route in `banking/views.py` and `banking/urls.py` covering FR-037-FR-040 verification by client tests.
- [ ] T084 [US4] Implement Add Employee Access template and AUTHORISER-role confirmation in `templates/banking/add_employee_access.html` covering UX-017 verification by UI review.
- [ ] T085 [US4] Implement provisioning success template in `templates/banking/add_employee_access_success.html` with next-step instructions and no retrievable password display covering SEC-008 verification by tests.
- [ ] T086 [US4] Run `python3 manage.py test banking.tests.test_employee_access banking.tests.test_password_workflows` and fix only provisioning defects for TEST-013-TEST-020.

## Phase 14: Temporary Password Reset

**Purpose**: Let active AUTHORISERS reset another employee's temporary password securely.

### Tests

- [ ] T087 [P] [US4] Create password reset tests in `banking/tests/test_password_reset.py` for AUTHORISER resets MEMBER, AUTHORISER resets another AUTHORISER, MEMBER denial, normal access blocked until change, prior password invalid, no password audit content, and self-reset rejection covering FR-044-FR-047, TEST-021-TEST-024.

### Implementation

- [ ] T088 [US4] Implement temporary password reset form in `banking/forms.py` with password confirmation and target employee validation covering FR-044-FR-047 verification by tests.
- [ ] T089 [US4] Implement `reset_employee_temporary_password` service in `banking/services/access.py` for active AUTHORISER, same Business Account, no administrative self-reset, Django password replacement, `PASSWORD_CHANGE_REQUIRED`, and audit event covering FR-044-FR-047 verification by tests.
- [ ] T090 [US4] Implement reset password view and route in `banking/views.py` and `banking/urls.py` covering FR-044-FR-047 verification by client tests.
- [ ] T091 [US4] Implement reset confirmation and success templates in `templates/banking/reset_employee_password.html` covering UX-020 verification by UI review.
- [ ] T092 [US4] Run `python3 manage.py test banking.tests.test_password_reset banking.tests.test_password_workflows` and fix only reset workflow defects for TEST-021-TEST-024.

## Phase 15: Employee Promotion, Deactivation, and Reactivation

**Purpose**: Implement AUTHORISER-only access administration with final-AUTHORISER protection.

### Tests

- [ ] T093 [P] [US4] Create access administration tests in `banking/tests/test_access_administration.py` for MEMBER promotion, MEMBER admin denial, MEMBER deactivation, eligible AUTHORISER deactivation, final AUTHORISER rejection, deactivated access denial, reactivation requiring temporary password, retained records, and audit events covering FR-057-FR-065, TEST-027-TEST-033.

### Implementation

- [ ] T094 [US4] Implement promotion form/action service in `banking/services/access.py` and `banking/forms.py` for MEMBER to AUTHORISER and unsupported demotion rejection covering FR-057-FR-058 verification by tests.
- [ ] T095 [US4] Implement deactivation service in `banking/services/access.py` for MEMBER deactivation, eligible AUTHORISER deactivation, final AUTHORISER rejection, immediate access denial, retained records, and audit events covering FR-059-FR-063 verification by tests.
- [ ] T096 [US4] Implement reactivation service in `banking/services/access.py` requiring new temporary password and `PASSWORD_CHANGE_REQUIRED` status covering FR-064-FR-065 verification by tests.
- [ ] T097 [US4] Implement promotion, deactivation, and reactivation views/routes in `banking/views.py` and `banking/urls.py` covering FR-057-FR-065 verification by client tests.
- [ ] T098 [US4] Implement confirmation/result templates `templates/banking/promote_employee.html`, `templates/banking/deactivate_employee.html`, and `templates/banking/reactivate_employee.html` with last-AUTHORISER messaging covering UX-021 verification by UI review.
- [ ] T099 [US4] Run `python3 manage.py test banking.tests.test_access_administration banking.tests.test_access_control` and fix only access administration defects for TEST-027-TEST-033, TEST-066.

## Phase 16: Personal Dashboard, Deposits, and Withdrawals

**Purpose**: Complete Personal account viewing and immediate Personal deposit/withdrawal flows.

### Tests

- [ ] T100 [P] [US2] Create Personal deposit/withdrawal tests in `banking/tests/test_deposits_withdrawals.py` for valid deposit, invalid deposit, valid withdrawal, full-balance withdrawal to `SGD 0.00`, overdraft rejection, UUID transaction only on success, no balance change on rejection, and owner-only permission covering FR-016-FR-018, TEST-036, TEST-039-TEST-040.

### Implementation

- [ ] T101 [US2] Implement Personal Dashboard and account detail services/views in `banking/views.py` and `banking/urls.py` covering FR-011-FR-020 verification by tests.
- [ ] T102 [US2] Implement Personal Dashboard and account detail templates in `templates/banking/personal_dashboard.html` and `templates/banking/personal_account.html` with balance, phone identifier, quick actions, and recent transactions covering UX-007 verification by UI review.
- [ ] T103 [US2] Implement Personal deposit and withdrawal services in `banking/services/accounts.py` using Decimal validation, owner permission, atomic balance updates, and completed transaction UUIDs covering FR-016-FR-018, FR-087 verification by tests.
- [ ] T104 [US2] Implement Personal deposit/withdrawal forms, views, routes, confirmation pages, and success states in `banking/forms.py`, `banking/views.py`, `banking/urls.py`, and `templates/banking/` covering FR-016-FR-018 verification by client tests.
- [ ] T105 [US2] Run `python3 manage.py test banking.tests.test_deposits_withdrawals` and fix only Personal deposit/withdrawal defects for TEST-036, TEST-039-TEST-040.

## Phase 17: Business Deposits

**Purpose**: Allow active Business employees to deposit without approval.

### Tests

- [ ] T106 [P] [US6] Extend `banking/tests/test_deposits_withdrawals.py` for active MEMBER deposit, active AUTHORISER deposit, password-change-required denial, deactivated denial, Personal login denial, valid UUID transaction, invalid no movement, and no approval request covering FR-049, FR-077, TEST-037, TEST-049.

### Implementation

- [ ] T107 [US6] Implement Business deposit service in `banking/services/accounts.py` with active employee permission, no approval request, actor attribution, atomic balance update, and completed transaction UUID covering FR-049, FR-087 verification by tests.
- [ ] T108 [US6] Implement Business deposit form/view/route/templates in `banking/forms.py`, `banking/views.py`, `banking/urls.py`, and `templates/banking/business_deposit.html` covering FR-049 verification by client tests.
- [ ] T109 [US6] Run `python3 manage.py test banking.tests.test_deposits_withdrawals banking.tests.test_access_control` and fix only Business deposit defects for TEST-037, TEST-049.

## Phase 18: Recipient Resolution and Transfer Review

**Purpose**: Resolve Personal-by-phone and Business-by-UEN recipients before transfer completion/request.

### Tests

- [ ] T110 [P] [US5] Create recipient resolution tests in `banking/tests/test_recipient_resolution.py` for Personal phone lookup, Business UEN lookup, unknown phone, unknown UEN, mismatched identifier type, self-transfer rejection, and safe confirmation output covering FR-067-FR-072, TEST-043-TEST-045.

### Implementation

- [ ] T111 [US5] Implement recipient resolution service in `banking/services/transfers.py` for selected destination type, phone/UEN normalization, unknown/mismatch rejection, self-transfer rejection, and safe display data covering FR-067-FR-072 verification by tests.
- [ ] T112 [US5] Implement shared transfer recipient form and review view helpers in `banking/forms.py` and `banking/views.py` covering FR-069-FR-072 verification by tests.
- [ ] T113 [US5] Implement recipient confirmation templates in `templates/banking/transfer_review.html` with no sensitive email/credential disclosure covering SEC-009 verification by tests.
- [ ] T114 [US5] Run `python3 manage.py test banking.tests.test_recipient_resolution` and fix only recipient resolution defects for TEST-043-TEST-045.

## Phase 19: Personal Outgoing Transfers

**Purpose**: Complete valid Personal transfers immediately and atomically.

### Tests

- [ ] T115 [P] [US5] Create Personal transfer tests in `banking/tests/test_transfers.py` for Personal-to-Personal, Personal-to-Business, full-balance boundary, insufficient funds, invalid amount, linked debit/credit records, shared operation ID, and no partial state covering FR-073, FR-088-FR-091, TEST-041-TEST-046.

### Implementation

- [ ] T116 [US5] Implement Personal transfer service in `banking/services/transfers.py` with owner permission, sufficient funds, full-balance `SGD 0.00`, TransferOperation, linked transactions, and atomic update covering FR-073, FR-088-FR-091 verification by tests.
- [ ] T117 [US5] Implement Personal transfer form/view/route/result templates in `banking/forms.py`, `banking/views.py`, `banking/urls.py`, and `templates/banking/personal_transfer.html` covering FR-067-FR-073 verification by client tests.
- [ ] T118 [US5] Run `python3 manage.py test banking.tests.test_recipient_resolution banking.tests.test_transfers` and fix only Personal transfer defects for TEST-041-TEST-046.

## Phase 20: Business Outgoing Withdrawal Requests

**Purpose**: Submit Business withdrawal requests as Pending with no money movement.

### Tests

- [ ] T119 [P] [US6] Create Business request tests in `banking/tests/test_business_requests.py` for MEMBER withdrawal request, AUTHORISER withdrawal request, password-change-required denial, deactivated denial, Personal denial, PENDING status, no balance movement, and no completed financial record covering FR-050, FR-076-FR-079, TEST-047-TEST-049.

### Implementation

- [ ] T120 [US6] Implement Business withdrawal request service in `banking/services/approvals.py` with active employee permission, amount validation, requester attribution, `PENDING` creation, and no financial movement covering FR-050, FR-076-FR-079 verification by tests.
- [ ] T121 [US6] Implement Business withdrawal request form/view/route/templates in `banking/forms.py`, `banking/views.py`, `banking/urls.py`, and `templates/banking/business_withdrawal_request.html` covering FR-050, FR-076 verification by client tests.
- [ ] T122 [US6] Run `python3 manage.py test banking.tests.test_business_requests` and fix only withdrawal request defects for TEST-047-TEST-049.

## Phase 21: Business Outgoing Transfer Requests

**Purpose**: Submit Business transfer requests as Pending with no completed transfer records.

### Tests

- [ ] T123 [P] [US6] Extend `banking/tests/test_business_requests.py` for MEMBER Business-to-Personal request, MEMBER Business-to-Business request, AUTHORISER request, invalid destination, self-transfer rejection, inactive/restricted employee denial, and no completed money movement covering FR-051, FR-075-FR-079, TEST-047-TEST-049.

### Implementation

- [ ] T124 [US6] Implement Business transfer request service in `banking/services/approvals.py` using recipient resolution, active employee permission, `PENDING` creation, and no TransferOperation/transaction creation covering FR-051, FR-075-FR-079 verification by tests.
- [ ] T125 [US6] Implement Business transfer request form/view/route/templates in `banking/forms.py`, `banking/views.py`, `banking/urls.py`, and `templates/banking/business_transfer_request.html` covering FR-051, FR-075 verification by client tests.
- [ ] T126 [US6] Run `python3 manage.py test banking.tests.test_business_requests banking.tests.test_recipient_resolution` and fix only Business transfer request defects for TEST-047-TEST-049.

## Phase 22: Approval, Rejection, and Cancellation Resolution

**Purpose**: Resolve Business outgoing requests with AUTHORISER approval/rejection/cancellation and MEMBER own cancellation.

### Tests

- [ ] T127 [P] [US6] Create approval lifecycle tests in `banking/tests/test_approvals.py` for MEMBER approval/rejection denial, AUTHORISER approval of other/own request, one approval suffices, withdrawal completion, transfer completion, `SGD 7,000.00` success, `SGD 6,999.99` failure, rejection, cancellation permissions, terminal rejection, and no APPROVED status covering FR-054-FR-086, TEST-050-TEST-057, TEST-059-TEST-060.

### Implementation

- [ ] T128 [US6] Implement approval list/detail query services in `banking/services/approvals.py` covering FR-093 verification by approval tests.
- [ ] T129 [US6] Implement `approve_business_request` in `banking/services/approvals.py` for active AUTHORISER, self-approval, approval-time revalidation, retained minimum, direct COMPLETED/FAILED transitions, and atomic financial movement covering FR-080-FR-086 verification by tests.
- [ ] T130 [US6] Implement `reject_business_request` and `cancel_business_request` in `banking/services/approvals.py` for role-specific permissions, PENDING-only actions, terminal state protection, and no money movement covering FR-052-FR-056, FR-085-FR-086 verification by tests.
- [ ] T131 [US6] Implement approval list/detail/action views and routes in `banking/views.py` and `banking/urls.py` covering FR-054-FR-086 verification by client tests.
- [ ] T132 [US6] Implement approval templates in `templates/banking/approvals.html` and `templates/banking/approval_detail.html` with requester, role, projected balance, retained-minimum status, approve/reject/cancel actions, and statuses covering UX-022 verification by UI review.
- [ ] T133 [US6] Run `python3 manage.py test banking.tests.test_approvals` and fix only approval lifecycle defects for TEST-050-TEST-057, TEST-059-TEST-060.

## Phase 23: Multiple Pending Requests and Independent Revalidation

**Purpose**: Prove Pending requests do not reserve funds and later approvals revalidate independently.

### Tests

- [ ] T134 [P] [US6] Create multiple Pending tests in `banking/tests/test_multiple_pending.py` for coexistence, unchanged displayed balance, no completed records while Pending, first completion success, later `SGD 6,999.99` failure, no money movement on failure, Approval History outcomes, and Transaction History completed-only display covering FR-077-FR-082, TEST-058-TEST-060.

### Implementation

- [ ] T135 [US6] Adjust `banking/services/approvals.py` and dashboard/history queries to ensure Pending requests do not reserve funds and balance display remains actual current balance covering FR-077-FR-079 verification by multiple Pending tests.
- [ ] T136 [US6] Run `python3 manage.py test banking.tests.test_multiple_pending banking.tests.test_approvals` and fix only multiple Pending/revalidation defects for TEST-058-TEST-060.

## Phase 24: Transaction History, Approval History, and Access Audit History

**Purpose**: Implement three distinct history areas with access control.

### Tests

- [ ] T137 [P] [US8] Create history tests in `banking/tests/test_histories.py` for completed-only Transaction History, workflow-only Approval History, access/security-only Access Audit History, no password content, password-change-required denial, deactivated denial, Personal denial from Business histories, and MEMBER/AUTHORISER visibility covering FR-092-FR-097, TEST-061-TEST-067.

### Implementation

- [ ] T138 [US8] Implement Transaction History query service and views in `banking/services/histories.py`, `banking/views.py`, and `banking/urls.py` covering FR-092, FR-095-FR-096 verification by history tests.
- [ ] T139 [US8] Implement Approval History query service and views in `banking/services/histories.py`, `banking/views.py`, and `banking/urls.py` covering FR-093, FR-095-FR-096 verification by history tests.
- [ ] T140 [US8] Implement Access Audit History query service and views in `banking/services/histories.py`, `banking/views.py`, and `banking/urls.py` covering FR-094-FR-096 verification by history tests.
- [ ] T141 [US8] Implement distinct history templates `templates/banking/transaction_history.html`, `templates/banking/approval_history.html`, and `templates/banking/access_audit_history.html` covering UX-023 verification by UI review.
- [ ] T142 [US8] Run `python3 manage.py test banking.tests.test_histories` and fix only history separation/access defects for TEST-061-TEST-067.

## Phase 25: Full Midnight Ledger UI Redesign and Responsive Verification

**Purpose**: Complete the required premium UI after core flows work.

- [ ] T143 [US7] Complete design-system CSS in `static/css/midnight-ledger.css` for variables, typography, spacing, cards, panels, buttons, forms, badges, tables, alerts, empty states, focus indicators, and responsive breakpoints covering UX-001-UX-003, UX-024-UX-029 verification by manual UI checklist.
- [ ] T144 [US7] Polish public pages in `templates/users/account_type_selection.html`, `templates/users/register_personal.html`, `templates/users/register_business.html`, and `templates/users/login.html` covering UX-004-UX-006 verification by manual UI checklist.
- [ ] T145 [US7] Polish Personal pages in `templates/banking/personal_dashboard.html`, `templates/banking/personal_account.html`, and Personal financial templates for balance/phone cards, quick actions, transaction preview, and no Business controls covering UX-007-UX-008 verification by manual UI checklist.
- [ ] T146 [US7] Polish Business Dashboard, Team Access, Add Employee Access, password change, reset, promotion, deactivation, reactivation, request, approval, and history templates under `templates/banking/` and `templates/users/password_change_required.html` covering UX-009-UX-023 verification by manual UI checklist.
- [ ] T147 [US7] Add or update UI permission tests in `banking/tests/test_ui_permissions.py` for no Invitations, no Business selector, role-specific controls, password-change gating, labelled forms, confirmations, and status text covering TEST-068-TEST-069.
- [ ] T148 [US7] Perform manual UI verification for desktop content use, no stranded small forms, visible context/role/status, non-colour-only states, destructive confirmations, labels/errors, keyboard focus, contrast, SGD formatting, and narrow width without horizontal scrolling; record results in `specs/001-banking-mvp/quickstart.md` or implementation notes for UX-001-UX-029.
- [ ] T149 [US7] Run `python3 manage.py test banking.tests.test_ui_permissions users.tests.test_public_onboarding_views` and fix only UI permission/view defects for TEST-068-TEST-069.

## Phase 26: Security, Permissions, and Repository Hygiene

**Purpose**: Harden sensitive flows and repository state.

- [ ] T150 [P] Create security regression tests in `banking/tests/test_access_control.py` for no plaintext temporary-password storage, no password/hash output, mandatory password-change enforcement, deactivated denial, context isolation, Personal owner-only access, AUTHORISER-only admin, cancellation permissions, final AUTHORISER protection, CSRF-protected forms, and safe errors covering SEC-001-SEC-013, TEST-066-TEST-067.
- [ ] T151 Enforce CSRF and POST-only behavior on all modifying views in `users/views.py` and `banking/views.py` covering SEC-001, SEC-010 verification by security tests.
- [ ] T152 Verify and fix safe display of phone numbers, UEN values, employee emails, recipient confirmations, errors, and audit metadata in templates under `templates/` covering SEC-008-SEC-010 verification by security tests.
- [ ] T153 Verify `.gitignore`, secret-key environment loading, local database exclusion, virtual environment exclusion, and local-only disclaimer in `.gitignore`, `bankapp/settings.py`, and `specs/001-banking-mvp/quickstart.md` covering SEC-011 verification by repository hygiene check.
- [x] T154 Document completed pre-implementation checklist housekeeping: `requirements-quality-v2.md` was archived outside `specs/001-banking-mvp/checklists/`, while compatible `requirements.md` and active `requirements-quality-v3.md` remain in the active checklist path, covering CHK-VERSION-007 verification by checklist scan.
- [ ] T155 Run `python3 manage.py test banking.tests.test_access_control users.tests.test_access_context` and fix only security/permission defects for SEC-001-SEC-013, TEST-066-TEST-067.

## Phase 27: Full Test Suite, Traceability, and Superseded-Model Removal Gate

**Purpose**: Verify the full v3 implementation and prove obsolete models are gone.

- [ ] T156 Run the full Django test suite with `python3 manage.py test` and fix all failures covering TEST-001-TEST-069 verification by passing suite.
- [ ] T157 Apply final migrations cleanly to a fresh local SQLite database with `python3 manage.py migrate` after approved reset, then remove any local database from tracked changes covering NFR-004-NFR-005 verification by migration output and `git status`.
- [ ] T158 Update `specs/001-banking-mvp/traceability.md` with final code component paths, test module paths, and requirement coverage for FR-001-FR-097, BR-001-BR-046, SEC-001-SEC-013, UX-001-UX-029, TEST-001-TEST-069 verification by traceability review.
- [ ] T159 Search `users/`, `banking/`, `templates/`, `static/`, and `specs/001-banking-mvp/` for active `Invitation`, `Invite Business User`, `Store Invitation`, invitation route/template/service/test, multi-Business membership, Business Account selector, authorised Personal Account, exactly-one-Authoriser, and persisted APPROVED remnants; remove or flag remaining active implementation hits covering FR-066, BR-036 verification by search output.
- [ ] T160 Verify all constitution v3.0.0 rules have automated or manual verification coverage in `specs/001-banking-mvp/traceability.md` and `specs/001-banking-mvp/tasks.md` covering NFR-005 verification by review.
- [ ] T161 Verify no `.env`, secret, temporary password, password hash fixture, or local SQLite database file is tracked by Git using `git status --short` and targeted `git ls-files` checks covering SEC-011 verification by repository output.

## Phase 28: Local macOS Deployment and Documentation

**Purpose**: Document local execution and final MVP limitations.

- [ ] T162 Update `specs/001-banking-mvp/quickstart.md` with final virtual environment, dependency installation, environment-variable setup, migration/reset preparation, test execution, static-file handling, and local-only disclaimer covering NFR-001, SEC-011 verification by quickstart review.
- [ ] T163 Verify or update Waitress launch guidance in `specs/001-banking-mvp/quickstart.md` and `bankapp/waitress_server.py` covering local deployment verification by `waitress-serve --listen=127.0.0.1:8000 bankapp.wsgi:application`.
- [ ] T164 Document employee credential provisioning, first-login password change, Team Access administration, password reset, deactivation, and reactivation walkthroughs in `specs/001-banking-mvp/quickstart.md` covering FR-037-FR-065 verification by documentation review.
- [ ] T165 Perform final clean Git verification with `git status --short`, confirm no source-generated secrets/local databases are tracked, and record final run instructions for handoff covering SEC-011 and deployment verification by repository output.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** must complete before any v3 implementation.
- **Phase 2** depends on Phase 1 and blocks schema/auth work.
- **Phase 3** depends on Phase 2 and blocks registration and route protection.
- **Phase 4** depends on Phase 3 and blocks services.
- **Phase 5** depends on Phase 4 and blocks financial/access workflows.
- **Phases 6-8** depend on Phase 5 and establish public onboarding plus account creation.
- **Phase 9** depends on Phases 6-8 and establishes authenticated shells.
- **Phases 10-15** depend on Phases 4, 5, 8, and 9 and implement Business employee governance.
- **Phases 16-19** depend on Phases 5, 7, 8, and 9 and implement Personal operations and transfers.
- **Phases 20-23** depend on Phases 5, 10, 13, 18, and 19 and implement Business request/approval behavior.
- **Phase 24** depends on completed financial, approval, and access records.
- **Phase 25** depends on working pages and flows.
- **Phases 26-28** are final hardening, verification, traceability, and deployment documentation.

### User Story Dependencies

- **US1**: Foundation for login, registration, and contexts; complete first.
- **US2**: Depends on US1 and money foundations.
- **US3**: Depends on US1 and model foundations.
- **US4**: Depends on US3 and employee access model.
- **US5**: Depends on US2, US3, and recipient resolution.
- **US6**: Depends on US3, US4, US5 foundations, and approval services.
- **US7**: Starts with public UI after setup, completes after all page flows exist.
- **US8**: Depends on financial, approval, and access audit record creation.

### Parallel Opportunities

- T016 and T017 can run in parallel after Phase 2.
- T031 and T032 can run in parallel after Phase 4.
- T038 can run while Phase 6 UI implementation tasks are prepared.
- Test-writing tasks marked `[P]` can run in parallel with other independent test files once prerequisite models/services exist.
- UI polish tasks T143-T147 can be split after all functional templates exist because they touch related but separable page groups; coordinate edits to shared CSS.

## Parallel Example: Employee Access Tests

```bash
Task: "T080 Extend banking/tests/test_employee_access.py for provisioning behavior"
Task: "T087 Create banking/tests/test_password_reset.py for temporary password reset"
Task: "T093 Create banking/tests/test_access_administration.py for promotion/deactivation/reactivation"
```

## Implementation Strategy

1. Inventory and remove superseded assumptions first.
2. Build identity, models, money validation, and permission helpers before user-visible workflows.
3. Deliver Personal registration and Business registration as the first usable vertical slices.
4. Add Business employee governance before allowing provisioned employee normal use.
5. Add Personal and Business financial operations with tests before history pages.
6. Complete the Midnight Ledger UI once functional pages exist.
7. Finish with full tests, traceability, superseded-model searches, repository hygiene, and Waitress documentation.

## Completion Gate

Implementation is complete only when:

- all mandatory tests pass;
- all invitation-based and multi-Business-membership behavior has been removed or replaced;
- Personal and Business login contexts are separate and enforced;
- a Business Employee Access Login is not treated as a bank account;
- each employee login belongs to one Business Account only;
- Personal Accounts receive transfers by unique phone number;
- Business Accounts receive transfers by unique UEN;
- temporary passwords and mandatory first-login password changes are implemented securely;
- password reset, deactivation, and reactivation workflows are implemented and audited;
- MEMBER and AUTHORISER permissions are enforced server-side;
- multiple AUTHORISERS are supported and the final active AUTHORISER is protected;
- Business financial approval and retained-minimum rules are enforced;
- completed financial transactions are atomic and auditable;
- Transaction History, Approval History, and Access Audit History are separate;
- Midnight Ledger UI requirements have been materially implemented and manually verified;
- security and repository hygiene checks pass;
- Waitress local macOS setup is documented and verified;
- traceability mappings are complete.
