# Implementation Plan: Banking MVP

**Branch**: `001-banking-mvp` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-banking-mvp/spec.md`, amended constitution v2.0.0, and v2 requirements-quality checklist.

## Constitution Check

*GATE: Passed before Phase 0 research. Re-check after Phase 1 design: Passed.*

- **Approved local stack**: Uses Python 3.11+, Django, SQLite3, Django templates, custom CSS, Django built-in authentication/forms/validation/CSRF/transactions/migrations/tests, and Waitress for local macOS execution only. No REST API, frontend framework, external CSS framework, external bank/payment provider, external UEN registry, OTP, third-party auth, queues, WebSockets, cloud service, or mandatory JavaScript is introduced.
- **Separate login identities**: Plans mutually exclusive `PERSONAL` and `BUSINESS` user access contexts. One login identity never accesses both Personal and Business functionality. A real individual requiring both contexts must register separate credentials with different globally unique emails.
- **Authentication and secrets**: Passwords are managed through Django password hashing. Django secret key and local secret files are loaded from environment or ignored local files and are excluded from Git.
- **Personal Account rules**: Personal Account registration creates exactly one Personal Account for a `PERSONAL` user, with unique receiving phone number, starting balance SGD 0.00, no opening deposit, no retained minimum, and no negative balance.
- **Business Account rules**: Business registration creates a company-owned shared Business Account with business display name, unique UEN, opening deposit at least SGD 7,000.00, initial AUTHORISER membership, opening-deposit transaction, and access audit events. Business outgoing completed withdrawals/transfers must retain at least SGD 7,000.00.
- **Business membership governance**: Business access is through individual `BUSINESS` user memberships only. Roles are `MEMBER` and `AUTHORISER`. Multiple AUTHORISERS are supported, and every Business Account must retain at least one active AUTHORISER after membership changes.
- **Invitations**: AUTHORISERS may invite by email with intended `MEMBER` or `AUTHORISER` role. Access begins only after a matching Business-only identity accepts. Real email delivery is out of MVP scope.
- **Business outgoing approval**: MEMBER or AUTHORISER may submit outgoing requests. One AUTHORISER approval is sufficient, AUTHORISER self-approval is allowed, and persisted statuses are only `PENDING`, `COMPLETED`, `REJECTED`, `CANCELLED`, and `FAILED`. There is no persisted `APPROVED` status.
- **Transfers**: Personal destinations resolve by unique phone number; Business destinations resolve by unique UEN. Sender selects destination account type before entering the matching identifier. Unknown identifiers, mismatches, and same-account self-transfers are rejected.
- **Money and records**: All money is SGD, uses `Decimal`, and supports at most two decimal places. Completed deposits/withdrawals create immutable UUID transaction records. Completed transfers create one UUID transfer operation and two immutable UUID transaction records sharing that operation ID.
- **Histories**: Transaction History contains completed financial movements only. Approval History contains Business outgoing workflow records. Access Audit History contains Business access-governance events. The three are separate.
- **Atomicity**: Balance changes, transfer operation creation, completed transaction creation, approval transitions, invitation acceptance, membership changes, and audit events use Django transaction boundaries where state must commit together.
- **Testing and traceability**: Plan maps `FR-###`, `BR-###`, `SEC-###`, `NFR-###`, and `TEST-###` to components and Django tests. Mandatory tests cover identity separation, membership, invitations, financial correctness, approvals, histories, access control, and UI acceptance.

No constitutional violations or unresolved planning clarifications remain.

## Summary

Build a server-rendered Django monolith for a local SGD banking MVP with two exclusive login experiences:

- Personal users register directly into one Personal Account that receives transfers by phone number.
- Business users register into or are invited into company-owned shared Business Accounts that receive transfers by UEN and are governed through `MEMBER` and `AUTHORISER` memberships.

The plan replaces the superseded model where one user owned both account types and a Personal Account authorised Business transactions. Banking logic will live in service-layer modules inside the `banking` app so forms and views are not the only enforcement point. The UI remains the custom-CSS Midnight Ledger experience using Django templates.

## Technical Context

**Language/Version**: Python 3.11 or later

**Primary Dependencies**: Django and Waitress only

**Storage**: SQLite3 for local MVP persistence

**Testing**: Django built-in test framework

**Target Platform**: Local macOS browser use and Waitress launch

**Project Type**: Server-rendered Django web application

**Performance Goals**: Local interactive use by a small number of development users; correctness, atomicity, and auditability are higher priority than throughput.

**Constraints**: SGD-only; Decimal money arithmetic; no mandatory JavaScript for core flows; custom CSS only; no external email delivery for invitations; no external UEN or phone verification; no real banking integration.

**Scale/Scope**: MVP covers registration, authentication, Personal Accounts, Business Accounts, memberships, invitations, deposits, withdrawals, transfers, Business approval workflow, three histories, tests, traceability, and local deployment.

## Project Structure

### Documentation

```text
specs/001-banking-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── server-rendered-flows.md
├── traceability.md
└── tasks.md              # Existing v1 task list is superseded; regenerate with /speckit.tasks.
```

### Planned Source Layout

```text
manage.py
requirements.txt
.env.example
bankapp/
├── __init__.py
├── settings.py
├── urls.py
├── wsgi.py
└── waitress_server.py
users/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── managers.py
├── models.py
├── urls.py
├── views.py
├── templates/users/
└── tests/
banking/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── services/
│   ├── __init__.py
│   ├── accounts.py
│   ├── approvals.py
│   ├── invitations.py
│   ├── memberships.py
│   ├── money.py
│   └── transfers.py
├── urls.py
├── views.py
├── templates/banking/
└── tests/
templates/
├── base_public.html
├── base_personal.html
├── base_business.html
└── includes/
static/
└── css/
    └── midnight-ledger.css
```

**Structure Decision**: Use one Django project package, a `users` app for identity/authentication, and one cohesive `banking` app for accounts, membership, money movement, approvals, histories, and UI. Splitting banking into many domain apps is deferred because MVP traceability is easier with one domain boundary plus explicit service modules.

## Architecture Direction

### Django Project Package

Responsible for settings, environment configuration, root URLs, template/static configuration, authentication configuration, local security settings, and Waitress entry-point guidance.

### `users` App

Use a custom Django user model with:

- unique email as login identifier;
- username display name;
- Django-managed password hash;
- required `access_context` choice: `PERSONAL` or `BUSINESS`;
- ordinary user metadata.

The access context is set at registration and is not changeable through ordinary MVP user flows. Authentication views and decorators/helpers must reject cross-context access server-side.

### `banking` App

Responsible for:

- Personal Account and Business Account records;
- Business Membership and Invitation records;
- Access Audit Events;
- balances, deposits, withdrawals, transfers, Transfer Operations;
- completed financial transaction records;
- Business Approval Requests;
- Transaction History, Approval History, Access Audit History;
- Personal and Business dashboards and money-operation pages.

Financial, membership, invitation, and approval rules belong in service modules so views and forms call authoritative domain operations.

## Registration and Onboarding Plan

### Personal Registration

Inputs: username, unique email, password and confirmation, unique phone number.

Atomic result:

- create `PERSONAL` user;
- create one Personal Account with balance SGD 0.00 and unique phone number;
- grant no Business access;
- create no opening-deposit transaction.

### New Business Account Registration

Inputs: creator username, unique email, password and confirmation, business display name, unique UEN, opening deposit >= SGD 7,000.00.

Atomic result:

- create `BUSINESS` user;
- create Business Account with balance equal to opening deposit;
- create active AUTHORISER membership for creator;
- create `BUSINESS_OPENING_DEPOSIT` completed transaction;
- create Access Audit Events for account creation and initial AUTHORISER assignment.

Reject the whole operation if email is duplicate, UEN is missing/duplicate, amount is invalid, opening deposit is below SGD 7,000.00, or any account/membership/transaction/audit creation fails.

### Invited Business User Registration and Acceptance

Support:

- existing `BUSINESS` user with matching invited email accepting a pending invitation;
- new Business-only registration from an invitation entry point;
- rejection when a `PERSONAL` user attempts acceptance;
- membership activation only after acceptance;
- one Business user accepting memberships in multiple Business Accounts.

No real email sending is planned. The MVP stores invitations and exposes acceptance through server-rendered invitation pages or invitation-specific entry links/IDs.

## Data and Domain Model Decisions

Detailed entities are in [data-model.md](./data-model.md). Key decisions:

- Use separate concrete `PersonalAccount` and `BusinessAccount` models rather than one type-discriminated account table. This keeps ownership and membership constraints readable for beginners.
- Use an explicit account-reference pair on completed transactions and transfer operations: nullable Personal Account field plus nullable Business Account field, with validation requiring exactly one side where an account is referenced. This avoids generic relations while supporting both account types in transfers and histories.
- Use inactive membership rows with `removed_at` rather than deleting memberships. This preserves auditability and makes immediate access loss an active-membership filter.
- Exclude invitation expiry from MVP. Invitation statuses are `PENDING`, `ACCEPTED`, and `CANCELLED`; expiry can be added later by amendment or clarification.
- Duplicate pending invitations: block a second `PENDING` invitation for the same Business Account and invited email. Accepted or cancelled invitations remain audit history and do not block future invitations.

## Service Layer Plan

Planned modules inside `banking/services/`:

- `money.py`: Decimal parsing, positivity, precision, SGD formatting, boundary constants, domain exceptions.
- `accounts.py`: Personal registration account creation; Business registration account creation; deposits; Personal withdrawals.
- `transfers.py`: recipient resolution by account type; safe recipient preview; Personal transfer completion.
- `invitations.py`: invitation creation, duplicate pending rule, acceptance, invitation-specific Business registration hooks.
- `memberships.py`: active membership checks, role checks, promotion, removal, last-AUTHORISER protection.
- `approvals.py`: Business withdrawal/transfer request submission, approval, rejection, cancellation, failed approval-time validation.

Views and forms may provide user-friendly validation and display, but service methods enforce all financial, permission, retained-minimum, membership, and audit invariants.

## Money Handling Strategy

- Use Python `Decimal` for all money operations.
- Use Django `DecimalField(max_digits=12, decimal_places=2)` for balances and transaction amounts. This supports up to SGD 9,999,999,999.99, comfortably beyond local MVP needs while remaining simple.
- Reject zero, negative, malformed, non-numeric, non-SGD, excessive-precision, and over-capacity amounts.
- Display amounts as `SGD 0.00`.
- Personal withdrawals/transfers may leave SGD 0.00 but never negative.
- Business opening is valid at exactly SGD 7,000.00.
- Business outgoing completion is valid when projected balance is exactly SGD 7,000.00 and fails at SGD 6,999.99.

Validation layers:

- Forms: understandable field and non-field errors.
- Services: authoritative business, permission, retained-minimum, and atomicity rules.
- Models/database: structural invariants such as uniqueness, required relationships, status choices, and non-negative balance constraints where practical for SQLite.

## Atomicity and SQLite Strategy

Use `transaction.atomic()` for:

- Business registration plus account, membership, opening transaction, and access audit events;
- invitation acceptance plus membership and audit events;
- membership promotion/removal plus audit events;
- deposits;
- Personal withdrawals;
- Personal transfers;
- approved Business withdrawals;
- approved Business transfers;
- FAILED approval transitions;
- cancellation transitions where request status and audit-facing data change together.

Before final financial completion, services re-read affected account rows and revalidate balances and retained-minimum rules. Multiple PENDING Business requests do not reserve funds; each approval uses current balance at approval time.

SQLite is acceptable for this local learning MVP, but it is not production-grade for high-concurrency financial workflows. Production concurrency, stronger locking, and migration to another database are explicitly outside the MVP.

## Forms and Server-Rendered Interaction Plan

Public/onboarding forms:

- account-type selection;
- Personal registration;
- Business Account registration;
- sign-in;
- invitation-specific Business registration;
- invitation acceptance.

Personal forms:

- deposit;
- withdrawal with confirmation;
- transfer recipient type, identifier, amount, safe confirmation, final submission;
- transaction filters.

Business financial forms:

- Business Account context selection;
- deposit;
- withdrawal request review/submission;
- transfer request review/submission;
- approval, rejection, cancellation;
- approval and transaction filters.

Business membership forms:

- invite user by email and role;
- accept invitation;
- promote MEMBER;
- remove MEMBER;
- remove AUTHORISER with last-authoriser protection;
- access audit filters.

All core workflows use Django forms and server-rendered review/confirmation pages. JavaScript may be optional progressive enhancement only and is not required.

## Page, Route, Navigation, and Permission Plan

Contracts/page flows are documented in [contracts/server-rendered-flows.md](./contracts/server-rendered-flows.md).

Public pages:

- account-type selection;
- Personal registration;
- Business Account registration;
- sign-in;
- invitation registration/acceptance entry.

Personal navigation:

- Dashboard;
- Personal Account;
- Deposit;
- Withdraw;
- Transfer;
- Transactions;
- Sign Out.

Business navigation:

- Business Dashboard;
- company selector when multiple active memberships exist;
- Deposit;
- Request Withdrawal;
- Request Transfer;
- Approvals;
- Members;
- Access Audit;
- Transactions;
- Invitations where relevant;
- Sign Out.

Every Business view/action checks active membership. AUTHORISER-only actions check the selected Business Account membership role server-side.

## Midnight Ledger UI Plan

Use custom CSS only:

- midnight-navy or charcoal shell;
- soft off-white/grey content surfaces;
- mint/teal/emerald primary actions and positive treatments;
- amber PENDING invitation/request treatment;
- rounded cards, restrained borders/shadows, strong hierarchy;
- readable status badges with labels/icons, not colour alone.

Registration starts with two polished paths:

- Personal Account: individual banking, phone-number transfer receipt, no opening deposit, starts SGD 0.00.
- Business Account: company banking, UEN transfer receipt, at least SGD 7,000.00 opening funds, invited team access, AUTHORISER approval controls.

Business Dashboard shows selected company, UEN, balance, retained-minimum reminder, current role, PENDING count, role-aware actions, recent financial activity, and recent approval activity. Multi-membership users get a prominent context selector.

The three audit views use distinct presentation:

- Transactions: completed money movement.
- Approvals: outgoing Business request lifecycle.
- Access Audit: invitations and membership governance.

Accessibility requirements: visible labels, field errors, keyboard-operable controls, focus indicators, strong contrast, status meaning not colour-only, consistent SGD formatting, confirmation before financial and membership-changing actions, and no normal-use horizontal scrolling at narrower widths.

## Security and Authorisation Plan

- Unique email login through custom user model.
- Django password hashing only; no plaintext passwords in UI, histories, recipient confirmation, or errors.
- Login required for all banking pages/actions.
- Personal owner-only checks on Personal data and operations.
- Business active-membership checks on every Business page/action.
- AUTHORISER-only checks for invitation issuance, role assignment, promotion, removal, approval, and rejection.
- Cancellation checks: MEMBER can cancel own PENDING request; AUTHORISER can cancel any PENDING request.
- Removed memberships immediately fail active-membership checks.
- Final AUTHORISER removal prevented in service layer and view permissions.
- CSRF protection on all state-changing forms.
- Safe recipient confirmation uses display name/account type/masked identifier and avoids exposing credentials or sensitive email details.
- `.env`, local secret files, SQLite DB files, virtual environments, Python caches, and generated local static output are ignored.
- Local-only learning MVP disclaimer appears in quickstart.

## Testing Strategy

Use Django tests mapped to `TEST-001` through `TEST-055`:

- separate identity/authentication tests;
- Personal Account creation and money tests;
- Business Account creation and opening-deposit/audit tests;
- membership invitation and acceptance tests;
- membership administration and final-AUTHORISER tests;
- money validation and retained-minimum boundary tests;
- deposit tests;
- Personal transfer tests;
- Business request tests;
- approval/rejection/cancellation tests;
- multiple PENDING and no-reservation tests;
- transaction, approval, and access audit history separation tests;
- security/access-control tests;
- view-level UI acceptance tests for navigation, forms, states, accessibility hooks, and responsive structure where practical.

Detailed requirement-to-test mapping is in [traceability.md](./traceability.md).

## Existing Implementation Refactoring Impact

The repository may contain code, tests, migrations, or docs based on the superseded one-login/Personal-authoriser model. Implementation must treat those as obsolete where they conflict with v2.0.0.

Likely affected areas:

- user model or account ownership assumptions that allow one login to own both Personal and Business Accounts;
- Business Account fields referencing an authorised Personal Account;
- Business creation forms/views requiring a Personal Account prerequisite;
- approval permissions based on a linked Personal Account;
- transfer restrictions based on same-user Personal-to-Business ownership;
- dashboards/navigation that show both Personal and Business functionality for one login;
- transaction/history filtering based on user ownership rather than Personal ownership or Business active membership;
- tests and task completion markers from the superseded model;
- migrations and local SQLite schema/data generated for the previous design.

**Recommendation for local MVP implementation**: Because this is a local learning MVP and v2.0.0 fundamentally changes identity, account, and membership schema, the safest implementation path is to replace superseded migrations for the feature branch and reset the local SQLite database before continuing. If any user data must be preserved later, a forward migration strategy would need a separate explicit plan; preservation is outside this local MVP planning scope.

Do not reset the database or rewrite code during planning. `/speckit.tasks` must regenerate tasks against this v2.0.0 plan before implementation resumes.

## Local Deployment Plan

`quickstart.md` documents:

- Python virtual environment setup on macOS;
- installing Django and Waitress;
- environment variable setup for Django secret key;
- migration setup and local reset guidance for superseded development DBs;
- test execution;
- local static-file handling;
- Waitress launch;
- browser access;
- disclaimer that this is not a real or public banking system.

## Scope Exclusions

Out of MVP:

- shared Business login credentials;
- one login accessing both Personal and Business contexts;
- real email delivery;
- external UEN registry verification;
- phone OTP verification;
- real bank/payment integration;
- non-SGD currencies;
- cards, interest, loans, overdraft products, scheduled/recurring payments;
- notification services;
- AUTHORISER demotion to MEMBER;
- configurable multi-authoriser approval thresholds;
- MFA;
- REST APIs;
- frontend frameworks;
- cloud or public production deployment.

## Phase Outputs

- [research.md](./research.md)
- [data-model.md](./data-model.md)
- [contracts/server-rendered-flows.md](./contracts/server-rendered-flows.md)
- [quickstart.md](./quickstart.md)
- [traceability.md](./traceability.md)

## Complexity Tracking

No constitution violations require justification.
