# Implementation Plan: Banking MVP v3.0.0

**Branch**: `001-banking-mvp` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-banking-mvp/spec.md`, governed by constitution version 3.0.0.

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design; no violations or unresolved clarifications remain.*

- **Distinct bank-account products**: The plan keeps Personal Account and Business Account as separate products. A Personal Login owns exactly one Personal Account. A Business Employee Access Login operates exactly one Business Account and is not a bank account.
- **Login-context isolation**: `users.CustomUser` carries an immutable MVP login context: `PERSONAL` or `BUSINESS_EMPLOYEE`. One login never accesses both contexts. Email is globally unique across all identities. Shared Business credentials are prohibited.
- **Recipient identity**: Personal Accounts receive transfers by unique phone number. Business Accounts receive transfers by unique UEN. Business employee logins have no receiving identifier.
- **SGD and Decimal money**: All financial amounts use Python `Decimal` and Django `DecimalField`; the MVP rejects zero, negative, malformed, non-SGD, over-capacity, and excessive-precision values.
- **Personal balance rules**: Personal Accounts open at `SGD 0.00`, require no opening deposit, have no minimum balance, and may be spent down to exactly `SGD 0.00` but never below.
- **Business balance rules**: Business Accounts require opening funding of at least `SGD 7,000.00`; completed outgoing Business withdrawals and transfers must leave at least `SGD 7,000.00`.
- **Provisioned employee access**: AUTHORISER-provisioned employee access replaces invitations. Provisioned employees start in `PASSWORD_CHANGE_REQUIRED`, must change temporary passwords before normal access, and may later be `ACTIVE` or `DEACTIVATED`.
- **Roles and governance**: MEMBER and AUTHORISER are the only roles. Multiple AUTHORISERS are permitted. Deactivating the final active AUTHORISER is prohibited. Demotion from AUTHORISER to MEMBER is outside scope.
- **Business approvals**: Any one active AUTHORISER may approve a valid outgoing Business request, including their own request. Persisted request statuses are only `PENDING`, `COMPLETED`, `REJECTED`, `CANCELLED`, and `FAILED`.
- **Financial records**: Completed financial transactions use UUID transaction IDs. Completed transfers create one shared UUID Transfer Operation ID and separate UUID debit/credit transaction IDs.
- **History separation**: Transaction History, Approval History, and Access Audit History are separate record families and separate UI areas.
- **Atomicity**: Financial movements and security-sensitive access changes are wrapped in Django transactions where multiple rows or balances change together.
- **Security, tests, traceability**: Password hashing, secret hygiene, CSRF, automated tests, and requirement-to-component/test traceability remain mandatory.
- **Deployment**: Local macOS execution uses Django and Waitress only.

## Summary

Build a beginner-friendly Django monolith for a local server-rendered SGD banking MVP. The v3.0.0 plan replaces all invitation and multi-Business-membership designs with company-owned Business Accounts operated by individually provisioned Business Employee Access Logins. AUTHORISERS create employee credentials, assign MEMBER or AUTHORISER roles, issue temporary passwords, enforce mandatory first-login password change, reset temporary passwords, deactivate/reactivate access, and maintain Access Audit History. Personal banking, Business approvals, transfer records, financial atomicity, and the Midnight Ledger UI are preserved and redesigned around the new access model.

## Technical Context

**Language/Version**: Python 3.11 or later

**Primary Dependencies**: Django and Waitress only

**Storage**: SQLite3 for local MVP persistence

**Testing**: Django built-in test framework

**Target Platform**: Local macOS development and local Waitress execution

**Project Type**: Server-rendered Django web application

**Performance Goals**: Human-scale local MVP; page actions should complete within normal local Django response times for dozens of development records

**Constraints**: No frontend framework, no Django REST Framework, no external CSS framework, no real banking/payment integration, no real email delivery, no OTP/SMS, no external UEN lookup, no queues, no WebSockets, no cloud deployment, no mandatory JavaScript for core flows

**Scale/Scope**: One Django project package, `users` app, `banking` app, custom CSS, server-rendered forms/pages, local SQLite data, and test coverage for TEST-001 through TEST-069

## Architecture

### Django Project Package: `bankapp`

Responsible for settings, environment variable configuration, static/template settings, top-level URLs, authentication model configuration, WSGI/Waitress entry point, local security defaults, and local-only deployment documentation.

### `users` App

Responsible for login identity and authentication:

- custom user model with unique email login;
- display name/username;
- Django password hashing;
- login context choices `PERSONAL` and `BUSINESS_EMPLOYEE`;
- sign-in and sign-out;
- route guards for Personal versus Business contexts;
- mandatory password-change routing for Business employees in `PASSWORD_CHANGE_REQUIRED`.

The user model is the authenticated identity only. It is not a financial account.

### `banking` App

Responsible for financial accounts, employee access, banking operations, histories, and Business governance:

- Personal Accounts;
- Business Accounts;
- Business Employee Access records;
- completed financial transactions;
- transfer operations;
- Business outgoing requests;
- Access Audit events;
- Personal and Business registration services;
- deposits, withdrawals, transfers, approvals, cancellations;
- Team Access administration;
- Transaction, Approval, and Access Audit pages;
- Midnight Ledger templates and custom CSS integration.

Invitation models, invitation services, invitation pages, invitation tests, invitation navigation, and multi-Business Account selector logic are superseded and must be removed or replaced during implementation.

## Required Modelling Decision: Business Employee Access Login

**Decision**: Use a custom `CustomUser` for authentication, separate financial account models, and a `BusinessEmployeeAccess` model for the employee's scoped company-account access.

```text
CustomUser(PERSONAL) 1--1 PersonalAccount
CustomUser(BUSINESS_EMPLOYEE) 1--1 BusinessEmployeeAccess *--1 BusinessAccount
BusinessAccount 1--* BusinessOutgoingRequest
BusinessAccount 1--* AccessAuditEvent
PersonalAccount / BusinessAccount -- CompletedFinancialTransaction
PersonalAccount / BusinessAccount -- TransferOperation
```

**Rationale**: This cleanly separates identity, money, and permission state. A Business Employee Access Login has no balance, no phone number, no UEN, and no independent bank account. The Business Account owns the UEN and balance. The employee access record owns role and access status.

**Rejected alternatives**:

- A Business user with many memberships: conflicts with v3 one-Business-Account-per-employee-login.
- Invitation acceptance: superseded by v3.
- Employee access state on the Business Account: conflates account state with per-employee security state.

**Source of truth for mandatory password change**: `BusinessEmployeeAccess.access_status` is the source of truth. `CustomUser` stores password hashes and authentication metadata; services update the employee access status after password changes or resets.

## Registration and Login Flows

### Personal Account Registration

Inputs: display name/username, unique email, password, confirmation, unique phone number.

Atomic success creates:

- one `PERSONAL` login;
- one Personal Account;
- balance `SGD 0.00`;
- no opening transaction;
- no Business access.

### New Business Account Registration

Inputs: initial AUTHORISER display name, unique login email, password, confirmation, business display name, unique UEN, opening deposit at least `SGD 7,000.00`.

Atomic success creates:

- one `BUSINESS_EMPLOYEE` login for the creator;
- one Business Account;
- one `BusinessEmployeeAccess` record with role `AUTHORISER` and status `ACTIVE`;
- one completed `BUSINESS_OPENING_DEPOSIT` transaction;
- Access Audit events for `BUSINESS_ACCOUNT_CREATED` and `INITIAL_AUTHORISER_CREATED`.

### Provisioned Employee Login

Provisioned employees do not self-register for a bank account. An active AUTHORISER creates an employee login in Team Access.

Inputs: employee display name, unique email, role `MEMBER` or `AUTHORISER`, temporary password, confirmation.

Atomic success creates:

- one `BUSINESS_EMPLOYEE` login;
- one `BusinessEmployeeAccess` scoped to the current Business Account;
- status `PASSWORD_CHANGE_REQUIRED`;
- Access Audit events for `EMPLOYEE_ACCESS_CREATED` and `TEMPORARY_PASSWORD_ISSUED`.

Plaintext temporary passwords are never stored and are not retrievable after the workflow response.

## Service Layer Plan

All rule enforcement lives in services callable from forms/views and tests.

### Identity and Registration Services

- `register_personal_account`: create Personal login and Personal Account atomically.
- `register_business_account`: create Business Account, initial employee login/access, opening financial transaction, and initial audit events atomically.
- `require_personal_login`, `require_business_employee`, `require_active_employee`, `require_authoriser`: reusable permission helpers.

### Employee Access Services

- `provision_employee_access`: active AUTHORISER only; validate global email uniqueness; hash temporary password; create login/access/audit records atomically.
- `complete_mandatory_password_change`: authenticated Business employee in `PASSWORD_CHANGE_REQUIRED`; set new password; transition to `ACTIVE`; write password-change/activation audit event.
- `reset_employee_temporary_password`: active AUTHORISER only; target must be another employee in same Business Account; set new temporary password; set `PASSWORD_CHANGE_REQUIRED`; audit without password content.
- `promote_member_to_authoriser`: active AUTHORISER only; MEMBER to AUTHORISER; no demotion path.
- `deactivate_employee_access`: active AUTHORISER only; allow MEMBER deactivation and eligible AUTHORISER deactivation; reject final active AUTHORISER; audit success and retained rejected final-AUTHORISER attempt.
- `reactivate_employee_access`: active AUTHORISER only; issue new temporary password; set `PASSWORD_CHANGE_REQUIRED`; audit reactivation and password issuance.

Administrative self-reset by an AUTHORISER is outside MVP scope per FR-045.

### Financial Services

- `parse_sgd_amount` and `format_sgd`: central Decimal validation and display helpers.
- `deposit`: Personal owner or active Business employee deposit; update balance and create completed transaction atomically.
- `withdraw_personal`: Personal owner withdrawal; allow final `SGD 0.00`; create completed transaction atomically.
- `resolve_recipient`: selected destination type plus phone/UEN; reject unknown, mismatched, or self-transfer.
- `transfer_personal`: debit Personal sender, credit Personal/Business recipient, create Transfer Operation and linked transactions atomically.
- `submit_business_withdrawal_request`: active MEMBER/AUTHORISER; create `PENDING` only.
- `submit_business_transfer_request`: active MEMBER/AUTHORISER; resolve destination; create `PENDING` only.
- `approve_business_request`: active AUTHORISER; self-approval allowed; revalidate balance, retained minimum, destination, status, and access; transition directly to `COMPLETED` with financial records or to `FAILED` without movement.
- `reject_business_request`: active AUTHORISER; `PENDING` to `REJECTED`.
- `cancel_business_request`: requester MEMBER may cancel own `PENDING`; AUTHORISER may cancel any `PENDING`.

## Money Handling and Atomicity Strategy

- Use `Decimal` everywhere for money.
- Store balances and amounts as `DecimalField(max_digits=12, decimal_places=2)` unless implementation finds a documented need for a larger local MVP limit.
- Reject zero, negative, malformed, non-numeric, non-SGD, over-capacity, and more-than-two-decimal-place inputs.
- Format all displayed money as `SGD 0.00`.
- Wrap multi-row actions in `transaction.atomic()`.
- Re-read relevant account/access/request state immediately before approval completion, password reset, deactivation, reactivation, and financial movement.
- SQLite is accepted only for local MVP correctness. It does not provide production-grade concurrency controls; production database concerns are out of scope.

## Forms and Server-Rendered Workflow Plan

### Public and Authentication

- product/account-type selection;
- Personal registration;
- Business Account registration;
- sign-in;
- sign-out;
- mandatory first-login password change.

### Personal Financial Functions

- Personal Dashboard and account detail;
- deposit with confirmation;
- withdrawal with projected balance;
- transfer destination selection, recipient confirmation, and completion;
- Transaction History filtering.

### Business Financial Functions

- Business Dashboard;
- deposit;
- outgoing withdrawal request;
- outgoing transfer request;
- approval list/detail/action;
- rejection and cancellation;
- Transaction History filtering;
- Approval History filtering.

### Business Team Access Functions

- Team Access overview;
- Add Employee Access;
- promote MEMBER to AUTHORISER;
- reset employee temporary password;
- deactivate access;
- reactivate access with new temporary password;
- Access Audit History display/filtering.

All consequential financial and access-management actions use POST plus CSRF and a review/confirmation step where appropriate. No core workflow requires JavaScript.

## Route, View, and Permission Plan

### Public Routes

- `/` product selection;
- `/register/personal/`;
- `/register/business/`;
- `/login/`;
- `/logout/`;
- `/password-change-required/`.

### Personal Routes

Accessible only to authenticated `PERSONAL` logins:

- Personal Dashboard;
- Personal Account detail;
- deposit;
- withdrawal;
- transfer;
- transaction history.

### Business Routes

Accessible only to authenticated `BUSINESS_EMPLOYEE` logins with `ACTIVE` access, except mandatory password change:

- Business Dashboard;
- deposit;
- request withdrawal;
- request transfer;
- approvals;
- approval detail/action;
- Team Access;
- Add Employee Access;
- reset temporary password;
- promote employee;
- deactivate employee;
- reactivate employee;
- Access Audit History;
- Transaction History;
- Approval History.

Employees in `PASSWORD_CHANGE_REQUIRED` are redirected to mandatory password change and blocked from Business operational pages. `DEACTIVATED` employees are denied Business access. No active Invitations route or Business Account selector route exists.

## Midnight Ledger UI Redesign Plan

The UI redesign is a core deliverable, not optional polish.

### Visual System

Use custom CSS only:

- midnight/navy app background;
- layered charcoal navigation surfaces;
- off-white or soft neutral content cards;
- mint/teal primary and positive actions;
- amber pending and password-change-required states;
- restrained red destructive styling;
- high-contrast typography;
- defined spacing scale;
- restrained card radius and border/shadow rules;
- reusable buttons, tables, badges, alerts, empty states, forms, and focus styles;
- responsive grid/flex layouts that stack cleanly at narrower widths.

### Layout Improvement

Replace sparse v2 screens with purposeful layouts:

- wider dashboard and table containers;
- contextual page headers with account, role, and status;
- summary-stat cards;
- structured data panels;
- side-by-side desktop arrangements where useful;
- no small form stranded in a large blank canvas on core screens.

### Required Page Experiences

- **Public pages**: product selection, Personal registration, Business registration, sign-in.
- **Personal Dashboard**: balance hero card, receiving phone number, quick actions, recent transactions, no Business controls.
- **Business Dashboard**: business name, UEN, employee role/status, balance, retained-minimum reminder, available outgoing capacity indicator, pending count, recent transactions, recent approvals, AUTHORISER Team Access summary.
- **Team Access**: account context, active employee count, active AUTHORISER count, password-change-required count, deactivated count, employee list, permitted actions, no password exposure.
- **Add Employee Access**: role selector, temporary password fields, mandatory-change notice, heightened confirmation for AUTHORISER role.
- **Mandatory Password Change**: branded security checkpoint, restricted navigation, activation success.
- **Reset/Deactivate/Reactivate**: affected employee identity, status/role, consequences, last-AUTHORISER blocking message, success outcomes.
- **Financial and History Screens**: recipient confirmation, projected post-approval balance, retained-minimum compliance, distinct Transaction/Approval/Access Audit views.

Manual UI acceptance and view/template tests must cover navigation, permission-specific controls, password-change gating, Team Access, statuses, responsive layouts, labels, focus, contrast, and SGD formatting.

## Security Plan

- Use Django password hashing for all passwords and temporary passwords.
- Enforce unique email at model/form/service levels.
- Enforce Personal/Business login context on every protected route.
- Enforce Business employee scope through `BusinessEmployeeAccess`.
- Gate `PASSWORD_CHANGE_REQUIRED` users to password-change and sign-out only.
- Deny `DEACTIVATED` users all Business functionality and data.
- Enforce AUTHORISER-only access management, approval, and rejection server-side.
- Protect final active AUTHORISER from deactivation in services.
- Use CSRF protection on all state-changing forms.
- Keep phone, UEN, employee email, and recipient confirmation output safe and non-credential-bearing.
- Never display passwords, temporary passwords after handover, password hashes, or secrets in ordinary pages, errors, or audit histories.
- Load Django secret key from environment.
- Exclude `.env`, local SQLite databases, caches, virtual environments, collected static output, and secret material from Git.
- Display/document local-only educational MVP disclaimer.

## Testing Plan

Use Django's built-in test framework with separate modules for maintainability.

- `users/tests/test_authentication.py`: sign-in/out, password hashing, invalid credentials.
- `users/tests/test_access_context.py`: Personal/Business context isolation and route denial.
- `users/tests/test_registration_forms.py`: Personal and Business registration form behavior.
- `banking/tests/test_models.py`: model constraints, choices, UUIDs, no `APPROVED`, one employee account scope.
- `banking/tests/test_money_validation.py`: Decimal parsing, formatting, invalid inputs, boundaries.
- `banking/tests/test_personal_registration.py`: Personal Account creation, phone uniqueness, no opening deposit.
- `banking/tests/test_business_registration.py`: Business Account creation, opening deposit, initial AUTHORISER, opening transaction, audit events, rollback.
- `banking/tests/test_employee_access.py`: provisioning, duplicate email, password-change-required, one Business Account per employee login.
- `banking/tests/test_password_workflows.py`: mandatory change, reset, old password invalidation, no password exposure.
- `banking/tests/test_team_access.py`: promotion, deactivation, reactivation, final AUTHORISER protection, audit.
- `banking/tests/test_deposits_withdrawals.py`: Personal and Business deposits, Personal withdrawal boundaries.
- `banking/tests/test_recipient_resolution.py`: phone/UEN lookup, mismatch, unknown, self-transfer.
- `banking/tests/test_transfers.py`: Personal immediate transfers, linked transfer records.
- `banking/tests/test_business_requests.py`: Pending withdrawal/transfer requests, no money movement.
- `banking/tests/test_approvals.py`: approve/reject/cancel, self-approval, retained minimum, FAILED, terminal states.
- `banking/tests/test_multiple_pending.py`: non-reservation and independent revalidation.
- `banking/tests/test_histories.py`: Transaction/Approval/Access Audit separation and access denial.
- `banking/tests/test_ui_permissions.py`: navigation, Team Access controls, no Invitations, no Business selector, password-change gating.

The full suite must cover TEST-001 through TEST-069 from the specification.

## Superseded Implementation Refactoring Impact

The repository contains v2-era implementation paths that must be treated as superseded, not valid starting points:

- `banking/services/invitations.py`;
- invitation-related forms, views, URLs, templates, and tests;
- `templates/users/register_business_invited.html`;
- Business membership logic that allows one Business login to access multiple Business Accounts;
- Business Account selector logic and navigation;
- invitation audit event types;
- v2 migrations and local SQLite schema reflecting invitations/memberships.

Replacement targets:

- `BusinessEmployeeAccess` model;
- Team Access screens;
- provision employee forms/services;
- mandatory first-login password-change workflow;
- temporary-password reset workflow;
- deactivation/reactivation workflow;
- revised Access Audit event types;
- one-Business-Account-per-employee-login enforcement.

### Local Database and Migration Strategy

This project is a local learning MVP with no approved user data preservation requirement. Preferred implementation strategy:

1. Do not preserve obsolete local SQLite data.
2. Remove or replace superseded uncommitted development migrations where safe.
3. Reset the local SQLite database before applying the v3 schema.
4. Generate fresh migrations for the v3 data model during implementation.
5. Recreate test data through tests/fixtures only.

If migrations are committed and must be preserved by project policy at task time, the task list must switch to a forward-migration plan that removes invitation tables/fields and converts membership access to single-account employee access. Do not execute either strategy during planning.

## Traceability Deliverables

The v3 traceability map must link requirements to:

- data model entities;
- services;
- forms;
- views/routes;
- templates and reusable UI components;
- automated test modules;
- manual UI verification;
- security controls.

All v2 invitation and multi-membership requirements are superseded and excluded from active implementation.

## Project Structure

### Documentation

```text
specs/001-banking-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── refactoring-impact.md
├── traceability.md
├── contracts/
│   └── server-rendered-flows.md
└── tasks.md                 # Not regenerated by this command
```

### Source Code

```text
manage.py
bankapp/
├── settings.py
├── urls.py
├── wsgi.py
└── waitress_server.py
users/
├── models.py
├── forms.py
├── permissions.py
├── views.py
├── urls.py
└── tests/
banking/
├── models.py
├── forms.py
├── views.py
├── urls.py
├── services/
└── tests/
templates/
├── base_public.html
├── base_personal.html
├── base_business.html
├── users/
└── banking/
static/
└── css/
```

**Structure Decision**: Keep the existing Django monolith shape with `bankapp`, `users`, and `banking`. Refactor within these apps rather than creating new packages.

## Complexity Tracking

No constitution violations require justification.
