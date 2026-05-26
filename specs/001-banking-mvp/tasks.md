# Tasks: Banking MVP Constitution v2.0.0

**Input**: Design documents from `specs/001-banking-mvp/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/server-rendered-flows.md`, `quickstart.md`, `traceability.md`, `checklists/requirements-quality-v2.md`

**Tests**: Automated tests are mandatory for banking, membership, permission, audit, and financial rules. Write the relevant tests before or alongside implementation and verify they fail for missing behavior before making them pass.

**Organization**: Tasks follow the required v2.0.0 implementation phases. User-story labels map to `spec.md` user stories: `[US1]` registration/context, `[US2]` Personal Account, `[US3]` Business registration, `[US4]` membership/invitations, `[US5]` transfers, `[US6]` Business requests/approvals, `[US7]` Midnight Ledger UI, `[US8]` histories.

## Phase 1: Superseded Implementation Assessment and Safe Refactoring Preparation

**Purpose**: Identify and isolate implementation work based on the superseded one-login / authorised-Personal-Account model before v2.0.0 implementation resumes.

- [X] T001 Create superseded-model assessment notes in `specs/001-banking-mvp/refactoring-impact.md` covering old user/account ownership, authorised Personal Account relationships, exactly-one-authoriser assumptions, same-user Personal/Business transfer restrictions, old tests, old migrations, and local SQLite state; verify notes reference `BR-007`, `BR-014`, `BR-018`, `BR-036`, and `SC-024`.
- [X] T002 Inspect `users/`, `banking/`, `templates/`, `static/`, and `specs/001-banking-mvp/tasks.md` history for code or tasks that assume one login owns both Personal and Business contexts; record affected paths in `specs/001-banking-mvp/refactoring-impact.md` and verify no preservation of obsolete behavior is required. [BR-007 to BR-009, SC-024]
- [X] T003 Inspect `banking/models.py`, `banking/forms.py`, `banking/services/`, `banking/views.py`, and migrations for authorised-Personal-Account fields or Personal-prerequisite Business creation logic; record removal/rewrite targets in `specs/001-banking-mvp/refactoring-impact.md`. [BR-014, FR-020 to FR-026]
- [X] T004 Inspect transfer and approval code/tests for same-user Personal/Business rejection, exactly-one-authoriser, or Personal-account approval assumptions; record rewrite targets in `specs/001-banking-mvp/refactoring-impact.md`. [BR-018, BR-026, BR-036]
- [X] T005 Assess local `db.sqlite3` and existing migration files for superseded schema compatibility; document the approved local reset approach in `specs/001-banking-mvp/refactoring-impact.md` and verify no valuable user data preservation assumption is introduced. [NFR-001, SC-024]
- [X] T006 Remove or quarantine superseded local SQLite database and obsolete generated migration files only after T001-T005 confirm local MVP reset is acceptable; verify the working tree contains no required user data files and that future migrations can be regenerated for v2.0.0. [NFR-001, SC-024]
- [X] T007 Run `rg "authorised Personal|authorized Personal|own Personal|exactly one author|same-user|same user|Personal Account author" users banking templates specs/001-banking-mvp` and update `specs/001-banking-mvp/refactoring-impact.md` with any remaining intentional or obsolete matches; verify v2.0.0 implementation baseline is ready. [BR-014, BR-018, BR-036]

**Checkpoint**: Superseded implementation assumptions are identified, local reset decision is documented, and v2.0.0 implementation can begin.

## Phase 2: Project Configuration, Dependencies, Secrets, and Test Bootstrap

**Purpose**: Establish the approved Django/SQLite/templates/custom CSS/Waitress foundation.

- [X] T008 Validate or create Django project package `bankapp/` with `settings.py`, `urls.py`, `wsgi.py`, and `waitress_server.py`; verify `python manage.py check` can discover the project. [NFR-001]
- [X] T009 Validate or create Django apps `users/` and `banking/` with `apps.py`, `admin.py`, `models.py`, `forms.py`, `views.py`, `urls.py`, `tests/`, and template directories; verify both apps are importable. [NFR-001]
- [X] T010 Configure `requirements.txt` with Django and Waitress only; verify no unapproved frontend framework, REST framework, external email, payment, queue, or cloud dependency is present. [NFR-001]
- [X] T011 Configure environment-based secret key and local debug settings in `bankapp/settings.py` and `.env.example`; verify settings fail safely or use documented local defaults without committing secrets. [SEC-010]
- [X] T012 Configure SQLite3, installed apps, custom user setting placeholder, templates, static files, login URLs, and CSRF defaults in `bankapp/settings.py`; verify configuration matches `plan.md` source layout. [SEC-001, NFR-001]
- [X] T013 Update `.gitignore` for `.env`, local secret files, SQLite database files, virtual environments, Python caches, collected static output, and local generated assets; verify `git status --ignored` excludes these local files. [SEC-010]
- [X] T014 Create shared template skeletons `templates/base_public.html`, `templates/base_personal.html`, `templates/base_business.html`, and `templates/includes/` with minimal blocks only; verify Django template discovery succeeds. [UX-001]
- [X] T015 Create custom CSS entry point `static/css/midnight-ledger.css` with initial design-token placeholders only; verify no external CSS framework is imported. [UX-001, NFR-001]
- [X] T016 Establish baseline tests in `users/tests/test_smoke.py` and `banking/tests/test_smoke.py` for project import and URL configuration; verify `python manage.py test users banking` runs. [TEST-055]

**Checkpoint**: Project configuration, dependency, template/static, secret, and baseline test infrastructure are ready.

## Phase 3: Exclusive Personal/Business User Identity and Authentication

**Purpose**: Build the identity foundation required by all account and membership flows.

- [X] T017 [P] Add authentication model tests in `users/tests/test_authentication.py` for unique email, username, access context choices `PERSONAL`/`BUSINESS`, password hashing, and duplicate email rejection across contexts; verify tests fail before model implementation. [FR-001 to FR-005, TEST-003, TEST-011]
- [X] T018 [P] Add access-context tests in `users/tests/test_access_context.py` for Personal denial from Business views/actions and Business denial from Personal views/actions using placeholder protected views; verify tests fail before guards exist. [FR-006 to FR-010, SEC-002, TEST-004 to TEST-006]
- [X] T019 Implement custom user manager and custom user model in `users/managers.py` and `users/models.py` with unique email login, username, password hashing, and required `access_context`; verify T017 passes. [FR-001 to FR-005, BR-007 to BR-009]
- [X] T020 Configure `AUTH_USER_MODEL`, authentication backend expectations, and admin registration in `bankapp/settings.py` and `users/admin.py`; verify fresh migrations can reference the custom user model before banking models. [FR-002]
- [X] T021 Create initial user migration in `users/migrations/`; verify `python manage.py makemigrations users --check --dry-run` is clean after migration generation. [FR-002, TEST-003]
- [X] T022 Implement sign-in, sign-out, and authentication views/forms in `users/forms.py`, `users/views.py`, `users/urls.py`, and `templates/users/`; verify valid and invalid sign-in tests pass. [FR-004 to FR-005, TEST-011]
- [X] T023 Implement access-context decorators/helpers in `users/views.py` or `users/permissions.py`; verify Personal and Business cross-context denial tests in `users/tests/test_access_context.py` pass. [FR-006 to FR-010, SEC-002, TEST-004 to TEST-006]

**Checkpoint**: Login identities are mutually exclusive and authenticated access context is enforceable.

## Phase 4: Core Banking, Membership, Invitation, Approval, Transfer, and Audit Models

**Purpose**: Implement revised v2.0.0 domain models and migrations.

- [X] T024 [P] Add account model tests in `banking/tests/test_models_accounts.py` for Personal ownership restricted to `PERSONAL`, one Personal Account per Personal user, unique phone, unique UEN, and Business Account fields; verify tests fail first. [FR-011 to FR-024, TEST-007 to TEST-010]
- [X] T025 [P] Add membership and invitation model tests in `banking/tests/test_models_memberships.py` for Business-only memberships, active membership uniqueness, multiple Business Accounts per Business user, roles, invitation statuses, and duplicate pending invitation constraints; verify tests fail first. [FR-027 to FR-048, TEST-037 to TEST-043]
- [X] T026 [P] Add financial record model tests in `banking/tests/test_models_financial_records.py` for UUID transaction IDs, Transfer Operation IDs, exactly-one account references, transaction types, and distinct transaction/approval/access audit structures; verify tests fail first. [FR-069 to FR-077, TEST-022, TEST-050 to TEST-053]
- [X] T027 [P] Add approval request model tests in `banking/tests/test_models_approvals.py` for request types, statuses `PENDING`/`COMPLETED`/`REJECTED`/`CANCELLED`/`FAILED`, absence of `APPROVED`, and terminal status choices; verify tests fail first. [FR-065 to FR-068, TEST-032 to TEST-033]
- [X] T028 Implement `PersonalAccount`, `BusinessAccount`, `BusinessMembership`, `BusinessInvitation`, `BusinessAccessAuditEvent`, `CompletedFinancialTransaction`, `TransferOperation`, and `BusinessApprovalRequest` in `banking/models.py`; verify model tests start failing only on missing constraints/services, not missing classes. [FR-011 to FR-080]
- [X] T029 Add model constants/choices for access roles, invitation statuses, approval statuses, transaction types, and audit event types in `banking/models.py`; verify `APPROVED` is not present in approval choices. [FR-065 to FR-066, TEST-032]
- [X] T030 Add SQLite-practical model constraints in `banking/models.py` for unique phone, unique UEN, active membership uniqueness, non-negative balances, and exact account-reference rules where practical; verify T024-T027 pass where model-only behavior is sufficient. [BR-012, BR-015, BR-018, BR-039]
- [X] T031 Create revised banking migrations in `banking/migrations/`; verify migrations apply cleanly to a fresh local SQLite database after the v2 reset. [NFR-004, SC-024]

**Checkpoint**: v2.0.0 data structures exist and no model includes authorised-Personal-Account fields.

## Phase 5: Shared Financial Validation, Permission Helpers, and Service Foundations

**Purpose**: Create reusable service-layer primitives before money, membership, and approval features.

- [X] T032 [P] Add money validation tests in `banking/tests/test_money_validation.py` for valid amounts, zero, negative, malformed, non-numeric, excessive precision, over-capacity, SGD 7,000.00 accepted boundary, and SGD 6,999.99 failure boundary; verify tests fail first. [BR-001 to BR-004, TEST-014, TEST-035 to TEST-036]
- [X] T033 [P] Add permission helper tests in `banking/tests/test_access_control.py` for Personal owner access, Business active membership, AUTHORISER-only access, final-AUTHORISER protection, removed membership denial, and cross-context denial; verify tests fail first. [SEC-001 to SEC-006, TEST-004, TEST-005, TEST-049, TEST-054]
- [X] T034 Create service package `banking/services/` with `__init__.py`, `money.py`, `accounts.py`, `transfers.py`, `invitations.py`, `memberships.py`, and `approvals.py`; verify imports work. [NFR-004]
- [X] T035 Implement Decimal parsing, validation, quantization, capacity checks, SGD formatting, and money constants in `banking/services/money.py`; verify `banking/tests/test_money_validation.py` passes. [BR-001 to BR-004, UX-019]
- [X] T036 Implement domain exceptions or validation-result objects in `banking/services/__init__.py` or `banking/services/money.py`; verify services can return safe user-facing errors without leaking sensitive data. [NFR-003, SEC-008]
- [X] T037 Implement Personal owner, active Business membership, AUTHORISER, requester cancellation, and last-AUTHORISER helper functions in `banking/services/memberships.py`; verify `banking/tests/test_access_control.py` passes for helper-level cases. [SEC-001 to SEC-006]
- [X] T038 Add transaction-safe service wrapper conventions in service modules and document them in code comments only where needed; verify service functions intended to mutate multiple records use `transaction.atomic`. [NFR-004, BR-038]

**Checkpoint**: Shared validation, permission, and transaction foundations are ready.

## Phase 6: Public Account-Type Selection and Authentication UI Foundation

**Purpose**: Provide public entry points and clear Personal/Business onboarding split.

- [X] T039 [P] Add public UI tests in `users/tests/test_public_onboarding_views.py` for account-type selection content, Personal path explanation, Business path explanation, and absence of cross-context actions; verify tests fail first. [UX-002 to UX-004, TEST-055]
- [X] T040 Implement account-type selection route in `users/urls.py` and `users/views.py`; verify route renders via `templates/users/account_type_selection.html`. [FR-001, UX-002]
- [X] T041 Implement `templates/users/account_type_selection.html` with Personal and Business cards explaining phone receipt, UEN receipt, opening funds, and team approvals; verify T039 content assertions pass. [UX-002 to UX-004]
- [X] T042 Implement public authentication layout styling in `templates/base_public.html` and `static/css/midnight-ledger.css`; verify page uses visible labels and clear primary actions. [UX-001, UX-015]
- [X] T043 Complete sign-in template and sign-out link handling in `templates/users/login.html` and `users/views.py`; verify sign-in/out view tests pass. [FR-004 to FR-005]

**Checkpoint**: Public onboarding clearly separates Personal and Business registration paths.

## Phase 7: Personal Registration and Personal Account Creation

**Goal**: Personal registration creates Personal-only access and one Personal Account. [US1, US2]

**Independent Test**: Registering a Personal user creates one `PERSONAL` identity, one Personal Account with unique phone and SGD 0.00 balance, no Business access, and no opening-deposit transaction.

- [X] T044 [P] [US1] Add Personal registration service and view tests in `banking/tests/test_personal_registration.py` for successful registration, duplicate email, duplicate phone, password hashing, SGD 0.00 balance, no opening deposit transaction, and no Business membership; verify tests fail first. [FR-001 to FR-014, TEST-001, TEST-003, TEST-007 to TEST-008, TEST-011]
- [X] T045 [US1] Implement Personal registration form in `users/forms.py` with username, email, password confirmation, and unique phone number; verify form tests for duplicates and required fields pass. [FR-011 to FR-014]
- [X] T046 [US1] Implement Personal registration service in `banking/services/accounts.py` to atomically create `PERSONAL` user and Personal Account with SGD 0.00; verify T044 service assertions pass. [FR-011 to FR-014, BR-010 to BR-013]
- [X] T047 [US1] Implement Personal registration view, route, and template in `users/views.py`, `users/urls.py`, and `templates/users/register_personal.html`; verify Personal registration view tests pass. [FR-001, UX-003]
- [X] T048 [US2] Implement Personal dashboard and Personal Account initial state in `banking/views.py`, `banking/urls.py`, and `banking/templates/banking/personal_dashboard.html`; verify Personal user sees balance and phone only. [FR-011 to FR-014, UX-005]
- [X] T049 [US1] Add access denial integration tests in `users/tests/test_access_context.py` proving Personal users cannot access Business pages or invitations after registration; verify tests pass. [FR-006 to FR-010, SEC-002, TEST-004]

**Checkpoint**: Personal registration and initial Personal Account are independently usable.

## Phase 8: New Business Account Registration and Initial AUTHORISER Creation

**Goal**: Business registration creates Business-only access, Business Account, initial AUTHORISER, opening deposit, and access audit records. [US1, US3]

**Independent Test**: Registering a Business creator with valid UEN and opening deposit creates all required records atomically and no Personal Account.

- [X] T050 [P] [US3] Add Business registration service and view tests in `banking/tests/test_business_registration.py` for exact SGD 7,000.00, above SGD 7,000.00, below SGD 7,000.00, missing display name, missing/duplicate UEN, UEN normalization, Business-only identity, no Personal Account, initial AUTHORISER, opening transaction UUID, initial audit events, and rollback; verify tests fail first. [FR-020 to FR-026, TEST-002, TEST-009 to TEST-010]
- [X] T051 [US3] Implement Business registration form in `users/forms.py` with creator username, email, password confirmation, business display name, UEN, and opening deposit; verify form validation tests pass. [FR-020 to FR-024, UX-004]
- [X] T052 [US3] Implement Business registration service in `banking/services/accounts.py` to create `BUSINESS` user, Business Account, initial AUTHORISER membership, `BUSINESS_OPENING_DEPOSIT`, and Access Audit Events atomically; verify service tests pass. [FR-020 to FR-026, BR-014 to BR-018]
- [X] T053 [US3] Implement Business registration view, route, and template in `users/views.py`, `users/urls.py`, and `templates/users/register_business.html`; verify Business registration view tests pass. [FR-001, UX-004]
- [X] T054 [US3] Implement initial Business dashboard route/template in `banking/views.py`, `banking/urls.py`, and `banking/templates/banking/business_dashboard.html`; verify creator sees Business Account, UEN, role AUTHORISER, balance, and retained-minimum notice. [UX-007 to UX-008]
- [X] T055 [US1] Add cross-context denial tests proving Business users cannot access Personal pages or operations; verify tests pass. [FR-006 to FR-010, SEC-002, TEST-005]

**Checkpoint**: Business Account creation is independent of Personal Accounts and creates initial governance records.

## Phase 9: Authenticated Midnight Ledger Shell and Context-Specific Navigation

**Goal**: Authenticated Personal and Business users see separate navigation and base layouts. [US7]

**Independent Test**: Personal and Business users get different navigation, while server-side permission tests still deny forbidden routes.

- [X] T056 [P] [US7] Add navigation and layout tests in `banking/tests/test_navigation_layouts.py` for Personal nav, Business nav, multi-membership selector placeholder, signed-in identity display, and forbidden link absence; verify tests fail first. [UX-005 to UX-007, TEST-055]
- [X] T057 [US7] Implement `templates/base_personal.html` with Dashboard, Personal Account, Deposit, Withdraw, Transfer, Transactions, and Sign Out navigation; verify Personal navigation tests pass. [UX-005 to UX-006]
- [X] T058 [US7] Implement `templates/base_business.html` with Business Dashboard, context selector, Deposit, Request Withdrawal, Request Transfer, Approvals, Members, Invitations, Access Audit, Transactions, and Sign Out navigation; verify Business navigation tests pass. [UX-007]
- [X] T059 [US7] Add reusable includes in `templates/includes/` for status badges, alerts, form errors, empty states, result panels, amount display, and confirmation summaries; verify templates render without missing includes. [UX-015 to UX-019]
- [X] T060 [US7] Expand `static/css/midnight-ledger.css` with design tokens, shell layout, cards, forms, buttons, focus states, status badges, and responsive basics; verify no external CSS framework is referenced. [UX-001, UX-017, UX-020 to UX-021]

**Checkpoint**: Authenticated shell supports distinct Personal and Business experiences.

## Phase 10: Business Invitation Creation and Acceptance

**Goal**: AUTHORISERS invite Business users and invited Business-only users accept access. [US4]

**Independent Test**: Invitations grant no access until acceptance; Personal users cannot accept; Business users can join multiple accounts.

- [X] T061 [P] [US4] Add invitation tests in `banking/tests/test_invitations.py` for AUTHORISER inviting MEMBER/AUTHORISER, MEMBER invite rejection, duplicate pending invite rejection, no access before acceptance, matching Business login acceptance, new Business-only registration from invite, Personal acceptance rejection, mismatched email rejection, multi-account membership, intended role assignment, and audit events; verify tests fail first. [FR-038 to FR-041, TEST-037 to TEST-043]
- [X] T062 [US4] Implement invitation creation service in `banking/services/invitations.py` with AUTHORISER-only permission, invitee email, role selection, duplicate pending rule, PENDING status, and `INVITATION_ISSUED` audit event; verify invitation service tests pass. [FR-038 to FR-039]
- [X] T063 [US4] Implement invitation acceptance service in `banking/services/invitations.py` with matching Business email, Personal rejection, membership creation, invitation ACCEPTED status, role assignment, and audit events inside one transaction; verify acceptance tests pass. [FR-039 to FR-041]
- [X] T064 [US4] Implement invitation-specific Business registration support in `users/forms.py`, `users/views.py`, and `templates/users/register_business_invited.html`; verify invited new Business user tests pass. [FR-040, TEST-040]
- [X] T065 [US4] Implement invitation list, create, and accept views/templates in `banking/views.py`, `banking/urls.py`, and `banking/templates/banking/invitations/`; verify no real email delivery dependency exists. [UX-007, SEC-005]

**Checkpoint**: Business invitations and acceptance work without shared credentials or email infrastructure.

## Phase 11: Business Membership Viewing and Context Selection

**Goal**: Business users select among active memberships and lose access immediately when removed. [US4, US7]

**Independent Test**: A Business user with multiple memberships can switch account context and cannot access removed accounts.

- [X] T066 [P] [US4] Add membership context tests in `banking/tests/test_business_context.py` for active membership lookup, multi-account selector, selected context, removed account denial, other membership preservation, and Personal context rejection; verify tests fail first. [FR-027, FR-047 to FR-048, TEST-042 to TEST-043, TEST-049]
- [X] T067 [US4] Implement active membership lookup and selected Business Account context helper in `banking/services/memberships.py`; verify helper tests pass. [FR-027, SEC-003]
- [X] T068 [US7] Implement Business Account selector view/template in `banking/views.py` and `banking/templates/banking/business_account_selector.html`; verify multi-membership selector tests pass. [UX-007]
- [X] T069 [US7] Expand Business dashboard in `banking/views.py` and `banking/templates/banking/business_dashboard.html` to show display name, UEN, balance, retained minimum, role, pending count, recent transactions, and recent request activity; verify dashboard tests pass. [UX-008]
- [X] T070 [US4] Enforce removed membership denial across Business views using active membership helper; verify removed-user access tests pass. [FR-047, SEC-004, NFR-008]

**Checkpoint**: Business membership context controls access for all Business pages.

## Phase 12: Membership Administration and Access Audit Events

**Goal**: AUTHORISERS manage members while preserving last-AUTHORISER protection and access auditability. [US4]

**Independent Test**: Allowed governance actions succeed, forbidden ones fail, and all outcomes are auditable.

- [X] T071 [P] [US4] Add membership administration tests in `banking/tests/test_memberships.py` for promote MEMBER, MEMBER cannot promote/remove, remove MEMBER, remove another AUTHORISER when another remains, final AUTHORISER removal rejection, demotion rejection, immediate access loss, and audit events; verify tests fail first. [FR-042 to FR-048, TEST-044 to TEST-050]
- [X] T072 [US4] Implement promotion service in `banking/services/memberships.py` for AUTHORISER-only MEMBER-to-AUTHORISER promotion plus `MEMBER_PROMOTED_TO_AUTHORISER` audit event; verify promotion tests pass. [FR-042, TEST-044]
- [X] T073 [US4] Implement removal service in `banking/services/memberships.py` for MEMBER removal and AUTHORISER removal with last-AUTHORISER protection plus audit events; verify removal tests pass. [FR-043 to FR-045, TEST-045 to TEST-047]
- [X] T074 [US4] Implement explicit demotion rejection path in `banking/services/memberships.py`; verify demotion rejection tests pass and no supported UI action implies demotion. [FR-046, TEST-048]
- [X] T075 [US4] Implement member roster and management views/templates in `banking/views.py`, `banking/urls.py`, and `banking/templates/banking/members/`; verify AUTHORISER controls and MEMBER read-only states render correctly. [UX-009 to UX-010, SEC-005]
- [X] T076 [US4] Add audit event assertions for promotions, removals, rejected final-authoriser removal, and access denial in `banking/tests/test_memberships.py`; verify Access Audit records do not create financial transactions. [FR-076 to FR-077, TEST-050, TEST-053]

**Checkpoint**: Business membership administration is role-safe and auditable.

## Phase 13: Personal Financial Dashboard, Deposits, and Withdrawals

**Goal**: Personal users can view account details, deposit, withdraw, and see completed transaction records. [US2]

**Independent Test**: Personal money operations are owner-only, Decimal-valid, atomic, and auditable.

- [X] T077 [P] [US2] Add Personal deposit tests in `banking/tests/test_deposits.py` for valid deposit, zero/negative/malformed/excessive precision rejection, transaction UUID creation, no change on rejection, and owner-only access; verify tests fail first. [FR-015, FR-069, TEST-012, TEST-014]
- [X] T078 [P] [US2] Add Personal withdrawal tests in `banking/tests/test_personal_withdrawals.py` for valid withdrawal, full-balance withdrawal to SGD 0.00, overdraft rejection, invalid amount rejection, transaction UUID creation, and no change on rejection; verify tests fail first. [FR-016 to FR-017, TEST-015 to TEST-016]
- [X] T079 [US2] Implement Personal deposit service in `banking/services/accounts.py` with owner permission, amount validation, atomic balance update, and completed `DEPOSIT` transaction; verify deposit tests pass. [FR-015, BR-038]
- [X] T080 [US2] Implement Personal withdrawal service in `banking/services/accounts.py` with owner permission, sufficient funds, SGD 0.00 allowed, atomic debit, and completed `WITHDRAWAL` transaction; verify withdrawal tests pass. [FR-016 to FR-017, BR-012]
- [X] T081 [US2] Implement Personal Account detail, deposit, and withdrawal views/forms/templates in `banking/forms.py`, `banking/views.py`, and `banking/templates/banking/personal/`; verify view tests and CSRF-protected POST flows pass. [UX-005, UX-016]
- [X] T082 [US2] Implement Personal recent transaction preview query in `banking/views.py`; verify completed Personal deposit/withdrawal rows appear and rejected attempts do not. [FR-074, TEST-051]

**Checkpoint**: Personal account core money operations are complete and auditable.

## Phase 14: Business Deposits

**Goal**: Active Business members deposit funds without approval. [US3, US4]

**Independent Test**: MEMBER and AUTHORISER deposits complete immediately; non-members and Personal users are denied.

- [X] T083 [P] [US4] Add Business deposit tests in `banking/tests/test_business_deposits.py` for MEMBER deposit, AUTHORISER deposit, non-member rejection, Personal rejection, invalid amount rejection, completed transaction UUID, actor attribution, and no approval request; verify tests fail first. [FR-030, BR-024, TEST-012 to TEST-013]
- [X] T084 [US4] Implement Business deposit service in `banking/services/accounts.py` with active membership permission, amount validation, atomic balance update, actor attribution, and completed `DEPOSIT` transaction; verify Business deposit service tests pass. [FR-030, BR-024, BR-038]
- [X] T085 [US4] Implement Business deposit form/view/template in `banking/forms.py`, `banking/views.py`, and `banking/templates/banking/business/deposit.html`; verify MEMBER and AUTHORISER view tests pass. [UX-007, UX-016]
- [X] T086 [US4] Add assertions that Business deposits do not create Business Approval Requests in `banking/tests/test_business_deposits.py`; verify tests pass. [BR-024, TEST-013]

**Checkpoint**: Business deposits are immediate, permission-checked, and not part of approval workflow.

## Phase 15: Recipient Resolution and Safe Transfer Confirmation

**Goal**: Shared transfer lookup safely resolves Personal-by-phone and Business-by-UEN destinations before movement or request creation. [US5]

**Independent Test**: Lookup and confirmation work without moving funds.

- [X] T087 [P] [US5] Add recipient resolution tests in `banking/tests/test_recipient_resolution.py` for Personal phone lookup, Business UEN lookup, unknown phone, unknown UEN, identifier mismatch, self-transfer, normalization, and no sensitive data in confirmation; verify tests fail first. [FR-049 to FR-054, SEC-008, TEST-019 to TEST-021]
- [X] T088 [US5] Implement recipient resolver and safe preview functions in `banking/services/transfers.py` with destination type, phone/UEN normalization, unknown/mismatch errors, and self-transfer rejection; verify T087 service tests pass. [FR-049 to FR-054, BR-034 to BR-035]
- [X] T089 [US5] Implement shared transfer/request review form components in `banking/forms.py` for recipient type, matching identifier, and SGD amount; verify form-level validation tests pass. [FR-051, UX-014]
- [X] T090 [US5] Implement server-rendered safe recipient confirmation templates in `banking/templates/banking/transfers/confirm.html`; verify view tests show recipient name/type/masked identifier and no sensitive email or credentials. [SEC-008, UX-014]

**Checkpoint**: Recipient resolution and safe confirmation are ready for Personal transfer and Business request flows.

## Phase 16: Personal Outgoing Transfers

**Goal**: Personal outgoing transfers complete immediately when valid and funded. [US2, US5]

**Independent Test**: Personal-to-Personal and Personal-to-Business transfers create atomic linked records.

- [X] T091 [P] [US5] Add Personal transfer tests in `banking/tests/test_personal_transfers.py` for Personal-to-Personal, Personal-to-Business, full-balance transfer to SGD 0.00, insufficient funds, invalid amount, unknown/mismatch/self-transfer rejection, shared Transfer Operation ID, two UUID transaction IDs, and no partial failure state; verify tests fail first. [FR-018 to FR-019, FR-055 to FR-056, FR-070 to FR-073, TEST-017 to TEST-022]
- [X] T092 [US5] Implement Personal transfer service in `banking/services/transfers.py` with owner permission, recipient resolver, sufficient funds, full-balance allowance, atomic debit/credit, Transfer Operation, and linked transaction records; verify Personal transfer service tests pass. [FR-018 to FR-019, FR-055, BR-037 to BR-038]
- [X] T093 [US5] Implement Personal transfer views/forms/templates in `banking/views.py`, `banking/forms.py`, and `banking/templates/banking/transfers/` for entry, confirmation, and completed result; verify transfer view tests pass. [UX-014, UX-016]
- [X] T094 [US5] Add transaction history assertions for Personal transfer debit/credit IDs and shared operation ID in `banking/tests/test_personal_transfers.py`; verify tests pass. [FR-070 to FR-073, TEST-022]

**Checkpoint**: Personal outgoing transfers are complete and auditable.

## Phase 17: Business Withdrawal Request Submission

**Goal**: Active Business members submit outgoing withdrawal requests that remain PENDING until AUTHORISER action. [US6]

**Independent Test**: Submission creates a workflow record only and moves no funds.

- [X] T095 [P] [US6] Add Business withdrawal request tests in `banking/tests/test_business_requests.py` for MEMBER submission, AUTHORISER submission, non-member rejection, Personal rejection, PENDING status, requester attribution, unchanged balance, and no completed withdrawal transaction; verify tests fail first. [FR-031, FR-058 to FR-060, TEST-023 to TEST-025]
- [X] T096 [US6] Implement Business withdrawal request service in `banking/services/approvals.py` with active membership permission, amount validation, requester attribution, PENDING status, and no balance or transaction changes; verify request service tests pass. [FR-031, FR-058 to FR-060]
- [X] T097 [US6] Implement Business withdrawal request form/view/templates in `banking/forms.py`, `banking/views.py`, and `banking/templates/banking/requests/withdrawal.html`; verify review page explains approval and unchanged balance. [UX-011, UX-016]
- [X] T098 [US6] Implement Pending request result page in `banking/templates/banking/requests/pending.html`; verify request ID and PENDING status are shown. [UX-018]

**Checkpoint**: Business withdrawal requests enter approval workflow without moving money.

## Phase 18: Business Transfer Request Submission

**Goal**: Active Business members submit outgoing transfer requests that remain PENDING until AUTHORISER approval. [US5, US6]

**Independent Test**: Business-to-Personal and Business-to-Business outgoing requests create no completed transfer records while PENDING.

- [X] T099 [P] [US6] Add Business transfer request tests in `banking/tests/test_business_transfer_requests.py` for MEMBER Business-to-Personal request, MEMBER Business-to-Business request, AUTHORISER request, non-member rejection, invalid destination, self-transfer, unchanged balances, no Transfer Operation, and no completed transaction records; verify tests fail first. [FR-032, FR-057, FR-059, TEST-023 to TEST-025]
- [X] T100 [US6] Implement Business transfer request service in `banking/services/approvals.py` using recipient resolver, active membership permission, amount validation, PENDING status, and no financial movement; verify Business transfer request tests pass. [FR-032, FR-057, BR-025]
- [X] T101 [US6] Implement Business transfer request form/view/templates in `banking/forms.py`, `banking/views.py`, and `banking/templates/banking/requests/transfer.html`; verify safe recipient confirmation and approval-required messaging render. [UX-011, UX-014]
- [X] T102 [US6] Add assertions in `banking/tests/test_business_transfer_requests.py` that PENDING transfer requests create no `TransferOperation`, `TRANSFER_DEBIT`, or `TRANSFER_CREDIT` records; verify tests pass. [FR-059, TEST-025]

**Checkpoint**: Business outgoing transfers are represented as PENDING requests only.

## Phase 19: Business Approval, Rejection, and Cancellation Processing

**Goal**: AUTHORISERS resolve PENDING requests; MEMBERS cancel only their own PENDING requests. [US6]

**Independent Test**: Approval completes or fails atomically according to current validation; rejection/cancellation never moves money.

- [X] T103 [P] [US6] Add approval tests in `banking/tests/test_approvals.py` for MEMBER cannot approve/reject, AUTHORISER approves own/others, one approval sufficient, valid withdrawal completion, valid transfer completion, exactly SGD 7,000.00 success, exactly SGD 6,999.99 FAILED, rejection, cancellation permissions, terminal immutability, and no APPROVED status; verify tests fail first. [FR-035 to FR-068, TEST-026 to TEST-036]
- [X] T104 [US6] Implement approval list and detail queries in `banking/services/approvals.py` and `banking/views.py`; verify active members see permitted requests with requester, role, amount, destination, status, and dates. [FR-075, UX-011]
- [X] T105 [US6] Implement approval action for Business withdrawals in `banking/services/approvals.py` with AUTHORISER check, PENDING-only check, balance revalidation, retained-minimum enforcement, atomic debit, completed withdrawal transaction, and COMPLETED or FAILED status; verify withdrawal approval tests pass. [FR-062 to FR-064, BR-023, TEST-035 to TEST-036]
- [X] T106 [US6] Implement approval action for Business transfers in `banking/services/approvals.py` with AUTHORISER check, retained-minimum enforcement, atomic sender debit, recipient credit, Transfer Operation, linked transactions, and COMPLETED or FAILED status; verify transfer approval tests pass. [FR-062 to FR-064, FR-070 to FR-073]
- [X] T107 [US6] Implement rejection service in `banking/services/approvals.py` for AUTHORISER-only PENDING-to-REJECTED with no balance movement; verify rejection tests pass. [FR-035, FR-067 to FR-068, TEST-029]
- [X] T108 [US6] Implement cancellation service in `banking/services/approvals.py` for MEMBER own-request cancellation and AUTHORISER any-request cancellation with PENDING-to-CANCELLED and no balance movement; verify cancellation tests pass. [FR-033, FR-035, TEST-030 to TEST-031]
- [X] T109 [US6] Implement approval list/detail/action views/templates in `banking/views.py`, `banking/forms.py`, and `banking/templates/banking/approvals/`; verify projected balance, retained-minimum compliance, permitted actions, and status history render. [UX-011, UX-018]
- [X] T110 [US6] Add regression assertion in `banking/tests/test_approvals.py` that no persisted `APPROVED` status or transition path exists; verify tests pass. [FR-066, BR-031, TEST-032]

**Checkpoint**: Business outgoing approval lifecycle matches constitution v2.0.0.

## Phase 20: Multiple Pending Requests and Revalidation

**Goal**: Multiple PENDING Business requests coexist without reservation and are independently revalidated. [US6]

**Independent Test**: One completed request can cause a later request to fail at the SGD 6,999.99 boundary.

- [X] T111 [P] [US6] Add multiple Pending tests in `banking/tests/test_multiple_pending.py` for two or more PENDING requests, unchanged balance, no completed records while Pending, first completion, later SGD 6,999.99 FAILED outcome, no movement for failed request, Approval History outcomes, and Transaction History only showing completed movement; verify tests fail first. [FR-061 to FR-064, TEST-034 to TEST-036]
- [X] T112 [US6] Adjust request submission and approval services in `banking/services/approvals.py` to explicitly allow multiple PENDING requests and avoid any fund reservation; verify T111 pending/no-reservation tests pass. [FR-059 to FR-061, BR-028 to BR-030]
- [X] T113 [US6] Ensure approval services re-read current balances and independently revalidate each request at approval time; verify later SGD 6,999.99 failure tests pass. [FR-062 to FR-064, TEST-036]
- [X] T114 [US6] Add history assertions for mixed COMPLETED and FAILED outcomes in `banking/tests/test_multiple_pending.py`; verify Approval History and Transaction History separation pass. [FR-074 to FR-077, TEST-051 to TEST-053]

**Checkpoint**: Pending Business requests behave correctly under current-state revalidation.

## Phase 21: Transaction History, Approval History, and Access Audit History

**Goal**: Users can view three distinct audit/history areas with correct access control. [US8]

**Independent Test**: Each history contains only its approved record types and denies unauthorised access.

- [X] T115 [P] [US8] Add Transaction History tests in `banking/tests/test_histories_transactions.py` for Personal and Business completed movements only, UUIDs, Transfer Operation IDs, debit/credit labels, filters, and exclusion of workflow/access records; verify tests fail first. [FR-074, TEST-051]
- [X] T116 [P] [US8] Add Approval History tests in `banking/tests/test_histories_approvals.py` for Business outgoing workflow records, statuses, requester, actioning AUTHORISER, dates, destinations, outcome reasons, and exclusion from Transaction History; verify tests fail first. [FR-075, TEST-052]
- [X] T117 [P] [US8] Add Access Audit History tests in `banking/tests/test_histories_access_audit.py` for creation, initial AUTHORISER, invitations, acceptances, role assignments, promotions, removals, rejected final-authoriser removal, and separation from financial transactions; verify tests fail first. [FR-076 to FR-077, TEST-050, TEST-053]
- [X] T118 [P] [US8] Add history access-control tests in `banking/tests/test_histories_access_control.py` for Personal ownership, Business active membership, removed-user denial, Personal-to-Business denial, and Business-to-Personal denial; verify tests fail first. [FR-078, SEC-003 to SEC-004, TEST-054]
- [X] T119 [US8] Implement Transaction History query/service and views/templates in `banking/views.py` and `banking/templates/banking/histories/transactions.html`; verify Transaction History tests pass. [FR-074, UX-012 to UX-013]
- [X] T120 [US8] Implement Approval History query/service and views/templates in `banking/views.py` and `banking/templates/banking/histories/approvals.html`; verify Approval History tests pass. [FR-075, UX-012 to UX-013]
- [X] T121 [US8] Implement Access Audit History query/service and views/templates in `banking/views.py` and `banking/templates/banking/histories/access_audit.html`; verify Access Audit tests pass. [FR-076 to FR-077, UX-012 to UX-013]
- [X] T122 [US8] Enforce history access checks using Personal owner and active Business membership helpers; verify history access-control tests pass. [FR-078, SEC-003 to SEC-004]

**Checkpoint**: Transaction, Approval, and Access Audit histories are distinct and permission-controlled.

## Phase 22: Midnight Ledger UI Completion, Accessibility, and Responsive Behaviour

**Goal**: Complete the premium server-rendered Midnight Ledger UI across all flows. [US7]

**Independent Test**: Core pages remain readable, role-aware, labelled, keyboard-friendly, and clear at desktop and narrow widths.

- [X] T123 [P] [US7] Add UI acceptance tests in `banking/tests/test_ui_acceptance.py` for registration choice, Personal navigation, Business navigation, role-aware controls, labelled forms, status text, confirmation pages, SGD formatting, and basic responsive class/structure expectations; verify tests fail first where UI is incomplete. [UX-001 to UX-021, TEST-055]
- [X] T124 [US7] Complete Midnight Ledger CSS in `static/css/midnight-ledger.css` for public pages, authenticated shells, cards, forms, tables/lists, status badges, focus states, alerts, empty states, and responsive narrow-width behavior; verify UI acceptance tests pass where automated. [UX-001, UX-017, UX-020 to UX-021]
- [X] T125 [US7] Apply reusable includes from `templates/includes/` across Personal, Business, invitation, membership, transfer, approval, and history templates; verify no template duplicates obsolete status or error treatment. [UX-015 to UX-018]
- [X] T126 [US7] Ensure all financial and membership-changing views include server-rendered confirmation or review pages before final action; verify UI acceptance and flow tests pass. [UX-016]
- [X] T127 [US7] Create manual UI verification checklist in `specs/001-banking-mvp/ui-acceptance.md` covering Midnight Ledger visual direction, keyboard navigation, focus states, non-colour-only statuses, narrow-width readability, and role-aware controls; verify it maps to `UX-001` through `UX-021`. [UX-001 to UX-021, TEST-055]

**Checkpoint**: UI meets clarified premium and accessibility expectations without frontend frameworks.

## Phase 23: Security, Permission Enforcement, and Repository Hygiene

**Purpose**: Harden server-side permissions, sensitive output, CSRF, and repository safety.

- [X] T128 [P] Add security regression tests in `banking/tests/test_security_permissions.py` for Personal/Business cross-context denial, non-member Business denial, AUTHORISER-only actions, requester cancellation rules, final-AUTHORISER protection, CSRF expectations, and safe errors; verify tests fail for any missing protections. [SEC-001 to SEC-009, TEST-054]
- [X] T129 [P] Add repository hygiene checks in `specs/001-banking-mvp/security-hygiene.md` documenting `.env`, DB, secret, cache, virtualenv, and generated asset exclusions; verify no local secret/database files are tracked by Git. [SEC-010]
- [X] T130 Enforce CSRF and login protection on all state-changing views in `users/views.py` and `banking/views.py`; verify security regression tests pass. [SEC-001, SEC-009]
- [X] T131 Audit safe display of phone numbers, UENs, invitee emails, recipient confirmations, errors, and histories in templates under `templates/` and `banking/templates/`; verify no passwords, secret keys, or sensitive credential details can appear. [SEC-007 to SEC-008]
- [X] T132 Re-run full access-control tests in `users/tests/test_access_context.py`, `banking/tests/test_access_control.py`, and `banking/tests/test_security_permissions.py`; verify all permission-sensitive tests pass. [SEC-001 to SEC-009, TEST-054]

**Checkpoint**: Security and permission invariants are enforced server-side.

## Phase 24: Traceability, Full Automated Test Suite, and Quality Gates

**Purpose**: Prove v2.0.0 requirements are implemented, tested, and free of obsolete model behavior.

- [X] T133 Update `specs/001-banking-mvp/traceability.md` with implemented component paths and test paths for `FR-001` through `FR-080`, `BR-001` through `BR-041`, `SEC-001` through `SEC-010`, `UX-001` through `UX-021`, `NFR-001` through `NFR-008`, and `TEST-001` through `TEST-055`; verify no mapping remains `Pending`. [NFR-005]
- [X] T134 Run `python manage.py test` for the full Django test suite; verify all mandatory banking, membership, audit, permission, and UI-flow tests pass. [TEST-001 to TEST-055]
- [X] T135 Run `python manage.py migrate` against a fresh local SQLite database after reset; verify migrations apply cleanly from zero state. [NFR-004]
- [X] T136 Run `rg "authorised Personal|authorized Personal|own Personal|linked Personal|exactly one author|same-user|same user|Personal Account author|APPROVED" users banking templates specs/001-banking-mvp` and update `specs/001-banking-mvp/refactoring-impact.md` with any remaining matches as removed or intentional references to absence; verify no obsolete implementation behavior remains. [SC-024, BR-014, BR-018, BR-031, BR-036]
- [X] T137 Verify completed financial transactions are immutable through ordinary user-facing flows by reviewing views/services and tests; record result in `specs/001-banking-mvp/traceability.md`. [BR-039, TEST-051]
- [X] T138 Document approved MVP limitations in `README.md` or `quickstart.md`, including local-only use, no real banking, no email delivery, no OTP, no external UEN registry, no shared Business credentials, and no production deployment. [NFR-001]

**Checkpoint**: Quality gates pass and traceability is complete.

## Phase 25: Local macOS Waitress Deployment and Documentation

**Purpose**: Finish local run documentation and repository readiness.

- [X] T139 Update `quickstart.md` with final virtual environment, dependency installation, environment variable, migration/reset, test, static file, Waitress, browser access, invitation-without-email, multi-Business-account context, and local-only disclaimer instructions; verify commands match implemented project names. [NFR-001, SEC-010]
- [X] T140 Implement or verify Waitress entry point in `bankapp/waitress_server.py` and document `waitress-serve --listen=127.0.0.1:8000 bankapp.wsgi:application`; verify local launch works. [NFR-001]
- [X] T141 Verify `python manage.py collectstatic` behavior for local use and document any required static-file steps in `quickstart.md`; verify custom CSS is available. [UX-001]
- [X] T142 Run final repository hygiene check with `git status --short`, `git ls-files`, and ignored-file inspection; verify no `.env`, local SQLite DB, secret, virtualenv, cache, or generated local asset is staged or tracked. [SEC-010]

## Dependencies and Execution Order

### Phase Dependencies

- Phase 1 must finish before replacement implementation begins.
- Phase 2 depends on Phase 1 and blocks all implementation.
- Phase 3 must complete before migrations that depend on the custom user model.
- Phase 4 depends on Phase 3.
- Phase 5 depends on Phase 4 and blocks money, membership, transfer, and approval services.
- Phases 6-9 build onboarding and shell after identity/models are ready.
- Phase 10 depends on Business registration and membership models.
- Phase 11 depends on invitations/memberships and Business dashboard shell.
- Phase 12 depends on membership helpers and context selection.
- Phases 13-14 depend on money validation and account models.
- Phase 15 depends on account models and money validation.
- Phase 16 depends on Phase 15.
- Phases 17-18 depend on Business membership and recipient resolution.
- Phase 19 depends on Business request submission.
- Phase 20 depends on approval processing.
- Phase 21 depends on financial, approval, and access audit records.
- Phase 22 depends on functional pages.
- Phases 23-25 are final verification and deployment gates.

### User Story Dependencies

- `US1` depends on project setup and custom user identity.
- `US2` depends on Personal registration/account models and money validation.
- `US3` depends on Business Account, membership, transaction, and audit models.
- `US4` depends on Business registration, active membership helpers, and audit events.
- `US5` depends on Personal/Business account models, money validation, and recipient resolution.
- `US6` depends on Business memberships, Business request models, and transfer resolution.
- `US7` depends on public/authenticated views and can be polished incrementally after each feature flow.
- `US8` depends on completed financial records, approval requests, and access audit events.

### Parallel Opportunities

- T017 and T018 can run in parallel because they write separate user test modules.
- T024, T025, T026, and T027 can run in parallel because they write separate banking model test modules.
- T032 and T033 can run in parallel because money validation and permission helper tests use separate modules.
- T061, T066, T071, T077, T078, T083, T087, T091, T095, T099, T103, T111, T115, T116, T117, T118, T123, T128, and T129 are isolated test/doc tasks after prerequisites.
- Do not parallelize tasks that edit `banking/models.py`, migrations, shared service modules, base templates, route files, or shared CSS.

## Parallel Examples

```bash
# After Phase 3 prerequisites, model tests can be drafted independently:
Task T024: banking/tests/test_models_accounts.py
Task T025: banking/tests/test_models_memberships.py
Task T026: banking/tests/test_models_financial_records.py
Task T027: banking/tests/test_models_approvals.py

# After Phase 5 prerequisites, distinct feature tests can be drafted independently:
Task T061: banking/tests/test_invitations.py
Task T071: banking/tests/test_memberships.py
Task T087: banking/tests/test_recipient_resolution.py
Task T095: banking/tests/test_business_requests.py
```

## Implementation Strategy

### MVP First

1. Complete Phases 1-5 to establish the v2 identity, model, validation, and permission foundation.
2. Complete Phases 6-8 to support both registration contexts.
3. Complete Phases 10-12 to prove Business membership and governance.
4. Complete Phases 13-20 to prove financial correctness and approvals.
5. Complete Phases 21-25 for histories, UI polish, security, traceability, and local deployment.

### Incremental Validation

- Run targeted test modules after each phase.
- Do not proceed to dependent phases while tests for financial, membership, or permission-sensitive tasks are failing.
- Regenerate or update traceability only after component and test paths exist.

## Implementation Completion Gate

The application is not complete until:

- all required tests pass;
- the superseded ownership/authorisation model has been removed or refactored;
- Personal and Business login contexts are separate and enforced;
- Personal Accounts receive funds by unique phone number;
- Business Accounts receive funds by unique UEN;
- Business memberships and invitations function as specified;
- MEMBER and AUTHORISER permissions are enforced server-side;
- multiple AUTHORISERS are supported;
- the last AUTHORISER cannot be removed;
- Business outgoing approvals follow the approved lifecycle;
- financial operations are atomic;
- three audit/history views remain distinct;
- Midnight Ledger UI acceptance requirements are met;
- repository secrets hygiene is verified;
- Waitress local macOS execution is documented and verified;
- requirement-to-implementation and requirement-to-test traceability is complete.
