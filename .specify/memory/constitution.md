<!--
Sync Impact Report
Version change: 1.1.0 -> 2.0.0
Modified principles:
- III. Account Types and Recipient Identity -> III. Separate Login Identities and Account Experiences
- IV. Personal Account Rules -> IV. Personal Account Model
- V. Business Account Opening and Balance Rules -> V. Business Account and Business User Model
- VIII. Business Account Authorisation -> VIII. Business Membership Roles and Authorisation
- XI. Automated Testing and Quality Gates -> XII. Automated Testing and Quality Gates
- XIII. Governance and SDD Compliance -> XIV. Governance and SDD Compliance
Added sections:
- VI. Business Account Membership and Invitations
- VII. Business Account Access Audit History
- X. Transaction, Approval, and Access History Separation
- Amendment 2.0.0 Separate Identity and Business Membership Governance
Removed sections:
- Amendment 1.1.0 Recipient and Approval Governance as standalone current
  amendment text; preserved non-conflicting recipient and approval rules inside
  core principles.
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
  traceability, and implementation code to remove the superseded one-user,
  own-Personal-authoriser Business Account model.
-->
# BankApp Constitution

## Core Principles

### I. MVP Technology and Scope
The MVP MUST use Python 3.11 or later, Django, SQLite3, Django templates, and
Waitress for simple local macOS deployment. All monetary values and transactions
MUST be restricted to Singapore Dollars (SGD) only.

The MVP MUST NOT introduce alternative databases, frontend frameworks, payment
gateways, external bank integrations, cloud infrastructure, microservices,
message queues, WebSockets, third-party authentication systems, OTP verification,
or external UEN registry verification without constitutional amendment.

The MVP scope MUST remain limited to registration, authentication, Personal
Account access, Business Account access, Business Account membership,
invitations, role management, deposits, withdrawals, transfers, outgoing
Business approval workflow, transaction history, approval history, access audit
history, automated tests, traceability, and local deployment.

Rationale: A narrow local-first stack keeps the SDD MVP auditable, testable, and
focused on proving banking and access-governance rules before architecture
expansion.

### II. Financial Correctness and Money Validation
All balances and monetary operations MUST use precise decimal arithmetic. The
application MUST never use floating-point arithmetic for money.

Deposits, withdrawals, opening deposits, and transfers MUST reject zero,
negative, malformed, non-numeric, non-SGD, or invalid-precision values. Monetary
values MUST support no more than two decimal places. Any operation that would
result in a negative account balance MUST be prevented. Rejected or failed
financial operations MUST NOT modify balances and MUST NOT be recorded as
completed financial transactions.

Rationale: Banking correctness depends on exact SGD arithmetic, strict amount
validation, and unchanged state after failed operations.

### III. Separate Login Identities and Account Experiences
During registration, a new user MUST choose exactly one account-access type:
Personal Account access or Business Account access. A Personal login identity
MUST access Personal Account functionality only. A Business login identity MUST
access Business Account functionality only. The same login identity MUST NOT
access both Personal and Business Accounts.

A real individual who requires both Personal and Business access MUST use
separate registered credentials for each context. Email addresses MUST remain
unique login identifiers across the whole application, so separate Personal and
Business login identities MUST use different email addresses.

Registered users MUST have a unique email address, securely stored password, and
user-selected username. Passwords MUST be stored using Django authentication and
password hashing facilities and MUST never be stored in plaintext.

Rationale: Personal banking and company banking are separate experiences with
different ownership and permission rules. Separate login identities prevent an
individual Personal Account from implicitly owning or authorising company funds.

### IV. Personal Account Model
A Personal user registers for and accesses exactly one Personal Account. A
Personal Account MUST require a user-selected username, unique email login,
securely stored password, and one unique phone number used for receiving
transfers.

A Personal Account MUST NOT require an opening deposit and MUST begin with
balance SGD 0.00 unless funds are later deposited or received. A Personal
Account has no minimum-balance requirement.

A Personal Account MAY deposit, withdraw, and make outgoing transfers only when
the amount is valid and greater than zero. A Personal Account withdrawal or
outgoing transfer MAY leave the account at SGD 0.00, but MUST NOT cause the
balance to become negative. A Personal Account receives incoming transfers using
its unique phone number.

Successful Personal Account deposits, withdrawals, and outgoing or incoming
transfers MUST be auditable through immutable completed financial transaction
records.

Rationale: Personal accounts are individual SGD accounts with no retained
minimum, but they still require exact validation, unique recipient identity, and
auditable financial movement.

### V. Business Account and Business User Model
A Business Account is a separate company-owned shared account. A Business
Account MUST NOT be owned or authorised by a Personal Account.

A Business Account MUST require a business display name, one unique company UEN
used for receiving transfers, an opening deposit of at least SGD 7,000.00, and
at least one active Business User with the AUTHORISER role. The opening deposit
MUST create one immutable completed financial transaction record with a UUID
transaction ID.

The individual who creates a new Business Account MUST create or use a
Business-only login identity and MUST automatically become the first AUTHORISER
for that Business Account. A Business User MAY be granted access to one or more
Business Accounts. A Business User MUST NOT gain access to Personal Account
functionality through the same login identity.

A Business Account MUST be accessed through individual Business User logins, not
shared company credentials. Sharing a single email/password login among multiple
individuals is not an approved application behaviour.

A Business Account MUST maintain a minimum balance of SGD 7,000.00 after every
completed outgoing withdrawal or outgoing transfer. Deposits into a Business
Account and incoming transfers received by a Business Account do not require
approval and MAY increase its balance.

Rationale: Business banking represents company funds governed by individual
Business Users and role-based membership, not by a Personal Account owner.

### VI. Business Account Membership and Invitations
The MVP MUST define exactly two Business Account membership roles: MEMBER and
AUTHORISER.

A MEMBER MAY view the Business Account balance, view completed Business Account
transaction history, view Business Account approval/request history, deposit
funds into the Business Account without approval, submit outgoing withdrawal
requests, submit outgoing transfer requests, and cancel their own PENDING
outgoing requests.

A MEMBER MUST NOT approve or reject outgoing requests, invite users, assign
membership roles, promote users, remove users, or cancel another user's PENDING
request.

An AUTHORISER has all MEMBER capabilities. An AUTHORISER MAY also approve any
PENDING outgoing Business Account withdrawal or transfer request, reject any
PENDING outgoing Business Account withdrawal or transfer request, cancel any
PENDING outgoing Business Account withdrawal or transfer request including their
own, invite Business Users to the Business Account, assign MEMBER or AUTHORISER
role when inviting a user, promote an existing MEMBER to AUTHORISER, remove an
existing MEMBER, and remove another AUTHORISER only when at least one
AUTHORISER remains afterward.

An AUTHORISER MUST NOT demote an AUTHORISER back to MEMBER in the MVP. An
AUTHORISER MUST NOT remove themselves or another AUTHORISER when doing so would
leave the Business Account without any AUTHORISER. The application MUST NOT
allow a Business Account to have zero AUTHORISER memberships.

Only an AUTHORISER MAY invite another user to access a Business Account.
Invitations MUST be addressed using the invitee's email address and MUST specify
the role to be granted upon acceptance: MEMBER or AUTHORISER. Access MUST be
granted only after the invited Business User accepts the invitation.

An invited person MUST register a Business-only login identity or sign in using
an existing Business-only login identity. A Personal-only login identity MUST
NOT accept or use Business Account access. A Business User MAY accept membership
in more than one Business Account.

Removed users MUST immediately lose access to the affected Business Account.
Removal from one Business Account MUST NOT remove access to other Business
Accounts where the user remains a member. Promoting a MEMBER to AUTHORISER is
supported. Demoting an AUTHORISER to MEMBER is outside MVP scope. Removing an
AUTHORISER is supported only when another AUTHORISER remains.

Rationale: Company account access requires individual accountability, explicit
membership, and a role model that protects Business Accounts from losing all
authorisers.

### VII. Business Account Access Audit History
The application MUST record Business Account access audit events for Business
Account creation and initial AUTHORISER assignment, invitation issuance,
invitation acceptance, role assigned through accepted invitation, MEMBER
promotion to AUTHORISER, MEMBER removal, AUTHORISER removal, and rejected or
invalid membership-management attempts where retained for audit purposes.

Each access audit event MUST record at minimum the affected Business Account,
acting Business User where applicable, affected or invited Business User or
email where applicable, action type, assigned or removed role where applicable,
date/time, and outcome or status.

Access audit history MUST be distinguishable from completed financial
Transaction History and outgoing-request Approval History.

Rationale: Business access governance is itself an auditable activity and must
not be confused with financial movement.

### VIII. Deposits, Withdrawals, and Business Approval
A valid positive deposit MAY be credited to a Personal Account or Business
Account. Any MEMBER or AUTHORISER with active access to a Business Account MAY
make a valid deposit into that Business Account without approval. Every
successful deposit MUST create an immutable deposit transaction record with a
UUID transaction ID.

A Personal Account withdrawal MAY complete without approval when the amount is
valid and the account has sufficient balance to avoid a negative balance. A
Business Account withdrawal is an outgoing Business request and MUST NOT
complete until approved by an AUTHORISER for that Business Account. Every
successfully completed withdrawal MUST create an immutable withdrawal
transaction record with a UUID transaction ID.

Any MEMBER or AUTHORISER with active access to a Business Account MAY submit an
outgoing Business withdrawal or transfer request. Submission MUST create a
PENDING request only. A PENDING request MUST NOT move money, reserve funds,
reduce displayed balance, or create completed financial transaction records.

Any one AUTHORISER approval is sufficient to approve and complete a valid
outgoing Business request. An AUTHORISER MAY approve a request they submitted
themselves. An AUTHORISER MAY reject any PENDING request. A MEMBER MAY cancel
only their own PENDING request. An AUTHORISER MAY cancel any PENDING request,
including their own.

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

Rationale: Business outgoing funds require role-based approval, current-state
financial revalidation, no fund reservation while pending, and a clear lifecycle
without an APPROVED stored state.

### IX. Transfers and Linked Transaction Records
Personal Accounts receive transfers using unique phone numbers. Business
Accounts receive transfers using unique UEN values. A sender MUST select whether
the destination is a Personal Account or Business Account. The entered
identifier MUST match the destination account type: phone number for Personal
Account destination and UEN for Business Account destination.

Unknown identifiers and identifier/account-type mismatches MUST be rejected.
Transfers from a Personal Account are performed by the Personal login identity
owning that account. Transfers from a Business Account are requested by a MEMBER
or AUTHORISER with active access to that Business Account and require AUTHORISER
approval before completion.

A transfer from an account back to the same account MUST be rejected. Prior
rules concerning transfers between a user's own Personal Account and Business
Account are removed because Personal and Business login identities are no longer
linked under one user ownership model.

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

Access Audit History MUST display Business Account access-management activity,
including invitations, invitation acceptances, assigned roles, promotions,
removals, and initial AUTHORISER creation.

Non-completed workflow records and access records MUST NOT be represented as
completed financial movements.

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
Automated tests are mandatory for core banking, access, and audit behaviour. A
feature with failing mandatory tests MUST NOT be treated as complete.

Mandatory tests MUST cover Personal registration creating Personal-only access;
Business registration creating Business-only access; Personal login denial from
Business Account pages and Business invitations; Business login denial from
Personal Account pages; separate registered credentials for individuals needing
both contexts; Personal Account creation at SGD 0.00 with unique phone number;
Personal deposits, withdrawals, full-balance withdrawal, outgoing transfers, and
negative-balance rejection; Business Account creation with unique UEN, opening
deposit of at least SGD 7,000.00, and initial AUTHORISER; duplicate UEN
rejection; Business User membership in multiple Business Accounts; AUTHORISER
invitation of MEMBER and AUTHORISER users; invitation acceptance before access
is granted; Personal-only identity rejection from Business invitation
acceptance; MEMBER inability to invite or assign roles; AUTHORISER promotion of
MEMBER to AUTHORISER; AUTHORISER removal of MEMBER; AUTHORISER removal of
another AUTHORISER only when another AUTHORISER remains; final AUTHORISER
removal rejection; removed user immediate access loss; demotion from AUTHORISER
to MEMBER being unsupported; MEMBER and AUTHORISER deposits without approval;
MEMBER and AUTHORISER outgoing request submission; MEMBER inability to approve
or reject; AUTHORISER approval of any PENDING request; one AUTHORISER approval
being sufficient; AUTHORISER self-approval; MEMBER cancellation of own PENDING
request only; AUTHORISER cancellation of any PENDING request; multiple PENDING
requests and approval-time revalidation; Business retained-minimum failure
changing request to FAILED without money movement; Personal phone recipient
lookup; Business UEN recipient lookup; unknown recipient rejection; identifier
type mismatch rejection; UUID transaction IDs; shared transfer operation IDs;
atomic rollback on failed financial operations; Transaction History containing
completed financial events only; Approval History containing outgoing Business
requests; and Access Audit History containing invitations, acceptances,
promotions, removals, and initial AUTHORISER creation.

Rationale: The MVP cannot claim banking or access-governance correctness unless
identity separation, membership permissions, money movement, approval workflow,
audit separation, and rollback behaviours are tested.

### XIII. Security and Secrets Management
Secrets and sensitive configuration MUST NOT be committed to GitHub. Django
secret keys, plaintext passwords, tokens, private credentials, environment files
containing secrets, and local SQLite database files MUST NOT be committed.

Secret configuration MUST be stored in environment variables or ignored local
files. An appropriate `.gitignore` MUST exist before creating local secrets,
SQLite database files, or Python virtual environments.

Authentication MUST use securely hashed passwords. Personal and Business login
identities MUST remain separate. Business Accounts MUST use individual user
logins and MUST NOT rely on shared credentials.

Business membership, invitation, role assignment, promotion, removal, approval,
rejection, cancellation, financial validation, account access, and permission
checks MUST be enforced server-side rather than relying only on the user
interface. Removed Business Users MUST lose access immediately. The last
remaining AUTHORISER MUST NOT be removed.

Rationale: Local MVP deployment still requires credential hygiene, identity
separation, role-based access protection, and server-side enforcement of all
security and banking invariants.

### XIV. Governance and SDD Compliance
This constitution is the highest-authority project document for non-negotiable
banking, identity, access-governance, and engineering rules. Every later
specification and technical plan MUST include a Constitution Check.

Every business rule MUST remain traceable from constitution to specification,
acceptance criteria, technical plan, implementation task, code component, and
automated test.

Specifications and plans MUST use identifiers such as `FR-###` for functional
requirements, `BR-###` for business rules, `SEC-###` for security requirements,
`NFR-###` for non-functional requirements, and `TEST-###` for mandatory tests.
Test names or associated traceability documentation MUST reference the banking
rule or requirement being verified.

A constitutional amendment is required for any change to the MVP technology
stack, SGD-only currency restriction, separate Personal and Business login
identity model, account types, Personal Account no-minimum-balance rule,
Business Account opening-deposit or minimum-balance rule, Business membership
roles, invitation rules, authorisation lifecycle, transfer recipient
identifiers, transfer recording, transaction/approval/access history separation,
security obligations, testing obligations, traceability obligations, or MVP
scope.

Semantic versioning MUST be applied as follows: MAJOR for removing or
fundamentally redefining a core principle or banking invariant; MINOR for adding
a mandatory principle or materially expanding scope; PATCH for clarifications
that do not change required behaviour.

Rationale: SDD artifacts must remain subordinate to the constitution, and
changes to banking or access-governance invariants must be intentional,
reviewed, and versioned.

## Amendment 2.0.0 Separate Identity and Business Membership Governance

This amendment replaces the former model where one login could own both a
Personal Account and a Business Account, and where the user's Personal Account
authorised Business Account outgoing transactions.

The application now requires separate Personal and Business login identities.
A Personal login identity accesses Personal Account functionality only. A
Business login identity accesses Business Account functionality only. Business
Accounts are company-owned shared accounts accessed by individual Business Users
through membership and role-based permissions.

This amendment introduces MEMBER and AUTHORISER Business membership roles,
Business Account invitations, promotion and removal governance, access audit
history, and mandatory tests for identity separation, membership permissions,
Business approval, and audit separation.

All later artifacts MUST remove or replace statements implying one login owns
both Personal and Business Accounts, a Personal Account authorises a Business
Account, a Business Account must be linked to an owner's Personal Account,
Business access is provided through shared credentials, or exactly one Business
authoriser exists.

## Specification-Driven Development Quality Gates

Every feature specification MUST include a Constitution Check and MUST identify
all applicable `BR-###`, `FR-###`, `SEC-###`, `NFR-###`, and `TEST-###`
identifiers. Each business rule MUST have acceptance criteria before planning
begins.

Every technical plan MUST prove alignment with the MVP stack, SGD-only money
handling, separate login identity model, Personal Account rules, Business
Account membership and role rules, invitation rules, access audit rules,
Business retained-minimum rules, deposit and withdrawal rules, transfer
atomicity, Business outgoing approval lifecycle, transaction immutability,
history separation, secrets management, mandatory tests, traceability, and
local deployment.

Every task list MUST include tests before implementation tasks for applicable
banking, membership, permission, audit, and security rules. Tasks MUST preserve
requirement and business-rule identifiers and name the code component and test
path that will satisfy each rule.

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
  identity, membership, authorisation, or audit invariant.
- MINOR: adding a mandatory principle or materially expanding scope.
- PATCH: clarifications that do not change required behaviour.

**Version**: 2.0.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-26
