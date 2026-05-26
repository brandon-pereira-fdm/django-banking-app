<!--
Sync Impact Report
Version change: 2.0.0 -> 3.0.0
Modified principles:
- III. Separate Login Identities and Account Experiences -> III. Account and Login Model
- V. Business Account and Business User Model -> V. Business Account Registration and Employee Access
- VI. Business Account Membership and Invitations -> VI. Business Employee Access Credentials
- VII. Business Account Access Audit History -> VII. Business Access State, Password Resets, and Audit History
- VIII. Deposits, Withdrawals, and Business Approval -> VIII. Business Roles, Permissions, and Approval
- X. Transaction, Approval, and Access History Separation -> X. Transaction, Approval, and Access History Separation
- XII. Automated Testing and Quality Gates -> XII. Automated Testing and Quality Gates
- XIII. Security and Secrets Management -> XIII. Security and Secrets Management
- XIV. Governance and SDD Compliance -> XIV. Governance and SDD Compliance
Added sections:
- Amendment 3.0.0 Authoriser-Provisioned Employee Access Governance
Removed sections:
- Invitation acceptance as an active MVP access model
- Multi-Business-Account membership for one Business login
- Business Account selector requirement for employee logins
Templates requiring updates:
- .specify/templates/plan-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/spec-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/tasks-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/checklist-template.md: pending by explicit user request
  to produce the amended constitution only.
Follow-up TODOs:
- Update specification, checklist, plan, data model, contracts, tasks,
  traceability, and implementation code to replace invitations and multi-account
  Business memberships with Authoriser-provisioned employee access credentials.
- Remove or refactor active invitation models, invitation forms, invitation
  services, invitation pages, invitation tests, invitation navigation, invitation
  acceptance logic, Business Account selector logic, and schema assumptions that
  conflict with provisioned employee access.
-->
# BankApp Constitution

## Core Principles

### I. MVP Technology and Scope
The MVP MUST use Python 3.11 or later, Django, SQLite3, Django templates,
custom CSS, Django built-in authentication, Django forms, Django transactions,
Django migrations, Django tests, and Waitress for simple local macOS execution.
All monetary values and transactions MUST be restricted to Singapore Dollars
(SGD) only.

The MVP MUST NOT introduce alternative databases, frontend frameworks, external
CSS frameworks, payment gateways, external bank integrations, cloud
infrastructure, microservices, message queues, WebSockets, third-party
authentication systems, OTP verification, email-delivery infrastructure, or
external UEN registry verification without constitutional amendment.

The MVP scope MUST remain limited to registration, authentication, Personal
Account access, Business Account access, Authoriser-provisioned employee access
credentials, role management, temporary-password change and reset flows,
deactivation and reactivation, deposits, withdrawals, transfers, outgoing
Business approval workflow, Transaction History, Approval History, Access Audit
History, automated tests, traceability, and local deployment.

Rationale: A narrow local-first stack keeps the SDD MVP auditable, testable, and
focused on proving banking and access-governance rules before architecture
expansion.

### II. Financial Correctness and Money Validation
All balances and monetary operations MUST use precise decimal arithmetic. The
application MUST never use floating-point arithmetic for money.

Deposits, withdrawals, opening deposits, and transfers MUST reject zero,
negative, malformed, non-numeric, non-SGD, over-capacity, or invalid-precision
values. Monetary values MUST support no more than two decimal places. Any
operation that would result in a negative account balance MUST be prevented.
Rejected or failed financial operations MUST NOT modify balances and MUST NOT
be recorded as completed financial transactions.

Rationale: Banking correctness depends on exact SGD arithmetic, strict amount
validation, and unchanged state after failed operations.

### III. Account and Login Model
The application supports exactly two bank-account products: Personal Account
and Business Account.

A Personal Account is an individual bank account with its own Personal login
credentials. A Business Account is a company-owned bank account with one or
more individual employee access logins. An employee access login is not itself
a Personal Account and is not itself a separate Business Account.

A Personal Account login MUST access Personal Account functionality only. A
Business employee access login MUST access Business Account functionality only.
A Business employee access login MUST NOT access Personal Account functionality.
A Personal Account login MUST NOT access Business Account functionality.

A Business employee access login belongs to exactly one Business Account. The
same Business employee login MUST NOT access multiple Business Accounts. If an
individual works with more than one company Business Account in this MVP,
separate employee access credentials MUST be created for each Business Account
using different unique email addresses.

A real individual who separately needs a Personal Account and employee access
to a Business Account MUST use separate login credentials and different unique
email addresses. Email addresses MUST remain unique login identifiers across
the whole application.

Shared Business Account credentials are prohibited. Each employee MUST have
their own assigned login identity. Passwords MUST be stored using Django
authentication and password hashing facilities and MUST never be stored in
plaintext.

Rationale: Personal banking, company ownership, and employee access are
separate accountability contexts. One login must not blur those boundaries.

### IV. Personal Account Model
Personal Account registration MUST require a user-selected username, unique
email login, securely stored password, and one unique phone number used for
receiving transfers.

A Personal Account MUST NOT require an opening deposit and MUST begin with
balance SGD 0.00 unless funds are later deposited or received. A Personal
Account has no minimum-balance requirement.

A Personal Account MAY deposit, withdraw, and make outgoing transfers only when
the amount is valid and greater than zero. A Personal Account withdrawal or
outgoing transfer MAY leave the account at SGD 0.00, but MUST NOT cause the
balance to become negative. A Personal Account receives incoming transfers
using its unique phone number.

Successful Personal Account deposits, withdrawals, and outgoing or incoming
transfers MUST be auditable through immutable completed financial transaction
records.

Rationale: Personal accounts are individual SGD accounts with no retained
minimum, but they still require exact validation, unique recipient identity, and
auditable financial movement.

### V. Business Account Registration and Employee Access
A Business Account is a separate company-owned account. A Business Account MUST
NOT be owned or authorised by a Personal Account.

A new Business Account MUST be created by its initial AUTHORISER. Business
Account registration MUST require the initial Authoriser's display name or
username, the initial Authoriser's unique login email, the initial Authoriser's
password, business display name, one unique company UEN used for receiving
transfers, and an opening deposit of at least SGD 7,000.00.

Successful Business Account creation MUST atomically create the Business
Account, the initial AUTHORISER employee-access login scoped only to that
Business Account, the completed Business opening-deposit financial transaction,
an Access Audit event for account creation, and an Access Audit event for
initial AUTHORISER creation.

The initial AUTHORISER login is not a separate Business Account and MUST NOT
access any other Business Account. A Business Account MUST maintain at least
one active AUTHORISER employee access login at all times.

Business Accounts receive incoming transfers using unique UEN values. Deposits
and incoming transfers into a Business Account do not require approval and MAY
increase its balance. Every completed outgoing Business withdrawal or transfer
MUST leave at least SGD 7,000.00 in the Business Account.

Rationale: Business banking represents company funds governed by individual
employee credentials scoped to the company account, not by Personal Account
ownership or reusable multi-company login identities.

### VI. Business Employee Access Credentials
Invitations are not part of the MVP. Existing bank customers or account holders
MUST NOT be added to a Business Account through invitation acceptance.

Only an active AUTHORISER MAY create a new employee access login for their
Business Account. Creating employee access MUST require employee display name,
unique login email, assigned role of MEMBER or AUTHORISER, temporary password,
and temporary password confirmation.

The employee access login MUST be scoped to exactly one Business Account. The
employee access login MUST be inactive for normal financial operation until the
employee signs in and changes the temporary password.

Temporary passwords MUST be securely hashed and MUST never be stored in
plaintext. Temporary passwords MAY be shown or communicated only at initial
assignment as necessary for local MVP use and MUST NOT be retrievable afterward.

The application MUST require the employee to change the temporary password at
first sign-in before accessing Business Account balances, histories, deposits,
request actions, approvals, or management actions. After the employee changes
the temporary password, the Authoriser MUST NOT know, recover, or view the
employee's new password.

Rationale: Company employees receive assigned, accountable access credentials
for one Business Account instead of joining as independent bank customers or
sharing company credentials.

### VII. Business Access State, Password Resets, and Audit History
A Business employee access login MUST have an access state sufficient to
represent pending first-login password change, active, and deactivated.

Only an active AUTHORISER MAY issue a new temporary password for another
employee access login in the same Business Account. Issuing a new temporary
password MUST require the employee to change password again at the next sign-in
before accessing banking functionality. Password reset MUST NOT display,
recover, or reveal the user's existing password.

Only an active AUTHORISER MAY deactivate or reactivate employee access. A
deactivated employee MUST immediately lose access to the Business Account and
MUST NOT initiate, submit, approve, reject, cancel, or action transactions.
Reactivation MAY require issuing a new temporary password according to the
technical plan.

Employee access records MUST NOT be deleted through ordinary user workflows
because their actions must remain auditable.

Access Audit History MUST record Business access and security-governance
events, including Business Account creation, initial AUTHORISER creation,
employee access created, temporary password issued, first-login password
changed or access activated, MEMBER promoted to AUTHORISER, employee access
deactivated, employee access reactivated, temporary password reset issued, and
rejected attempts to deactivate the final AUTHORISER where retained for audit.

Access Audit History MUST never reveal password values, password hashes, or
secret credentials.

Rationale: Employee access lifecycle events change who can act on company
funds, so they require explicit state, server-side enforcement, and audit
records that do not expose credentials.

### VIII. Business Roles, Permissions, and Approval
The MVP MUST define exactly two Business employee access roles: MEMBER and
AUTHORISER.

A MEMBER with active access MAY view the Business Account balance, view
completed Transaction History, view Approval History, view Access Audit
History, make valid deposits into the Business Account without approval, submit
outgoing withdrawal requests, submit outgoing transfer requests, and cancel
their own PENDING outgoing requests.

A MEMBER MUST NOT approve or reject requests, cancel another employee's
request, create employee access, reset another user's password, deactivate or
reactivate users, promote users, remove users, alter users, or assign roles.

An AUTHORISER with active access has all MEMBER capabilities. An AUTHORISER MAY
also approve any PENDING outgoing Business withdrawal or transfer, reject any
PENDING outgoing Business withdrawal or transfer, cancel any PENDING outgoing
request including their own, create MEMBER or AUTHORISER employee access
logins, reset an employee's password using a new temporary password, promote a
MEMBER to AUTHORISER, deactivate or reactivate an employee access login, and
deactivate another AUTHORISER only when at least one other active AUTHORISER
remains.

An AUTHORISER MUST NOT demote an AUTHORISER to MEMBER in the MVP. An AUTHORISER
MUST NOT deactivate the final remaining active AUTHORISER. An AUTHORISER MUST
NOT access, recover, or reveal another employee's chosen password after
first-login password change.

Any MEMBER or AUTHORISER with active access to a Business Account MAY submit an
outgoing Business withdrawal or transfer request. Submission MUST create a
PENDING request only. A PENDING request MUST NOT move money, reserve funds,
reduce displayed balance, or create completed financial transaction records.

Any one active AUTHORISER approval is sufficient to approve and complete a
valid outgoing Business request. An AUTHORISER MAY approve a request they
submitted themselves. An AUTHORISER MAY reject any PENDING request. A MEMBER
MAY cancel only their own PENDING request. An AUTHORISER MAY cancel any PENDING
request, including their own.

The only persisted outgoing-request statuses are PENDING, COMPLETED, REJECTED,
CANCELLED, and FAILED. There is no separately persisted APPROVED status.
Approval is an action applied to a PENDING request.

When approval succeeds and all financial validations pass, the request changes
directly from PENDING to COMPLETED and money movement completes atomically. If
approval is attempted but current rules fail, including the SGD 7,000.00
retained-minimum rule, the request changes from PENDING to FAILED and no money
moves. Only PENDING requests MAY be approved, rejected, or cancelled.
COMPLETED, REJECTED, CANCELLED, and FAILED requests are final.

Multiple PENDING outgoing requests MAY exist simultaneously. Each PENDING
request MUST be independently revalidated at approval time.

Rationale: Business outgoing funds require active employee status, role-based
approval, current-state financial revalidation, no fund reservation while
pending, and a clear lifecycle without an APPROVED stored state.

### IX. Transfers and Linked Transaction Records
Personal Accounts receive transfers using unique phone numbers. Business
Accounts receive transfers using unique UEN values. A sender MUST select
whether the destination is a Personal Account or Business Account. The entered
identifier MUST match the destination account type: phone number for Personal
Account destination and UEN for Business Account destination.

Unknown identifiers and identifier/account-type mismatches MUST be rejected.
Transfers from a Personal Account are performed by the Personal login identity
owning that account. Transfers from a Business Account are requested by an
active MEMBER or AUTHORISER employee access login for that Business Account and
require AUTHORISER approval before completion.

A transfer from an account back to the same account MUST be rejected. Old rules
rejecting transfers because one user owned both Personal and Business contexts
MUST NOT be reintroduced.

Every successfully completed transfer MUST create one unique transfer operation
ID, one immutable sender debit financial transaction record, and one immutable
recipient credit financial transaction record. The sender debit record and
recipient credit record MUST each have their own UUID transaction ID and MUST
reference the same transfer operation ID.

Sender debiting, recipient crediting, transfer operation creation, and
transaction-record creation MUST be atomic: either all changes succeed or none
occur.

Rationale: Recipient identity differs by account type, while completed transfer
records must remain linked, auditable, and atomic.

### X. Transaction, Approval, and Access History Separation
The application MUST provide three logically distinct audit views.

Transaction History MUST display completed financial movements only, including
deposits, completed withdrawals, completed transfer debits, completed transfer
credits, and Business Account opening deposits.

Approval History MUST display Business Account outgoing withdrawal and transfer
requests and their workflow statuses: PENDING, COMPLETED, REJECTED, CANCELLED,
and FAILED.

Access Audit History MUST display Business access and security-governance
activity, including Business Account creation, initial AUTHORISER creation,
employee access creation, temporary-password issuance, first-login password
change or access activation, MEMBER promotion, employee deactivation,
employee reactivation, temporary-password reset issuance, and rejected
final-AUTHORISER deactivation attempts where retained for audit.

Non-completed workflow records and access records MUST NOT be represented as
completed financial movements. Access Audit History MUST NOT display password
values, password hashes, temporary password values after initial assignment, or
secret credentials.

Rationale: Financial audit, outgoing-request workflow, and access governance
answer different accountability questions and must remain separate.

### XI. Transaction Auditability and Immutability
Every successful deposit and completed withdrawal MUST have an immutable
financial transaction record with a UUID transaction ID. Every successfully
completed transfer MUST produce two immutable linked financial transaction
records joined by one transfer operation ID. Completed financial transaction
records MUST NOT be editable through application logic.

Completed financial transaction records MUST include at minimum a UUID
transaction ID, transaction type, amount in SGD, associated account, completion
timestamp, transaction status, and transfer operation ID where applicable.

Rejected, CANCELLED, FAILED, or still-PENDING outgoing requests MUST NOT move
funds or create completed financial transaction records.

Rationale: Completed financial history must be complete, immutable, and clearly
separated from pending or failed workflow and access records.

### XII. Automated Testing and Quality Gates
Automated tests are mandatory for core banking, employee access, security, and
audit behaviour. A feature with failing mandatory tests MUST NOT be treated as
complete.

Mandatory tests MUST cover Personal registration and Personal-only access;
Business Account registration and initial AUTHORISER employee access creation;
absence of active invitation behaviour; AUTHORISER creation of MEMBER access
with temporary password; AUTHORISER creation of AUTHORISER access with
temporary password; MEMBER inability to create employee access; new employee
denial from Business functionality until changing the temporary password;
temporary password change activating normal access; password values not exposed
or retrievable; active MEMBER permissions; active AUTHORISER permissions;
MEMBER promotion; MEMBER deactivation; AUTHORISER deactivation only when
another active AUTHORISER remains; rejection of final active AUTHORISER
deactivation; deactivated employee immediate access loss; password reset
issuing a new temporary password and requiring password change again;
reactivation behaviour; one Business Account per employee login; and Access
Audit events for account creation, access creation, password reset, password
activation or change, promotion, deactivation, and reactivation.

Mandatory tests MUST also cover Personal Account creation at SGD 0.00 with
unique phone number; Personal deposits, withdrawals, full-balance withdrawal,
outgoing transfers, and negative-balance rejection; Business Account creation
with unique UEN and opening deposit of at least SGD 7,000.00; duplicate UEN
rejection; MEMBER and AUTHORISER deposits without approval; MEMBER and
AUTHORISER outgoing request submission; MEMBER inability to approve or reject;
AUTHORISER approval of any PENDING request; one AUTHORISER approval being
sufficient; AUTHORISER self-approval; MEMBER cancellation of own PENDING
request only; AUTHORISER cancellation of any PENDING request; multiple PENDING
requests and approval-time revalidation; Business retained-minimum failure
changing request to FAILED without money movement; Personal phone recipient
lookup; Business UEN recipient lookup; unknown recipient rejection; identifier
type mismatch rejection; UUID transaction IDs; shared transfer operation IDs;
atomic rollback on failed financial operations; Transaction History containing
completed financial events only; Approval History containing outgoing Business
requests only; and Access Audit History containing access-governance events
only.

Rationale: The MVP cannot claim banking or access-governance correctness unless
employee access state, role permissions, money movement, approval workflow,
audit separation, and rollback behaviours are tested.

### XIII. Security and Secrets Management
Secrets and sensitive configuration MUST NOT be committed to GitHub. Django
secret keys, plaintext passwords, temporary passwords, password hashes, tokens,
private credentials, environment files containing secrets, and local SQLite
database files MUST NOT be committed.

Secret configuration MUST be stored in environment variables or ignored local
files. An appropriate `.gitignore` MUST exist before creating local secrets,
SQLite database files, collected local static files, or Python virtual
environments.

Authentication MUST use securely hashed passwords. Personal Account logins and
Business employee access logins MUST remain separate. Business Accounts MUST
use individual employee access logins and MUST NOT rely on shared credentials.

Temporary passwords MUST be hashed and MUST NOT be retrievable after initial
assignment. Mandatory first-login password change MUST be enforced
server-side. Deactivated employees MUST NOT access Business functionality.

Only active AUTHORISERS MAY create credentials, reset temporary passwords,
promote users, deactivate users, or reactivate users. The final active
AUTHORISER MUST NOT be deactivated. Permission enforcement MUST NOT rely on UI
hiding alone.

Rationale: Local MVP deployment still requires credential hygiene, identity
separation, role-based access protection, and server-side enforcement of all
security and banking invariants.

### XIV. Governance and SDD Compliance
This constitution is the highest-authority project document for non-negotiable
banking, identity, employee-access-governance, and engineering rules. Every
later specification and technical plan MUST include a Constitution Check.

Every business rule MUST remain traceable from constitution to specification,
acceptance criteria, technical plan, implementation task, code component, and
automated test.

Specifications and plans MUST use identifiers such as `FR-###` for functional
requirements, `BR-###` for business rules, `SEC-###` for security requirements,
`NFR-###` for non-functional requirements, and `TEST-###` for mandatory tests.
Test names or associated traceability documentation MUST reference the banking
rule or requirement being verified.

A constitutional amendment is required for any change to the MVP technology
stack, SGD-only currency restriction, Personal Account login model, Business
employee access login model, account types, Personal Account no-minimum-balance
rule, Business Account opening-deposit or retained-minimum rule, Business
employee roles, temporary-password rules, employee access state rules,
authorisation lifecycle, transfer recipient identifiers, transfer recording,
transaction/approval/access history separation, security obligations, testing
obligations, traceability obligations, or MVP scope.

Semantic versioning MUST be applied as follows: MAJOR for removing or
fundamentally redefining a core principle or banking invariant; MINOR for
adding a mandatory principle or materially expanding scope; PATCH for
clarifications that do not change required behaviour.

Rationale: SDD artifacts must remain subordinate to the constitution, and
changes to banking or access-governance invariants must be intentional,
reviewed, and versioned.

## Amendment 3.0.0 Authoriser-Provisioned Employee Access Governance

This amendment replaces the version 2.0.0 invitation-and-membership onboarding
model. Invitations, invitation acceptance, existing Business-user membership
acceptance, and one Business login joining multiple Business Accounts are no
longer valid MVP behaviours.

A Business Account now has employee access logins provisioned by an active
AUTHORISER of that Business Account. Each employee access login is scoped to
exactly one Business Account. Employees do not create separate Business
Accounts or join as existing bank-account users to gain access to a company
Business Account.

This amendment introduces temporary-password provisioning, mandatory
first-login password change, temporary-password reset, active/deactivated
access state, deactivation and reactivation governance, one Business Account
per employee login, and Access Audit events for access and password-governance
activity.

All later artifacts MUST remove or replace active statements, models, services,
forms, routes, templates, tests, or tasks implying Business invitations,
invitation acceptance, a Business user accepting membership in multiple
Business Accounts, a Business Account selector for employee logins, shared
Business credentials, or Personal Account authorisation of Business Accounts.

## Specification-Driven Development Quality Gates

Every feature specification MUST include a Constitution Check and MUST identify
all applicable `BR-###`, `FR-###`, `SEC-###`, `NFR-###`, and `TEST-###`
identifiers. Each business rule MUST have acceptance criteria before planning
begins.

Every technical plan MUST prove alignment with the MVP stack, SGD-only money
handling, Personal Account rules, Business Account employee access rules,
temporary-password and access-state rules, role rules, Access Audit rules,
Business retained-minimum rules, deposit and withdrawal rules, transfer
atomicity, Business outgoing approval lifecycle, transaction immutability,
history separation, secrets management, mandatory tests, traceability, and
local deployment.

Every task list MUST include tests before implementation tasks for applicable
banking, employee-access, permission, audit, password-governance, and security
rules. Tasks MUST preserve requirement and business-rule identifiers and name
the code component and test path that will satisfy each rule.

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
dependent Spec Kit templates are updated together, unless the amendment request
explicitly limits the command to constitution-only output and records template
updates as pending follow-up work.

Compliance review is mandatory during specification and planning. A feature may
not proceed from specification to planning, from planning to tasks, or from
tasks to complete implementation while any applicable constitutional gate is
failing.

Versioning follows semantic versioning:
- MAJOR: removing or fundamentally redefining a core principle or banking,
  identity, employee-access, authorisation, or audit invariant.
- MINOR: adding a mandatory principle or materially expanding scope.
- PATCH: clarifications that do not change required behaviour.

**Version**: 3.0.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-26
