# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11 or NEEDS CLARIFICATION]

**Primary Dependencies**: [Django, Waitress or NEEDS CLARIFICATION]

**Storage**: [SQLite3 or NEEDS CLARIFICATION]

**Testing**: [Django test framework or NEEDS CLARIFICATION]

**Target Platform**: [local macOS deployment or NEEDS CLARIFICATION]

**Project Type**: [Django web application or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Restricted MVP Technology**: Plan uses only Python, Django, SQLite3,
  Django templates, and Waitress on local macOS. Plan restricts money to SGD
  and does not add alternative databases, frontend frameworks, payment gateways,
  external bank integrations, cloud infrastructure, microservices, message
  queues, or third-party authentication.
- **MVP Scope**: Plan stays within registration, authentication, personal
  accounts, business accounts, deposits, withdrawals, transfers, transaction
  history, business-account outgoing approval, automated tests, traceability,
  and local deployment.
- **Financial Correctness**: Plan uses Decimal arithmetic only; rejects zero,
  negative, malformed, non-numeric, and invalid-precision money values; prevents
  negative balances; and leaves no balance or completed-transaction changes for
  failed operations.
- **Account Types and Identity**: Plan supports exactly Personal Account and
  Business Account, allows one user to have both, requires unique user email,
  password, user-selected username, Django password hashing, unique Personal
  Account phone number, unique Business Account UEN, and business display name.
- **Personal Account Rules**: Plan allows Personal Accounts to open at SGD 0.00
  with no minimum balance and prevents withdrawals/transfers that would make the
  balance negative.
- **Business Account Rules**: Plan requires at least SGD 7,000.00 opening
  deposit, unique UEN, and own authorised Personal Account before creation;
  enforces SGD 7,000.00 after outgoing transactions; and allows incoming
  deposits/transfers without approval.
- **Deposits, Withdrawals, and Transfers**: Plan creates UUID transaction IDs
  for successful deposits/withdrawals, uses Personal Account phone numbers and
  Business Account UENs for recipient lookup, requires recipient account type
  selection, rejects mismatched identifiers and self/own-account transfers, and
  creates linked sender debit and recipient credit records sharing one transfer
  operation ID.
- **Business Authorisation**: Plan associates each Business Account with exactly
  one authorised Personal Account; defines PENDING, COMPLETED, REJECTED,
  CANCELLED, and FAILED states; excludes a persisted APPROVED state; allows
  multiple PENDING requests; and revalidates each request independently at
  approval time with no fund reservation.
- **Auditability and Atomicity**: Plan makes completed transaction records
  immutable, distinguishes approval workflow records from completed financial
  transactions, and wraps balance plus transaction-record changes atomically.
- **Security and Secrets**: Plan keeps Django secret keys, plaintext passwords,
  tokens, private credentials, secret env files, local SQLite DBs, and virtual
  environments out of GitHub; server-side enforcement covers authentication,
  validation, balances, ownership, and approvals.
- **Automated Testing**: Plan includes all mandatory `TEST-###` cases for
  account creation, duplicates, password hashing, deposits, withdrawals,
  Personal phone lookup, Business UEN lookup, duplicate UEN rejection,
  mismatched recipient identifiers, safe recipient confirmation, transfers,
  business approvals, multiple pending requests, no fund reservation, FAILED
  revalidation outcomes, absence of persisted APPROVED status, UUIDs, linked
  transfer IDs, and rollback.
- **Traceability**: Plan preserves constitution-to-spec-to-acceptance-to-plan-
  to-task-to-code-to-test links using `BR-###`, `FR-###`, `SEC-###`, `NFR-###`,
  and `TEST-###` identifiers.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Django banking MVP
manage.py
[project]/
├── settings.py
├── urls.py
└── wsgi.py

[app]/
├── models.py
├── forms.py
├── services.py
├── views.py
├── urls.py
├── templates/
└── tests.py

templates/
└── [shared templates]

db.sqlite3
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
