<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- III. Account Types and User Identity -> III. Account Types and Recipient Identity
- V. Business Account Opening and Balance Rules -> V. Business Account Opening and Balance Rules
- VII. Transfers and Linked Transaction Records -> VII. Transfers and Linked Transaction Records
- VIII. Business Account Authorisation -> VIII. Business Account Authorisation
- XI. Automated Testing and Quality Gates -> XI. Automated Testing and Quality Gates
- XIII. Governance and SDD Compliance -> XIII. Governance and SDD Compliance
Added sections:
- Amendment 1.1.0 Recipient and Approval Governance
Removed sections:
- None
Templates requiring updates:
- [x] .specify/templates/plan-template.md
- [x] .specify/templates/spec-template.md
- [x] .specify/templates/tasks-template.md
- [x] .specify/templates/checklist-template.md
Follow-up TODOs:
- Current feature specification and checklist must be updated to replace
  phone-only Business Account transfers with UEN-based Business Account
  transfers before planning.
-->
# BankApp Constitution

## Core Principles

### I. MVP Technology and Scope
The MVP MUST use Python 3.11 or later, Django, SQLite3, Django templates, and
Waitress for simple local macOS deployment. All monetary values and transactions
MUST be restricted to Singapore Dollars (SGD) only.

The MVP MUST NOT introduce alternative databases, frontend frameworks, payment
gateways, external bank integrations, cloud infrastructure, microservices,
message queues, or third-party authentication systems.

The MVP scope MUST remain limited to user registration, authentication, personal
accounts, business accounts, deposits, withdrawals, transfers, transaction
history, business-account outgoing-transaction approval, automated tests,
traceability, and local deployment.

Rationale: A narrow local-first stack keeps the SDD MVP auditable, testable, and
focused on proving banking rules before architecture expansion.

### II. Financial Correctness and Money Validation
All balances and monetary operations MUST use precise decimal arithmetic. The
application MUST never use floating-point arithmetic for money.

Deposits, withdrawals, opening deposits, and transfers MUST reject zero,
negative, malformed, non-numeric, or invalid-precision values. Any operation
that would result in a negative account balance MUST be prevented. Rejected or
failed financial operations MUST NOT modify balances and MUST NOT be recorded as
completed transactions.

Rationale: Banking correctness depends on exact SGD arithmetic, strict amount
validation, and unchanged state after failed operations.

### III. Account Types and Recipient Identity
The MVP MUST support exactly two account types: Personal Account and Business
Account. A user MAY have one Personal Account and one Business Account.

A registered user MUST have a unique email address, password, and user-selected
username. Passwords MUST be stored using Django authentication and password
hashing facilities and MUST never be stored in plaintext.

A Personal Account MUST have an owner, balance, and one unique registered phone
number used as its transfer recipient identifier. A Business Account MUST have
an owner, balance, one unique company UEN used as its transfer recipient
identifier, exactly one authorised Personal Account, and a business display name
to be defined more fully in the feature specification. A company UEN MUST be
unique across all Business Accounts.

Rationale: Personal recipients and business recipients need distinct identifiers
so incoming transfers are unambiguous when a user owns both account types.

### IV. Personal Account Rules
A Personal Account MUST NOT require an opening deposit and MAY begin with a
balance of SGD 0.00. A Personal Account has no minimum-balance requirement.

A Personal Account MAY withdraw or transfer funds only when the amount is valid,
greater than zero, and the operation does not cause the balance to become
negative. Successful Personal Account deposits, withdrawals, and outgoing or
incoming transfers MUST be auditable through transaction records.

Rationale: Personal accounts are ordinary user accounts with no minimum-balance
constraint, but they still require exact validation and auditability.

### V. Business Account Opening and Balance Rules
A user MUST already have a Personal Account before opening a Business Account.
A new Business Account MUST require an opening deposit of at least SGD 7,000.00
before it can be created. A Business Account cannot be created unless a unique
company UEN is supplied. The UEN MUST be recorded as the Business Account's
incoming-transfer identifier and MUST NOT be duplicated across Business
Accounts.

The user's own Personal Account is the single authorised Personal Account for
their Business Account in the MVP. A Business Account MUST maintain a minimum
balance of SGD 7,000.00 after every completed outgoing transaction. A withdrawal
or outgoing transfer from a Business Account MUST be rejected when it would cause
the balance to fall below SGD 7,000.00. Deposits into a Business Account and
incoming transfers received by a Business Account do not require approval and
MAY increase its balance.

Rationale: Business accounts have explicit company identity, opening, approval,
and ongoing balance obligations that differ from personal accounts.

### VI. Deposits and Withdrawals
A valid positive deposit MAY be credited to either a Personal Account or a
Business Account. Every successful deposit MUST create an immutable deposit
transaction record with a UUID transaction ID.

A Personal Account withdrawal MAY complete without approval when the amount is
valid and the account has sufficient balance to avoid a negative balance. A
Business Account withdrawal is an outgoing business transaction and MUST NOT
complete until it is approved by its authorised Personal Account. Every
successfully completed withdrawal MUST create an immutable withdrawal
transaction record with a UUID transaction ID.

Rationale: Deposits are immediate positive credits, while withdrawals require
account-type-specific balance and authorization enforcement.

### VII. Transfers and Linked Transaction Records
Transfers to a Personal Account MUST use the recipient Personal Account's unique
registered phone number. Transfers to a Business Account MUST use the recipient
Business Account's unique company UEN. A Business Account MUST NOT use a phone
number as its incoming transfer identifier.

The transfer flow MUST require the sender to identify the recipient account
type. For a Personal Account recipient, the sender MUST enter a phone number.
For a Business Account recipient, the sender MUST enter a UEN. Before
confirmation, the system MUST display safe recipient confirmation details such
as username or business display name and account type without exposing sensitive
information.

Transfers MUST reject zero, negative, malformed, or invalid-precision amounts;
unknown or mismatched recipient identifiers; amounts that would cause a Personal
Account sender to become negative; amounts that would cause a Business Account
sender to fall below SGD 7,000.00; and outgoing Business Account transfers that
have not received required approval. Self-transfers remain excluded from the
MVP. Transfers between a user's own Personal Account and Business Account remain
excluded from the MVP unless explicitly added by a future amendment.

Every successfully completed transfer MUST create one unique transfer operation
ID, one immutable sender debit transaction record, and one immutable recipient
credit transaction record. The sender debit record and recipient credit record
MUST each have their own UUID transaction ID and MUST reference the same
transfer operation ID.

Sender debiting, recipient crediting, and transaction-record creation MUST be
atomic: either all changes succeed or none occur.

Rationale: Personal and business recipients require different identifiers, while
completed transfer records must remain linked, auditable, and atomic.

### VIII. Business Account Authorisation
Each Business Account MUST be associated with exactly one authorised Personal
Account. A Business Account MUST NOT complete an outgoing transaction unless its
authorised Personal Account approves it.

Approval is required for withdrawals from a Business Account and transfers sent
from a Business Account. Approval is not required for deposits into a Business
Account or incoming transfers received by a Business Account.

The approval workflow statuses are:
- PENDING: an outgoing Business Account withdrawal or transfer request has been
  submitted but not resolved.
- COMPLETED: the authorised Personal Account approved the request, all financial
  validations passed, and the money movement completed.
- REJECTED: the authorised Personal Account declined the request and no money
  moved.
- CANCELLED: the Business Account owner cancelled a PENDING request and no money
  moved.
- FAILED: the authorised Personal Account attempted approval, but completion
  failed because current validation rules were not satisfied and no money moved.

There is no separately stored APPROVED status in the MVP. Approval is an action
taken on a PENDING request. If approval succeeds and funds move, the request
becomes COMPLETED. If approval is attempted but completion validation fails, the
request becomes FAILED. Only PENDING requests may be approved, rejected, or
cancelled. COMPLETED, REJECTED, CANCELLED, and FAILED are final statuses.

A Business Account MAY have multiple PENDING outgoing transaction requests at
the same time. PENDING requests MUST NOT reserve funds and MUST NOT alter
displayed account balances. Each PENDING request MUST be independently
revalidated at the time approval is attempted. Completing one request MAY cause
a later PENDING request to fail approval if the Business Account would no longer
retain SGD 7,000.00 after completion.

Rationale: Business outgoing funds require explicit personal-account governance,
current-state revalidation, and an audit-friendly lifecycle without a separate
persisted APPROVED status.

### IX. Transaction Auditability and Immutability
Every successful deposit and completed withdrawal MUST have an immutable
transaction record with a UUID transaction ID. Every successfully completed
transfer MUST produce two immutable linked transaction records joined by one
transfer operation ID. Completed transaction records MUST NOT be editable through
application logic.

Completed transaction records MUST include at minimum a UUID transaction ID,
transaction type, amount in SGD, associated account, completion timestamp,
transaction status, and transfer operation ID where applicable.

PENDING, REJECTED, CANCELLED, or FAILED Business Account approval requests MAY
be retained for workflow auditability, but they MUST be clearly distinguished
from completed balance-changing transactions.

Rationale: Completed financial history must be complete, immutable, and clearly
separated from pending or failed workflow records.

### X. Security and Secrets Management
Secrets and sensitive configuration MUST NOT be committed to GitHub. Django
secret keys, plaintext passwords, tokens, private credentials, environment files
containing secrets, and local SQLite database files MUST NOT be committed.

Secret configuration MUST be stored in environment variables or ignored local
files. An appropriate `.gitignore` MUST exist before creating local secrets,
SQLite database files, or Python virtual environments.

Authentication, financial validation, balance rules, account ownership, and
Business Account approvals MUST be enforced server-side rather than relying only
on the user interface.

Rationale: Local MVP deployment still requires credential hygiene and server-side
control of all security and banking invariants.

### XI. Automated Testing and Quality Gates
Automated tests are mandatory for core banking behaviour. A feature with failing
mandatory tests MUST NOT be treated as complete.

Mandatory tests MUST cover successful Personal Account creation without an
opening deposit; Personal Account beginning at SGD 0.00; successful Business
Account creation with an opening deposit of SGD 7,000.00 or more, unique UEN,
and own authorised Personal Account; rejection of Business Account opening
deposits below SGD 7,000.00; duplicate email rejection; duplicate phone-number
rejection for Personal Accounts; duplicate UEN rejection for Business Accounts;
secure password hashing expectations; successful positive deposits for both
account types; rejection of zero and negative deposits; successful Personal
Account withdrawal where sufficient balance exists; rejection of Personal
Account withdrawal that would cause a negative balance; Personal Account
transfer lookup by unique phone number; Business Account transfer lookup by
unique UEN; rejection of a transfer where the selected recipient account type
and identifier do not match; safe recipient confirmation behavior; successful
Personal Account outgoing transfer where sufficient balance exists; rejection of
Personal Account transfer that would cause a negative balance; successful
permitted Business Account withdrawal after approval; rejection or non-completion
of unapproved Business Account withdrawals; rejection of Business Account
withdrawals that breach the SGD 7,000.00 minimum; rejection of unknown recipient
identifiers; rejection of zero and negative transfers; rejection or
non-completion of unapproved outgoing Business Account transfers; rejection of
outgoing Business Account transfers that breach the SGD 7,000.00 minimum;
incoming Business Account deposits and transfers proceeding without approval;
multiple PENDING Business requests; no fund reservation while requests are
PENDING; a PENDING request becoming FAILED when another completed request causes
the retained-minimum rule to fail at approval time; absence of a separate
APPROVED persisted status; generation of UUID transaction IDs; generation of one
transfer operation ID shared by linked sender debit and recipient credit
records; and atomic rollback when a financial operation fails.

Rationale: The MVP cannot claim banking correctness unless the required account,
recipient identity, money, authorization, transaction, and rollback behaviours
are tested.

### XII. Requirements Traceability
Every business rule MUST remain traceable from constitution to specification,
acceptance criteria, technical plan, implementation task, code component, and
automated test.

Specifications and plans MUST use identifiers such as `FR-###` for functional
requirements, `BR-###` for business rules, `SEC-###` for security requirements,
`NFR-###` for non-functional requirements, and `TEST-###` for mandatory tests.
Test names or associated traceability documentation MUST reference the banking
rule or requirement being verified.

A feature MUST NOT be considered complete unless its applicable business rules
have implemented and passing tests.

Rationale: SDD requires every rule to stay visible from intent through verified
implementation.

### XIII. Governance and SDD Compliance
This constitution is the highest-authority project document for non-negotiable
banking and engineering rules. Every later specification and technical plan MUST
include a Constitution Check.

A constitutional amendment is required for any change to the MVP technology
stack, SGD-only currency restriction, account types, Personal Account
no-minimum-balance rule, Business Account opening-deposit or minimum-balance
rule, transfer recipient identifiers, transfer recording, Business Account
authorisation lifecycle, security obligations, testing obligations, traceability
obligations, or MVP scope.

Semantic versioning MUST be applied as follows: MAJOR for removing or
fundamentally redefining a core principle or banking invariant; MINOR for adding
a mandatory principle or materially expanding scope; PATCH for clarifications
that do not change required behaviour.

Rationale: SDD artifacts must remain subordinate to the constitution, and
changes to banking invariants must be intentional, reviewed, and versioned.

## Amendment 1.1.0 Recipient and Approval Governance

This amendment replaces phone-only transfer recipient identification with
account-type-specific recipient identification. Personal Account incoming
transfers use unique phone numbers. Business Account incoming transfers use
unique company UENs. Sender transfer flows MUST require the recipient account
type before collecting the matching identifier.

This amendment resolves approval lifecycle governance by removing any separate
persisted APPROVED status from the MVP. Approval is an action on a PENDING
request. A successful approval produces COMPLETED; an attempted approval that
fails current validation produces FAILED.

This amendment also permits multiple PENDING Business Account outgoing requests
at the same time, with no fund reservation and independent approval-time
revalidation for each request.

## Specification-Driven Development Quality Gates

Every feature specification MUST include a Constitution Check and MUST identify
all applicable `BR-###`, `FR-###`, `SEC-###`, `NFR-###`, and `TEST-###`
identifiers. Each business rule MUST have acceptance criteria before planning
begins.

Every technical plan MUST prove alignment with the MVP stack, SGD-only money
handling, account-type rules, personal and business recipient identifiers,
personal and business balance rules, deposit and withdrawal rules, transfer
atomicity, business authorization lifecycle, transaction immutability, secrets
management, mandatory tests, traceability, and local deployment.

Every task list MUST include tests before implementation tasks for applicable
banking rules. Tasks MUST preserve requirement and business-rule identifiers and
name the code component and test path that will satisfy each rule.

Completion requires passing mandatory automated tests and updated traceability
from constitution rule to specification, acceptance criteria, plan, task, code
component, and test.

## Governance

This constitution supersedes conflicting repository conventions, templates,
plans, specifications, tasks, and implementation choices. When conflict exists,
the constitution wins until amended.

Amendments MUST be proposed as explicit documentation changes that state the
motivation, affected rules, migration impact, version impact, and required
template updates. An amendment is approved only after the constitution and
dependent Spec Kit templates are updated together.

Compliance review is mandatory during specification and planning. A feature may
not proceed from specification to planning, from planning to tasks, or from tasks
to complete implementation while any applicable constitutional gate is failing.

Versioning follows semantic versioning:
- MAJOR: removing or fundamentally redefining a core principle or banking
  invariant.
- MINOR: adding a mandatory principle or materially expanding scope.
- PATCH: clarifications that do not change required behaviour.

**Version**: 1.1.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-25
