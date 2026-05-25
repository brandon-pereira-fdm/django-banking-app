# Implementation Plan: Banking MVP

**Branch**: `main` | **Date**: 2026-05-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-banking-mvp/spec.md`

## Summary

Build a local, server-rendered Django banking MVP for SGD Personal Accounts and
Business Accounts. The implementation will use a beginner-friendly Django
monolith with a custom email-login user model, one `users` app for identity and
one `banking` app for accounts, balances, transfers, approval workflow,
transaction history, and the Midnight Ledger interface.

The plan preserves the approved rules exactly: Personal Accounts use unique
phone numbers for receiving transfers, Business Accounts use unique UEN values,
Business outgoing withdrawals and transfers require approval, multiple PENDING
Business requests are allowed without fund reservation, and completed financial
records remain immutable and auditable.

## Technical Context

**Language/Version**: Python 3.11 or later

**Primary Dependencies**: Django, Waitress

**Storage**: SQLite3 for local persistence

**Testing**: Django built-in test framework

**Target Platform**: Local macOS browser deployment

**Project Type**: Server-rendered Django web application

**Performance Goals**: Responsive local MVP pages for a single-developer,
learning/demo environment; financial correctness and atomicity are higher
priority than throughput.

**Constraints**: No frontend framework, REST API framework, external CSS
framework, external auth, payment provider, external bank integration, queue,
cloud service, microservice, or database other than SQLite3. Core banking flows
must work without mandatory JavaScript.

**Scale/Scope**: MVP scope is limited to registration, authentication, Personal
Accounts, Business Accounts, deposits, withdrawals, transfers, Business outgoing
approvals, transaction history, approval history, automated tests,
traceability, premium custom-CSS UI, and local Waitress deployment.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Restricted MVP Technology**: PASS. Plan uses only Python 3.11+, Django,
  SQLite3, Django templates, custom CSS, and Waitress for local macOS. It does
  not add alternative databases, frontend frameworks, payment platforms,
  external bank integrations, cloud infrastructure, microservices, queues,
  WebSockets, or third-party authentication.
- **SGD-Only Money**: PASS. All balances, deposits, withdrawals, transfers, and
  opening deposits are in SGD only and display as `SGD 0.00`.
- **Precise Financial Correctness**: PASS. All calculations use Python
  `Decimal`, stored money uses Django decimal-backed fields, and floating-point
  arithmetic for money is prohibited.
- **Personal Account Rules**: PASS. Personal Accounts require no opening
  deposit, may start at SGD 0.00, have no minimum balance, may end at SGD 0.00,
  and must never become negative.
- **Business Account Rules**: PASS. Business Accounts require business display
  name, unique UEN, existing owner Personal Account, exactly one authorised
  Personal Account, and opening deposit of at least SGD 7,000.00. Completed
  outgoing withdrawals/transfers must retain at least SGD 7,000.00.
- **Business Approval Rules**: PASS. Business withdrawals and outgoing transfers
  create approval requests before completion. Business deposits and incoming
  transfers complete without approval.
- **Recipient Identifiers**: PASS. Personal recipients are resolved by unique
  Personal Account phone number. Business recipients are resolved by unique UEN.
  Sender must select recipient account type before entering the identifier.
- **Transfers and Audit IDs**: PASS. Completed transfers create one shared
  transfer operation ID plus one sender debit and one recipient credit
  completed transaction record, each with its own UUID transaction ID.
- **Immutable Completed History**: PASS. Completed transaction records are not
  editable or deletable through ordinary user-facing flows.
- **Atomic Financial Operations**: PASS. All balance changes and completed
  transaction creation happen inside Django database transactions.
- **Security and Secrets**: PASS. Django authentication/password hashing,
  CSRF, server-side permission checks, environment-based secrets, and ignored
  local secret/database files are planned.
- **Mandatory Automated Testing**: PASS. Testing strategy maps to all mandatory
  banking behaviours, including UEN lookup, multiple PENDING requests,
  no-reservation rules, approval failure, UUIDs, transfer IDs, and rollback.
- **Traceability**: PASS. Requirement IDs remain traceable from constitution and
  specification to planned components and tests through [traceability.md](./traceability.md).

**Violations**: None. Any future implementation decision that adds an
unapproved database, frontend framework, payment integration, external auth,
queue, cloud service, or product behaviour must be treated as a constitutional
violation requiring amendment.

## Project Structure

### Documentation (this feature)

```text
specs/001-banking-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── traceability.md
├── contracts/
│   └── server-rendered-flows.md
└── checklists/
    └── requirements-quality.md
```

### Source Code (planned)

```text
manage.py
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
├── tests.py
├── urls.py
└── views.py
banking/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── services.py
├── tests.py
├── urls.py
└── views.py
templates/
├── base.html
├── public_base.html
├── users/
├── banking/
└── components/
static/
└── css/
    └── app.css
```

**Structure Decision**: Use a single Django project package, one `users` app,
and one `banking` app. This keeps the MVP understandable while maintaining a
clear boundary between identity and banking rules. Business rules live in
`banking.services`, not only in forms or views.

## Architecture Direction

### Django Project Package

Responsibilities:

- Environment-based settings, including `SECRET_KEY`, `DEBUG`, allowed hosts,
  static files, SQLite path, templates, CSRF, and authentication settings.
- Top-level URL routing to `users` and `banking`.
- WSGI configuration and a small Waitress entry-point module for local launch.
- Local security defaults suitable for an MVP: CSRF enabled, secure password
  hashing through Django, no committed secrets, and clear local-only warnings.

### `users` App

Responsibilities:

- Custom user model from project start.
- Unique email as login identifier.
- Username as user-facing display name.
- Registration, sign-in, sign-out, and authentication views/forms.
- Password management exclusively through Django authentication and hashing.

Planned design:

- Custom user model extends Django authentication base classes.
- `email` is unique and normalised.
- `USERNAME_FIELD = "email"`.
- `username` remains required for display but is not the login credential.

### `banking` App

Responsibilities:

- Account records and account ownership.
- Personal phone recipient identifiers.
- Business UEN recipient identifiers and business display name.
- Business authorised Personal Account relationship.
- Money validation, balances, deposits, withdrawals, transfers, approvals,
  completed transactions, transaction history, approval history, dashboard,
  and financial-operation pages.

Planning decision:

- Keep Personal and Business banking behaviour in one app for the MVP.
- Use a service layer for authoritative rules and atomic operations.
- Use Django forms for user input validation and Django views/templates for
  server-rendered multi-step flows.

## Data Model Summary

Detailed design is in [data-model.md](./data-model.md).

Planned entities:

- `CustomUser`
- `BankAccount`
- `CompletedTransaction`
- `TransferOperation`
- `ApprovalRequest`

`BankAccount` will use one model with an account-type discriminator and
type-specific nullable fields guarded by validation and database constraints.
This is the simplest clear design for an MVP because balances, ownership,
history, and transfers are common across both account types, while Personal and
Business fields are few and explicitly constrained.

Money fields use `DecimalField(max_digits=12, decimal_places=2)`, supporting up
to SGD 9,999,999,999.99. This is ample for a local MVP without implying
production-scale banking limits.

## Financial Service Layer Plan

The `banking.services` module will expose transaction-safe service functions.
Forms and views may validate user input for feedback, but services remain the
authoritative enforcement point for money movement, ownership, approval, and
audit rules.

Planned services:

- `create_personal_account(user, phone_number)`
- `create_business_account(user, business_display_name, uen, opening_deposit)`
- `deposit(account, amount, actor)`
- `withdraw_personal(account, amount, actor)`
- `request_business_withdrawal(business_account, amount, actor)`
- `resolve_transfer_recipient(recipient_type, identifier)`
- `preview_transfer(sender_account, recipient_type, identifier, amount, actor)`
- `transfer_from_personal(sender_account, recipient, amount, actor)`
- `request_business_transfer(sender_account, recipient, amount, actor)`
- `approve_request(approval_request, actor)`
- `reject_request(approval_request, actor)`
- `cancel_request(approval_request, actor)`

Service responsibilities:

- Normalise and validate money using `Decimal`.
- Lock or re-read affected account records inside atomic blocks.
- Validate ownership and authorisation server-side.
- Reject invalid amount, unknown recipient, mismatched identifier, self-transfer,
  same-user cross-account transfer, insufficient Personal funds, Business
  retained-minimum breach, and unauthorised approval attempts.
- Create completed transaction records only after successful balance movement.
- For Business approval, move `PENDING` directly to `COMPLETED` on successful
  approval and completion, or to `FAILED` when approval-time validation fails.

## Atomicity and SQLite Strategy

Use `transaction.atomic()` for:

- Business Account creation and opening-deposit transaction.
- Deposits.
- Personal withdrawals.
- Personal outgoing transfers.
- Approval completion for Business withdrawals.
- Approval completion for Business transfers.
- Approval failure outcomes that mark requests `FAILED` without money movement.

Balance and record strategy:

- Re-read sender and recipient accounts inside the atomic block immediately
  before completed movement.
- Revalidate current balance and retained-minimum rules at completion time.
- Update balances and create completed transaction records in the same atomic
  block.
- For transfers, create the `TransferOperation`, sender debit record, recipient
  credit record, and balance updates together.
- Multiple PENDING Business requests do not reserve funds. Each approval attempt
  revalidates the current Business Account balance, so a later request may fail
  after an earlier one completes.

SQLite suitability:

- SQLite is acceptable for this local macOS MVP and Django test suite.
- SQLite has concurrency and write-locking limitations and is not treated as a
  production-grade financial database.
- Migrating to PostgreSQL, MySQL, or hosted storage is outside the MVP and would
  require a constitutional amendment.

## Forms and Server-Rendered Interaction Plan

Use Django forms for:

- Registration.
- Sign-in.
- Personal Account creation.
- Business Account creation.
- Deposit.
- Personal withdrawal.
- Personal transfer.
- Business withdrawal request.
- Business outgoing transfer request.
- Approval decision.
- Pending-request cancellation.
- Transaction filtering.
- Approval-status filtering.

Transfer flow without mandatory JavaScript:

1. Sender selects source account, recipient account type, identifier, and SGD
   amount.
2. Server validates identifier format and resolves the recipient by phone/UEN.
3. Server renders safe recipient confirmation with username or business display
   name, account type, masked identifier where appropriate, amount, approval
   requirement, and retained-minimum notice where applicable.
4. Sender confirms.
5. Personal sender completes immediately if valid. Business sender creates a
   PENDING approval request.

## Page, Route, and Navigation Plan

Detailed page-flow contracts are in [contracts/server-rendered-flows.md](./contracts/server-rendered-flows.md).

Planned pages:

- Registration.
- Sign-In.
- Dashboard.
- Personal Account setup and detail.
- Business Account setup and detail.
- Deposit flow.
- Withdrawal flow.
- Transfer flow.
- Approvals list and detail.
- Transactions history.

Planned URL shape:

```text
/register/
/login/
/logout/
/dashboard/
/accounts/personal/setup/
/accounts/personal/
/accounts/business/setup/
/accounts/business/
/deposit/
/withdraw/
/transfer/
/transfer/confirm/
/approvals/
/approvals/<request_id>/
/transactions/
```

## Premium UI Plan: Midnight Ledger

Use Django templates and custom CSS only.

Visual direction:

- Midnight navy or charcoal app shell.
- Off-white or soft-grey content cards.
- Mint, teal, or emerald primary action accents.
- Amber treatment for PENDING approvals.
- High-contrast typography.
- Generous whitespace.
- Rounded cards with restrained borders and shadows.
- Text labels and icons in addition to colour for statuses.

Layout:

- Public authentication layout for registration/sign-in.
- Authenticated app shell with desktop sidebar.
- Compact navigation adaptation for narrow widths.
- Top bar with signed-in username and sign-out.
- Reusable template fragments for account cards, transaction rows, status
  badges, field errors, confirmation summaries, empty states, and alerts.

UX requirements:

- Strong dashboard hierarchy.
- Clear Personal versus Business distinction.
- Personal Account card shows receiving phone number.
- Business Account card shows UEN and retained-minimum notice.
- Transfer flow shows Personal/Business recipient selector.
- Approval review shows current balance, requested amount, projected balance,
  and retained-minimum result.
- Success pages include UUID transaction IDs or transfer operation IDs where
  applicable.
- Visible labels, keyboard-operable flows, focus indicators, accessible
  contrast, no reliance on colour alone, and no normal-use horizontal scrolling
  at narrower widths.

## Authentication, Authorisation, and Security Plan

Security controls:

- Email-based login using the custom user model.
- Django password hashing only; plaintext passwords are never stored or shown.
- Authentication required for account, money, transaction, and approval pages.
- Ownership checks on every account and financial operation.
- Approval permission checks against the Business Account's authorised Personal
  Account.
- CSRF protection on all modifying forms.
- Safe recipient confirmation without email or sensitive account details.
- Clear validation errors without leaking sensitive information.
- `SECRET_KEY` loaded from environment.
- `.env`, local secret files, SQLite database files, virtual environments, and
  generated local artifacts excluded from Git.
- Local-only deployment disclaimer in quickstart.

Security mapping:

- `SEC-001`: login required middleware/decorators and view checks.
- `SEC-002`: ownership and authorised-approver service checks.
- `SEC-003`: Django password hashing and no password display.
- `SEC-004`: server-side financial and approval enforcement.
- `SEC-005`: generic auth errors and safe validation messages.
- `SEC-006`: masked recipient confirmation.
- `SEC-007`: environment-loaded secrets and ignored local config.

## Testing Strategy

Use Django's built-in test framework. Tests will be grouped into:

- `users` tests for registration, duplicate email, password hashing, sign-in,
  sign-out, and unauthenticated access.
- `banking` model/service tests for account invariants, money validation,
  Decimal handling, deposits, withdrawals, transfers, approvals, atomicity, and
  transaction records.
- `banking` view tests for access control, form validation, safe recipient
  confirmation, histories, filters, and Midnight Ledger UI expectations that are
  measurable at rendered-response level.

Mandatory coverage includes `TEST-001` through `TEST-053` from the
specification. Detailed mapping is in [traceability.md](./traceability.md).

## Local macOS Deployment Plan

Quickstart is in [quickstart.md](./quickstart.md).

Deployment plan:

- Create a Python virtual environment.
- Install minimal dependencies: Django and Waitress.
- Set environment variables such as `DJANGO_SECRET_KEY` and `DJANGO_DEBUG`.
- Run migrations against local SQLite.
- Run Django tests.
- Collect static files if using a local static root.
- Launch with Waitress against the Django WSGI application.
- Open the local browser URL.
- Display explicit warning that the app is a local learning MVP, not real
  banking or public production software.

## Post-Design Constitution Check

- **Technology scope**: PASS. No unapproved dependency or infrastructure is
  introduced.
- **Financial correctness**: PASS. Decimal handling, form validation, service
  validation, and database constraints are planned.
- **Account and transfer identity**: PASS. Personal phone and Business UEN
  recipient identities are separate and unique.
- **Business approval lifecycle**: PASS. Only PENDING, COMPLETED, REJECTED,
  CANCELLED, and FAILED are persisted; no APPROVED status is planned.
- **Atomicity and auditability**: PASS. Balance changes and completed records
  are committed together; workflow records remain separate from completed
  financial history.
- **Security and tests**: PASS. Server-side enforcement, secret handling, and
  full mandatory test mapping are planned.

## Complexity Tracking

No constitution violations or complexity exceptions are planned.
