# Tasks: Banking MVP

**Input**: Design documents from `/specs/001-banking-mvp/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/server-rendered-flows.md](./contracts/server-rendered-flows.md), [quickstart.md](./quickstart.md), [traceability.md](./traceability.md), [checklists/requirements-quality.md](./checklists/requirements-quality.md)

**Tests**: Mandatory. Financial, permission-sensitive, and traceability-critical tasks include test tasks before or alongside implementation tasks.

**Organization**: Tasks follow the approved 20-phase implementation sequence. User-story labels map to the specification:

- **US1**: Register and Access Own Accounts
- **US2**: Open and Use a Personal Account
- **US3**: Open and Use a Business Account
- **US4**: Transfer Money Safely
- **US5**: Review Business Approvals
- **US6**: Navigate the Midnight Ledger Interface
- **US7**: View Transaction and Approval History

## Phase 1: Project Setup and Configuration

**Purpose**: Establish the Django project shell, approved dependencies, local configuration, templates/static structure, and baseline test execution.

- [X] T001 Create `requirements.txt` with only Django and Waitress dependencies; verify with `pip install -r requirements.txt` and confirm no unapproved packages are listed. [Constitution §I]
- [X] T002 Create Django project package `bankapp/` and `manage.py` using the planned structure in `specs/001-banking-mvp/plan.md`; verify `python manage.py help` runs. [NFR-001]
- [X] T003 Create Django apps `users/` and `banking/`; verify both apps are importable and ready to add to `INSTALLED_APPS`. [FR-001, FR-006]
- [X] T004 Configure `bankapp/settings.py` for SQLite3, installed local apps, Django templates, static files, CSRF defaults, and local macOS development; verify `python manage.py check` passes. [NFR-001, SEC-007]
- [X] T005 Configure environment-based `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and allowed hosts handling in `bankapp/settings.py`; verify missing or local env values produce safe development behaviour without committed secrets. [SEC-007]
- [X] T006 Update `.gitignore` for `.env`, local secret files, `db.sqlite3`, SQLite sidecar files, virtual environments, Python caches, collected static output, and local generated artifacts; verify `git status --ignored` excludes those paths. [SEC-007]
- [X] T007 Create base template directories `templates/`, `templates/users/`, `templates/banking/`, `templates/components/`, and `static/css/`; verify Django template discovery is configured. [UX-003, UX-011]
- [X] T008 Create placeholder `bankapp/urls.py`, `users/urls.py`, and `banking/urls.py` routing structure without feature logic; verify `python manage.py check` passes. [NFR-001]
- [X] T009 Create `bankapp/waitress_server.py` entry point placeholder aligned to `quickstart.md`; verify Waitress import path is documented but no deployment starts during task execution. [NFR-014]
- [X] T010 Create baseline test module `users/tests.py` and test package `banking/tests/` with `__init__.py`; verify `python manage.py test` discovers tests successfully. [TEST-001 to TEST-053]
- [X] T011 Verify initial Django launch locally with `python manage.py runserver`; record manual result in `specs/001-banking-mvp/traceability.md`. [NFR-014]

## Phase 2: User Identity and Authentication

**Purpose**: Implement email-login identity separately from banking accounts.

- [X] T012 [US1] Add custom user manager tests in `users/tests.py` for unique email login and username display; verify tests fail before model implementation. [FR-001, FR-002, TEST-008]
- [X] T013 [US1] Add authentication tests in `users/tests.py` for password hashing, successful sign-in, failed sign-in, sign-out, and unauthenticated protected-page denial; verify tests fail before views/forms. [FR-003, FR-004, SEC-001, SEC-003, TEST-009, TEST-041]
- [X] T014 [US1] Implement custom `CustomUser` and manager in `users/models.py` and `users/managers.py` with unique email login and username display; verify `python manage.py makemigrations --check --dry-run` identifies expected migration. [FR-001, FR-002]
- [X] T015 [US1] Configure `AUTH_USER_MODEL` and authentication redirects in `bankapp/settings.py`; verify `python manage.py check` passes before initial migrations are committed. [SEC-001]
- [X] T016 [US1] Register the custom user model in `users/admin.py`; verify admin system checks pass without exposing plaintext passwords. [SEC-003]
- [X] T017 [US1] Create registration and sign-in forms in `users/forms.py` with duplicate email validation and password confirmation; verify form tests cover duplicate email and password handling. [FR-001, FR-002, TEST-008, TEST-009]
- [X] T018 [US1] Implement registration, sign-in, and sign-out views in `users/views.py` and routes in `users/urls.py`; verify authentication tests pass for correct and incorrect credentials. [FR-003, FR-004, TEST-041]
- [X] T019 [US1] Create `templates/public_base.html`, `templates/users/register.html`, and `templates/users/login.html` with visible labels, inline errors, and account-identifier setup explanation; verify rendered responses include required fields and no password echo. [UX-011, SEC-003, TEST-046]
- [X] T020 [US1] Add authenticated navigation state helpers in `templates/base.html` and `bankapp/urls.py`; verify signed-in and signed-out navigation states render appropriately. [FR-003, UX-003]
- [X] T021 [US1] Run `python manage.py test users` against `users/tests.py`; verify all US1 authentication tests pass. [TEST-008, TEST-009, TEST-041, TEST-046]

## Phase 3: Core Banking Models and Constraints

**Purpose**: Create the foundational banking data structures before financial services.

- [X] T022 [P] Add account model tests in `banking/tests/test_models_accounts.py` for `BankAccount` account type choices, one Personal Account per user, one Business Account per user, Personal phone uniqueness, Business UEN uniqueness, and invalid type-specific fields; verify tests fail before model implementation. [FR-006 to FR-010, FR-016 to FR-020, TEST-003, TEST-007]
- [X] T023 [P] Add completed-transaction model tests in `banking/tests/test_models_transactions.py` for `CompletedTransaction`, UUID transaction IDs, transaction type choices, immutable ordinary-flow expectation, and exact SGD amount field precision; verify tests fail before model implementation. [FR-060 to FR-063, BR-034, TEST-036, TEST-042]
- [X] T024 [P] Add transfer-operation model tests in `banking/tests/test_models_transfers.py` for `TransferOperation` UUID operation IDs and linked debit/credit relationship expectations; verify tests fail before model implementation. [FR-053 to FR-055, TEST-037]
- [X] T025 [P] Add approval-request model tests in `banking/tests/test_models_approvals.py` for `ApprovalRequest` request types, statuses PENDING/COMPLETED/REJECTED/CANCELLED/FAILED, and absence of APPROVED status; verify tests fail before model implementation. [FR-038, FR-039, TEST-035, TEST-040]
- [X] T026 Implement `BankAccount`, `CompletedTransaction`, `TransferOperation`, and `ApprovalRequest` in `banking/models.py` using Decimal fields, UUID fields, relationships, and status choices from `data-model.md`; verify model tests progress to validation failures rather than missing models. [FR-006 to FR-063]
- [X] T027 Add practical SQLite-compatible constraints in `banking/models.py` for owner/account type uniqueness, Personal phone uniqueness, Business UEN uniqueness, non-negative balance, and type-specific field consistency; verify constraint tests pass. [BR-011, BR-013, BR-038]
- [X] T028 Register banking models in `banking/admin.py` with read-oriented completed transaction configuration; verify admin checks pass and ordinary admin registration does not imply user-facing edit/delete flows. [FR-063]
- [X] T029 Create and apply initial migrations for `users` and `banking`; verify `python manage.py migrate` succeeds on SQLite. [NFR-001]
- [X] T030 Run `python manage.py test banking.tests.test_models_accounts banking.tests.test_models_transactions banking.tests.test_models_transfers banking.tests.test_models_approvals`; verify all model and constraint tests pass before service work begins. [TEST-003, TEST-007, TEST-035, TEST-036, TEST-037, TEST-040, TEST-042]

## Phase 4: Financial Validation and Service Layer Foundations

**Purpose**: Establish authoritative Decimal validation, formatting, ownership checks, and service-layer structure.

- [X] T031 [P] Add Decimal validation tests in `banking/tests/test_money_validation.py` for zero, negative, malformed, non-numeric, excessive precision, valid amount, over-capacity amount, SGD 7,000.00 retained-minimum boundary, and SGD 6,999.99 retained-minimum failure boundary; verify tests fail before helper implementation. [BR-001 to BR-005, BR-019, TEST-011, TEST-012, TEST-019, TEST-026, TEST-030]
- [X] T032 [P] Add permission helper tests in `banking/tests/test_access_control.py` for account ownership checks, authorised Personal Account checks, and unauthorised access outcomes; verify tests fail before helper implementation. [SEC-001, SEC-002, TEST-039, TEST-041]
- [X] T033 Create `banking/services.py` with domain exceptions or safe validation result classes, `validate_sgd_amount`, `format_sgd`, phone normalisation, UEN normalisation, ownership checks, and authorised-approver checks; verify Decimal and permission tests pass. [BR-001 to BR-005, SEC-002]
- [X] T034 Add transaction-safe service helper patterns in `banking/services.py` using `transaction.atomic()` and current-balance re-read conventions; verify helper-level tests document atomic behaviour expectations. [NFR-004, TEST-038]
- [X] T035 Add reusable form field validation helpers in `banking/forms.py` for SGD amount, phone number, and UEN inputs; verify form-level validation tests cover user-facing errors. [FR-064, NFR-003]
- [X] T036 Update `specs/001-banking-mvp/traceability.md` with planned helper and service paths for BR-001 to BR-007 and SEC-001 to SEC-007; verify traceability references remain current. [NFR-005]

## Phase 5: Personal Account Creation and UI

**Purpose**: Deliver Personal Account setup with unique phone identifier and SGD 0.00 starting balance.

- [X] T037 [P] [US2] Add service tests in `banking/tests/test_personal_accounts.py` for Personal Account creation, duplicate Personal Account rejection, duplicate phone rejection, and starting balance SGD 0.00; verify tests fail first. [FR-008 to FR-010, TEST-001, TEST-002, TEST-003]
- [X] T038 [US2] Implement `create_personal_account` in `banking/services.py` with authenticated owner, unique normalised phone number, one-account-per-user enforcement, and SGD 0.00 balance; verify service tests pass. [BR-008 to BR-011]
- [X] T039 [US2] Create `PersonalAccountForm` in `banking/forms.py`; verify duplicate phone and required phone validation render clear errors. [FR-009, FR-010, UX-012]
- [X] T040 [US2] Implement Personal Account setup and detail views in `banking/views.py` and routes in `banking/urls.py`; verify authenticated access and duplicate account prevention tests pass. [FR-005, FR-008]
- [X] T041 [US2] Create `templates/banking/personal_setup.html` and `templates/banking/personal_detail.html` with phone receiving identifier, SGD 0.00 start explanation, no-minimum notice, action links, and recent completed transactions; verify rendered content meets UX-012. [UX-012, TEST-045]
- [X] T042 [US2] Add Personal Account empty-state component in `templates/components/empty_state.html` or account card fragment; verify dashboard/detail tests can render a no-account state. [UX-026]
- [X] T043 [US2] Run Personal Account tests in `banking/tests/test_personal_accounts.py` with `python manage.py test banking.tests.test_personal_accounts`; verify `TEST-001`, `TEST-002`, and `TEST-003` pass. [TEST-001, TEST-002, TEST-003]

## Phase 6: Business Account Creation and UI

**Purpose**: Deliver Business Account setup with display name, UEN, opening deposit, sole authoriser, and opening transaction.

- [X] T044 [P] [US3] Add service tests in `banking/tests/test_business_accounts.py` for Business Account creation at SGD 7,000.00, above SGD 7,000.00, below SGD 7,000.00 rejection, no Personal Account rejection, missing display name rejection, duplicate UEN rejection, and sole authorised Personal Account linkage; verify tests fail first. [FR-016 to FR-026, TEST-004 to TEST-007]
- [X] T045 [P] [US3] Add atomicity tests in `banking/tests/test_business_account_atomicity.py` for Business Account creation and `BUSINESS_OPENING_DEPOSIT` transaction creation or full rollback on failure; verify tests fail first. [BR-014, BR-034, TEST-036, TEST-038]
- [X] T046 [US3] Implement `create_business_account` in `banking/services.py` with Personal prerequisite, display name validation, normalised unique UEN, opening deposit minimum, authorised Personal Account link, and atomic opening transaction; verify service tests pass. [FR-016 to FR-026, BR-012 to BR-017]
- [X] T047 [US3] Create `BusinessAccountForm` in `banking/forms.py` with business display name, UEN, and opening deposit validation; verify form tests cover missing/duplicate UEN and low deposit messages. [FR-017 to FR-022, UX-013]
- [X] T048 [US3] Implement Business Account setup and detail views in `banking/views.py` and routes in `banking/urls.py`; verify users without Personal Accounts cannot create Business Accounts. [FR-016, FR-023]
- [X] T049 [US3] Create `templates/banking/business_setup.html` and `templates/banking/business_detail.html` with business display name, UEN, SGD 7,000.00 opening/retained-minimum notices, Pending summary, actions, and recent transactions; verify UX-013 and UX-008 coverage. [UX-008, UX-013]
- [X] T050 [US3] Add validation-failure and no-Business empty states in `templates/components/empty_state.html` or Business templates; verify rendered messages are clear and non-technical. [UX-026, UX-027]
- [X] T051 [US3] Run Business Account tests in `banking/tests/test_business_accounts.py` and `banking/tests/test_business_account_atomicity.py`; verify `TEST-004` through `TEST-007`, opening transaction, and rollback cases pass. [TEST-004 to TEST-007, TEST-036, TEST-038]

## Phase 7: Dashboard and Authenticated Application Shell

**Purpose**: Establish the Midnight Ledger shell and dashboard foundation.

- [X] T052 [P] [US6] Add rendered-template tests in `banking/tests/test_dashboard_ui.py` for authenticated dashboard shell, navigation destinations, username top bar, sign-out action, account cards, setup empty states, recent transaction preview, and Pending indicator; verify tests fail first. [UX-003 to UX-010, TEST-045]
- [X] T053 [US6] Implement `templates/base.html` with authenticated desktop sidebar, compact navigation markup, top bar username, sign-out action, CSRF-ready form areas, and content blocks; verify dashboard template tests progress. [UX-003, UX-004]
- [X] T054 [US6] Implement `templates/public_base.html` refinements for public authentication layout; verify registration and sign-in pages use the public layout. [UX-011, TEST-046]
- [X] T055 [US6] Create `static/css/app.css` with Midnight Ledger design tokens for midnight shell, soft surfaces, teal/mint accents, amber Pending, typography, spacing, focus states, borders, and shadows; verify CSS file is included by base templates. [UX-001, UX-002]
- [X] T056 [P] [US6] Create reusable fragments `templates/components/account_card.html`, `status_badge.html`, `alert.html`, `field_errors.html`, `confirmation_summary.html`, `empty_state.html`, and `transaction_row.html`; verify template tests can include each fragment. [UX-006, UX-021, UX-024, UX-026]
- [X] T057 [US6] Implement dashboard view in `banking/views.py` and route `/dashboard/` with Personal/Business account summaries, quick actions, recent completed transactions, and Pending approval count; verify dashboard tests pass. [UX-005, UX-010]
- [X] T058 [US6] Add responsive CSS rules in `static/css/app.css` for narrow-width navigation and readable cards/forms without normal-use horizontal scrolling; verify manual checklist entry in `specs/001-banking-mvp/traceability.md`. [NFR-014 to NFR-016, TEST-053]
- [X] T059 [US6] Add accessibility checks for visible labels, focus states, non-colour-only statuses, and strong contrast to rendered template tests or manual checklist notes; verify `TEST-052` traceability is updated. [NFR-006 to NFR-013, TEST-052]

## Phase 8: Deposit Feature

**Purpose**: Implement positive deposits into Personal and Business Accounts with completed transaction records.

- [X] T060 [P] [US2] Add deposit service tests in `banking/tests/test_deposits.py` for Personal deposit, Business deposit without approval, zero rejection, negative rejection, invalid precision rejection, completed `DEPOSIT` record creation, and no changes on rejection; verify tests fail first. [FR-011, FR-027, TEST-010 to TEST-012]
- [X] T061 [US2] Implement `deposit` in `banking/services.py` with ownership validation, positive SGD validation, atomic balance credit, and completed `DEPOSIT` transaction UUID creation; verify service tests pass. [BR-001 to BR-007, BR-034]
- [X] T062 [US2] Create `DepositForm` in `banking/forms.py` with account selection and SGD amount validation; verify form tests cover invalid inputs. [FR-064]
- [X] T063 [US2] Implement deposit view, confirmation flow, success view, and route in `banking/views.py` and `banking/urls.py`; verify CSRF-protected POST and owner-only account selection tests pass. [SEC-001, SEC-002]
- [X] T064 [US2] Create `templates/banking/deposit_form.html`, `deposit_confirm.html`, and `deposit_success.html` showing selected account, amount, errors, and UUID transaction ID; verify rendered success contains transaction ID. [UX-014, TEST-036]
- [X] T065 [US2] Run deposit tests in `banking/tests/test_deposits.py`; verify Personal deposit, Business deposit, validation rejection, transaction record, and atomic rejection behaviour pass. [TEST-010, TEST-011, TEST-012, TEST-036, TEST-038]

## Phase 9: Personal Withdrawal Feature

**Purpose**: Implement Personal Account withdrawals, including full-balance withdrawal to SGD 0.00.

- [X] T066 [P] [US2] Add Personal withdrawal service tests in `banking/tests/test_withdrawals.py` for valid withdrawal, full-balance withdrawal, overdraft rejection, invalid amount rejection, completed `WITHDRAWAL` record creation, and unchanged state on failure; verify tests fail first. [FR-012, FR-013, TEST-013, TEST-014]
- [X] T067 [US2] Implement `withdraw_personal` in `banking/services.py` with positive SGD validation, sufficient-funds check, SGD 0.00 allowed result, atomic debit, and completed `WITHDRAWAL` transaction UUID creation; verify tests pass. [BR-008 to BR-010, BR-034]
- [X] T068 [US2] Create `WithdrawalForm` in `banking/forms.py` for Personal withdrawal amount and source account validation; verify form tests reject Business immediate withdrawal path. [FR-012, FR-029]
- [X] T069 [US2] Implement Personal withdrawal review, confirmation, success, and failure views/templates in `banking/views.py`, `banking/urls.py`, and `templates/banking/withdraw_*.html`; verify success page shows UUID transaction ID. [UX-015, TEST-036]
- [X] T070 [US2] Run Personal withdrawal tests in `banking/tests/test_withdrawals.py`; verify valid, full-balance, overdraft, invalid amount, transaction creation, and atomic failure tests pass. [TEST-013, TEST-014, TEST-036, TEST-038]

## Phase 10: Recipient Resolution and Transfer Review Flow

**Purpose**: Verify recipient lookup and safe confirmation before implementing transfer money movement.

- [X] T071 [P] [US4] Add recipient-resolution tests in `banking/tests/test_transfers_resolution.py` for Personal recipient lookup by phone, Business recipient lookup by UEN, unknown phone, unknown UEN, mismatched identifier/account type, self-transfer, and same-user Personal/Business transfer rejection; verify tests fail first. [FR-043 to FR-051, TEST-020 to TEST-028]
- [X] T072 [P] [US4] Add view tests in `banking/tests/test_transfer_views.py` for transfer form recipient type selector, adaptive identifier labels, safe recipient confirmation content, approval-required notice, and no sensitive email exposure; verify tests fail first. [FR-049, SEC-006, UX-017 to UX-019, TEST-025, TEST-048]
- [X] T073 [US4] Implement `resolve_transfer_recipient` and `preview_transfer` in `banking/services.py` with recipient type, phone/UEN normalisation, mismatch detection, unknown recipient errors, self-transfer rejection, and same-user cross-account rejection; verify recipient-resolution tests pass. [BR-028 to BR-033]
- [X] T074 [US4] Create `TransferStartForm` and transfer confirmation form support in `banking/forms.py`; verify form tests cover Personal phone field, Business UEN field, and amount validation. [FR-043 to FR-049]
- [X] T075 [US4] Implement transfer start and confirmation preview views/routes in `banking/views.py` and `banking/urls.py` without money movement; verify safe confirmation tests pass. [FR-049, TEST-025]
- [X] T076 [US4] Create `templates/banking/transfer_start.html` and `transfer_confirm.html` with source account, recipient type, phone/UEN identifier, amount, safe recipient details, approval requirement, and retained-minimum notice; verify UX tests pass. [UX-017 to UX-020]
- [X] T077 [US4] Run transfer lookup and review tests in `banking/tests/test_transfers_resolution.py` and `banking/tests/test_transfer_views.py`; verify lookup, mismatch, unknown, self-transfer, same-user transfer, and safe confirmation behaviours pass before transfer completion work. [TEST-020 to TEST-028, TEST-048]

## Phase 11: Personal Outgoing Transfers

**Purpose**: Implement immediate Personal Account transfers with linked records and atomicity.

- [X] T078 [P] [US4] Add Personal transfer service tests in `banking/tests/test_personal_transfers.py` for Personal-to-Personal transfer, Personal-to-Business transfer by UEN, full-balance transfer to SGD 0.00, insufficient-funds rejection, linked transaction records, shared transfer operation ID, and atomic rollback; verify tests fail first. [FR-014, FR-015, FR-052 to FR-055, TEST-015, TEST-016, TEST-037, TEST-038]
- [X] T079 [US4] Implement `transfer_from_personal` in `banking/services.py` with current balance re-read, sufficient-funds validation, atomic sender debit, recipient credit, `TransferOperation`, `TRANSFER_DEBIT`, and `TRANSFER_CREDIT` records; verify service tests pass. [BR-034 to BR-037]
- [X] T080 [US4] Wire Personal sender confirmation POST in `banking/views.py` to `transfer_from_personal`; verify Personal sender transfer view tests pass. [FR-052]
- [X] T081 [US4] Create `templates/banking/transfer_success.html` showing amount, safe recipient details, status, transfer operation ID, and sender debit UUID transaction ID; verify rendered success contains required identifiers. [UX-020, TEST-037]
- [X] T082 [US4] Run Personal transfer tests in `banking/tests/test_personal_transfers.py`; verify Personal-to-Personal, Personal-to-Business, full-balance, insufficient-funds, linked records, shared operation ID, and rollback tests pass. [TEST-015, TEST-016, TEST-020, TEST-021, TEST-037, TEST-038]

## Phase 12: Business Withdrawal Approval Requests

**Purpose**: Implement Business withdrawal request creation without moving funds.

- [X] T083 [P] [US5] Add Business withdrawal request tests in `banking/tests/test_business_withdrawal_requests.py` for PENDING request creation, unchanged balance, no completed withdrawal transaction before completion, cancellation to CANCELLED, and terminal status immutability; verify tests fail first. [FR-029, FR-031, FR-040 to FR-042, TEST-018, TEST-040]
- [X] T084 [US5] Implement `request_business_withdrawal` and `cancel_request` in `banking/services.py` for valid positive amount, owner permission, PENDING status, no balance movement, no completed transaction, and PENDING-only cancellation; verify request tests pass. [BR-018, BR-021, BR-025, BR-026]
- [X] T085 [US5] Create `BusinessWithdrawalRequestForm` in `banking/forms.py`; verify form tests cover valid amount and clear pending-approval messaging. [FR-029, UX-016]
- [X] T086 [US5] Implement Business withdrawal request and pending outcome views/templates in `banking/views.py`, `banking/urls.py`, `templates/banking/business_withdrawal_*.html`; verify pending page states no immediate balance change. [UX-016, UX-026]
- [X] T087 [US5] Add approval-list visibility tests for authorised Personal Account in `banking/tests/test_approval_visibility.py`; verify only the linked authorised Personal Account sees eligible Business withdrawal requests. [FR-034, SEC-002, TEST-039]

## Phase 13: Business Transfer Approval Requests

**Purpose**: Implement Business outgoing transfer request creation without moving funds.

- [X] T088 [P] [US5] Add Business transfer request tests in `banking/tests/test_business_transfer_requests.py` for Business-to-Personal PENDING request, Business-to-Business PENDING request, invalid destination rejection, prohibited same-user transfer rejection, no sender debit, no recipient credit, no transfer operation, and no completed transactions while PENDING; verify tests fail first. [FR-030, FR-031, TEST-029, TEST-031]
- [X] T089 [US5] Implement `request_business_transfer` in `banking/services.py` using recipient resolution, prohibited-transfer validation, valid amount validation, PENDING request creation, and no financial movement; verify service tests pass. [BR-018, BR-021, BR-028 to BR-033]
- [X] T090 [US5] Wire Business sender transfer confirmation POST in `banking/views.py` to `request_business_transfer`; verify Business transfer request view tests pass. [FR-030, UX-017]
- [X] T091 [US5] Create or extend `templates/banking/transfer_pending.html` for Business outgoing transfer pending outcome with safe recipient details and no-fund-reservation message; verify rendered pending state is clear. [UX-026, UX-027]
- [X] T092 [US5] Run Business request tests in `banking/tests/test_business_withdrawal_requests.py`, `banking/tests/test_business_transfer_requests.py`, and `banking/tests/test_approval_visibility.py`; verify Business withdrawal and Business transfer PENDING creation, no movement, no completed records, cancellation, and authorised visibility tests pass. [TEST-018, TEST-029, TEST-031, TEST-039, TEST-040]

## Phase 14: Approval Resolution and Approval UI

**Purpose**: Complete Business approval actions and approval screens.

- [X] T093 [P] [US5] Add approval-resolution service tests in `banking/tests/test_approvals_resolution.py` for unauthorised approval rejection, valid Business withdrawal completion leaving exactly SGD 7,000.00, valid Business transfer completion leaving exactly SGD 7,000.00, direct approval-time withdrawal failure when the resulting balance would be SGD 6,999.99, direct approval-time transfer failure when the resulting balance would be SGD 6,999.99, FAILED status with unchanged Business and recipient balances, no completed withdrawal transaction on failed withdrawal approval, no Transfer Operation or TRANSFER_DEBIT/TRANSFER_CREDIT records on failed transfer approval, rejection to REJECTED, cancellation to CANCELLED, terminal-state immutability, and no persisted APPROVED status; verify tests fail first. [FR-034 to FR-041, BR-019, BR-021, BR-023 to BR-027, BR-034 to BR-037, TEST-017, TEST-019, TEST-030, TEST-035, TEST-038, TEST-039, TEST-040]
- [X] T094 [P] [US5] Add approval view tests in `banking/tests/test_approvals_views.py` for status filtering, request detail, projected balance, explicit SGD 7,000.00 pass and SGD 6,999.99 failure retained-minimum messaging, approve/reject buttons for PENDING only, and no action controls for final states; verify tests fail first. [UX-021 to UX-023, TEST-049]
- [X] T095 [US5] Implement `approve_request` in `banking/services.py` for authorised Personal Account only, PENDING-only action, current revalidation, retained-minimum enforcement, completed Business withdrawal, completed Business transfer, linked records, COMPLETED status, and FAILED status on approval-time validation failure; verify service tests pass. [BR-018 to BR-027, BR-034 to BR-037]
- [X] T096 [US5] Implement `reject_request` in `banking/services.py` for authorised Personal Account only, PENDING-only action, REJECTED status, and no balance movement; verify rejection tests pass. [FR-034, FR-040, FR-041]
- [X] T097 [US5] Implement approval list/detail/filter/action views in `banking/views.py` and routes in `banking/urls.py`; verify access and status filtering tests pass. [FR-057, UX-021]
- [X] T098 [US5] Create `templates/banking/approvals_list.html` and `approvals_detail.html` with status badges, safe recipient details, projected balance, retained-minimum result, approve/reject/cancel controls, and final-state display; verify approval UI tests pass. [UX-021 to UX-023]
- [X] T099 [US5] Run approval tests in `banking/tests/test_approvals_resolution.py` and `banking/tests/test_approvals_views.py`; verify authorised approval, unauthorised denial, withdrawal completion at exactly SGD 7,000.00 retained balance, transfer completion at exactly SGD 7,000.00 retained balance, retained-minimum FAILED at SGD 6,999.99, rejection, cancellation, terminal immutability, projected balance, and no APPROVED status pass. [TEST-017, TEST-019, TEST-030, TEST-035, TEST-039, TEST-040, TEST-049]

## Phase 15: Multiple Pending Request Handling

**Purpose**: Prove simultaneous PENDING Business requests, no reservation, and independent revalidation.

- [X] T100 [P] [US5] Add multiple-PENDING tests in `banking/tests/test_multiple_pending_requests.py` for two concurrent PENDING requests, unchanged displayed balance, no fund reservation or movement while PENDING, first request completion reducing available Business balance, second request becoming FAILED when approval would leave exactly SGD 6,999.99, Approval History showing both workflow outcomes, and Transaction History containing only the successfully completed movement; verify tests fail first if not already covered. [FR-031 to FR-037, BR-021 to BR-027, TEST-032 to TEST-034, TEST-038, TEST-043, TEST-044]
- [X] T101 [US5] Adjust `banking/services.py` approval and request creation logic if needed so multiple PENDING requests are allowed and never reserve funds; verify service tests pass. [BR-021, BR-022]
- [X] T102 [US5] Ensure dashboard and Business detail views in `banking/views.py` show actual balance and PENDING counts without subtracting PENDING requests; verify view tests pass. [FR-032, UX-010]
- [X] T103 [US5] Ensure approval history display in `templates/banking/approvals_list.html` accurately shows one COMPLETED and one FAILED outcome after sequential approvals; verify multiple-PENDING view tests pass. [FR-057, FR-059]
- [X] T104 [US5] Run multiple-PENDING regression tests in `banking/tests/test_multiple_pending_requests.py`; verify coexistence of PENDING requests, no reservation, first successful completion, second FAILED at SGD 6,999.99, Transaction History, and Approval History behaviours pass. [TEST-032, TEST-033, TEST-034, TEST-038, TEST-043, TEST-044]

## Phase 16: Transaction History and Approval History

**Purpose**: Deliver distinct completed financial history and Business workflow history.

- [X] T105 [P] [US7] Add transaction-history tests in `banking/tests/test_histories.py` for completed deposits, withdrawals, transfer debit/credit records, UUID display, transfer operation ID display, credit/debit labels, filters, and exclusion of PENDING/REJECTED/CANCELLED/FAILED workflow records; verify tests fail first. [FR-056 to FR-063, TEST-036, TEST-037, TEST-043, TEST-050]
- [X] T106 [P] [US7] Add access-control history tests in `banking/tests/test_history_access_control.py` for another user's account, Transaction History, and Approval History denial; verify tests fail first. [FR-005, SEC-002, TEST-041]
- [X] T107 [US7] Implement transaction-history query helpers in `banking/services.py` or `banking/views.py` returning completed financial movements only and respecting account ownership; verify service/view tests pass. [FR-056, FR-059]
- [X] T108 [US7] Implement `/transactions/` view and route in `banking/views.py` and `banking/urls.py` with account and transaction-type filters; verify filter tests pass. [FR-060 to FR-062, UX-024]
- [X] T109 [US7] Create `templates/banking/transactions.html` with readable rows/cards, UUID transaction IDs, transfer operation IDs, credit/debit labels, filters, and empty state; verify rendered history tests pass. [UX-024, UX-026]
- [X] T110 [US7] Ensure Approval History remains in Approvals pages and includes PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED workflow records while Transaction History excludes non-completed workflow records; verify combined history tests pass. [FR-057 to FR-059, BR-039]
- [X] T111 [US7] Run history tests in `banking/tests/test_histories.py` and `banking/tests/test_history_access_control.py`; verify completed transaction visibility, approval visibility, separation, transfer IDs, access denial, and completed Business operation dual-audit behaviour pass. [TEST-041 to TEST-044, TEST-050]

## Phase 17: UI Polish, Accessibility, and Responsive Verification

**Purpose**: Finish Midnight Ledger presentation and measurable UI acceptance.

- [X] T112 [P] [US6] Add UI snapshot/assertion tests in `banking/tests/test_ui_polish.py` for required page headings, visible labels, status text, SGD formatting, and identifier display on major screens; verify tests fail where polish is incomplete. [UX-001 to UX-027, TEST-045 to TEST-053]
- [X] T113 [US6] Complete Midnight Ledger styling in `static/css/app.css` across authentication, dashboard, account, deposit, withdrawal, transfer, approval, and transaction pages; verify manual and rendered checks show consistent design treatment. [UX-001, UX-002]
- [X] T114 [US6] Ensure all templates in `templates/users/`, `templates/banking/`, and `templates/components/` use visible labels, inline field errors, clear primary actions, and calm success/error/PENDING/FAILED/REJECTED/CANCELLED messages; verify UI tests pass. [UX-011, UX-026, UX-027, NFR-006, NFR-007]
- [X] T115 [US6] Add or refine focus styles, keyboard-friendly form order, non-colour-only status labels, and high-contrast text in `static/css/app.css` and templates; verify accessibility checklist entries and tests pass. [NFR-008 to NFR-011, TEST-052]
- [X] T116 [US6] Confirm all monetary values in templates use `format_sgd` or equivalent display helper; verify rendered tests show `SGD` marker and two decimal places. [NFR-012, SC-018]
- [X] T117 [US6] Confirm phone numbers and UEN values are safely presented or masked where appropriate in transfer confirmation, transaction rows, account cards, and approvals; verify no email or sensitive account details appear. [SEC-006, UX-019, UX-025]
- [X] T118 [US6] Perform narrow-width manual verification for dashboard cards, transfer forms, approval requests, and transaction history; record result in `specs/001-banking-mvp/traceability.md`. [NFR-014 to NFR-016, TEST-053]
- [X] T119 [US6] Verify review/confirmation pages exist for final or consequential deposit, withdrawal, transfer, and approval actions; update missing templates/views if needed. [NFR-013, SC-021]

## Phase 18: Security and Secrets Verification

**Purpose**: Confirm server-side protection, CSRF, secret handling, and safe outputs.

- [X] T120 [P] Add security tests in `users/tests.py` and `banking/tests/test_security.py` for CSRF-protected modifying forms where testable, login requirements, account ownership denial, approval-access denial, and safe invalid-sign-in errors; verify tests fail where protection is missing. [SEC-001 to SEC-005, TEST-039, TEST-041]
- [X] T121 Ensure all state-changing views in `users/views.py` and `banking/views.py` require POST plus CSRF and enforce authentication/ownership/approval checks server-side; verify security tests pass. [SEC-001, SEC-002, SEC-004]
- [X] T122 Review `bankapp/settings.py`, `.gitignore`, and local config handling so `DJANGO_SECRET_KEY` is environment-loaded and secrets/database files are ignored; verify `git status --ignored` and settings tests/manual checks pass. [SEC-007]
- [X] T123 Review templates and errors in `templates/users/`, `templates/banking/`, and `templates/components/` to ensure passwords, emails in recipient confirmation, sensitive identifiers, stack traces, and vague unsafe errors are not exposed; verify rendered tests pass. [SEC-003, SEC-005, SEC-006]
- [X] T124 Document local MVP security limitations in `quickstart.md` or `README.md`; verify disclaimer states no real banking, public production use, external integrations, or real money movement. [SEC-007, NFR-001]

## Phase 19: Test Completion, Traceability, and Quality Gates

**Purpose**: Prove the implementation satisfies the constitution and all mandatory rule tests.

- [X] T125 Run the complete Django test suite with `python manage.py test` across `users/tests.py` and the `banking/tests/` package; verify all tests pass and failures are resolved without weakening requirements. [TEST-001 to TEST-053]
- [X] T126 Update `specs/001-banking-mvp/traceability.md` with final implementation file paths and test paths for every BR, FR, SEC, NFR, UX, and TEST mapping; verify no required identifier is unmapped. [NFR-005]
- [X] T127 Review implemented behaviour against `.specify/memory/constitution.md`, `specs/001-banking-mvp/spec.md`, and `specs/001-banking-mvp/plan.md`; verify no unapproved technology, product behaviour, or approval/transfer rule drift exists. [Constitution §I to §XIII]
- [X] T128 Confirm completed transaction records are immutable through ordinary UI flows and failed/PENDING/REJECTED/CANCELLED/FAILED operations do not create completed financial records; verify test evidence exists. [BR-006, BR-007, BR-038, TEST-038, TEST-042, TEST-043]
- [X] T129 Confirm Personal phone transfers, Business UEN transfers, identifier mismatch rejection, safe confirmation, and same-user transfer rejection are all implemented and tested; verify `TEST-020` through `TEST-028` pass. [FR-043 to FR-051]
- [X] T130 Confirm Business approval, retained-minimum enforcement, no persisted APPROVED status, multiple PENDING requests, and approval-time FAILED behaviour are implemented and tested; verify `TEST-017` to `TEST-019` and `TEST-029` to `TEST-035` pass. [FR-029 to FR-042]
- [X] T131 Document any non-blocking known limitations inside approved MVP scope in `README.md` or `quickstart.md`; verify no limitation contradicts a mandatory requirement. [NFR-001]

## Phase 20: Local macOS Deployment and Documentation

**Purpose**: Finalise local setup, Waitress launch, and repository hygiene documentation.

- [X] T132 Update `quickstart.md` with final dependency installation, virtual environment, environment variable, migration, static-file, test, Django runserver, and Waitress startup commands; verify commands match actual project package names. [NFR-014]
- [X] T133 Create or update `README.md` to point to `specs/001-banking-mvp/quickstart.md`, constitution, and local MVP disclaimer; verify no production-readiness claims are made. [NFR-001, SEC-007]
- [X] T134 Verify `python manage.py migrate`, `python manage.py test`, and `python manage.py collectstatic` if configured run on a clean local SQLite setup; record outcome in `quickstart.md` or implementation notes. [TEST-001 to TEST-053]
- [X] T135 Verify Waitress local launch command starts `bankapp.wsgi:application` on `127.0.0.1:8000`; record local browser access result and stop the server after verification. [NFR-014]
- [X] T136 Perform final repository hygiene check for secrets, `.env`, `db.sqlite3`, SQLite sidecars, virtual environments, caches, and collected static artifacts; verify none are staged for commit. [SEC-007]
- [X] T137 Perform final manual smoke test for registration, login, Personal setup, Business setup, deposit, withdrawal, Personal transfer, Business PENDING request, approval, histories, and sign-out; record result in `specs/001-banking-mvp/traceability.md`. [SC-001 to SC-025]

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** has no dependencies.
- **Phase 2** depends on Phase 1 because the custom user model must be configured before initial migrations are finalised.
- **Phase 3** depends on Phase 2 because banking models reference the custom user model.
- **Phase 4** depends on Phase 3 because service helpers depend on account and transaction models.
- **Phase 5** depends on Phase 4.
- **Phase 6** depends on Phase 5 because Business Accounts require an existing Personal Account.
- **Phase 7** can start after Phase 5 for shell/card work, but final dashboard content depends on Phase 6 and later history data.
- **Phase 8** depends on Phase 5 and Phase 4.
- **Phase 9** depends on Phase 5 and Phase 4.
- **Phase 10** depends on Phase 5, Phase 6, and Phase 4.
- **Phase 11** depends on Phase 10.
- **Phase 12** depends on Phase 6 and Phase 4.
- **Phase 13** depends on Phase 10 and Phase 12 patterns.
- **Phase 14** depends on Phases 12 and 13.
- **Phase 15** depends on Phase 14.
- **Phase 16** depends on completed transaction and approval workflows from Phases 8 through 15.
- **Phase 17** depends on functional templates and views from Phases 7 through 16.
- **Phase 18** can run alongside later feature phases but must complete before final quality gates.
- **Phase 19** depends on all feature phases.
- **Phase 20** depends on all implementation and verification work.

### User Story Dependencies

- **US1**: Start after Phase 1.
- **US2**: Start after foundational banking models/services in Phases 3 and 4.
- **US3**: Depends on US2 Personal Account creation.
- **US4**: Depends on US2 and US3 account availability plus recipient resolution.
- **US5**: Depends on US3 and transfer/request foundations.
- **US6**: Can begin after base setup, but final UI requires all feature views.
- **US7**: Depends on completed financial and approval records from US2 through US5.

### Parallel Opportunities

- T022 through T025 can run in parallel because they add different model-test modules under `banking/tests/`.
- T031 and T032 can run in parallel because they target `banking/tests/test_money_validation.py` and `banking/tests/test_access_control.py`.
- T044 and T045 can run in parallel because they target `banking/tests/test_business_accounts.py` and `banking/tests/test_business_account_atomicity.py`.
- T052 and T056 can run in parallel after base templates exist because dashboard tests and component fragments touch different concerns.
- T071 and T072 can run in parallel because they target `banking/tests/test_transfers_resolution.py` and `banking/tests/test_transfer_views.py`.
- T093 and T094 can run in parallel because they target `banking/tests/test_approvals_resolution.py` and `banking/tests/test_approvals_views.py`.
- T105 and T106 can run in parallel because they target `banking/tests/test_histories.py` and `banking/tests/test_history_access_control.py`.
- T112 and T120 can run in parallel because they target `banking/tests/test_ui_polish.py` and `banking/tests/test_security.py` plus `users/tests.py`.

## Parallel Example: Transfer Workstream

```text
Task: T071 [US4] Add recipient-resolution tests in banking/tests/test_transfers_resolution.py
Task: T072 [US4] Add view tests for transfer form and safe confirmation in banking/tests/test_transfer_views.py
```

After T071 and T072 are complete, T073 through T077 should proceed in order.

## Implementation Strategy

### MVP First

1. Complete Phases 1 through 4.
2. Complete US1 authentication and US2 Personal Account creation.
3. Validate registration, sign-in, Personal Account setup, and protected access.
4. Continue through Business Account creation, deposits, withdrawals, transfers, approvals, histories, and UI polish.

### Tests-First Rule

For financial and permission-sensitive work, complete the listed test task before the implementation task. Tests should fail for the expected missing behaviour before implementation and pass after the corresponding service/view/template work.

### Incremental Delivery

Each phase should leave the application in a testable state. Do not proceed to dependent financial flows until the prior phase's tests pass, especially Decimal validation, account constraints, recipient resolution, and approval lifecycle tests.

## Completion Gate

Implementation is complete only when:

- All mandatory automated tests pass.
- All approved business rules are implemented without weakening the constitution.
- Completed financial transactions are auditable and immutable through ordinary UI flows.
- Personal Account phone-number transfers and Business Account UEN transfers work as specified.
- Business approval, multiple PENDING requests, no-reservation behaviour, retained-minimum enforcement, and FAILED approval-time outcomes are enforced.
- Transaction History contains completed financial movements only.
- Approval History contains Business workflow records and remains distinct from Transaction History.
- The premium server-rendered Midnight Ledger UI meets clarified acceptance requirements.
- Security, CSRF, ownership, approval-access, safe error, safe recipient confirmation, and secret-handling checks pass.
- Waitress local macOS launch is documented and verified.
- Traceability mapping is complete from requirement IDs to implementation components and tests.
